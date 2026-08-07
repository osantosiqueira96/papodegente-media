# POP — ig-comment (comment-bot / motor de venda)
**Objetivo:** palavra-gatilho no comentário -> resposta pública + DM com link (nosso ManyChat).
**Gatilho:** cron 15/15min + push em cloud/flows.json (salvar no PG Flows dispara na hora).
**Entradas:** cloud/flows.json (editar em https://osantosiqueira96.github.io/papodegente-media/flows/), cloud/bot_state.json (já processados).
**Passos:** 1) lista comentários dos últimos 10 posts; 2) ignora usuários da lista e já-processados; 3) match contains/exact sem acento/caixa; 4) responde comentário e/ou private reply (DM); 5) grava bot_state.
**Limitação conhecida (07/08):** app em modo Desenvolvimento -> a API só mostra comentários de TESTADORES do app. Destrave: perfil pessoal como Testador do Instagram (aceitar convite) OU modo Live.
**Não fazer:** responder 2x o mesmo comentário (bot_state é a trava); apagar bot_state sem motivo.
**Anti-spam:** config.max_acoes_por_ciclo (padrão 20).
