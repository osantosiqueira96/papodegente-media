# POP — dashboard-agent (rotina nuvem 8h34)
**Objetivo:** manter o dashboard (artifact claude.ai) com os números do dia. Tarefa MECÂNICA.
**Antes de começar:** ler este POP (pop/POP-dashboard-agent.md no repo).
**Passos:** 1) baixar dashboard/central.html + cloud/metrics.json + cloud/queue.json (raw.githubusercontent); 2) editar SOMENTE: data do eyebrow, números north-star, tags PUBLICADO da esteira, avisos de erro; 3) republicar SEMPRE com url=https://claude.ai/code/artifact/16746404-173e-4e6a-9634-cfe6fe26dcad (sem esse url cria link novo — PROIBIDO).
**Não fazer:** redesenhar layout; inventar números (fonte = metrics.json).
**Se metrics.json tiver mais de 26h:** publicar só com data nova + aviso de verificar o ig-report.
**Sincronia:** quem editar o dashboard manualmente DEVE commitar a cópia em dashboard/central.html (é a base deste agente).
