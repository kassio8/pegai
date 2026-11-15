![Pegaí](assets/banner-Pegai.svg)

# Pegaí

Script de terminal para baixar vídeos do YouTube ou extrair áudio em MP3.

## Executar

```sh
# Windows
py baixar_youtube_autodetect.py

# macOS e Linux
python3 baixar_youtube_autodetect.py
```

## Opções

- **Melhor qualidade:** baixa o vídeo na melhor qualidade disponível.
- **Escolher resolução:** lista as resoluções disponíveis para o vídeo.
- **MP3:** extrai o áudio em 192 kbps.

## Requisitos

Python 3.11+, internet e permissão de escrita na pasta do projeto; na primeira execução, o script cria `.venv` e instala `yt-dlp[default,deno]` e `imageio-ffmpeg`.

## Licença

MIT. Criador: kassio8. Consulte [LICENSE](LICENSE).
