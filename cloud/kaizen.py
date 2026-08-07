# -*- coding: utf-8 -*-
"""
agente-kaizen — POP: pop/POP-kaizen.md
Roda o ciclo DETECTAR -> RESOLVER -> REGISTRAR sozinho, com base em EVIDENCIA
(nunca achismo). Le: execucoes dos robos, fila, metricas, analise e batimentos.
Escreve: cloud/kaizen.json (memoria, sem duplicar) + cloud/kaizen.md (relatorio).
Se houver entrada nova, o workflow abre issue (-> e-mail).
"""
import os, json, urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("GITHUB_REPOSITORY", "osantosiqueira96/papodegente-media")
TOKEN = os.environ.get("GH_TOKEN", "")
TZ = ZoneInfo("America/Sao_Paulo")
KJ = os.path.join(ROOT, "kaizen.json")

def api(path):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/{path}",
                                 headers={"Authorization": "Bearer " + TOKEN,
                                          "Accept": "application/vnd.github+json",
                                          "User-Agent": "kaizen"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)

def arquivo(nome, padrao=None):
    p = os.path.join(ROOT, nome)
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8-sig"))
        except Exception:
            return padrao
    return padrao

NOMES = {"ig-publish.yml": "ig-publish", "ig-report.yml": "ig-report", "ig-comment.yml": "comment-bot",
         "ig-trend.yml": "trend-scout", "ig-analyst.yml": "engagement-analyst", "ig-story.yml": "story-poster",
         "ig-factory.yml": "content-factory", "ig-refresh.yml": "ig-refresh", "ig-competitor.yml": "competitor-watch",
         "ig-kaizen.yml": "agente-kaizen"}

