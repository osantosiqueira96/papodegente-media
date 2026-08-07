# POP — content-factory v1 (fábrica na nuvem)
**Objetivo:** produzir ESTÁTICOS e CARROSSÉIS sem PC: spec JSON -> slides renderizados -> fila.
**Gatilho:** push de factory/spec-*.json + dispatch.
**Spec:** name (Estatico-XX---Tema), type (photo|carousel), when (YYYY-MM-DD HH:MM), caption, slides[] com eyebrow/title/body/callout.
**Passos:** 1) instala chromium (playwright); 2) renderiza cada slide no template oficial (1080x1350, roxo/dourado, balão PG, callout de dado na capa); 3) commit em cloud/posts/NOME/ + legenda.txt; 4) adiciona o item na queue.json (retry/poka-yoke); 5) move a spec pra factory/done/.
**Regras do template:** capa com número/callout; até 30 palavras por slide; último slide = CTA salva e segue @papodegentebr.
**v2 (fila):** reels na nuvem (voz Piper + ffmpeg no runner).
**Erros:** issue andon; spec inválida = issue explicando o campo errado.
