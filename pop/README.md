# 📚 POPs — Procedimentos Operacionais Padrão dos robôs @papodegentebr

**Regra de ouro: TODO agente (Claude, rotina da nuvem ou humano) consulta o POP do robô ANTES de alterá-lo ou operá-lo.**

| Robô | POP | Onde roda |
|---|---|---|
| ig-publish | POP-ig-publish.md | GitHub Actions (30/30min) |
| ig-report | POP-ig-report.md | GitHub Actions (8h00/20/40) |
| ig-comment (comment-bot) | POP-ig-comment.md | GitHub Actions (15/15min) |
| ig-refresh | POP-ig-refresh.md | GitHub Actions (20 dias) |
| dashboard-agent | POP-dashboard-agent.md | Rotina nuvem Claude (8h34) |
| rotina_planilha | POP-rotina-planilha.md | Windows (8h50 ou ao ligar) |
| trend-scout | POP-trend-scout.md | GitHub Actions (7h30) |
| content-factory | POP-content-factory.md | GitHub Actions (por spec) |
| threads-mirror | POP-threads-mirror.md | dentro do ig-publish |

## Regras invioláveis do projeto (valem pra todos)
1. **Números > linha editorial** (Regra-mestra): o que der seguidor/alcance manda.
2. **Proibido**: comprar seguidor, bot de engajamento/follow, rajada de posts (espaçar >=2h).
3. **Anti-frágil**: nenhum robô confia num único cron -> retry + gatilho manual por arquivo (nudge).
4. **Andon**: toda falha vira issue (-> e-mail). Falha silenciosa é o pior defeito.
5. **Fonte da verdade**: fila = cloud/queue.json · números = cloud/metrics.json · fluxos = cloud/flows.json.
6. **Kaizen**: erro novo -> registrar (Negativas) -> resolver -> registrar solução (Positiva). Aprendizado validado por números NÃO é defeito nem cancelada — vira "Virou diretriz".
