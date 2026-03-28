from __future__ import annotations

from typing import Any

import requests

from app.config import settings


class AnkiConnectError(Exception):
    """Ошибка при работе с AnkiConnect."""


def invoke(action: str, params: dict[str, Any] | None = None) -> Any:
    """
    Универсальный вызов AnkiConnect API.

    :param action: имя действия AnkiConnect, например 'version' или 'deckNames'
    :param params: словарь параметров для действия
    :return: поле result из ответа AnkiConnect
    """
    payload = {
        "action": action,
        "version": 6,
        "params": params or {},
    }

    try:
        response = requests.post(
            settings.anki_connect_url,
            json=payload,
            timeout=settings.anki_connect_timeout,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        raise AnkiConnectError(
            f"Не удалось подключиться к AnkiConnect: {error}"
        ) from error

    try:
        data = response.json()
    except ValueError as error:
        raise AnkiConnectError("AnkiConnect вернул некорректный JSON.") from error

    if data.get("error") is not None:
        raise AnkiConnectError(f"Ошибка AnkiConnect: {data['error']}")

    return data.get("result")


def check_connection() -> bool:
    """
    Проверяет, отвечает ли AnkiConnect.
    """
    version = invoke("version")
    return isinstance(version, int)


def get_deck_names() -> list[str]:
    """
    Возвращает список названий колод.
    """
    result = invoke("deckNames")
    if not isinstance(result, list):
        raise AnkiConnectError("AnkiConnect вернул некорректный список колод.")

    return sorted(str(deck_name) for deck_name in result)


def find_note_ids_by_deck(deck_name: str) -> list[int]:
    """
    Возвращает список ID заметок из указанной колоды.
    """
    query = f'deck:"{deck_name}"'
    result = invoke("findNotes", {"query": query})

    if not isinstance(result, list):
        raise AnkiConnectError("AnkiConnect вернул некорректный список note ID.")

    note_ids: list[int] = []
    for item in result:
        if not isinstance(item, int):
            raise AnkiConnectError("AnkiConnect вернул note ID некорректного типа.")
        note_ids.append(item)

    return note_ids


def get_notes_info(note_ids: list[int]) -> list[dict[str, Any]]:
    """
    Возвращает подробную информацию по заметкам.
    """
    if not note_ids:
        return []

    result = invoke("notesInfo", {"notes": note_ids})

    if not isinstance(result, list):
        raise AnkiConnectError("AnkiConnect вернул некорректные данные заметок.")

    notes: list[dict[str, Any]] = []
    for item in result:
        if not isinstance(item, dict):
            raise AnkiConnectError("AnkiConnect вернул заметку некорректного формата.")
        notes.append(item)

    return notes

def get_first_note_info_by_deck(deck_name: str) -> dict[str, Any] | None:
    """
    Возвращает информацию о первой заметке из колоды.
    Если заметок нет, возвращает None.
    """
    note_ids = find_note_ids_by_deck(deck_name)
    if not note_ids:
        return None

    notes = get_notes_info([note_ids[0]])
    if not notes:
        return None

    return notes[0]

def get_field_names_from_first_note(deck_name: str) -> list[str]:
    """
    Возвращает список названий полей из первой заметки колоды.
    """
    note = get_first_note_info_by_deck(deck_name)
    if note is None:
        return []

    fields = note.get("fields", {})
    if not isinstance(fields, dict):
        raise AnkiConnectError("Некорректный формат fields у заметки.")

    return list(fields.keys())

def update_note_fields(note_id: int, fields: dict[str, str]) -> None:
    """
    Обновляет поля заметки по note_id.
    """
    if not fields:
        raise AnkiConnectError("Не переданы поля для обновления заметки.")

    invoke(
        "updateNoteFields",
        {
            "note": {
                "id": note_id,
                "fields": fields,
            }
        },
    )
