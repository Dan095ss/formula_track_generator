from shift_scheduler.model import Analyst, Region, ShiftType
from shift_scheduler.generator import generate

D, O, N, V = ShiftType.DAY, ShiftType.OFF, ShiftType.NIGHT, ShiftType.VACATION


def test_base_pattern_offset_0():
    a = Analyst("A", Region.WEST, offset=0)
    sch = generate([a], 2026, 6)          # June = 30 days
    # offset 0 -> D D O O D D O O ...
    assert sch.grid["A"][:6] == [D, D, O, O, D, D]
    assert sch.n_days == 30


def test_base_pattern_offset_2():
    a = Analyst("A", Region.WEST, offset=2)
    sch = generate([a], 2026, 6)
    # offset 2 -> O O D D O O ...
    assert sch.grid["A"][:6] == [O, O, D, D, O, O]
