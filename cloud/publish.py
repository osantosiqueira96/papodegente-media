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
# Threads (espelhamento automatico) — dormente ate os secrets existirem
TH_API = "https://graph.threads.net/v1.0"
TH_USER = os.environ.get("THREADS_USER_ID", "")
TH_TOKEN = os.environ.get("THREADS_TOKEN", "")
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

def threads_mirror(folder, typ):
    """Espelha o post no Threads (texto ate 500 + midia). Nunca bloqueia o IG."""
    if not (TH_USER and TH_TOKEN):
        return None
    try:
        text = caption_of(folder)[:480]
        data = {"access_token": TH_TOKEN, "text": text}
        if typ == "reel":
            mp4s = glob.glob(os.path.join(ROOT, "posts", folder, "*.mp4"))
            if not mp4s:
                return None
            data.update({"media_type": "VIDEO",
                         "video_url": f"{RAW}/cloud/posts/{folder}/{os.path.basename(mp4s[0])}"})
            tries, pause = 40, 8
        else:
            slides = sorted(glob.glob(os.path.join(ROOT, "posts", folder, "slide*.jpg")))
            if slides:
                data.update({"media_type": "IMAGE",
                             "image_url": f"{RAW}/cloud/posts/{folder}/{os.path.basename(slides[0])}"})
            else:
                data["media_type"] = "TEXT"
            tries, pause = 20, 5
        r = requests.post(f"{TH_API}/{TH_USER}/threads", data=data, timeout=120)
        if r.status_code >= 400:
            raise RuntimeError(r.text[:200])
        cid = r.json()["id"]
        for _ in range(tries):
            st = requests.get(f"{TH_API}/{cid}", params={"fields": "status",
                              "access_token": TH_TOKEN}, timeout=60).json().get("status")
            if st == "FINISHED":
                break
            if st == "ERROR":
                raise RuntimeError("container ERROR")
            time.sleep(pause)
        r2 = requests.post(f"{TH_API}/{TH_USER}/threads_publish",
                           data={"creation_id": cid, "access_token": TH_TOKEN}, timeout=120)
        if r2.status_code >= 400:
            raise RuntimeError(r2.text[:200])
        tid = r2.json().get("id")
        print(f"    THREADS OK id={tid}")
        return tid
    except Exception as e:
        print(f"    THREADS falhou (IG nao afetado): {e}")
        return None

def main():
    if not os.path.exists(QUEUE):
        print("sem queue.json — nada a fazer")
        return
    q = json.load(open(QUEUE, encoding="utf-8-sig"))
    now = datetime.now(TZ)
    changed = False
    errs = []
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
            tid = threads_mirror(name, typ)
            if tid:
                item["threads_id"] = tid
        except Exception as e:
            msg = str(e)
            # limite de requisicao da Meta = TEMPORARIO: segura na fila e tenta de novo
            transitorio = ("request limit" in msg or '"code":4' in msg or "2207051" in msg
                           or "rate limit" in msg.lower() or '"code":32' in msg)
            if transitorio:
                item["status"] = "pending"
                item["note"] = f"limite temporario da Meta em {now.strftime('%H:%M')} — nova tentativa no proximo ciclo"
                print(f"    LIMITE DA META (temporario): fica na fila e tenta de novo")
            else:
                item["status"] = "error"
                item["note"] = msg[:200]
                errs.append(f"{name} ({item['when']}): {msg[:160]}")
                print(f"    ERRO: {e}")
        changed = True
    if changed:
        json.dump(q, open(QUEUE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("queue.json atualizado")
    else:
        print("nada vencido; nada a publicar")
    if errs:
        # ANDON: arquivo-sinal (efêmero, só existe no runner) — o workflow abre o alerta
        open(os.path.join(ROOT, "_alert.txt"), "w", encoding="utf-8").write("\n".join(errs))

if __name__ == "__main__":
    main()
