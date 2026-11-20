![Pegaí](assets/banner-Pegai.svg)

# Pegaí

Baixe vídeos do YouTube ou transforme uma **playlist inteira de músicas em MP3** pelo terminal. Cada vídeo da playlist vira um arquivo de áudio a **192 kbps**.

## Como começar

Você precisa de **Python 3.11 ou superior**, conexão com a internet e permissão para gravar nas pastas do projeto e dos downloads.

1. Baixe e extraia o ZIP do projeto ou clone o repositório com `git clone https://github.com/kassio8/pegai.git`.
2. Abra o terminal na pasta que contém `baixar_youtube_autodetect.py`.
3. Execute o comando do seu sistema.

| Sistema | Comando |
| --- | --- |
| Windows | `py baixar_youtube_autodetect.py` |
| macOS ou Linux | `python3 baixar_youtube_autodetect.py` |

Na primeira execução, o Pegaí prepara o ambiente e instala o yt-dlp, o Deno e uma versão portátil do FFmpeg. Quando o menu aparecer, cole o link do YouTube e escolha o que deseja baixar.

## Qual opção escolher?

| Opção | O que você recebe |
| --- | --- |
| **1 — Vídeo (melhor qualidade)** | O vídeo na melhor qualidade disponível. Com o link direto de uma playlist, baixa os vídeos da lista. |
| **2 — Vídeo (escolher qualidade)** | Uma lista das resoluções disponíveis para o vídeo. Digite o número da resolução desejada. |
| **3 — Somente áudio (MP3)** | Um MP3 para um vídeo avulso ou um MP3 por vídeo da playlist. |

## Como baixar uma playlist de músicas

1. No YouTube, abra a **página da playlist** e copie o endereço que contém `youtube.com/playlist?list=...`.
2. Cole o endereço no Pegaí e escolha **3 — Somente áudio (MP3)**.
3. Digite uma pasta para guardar as músicas ou pressione **Enter** para usar a pasta sugerida. O Pegaí cria a pasta de destino se necessário.

> **Confira o link.** Um endereço com `watch?v=...&list=...` aponta para o vídeo que está tocando. Com esse link, o Pegaí baixa só aquele vídeo.

No teste com **PRODUTO DO AMBIENTE MIXTAPE**, os 12 vídeos geraram 12 MP3 a 192 kbps, totalizando 101 MB. Foram 11 faixas individuais e um arquivo de 35 minutos, porque a playlist também inclui um vídeo com a mixtape completa. [Ver a playlist do teste](https://www.youtube.com/playlist?list=PLvnkn1Ox2UftPf21azpttWSZJfqK0EDK9)

## Onde ficam os arquivos?

O menu mostra a pasta de destino antes de baixar. O Pegaí sugere `Downloads` ou `Download` dentro da sua pasta de usuário. Se nenhuma delas existir, sugere a própria pasta de usuário.

Cada arquivo inclui o título e o ID do vídeo, como `Minha música [abc123].mp3`. Assim, vídeos diferentes com o mesmo título têm arquivos distintos.

## Se aparecer um aviso sobre a .venv

A pasta `.venv` guarda o ambiente Python do projeto. Se ela estiver incompleta ou incompatível, o Pegaí para e preserva o conteúdo. Renomeie a pasta para um nome livre, como `.venv.backup`, e execute o comando novamente. O Pegaí criará um ambiente novo.

## Licença

Criado por **kassio8**. [Licença MIT](LICENSE)
