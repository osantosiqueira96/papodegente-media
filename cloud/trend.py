# -*- coding: utf-8 -*-
"""
trend-scout — pauta do dia (POP: pop/POP-trend-scout.md)
Fontes: Google Trends BR (RSS) + G1 Economia (RSS). Gera cloud/pauta.md;
o workflow abre a issue (-> e-mail). Sem API paga, so stdlib.
"""
import os, urllib.request, xml.etree.ElementTree as ET, re, unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Sao_Paulo")
NICHO = ["dinheiro","imposto","pix","banco","salario","salário","inflacao","inflação","juros","selic",
         "golpe","aposentadoria","inss","fgts","cartao","cartão","divida","dívida","financiamento",
         "aluguel","conta de luz","gasolina","bolsa familia","bolsa família","13o","décimo","ia",
         "inteligencia artificial","inteligência artificial","nubank","caixa","real","dolar","dólar","preço","preco"]

def norm(s):
    return unicodedata.normalize("NFD", (s or "").lower()).encode("ascii","ignore").decode()

def fetch_rss(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (papodegente-trend-scout)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        root = ET.fromstring(r.read())
    items = []
    for it in root.iter("item"):
        t = it.findtext("title") or ""
        if t: items.append(t.strip())
    return items

def main():
    hoje = datetime.now(TZ).strftime("%d/%m/%Y")
    trends, g1 = [], []
    try:
        trends = fetch_rss("https://trends.google.com.br/trending/rss?geo=BR")[:20]
    except Exception as e:
        print("trends falhou:", e)
    try:
        g1 = fetch_rss("https://g1.globo.com/rss/g1/economia/")[:15]
    except Exception as e:
        print("g1 falhou:", e)

    nicho_norm = [norm(k) for k in NICHO]
    def eh_nicho(t):
        tn = norm(t)
        return any(k in tn for k in nicho_norm)

    quentes = [t for t in trends + g1 if eh_nicho(t)]
    vistos = set(); quentes = [t for t in quentes if not (norm(t) in vistos or vistos.add(norm(t)))]

    L = [f"# 🗞️ Pauta do dia — @papodegentebr ({hoje})", ""]
    L.append("## 🔥 Assunto do momento × nosso nicho (prioridade máxima)")
    if quentes:
        for t in quentes[:8]:
            L.append(f"- **{t}**")
            L.append(f"  - Ângulo: gancho de curiosidade → o que muda no SEU bolso → CTA 'salva e segue'")
    else:
        L.append("- (nenhum cruzamento hoje — usar a lane padrão: dinheiro no dia a dia)")
    L.append("")
    L.append("## 📈 Google Trends BR (top do dia)")
    for t in trends[:10]: L.append(f"- {t}")
    L.append("")
    L.append("## 📰 G1 Economia (manchetes)")
    for t in g1[:10]: L.append(f"- {t}")
    L.append("")
    L.append("## 📏 Diretrizes (POP)")
    L.append("- Assunto do momento primeiro · antirrepetição (conferir aba Controle) · reels-first")
    L.append("- Formato vencedor: curiosidade IA/tech amarrada no bolso (140 de alcance = 35× média)")
    L.append("- Estrutura: Gancho(3s) → Valor(1 ideia) → CTA 'salva e segue @papodegentebr'")

    # ---- Roteiro do dia do Professor PG (formato personagem IA) ----
    tema = quentes[0] if quentes else "as tarifas escondidas que comem seu salário"
    BLOCO = ("Uma capivara antropomórfica professora de finanças, estilo Pixar 3D, pelagem marrom-avermelhada, "
             "óculos redondos dourados, colete marrom, gravata roxa com cifrões, em sala de aula com lousa escura "
             "cheia de anotações de dinheiro em giz colorido, iluminação de estúdio quente. "
             "FORMATO OBRIGATÓRIO: vídeo VERTICAL 9:16 (celular), personagem centralizado. "
             "LEGENDAS: as frases faladas aparecem como legenda grande em português do Brasil, letras brancas com "
             "contorno preto, no TERÇO CENTRAL da tela, estilo reel viral.")
    cenas = [
        ("Ela arregala os olhos em choque cômico segurando um jornal.",
         f"Você viu isso?! {tema}... e ninguém te explica o que muda no SEU bolso!"),
        ("Ela levanta o dedo como professora e bate a ponteira na lousa.",
         "Calma. O Professor PG explica: o que importa é quanto sai do seu salário no fim do mês."),
        ("Ela mostra uma calculadora para a câmera com expressão de segredo revelado.",
         "Faz a conta comigo: anota o gasto, corta um exagero e guarda a diferença. Todo mês."),
        ("Ela cruza os braços, pisca e faz joinha para a câmera.",
         "Simples assim. A capivara aprova! Segue o papo de gente pra mais aulas!"),
    ]
    L += ["", "## 🦫 Roteiro do dia — Professor PG (cola no Gemini, 1 por vez)", f"**Tema:** {tema}", ""]
    for i, (acao, fala) in enumerate(cenas, 1):
        extra = ' No final aparece na tela em letras grandes douradas: "SEGUE @papodegentebr".' if i == 4 else ""
        L.append(f"**Prompt {i}:**")
        L.append("```")
        L.append(f'{BLOCO} {acao} Ela fala em português brasileiro: "{fala}". 8 segundos.{extra}')
        L.append("```")
    L.append("**Depois:** salve como 01.mp4...04.mp4 em `Identidade Visual\\Mascote PG\\videos\\inbox` — o PG-Builder monta, agenda e publica sozinho.")

    try:
        rad = os.path.join(os.path.dirname(os.path.abspath(__file__)), "radar.md")
        if os.path.exists(rad):
            L.append("")
            L.append(open(rad, encoding="utf-8-sig").read())
    except Exception as e:
        print("radar nao incluido:", e)
    open("cloud/pauta.md", "w", encoding="utf-8").write("\n".join(L))
    print(f"pauta gerada: {len(quentes)} match(es) de nicho, {len(trends)} trends, {len(g1)} manchetes")

if __name__ == "__main__":
    main()
