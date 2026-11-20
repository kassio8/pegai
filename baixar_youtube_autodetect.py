#!/usr/bin/env python3
"""
Pegaí: baixador de vídeos do YouTube usando yt-dlp
Uso: python baixar_youtube_autodetect.py
Na primeira execução, cria uma venv e instala yt-dlp, Deno e FFmpeg portátil.
"""

import errno
import ntpath
import os
import shutil
import subprocess
import sys
from pathlib import Path, PureWindowsPath
from urllib.parse import parse_qs, urlencode, urlsplit

INSTALL_PACKAGES = ("yt-dlp[default,deno]", "imageio-ffmpeg")
REQUIRED_DISTRIBUTIONS = ("yt-dlp", "yt-dlp-ejs", "deno", "imageio-ffmpeg")
NOME_ARQUIVO = "%(title)s [%(id)s].%(ext)s"


def _venv_dir():
    return Path(__file__).resolve().parent / ".venv"


def _venv_python(venv_dir):
    return venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _python_is_supported(python):
    try:
        result = subprocess.run(
            [str(python), "-c", "import sys; raise SystemExit(sys.version_info < (3, 11) or sys.prefix == sys.base_prefix)"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0


def _dependencies_installed(python):
    check = (
        "import importlib.metadata as m; "
        f"[m.version(name) for name in {REQUIRED_DISTRIBUTIONS!r}]"
    )
    result = subprocess.run(
        [str(python), "-c", check],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def instalar_ytdlp():
    """Prepara as dependências numa venv e reinicia nela quando necessário."""
    if sys.version_info < (3, 11):
        raise RuntimeError("Este programa requer Python 3.11 ou superior.")

    if sys.prefix != sys.base_prefix:
        if not _dependencies_installed(sys.executable):
            print("Instalando dependências no ambiente virtual...", flush=True)
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", *INSTALL_PACKAGES]
            )
        return

    venv_dir = _venv_dir()
    venv_python = _venv_python(venv_dir)
    if not os.path.lexists(venv_dir):
        print("Criando ambiente virtual...", flush=True)
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
    elif not venv_python.is_file() or not _python_is_supported(venv_python):
        raise RuntimeError(
            f"O ambiente em '{venv_dir}' precisa de um Python 3.11+ funcional. "
            "Renomeie .venv para um nome livre, como .venv.backup, e execute novamente."
        )

    if not _dependencies_installed(venv_python):
        print("Instalando dependências do projeto...", flush=True)
        subprocess.check_call(
            [str(venv_python), "-m", "pip", "install", *INSTALL_PACKAGES]
        )

    print("Iniciando na venv do projeto...\n", flush=True)
    os.execv(str(venv_python), [str(venv_python), *sys.argv])


def pasta_downloads_padrao():
    """Tenta detectar a pasta de Downloads padrão do usuário."""
    home = Path.home()
    possiveis = ["Downloads", "Download"]

    for nome in possiveis:
        caminho = home / nome
        if caminho.exists() and caminho.is_dir():
            return str(caminho)

    return str(home)


def obter_caminho_ffmpeg():
    """Retorna FFmpeg do sistema, da pasta local ou do pacote portátil."""
    exe_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    caminho = shutil.which(exe_name)
    if caminho:
        return caminho

    local_root = os.path.join(os.path.dirname(__file__), "ffmpeg")
    if os.path.isdir(local_root):
        for root, _, files in os.walk(local_root):
            if exe_name in files:
                return os.path.join(root, exe_name)

    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, OSError, RuntimeError):
        pass
    return None


def ffmpeg_instalado():
    """Retorna True se FFmpeg estiver disponível no sistema ou na venv."""
    return obter_caminho_ffmpeg() is not None


def listar_qualidades(url):
    """Lista as qualidades disponíveis para o vídeo."""
    import yt_dlp

    ydl_opts = {"quiet": True, "no_warnings": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formatos = info.get("formats", [])

        print(f"\n📹 Título: {info.get('title', 'Desconhecido')}")
        duracao = info.get("duration")
        if duracao is None:
            print("⏱  Duração indisponível")
        else:
            minutos, segundos = divmod(int(duracao), 60)
            print(f"⏱  Duração: {minutos}min {segundos}s")
        print(f"👤 Canal: {info.get('uploader', 'Desconhecido')}\n")

        qualidades = {}
        for f in formatos:
            if f.get("vcodec") == "none":
                continue

            height = f.get("height")
            width = f.get("width")
            res = f.get("resolution")
            if not res and height:
                res = f"{width}x{height}" if width else f"{height}p"
            if not res:
                res = f.get("format_note", "")

            ext = f.get("ext", "")
            fid = f.get("format_id", "")
            acodec = f.get("acodec", "")
            fps = f.get("fps")
            if not res or not fid or ext not in ("mp4", "webm"):
                continue

            descricao = res
            if fps:
                descricao += f" {fps}fps"
            descricao += " (com áudio)" if acodec != "none" else " (só vídeo)"

            if descricao not in qualidades:
                if acodec != "none":
                    qualidades[descricao] = fid
                else:
                    qualidades[descricao] = f"{fid}+bestaudio/best"

        return qualidades, info.get("title", "video")


def _url_playlist(url):
    partes = urlsplit(url if "://" in url else "//" + url)
    host = partes.hostname or ""
    if host != "youtu.be" and host != "youtube.com" and not host.endswith(".youtube.com"):
        return None
    consulta = parse_qs(partes.query)
    if not consulta.get("list"):
        return None
    if partes.path.rstrip("/") != "/playlist":
        tem_video = (consulta.get("v") or host == "youtu.be"
                     or partes.path.startswith(("/shorts/", "/live/", "/embed/")))
        if not tem_video:
            return None
        while True:
            escolha = input("1. Só este vídeo (Enter)\n2. Playlist inteira\nEscolha: ").strip()
            if escolha in ("", "1"):
                return None
            if escolha == "2":
                break
            print("Escolha 1 ou 2.")
    return "https://www.youtube.com/playlist?" + urlencode({"list": consulta["list"][0]})


def _ler_playlist(url):
    import yt_dlp

    with yt_dlp.YoutubeDL({"extract_flat": "in_playlist", "quiet": True}) as ydl:
        playlist = ydl.extract_info(url, download=False)
    if not playlist or not playlist.get("entries"):
        raise ValueError("A playlist está vazia ou não tem itens visíveis.")
    return playlist


def _nome_pasta_playlist(playlist):
    from yt_dlp.utils import sanitize_filename

    nome = sanitize_filename(playlist.get("title") or "Playlist", is_id=False)
    nome = nome.encode("utf-8")[:180].decode("utf-8", "ignore").strip(" .") or "Playlist"
    reservado = ntpath.isreserved(nome) if hasattr(ntpath, "isreserved") else PureWindowsPath(nome).is_reserved()
    if reservado:
        nome = "_" + nome
    return nome


def _orientacao_destino(erro):
    while erro is not None:
        if isinstance(erro, OSError):
            if erro.errno == errno.ENOSPC:
                return "Espaço insuficiente. Libere espaço ou escolha outra pasta."
            if isinstance(erro, PermissionError) or erro.errno == errno.EROFS:
                return "Sem permissão para gravar. Escolha uma pasta com acesso de escrita."
            if isinstance(erro, (NotADirectoryError, FileExistsError, IsADirectoryError)):
                return "O caminho de destino conflita com um arquivo ou pasta. Escolha outra pasta."
        erro = erro.__cause__ or erro.__context__
    return None


def _baixar(url, pasta, opcoes_formato, playlist=None):
    import yt_dlp

    os.makedirs(pasta, exist_ok=True)

    ydl_opts = {
        **opcoes_formato,
        "paths": {"home": os.path.abspath(pasta)},
        "outtmpl": NOME_ARQUIVO,
        "progress_hooks": [progresso_hook],
        "noplaylist": True,
    }
    ffmpeg_path = obter_caminho_ffmpeg()
    if ffmpeg_path:
        ydl_opts["ffmpeg_location"] = ffmpeg_path

    if playlist is not None:
        largura = max(2, len(str(len(playlist["entries"]))))
        ydl_opts["outtmpl"] = f"%(playlist_index)0{largura}d - {NOME_ARQUIVO}"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if playlist is None:
            if ydl.download([url]):
                raise RuntimeError("O yt-dlp não conseguiu concluir o download.")
            return
        _baixar_faixas(ydl, playlist, pasta)


def _baixar_faixas(ydl, playlist, pasta):
    from yt_dlp.utils import YoutubeDLError

    total = len(playlist["entries"])
    falhas = []
    salvos = 0
    for numero, faixa in enumerate(playlist["entries"], 1):
        titulo = (faixa or {}).get("title") or (faixa or {}).get("id") or "Faixa indisponível"
        print(f"\n{numero}/{total} — {titulo}", flush=True)
        contexto = {"playlist": playlist.get("title") or "Playlist", "playlist_index": numero}
        try:
            if not faixa or not ydl.process_ie_result(faixa, extra_info=contexto):
                raise ValueError("Faixa indisponível")
        except (YoutubeDLError, OSError, ValueError) as erro:
            falhas.append(f"{numero:02d} - {titulo} ({erro})")
            orientacao = _orientacao_destino(erro)
            if orientacao:
                print(orientacao)
                break
        else:
            salvos += 1
    print(f"\nPlaylist: {salvos} de {total} na pasta '{pasta}'. Falhas: {len(falhas)}.")
    pendentes = total - salvos - len(falhas)
    if pendentes:
        print(f"Itens pendentes: {pendentes}.")
    for falha in falhas:
        print(f"  {falha}")


def baixar_video(url, qualidade="bestvideo*+bestaudio/best", pasta="downloads", *, playlist=None):
    """Baixa o vídeo com a qualidade especificada."""
    _baixar(url, pasta, {"format": qualidade}, playlist)


def baixar_audio(url, pasta="downloads", *, playlist=None):
    """Baixa apenas o áudio em formato MP3."""
    opcoes_mp3 = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    _baixar(url, pasta, opcoes_mp3, playlist)


def progresso_hook(d):
    """Exibe o progresso do download."""
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "N/A").strip()
        speed = d.get("_speed_str", "N/A").strip()
        eta = d.get("_eta_str", "N/A").strip()
        print(f"\r⬇️  Baixando: {percent} | Velocidade: {speed} | ETA: {eta}   ", end="")
    elif d["status"] == "finished":
        print(f"\n✅ Download concluído! Processando arquivo...")


def menu():
    print("=" * 50)
    print("   🎬 PEGAÍ — BAIXADOR DO YOUTUBE")
    print("=" * 50)

    url = input("\nCole a URL do vídeo ou da playlist: ").strip()
    if not url:
        print("❌ URL inválida.")
        return

    try:
        url_playlist = _url_playlist(url)
        print("\nO que deseja baixar?")
        print("  1. Vídeo (melhor qualidade)")
        print("  2. Vídeo (escolher qualidade)")
        print("  3. Somente áudio (MP3)")
        opcao = input("\nEscolha (1/2/3): ").strip()
        if opcao not in ("1", "2", "3"):
            print("❌ Opção inválida.")
            return

        pasta_padrao = Path(pasta_downloads_padrao())
        playlist = None
        if url_playlist:
            print("Consultando playlist...")
            playlist = _ler_playlist(url_playlist)
            pasta_padrao /= _nome_pasta_playlist(playlist)
        destino = input(f"Pasta de destino (Enter para '{pasta_padrao}'): ").strip()
        pasta = os.path.expanduser(destino or str(pasta_padrao))

        if opcao == "1":
            baixar_video(url, pasta=pasta, playlist=playlist)

        elif opcao == "2" and playlist is not None:
            while True:
                altura = input("Resolução máxima da playlist em pixels (ex.: 720 ou 1080): ").strip()
                try:
                    altura = int(altura)
                except ValueError:
                    altura = 0
                if altura > 0:
                    break
                print("Digite uma altura válida, como 720.")
            formato = f"bestvideo*[height<={altura}]+bestaudio/best[height<={altura}]"
            baixar_video(url, qualidade=formato, pasta=pasta, playlist=playlist)
        elif opcao == "2":
            print("\n🔍 Listando qualidades disponíveis...")
            qualidades, titulo = listar_qualidades(url)

            if not qualidades:
                print("Nenhuma qualidade encontrada. Baixando na melhor disponível...")
                baixar_video(url, pasta=pasta)
            else:
                print("Qualidades disponíveis:")
                opcoes = list(qualidades.keys())
                for i, q in enumerate(opcoes, 1):
                    print(f"  {i}. {q}")

                while True:
                    escolha = input("\nEscolha o número da qualidade: ").strip()
                    try:
                        numero = int(escolha)
                    except ValueError:
                        numero = 0
                    if 1 <= numero <= len(opcoes):
                        break
                    print(f"Opção inválida. Digite um número de 1 a {len(opcoes)}.")
                formato = qualidades[opcoes[numero - 1]]
                baixar_video(url, qualidade=formato, pasta=pasta)

        else:
            print("\n🎵 Baixando áudio em MP3...")
            if not ffmpeg_instalado():
                print("❌ FFmpeg não encontrado. Reinstale as dependências ou instale FFmpeg no sistema.")
                return
            baixar_audio(url, pasta=pasta, playlist=playlist)

        if playlist is None:
            print(f"\n✅ Arquivo salvo na pasta: '{pasta}'")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        orientacao = _orientacao_destino(e)
        if orientacao:
            print(orientacao)


if __name__ == "__main__":
    try:
        instalar_ytdlp()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as e:
        print(f"❌ Não foi possível preparar o ambiente: {e}")
        raise SystemExit(1) from e
    while True:
        menu()
        resposta = input("\nDeseja fazer outro download? (s/n): ").strip().lower()
        if resposta not in ("s", "sim"):
            print("Saindo. Até logo!")
            break
