from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path

import edge_tts

from app.config import settings


class TTSServiceError(Exception):
    """Ошибка при генерации TTS."""


def _build_output_path(text: str, voice: str) -> Path:
    """
    Строит стабильное имя файла на основе текста и голоса.
    """
    output_dir = Path(settings.tts_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    file_hash = hashlib.sha256(f"{voice}::{text}".encode("utf-8")).hexdigest()[:16]
    filename = f"{voice}_{file_hash}.mp3"
    return output_dir / filename


async def _generate_tts_async(text: str, voice: str, output_path: Path) -> None:
    """
    Асинхронно генерирует mp3 через edge-tts.
    """
    communicator = edge_tts.Communicate(text=text, voice=voice)
    await communicator.save(str(output_path))


def generate_tts_audio(text: str, voice: str) -> Path:
    """
    Генерирует mp3-файл из текста и возвращает путь к нему.
    """
    normalized_text = text.strip()
    if not normalized_text:
        raise TTSServiceError("Нельзя сгенерировать TTS для пустого текста.")

    output_path = _build_output_path(normalized_text, voice)
    
    if output_path.exists():
        return output_path
    
    try:
        asyncio.run(_generate_tts_async(normalized_text, voice, output_path))
    except Exception as error:
        raise TTSServiceError(f"Не удалось сгенерировать TTS: {error}") from error

    return output_path