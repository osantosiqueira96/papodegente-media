# POP — rotina_planilha (Windows 8h50)
**Objetivo:** planilha de controle sempre atual sem trabalho manual.
**Gatilho:** tarefa Windows 8h50; se o PC estava desligado, roda ao ligar (StartWhenAvailable).
**Passos:** 1) baixa metrics.json + queue.json; 2) Painel: seguidores/posts/agendados/alcance/atualizado-em; 3) Evolução: 1 linha por dia (atualiza a de hoje se existir) + ganho vs último valor; 4) Controle: Agendado vencido -> Publicado.
**Regras:** NUNCA apagar histórico; NUNCA sobrescrever Positiva/Negativas/Lean (são do ciclo kaizen humano+Claude); aprendizado validado por números NÃO é defeito nem cancelada — status "Virou diretriz".
**Falha comum:** planilha aberta no Excel = arquivo travado -> fechar o Excel e rodar de novo.
