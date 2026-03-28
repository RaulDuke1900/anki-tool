from __future__ import annotations


from typing import Any

from app.cli_state import AppState, MenuCommand
from app.config import settings
from app.text_cleaner import clean_text_for_tts
from app.services.anki_media import AnkiMediaError, store_media_file
from app.services.tts_service import TTSServiceError, generate_tts_audio
from app.services.anki_connect import (
    AnkiConnectError,
    check_connection,
    find_note_ids_by_deck,
    get_deck_names,
    get_notes_info,
    get_first_note_info_by_deck,
    get_field_names_from_first_note,
    update_note_fields,
)


def print_menu(state: AppState, commands: list[MenuCommand]) -> None:
    print("\n=== Anki Tool ===")
    print(f"Текущая колода: {state.selected_deck or '[не выбрана]'}")
    print(f"DE source: {state.source_field_de or '[не выбрано]'}")
    print(f"EN source: {state.source_field_en or '[не выбрано]'}")
    print(f"DE audio target: {state.audio_field_de or '[не выбрано]'}")
    print(f"EN audio target: {state.audio_field_en or '[не выбрано]'}")
    print(f"Overwrite audio: {'yes' if state.overwrite_audio else 'no'}")
    print(f"------------------------------")

    for command in commands:
        print(f"{command.key}. {command.title}")

    print("0. Выход")

def handle_check_connection(state: AppState) -> None:
    try:
        is_ok = check_connection()
        if is_ok:
            print("Соединение с AnkiConnect установлено.")
        else:
            print("AnkiConnect ответил неожиданным образом.")
    except AnkiConnectError as error:
        print(f"Ошибка: {error}")

def handle_select_deck(state: AppState) -> None:
    deck_name = choose_deck()
    if deck_name is None:
        return

    state.selected_deck = deck_name
    print(f"\nВыбрана колода: {deck_name}")

def handle_show_decks(state: AppState) -> None:
    try:
        decks = get_deck_names()
    except AnkiConnectError as error:
        print(f"Ошибка: {error}")
        return

    if not decks:
        print("Колоды не найдены.")
        return

    print("\nСписок колод:")
    for index, deck_name in enumerate(decks, start=1):
        print(f"{index}. {deck_name}")

def handle_show_note_structure(state: AppState) -> None:
    if state.selected_deck is None:
        print("Сначала выбери колоду.")
        return

    try:
        note = get_first_note_info_by_deck(state.selected_deck)
    except AnkiConnectError as error:
        print(f"Ошибка: {error}")
        return

    if note is None:
        print(f"В колоде '{state.selected_deck}' заметки не найдены.")
        return

    note_id = note.get("noteId", "unknown")
    model_name = note.get("modelName", "unknown")
    tags = note.get("tags", [])
    fields = note.get("fields", {})

    print(f"\nСтруктура заметки из колоды: {state.selected_deck}")
    print(f"note_id: {note_id}")
    print(f"modelName: {model_name}")
    print(f"tags: {tags if tags else '[]'}")

    if not isinstance(fields, dict) or not fields:
        print("Поля не найдены.")
        return

    print("\nПоля заметки:")
    for field_name, field_data in fields.items():
        if not isinstance(field_data, dict):
            print(f"- {field_name}: [некорректный формат]")
            continue

        value = field_data.get("value", "")
        if not isinstance(value, str):
            value = ""

        preview = value.strip().replace("\n", " ")
        preview = preview[:80] if preview else "[пусто]"

        print(f"- {field_name}: {preview}")

def handle_select_tts_fields(state: AppState) -> None:
    if state.selected_deck is None:
        print("Сначала выбери колоду.")
        return

    try:
        field_names = get_field_names_from_first_note(state.selected_deck)
    except AnkiConnectError as error:
        print(f"Ошибка: {error}")
        return

    if not field_names:
        print("Не удалось получить поля заметки.")
        return

    print("\nНастройка полей для TTS.")

    source_field_de = choose_field(field_names, "Выбери поле-источник для немецкого текста:")
    if source_field_de is None:
        return

    source_field_en = choose_field(field_names, "Выбери поле-источник для английского текста:")
    if source_field_en is None:
        return

    audio_field_de = choose_field(field_names, "Выбери поле для записи немецкого аудио:")
    if audio_field_de is None:
        return

    audio_field_en = choose_field(field_names, "Выбери поле для записи английского аудио:")
    if audio_field_en is None:
        return

    state.source_field_de = source_field_de
    state.source_field_en = source_field_en
    state.audio_field_de = audio_field_de
    state.audio_field_en = audio_field_en

    print("\nПоля для TTS сохранены:")
    print(f"DE source: {state.source_field_de}")
    print(f"EN source: {state.source_field_en}")
    print(f"DE audio target: {state.audio_field_de}")
    print(f"EN audio target: {state.audio_field_en}")

