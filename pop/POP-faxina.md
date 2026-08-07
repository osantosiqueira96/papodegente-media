# POP - faxina (domingo 3h)
**Objetivo:** manter o repositorio leve (limite pratico do GitHub Pages: ~1 GB; hoje ~75 MB, cada reel ~5 MB).
**Regra:** post com status=published ha mais de 30 dias tem a midia pesada (mp4 e slides) trocada por uma miniatura thumb.jpg de 320px. A legenda permanece.
**Por que e seguro:** depois de publicado, o Instagram guarda a propria copia da midia - o arquivo no repo so servia para o upload. O original de producao continua no PC (pasta Conteudo).
**Nunca arquiva:** post pendente, post com erro, post publicado ha menos de 30 dias, e nao apaga se a miniatura falhar (seguranca primeiro).
**Gatilho:** cron domingo 06:00 UTC (3h BRT) + nudge (cloud/faxina_nudge.txt) + botao no app. Suporta simulacao: workflow_dispatch com dry=1 mostra o que seria arquivado sem apagar nada.
**Saida:** issue "Faxina" com o que foi arquivado e quantos MB foram liberados; a fila marca arquivado=true e o Previews passa a usar a miniatura.
