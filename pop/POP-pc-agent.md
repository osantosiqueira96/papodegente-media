# POP - pc-agent (ponte web -> PC, 3/3 min)
**Objetivo:** permitir disparar os robos LOCAIS (planilha, nudger, pg-builder) pelo app PG Central.
**Como funciona:** o botao Disparar do app grava requests/<robo>.json no repositorio -> o pc-agent (Tarefa do Windows, 3/3 min) le a pasta, executa o script correspondente, grava heartbeats/<robo>.json com o resultado e APAGA o pedido. O app acompanha o batimento e avisa quando termina.
**Requisito:** PC ligado. Com o PC desligado o pedido fica na fila e roda assim que ligar (a tarefa tem StartWhenAvailable).
**Robos atendidos:** planilha (rotina_planilha.py), nudger (publish_nudger.ps1), pg-builder (pg_builder.py).
**Nao fazer:** criar pedido com nome fora do mapa ROBOS (o agente ignora e loga); acumular pedidos repetidos - o app grava sempre no mesmo caminho, entao 1 pedido por robo por vez.
**Seguranca:** o pc-agent so executa scripts do mapa fixo ROBOS - nunca comandos vindos do arquivo de pedido.
