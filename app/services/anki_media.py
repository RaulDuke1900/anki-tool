from __future__ import annotations

import base64
from pathlib import Path

from app.services.anki_connect import AnkiConnectError, invoke


class AnkiMediaError(Exception):
    """Ошибка при работе с медиатекой Anki."""


def store_media_file(file_path: Path) -> str:
    """
    Загружает файл в медиатеку Anki.
    Возвращает имя файла в медиатеке.
    """
    if not file_path.exists():
        raise AnkiMediaError(f"Файл не найден: {file_path}")

    filename = file_path.name

    try:
        data = file_path.read_bytes()
        encoded = base64.b64encode(data).decode("utf-8")

        invoke(
            "storeMediaFile",
            {
                "filename": filename,
                "data": encoded,
            },
        )

    except AnkiConnectError as error:
        raise AnkiMediaError(f"Ошибка загрузки файла в Anki: {error}") from error
    except OSError as error:
        raise AnkiMediaError(f"Ошибка чтения файла: {error}") from error

    return filename