"""Tests for home/models/snippets/judges.py"""

import pytest
from django.core.exceptions import ValidationError

from home.models.snippets.judges import (
    JudgeCollection,
    JudgeCollectionOrderable,
    JudgeProfile,
    JudgeRole,
)

pytestmark = pytest.mark.django_db


def make_judge(first="Ann", last="Adams", title="Judge", **kwargs):
    return JudgeProfile.objects.create(
        first_name=first, last_name=last, title=title, **kwargs
    )


def collection_names(judge):
    return set(
        JudgeCollectionOrderable.objects.filter(judge=judge).values_list(
            "collection__name", flat=True
        )
    )


class TestJudgeProfileSave:
    def test_display_name_built_from_name_parts_when_blank(self):
        judge = make_judge(first="Ann", last="Adams", middle_initial="B", suffix="Jr")
        assert judge.display_name == "Ann B Adams Jr"

    def test_display_name_skips_empty_parts(self):
        judge = make_judge(first="Ann", last="Adams")
        assert judge.display_name == "Ann Adams"

    def test_explicit_display_name_is_preserved(self):
        judge = make_judge(display_name="Hon. Ann Adams")
        assert judge.display_name == "Hon. Ann Adams"

    def test_whitespace_display_name_is_regenerated(self):
        judge = make_judge(display_name="   ")
        assert judge.display_name == "Ann Adams"

    def test_last_updated_date_is_set(self):
        assert make_judge().last_updated_date is not None

    def test_new_judge_added_to_auto_managed_collection(self):
        judge = make_judge(title="Judge")
        assert collection_names(judge) == {"Judges"}

    def test_each_title_maps_to_its_collection(self):
        mapping = {
            "Senior Judge": "Senior Judges",
            "Special Trial Judge": "Special Trial Judges",
            "Senior Special Trial Judge": "Senior Special Trial Judges",
        }
        for title, expected in mapping.items():
            judge = make_judge(first=title, last=title, title=title)
            assert collection_names(judge) == {expected}

    def test_resave_does_not_duplicate_membership(self):
        judge = make_judge()
        judge.save()
        judge.save()
        assert JudgeCollectionOrderable.objects.filter(judge=judge).count() == 1

    def test_title_change_moves_judge_between_collections(self):
        judge = make_judge(title="Judge")
        judge.title = "Senior Judge"
        judge.save()
        assert collection_names(judge) == {"Senior Judges"}

    def test_title_change_when_old_collection_missing_still_adds_new(self):
        judge = make_judge(title="Judge")
        JudgeCollection.objects.filter(name="Judges").delete()
        judge.title = "Senior Judge"
        judge.save()
        assert collection_names(judge) == {"Senior Judges"}

    def test_str_and_revisions(self):
        judge = make_judge()
        assert str(judge) == "Ann Adams"
        assert list(judge.revisions.all()) == []


class TestJudgeCollectionReorder:
    def test_reorder_with_no_judges_is_noop(self):
        collection = JudgeCollection.objects.create(name="Empty")
        collection.save()
        assert collection.ordered_judges.count() == 0

    def test_judges_sorted_by_last_then_first_name(self):
        zed = make_judge(first="Zed", last="Young")
        amy = make_judge(first="Amy", last="Baker")
        abe = make_judge(first="Abe", last="Baker")
        collection = JudgeCollection.objects.get(name="Judges")
        ordered = [
            o.judge
            for o in collection.ordered_judges.order_by("sort_order").select_related(
                "judge"
            )
        ]
        assert ordered == [abe, amy, zed]

    def test_restricted_role_judge_is_first(self):
        make_judge(first="Amy", last="Aaron")
        chief = make_judge(first="Zed", last="Young")
        JudgeRole.objects.create(role_name="Chief Judge", judge=chief)
        collection = JudgeCollection.objects.get(name="Judges")
        first = collection.ordered_judges.order_by("sort_order").first()
        assert first.judge == chief

    def test_collection_str_and_revisions(self):
        collection = JudgeCollection.objects.create(name="Featured")
        assert str(collection) == "Featured"
        assert list(collection.revisions.all()) == []


class TestJudgeRoleValidation:
    def test_cannot_rename_restricted_role(self):
        role = JudgeRole.objects.create(role_name="Chief Judge")
        role.role_name = "Something Else"
        with pytest.raises(ValidationError):
            role.clean()

    def test_can_rename_unrestricted_role(self):
        role = JudgeRole.objects.create(role_name="Clerk")
        role.role_name = "Head Clerk"
        role.clean()

    def test_judge_cannot_hold_two_restricted_roles(self):
        judge = make_judge()
        JudgeRole.objects.create(role_name="Chief Judge", judge=judge)
        second = JudgeRole(role_name="Chief Special Trial Judge", judge=judge)
        with pytest.raises(ValidationError) as exc:
            second.clean()
        assert "already assigned" in str(exc.value)

    def test_restricted_role_for_judge_without_conflict_is_valid(self):
        judge = make_judge()
        JudgeRole(role_name="Chief Judge", judge=judge).clean()

    def test_cannot_delete_restricted_role(self):
        role = JudgeRole.objects.create(role_name="Chief Judge")
        with pytest.raises(ValidationError):
            role.delete()
        assert JudgeRole.objects.filter(pk=role.pk).exists()

    def test_can_delete_unrestricted_role(self):
        role = JudgeRole.objects.create(role_name="Clerk")
        role.delete()
        assert not JudgeRole.objects.filter(pk=role.pk).exists()


class TestJudgeRoleSave:
    def test_str_with_and_without_judge(self):
        judge = make_judge()
        assert str(JudgeRole(role_name="Clerk", judge=judge)).startswith("Clerk, ")
        assert str(JudgeRole(role_name="Clerk")) == "Clerk, ** Selection Pending **"

    def test_revisions_property(self):
        role = JudgeRole.objects.create(role_name="Clerk")
        assert list(role.revisions.all()) == []

    def test_save_reorders_collections_of_assigned_judge(self):
        make_judge(first="Amy", last="Aaron")
        late = make_judge(first="Zed", last="Young")
        role = JudgeRole.objects.create(role_name="Chief Judge", judge=late)
        collection = JudgeCollection.objects.get(name="Judges")
        assert collection.ordered_judges.order_by("sort_order").first().judge == late
        assert role.judge == late

    def test_reassigning_role_reorders_previous_judges_collections(self):
        first = make_judge(first="Amy", last="Aaron")
        second = make_judge(first="Zed", last="Young")
        role = JudgeRole.objects.create(role_name="Chief Judge", judge=second)
        role.judge = first
        role.save()
        collection = JudgeCollection.objects.get(name="Judges")
        assert collection.ordered_judges.order_by("sort_order").first().judge == first

    def test_unassigning_judge_from_role(self):
        judge = make_judge()
        role = JudgeRole.objects.create(role_name="Chief Judge", judge=judge)
        role.judge = None
        role.save()
        role.refresh_from_db()
        assert role.judge is None

    def test_save_skips_reorder_for_non_auto_managed_collection(self):
        judge = make_judge()
        custom = JudgeCollection.objects.create(name="Custom")
        JudgeCollectionOrderable.objects.create(collection=custom, judge=judge)
        JudgeRole.objects.create(role_name="Clerk", judge=judge)
