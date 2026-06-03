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


def test_night_only_for_night_permitted():
    # Lone WEST analyst, no opposite-region coverage -> demand exists every day,
    # but no allows_night => no NIGHT cells.
    a = Analyst("A", Region.WEST, offset=0, allows_night=False)
    sch = generate([a], 2026, 6)
    assert N not in sch.grid["A"]


def test_night_requires_preceding_off():
    a = Analyst("A", Region.WEST, offset=0, allows_night=True)
    sch = generate([a], 2026, 6)
    for d, cell in enumerate(sch.grid["A"]):
        if cell == N:
            assert d > 0
            assert sch.grid["A"][d - 1] in (O, V)


def test_day_one_is_never_night():
    # day index 0 has no preceding day -> cannot be NIGHT
    a = Analyst("A", Region.WEST, offset=0, allows_night=True)
    sch = generate([a], 2026, 6)
    assert sch.grid["A"][0] != N
