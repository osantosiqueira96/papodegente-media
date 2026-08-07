# POP — story-poster (17h30)
**Objetivo:** perfil vivo diariamente: story com o melhor post das últimas 24h.
**Gatilho:** crons 20:30/20:50 UTC + nudge (cloud/story_nudge.txt).
**Regras:** máximo 1 story/dia (story_state.json é a trava); fonte = post de maior alcance das últimas 26h (fallback: mais recente); vídeo -> usa thumbnail.
**Não fazer:** story de post com erro; mais de 1 repost do mesmo post.
