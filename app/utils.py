from __future__ import annotations

from typing import Any


def get_note_field_value(note: dict[str, Any], field_name: str) -> str:
    """Возвращает строковое значение поля заметки или пустую строку."""
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