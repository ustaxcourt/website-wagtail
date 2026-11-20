import copy
import importlib

migration = importlib.import_module(
    "home.migrations.0169_migrate_show_info_icon_to_bubble_content"
)


def _timeline(phases):
    return [{"type": "detailed_timeline", "value": {"phases": phases}}]


def _phase(**value):
    return {"type": "phase", "value": {"title": "t", **value}}


def test_checked_info_icon_becomes_info_and_unchecked_becomes_number():
    data = _timeline(
        [_phase(show_info_icon=False), _phase(show_info_icon=True), _phase()]
    )
    assert migration._convert_phases(data) is True
    values = [p["value"] for p in data[0]["value"]["phases"]]
    assert [v["bubble_content"] for v in values] == ["number", "info", "number"]
    assert all("show_info_icon" not in v for v in values)


def test_nested_timelines_are_converted():
    inner = _timeline([_phase(show_info_icon=True)])
    data = [{"type": "anchor", "value": {"body": inner}}]
    assert migration._convert_phases(data) is True
    assert inner[0]["value"]["phases"][0]["value"]["bubble_content"] == "info"


def test_already_migrated_data_is_unchanged_and_idempotent():
    data = _timeline([_phase(bubble_content="scale")])
    before = copy.deepcopy(data)
    assert migration._convert_phases(data) is False
    assert data == before


def test_existing_bubble_content_is_not_overwritten_but_old_key_removed():
    data = _timeline([_phase(bubble_content="user", show_info_icon=True)])
    assert migration._convert_phases(data) is True
    assert data[0]["value"]["phases"][0]["value"] == {
        "title": "t",
        "bubble_content": "user",
    }


def test_convert_stream_json_accepts_json_string_and_skips_unchanged():
    raw = '[{"type": "paragraph", "value": "x"}]'
    assert migration._convert_stream_json(raw) is None
