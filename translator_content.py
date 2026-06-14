"""UI labels for CHERRY translator — translate only, no Q&A."""
from __future__ import annotations

LANG_TH = "th"
LANG_EN = "en"
LANG_KM = "km"
LANG_ID = "id"
LANG_ZH = "zh"

SINGLE_LANG_ORDER = (LANG_TH, LANG_EN, LANG_KM, LANG_ID, LANG_ZH)

LANG_NAMES: dict[str, str] = {
    LANG_TH: "Thai",
    LANG_EN: "English",
    LANG_KM: "Khmer",
    LANG_ID: "Indonesian",
    LANG_ZH: "Chinese",
}

LANG_FLAGS: dict[str, str] = {
    LANG_TH: "🇹🇭",
    LANG_EN: "🇬🇧",
    LANG_KM: "🇰🇭",
    LANG_ID: "🇮🇩",
    LANG_ZH: "🇨🇳",
}

BTN_TO_TH = "🇹🇭 Translate To Thai"
BTN_TO_EN = "🇬🇧 Translate To English"
BTN_TO_KM = "🇰🇭 Translate To Khmer"
BTN_TO_ID = "🇮🇩 Translate To Indonesian"
BTN_TO_ZH = "🇨🇳 Translate To Chinese"
BTN_ALL = "🔁 Translate To All 5 Languages"

MODE_ALL = "all"
SESSION_MODE_KEY = "translator_mode"

WELCOME = (
    "🌐 CHERRY Translator\n\n"
    "Choose language — then send text.\n"
    "Translate ONLY. No answers. No questions."
)

MODE_PROMPT = "Send the text you want translated."

TRANSLATE_FAIL = "⚠️ Could not translate. Send /health to check OpenAI."
EMPTY_INPUT = "Please send text to translate."


def lang_label(code: str) -> str:
    flag = LANG_FLAGS.get(code, "")
    name = LANG_NAMES.get(code, code)
    return f"{flag} {name}".strip()


def single_mode_prompt(code: str) -> str:
    return f"{lang_label(code)} mode\n\n{MODE_PROMPT}"


def single_result_header(code: str) -> str:
    return f"{lang_label(code)} Translation"


def format_all_results(results: dict[str, str]) -> str:
    blocks: list[str] = []
    for code in SINGLE_LANG_ORDER:
        blocks.append(f"{lang_label(code)}\n{results.get(code, '—')}")
        blocks.append("━━━━━━━━━━━━━━")
    if blocks and blocks[-1] == "━━━━━━━━━━━━━━":
        blocks.pop()
    return "\n".join(blocks)
