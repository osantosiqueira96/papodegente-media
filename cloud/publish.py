# -*- coding: utf-8 -*-
"""
Publicador na NUVEM (roda no GitHub Actions a cada 30 min).
Le cloud/queue.json, publica no Instagram o que estiver vencido (horario de Brasilia),
e atualiza o status. Midia servida do proprio repo via raw.githubusercontent.com.

Env: IG_USER_ID, IG_TOKEN, GITHUB_REPOSITORY (owner/repo, setado pelo Actions)
"""
import os, json, glob, time, sys
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

API = "https://graph.instagram.com/v21.0"
IG = os.environ["IG_USER_ID"]
TOKEN = os.environ["IG_TOKEN"]
REPO = os.environ.get("GITHUB_REPOSITORY", "osantosiqueira96/papodegente-media")
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
ROOT = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(ROOT, "queue.json")
TZ = ZoneInfo("America/Sao_Paulo")

def api_post(path, data, timeout=120):
    r = requests.post(f"{API}/{path}", data={**data, "access_token": TOKEN}, timeout=timeout)
    if r.status_code >= 400:
        raise RuntimeError(f"{path}: {r.status_code} {r.text[:300]}")
    return r.json()

def api_get(path, params, timeout=60):
    r = requests.get(f"{API}/{path}", params={**params, "access_token": TOKEN}, timeout=timeout)
    r.raise_for_status()
    return r.json()

def wait_ready(cid, tries=40, sleep=6):
    for _ in range(tries):
        s = api_get(cid, {"fields": "status_code"}).get("status_code")
        if s == "FINISHED":
            return
        if s == "ERROR":
            raise RuntimeError(f"container {cid} ERROR")
        time.sleep(sleep)
    raise RuntimeError(f"container {cid} timeout")

def caption_of(folder):
    p = os.path.join(ROOT, "posts", folder, "legenda.txt")
    return open(p, encoding="utf-8-sig").read().strip() if os.path.exists(p) else ""

def publish_carousel(folder):
    slides = sorted(glob.glob(os.path.join(ROOT, "posts", folder, "slide*.jpg")),
                    key=lambda p: int("".join(filter(str.isdigit, os.path.basename(p))) or 0))
    if not slides:
        raise RuntimeError("sem slides jpg")
    children = []
    for s in slides:
        url = f"{RAW}/cloud/posts/{folder}/{os.path.basename(s)}"
        cid = api_post(f"{IG}/media", {"image_url": url, "is_carousel_item": "true"})["id"]
        children.append(cid)
        time.sleep(1)
    for c in children:
        wait_ready(c)
    parent = api_post(f"{IG}/media", {"media_type": "CAROUSEL",
                                      "children": ",".join(children),
                                      "caption": caption_of(folder)})["id"]
    wait_ready(parent)
    return api_post(f"{IG}/media_publish", {"creation_id": parent})["id"]

def publish_photo(folder):
    slides = sorted(glob.glob(os.path.join(ROOT, "posts", folder, "slide*.jpg")))
    url = f"{RAW}/cloud/posts/{folder}/{os.path.basename(slides[0])}"
    cid = api_post(f"{IG}/media", {"image_url": url, "caption": caption_of(folder)})["id"]
    wait_ready(cid)
    return api_post(f"{IG}/media_publish", {"creation_id": cid})["id"]

def publish_reel(folder):
    mp4s = glob.glob(os.path.join(ROOT, "posts", folder, "*.mp4"))
    if not mp4s:
        raise RuntimeError("sem mp4")
    url = f"{RAW}/cloud/posts/{folder}/{os.path.basename(mp4s[0])}"
    cid = api_post(f"{IG}/media", {"media_type": "REELS", "video_url": url,
                                   "share_to_feed": "true", "caption": caption_of(folder)})["id"]
    wait_ready(cid, tries=60, sleep=10)
    return api_post(f"{IG}/media_publish", {"creation_id": cid})["id"]

def main():
    if not os.path.exists(QUEUE):
        print("sem queue.json — nada a fazer")
        return
    q = json.load(open(QUEUE, encoding="utf-8-sig"))
    now = datetime.now(TZ)
    changed = False
    for item in q:
        if item.get("status") != "pending":
            continue
        due = datetime.strptime(item["when"], "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        if due > now:
            continue
        name, typ = item["name"], item.get("type", "carousel")
        print(f">>> publicando {name} ({typ}) agendado {item['when']}")
        try:
            fn = {"carousel": publish_carousel, "photo": publish_photo, "reel": publish_reel}[typ]
            post_id = fn(name)
            item["status"] = "published"
            item["post_id"] = post_id
            item["published_at"] = now.strftime("%Y-%m-%d %H:%M")
            print(f"    OK id={post_id}")
        except Exception as e:
            item["status"] = "error"
            item["note"] = str(e)[:200]
            print(f"    ERRO: {e}")
        changed = True
    if changed:
        json.dump(q, open(QUEUE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("queue.json atualizado")
    else:
        print("nada vencido; nada a publicar")

if __name__ == "__main__":
    main()
