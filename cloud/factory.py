# -*- coding: utf-8 -*-
"""
content-factory v1 — POP: pop/POP-content-factory.md
Le factory/spec-*.json, renderiza slides 1080x1350 no template oficial
(playwright/chromium) e coloca o post na fila da nuvem.
"""
import os, json, glob, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))          # cloud/
BASE = os.path.dirname(ROOT)                               # raiz do repo
FACTORY = os.path.join(BASE, "factory")
QUEUE = os.path.join(ROOT, "queue.json")

TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;overflow:hidden;font-family:Arial,Helvetica,sans-serif;
 background:radial-gradient(120% 90% at 18% 0%,#241042,#150925 70%);color:#F3EDFA;
 display:flex;flex-direction:column;justify-content:center;padding:90px 84px;position:relative}
.eyebrow{font-size:26px;letter-spacing:6px;text-transform:uppercase;color:#A374FF;font-weight:700;margin-bottom:34px}
.callout{display:inline-block;background:#FFD100;color:#261442;font-weight:900;font-size:44px;
 padding:12px 30px;border-radius:16px;margin-bottom:38px;max-width:850px}
h1{font-size:__TSIZE__px;font-weight:900;line-height:1.14;letter-spacing:-1px;margin-bottom:36px;white-space:pre-line}
h1 b,h1 strong{color:#FFD100}
.body{font-size:40px;line-height:1.4;color:#D9CCEF;max-width:880px;white-space:pre-line}
.pg{position:absolute;top:64px;right:70px;background:#FFD100;color:#261442;font-weight:900;
 font-size:34px;padding:10px 22px;border-radius:14px}
.pg:after{content:"";position:absolute;bottom:-14px;left:24px;border:10px solid transparent;border-top:16px solid #FFD100}
.cta{position:absolute;bottom:72px;left:84px;font-size:30px;color:#B8A6D9}
.cta b{color:#FFD100}
</style></head><body>
<div class="pg">PG</div>
__EYEBROW__ __CALLOUT__
<h1>__TITLE__</h1>
__BODY__
<div class="cta">💾 salva &nbsp;·&nbsp; ➕ segue <b>@papodegentebr</b></div>
</body></html>"""

def render_slide(page, slide, out_path):
    title = slide.get("title", "")
    tsize = 88 if len(title) <= 90 else 72
    html = (TPL.replace("__TSIZE__", str(tsize))
              .replace("__EYEBROW__", f'<div class="eyebrow">{slide.get("eyebrow","papo de gente · dinheiro no dia a dia")}</div>' if slide.get("eyebrow", True) else "")
              .replace("__CALLOUT__", f'<div class="callout">{slide["callout"]}</div>' if slide.get("callout") else "")
              .replace("__TITLE__", title)
              .replace("__BODY__", f'<div class="body">{slide["body"]}</div>' if slide.get("body") else ""))
    page.set_content(html)
    page.screenshot(path=out_path, type="jpeg", quality=92)

def add_to_queue(item):
    q = json.load(open(QUEUE, encoding="utf-8-sig")) if os.path.exists(QUEUE) else []
    if any(x.get("name") == item["name"] for x in q):
        print(f"  fila: {item['name']} ja existe — pulando")
        return
    q.append(item)
    json.dump(q, open(QUEUE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  fila: + {item['name']} @ {item['when']}")

def main():
    specs = sorted(glob.glob(os.path.join(FACTORY, "spec-*.json")))
    if not specs:
        print("nenhuma spec nova")
        return
    from playwright.sync_api import sync_playwright
    done_dir = os.path.join(FACTORY, "done")
    os.makedirs(done_dir, exist_ok=True)
    errs = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        for spec_path in specs:
            try:
                s = json.load(open(spec_path, encoding="utf-8-sig"))
                for k in ("name", "type", "when", "caption", "slides"):
                    if k not in s:
                        raise ValueError(f"spec sem campo obrigatorio: {k}")
                out = os.path.join(ROOT, "posts", s["name"])
                os.makedirs(out, exist_ok=True)
                for i, sl in enumerate(s["slides"], 1):
                    render_slide(page, sl, os.path.join(out, f"slide{i}.jpg"))
                open(os.path.join(out, "legenda.txt"), "w", encoding="utf-8").write(s["caption"])
                add_to_queue({"name": s["name"], "type": s["type"], "when": s["when"], "status": "pending"})
                shutil.move(spec_path, os.path.join(done_dir, os.path.basename(spec_path)))
                print(f"OK {s['name']}: {len(s['slides'])} slide(s)")
            except Exception as e:
                errs.append(f"{os.path.basename(spec_path)}: {e}")
                print(f"ERRO {spec_path}: {e}")
        browser.close()
    if errs:
        open(os.path.join(ROOT, "_alert.txt"), "w", encoding="utf-8").write("\n".join(errs))
        sys.exit(0)  # andon cuida; nao derruba o run

if __name__ == "__main__":
    main()
