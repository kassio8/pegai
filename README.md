# Baixaryt

Baixador interativo de vídeos e áudio do YouTube, feito em Python com `yt-dlp`.

**Criador: kassio8**

## Requisitos

- Python 3.11 ou superior. O `yt-dlp` atual requer essa versão mínima. [Downloads do Python](https://www.python.org/downloads/) · [Requisitos do yt-dlp](https://github.com/yt-dlp/yt-dlp#dependencies)
- Internet na primeira inicialização, para instalar as dependências, e durante os downloads.
- Ao iniciar fora de uma venv, permissão para gravar na pasta do projeto, onde o programa cria `.venv`.
- Um terminal para interagir com o menu.

O arquivo `.py` não inclui Python. Instale Python antes de iniciar o programa.

## Instalação e primeira execução

1. Baixe ou copie o projeto para uma pasta gravável.
2. Abra um terminal nessa pasta.
3. Inicie o script:

   **Windows (PowerShell ou Prompt de Comando):**

   ```powershell
   py --version
   py baixar_youtube_autodetect.py
   ```

   **macOS ou Linux:**

   ```sh
   python3 --version
   python3 baixar_youtube_autodetect.py
   ```

Quando iniciado fora de uma venv, o programa cria `.venv` e instala automaticamente `yt-dlp`, Deno e FFmpeg portátil. A instalação pode levar alguns minutos e baixar arquivos grandes. Não precisa ativar a venv nem instalar pacotes manualmente.

Se iniciar o script dentro de outra venv já ativa, ele usa essa venv e instala nela as dependências que faltarem. Caso contrário, usa a `.venv` do projeto.

Cada PC cria sua própria venv. Não copie `.venv` entre computadores ou sistemas operacionais.

## Como usar

1. Cole a URL do vídeo.
2. Escolha uma opção:
   - **1:** vídeo na melhor qualidade disponível.
   - **2:** escolha uma qualidade da lista.
   - **3:** áudio em MP3, qualidade 192 kbps.
3. Informe a pasta de destino ou pressione Enter para usar `Downloads` ou `Download`. Se nenhuma existir, o programa usa sua pasta pessoal.
4. Responda `s` para iniciar outro download ou `n` para sair.

O programa baixa um vídeo por vez; playlists ficam desativadas. Ele cria a pasta de destino quando necessário.

## Como funciona

- Ao iniciar, verifica a versão do Python e as dependências.
- Fora de uma venv, cria ou reaproveita `.venv` e reinicia o programa com o Python dela.
- Instala `yt-dlp[default,deno]`, que inclui os componentes EJS do yt-dlp e Deno, além de `imageio-ffmpeg`. [Guia EJS do yt-dlp](https://github.com/yt-dlp/yt-dlp/wiki/ejs)
- Procura FFmpeg no sistema, na pasta local `ffmpeg/` e no pacote portátil. O pacote fornece binários para plataformas comuns; confira seus limites de sistema e arquitetura no [README do imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg).
- Usa FFmpeg para mesclar faixas separadas de áudio e vídeo e para converter áudio em MP3.

As dependências não ficam presas a versões específicas. Para atualizá-las manualmente:

**Windows:**

```powershell
.venv\Scripts\python.exe -m pip install --upgrade "yt-dlp[default,deno]" imageio-ffmpeg
```

**macOS ou Linux:**

```sh
.venv/bin/python -m pip install --upgrade "yt-dlp[default,deno]" imageio-ffmpeg
```

Se usar outra venv, rode `python -m pip install --upgrade "yt-dlp[default,deno]" imageio-ffmpeg` com ela ativa.

## Testes

Execute na pasta do projeto:

**Windows:**

```powershell
py -m unittest -v test_baixar_youtube_autodetect.py
py -m py_compile baixar_youtube_autodetect.py test_baixar_youtube_autodetect.py
```

**macOS ou Linux:**

```sh
python3 -m unittest -v test_baixar_youtube_autodetect.py
python3 -m py_compile baixar_youtube_autodetect.py test_baixar_youtube_autodetect.py
```

## Problemas comuns

- **Python antigo:** instale Python 3.11 ou superior.
- **Falha ao criar a venv:** confirme que Python inclui `venv` e `pip`, que a pasta do projeto permite gravação e que há internet.
- **Falha ao encontrar FFmpeg:** reinstale as dependências ou instale FFmpeg no sistema e deixe o executável disponível no PATH. Algumas arquiteturas ou versões antigas de Linux podem não ter um binário portátil compatível.
- **Vídeo indisponível:** confira a URL e restrições de acesso. Mudanças no YouTube também podem exigir uma atualização do `yt-dlp`.
