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

Os arquivos são salvos como `Título [ID do vídeo].extensão`, para distinguir vídeos com o mesmo título.

## Requisitos

Python 3.11+, internet e permissão de escrita na pasta do projeto; na primeira execução, o script cria `.venv` e instala `yt-dlp[default,deno]` e `imageio-ffmpeg`.

Se a `.venv` existente estiver incompleta ou usar um Python incompatível, o Pegaí interrompe a inicialização. Renomeie a pasta para um nome livre, como `.venv.backup`, e execute o script novamente.

## Licença

MIT. Criador: kassio8. Consulte [LICENSE](LICENSE).
