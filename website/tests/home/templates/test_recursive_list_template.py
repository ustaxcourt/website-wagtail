from django.template.loader import render_to_string
from django.test import TestCase

from home.models.custom_blocks.nested_list import LIST_TYPE_CHOICES


class RecursiveListTemplateTests(TestCase):
    def test_checkbox_with_subtext_is_available_as_list_type_choice(self):
        self.assertIn(
            ("checkbox_with_subtext", "Checkbox with Subtext"), LIST_TYPE_CHOICES
        )

    def test_checkbox_list_renders_subtext_only_for_items_that_have_it(self):
        """Subtext is an optional per-item sub-label: a plain 'checkbox' list
        can mix items with and without a sub-label."""
        html = render_to_string(
            "home/_recursive_list.html",
            {
                "list_type": "checkbox",
                "items": [
                    {
                        "text": "<p>first item on the list</p>",
                        "subtext": "<p>subtext should render</p>",
                    },
                    {
                        "text": "<p>second item on the list</p>",
                        "subtext": "",
                    },
                ],
            },
        )

        self.assertIn("first item on the list", html)
        self.assertIn("subtext should render", html)
        self.assertIn("second item on the list", html)
        self.assertIn('class="nested-list checkbox-list"', html)
        self.assertIn('class="has-subtext"', html)

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
        self.assertIn('class="nested-list checkbox-list"', html)
        self.assertIn('class="has-subtext"', html)

    def test_disabled_checkbox_item_renders_disabled_attribute(self):
        html = render_to_string(
            "home/_recursive_list.html",
            {
                "list_type": "checkbox",
                "items": [
                    {
                        "text": "<p>disabled item</p>",
                        "disabled": True,
                    },
                    {
                        "text": "<p>enabled item</p>",
                        "disabled": False,
                    },
                ],
            },
        )

        self.assertIn("disabled item", html)
        self.assertIn("enabled item", html)
        self.assertIn(
            '<input type="checkbox" disabled data-static-disabled="true" aria-disabled="true">',
            html,
        )
        self.assertIn('class="checkbox-label-container is-disabled"', html)
        self.assertIn('<input type="checkbox">', html)

    def test_conditional_checkbox_renders_condition_key_and_requires_checked(self):
        """A checkbox item can require another item's Condition Key to be
        checked before it becomes enabled. It should render as disabled by
        default (nothing is checked on page load) with the data attributes
        the client-side script needs to wire up the dependency."""
        html = render_to_string(
            "home/_recursive_list.html",
            {
                "list_type": "checkbox",
                "items": [
                    {
                        "text": "<p>I agree to the terms</p>",
                        "condition_key": "agree",
                    },
                    {
                        "text": "<p>Proceed to next step</p>",
                        "requires_checked": "agree",
                    },
                ],
            },
        )

        self.assertIn('data-condition-key="agree"', html)
        self.assertIn('data-requires-checked="agree"', html)
        self.assertIn(
            'class="checkbox-label-container is-disabled" data-requires-checked="agree"',
            html,
        )
        self.assertIn('<input type="checkbox" disabled aria-disabled="true">', html)
