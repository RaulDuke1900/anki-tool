from __future__ import annotations

import html
import re


CLOZE_PATTERN = re.compile(r"\{\{c\d+::(.*?)(?:::(.*?))?\}\}")
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")


def _remove_cloze_markup(text: str) -> str:
    """
    Превращает {{c1::word}} в word.
    Также поддерживает форму {{c1::word::hint}} -> word.
    """
    return CLOZE_PATTERN.sub(r"\1", text)


def _remove_html_tags(text: str) -> str:
    """
    Удаляет простые HTML-теги.
    """
    return HTML_TAG_PATTERN.sub(" ", text)

def _remove_plus_and_case_hint(text: str) -> str:
    """
    Удаляет '+' и всё, что идёт после него.
    Пример:
    'übertreffen in +Dat' -> 'übertreffen in'
    """
    if "+" in text:
        text = text.split("+", 1)[0]
    return text.strip()

def clean_text_for_tts(text: str) -> str:
    """
    Очищает текст для озвучки:
    - декодирует HTML entities
    - убирает cloze-разметку
    - убирает HTML-теги
    - нормализует пробелы
    """
    cleaned = html.unescape(text)
    cleaned = _remove_cloze_markup(cleaned)
    cleaned = _remove_html_tags(cleaned)
    cleaned = _remove_plus_and_case_hint(cleaned)
    cleaned = WHITESPACE_PATTERN.sub(" ", cleaned).strip()
    return cleaned