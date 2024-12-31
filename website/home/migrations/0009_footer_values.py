from django.db import migrations


def populate_footer_defaults(apps, schema_editor):
    Footer = apps.get_model("home", "Footer")

    Footer.objects.create(
        technicalQuestions=(
            "For assistance with DAWSON, view the FAQs and other materials "
            '<a href="https://www.ustaxcourt.gov/faqs" target="_blank">here</a>. '
            "To contact the Webmaster for technical issues or problems with the website, "
            'send an email to <a href="mailto:webmaster@ustaxcourt.gov">webmaster@ustaxcourt.gov</a>. '
            "No documents can be filed with the Court at this email address."
        ),
        otherQuestions="For all non-technical questions, contact the Office of the Clerk of the Court at (202) 521-0700.",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0008_footer_remove_homepage_otherquestions_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_footer_defaults),
    ]
