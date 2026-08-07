# -*- coding: utf-8 -*-
"""
faxina — POP: pop/POP-faxina.md
Mantem o repositorio leve: posts JA PUBLICADOS ha mais de N dias perdem a midia
pesada (mp4/slides) e ficam so com uma miniatura (thumb.jpg) + legenda.
Seguro: depois de publicado, o Instagram guarda a propria copia da midia.

Env: DIAS (padrao 30) · DRY (1 = so simula, nao apaga)
"""
import os, json, glob, subprocess
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(ROOT, "queue.json")
POSTS = os.path.join(ROOT, "posts")
DIAS = int(os.environ.get("DIAS", "30"))
DRY = os.environ.get("DRY", "") == "1"

def mb(b):
    return round(b / 1048576.0, 2)

def miniatura(pasta):
    """Cria thumb.jpg (320px) a partir do reel ou do 1o slide. Retorna True se criou."""
    destino = os.path.join(pasta, "thumb.jpg")
    if os.path.exists(destino):
        return True
    mp4 = glob.glob(os.path.join(pasta, "*.mp4"))
    slides = sorted(glob.glob(os.path.join(pasta, "slide*.jpg")))
    fonte = mp4[0] if mp4 else (slides[0] if slides else None)
    if not fonte:
        return False
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    if fonte.endswith(".mp4"):
        cmd += ["-ss", "1", "-i", fonte, "-frames:v", "1"]
    else:
        cmd += ["-i", fonte]
    cmd += ["-vf", "scale=320:-2", "-q:v", "6", destino]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
        return os.path.exists(destino)
    except Exception as e:
        print(f"    miniatura falhou: {str(e)[:100]}")
        return False

def main():
    if not os.path.exists(QUEUE):
        print("sem queue.json"); return
    fila = json.load(open(QUEUE, encoding="utf-8-sig"))
    corte = datetime.now() - timedelta(days=DIAS)
    liberado = 0
    arquivados = []
    for item in fila:
        if item.get("status") != "published" or item.get("arquivado"):
            continue
        quando = item.get("published_at") or item.get("when")
        try:
            d = datetime.strptime(quando, "%Y-%m-%d %H:%M")
        except Exception:
            continue
        if d > corte:
            continue
        pasta = os.path.join(POSTS, item["name"])
        if not os.path.isdir(pasta):
            item["arquivado"] = True
            continue
        pesados = glob.glob(os.path.join(pasta, "*.mp4")) + glob.glob(os.path.join(pasta, "slide*.jpg"))
        if not pesados:
            item["arquivado"] = True
            continue
        tamanho = sum(os.path.getsize(f) for f in pesados)
        print(f">>> {item['name']} ({quando}) — {len(pesados)} arquivo(s), {mb(tamanho)} MB")
        if DRY:
            print("    [simulacao] seria arquivado")
            liberado += tamanho
            arquivados.append(item["name"])
            continue
        if not miniatura(pasta):
            print("    sem miniatura — mantendo a midia por seguranca")
            continue
        for f in pesados:
            os.remove(f)
        item["arquivado"] = True
        item["thumb"] = True
        liberado += tamanho
        arquivados.append(item["name"])
        print(f"    arquivado (miniatura mantida)")

    if arquivados and not DRY:
        json.dump(fila, open(QUEUE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    total_repo = 0
    for raiz, _, arqs in os.walk(POSTS):
        for a in arqs:
            total_repo += os.path.getsize(os.path.join(raiz, a))
    resumo = (f"faxina: {len(arquivados)} post(s) arquivado(s), {mb(liberado)} MB liberados; "
              f"midia restante: {mb(total_repo)} MB")
    print(resumo)
    if arquivados and not DRY:
        open(os.path.join(ROOT, "_faxina.txt"), "w", encoding="utf-8").write(
            resumo + "\n\n" + "\n".join(f"- {n}" for n in arquivados))

if __name__ == "__main__":
    main()
