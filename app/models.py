from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AudioConfig:
    """Конфигурация для генерации аудио. Не зависит от CLI."""
    source_field_de: str | None = None
    source_field_en: str | None = None
    audio_field_de: str | None = None
    audio_field_en: str | None = None
    overwrite_audio: bool = False