from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    anki_connect_url: str
    anki_connect_timeout: int
    tts_output_dir: str
    tts_de_voice: str
    tts_en_voice: str


def load_settings() -> Settings:
    return Settings(
        anki_connect_url=os.getenv("ANKI_CONNECT_URL", "http://127.0.0.1:8765"),
        anki_connect_timeout=int(os.getenv("ANKI_CONNECT_TIMEOUT", "10")),
        tts_output_dir=os.getenv("TTS_OUTPUT_DIR", "generated_audio"),
        tts_de_voice=os.getenv("TTS_DE_VOICE", "de-DE-KatjaNeural"),
        tts_en_voice=os.getenv("TTS_EN_VOICE", "en-US-AriaNeural"),
    )


settings = load_settings()