#!/usr/bin/env python3
"""
Pegaí: baixador de vídeos do YouTube usando yt-dlp
Uso: python baixar_youtube_autodetect.py
Na primeira execução, cria uma venv e instala yt-dlp, Deno e FFmpeg portátil.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

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


def _baixar(url, pasta, opcoes_formato):
    import yt_dlp

    os.makedirs(pasta, exist_ok=True)

    ydl_opts = {
        **opcoes_formato,
        "outtmpl": os.path.join(pasta, NOME_ARQUIVO),
        "progress_hooks": [progresso_hook],
        "noplaylist": True,
    }
    ffmpeg_path = obter_caminho_ffmpeg()
    if ffmpeg_path:
        ydl_opts["ffmpeg_location"] = ffmpeg_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def baixar_video(url, qualidade="bestvideo*+bestaudio/best", pasta="downloads"):
    """Baixa o vídeo com a qualidade especificada."""
    _baixar(url, pasta, {"format": qualidade})


def baixar_audio(url, pasta="downloads"):
    """Baixa apenas o áudio em formato MP3."""
    opcoes_mp3 = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    _baixar(url, pasta, opcoes_mp3)


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

    url = input("\nCole a URL do vídeo: ").strip()
    if not url:
        print("❌ URL inválida.")
        return

    print("\nO que deseja baixar?")
    print("  1. Vídeo (melhor qualidade)")
    print("  2. Vídeo (escolher qualidade)")
    print("  3. Somente áudio (MP3)")
    opcao = input("\nEscolha (1/2/3): ").strip()

    pasta_padrao = pasta_downloads_padrao()
    pasta = input(f"Pasta de destino (Enter para '{pasta_padrao}'): ").strip() or pasta_padrao

    try:
        if opcao == "1":
            print("\n🔍 Obtendo informações do vídeo...")
            baixar_video(url, pasta=pasta)

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

        elif opcao == "3":
            print("\n🎵 Baixando áudio em MP3...")
            if not ffmpeg_instalado():
                print("❌ FFmpeg não encontrado. Reinstale as dependências ou instale FFmpeg no sistema.")
                return
            else:
                print("⚠️  FFmpeg encontrado. Iniciando conversão para MP3...")
            baixar_audio(url, pasta=pasta)

        else:
            print("❌ Opção inválida.")
            return

        print(f"\n✅ Arquivo salvo na pasta: '{pasta}/'")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("Verifique se a URL é válida e tente novamente.")


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
