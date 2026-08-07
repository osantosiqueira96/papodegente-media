# POP — threads-mirror (espelhamento no Threads)
**Objetivo:** todo post do IG sai também no Threads (2 redes, 1 esforço).
**Onde vive:** dentro do publish.py (função threads_mirror), logo após o IG publicar.
**Estado:** DORMENTE até existirem os secrets THREADS_USER_ID e THREADS_TOKEN.
**Ativação:** 1) Yuri manda a Chave secreta do Threads + adiciona a redirect URI + aceita testador; 2) OAuth -> código -> token curto -> trocar por longo (60d); 3) gravar secrets; 4) renovação entra no ig-refresh.
**Regras:** reel -> VIDEO; foto/carrossel -> IMAGE (1º slide); legenda cortada em 480 chars; falha no Threads NUNCA bloqueia o IG (só loga); registrar threads_id no item da fila.