def handle_preview_tts_data(state: AppState) -> None:
    if state.selected_deck is None:
        print("Сначала выбери колоду.")
        return

    required_fields = [
        state.source_field_de,
        state.source_field_en,
        state.audio_field_de,
        state.audio_field_en,
    ]
    if not all(required_fields):
        print("Сначала настрой все поля для TTS.")
        return

    try:
        note_ids = find_note_ids_by_deck(state.selected_deck)
    except AnkiConnectError as error:
        print(f"Ошибка: {error}")
        return

    if not note_ids:
        print(f"В колоде '{state.selected_deck}' заметки не найдены.")
        return

    preview_ids = note_ids[:5]

    try:
        notes = get_notes_info(preview_ids)
    except AnkiConnectError as error:
        print(f"Ошибка: {error}")
        return

    print(f"\nPreview TTS data for deck: {state.selected_deck}")
    print(f"Показываю первые {len(notes)} заметок:\n")
    print("-----------------------------------")

    for index, note in enumerate(notes, start=1):
        note_id = note.get("noteId", "unknown")

        de_text_raw = get_note_field_value(note, state.source_field_de)
        en_text_raw = get_note_field_value(note, state.source_field_en)

        de_text = clean_text_for_tts(de_text_raw)
        en_text = clean_text_for_tts(en_text_raw)

        de_audio_value = get_note_field_value(note, state.audio_field_de)
        en_audio_value = get_note_field_value(note, state.audio_field_en)

        de_status = "will write" if de_text else "skip empty source"
        en_status = "will write" if en_text else "skip empty source"

        if de_audio_value and not state.overwrite_audio:
            de_status = "skip audio exists"

        if en_audio_value and not state.overwrite_audio:
            en_status = "skip audio exists"

        print(f"{index}. note_id={note_id}")
        print(f"   DE text: {de_text or '[пусто]'}")
        print(f"   EN text: {en_text or '[пусто]'}")
        print(f"   DE target current: {de_audio_value or '[пусто]'}")
        print(f"   EN target current: {en_audio_value or '[пусто]'}")
        print(f"   DE status: {de_status}")
        print(f"   EN status: {en_status}")
        print()

def handle_generate_test_tts(state: AppState) -> None:
    if state.selected_deck is None:
        print("Сначала выбери колоду.")
        return

    if state.source_field_de is None and state.source_field_en is None:
        print("Сначала настрой поля для TTS.")
        return

    try:
        note = get_first_note_info_by_deck(state.selected_deck)
    except AnkiConnectError as error:
        print(f"Ошибка AnkiConnect: {error}")
        return

    if note is None:
        print(f"В колоде '{state.selected_deck}' заметки не найдены.")
        return

    note_id = note.get("noteId", "unknown")
    print(f"\nGenerate test TTS for note_id={note_id}")

    if state.source_field_de:
        de_text_raw = get_note_field_value(note, state.source_field_de)
        de_text = clean_text_for_tts(de_text_raw)

        if de_text:
            try:
                de_path = generate_tts_audio(de_text, settings.tts_de_voice)
                print(f"DE text: {de_text}")
                print(f"DE audio file: {de_path}")
            except TTSServiceError as error:
                print(f"Ошибка генерации DE TTS: {error}")
        else:
            print("DE text: [пусто]")

    if state.source_field_en:
        en_text_raw = get_note_field_value(note, state.source_field_en)
        en_text = clean_text_for_tts(en_text_raw)

        if en_text:
            try:
                en_path = generate_tts_audio(en_text, settings.tts_en_voice)
                print(f"EN text: {en_text}")
                print(f"EN audio file: {en_path}")
            except TTSServiceError as error:
                print(f"Ошибка генерации EN TTS: {error}")
        else:
            print("EN text: [пусто]")

