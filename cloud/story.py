# -*- coding: utf-8 -*-
"""story-poster — POP: pop/POP-story.md
Diario 17h30: reposta como STORY o post de maior alcance das ultimas 24h
(fallback: post mais recente). 1 story/dia (story_state.json).
"""
import os, json, time, requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

API = "https://graph.instagram.com/v21.0"
IG = os.environ["IG_USER_ID"]; TOKEN = os.environ["IG_TOKEN"]
ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, "story_state.json")
TZ = ZoneInfo("America/Sao_Paulo")

def get(path, params):
    r = requests.get(f"{API}/{path}", params={**params, "access_token": TOKEN}, timeout=60)
    r.raise_for_status(); return r.json()

def post(path, data):
    r = requests.post(f"{API}/{path}", data={**data, "access_token": TOKEN}, timeout=120)
    if r.status_code >= 400: raise RuntimeError(f"{path}: {r.status_code} {r.text[:200]}")
    return r.json()

def main():
    hoje = datetime.now(TZ).strftime("%Y-%m-%d")
    st = json.load(open(STATE, encoding="utf-8-sig")) if os.path.exists(STATE) else {}
    if st.get("last_date") == hoje:
        print("story de hoje ja foi — nada a fazer"); return
    media = get(f"{IG}/media", {"fields": "id,media_type,media_url,thumbnail_url,timestamp,like_count", "limit": 6}).get("data", [])
    corte = (datetime.now(TZ) - timedelta(hours=26)).isoformat()
    recentes = [m for m in media if m.get("timestamp", "") >= corte and m.get("media_url") or m.get("thumbnail_url")]
    alvo = None; best = -1
    for m in (recentes or media[:1]):
        reach = 0
        try:
            ins = get(f"{m['id']}/insights", {"metric": "reach"}).get("data", [])
            reach = (ins[0].get("values") or [{}])[0].get("value", 0) or 0
        except Exception: pass
        if reach >= best: best = reach; alvo = m
    if not alvo: print("nenhum post pra repostar"); return
    if alvo.get("media_type") == "VIDEO":
        url = alvo.get("thumbnail_url") or alvo.get("media_url")
        data = {"media_type": "STORIES", "image_url": url}
    else:
        data = {"media_type": "STORIES", "image_url": alvo.get("media_url")}
    cid = post(f"{IG}/media", data)["id"]
    for _ in range(20):
        s = get(cid, {"fields": "status_code"}).get("status_code")
        if s == "FINISHED": break
        if s == "ERROR": raise RuntimeError("container story ERROR")
        time.sleep(5)
    sid = post(f"{IG}/media_publish", {"creation_id": cid}).get("id")
    st["last_date"] = hoje; st["last_story"] = sid; st["source"] = alvo["id"]
    json.dump(st, open(STATE, "w", encoding="utf-8"), indent=1)
    print(f"story publicado: {sid} (fonte reach={best})")

if __name__ == "__main__":
    main()
