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
| **1 — Vídeo (melhor qualidade)** | Cada vídeo na melhor qualidade disponível. |
| **2 — Vídeo (escolher qualidade)** | Para um vídeo, escolha uma das resoluções listadas. Para uma playlist, informe uma altura máxima, como 720 ou 1080 pixels. |
| **3 — Somente áudio (MP3)** | Um MP3 para um vídeo avulso ou um MP3 por vídeo da playlist. |

## Como baixar uma playlist de músicas

1. Cole o link da playlist no Pegaí. Um link direto como `youtube.com/playlist?list=...` já seleciona a lista inteira.
2. Se você copiou o link enquanto um vídeo tocava (`watch?v=...&list=...`), escolha **2 — Playlist inteira**. Para baixar apenas o vídeo aberto, pressione **Enter**.
3. No menu de formato, escolha **3 — Somente áudio (MP3)**.
4. Pressione **Enter** para salvar na pasta sugerida com o nome da playlist. Se preferir, digite o destino exato, como `D:\Músicas\BK`.

Os arquivos recebem o número de cada vídeo na lista, como `01 - Até Amanhã [lJY-xj-SBhk].mp3`. Se uma faixa estiver indisponível ou falhar na conversão, o Pegaí segue para a próxima e mantém a numeração original. Ao final, mostra quantos itens ficaram salvos e identifica as falhas por número e título.

No teste com **PRODUTO DO AMBIENTE MIXTAPE**, os 12 vídeos geraram 12 MP3 a 192 kbps, totalizando 101 MB. Foram 11 faixas individuais e um arquivo de 35 minutos, porque a playlist também inclui um vídeo com a mixtape completa. [Ver a playlist do teste](https://www.youtube.com/playlist?list=PLvnkn1Ox2UftPf21azpttWSZJfqK0EDK9)

## Onde ficam os arquivos?

O menu mostra a pasta de destino antes de baixar. O Pegaí procura `Downloads` ou `Download` na sua pasta de usuário. Se nenhuma delas existir, usa a pasta de usuário como base. Para playlists, acrescenta o nome da lista à sugestão. Um caminho digitado por você é usado diretamente. O Pegaí cria a pasta escolhida se necessário.

Cada arquivo inclui o título e o ID do vídeo, como `Minha música [abc123].mp3`. Assim, vídeos diferentes com o mesmo título têm arquivos distintos.

Se faltar espaço ou permissão para gravar, o Pegaí interrompe a playlist e informa quantos itens ficaram pendentes. Libere espaço ou escolha uma pasta onde você possa gravar.

## Se aparecer um aviso sobre a .venv

A pasta `.venv` guarda o ambiente Python do projeto. Se ela estiver incompleta ou incompatível, o Pegaí para e preserva o conteúdo. Renomeie a pasta para um nome livre, como `.venv.backup`, e execute o comando novamente. O Pegaí criará um ambiente novo.

## Licença

Criado por **kassio8**. [Licença MIT](LICENSE)