def main():
    agora = datetime.now(TZ)
    hoje = agora.strftime("%Y-%m-%d")
    k = arquivo("kaizen.json", None) or {"entradas": [], "ids": []}
    ids = set(k.get("ids", []))
    novas = []

    def add(tipo, titulo, evidencia, acao, status, eid):
        if eid in ids:
            return
        ids.add(eid)
        e = {"id": eid, "data": hoje, "tipo": tipo, "titulo": titulo,
             "evidencia": evidencia, "acao": acao, "status": status}
        k["entradas"].append(e)
        novas.append(e)

    # ---------- 1) falhas de robo nas ultimas 24h (auto-resolvidas ou nao) ----------
    limite = datetime.now(timezone.utc) - timedelta(hours=24)
    try:
        runs = api("actions/runs?per_page=100").get("workflow_runs", [])
    except Exception as e:
        runs = []
        print("nao consegui ler runs:", e)
    recentes = [r for r in runs if r.get("path", "").endswith(".yml")
                and datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")) > limite]
    por_wf = {}
    for r in recentes:
        por_wf.setdefault(os.path.basename(r["path"]), []).append(r)
    for wf, lista in por_wf.items():
        nome = NOMES.get(wf, wf)
        falhas = [r for r in lista if r.get("conclusion") == "failure"]
        if not falhas:
            continue
        lista.sort(key=lambda r: r["created_at"])
        ultimo = lista[-1]
        recuperou = ultimo.get("conclusion") == "success"
        if recuperou:
            add("positiva", f"Retry salvou o {nome}",
                f"{len(falhas)} falha(s) nas ultimas 24h, mas a execucao seguinte deu certo (run {ultimo['id']}).",
                "Manter o padrao anti-fragil: todo robo com retry + gatilho manual.",
                "OK", f"pos-retry-{wf}-{hoje}")
        else:
            add("negativa", f"{nome} falhou e NAO se recuperou",
                f"{len(falhas)} falha(s) nas ultimas 24h; ultima execucao: {ultimo.get('conclusion')}.",
                f"Investigar o log da run {ultimo['id']} e corrigir a causa raiz.",
                "Aberta", f"neg-falha-{wf}-{hoje}")

    # ---------- 2) erros na fila ----------
    fila = arquivo("queue.json", []) or []
    for it in fila:
        if it.get("status") == "error":
            add("negativa", f"Post com erro na fila: {it.get('name')}",
                f"Motivo: {str(it.get('note', ''))[:160]}",
                "Corrigir a midia/legenda e reagendar; se for erro de API, checar token.",
                "Aberta", f"neg-fila-{it.get('name')}")

    # ---------- 3) recorde de alcance ----------
    ana = arquivo("analysis.json", {}) or {}
    rec = ana.get("recorde", 0)
    if rec and rec >= 100:
        add("positiva", f"Recorde de alcance: {rec}",
            f"Maior alcance ja registrado no perfil ({rec}).",
            "Replicar o formato/angulo do post recordista nas proximas pecas.",
            "OK", f"pos-recorde-{rec}")

    # ---------- 4) intervencao do nudger (desperdicio: espera) ----------
    hb = None
    try:
        with urllib.request.urlopen(
                f"https://raw.githubusercontent.com/{REPO}/main/heartbeats/nudger.json", timeout=30) as r:
            hb = json.load(r)
    except Exception:
        pass
    if hb and str(hb.get("quando", ""))[:10] == hoje and "cutucou" in str(hb.get("resultado", "")):
        add("lean", "Espera: o agendador do GitHub atrasou a publicacao",
            f"O nudger precisou intervir hoje ({hb.get('resultado')}).",
            "Nudger no PC (20/20min) + botao de disparo no app ja cobrem. Se repetir muito, encurtar o cron.",
            "Em execucao", f"lean-nudger-{hoje}")

    # ---------- 5) leitura de formato (reels x resto) ----------
    if os.path.exists(os.path.join(ROOT, "analysis.md")):
        txt = open(os.path.join(ROOT, "analysis.md"), encoding="utf-8-sig").read()
        import re
        m = re.search(r"reels \*\*([\d.]+)\*\* vs demais \*\*([\d.]+)\*\*", txt)
        if m:
            r1, r2 = float(m.group(1)), float(m.group(2))
            if r2 > 0 and r1 / max(r2, 0.1) >= 3:
                add("positiva", "Reels-first confirmado pelos numeros",
                    f"Alcance medio: reels {r1} vs demais {r2} ({round(r1/max(r2,0.1),1)}x).",
                    "Manter reels como formato principal da esteira.",
                    "OK", f"pos-reelsfirst-{hoje}")

    # ---------- grava ----------
    k["ids"] = sorted(ids)
    k["atualizado"] = agora.strftime("%Y-%m-%d %H:%M")
    json.dump(k, open(KJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if novas:
        L = [f"# ♻️ Ciclo Kaizen — {agora.strftime('%d/%m/%Y %H:%M')}", "",
             f"**{len(novas)} registro(s) novo(s)** detectados por evidencia (sem achismo).", ""]
        icone = {"positiva": "✅", "negativa": "⛔", "lean": "🔍"}
        for e in novas:
            L += [f"### {icone.get(e['tipo'],'•')} {e['titulo']}  \n`{e['tipo']}` · status: **{e['status']}**",
                  f"- **Evidencia:** {e['evidencia']}",
                  f"- **Acao:** {e['acao']}", ""]
        abertas = [e for e in k["entradas"] if e.get("status") == "Aberta"]
        L += ["---", f"**Impedimentos abertos no total: {len(abertas)}**"]
        for e in abertas[-5:]:
            L.append(f"- {e['titulo']} ({e['data']})")
        L += ["", "_A planilha de controle sincroniza estes registros na proxima rotina das 8h50._"]
        open(os.path.join(ROOT, "kaizen.md"), "w", encoding="utf-8").write("\n".join(L))
        print(f"kaizen: {len(novas)} entrada(s) nova(s)")
    else:
        print("kaizen: nada novo hoje (ciclo saudavel)")

if __name__ == "__main__":
    main()
