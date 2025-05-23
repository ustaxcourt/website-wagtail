# Generated by Django 5.1.7 on 2025-04-01 19:37

import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0031_alter_enhancedstandardpage_body_and_more"),
        ("wagtailcore", "0094_alter_page_locale"),
    ]

    operations = [
        migrations.CreateModel(
            name="DirectoryIndex",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "body",
                    wagtail.fields.StreamField(
                        [("directory", 18)],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.CharBlock", (), {"label": "Heading 2"}),
                            1: ("wagtail.blocks.CharBlock", (), {"label": "Heading 3"}),
                            2: (
                                "wagtail.blocks.BooleanBlock",
                                (),
                                {
                                    "default": True,
                                    "help_text": "Add Horizontal Rule.",
                                    "label": "Horizontal Rule",
                                },
                            ),
                            3: ("wagtail.blocks.CharBlock", (), {}),
                            4: ("wagtail.blocks.CharBlock", (), {"required": False}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("text", 3), ("anchortag", 4)]],
                                {
                                    "help_text": "Heading 2 with optional anchor tag for linking",
                                    "label": "Heading 2 with Anchor Tag",
                                },
                            ),
                            6: (
                                "wagtail.blocks.StructBlock",
                                [[("text", 3), ("url", 4)]],
                                {"label": "Clickable Button"},
                            ),
                            7: (
                                "wagtail.blocks.ChoiceBlock",
                                [],
                                {
                                    "choices": [
                                        ("indented", "Indented"),
                                        ("unindented", "Unindented"),
                                    ]
                                },
                            ),
                            8: (
                                "wagtail.blocks.ChoiceBlock",
                                [],
                                {
                                    "choices": [
                                        ("", "None"),
                                        ("fa-solid fa-book", "Book"),
                                        (
                                            "fa-solid fa-building-columns",
                                            "Building Bank",
                                        ),
                                        ("fa-solid fa-calendar", "Calendar Month"),
                                        ("fa-solid fa-chevron-right", "Chevron Right"),
                                        ("fa-solid fa-file", "File"),
                                        ("fa-solid fa-gavel", "Hammer"),
                                        ("fa-solid fa-circle-info", "Info"),
                                        ("fa-solid fa-check", "Check"),
                                        ("fa-solid fa-link", "Link"),
                                        ("fa-solid fa-exclamation", "Exclamation Mark"),
                                        ("fa-solid fa-file-pdf", "Pdf"),
                                        ("fa-solid fa-scale-balanced", "Scale"),
                                        ("fa-solid fa-user", "User"),
                                        ("fa-solid fa-video", "Video"),
                                        ("fa-solid fa-gear", "Settings"),
                                        ("fa-solid fa-briefcase", "Briefcase"),
                                        ("fa-solid fa-magnifying-glass", "Search"),
                                    ],
                                    "required": False,
                                },
                            ),
                            9: (
                                "wagtail.documents.blocks.DocumentChooserBlock",
                                (),
                                {"required": False},
                            ),
                            10: (
                                "wagtail.blocks.BooleanBlock",
                                (),
                                {"required": False},
                            ),
                            11: (
                                "wagtail.blocks.StructBlock",
                                [
                                    [
                                        ("title", 3),
                                        ("icon", 8),
                                        ("document", 9),
                                        ("video", 9),
                                        ("url", 4),
                                        ("text_only", 10),
                                    ]
                                ],
                                {},
                            ),
                            12: ("wagtail.blocks.ListBlock", (11,), {}),
                            13: (
                                "wagtail.blocks.StructBlock",
                                [[("class", 7), ("links", 12)]],
                                {"label": "Links"},
                            ),
                            14: (
                                "wagtail.snippets.blocks.SnippetChooserBlock",
                                (),
                                {
                                    "help_text": "Optionally pick a JudgeCollection snippet",
                                    "label": "Judge Collection",
                                    "required": False,
                                    "target_model": "home.JudgeCollection",
                                },
                            ),
                            15: ("wagtail.blocks.RichTextBlock", (), {}),
                            16: (
                                "wagtail.blocks.StructBlock",
                                [[("description", 15), ("phone_number", 3)]],
                                {},
                            ),
                            17: ("wagtail.blocks.ListBlock", (16,), {}),
                            18: (
                                "wagtail.blocks.StreamBlock",
                                [
                                    [
                                        ("h2", 0),
                                        ("h3", 1),
                                        ("hr", 2),
                                        ("h2WithAnchorTag", 5),
                                        ("clickableButton", 6),
                                        ("links", 13),
                                        ("JudgeCollection", 14),
                                        ("DirectoryEntry", 17),
                                    ]
                                ],
                                {},
                            ),
                        },
                        help_text="Directory entries or judge profiles",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
        migrations.RemoveField(
            model_name="enhancedstandardpage",
            name="description",
        ),
        migrations.RemoveField(
            model_name="enhancedstandardpage",
            name="title_text",
        ),
        migrations.RemoveField(
            model_name="enhancedstandardpage",
            name="video_url",
        ),
    ]
