# POP — trend-scout (pauta do dia 7h30)
**Objetivo:** e-mail diário com o assunto do momento ANTES de produzir (diretriz: assunto do momento primeiro).
**Gatilho:** crons 10:30/10:50 UTC (7h30/7h50 BRT) + nudge (cloud/trend_nudge.txt).
**Fontes:** Google Trends BR (RSS) + G1 Economia (RSS). Sem API paga.
**Passos:** 1) baixa as fontes; 2) cruza com palavras do nicho (dinheiro, imposto, pix, banco, salário, inflação, juros, golpe, aposentadoria, IA...); 3) monta a pauta: matches do nicho + trends gerais + manchetes, com ângulo Gancho->Valor->CTA sugerido; 4) issue de pauta -> e-mail.
**Anti-duplicata:** issue com a data de hoje já existe -> pula (cron).
**Uso:** o Claude lê a pauta na Janela 1 da rotina e propõe os posts do dia. Antirrepetição: conferir a aba Controle antes de aprovar tema.
