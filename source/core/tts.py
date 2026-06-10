import asyncio
import os
import queue
import re
import tempfile
import threading
import uuid


class Speaker:
    def __init__(
        self,
        enabled: bool = True,
        voice: str = "ru-RU-SvetlanaNeural"
    ):

        self.enabled = enabled
        self.voice = voice

        self._queue = queue.Queue()
        self._thread = threading.Thread(
            target=self._worker,
            daemon=True
        )

        self._thread.start()

    # =====================================================
    # PUBLIC
    # =====================================================

    def speak(
        self,
        text: str
    ):

        if not self.enabled:
            return

        text = self._prepare_text(
            text
        )

        if not text:
            return

        self._queue.put(
            text
        )

    def stop(
        self
    ):

        try:
            self._queue.put(
                None
            )
        except Exception:
            pass

    # =====================================================
    # TEXT PREPARE
    # =====================================================

    def _prepare_text(
        self,
        text: str
    ) -> str:

        text = text or ""

        replacements = {
            "✅": "",
            "📝": "",
            "❌": "",
            "⚠️": "",
            "🎤": "",
            "AAYA": "Ая",
            "TODO": "туду",
        }

        for old, new in replacements.items():

            text = text.replace(
                old,
                new
            )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =====================================================
    # WORKER THREAD
    # =====================================================

    def _worker(
        self
    ):

        while True:

            text = self._queue.get()

            if text is None:
                break

            try:
                asyncio.run(
                    self._speak_async(
                        text
                    )
                )

            except Exception as e:
                print(
                    f"Ошибка Edge TTS: {e}"
                )

    # =====================================================
    # EDGE TTS
    # =====================================================

    async def _speak_async(
        self,
        text: str
    ):

        try:
            import edge_tts
            import pygame

        except Exception as e:
            print(
                f"Не удалось загрузить edge-tts или pygame: {e}"
            )
            return

        temp_dir = tempfile.gettempdir()

        filename = os.path.join(
            temp_dir,
            f"aaya_tts_{uuid.uuid4().hex}.mp3"
        )

        try:

            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice
            )

            await communicate.save(
                filename
            )

            self._play_mp3(
                pygame,
                filename
            )

        finally:

            try:
                if os.path.exists(
                    filename
                ):

                    os.remove(
                        filename
                    )

            except Exception:
                pass

    # =====================================================
    # PLAY AUDIO
    # =====================================================

    def _play_mp3(
        self,
        pygame,
        filename: str
    ):

        try:

            if not pygame.mixer.get_init():

                pygame.mixer.init()

            pygame.mixer.music.load(
                filename
            )

            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():

                pygame.time.Clock().tick(
                    10
                )

            pygame.mixer.music.unload()

        except Exception as e:

            print(
                f"Ошибка воспроизведения речи: {e}"
            )