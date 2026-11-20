#Script feito por Kássio Lima (ks) e ajuda do Copilot
import contextlib
import importlib.util
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import call, patch


SCRIPT_PATH = Path(__file__).with_name("baixar_youtube_autodetect.py")
SPEC = importlib.util.spec_from_file_location("baixar_youtube_autodetect", SCRIPT_PATH)
downloader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(downloader)


class InstallYtDlpTests(unittest.TestCase):
    def test_rejects_python_older_than_311(self):
        with (
            patch.object(sys, "version_info", (3, 10, 0)),
            patch("subprocess.check_call") as check_call,
        ):
            with self.assertRaisesRegex(RuntimeError, "Python 3.11"):
                downloader.instalar_ytdlp()

        check_call.assert_not_called()

    def test_installs_dependencies_into_active_venv_without_restarting(self):
        with (
            patch.object(sys, "version_info", (3, 12, 0)),
            patch.object(sys, "prefix", "/project/.venv"),
            patch.object(sys, "base_prefix", "/usr"),
            patch.object(downloader, "_dependencies_installed", return_value=False),
            patch("subprocess.check_call") as check_call,
            patch("os.execv") as execv,
        ):
            downloader.instalar_ytdlp()

        check_call.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", *downloader.INSTALL_PACKAGES]
        )
        execv.assert_not_called()

    def test_creates_venv_installs_dependencies_and_restarts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_dir = Path(temp_dir) / ".venv"
            venv_python = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            script_path = str(SCRIPT_PATH.resolve())
            arguments = [script_path, "--dry-run"]

            with (
                patch.object(sys, "version_info", (3, 12, 0)),
                patch.object(sys, "prefix", "/usr"),
                patch.object(sys, "base_prefix", "/usr"),
                patch.object(sys, "argv", arguments),
                patch.object(downloader, "_venv_dir", return_value=venv_dir),
                patch.object(downloader, "_dependencies_installed", return_value=False),
                patch("subprocess.check_call") as check_call,
                patch("os.execv") as execv,
            ):
                downloader.instalar_ytdlp()

        self.assertEqual(
            check_call.call_args_list,
            [
                call([sys.executable, "-m", "venv", str(venv_dir)]),
                call([str(venv_python), "-m", "pip", "install", *downloader.INSTALL_PACKAGES]),
            ],
        )
        execv.assert_called_once_with(
            str(venv_python),
            [str(venv_python), script_path, "--dry-run"],
        )

    def test_reuses_project_venv_even_if_system_python_has_packages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_dir = Path(temp_dir) / ".venv"
            venv_python = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            venv_python.parent.mkdir(parents=True)
            venv_python.touch()
            script_path = str(SCRIPT_PATH.resolve())

            with (
                patch.object(sys, "version_info", (3, 12, 0)),
                patch.object(sys, "prefix", "/usr"),
                patch.object(sys, "base_prefix", "/usr"),
                patch.object(sys, "argv", [script_path]),
                patch.object(downloader, "_venv_dir", return_value=venv_dir),
                patch.object(downloader, "_python_is_supported", return_value=True),
                patch.object(downloader, "_dependencies_installed", return_value=True) as installed,
                patch("subprocess.check_call") as check_call,
                patch("os.execv") as execv,
            ):
                downloader.instalar_ytdlp()

        installed.assert_called_once_with(venv_python)
        check_call.assert_not_called()
        execv.assert_called_once_with(str(venv_python), [str(venv_python), script_path])

    def test_preserves_existing_directory_with_missing_or_unsupported_python(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_dir = Path(temp_dir) / ".venv"
            venv_python = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            venv_python.parent.mkdir(parents=True)
            arquivo = venv_dir / "pessoal.txt"
            arquivo.write_text("preservar", encoding="utf-8")

            with (
                patch.object(sys, "version_info", (3, 12, 0)),
                patch.object(sys, "prefix", "/usr"),
                patch.object(sys, "base_prefix", "/usr"),
                patch.object(downloader, "_venv_dir", return_value=venv_dir),
                patch.object(downloader, "_python_is_supported", return_value=False),
                patch("subprocess.check_call") as check_call,
                patch("os.execv") as execv,
            ):
                for has_python in (False, True):
                    with self.subTest(has_python=has_python):
                        if has_python:
                            venv_python.touch()
                        with self.assertRaisesRegex(RuntimeError, r"\.venv\.backup"):
                            downloader.instalar_ytdlp()
                        check_call.assert_not_called()
                        execv.assert_not_called()
                        self.assertEqual(arquivo.read_text(encoding="utf-8"), "preservar")


class QualitySelectionTests(unittest.TestCase):
    def test_quality_selectors_keep_audio_formats_correct(self):
        captured = {}

        class FakeYoutubeDL:
            def __init__(self, options):
                captured.update(options)

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def extract_info(self, url, download):
                return {
                    "title": "Teste",
                    "duration": None,
                    "uploader": "Canal",
                    "formats": [
                        {
                            "format_id": "18",
                            "ext": "mp4",
                            "resolution": "360p",
                            "vcodec": "avc1",
                            "acodec": "aac",
                        },
                        {
                            "format_id": "137",
                            "ext": "mp4",
                            "resolution": "1080p",
                            "vcodec": "avc1",
                            "acodec": "none",
                            "fps": 30,
                        },
                    ],
                }

        with (
            patch.dict(sys.modules, {"yt_dlp": SimpleNamespace(YoutubeDL=FakeYoutubeDL)}),
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            qualities, _ = downloader.listar_qualidades("https://example.invalid/watch?v=1&list=2")

        self.assertTrue(captured["noplaylist"])
        self.assertIn("Duração indisponível", output.getvalue())
        self.assertEqual(qualities["360p (com áudio)"], "18")
        self.assertEqual(qualities["1080p 30fps (só vídeo)"], "137+bestaudio/best")

    def test_menu_passes_selected_selector_without_duplicating_audio(self):
        selector = "137+bestaudio/best"
        with (
            patch("builtins.input", side_effect=["https://example.invalid/video", "2", "", "0", "-1", "2", "x", "1"]),
            patch.object(downloader, "pasta_downloads_padrao", return_value="/tmp/downloads"),
            patch.object(downloader, "listar_qualidades", return_value=({"1080p": selector}, "Teste")),
            patch.object(downloader, "baixar_video") as download,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            downloader.menu()

        download.assert_called_once_with(
            "https://example.invalid/video", qualidade=selector, pasta="/tmp/downloads"
        )

    def test_download_error_does_not_retry_with_another_quality(self):
        with (
            patch("builtins.input", side_effect=["url", "2", "destino", "1"]),
            patch.object(downloader, "listar_qualidades", return_value=({"360p": "18"}, "Teste")),
            patch.object(downloader, "baixar_video", side_effect=ValueError("falha no download")) as download,
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            downloader.menu()

        download.assert_called_once_with("url", qualidade="18", pasta="destino")
        self.assertIn("falha no download", output.getvalue())


class FfmpegTests(unittest.TestCase):
    def test_finds_portable_ffmpeg_from_imageio_package(self):
        imageio_ffmpeg = SimpleNamespace(get_ffmpeg_exe=lambda: "/venv/ffmpeg")
        with (
            patch("shutil.which", return_value=None),
            patch("os.path.isdir", return_value=False),
            patch.dict(sys.modules, {"imageio_ffmpeg": imageio_ffmpeg}),
        ):
            self.assertEqual(downloader.obter_caminho_ffmpeg(), "/venv/ffmpeg")

    def test_video_download_uses_best_merged_format_and_portable_ffmpeg(self):
        captured = {}

        class FakeYoutubeDL:
            def __init__(self, options):
                captured["options"] = options

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def download(self, urls):
                self.urls = urls

        fake_yt_dlp = SimpleNamespace(YoutubeDL=FakeYoutubeDL)
        with (
            patch.dict(sys.modules, {"yt_dlp": fake_yt_dlp}),
            patch.object(downloader, "obter_caminho_ffmpeg", return_value="/venv/ffmpeg"),
            patch("os.makedirs"),
        ):
            downloader.baixar_video("https://example.invalid/video")

        self.assertEqual(captured["options"]["format"], "bestvideo*+bestaudio/best")
        self.assertEqual(Path(captured["options"]["outtmpl"]).name, "%(title)s [%(id)s].%(ext)s")
        self.assertEqual(captured["options"]["ffmpeg_location"], "/venv/ffmpeg")

    def test_audio_download_uses_portable_ffmpeg(self):
        captured = {}

        class FakeYoutubeDL:
            def __init__(self, options):
                captured["options"] = options

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def download(self, urls):
                captured["urls"] = urls

        with (
            patch.dict(sys.modules, {"yt_dlp": SimpleNamespace(YoutubeDL=FakeYoutubeDL)}),
            patch.object(downloader, "obter_caminho_ffmpeg", return_value="/venv/ffmpeg"),
            patch("os.makedirs"),
        ):
            downloader.baixar_audio("https://example.invalid/video")

        self.assertEqual(captured["options"]["ffmpeg_location"], "/venv/ffmpeg")
        self.assertEqual(captured["options"]["postprocessors"][0]["preferredcodec"], "mp3")
        self.assertEqual(Path(captured["options"]["outtmpl"]).name, "%(title)s [%(id)s].%(ext)s")


if __name__ == "__main__":
    unittest.main()
