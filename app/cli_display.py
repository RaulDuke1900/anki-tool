from __future__ import annotations

from app.cli_state import AppState, MenuCommand


def print_menu(state: AppState, commands: list[MenuCommand]) -> None:
    print("\n=== Anki Tool ===")
    print(f"Текущая колода: {state.selected_deck or '[не выбрана]'}")
    print(f"DE source: {state.source_field_de or '[не выбрано]'}")
    print(f"EN source: {state.source_field_en or '[не выбрано]'}")
    print(f"DE audio target: {state.audio_field_de or '[не выбрано]'}")
    print(f"EN audio target: {state.audio_field_en or '[не выбрано]'}")
    print(f"Overwrite audio: {'yes' if state.overwrite_audio else 'no'}")
    print("------------------------------")

    for command in commands:
        print(f"{command.key}. {command.title}")

    print("0. Выход")