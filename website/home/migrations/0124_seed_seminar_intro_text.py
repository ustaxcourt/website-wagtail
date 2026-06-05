from django.db import migrations

CORRECT_INTRO = (
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

OLD_PLACEHOLDER = (
    "<p>The following are private seminar disclosures submitted by "
    "judges of the United States Tax Court.</p>"
)


def set_seminar_intro_text(apps, schema_editor):
    JudgeIndex = apps.get_model("home", "JudgeIndex")
    updated = (
        JudgeIndex.objects.filter(slug="judges")
        .exclude(seminar_intro_text=CORRECT_INTRO)
        .update(seminar_intro_text=CORRECT_INTRO)
    )
    if updated:
        print(f"  Updated seminar_intro_text on {updated} JudgeIndex page(s).")


def revert_seminar_intro_text(apps, schema_editor):
    JudgeIndex = apps.get_model("home", "JudgeIndex")
    JudgeIndex.objects.filter(slug="judges", seminar_intro_text=CORRECT_INTRO).update(
        seminar_intro_text=OLD_PLACEHOLDER
    )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0123_judgeindex_seminar_text_and_disclosure_settings"),
    ]

    operations = [
        migrations.RunPython(
            set_seminar_intro_text,
            revert_seminar_intro_text,
        ),
    ]
