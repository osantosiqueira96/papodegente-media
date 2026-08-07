# -*- coding: utf-8 -*-
"""
RELATORIO DIARIO @papodegentebr (roda no GitHub Actions ~21h BRT).
North-star: SEGUIDORES + ALCANCE (regra 'guiado por numeros').
Gera report.md -> o workflow abre um issue (=> e-mail pro Yuri).
Env: IG_USER_ID, IG_TOKEN
"""
import os, json, requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

API="https://graph.instagram.com/v21.0"
IG=os.environ["IG_USER_ID"]; TOKEN=os.environ["IG_TOKEN"]
TZ=ZoneInfo("America/Sao_Paulo")
ROOT=os.path.dirname(os.path.abspath(__file__))

def get(path, params):
    r=requests.get(f"{API}/{path}", params={**params,"access_token":TOKEN}, timeout=60)
    r.raise_for_status(); return r.json()

now=datetime.now(TZ)
prof=get(IG, {"fields":"username,followers_count,media_count"})
media=get(f"{IG}/media", {"fields":"id,caption,media_type,timestamp,permalink,like_count,comments_count","limit":25}).get("data",[])

posts=[]
for m in media:
    ins={"reach":0,"saved":0,"shares":0,"total_interactions":0}
    try:
        for d in get(f"{m['id']}/insights", {"metric":"reach,saved,shares,total_interactions"}).get("data",[]):
            ins[d["name"]]=d["values"][0]["value"]
    except Exception:
        pass
    cap=(m.get("caption") or "").replace("\n"," ")[:60]
    ts=datetime.fromisoformat(m["timestamp"].replace("+0000","+00:00")).astimezone(TZ)
    posts.append({"quando":ts,"tipo":m["media_type"],"cap":cap,"likes":m.get("like_count",0),
                  "com":m.get("comments_count",0),**ins,"link":m.get("permalink","")})

rank=sorted(posts,key=lambda p:-p["reach"])[:5]
h24=[p for p in posts if p["quando"] > now-timedelta(hours=24)]

# fila da nuvem
qtxt=""
qp=os.path.join(ROOT,"queue.json")
if os.path.exists(qp):
    q=json.load(open(qp,encoding="utf-8-sig"))
    pend=[i for i in q if i.get("status")=="pending"]
    errs=[i for i in q if i.get("status")=="error"]
    pubs=[i for i in q if i.get("status")=="published"]
    qtxt=f"\n## Fila da nuvem\n- publicados: {len(pubs)} | pendentes: {len(pend)} | erros: {len(errs)}\n"
    for i in errs: qtxt+=f"- 🔴 ERRO: {i['name']} — {i.get('note','')[:120]}\n"
    for i in pend[:5]: qtxt+=f"- ⏳ {i['when']} — {i['name']}\n"

L=[]
L.append(f"# 📰 Relatório diário — @{prof['username']} ({now.strftime('%d/%m %H:%M')})")
L.append("")
L.append("## North-star (guiado por números)")
L.append(f"- **Seguidores: {prof['followers_count']}**")
L.append(f"- **Posts: {prof['media_count']}** | alcance total (25 últimos): **{sum(p['reach'] for p in posts)}**")
L.append("")
L.append("## Últimas 24h")
if h24:
    for p in h24:
        L.append(f"- {p['quando'].strftime('%H:%M')} {p['tipo']}: alcance **{p['reach']}**, likes {p['likes']}, coment. {p['com']}, salvos {p['saved']} — {p['cap']}")
else:
    L.append("- nenhum post nas últimas 24h ⚠️")
L.append("")
L.append("## 🏆 Ranking por ALCANCE (top 5)")
for i,p in enumerate(rank,1):
    L.append(f"{i}. **{p['reach']}** — {p['tipo']} {p['quando'].strftime('%d/%m')} — {p['cap']}")
if rank and rank[0]["reach"]>0:
    L.append(f"\n**Vencedor a estudar/replicar:** {rank[0]['cap']} ({rank[0]['reach']} alcance) — {rank[0]['link']}")
L.append(qtxt)
L.append("## Ciclo kaizen")
L.append("- Impedimentos/soluções: ver abas Lean + Negativas/Postiva da planilha de controle.")
L.append("- Próxima ação guiada por números: replicar o formato do vencedor acima.")

open(os.path.join(ROOT,"report.md"),"w",encoding="utf-8").write("\n".join(L)+"\n")
print("report.md gerado")
print("\n".join(L[:12]))