def handle_write_test_audio_to_first_note(state: AppState) -> None:
    if state.selected_deck is None:
        print("Сначала выбери колоду.")
        return

    required_fields = [
        state.source_field_de,
        state.source_field_en,
        state.audio_field_de,
        state.audio_field_en,
    ]
    if not all(required_fields):
        print("Сначала настрой все поля для TTS.")
        return

    try:
        note = get_first_note_info_by_deck(state.selected_deck)
    except AnkiConnectError as error:
        print(f"Ошибка AnkiConnect: {error}")
        return

    if note is None:
        print(f"В колоде '{state.selected_deck}' заметки не найдены.")
        return

    result = process_note_audio(note, state)

    print(f"\nWrite test audio to first note: note_id={result['note_id']}")

    if result["updated_fields"]:
        print("Поля заметки обновлены:")
        for field_name, value in result["updated_fields"].items():
            print(f"- {field_name}: {value}")
    else:
        print("Нет полей для обновления.")

    if result["skipped"]:
        print("Пропуски:")
        for item in result["skipped"]:
            print(f"- {item}")

    if result["errors"]:
        print("Ошибки:")
        for item in result["errors"]:
            print(f"- {item}")


def process_note_audio(note: dict[str, Any], state: AppState) -> dict[str, Any]:
    note_id = note.get("noteId")
    if not isinstance(note_id, int):
        return {
            "note_id": "unknown",
            "updated_fields": {},
            "errors": ["Некорректный note_id."],
        }

    updated_fields: dict[str, str] = {}
    errors: list[str] = []
    skipped: list[str] = []

    if state.source_field_de and state.audio_field_de:
        de_text_raw = get_note_field_value(note, state.source_field_de)
        de_text = clean_text_for_tts(de_text_raw)
        current_de_audio = get_note_field_value(note, state.audio_field_de)

        if not de_text:
            skipped.append("DE empty source")
        elif current_de_audio and not state.overwrite_audio:
            skipped.append("DE audio exists")
        else:
            try:
                de_path = generate_tts_audio(de_text, settings.tts_de_voice)
                de_filename = store_media_file(de_path)
                updated_fields[state.audio_field_de] = f"[sound:{de_filename}]"
            except (TTSServiceError, AnkiMediaError) as error:
                errors.append(f"DE: {error}")

    if state.source_field_en and state.audio_field_en:
        en_text_raw = get_note_field_value(note, state.source_field_en)
        en_text = clean_text_for_tts(en_text_raw)
        current_en_audio = get_note_field_value(note, state.audio_field_en)

        if not en_text:
            skipped.append("EN empty source")
        elif current_en_audio and not state.overwrite_audio:
            skipped.append("EN audio exists")
        else:
            try:
                en_path = generate_tts_audio(en_text, settings.tts_en_voice)
                en_filename = store_media_file(en_path)
                updated_fields[state.audio_field_en] = f"[sound:{en_filename}]"
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


