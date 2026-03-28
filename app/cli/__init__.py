from __future__ import annotations

from app.cli.state import AppState, MenuCommand
from app.cli.display import print_menu
from app.cli.handlers import (
    handle_check_connection,
    handle_select_deck,
    handle_audio_menu,
    handle_not_implemented,


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