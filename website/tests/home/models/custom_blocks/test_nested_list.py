from django.test import SimpleTestCase

from home.models.custom_blocks.nested_list import create_nested_list_block


class NestedListBlockCleanTests(SimpleTestCase):
    def test_checkbox_list_keeps_subtext(self):
        """Subtext is an optional per-item sub-label on the plain 'checkbox'
        list type, not just the legacy 'checkbox_with_subtext' type."""
        block = create_nested_list_block(max_depth=1)

        cleaned = block.clean(
            {
                "list_type": "checkbox",
                "items": [
                    {
                        "text": "<p>first item</p>",
                        "subtext": "<p>should stay</p>",
                        "image": None,
                    }
                ],
            }
        )

        self.assertNotEqual(cleaned["items"][0]["subtext"].source, "")

    def test_ordered_list_strips_subtext(self):
        block = create_nested_list_block(max_depth=1)

        cleaned = block.clean(
            {
                "list_type": "ordered",
                "items": [
                    {
                        "text": "<p>first item</p>",
                        "subtext": "<p>should be removed</p>",
                        "image": None,
                    }
                ],
            }
        )

        self.assertEqual(cleaned["items"][0]["subtext"].source, "")

    def test_checkbox_with_subtext_keeps_subtext(self):
        block = create_nested_list_block(max_depth=1)

        cleaned = block.clean(
            {
                "list_type": "checkbox_with_subtext",
                "items": [
                    {
                        "text": "<p>first item</p>",
                        "subtext": "<p>should stay</p>",
                        "image": None,
                    }
                ],
            }
        )

        self.assertNotEqual(cleaned["items"][0]["subtext"].source, "")

    def test_checkbox_list_keeps_disabled(self):
        block = create_nested_list_block(max_depth=1)

        cleaned = block.clean(
            {
                "list_type": "checkbox",
                "items": [
                    {
                        "text": "<p>first item</p>",
                        "subtext": "",
                        "disabled": True,
                        "image": None,
                    }
                ],
            }
        )

        self.assertTrue(cleaned["items"][0]["disabled"])

    def test_checkbox_with_subtext_keeps_disabled(self):
        block = create_nested_list_block(max_depth=1)

        cleaned = block.clean(
            {
                "list_type": "checkbox_with_subtext",
                "items": [
                    {
                        "text": "<p>first item</p>",
                        "subtext": "<p>should stay</p>",
                        "disabled": True,
                        "image": None,
                    }
                ],
            }
        )

        self.assertTrue(cleaned["items"][0]["disabled"])

    def test_checkbox_list_keeps_conditional_fields(self):
        block = create_nested_list_block(max_depth=1)

        cleaned = block.clean(
            {
                "list_type": "checkbox",
                "items": [
                    {
                        "text": "<p>I agree</p>",
                        "subtext": "",
                        "disabled": False,
                        "condition_key": "agree",
                        "requires_checked": "",
                        "image": None,
                    },
                    {
                        "text": "<p>Next step</p>",
                        "subtext": "",
                        "disabled": False,
                        "condition_key": "",
                        "requires_checked": "agree",
                        "image": None,
                    },
                ],
            }
        )

        self.assertEqual(cleaned["items"][0]["condition_key"], "agree")
        self.assertEqual(cleaned["items"][1]["requires_checked"], "agree")

    def test_non_checkbox_list_strips_conditional_fields(self):
        block = create_nested_list_block(max_depth=1)

        cleaned = block.clean(
            {
                "list_type": "unordered",
                "items": [
                    {
                        "text": "<p>Next step</p>",
                        "subtext": "",
                        "disabled": False,
                        "condition_key": "agree",
                        "requires_checked": "agree",
                        "image": None,
                    }
                ],
            }
        )

        self.assertEqual(cleaned["items"][0]["condition_key"], "")
        self.assertEqual(cleaned["items"][0]["requires_checked"], "")

    def test_non_checkbox_list_strips_disabled(self):
        block = create_nested_list_block(max_depth=1)

        cleaned = block.clean(
            {
                "list_type": "unordered",
                "items": [
                    {
                        "text": "<p>first item</p>",
                        "subtext": "",
                        "disabled": True,
                        "image": None,
                    }
                ],
            }
        )

        self.assertFalse(cleaned["items"][0]["disabled"])
