# POP — pg-builder (Professor PG, PC, 30/30min)
**Objetivo:** transformar clipes do Gemini/Veo em reel agendado, sem trabalho manual.
**Fluxo:** roteiro chega na pauta 7h30 (secao do Professor PG) -> Yuri gera os 4 clipes no Gemini -> salva como 01.mp4..04.mp4 em Identidade Visual\Mascote PG\videos\inbox -> builder converte pra 1080x1920 (fundo desfocado se horizontal), concatena na ordem, anexa assets\cta.mp4 e agenda na nuvem pras 15h de amanha.
**Regras:** so processa inbox "estavel" (nenhum arquivo com <2min — evita pegar upload pela metade); clipes processados vao pra videos\processados com data; legenda padrao criada se nao existir (editavel antes das 15h).
**Conferencia humana:** o Yuri DEVE assistir os clipes antes de por na inbox (IA erra grafia de legenda; @papodegentebr escrito errado = clipe fora).
**Custo zero.** Full-auto de verdade exige API paga do Veo (~R$25-35/reel) — decisao de negocio adiada ate o formato provar numeros.
