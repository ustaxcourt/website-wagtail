from django.template.loader import render_to_string
from django.test import TestCase

from home.models.custom_blocks.nested_list import LIST_TYPE_CHOICES


class RecursiveListTemplateTests(TestCase):
    def test_checkbox_with_subtext_is_available_as_list_type_choice(self):
        self.assertIn(
            ("checkbox_with_subtext", "Checkbox with Subtext"), LIST_TYPE_CHOICES
        )

    def test_regular_checkbox_list_does_not_render_subtext(self):
        html = render_to_string(
            "home/_recursive_list.html",
            {
                "list_type": "checkbox",
                "items": [
                    {
                        "text": "<p>first item on the list</p>",
                        "subtext": "<p>subtext should not render</p>",
                    }
                ],
            },
        )

        self.assertIn("first item on the list", html)
        self.assertNotIn("subtext should not render", html)
        self.assertIn('class="nested-list checkbox-list"', html)
        self.assertNotIn("checkbox-list-with-subtext", html)

    def test_checkbox_with_subtext_list_renders_subtext(self):
        html = render_to_string(
            "home/_recursive_list.html",
            {
                "list_type": "checkbox_with_subtext",
                "items": [
                    {
                        "text": "<p>first item on the list</p>",
                        "subtext": "<p>subtext should render</p>",
                    }
                ],
            },
        )

        self.assertIn("first item on the list", html)
        self.assertIn("subtext should render", html)
        self.assertIn("checkbox-list-with-subtext", html)
        self.assertIn('class="has-subtext"', html)
