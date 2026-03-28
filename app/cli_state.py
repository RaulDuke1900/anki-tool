from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class AppState:
    selected_deck: str | None = None
    overwrite_audio: bool = False
    source_field_de: str | None = None
    source_field_en: str | None = None
    audio_field_de: str | None = None
    audio_field_en: str | None = None


@dataclass(frozen=True)
class MenuCommand:
    key: str
    title: str
    handler: Callable[[AppState], None]