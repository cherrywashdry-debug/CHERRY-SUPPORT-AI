"""Translator menu — 5 target languages, translate only."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from translator_content import (  # noqa: E402
    LANG_NAMES,
    MODE_ALL,
    SINGLE_LANG_ORDER,
    lang_label,
)


class TestTranslatorContent(unittest.TestCase):
    def test_five_target_languages(self) -> None:
        self.assertEqual(len(SINGLE_LANG_ORDER), 5)
        self.assertEqual(set(LANG_NAMES.keys()), set(SINGLE_LANG_ORDER))

    def test_lang_labels(self) -> None:
        self.assertIn("Thai", lang_label("th"))
        self.assertIn("Chinese", lang_label("zh"))

    def test_all_mode_constant(self) -> None:
        self.assertEqual(MODE_ALL, "all")


if __name__ == "__main__":
    unittest.main()
