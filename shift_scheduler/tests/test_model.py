from shift_scheduler.model import Region, ShiftType


def test_region_has_two_members_with_labels():
    assert Region.WEST.label == "Запад"
    assert Region.EAST.label == "Восток"


def test_shifttype_glyphs():
    assert ShiftType.DAY.glyph == "Д"
    assert ShiftType.NIGHT.glyph == "Н"
    assert ShiftType.VACATION.glyph == "О"
    assert ShiftType.OFF.glyph == "·"


def test_shifttype_is_working():
    assert ShiftType.DAY.is_working
    assert ShiftType.NIGHT.is_working
    assert not ShiftType.OFF.is_working
    assert not ShiftType.VACATION.is_working
