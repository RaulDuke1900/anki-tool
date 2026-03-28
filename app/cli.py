from __future__ import annotations

from app.cli_state import AppState, MenuCommand
from app.cli_display import print_menu
from app.cli_handlers import (
    handle_check_connection,
    handle_show_decks,
    handle_select_deck,
    handle_show_notes_from_selected_deck,
    handle_show_note_structure,
    handle_select_tts_fields,
    handle_preview_tts_data,
    handle_generate_test_tts,
    handle_write_test_audio_to_first_note,
    handle_generate_audio_for_all_notes,
)


def build_menu_commands() -> list[MenuCommand]:
    return [
        MenuCommand(key="1",  title="Проверить соединение с Anki",          
                    handler=handle_check_connection),
        MenuCommand(key="2",  title="Показать список колод",                 
                    handler=handle_show_decks),
        MenuCommand(key="3",  title="Выбрать колоду",                        
                    handler=handle_select_deck),
        MenuCommand(key="4",  title="Показать заметки из выбранной колоды",  
                    handler=handle_show_notes_from_selected_deck),
        MenuCommand(key="5",  title="Показать структуру первой заметки",      
                    handler=handle_show_note_structure),
        MenuCommand(key="6",  title="Настроить поля для TTS",                
                    handler=handle_select_tts_fields),
        MenuCommand(key="7",  title="Preview TTS data",                      
                    handler=handle_preview_tts_data),
        MenuCommand(key="8",  title="Generate test TTS",                     
                    handler=handle_generate_test_tts),
        MenuCommand(key="9",  title="Write test audio to first note",        
                    handler=handle_write_test_audio_to_first_note),
        MenuCommand(key="10", title="Generate audio for ALL notes",          
                    handler=handle_generate_audio_for_all_notes),
    ]


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