def handle_generate_audio_for_all_notes(state: AppState) -> None:
    if state.selected_deck is None:
        print("Сначала выбери колоду.")
        return

    required_fields = [
        state.source_field_de,
        state.source_field_en,
        state.audio_field_de,
        state.audio_field_en,
    ]
    if not all(required_fields):
        print("Сначала настрой все поля для TTS.")
        return

    try:
        note_ids = find_note_ids_by_deck(state.selected_deck)
    except AnkiConnectError as error:
        print(f"Ошибка AnkiConnect: {error}")
        return

    if not note_ids:
        print(f"В колоде '{state.selected_deck}' заметки не найдены.")
        return

    print(f"\nНачинаю обработку колоды: {state.selected_deck}")
    print(f"Всего заметок: {len(note_ids)}")
    print("-----------------------------------")

    total_notes = 0
    updated_notes = 0
    skipped_notes = 0
    error_notes = 0

    for index, note_id in enumerate(note_ids, start=1):
        try:
            notes = get_notes_info([note_id])
        except AnkiConnectError as error:
            print(f"{index}/{len(note_ids)} note_id={note_id} -> ошибка чтения: {error}")
            error_notes += 1
            total_notes += 1
            continue

        if not notes:
            print(f"{index}/{len(note_ids)} note_id={note_id} -> заметка не найдена")
            error_notes += 1
            total_notes += 1
            continue

        note = notes[0]
        result = process_note_audio(note, state)

        total_notes += 1

        if result["errors"]:
            error_notes += 1
            print(f"{index}/{len(note_ids)} note_id={note_id} -> ERROR")
            for item in result["errors"]:
                print(f"   - {item}")
            continue

        if result["updated_fields"]:
            updated_notes += 1
            updated_field_names = ", ".join(result["updated_fields"].keys())
            print(f"{index}/{len(note_ids)} note_id={note_id} -> UPDATED ({updated_field_names})")
        else:
            skipped_notes += 1
            if result["skipped"]:
                print(f"{index}/{len(note_ids)} note_id={note_id} -> SKIPPED ({'; '.join(result['skipped'])})")
            else:
                print(f"{index}/{len(note_ids)} note_id={note_id} -> SKIPPED")

    print("\nГотово.")
    print(f"Всего заметок: {total_notes}")
    print(f"Обновлено: {updated_notes}")
    print(f"Пропущено: {skipped_notes}")
    print(f"С ошибками: {error_notes}")


def build_menu_commands() -> list[MenuCommand]:
    return [
        MenuCommand(
            key="1",
            title="Проверить соединение с Anki",
            handler=handle_check_connection,
        ),
        MenuCommand(
            key="2",
            title="Показать список колод",
            handler=handle_show_decks,
        ),
        MenuCommand(
            key="3",
            title="Выбрать колоду",
            handler=handle_select_deck,
        ),
        MenuCommand(
            key="4",
            title="Показать заметки из выбранной колоды",
            handler=handle_show_notes_from_selected_deck,
        ),
        MenuCommand(
            key="5",
            title="Показать структуру первой заметки",
            handler=handle_show_note_structure,
        ),
        MenuCommand(
            key="6",
            title="Настроить поля для TTS",
            handler=handle_select_tts_fields,
        ),
        MenuCommand(
            key="7",
            title="Preview TTS data",
            handler=handle_preview_tts_data,
        ),
        MenuCommand(
            key="8",
            title="Generate test TTS",
            handler=handle_generate_test_tts,
        ),
        MenuCommand(
            key="9",
            title="Write test audio to first note",
            handler=handle_write_test_audio_to_first_note,
        ),
        MenuCommand(
            key="10",
            title="Generate audio for ALL notes",
            handler=handle_generate_audio_for_all_notes,
),
    ]

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


def extract_note_preview(note: dict[str, Any]) -> str:
    """
    Пытается достать человекочитаемый preview заметки.
    """
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


def handle_show_notes_from_selected_deck(state: AppState) -> None:
    if state.selected_deck is None:
        print("Сначала выбери колоду.")
        return

    try:
        note_ids = find_note_ids_by_deck(state.selected_deck)
    except AnkiConnectError as error:
        print(f"Ошибка: {error}")
        return

    if not note_ids:
        print(f"\nВ колоде '{state.selected_deck}' заметки не найдены.")
        return

    preview_ids = note_ids[:10]

    try:
        notes = get_notes_info(preview_ids)
    except AnkiConnectError as error:
        print(f"Ошибка: {error}")
        return

    print(f"\nКолода: {state.selected_deck}")
    print(f"Всего заметок найдено: {len(note_ids)}")
    print("Показываю первые 10:\n")

    for index, note in enumerate(notes, start=1):
        note_id = note.get("noteId", "unknown")
        preview = extract_note_preview(note)
        print(f"{index}. note_id={note_id} | {preview}")

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


def run_cli() -> None:
    state = AppState()
    commands = build_menu_commands()

    command_map = {command.key: command for command in commands}

    while True:
        print_menu(state, commands)
        choice = input("\nВыбери действие: ").strip()

        if choice == "0":
            print("Выход из программы.")
            break

        command = command_map.get(choice)
        if command is None:
            print("Неизвестная команда. Попробуй ещё раз.")
            continue
        print("---------------")
        command.handler(state)