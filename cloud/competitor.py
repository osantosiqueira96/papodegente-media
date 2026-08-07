# -*- coding: utf-8 -*-
"""competitor-watch — POP: pop/POP-competitor.md
Diario 6h45: espiona perfis-referencia via business_discovery (API oficial,
sem scraping) -> cloud/radar.md (o trend-scout inclui na pauta das 7h30).
DORMENTE sem secrets FB_TOKEN + FB_IG_ID.
"""
import os, json, requests
from datetime import datetime
from zoneinfo import ZoneInfo

G = "https://graph.facebook.com/v21.0"
FB = os.environ.get("FB_TOKEN", ""); ANCORA = os.environ.get("FB_IG_ID", "")
ROOT = os.path.dirname(os.path.abspath(__file__))
TZ = ZoneInfo("America/Sao_Paulo")

def main():
    if not (FB and ANCORA):
        print("dormente: secrets FB_TOKEN/FB_IG_ID ausentes"); return
    perfis = json.load(open(os.path.join(ROOT, "competitors.json"), encoding="utf-8-sig"))["perfis"]
    L = [f"## 🕵️ Radar da concorrência ({datetime.now(TZ).strftime('%d/%m %H:%M')})", ""]
    for u in perfis:
        try:
            f = f"business_discovery.username({u}){{followers_count,media.limit(6){{like_count,comments_count,media_type,permalink,caption,timestamp}}}}"
            r = requests.get(f"{G}/{ANCORA}", params={"fields": f, "access_token": FB}, timeout=60)
            r.raise_for_status()
            bd = r.json().get("business_discovery", {})
            posts = sorted(bd.get("media", {}).get("data", []), key=lambda m: -(m.get("like_count") or 0))
            L.append(f"### @{u} ({bd.get('followers_count','?')} seguidores)")
            for m in posts[:2]:
                cap = (m.get("caption") or "").split("\n")[0][:70]
                L.append(f"- {m.get('like_count',0)} likes/{m.get('comments_count',0)} com ({m.get('media_type')}): {cap}")
                L.append(f"  {m.get('permalink','')}")
            L.append("")
        except Exception as e:
            L.append(f"### @{u}: erro {str(e)[:80]}"); L.append("")
    L.append("**Uso:** replicar ANGULO vencedor com o nosso motor (original, nunca repost).")
    open(os.path.join(ROOT, "radar.md"), "w", encoding="utf-8").write("\n".join(L))
    print(f"radar ok: {len(perfis)} perfis")

if __name__ == "__main__":
    main()
