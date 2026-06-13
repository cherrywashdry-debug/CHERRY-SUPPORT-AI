"""Tests for CHERRY SUPPORT AI FAQ bot routing and content."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from faq_content import (  # noqa: E402
    BTN_BACK,
    BTN_CHANGE_LANG,
    BTN_CONTACT,
    BTN_DELIVERY_FEE,
    BTN_LAUNDRY,
    BTN_LAUNDRY_PRICE,
    BTN_LANG_TH,
    BTN_LOCATION,
    BTN_OPENING_HOURS,
    BTN_PRICE_DELIVERY,
    BTN_READ_BEFORE,
    BTN_SEPARATE_MIXED,
    BTN_SPECIAL_ITEMS,
    BUTTON_CONTENT_KEYS,
    FAQ_CONTENT,
    SUBMENU_TRIGGERS,
    faq_answer,
    normalize_lang,
)
from app import ALL_KNOWN_BUTTONS, resolve_button_action  # noqa: E402


class TestLanguage(unittest.TestCase):
    def test_default_lang(self) -> None:
        self.assertEqual(normalize_lang(""), "en")
        self.assertEqual(normalize_lang("xx"), "en")

    def test_supported_langs(self) -> None:
        self.assertEqual(normalize_lang("th"), "th")
        self.assertEqual(normalize_lang("km"), "km")

    def test_km_id_fallback_to_en_content(self) -> None:
        en = faq_answer("en", "opening_hours")
        km = faq_answer("km", "opening_hours")
        id_ = faq_answer("id", "opening_hours")
        self.assertEqual(km, en)
        self.assertEqual(id_, en)

    def test_th_content_differs_from_en(self) -> None:
        self.assertNotEqual(
            faq_answer("en", "opening_hours"),
            faq_answer("th", "opening_hours"),
        )


class TestContentCoverage(unittest.TestCase):
    def test_all_button_keys_have_en_and_th_answers(self) -> None:
        for key in BUTTON_CONTENT_KEYS.values():
            self.assertIn(key, FAQ_CONTENT["en"], msg=key)
            self.assertIn(key, FAQ_CONTENT["th"], msg=key)
            self.assertTrue(FAQ_CONTENT["en"][key].strip(), msg=key)
            self.assertTrue(FAQ_CONTENT["th"][key].strip(), msg=key)

    def test_location_has_map_link(self) -> None:
        self.assertIn("maps.app.goo.gl", faq_answer("en", "location"))

    def test_contact_has_whatsapp_and_phone(self) -> None:
        contact = faq_answer("en", "contact")
        self.assertIn("wa.me", contact)
        self.assertIn("+66 94 283 9236", contact)


class TestButtonRouting(unittest.TestCase):
    def test_main_menu_submenus(self) -> None:
        for btn in SUBMENU_TRIGGERS:
            action = resolve_button_action(btn)
            self.assertIsNotNone(action)
            self.assertEqual(action["type"], "submenu")

    def test_price_submenu_answers(self) -> None:
        action = resolve_button_action(BTN_LAUNDRY_PRICE)
        self.assertEqual(action, {"type": "answer", "content_key": "price_laundry"})
        action = resolve_button_action(BTN_DELIVERY_FEE)
        self.assertEqual(action, {"type": "answer", "content_key": "price_delivery_fee"})

    def test_direct_answers(self) -> None:
        action = resolve_button_action(BTN_OPENING_HOURS)
        self.assertEqual(action, {"type": "answer", "content_key": "opening_hours"})
        action = resolve_button_action(BTN_CONTACT)
        self.assertEqual(action, {"type": "answer", "content_key": "contact"})
        action = resolve_button_action(BTN_LOCATION)
        self.assertEqual(action, {"type": "answer", "content_key": "location"})

    def test_laundry_submenu(self) -> None:
        action = resolve_button_action(BTN_SEPARATE_MIXED)
        self.assertEqual(action, {"type": "answer", "content_key": "laundry_separate"})

    def test_read_before_submenu(self) -> None:
        action = resolve_button_action(BTN_SPECIAL_ITEMS)
        self.assertEqual(action, {"type": "answer", "content_key": "read_special"})

    def test_back_to_menu(self) -> None:
        self.assertEqual(resolve_button_action(BTN_BACK), {"type": "main_menu"})

    def test_language_selection(self) -> None:
        action = resolve_button_action(BTN_LANG_TH)
        self.assertEqual(action, {"type": "set_language", "lang": "th"})

    def test_unknown_text_returns_none(self) -> None:
        self.assertIsNone(resolve_button_action("random hello"))
        self.assertIsNone(resolve_button_action(""))

    def test_all_known_buttons_resolve(self) -> None:
        for btn in ALL_KNOWN_BUTTONS:
            if btn == BTN_CHANGE_LANG:
                action = resolve_button_action(btn)
                self.assertEqual(action["type"], "language_menu")
            else:
                self.assertIsNotNone(resolve_button_action(btn), msg=btn)


class TestSubmenuEntryPoints(unittest.TestCase):
    def test_price_delivery_opens_submenu(self) -> None:
        action = resolve_button_action(BTN_PRICE_DELIVERY)
        self.assertEqual(action, {"type": "submenu", "submenu": "price"})

    def test_laundry_opens_submenu(self) -> None:
        action = resolve_button_action(BTN_LAUNDRY)
        self.assertEqual(action, {"type": "submenu", "submenu": "laundry"})

    def test_read_before_opens_submenu(self) -> None:
        action = resolve_button_action(BTN_READ_BEFORE)
        self.assertEqual(action, {"type": "submenu", "submenu": "read_before"})


if __name__ == "__main__":
    unittest.main()
