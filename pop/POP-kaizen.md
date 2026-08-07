# POP - agente-kaizen (22h)
**Objetivo:** rodar o ciclo DETECTAR -> RESOLVER -> REGISTRAR sozinho, sempre por EVIDENCIA (nunca achismo).
**Gatilho:** crons 01:00/01:20 UTC (22h/22h20 BRT) + nudge (cloud/kaizen_nudge.txt) + botao no app.
**O que ele observa:** execucoes dos robos nas ultimas 24h (falha que se recuperou = positiva "retry salvou"; falha que persiste = negativa aberta), erros na fila, recorde de alcance, intervencao do nudger (desperdicio "espera"), comparacao reels x demais formatos.
**Memoria:** cloud/kaizen.json guarda todas as entradas + ids ja registrados (nunca duplica). cloud/kaizen.md e o corpo da issue do dia (apagado apos abrir).
**Saida:** issue "Ciclo Kaizen" marcando @osantosiqueira96 (vira e-mail) + sincronizacao automatica nas abas Postiva/Negativas/Lean pela rotina_planilha das 8h50 (marcador local kaizen_aplicados.json evita duplicar).
**Nao fazer:** registrar aprendizado sem evidencia numerica ou log; classificar como "defeito" um resultado validado por numeros (isso e diretriz - ver regra-mestra).
