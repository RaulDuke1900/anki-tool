from dataclasses import dataclass
from typing import Literal, Optional


LanguageMode = Literal["both", "de", "en"]


@dataclass
class TTSOptions:
    language_mode: LanguageMode = "both"
    overwrite_audio: bool = False
    dry_run: bool = False
    de_voice: Optional[str] = None
    en_voice: Optional[str] = None