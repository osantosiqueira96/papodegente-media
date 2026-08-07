# POP — ig-publish (publicador da nuvem)
**Objetivo:** publicar no Instagram (e espelhar no Threads) tudo que estiver vencido na fila, sem PC.
**Gatilho:** cron 30/30min + push em cloud/queue.json ou cloud/posts/**.
**Entradas:** cloud/queue.json (itens name/type/when/status), mídia em cloud/posts/NOME/ (slideN.jpg, *.mp4, legenda.txt), secrets IG_USER_ID/IG_TOKEN (+THREADS_* opcionais).
**Passos:** 1) lê a fila; 2) para cada pending vencido (hora de Brasília): cria container -> espera FINISHED -> publica; 3) marca published/error + post_id; 4) espelha no Threads se os secrets existirem (falha do Threads NUNCA bloqueia o IG); 5) commit da fila com retry 3x e poka-yoke (pula gravação vazia).
**Erros:** item vira status=error + nota; workflow abre issue andon -> e-mail.
**Não fazer:** editar queue.json sem o sha atual; remover o [skip ci] do commit da fila.
**Regra:** horário nobre = 12h/15h/19h/21h; nunca 2 posts com menos de 2h de intervalo (anti-rajada).
