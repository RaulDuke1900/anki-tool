from __future__ import annotations

from dataclasses import dataclass


from typing import Literal


LanguageMode = Literal["both", "de", "en"]


@dataclass
class AudioConfig:
    source_field_de: str | None = None
    source_field_en: str | None = None
    audio_field_de: str | None = None
    audio_field_en: str | None = None
    overwrite_audio: bool = False
    dry_run: bool = False
    language_mode: LanguageMode = "both"
    de_voice: str | None = None
    en_voice: str | None = None