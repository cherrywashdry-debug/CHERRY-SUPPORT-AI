"""Staff language menu — 5 languages."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import staff_translate as staff  # noqa: E402


class TestStaffLanguages(unittest.TestCase):
    def test_five_staff_languages(self) -> None:
        self.assertEqual(
            list(staff.STAFF_LANG_OPTIONS.keys()),
            ["th", "en", "km", "id", "zh"],
        )
        self.assertEqual(len(staff.STAFF_LANG_LABELS), 5)

    def test_staff_meaning_ok_by_language(self) -> None:
        self.assertTrue(staff.staff_meaning_ok("សួស្តី", "km"))
        self.assertTrue(staff.staff_meaning_ok("สวัสดี", "th"))
        self.assertTrue(staff.staff_meaning_ok("Hello", "en"))
        self.assertTrue(staff.staff_meaning_ok("Halo pelanggan", "id"))
        self.assertTrue(staff.staff_meaning_ok("你好", "zh"))
        self.assertFalse(staff.staff_meaning_ok("Hello", "km"))


if __name__ == "__main__":
    unittest.main()
