from django.db import migrations
from django.utils import timezone

# The FilterTag options that were previously hardcoded in the Q&A block. The slugs
# match the values already stored in existing Q&As, so no page content changes.
INITIAL_TAGS = [
    ("filing", "Filing"),
    ("deadlines", "Deadlines"),
    ("representation", "Representation"),
    ("forms-documents", "Forms & Documents"),
    ("trial-process", "Trial Process"),
    ("fees-costs", "Fees & Costs"),
    ("after-decision", "After Decision"),
]


def seed_filter_tags(apps, schema_editor):
    FAQFilterTag = apps.get_model("home", "FAQFilterTag")
    now = timezone.now()
    for slug, name in INITIAL_TAGS:
        FAQFilterTag.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "live": True,
                "first_published_at": now,
                "last_published_at": now,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("home", "0149_faq_filter_tag")]

    operations = [migrations.RunPython(seed_filter_tags, migrations.RunPython.noop)]
