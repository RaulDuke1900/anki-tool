from __future__ import annotations

from app.cli.state import AppState, MenuCommand
from app.cli.display import print_menu
from app.cli.handlers import (
    handle_check_connection,
    handle_select_deck,
    handle_audio_menu,
    handle_not_implemented,
    handle_select_tts_fields,
    handle_toggle_language_mode,
    handle_preview_tts_data,
    handle_generate_test_tts,
    handle_write_test_audio_to_first_note,
    handle_generate_audio_for_all_notes,
)


def build_menu_commands() -> list[MenuCommand]:
    return [
        MenuCommand(key="1", title="Проверить подключение к Anki",
                handler=handle_check_connection),

    MenuCommand(key="2", title="Выбрать колоду",
                handler=handle_select_deck),

    MenuCommand(key="3", title="Аудио",
                handler=handle_audio_menu),

    MenuCommand(key="4", title="Перевод (пока не реализовано)",
                handler=handle_not_implemented),

    MenuCommand(key="5", title="Словари (пока не реализовано)",
                handler=handle_not_implemented),

    MenuCommand(key="6", title="ИИ инструменты (пока не реализовано)",
                handler=handle_not_implemented),
    ]

def build_audio_menu_commands() -> list[MenuCommand]:
    return [
        MenuCommand(key="1", title="Настроить поля для аудио",
                    handler=handle_select_tts_fields),
        MenuCommand(key="2", title="Настроить режим языка",
                    handler=handle_toggle_language_mode),
        MenuCommand(key="3", title="Показать preview",
                    handler=handle_preview_tts_data),
        MenuCommand(key="4", title="Сгенерировать тестовое аудио",
                    handler=handle_generate_test_tts),
        MenuCommand(key="5", title="Записать тестовое аудио в первую заметку",
                    handler=handle_write_test_audio_to_first_note),
        MenuCommand(key="6", title="Запустить генерацию для всех заметок",
                    handler=handle_generate_audio_for_all_notes),
    ]

def run_submenu(
    state: AppState,
    title: str,
    commands: list[MenuCommand],
) -> None:
    command_map = {command.key: command for command in commands}

    while True:
        print(f"\n=== {title} ===")
        for command in commands:
            print(f"{command.key}. {command.title}")
        print("0. Назад")

        choice = input("\nВыбери действие: ").strip()

        if choice == "0":
            break

        command = command_map.get(choice)
        if command is None:
            print("Неизвестная команда. Попробуй ещё раз.")
            continue

        print("---------------")
        command.handler(state)

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