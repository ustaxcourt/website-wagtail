from unittest.mock import Mock, patch

from django.test import TestCase, override_settings

from home.management.commands.snippets.call_to_action_box import (
    CallToActionBoxInitializer,
    snippet_name,
)
from home.models.snippets.call_to_action import CallToActionBox


class CallToActionBoxInitializerTests(TestCase):
    def setUp(self):
        self.initializer = CallToActionBoxInitializer()

    def _create_box(self, header, body="Original body"):
        return CallToActionBox.objects.create(
            header=header,
            body=body,
            buttons=[],
        )

    @override_settings(SITE_IS_LIVE=True, BASE_URL="http://example.com")
    def test_update_preserves_existing_boxes_on_live(self):
        target_box = self._create_box(snippet_name, body="Old body")
        other_box = self._create_box("Another CTA", body="Keep me")

        with patch.object(
            self.initializer,
            "_get_arrow_forward_document",
            return_value=Mock(pk=123),
        ):
            self.initializer.update()

        target_box.refresh_from_db()
        other_box.refresh_from_db()

        self.assertEqual(CallToActionBox.objects.count(), 2)
        self.assertEqual(
            target_box.body,
            "Once you have your documents ready, start your petition through DAWSON, the Court's electronic filing system.",
        )
        self.assertEqual(other_box.body, "Keep me")

    @override_settings(SITE_IS_LIVE=True)
    def test_create_skips_when_target_missing_on_live(self):
        other_box = self._create_box("Another CTA", body="Keep me")

        with patch.object(self.initializer, "_get_arrow_forward_document") as mock_doc:
            self.initializer.create()

        other_box.refresh_from_db()
        self.assertEqual(CallToActionBox.objects.count(), 1)
        self.assertEqual(other_box.body, "Keep me")
        self.assertFalse(CallToActionBox.objects.filter(header=snippet_name).exists())
        mock_doc.assert_not_called()

    @override_settings(SITE_IS_LIVE=False, BASE_URL="http://example.com")
    def test_update_does_not_delete_unrelated_boxes_off_live(self):
        other_box = self._create_box("Another CTA", body="Keep me")

        with patch.object(
            self.initializer,
            "_get_arrow_forward_document",
            return_value=Mock(pk=456),
        ):
            self.initializer.update()

        other_box.refresh_from_db()
        target_box = CallToActionBox.objects.get(header=snippet_name)

        self.assertEqual(CallToActionBox.objects.count(), 2)
        self.assertEqual(other_box.body, "Keep me")
        self.assertEqual(
            target_box.body,
            "Once you have your documents ready, start your petition through DAWSON, the Court's electronic filing system.",
        )
        self.assertEqual(len(target_box.buttons), 2)
        self.assertEqual(target_box.buttons[1].value["text"], "File a Petition Online")
