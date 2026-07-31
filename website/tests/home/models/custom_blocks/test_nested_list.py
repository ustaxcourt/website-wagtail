from django.test import SimpleTestCase

from home.models.custom_blocks.nested_list import create_nested_list_block


class NestedListBlockCleanTests(SimpleTestCase):
    def test_checkbox_list_strips_subtext(self):
        block = create_nested_list_block(max_depth=1)

        cleaned = block.clean(
            {
                "list_type": "checkbox",
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
