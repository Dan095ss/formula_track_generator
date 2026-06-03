import calendar

from shift_scheduler.model import Analyst, Region, ShiftType
from shift_scheduler.generator import generate, inherit_offsets

D, O = ShiftType.DAY, ShiftType.OFF


def _last_two(sch, name):
    return sch.grid[name][-2:]


def _first_two(sch, name):
    return sch.grid[name][:2]


def test_rule_off_off_to_work_work():
    # Pick offset so June (30 days) ends on OFF, OFF.
    # offset 0: day28(idx27)->(0+27)%4=3 OFF, day29 idx28 ->0 DAY... find offset giving OFF,OFF at end.
    # n_days=30; last two indices 28,29. Want both OFF: (off+28)%4 in {2,3} and (off+29)%4 in {2,3}.
    # off=2: (30)%4=2 ->OFF? (2+28)=30%4=2 OFF, (2+29)=31%4=3 OFF. Good.
    a = Analyst("A", Region.WEST, offset=2)
    june = generate([a], 2026, 6)
    assert _last_two(june, "A") == [O, O]
    inherit_offsets([a], 2026, 6)
    july = generate([a], 2026, 7)
    assert _first_two(july, "A") == [D, D]


def test_rule_work_work_to_off_off():
    # offset 0: last two indices 28,29 -> (0+28)%4=0 DAY, (0+29)%4=1 DAY.
    a = Analyst("A", Region.WEST, offset=0)
    june = generate([a], 2026, 6)
    assert _last_two(june, "A") == [D, D]
    inherit_offsets([a], 2026, 6)
    july = generate([a], 2026, 7)
    assert _first_two(july, "A") == [O, O]


def test_rule_off_then_work_to_work_first_day():
    # Want June end = OFF (idx28), DAY (idx29): (off+28)%4 in {2,3} and (off+29)%4 in {0,1}.
    # off=1: (1+28)=29%4=1 DAY no. off=3:(3+28)=31%4=3 OFF,(3+29)=32%4=0 DAY. Good.
    a = Analyst("A", Region.WEST, offset=3)
    june = generate([a], 2026, 6)
    assert june.grid["A"][28] == O and june.grid["A"][29] == D
    inherit_offsets([a], 2026, 6)
    july = generate([a], 2026, 7)
    assert july.grid["A"][0] == D


def test_inherit_clears_one_off_overrides():
    a = Analyst("A", Region.WEST, offset=0, vacation={5}, day_off_requests={6})
    inherit_offsets([a], 2026, 6)
    assert a.vacation == set()
    assert a.day_off_requests == set()
    assert a.offset == (0 + 30) % 4  # 2
