from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from app.models import AudioConfig


@dataclass
class AppState:
    selected_deck: str | None = None
    audio_config: AudioConfig = field(default_factory=AudioConfig)

    # Shortcuts для удобства в handlers
    @property
    def source_field_de(self) -> str | None:
        return self.audio_config.source_field_de

    @property
    def source_field_en(self) -> str | None:
        return self.audio_config.source_field_en

    @property
    def audio_field_de(self) -> str | None:
        return self.audio_config.audio_field_de

    @property
    def audio_field_en(self) -> str | None:
        return self.audio_config.audio_field_en

    @property
    def overwrite_audio(self) -> bool:
        return self.audio_config.overwrite_audio


@dataclass(frozen=True)
class MenuCommand:
    key: str
    title: str
    handler: Callable[[AppState], None]