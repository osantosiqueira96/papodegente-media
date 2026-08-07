# POP — ig-report (relatório diário 8h)
**Objetivo:** e-mail diário com north-star (seguidores/alcance), últimas 24h, top 5 e estado da fila.
**Gatilho:** crons 11:00/11:20/11:40 UTC (8h00/20/40 BRT) + nudge (cloud/report_nudge.txt) + dispatch.
**Anti-duplicata:** se já existe issue com a data de hoje no título -> pula (só quando disparado por cron; nudge sempre roda).
**Passos:** 1) report.py consulta a API do IG; 2) grava cloud/metrics.json (fonte do dashboard e da planilha) + cloud/report.md; 3) commit; 4) abre issue com o github.token (author = github-actions -> a notificação por e-mail CHEGA).
**Erros:** falha de API -> issue andon. NUNCA criar a issue com o PAT do dono (GitHub suprime notificação da própria ação).
**Consumidores do metrics.json:** dashboard-agent (8h34) e rotina_planilha (8h50) — mudou o formato? Atualize os dois.
