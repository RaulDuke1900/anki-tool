from __future__ import annotations

from typing import Any

from app.models import AudioConfig
from app.config import settings
from app.utils import get_note_field_value
from app.text_cleaner import clean_text_for_tts
from app.services.anki_connect import AnkiConnectError, update_note_fields
from app.services.anki_media import AnkiMediaError, store_media_file
from app.services.tts_service import TTSServiceError, generate_tts_audio


def process_note_audio(note: dict[str, Any], config: AudioConfig) -> dict[str, Any]:
    note_id = note.get("noteId")
    if not isinstance(note_id, int):
        return {
            "note_id": "unknown",
            "updated_fields": {},
            "skipped": [],
            "errors": ["Некорректный note_id."],
        }

    updated_fields: dict[str, str] = {}
    errors: list[str] = []
    skipped: list[str] = []

    if config.source_field_de and config.audio_field_de:
        de_text = clean_text_for_tts(get_note_field_value(note, config.source_field_de))
        current_de_audio = get_note_field_value(note, config.audio_field_de)

        if not de_text:
            skipped.append("DE empty source")
        elif current_de_audio and not config.overwrite_audio:
            skipped.append("DE audio exists")
        else:
            try:
                de_path = generate_tts_audio(de_text, settings.tts_de_voice)
                de_filename = store_media_file(de_path)
                updated_fields[config.audio_field_de] = f"[sound:{de_filename}]"
            except (TTSServiceError, AnkiMediaError) as error:
                errors.append(f"DE: {error}")

    if config.source_field_en and config.audio_field_en:
        en_text = clean_text_for_tts(get_note_field_value(note, config.source_field_en))
        current_en_audio = get_note_field_value(note, config.audio_field_en)

        if not en_text:
            skipped.append("EN empty source")
        elif current_en_audio and not config.overwrite_audio:
            skipped.append("EN audio exists")
        else:
            try:
                en_path = generate_tts_audio(en_text, settings.tts_en_voice)
                en_filename = store_media_file(en_path)
                updated_fields[config.audio_field_en] = f"[sound:{en_filename}]"
            except (TTSServiceError, AnkiMediaError) as error:
                errors.append(f"EN: {error}")

    if updated_fields:
        try:
            update_note_fields(note_id, updated_fields)
        except AnkiConnectError as error:
            errors.append(f"updateNoteFields: {error}")
            updated_fields = {}

    return {
        "note_id": note_id,
        "updated_fields": updated_fields,
        "errors": errors,
        "skipped": skipped,
    }