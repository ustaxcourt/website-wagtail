"""
0127: Bump JudgeIndex.seminar_intro_text from the old "policy paragraph only"
content to the new combined "policy paragraph + 'Below is the Running list...'
line" content.

Previously the "Below is the Running list of Tax Court Disclosures:" sentence
was hardcoded in `private_seminar_disclosures.html`. Per Jenna / Som's
feedback we don't want any hardcoded copy beneath the page header, so the
sentence moved into the editable `seminar_intro_text` RichTextField. This
data migration brings existing rows in line with the new field default
without clobbering any admin-customized intro copy.

Idempotent + edit-preserving: only updates rows whose current value matches
one of the three previously-known canonical states (empty, the original
OLD_PLACEHOLDER short text, or the old long policy paragraph). Anything
else means an editor has customized the field and we leave it alone.
"""

from django.db import migrations


# Previously-canonical values written by migrations 0123 (field default)
# and 0124 (data seed). Listing all three so the upgrade is safe regardless
# of which path a given environment took.
OLD_PLACEHOLDER = (
    "<p>The following are private seminar disclosures submitted by "
    "judges of the United States Tax Court.</p>"
)

OLD_CORRECT_INTRO = (
    "<p>The US Tax Court follows the <a href='https://www.uscourts.gov/administration-policies/"
    "privately-funded-seminars-disclosure-system/judicial-conference-policy-judges-attendance-"
    "privately-funded-educational-programs'> private seminars disclosure reporting policy</a> of all "
    "Federal US Courts which requires educational program providers and judges to disclose certain "
    "information relevant to judges' attendance at privately-funded educational programs. Any "
    "organization covered by the policy that issues an invitation to a federal judge to attend an "
    "educational program as a speaker, panelist, or attendee and offers to pay for or reimburse that "
    "judge, in excess of $480, must disclose financial and programmatic information and publish it on "
    "the Court's website for three years time.</p>"
)

NEW_CORRECT_INTRO = (
    OLD_CORRECT_INTRO + "<p>Below is the Running list of Tax Court Disclosures:</p>"
)


def set_combined_seminar_intro_text(apps, schema_editor):
    JudgeIndex = apps.get_model("home", "JudgeIndex")
    updated = (
        JudgeIndex.objects.filter(slug="judges")
        .filter(seminar_intro_text__in=[OLD_PLACEHOLDER, OLD_CORRECT_INTRO, ""])
        .update(seminar_intro_text=NEW_CORRECT_INTRO)
    )
    if updated:
        print(f"  Updated seminar_intro_text on {updated} JudgeIndex page(s).")


def revert_combined_seminar_intro_text(apps, schema_editor):
    JudgeIndex = apps.get_model("home", "JudgeIndex")
    JudgeIndex.objects.filter(
        slug="judges", seminar_intro_text=NEW_CORRECT_INTRO
    ).update(seminar_intro_text=OLD_CORRECT_INTRO)


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0126_alter_judgeindex_seminar_intro_text"),
    ]

    operations = [
        migrations.RunPython(
            set_combined_seminar_intro_text,
            revert_combined_seminar_intro_text,
        ),
    ]
