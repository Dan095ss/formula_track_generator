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


def test_vacation_overrides_work_day():
    a = Analyst("A", Region.WEST, offset=0, vacation={1})  # day 1 is a work day
    sch = generate([a], 2026, 6)
    assert sch.grid["A"][0] == V


def test_day_off_request_forces_off():
    a = Analyst("A", Region.WEST, offset=0, day_off_requests={2})  # day 2 work day
    sch = generate([a], 2026, 6)
    assert sch.grid["A"][1] == O


def test_request_on_off_day_is_noop():
    a = Analyst("A", Region.WEST, offset=0, day_off_requests={3})  # day 3 is OFF
    sch = generate([a], 2026, 6)
    assert sch.grid["A"][2] == O
