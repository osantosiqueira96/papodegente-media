# -*- coding: utf-8 -*-
"""
COMMENT-BOT @papodegentebr — nosso 'ManyChat' oficial e gratis.
Le cloud/flows.json (fluxos configuraveis), varre comentarios novos dos ultimos posts,
e executa: responder comentario (publico) + private reply (DM) por palavra-chave.
100% API oficial (sem risco de ban). Roda no GitHub Actions a cada 15 min.

Env: IG_USER_ID, IG_TOKEN
Estado: cloud/bot_state.json (ids ja processados) — commitado pelo workflow.
"""
import os, json, unicodedata, requests

API = "https://graph.instagram.com/v21.0"
IG = os.environ["IG_USER_ID"]
TOKEN = os.environ["IG_TOKEN"]
ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, "bot_state.json")
FLOWS = os.path.join(ROOT, "flows.json")

def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

def get(path, params):
    r = requests.get(f"{API}/{path}", params={**params, "access_token": TOKEN}, timeout=60)
    r.raise_for_status(); return r.json()

def post(path, data):
    r = requests.post(f"{API}/{path}", data={**data, "access_token": TOKEN}, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"{path}: {r.status_code} {r.text[:200]}")
    return r.json()

def load(p, default):
    if os.path.exists(p):
        try: return json.load(open(p, encoding="utf-8-sig"))
        except Exception: return default
    return default

def match(flow, texto):
    t = norm(texto)
    gats = [norm(g) for g in flow.get("gatilho", [])]
    m = flow.get("match", "contains")
    if m == "exact":
        return any(t.strip() == g for g in gats)
    if m == "any":
        return True
    return any(g in t for g in gats)

def main():
    cfg = load(FLOWS, {"config": {}, "flows": []})
    flows = [f for f in cfg.get("flows", []) if f.get("ativo")]
    if not flows:
        print("nenhum fluxo ativo — nada a fazer"); return
    ignore = {norm(u) for u in cfg.get("config", {}).get("ignorar_usuarios", [])}
    maxact = int(cfg.get("config", {}).get("max_acoes_por_ciclo", 20))
    state = load(STATE, {"processed": []})
    seen = set(state["processed"])
    acted = 0; errs = []

    media = get(f"{IG}/media", {"fields": "id,timestamp", "limit": 10}).get("data", [])
    for m in media:
        if acted >= maxact: break
        try:
            comments = get(f"{m['id']}/comments", {"fields": "id,text,username,timestamp", "limit": 50}).get("data", [])
        except Exception as e:
            errs.append(f"listar comentarios {m['id']}: {str(e)[:120]}"); continue
        for c in comments:
            if acted >= maxact: break
            cid = c["id"]
            if cid in seen: continue
            seen.add(cid)  # marca mesmo sem match (nao reprocessar)
            if norm(c.get("username", "")) in ignore: continue
            for f in flows:
                if not match(f, c.get("text", "")): continue
                print(f">>> fluxo '{f['id']}' disparado por @{c.get('username')}: {c.get('text','')[:60]}")
                try:
                    if f.get("responder_comentario"):
                        post(f"{cid}/replies", {"message": f["responder_comentario"]})
                        print("    respondido no comentario")
                    if f.get("dm"):
                        post(f"{IG}/messages", {
                            "recipient": json.dumps({"comment_id": cid}),
                            "message": json.dumps({"text": f["dm"]})})
                        print("    DM (private reply) enviada")
                    acted += 1
                except Exception as e:
                    errs.append(f"fluxo {f['id']} em {cid}: {str(e)[:150]}")
                    print(f"    ERRO: {e}")
                break  # 1 fluxo por comentario

    state["processed"] = list(seen)[-3000:]
    json.dump(state, open(STATE, "w", encoding="utf-8"), indent=1)
    print(f"ciclo ok: {acted} acao(oes), {len(errs)} erro(s)")
    if errs:
        open(os.path.join(ROOT, "_alert.txt"), "w", encoding="utf-8").write("COMMENT-BOT:\n" + "\n".join(errs))

if __name__ == "__main__":
    main()
