from __future__ import annotations

from typing import Any

from app.services.anki_connect import AnkiConnectError, get_deck_names


def choose_deck() -> str | None:
    try:
        decks = get_deck_names()
    except AnkiConnectError as error:
        print(f"Ошибка: {error}")
        return None

    if not decks:
        print("Колоды не найдены.")
        return None

    print("\nВыбери колоду:")
    for index, deck_name in enumerate(decks, start=1):
        print(f"{index}. {deck_name}")

    raw_choice = input("\nВведи номер колоды: ").strip()

    if not raw_choice.isdigit():
        print("Нужно ввести номер колоды.")
        return None

    choice = int(raw_choice)

    if choice < 1 or choice > len(decks):
        print("Колода с таким номером не найдена.")
        return None

    return decks[choice - 1]


def choose_field(field_names: list[str], prompt: str) -> str | None:
    if not field_names:
        print("Поля не найдены.")
        return None

    print(f"\n{prompt}")
    for index, field_name in enumerate(field_names, start=1):
        print(f"{index}. {field_name}")

    raw_choice = input("\nВведи номер поля: ").strip()

    if not raw_choice.isdigit():
        print("Нужно ввести номер поля.")
        return None

    choice = int(raw_choice)

    if choice < 1 or choice > len(field_names):
        print("Поле с таким номером не найдено.")
        return None

    return field_names[choice - 1]


def get_note_field_value(note: dict[str, Any], field_name: str) -> str:
    fields = note.get("fields", {})
    if not isinstance(fields, dict):
        return ""

    field_data = fields.get(field_name)
    if not isinstance(field_data, dict):
        return ""

    value = field_data.get("value", "")
    if not isinstance(value, str):
        return ""

    return value.strip()


def extract_note_preview(note: dict[str, Any]) -> str:
    """Пытается достать человекочитаемый preview заметки."""
    fields = note.get("fields", {})
    if not isinstance(fields, dict) or not fields:
        return "[без полей]"

    first_field = next(iter(fields.values()), None)
    if not isinstance(first_field, dict):
        return "[без preview]"

    value = first_field.get("value", "")
    if not isinstance(value, str):
        return "[без текста]"

    value = value.strip().replace("\n", " ")
    return value[:120] if value else "[пустое поле]"