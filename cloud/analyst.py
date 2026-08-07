# -*- coding: utf-8 -*-
"""engagement-analyst — POP: pop/POP-analyst.md
Diario 21h30: snapshot de metricas por post -> cloud/analysis.json + analysis.md.
Issue so no DOMINGO (resumo semanal) ou quando ha NOVO RECORDE de alcance.
"""
import os, json, requests
from datetime import datetime
from zoneinfo import ZoneInfo

API = "https://graph.instagram.com/v21.0"
IG = os.environ["IG_USER_ID"]; TOKEN = os.environ["IG_TOKEN"]
ROOT = os.path.dirname(os.path.abspath(__file__))
TZ = ZoneInfo("America/Sao_Paulo")

def get(path, params):
    r = requests.get(f"{API}/{path}", params={**params, "access_token": TOKEN}, timeout=60)
    r.raise_for_status(); return r.json()

def main():
    now = datetime.now(TZ); hoje = now.strftime("%Y-%m-%d")
    perfil = get(IG, {"fields": "followers_count,media_count"})
    media = get(f"{IG}/media", {"fields": "id,caption,media_type,timestamp,like_count,comments_count,permalink", "limit": 12}).get("data", [])
    posts = []
    for m in media:
        reach = saved = 0
        try:
            ins = get(f"{m['id']}/insights", {"metric": "reach,saved"}).get("data", [])
            for i in ins:
                v = (i.get("values") or [{}])[0].get("value", 0) or 0
                if i["name"] == "reach": reach = v
                if i["name"] == "saved": saved = v
        except Exception:
            pass
        posts.append({"id": m["id"], "tipo": m.get("media_type"), "quando": m.get("timestamp", "")[:10],
                      "gancho": (m.get("caption") or "").split("\n")[0][:70],
                      "reach": reach, "saved": saved, "likes": m.get("like_count", 0),
                      "coments": m.get("comments_count", 0), "link": m.get("permalink")})
    hist_p = os.path.join(ROOT, "analysis.json")
    hist = json.load(open(hist_p, encoding="utf-8-sig")) if os.path.exists(hist_p) else {"dias": {}, "recorde": 0}
    hist["dias"][hoje] = {"seguidores": perfil.get("followers_count", 0),
                          "alcance_total": sum(p["reach"] for p in posts)}
    hist["dias"] = {k: hist["dias"][k] for k in sorted(hist["dias"])[-90:]}

    top = sorted(posts, key=lambda p: -p["reach"])
    recorde_novo = top and top[0]["reach"] > hist.get("recorde", 0)
    if recorde_novo: hist["recorde"] = top[0]["reach"]
    json.dump(hist, open(hist_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    reels = [p for p in posts if p["tipo"] == "VIDEO"]; outros = [p for p in posts if p["tipo"] != "VIDEO"]
    med = lambda xs: round(sum(x["reach"] for x in xs) / len(xs), 1) if xs else 0
    L = [f"# 📈 Análise de engajamento — {now.strftime('%d/%m/%Y %H:%M')}", ""]
    L += [f"Seguidores: **{perfil.get('followers_count',0)}** · Posts: {perfil.get('media_count',0)} · Alcance médio: reels **{med(reels)}** vs demais **{med(outros)}**", ""]
    L.append("## 🏆 Top 5 por alcance")
    for p in top[:5]:
        L.append(f"1. **{p['reach']}** ({p['tipo']}, {p['quando']}, {p['saved']} salvos) — {p['gancho']}")
    L += ["", "## 🧭 Recomendações (regra: números mandam)"]
    if med(reels) > med(outros): L.append(f"- Reels alcançam {med(reels)}x{med(outros)} dos demais -> manter reels-first.")
    if top: L.append(f"- Replicar o ângulo do nº1: \"{top[0]['gancho']}\"")
    salv = sorted(posts, key=lambda p: -p["saved"])[:1]
    if salv and salv[0]["saved"] > 0: L.append(f"- Post mais salvo: {salv[0]['gancho']} -> tema pra série.")
    open(os.path.join(ROOT, "analysis.md"), "w", encoding="utf-8").write("\n".join(L))

    dow = now.weekday()  # 6=domingo
    if recorde_novo:
        open(os.path.join(ROOT, "_issue_analyst.txt"), "w", encoding="utf-8").write(
            f"🏆 NOVO RECORDE de alcance: {hist['recorde']}\n\n" + "\n".join(L))
    elif dow == 6:
        open(os.path.join(ROOT, "_issue_analyst.txt"), "w", encoding="utf-8").write("\n".join(L))
    print(f"analysis ok: {len(posts)} posts, recorde={'NOVO ' if recorde_novo else ''}{hist['recorde']}")

if __name__ == "__main__":
    main()
