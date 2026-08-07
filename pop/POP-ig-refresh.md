# POP — ig-refresh (renovação de token)
**Objetivo:** o token do Instagram nunca expirar (validade 60 dias).
**Gatilho:** cron a cada 20 dias + dispatch. Local: tarefa Windows homônima renova o .env.
**Passos:** GET /refresh_access_token -> grava o novo token no secret IG_TOKEN via API do GitHub (criptografia libsodium).
**Erros:** falha -> issue andon URGENTE (sem token o motor inteiro para). Se expirar de vez: gerar token novo no painel Meta (ver memória instagram-publishing-setup).
**Futuro:** renovação do token do Facebook (60d) e do Threads (60d) entram aqui quando as chaves forem fornecidas.
