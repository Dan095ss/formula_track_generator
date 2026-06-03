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


from shift_scheduler.model import Analyst, MonthSchedule


def _analyst(name="A", region=Region.WEST, **kw):
    return Analyst(name=name, region=region, **kw)


def test_analyst_defaults():
    a = _analyst()
    assert a.allows_night is False
    assert a.offset == 0
    assert a.vacation == set()
    assert a.day_off_requests == set()


def test_monthschedule_counts():
    w1 = _analyst("W1", Region.WEST)
    w2 = _analyst("W2", Region.WEST)
    grid = {
        "W1": [ShiftType.DAY, ShiftType.OFF, ShiftType.NIGHT],
        "W2": [ShiftType.OFF, ShiftType.DAY, ShiftType.VACATION],
    }
    sch = MonthSchedule(year=2026, month=6, n_days=3, grid=grid)
    assert sch.shift_count("W1") == 2          # DAY + NIGHT
    assert sch.shift_count("W2") == 1          # DAY only (VACATION excluded)
    assert sch.working_count(0) == 1           # W1 day0 DAY
    assert sch.region_working(2, Region.WEST, [w1, w2]) == 1  # only W1 NIGHT
