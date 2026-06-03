from shift_scheduler.model import Analyst, Region, ShiftType, MonthSchedule
from shift_scheduler.validator import validate, Violation

D, O, N, V = ShiftType.DAY, ShiftType.OFF, ShiftType.NIGHT, ShiftType.VACATION


def _sched(grid, n_days):
    return MonthSchedule(year=2026, month=6, n_days=n_days, grid=grid)


def _hard_msgs(violations):
    return [v.message for v in violations if v.severity == "hard"]


def test_more_than_two_work_in_a_row_flagged():
    a = Analyst("A", Region.WEST)
    sch = _sched({"A": [D, D, D, O]}, 4)
    v = validate(sch, [a])
    assert any("подряд" in m for m in _hard_msgs(v))


def test_night_without_preceding_off_flagged():
    a = Analyst("A", Region.WEST, allows_night=True)
    sch = _sched({"A": [D, N, O, O]}, 4)  # N at idx1 preceded by DAY
    v = validate(sch, [a])
    assert any("перед" in m and "ночн" in m.lower() for m in _hard_msgs(v))


def test_night_without_permission_flagged():
    a = Analyst("A", Region.WEST, allows_night=False)
    sch = _sched({"A": [O, N, O, O]}, 4)
    v = validate(sch, [a])
    assert any("разреш" in m for m in _hard_msgs(v))


def test_unhonored_vacation_flagged():
    a = Analyst("A", Region.WEST, vacation={1})
    sch = _sched({"A": [D, O, O, O]}, 4)  # day1 should be VACATION but is DAY
    v = validate(sch, [a])
    assert any("отпуск" in m.lower() for m in _hard_msgs(v))


def test_unhonored_request_flagged():
    a = Analyst("A", Region.WEST, day_off_requests={1})
    sch = _sched({"A": [D, O, O, O]}, 4)  # day1 should be OFF but is DAY
    v = validate(sch, [a])
    assert any("запрос" in m.lower() for m in _hard_msgs(v))


def test_even_team_coverage_below_two_flagged():
    # 4 EAST analysts (even >2). On day0 only 1 works.
    roster = [Analyst(f"E{i}", Region.EAST) for i in range(4)]
    grid = {
        "E0": [D, O], "E1": [O, D], "E2": [O, D], "E3": [O, O],
    }
    sch = _sched(grid, 2)
    v = validate(sch, roster)
    assert any("покрыт" in m.lower() for m in _hard_msgs(v))


def test_clean_schedule_has_no_hard_violations():
    a = Analyst("A", Region.WEST)
    sch = _sched({"A": [D, D, O, O, D, D, O, O]}, 8)
    assert _hard_msgs(validate(sch, [a])) == []


def _soft_msgs(violations):
    return [v.message for v in violations if v.severity == "soft"]


def test_shift_count_out_of_range_flagged():
    # 2 work days in a 30-day month -> well below 12.
    a = Analyst("A", Region.WEST)
    row = [D, D] + [O] * 28
    sch = _sched({"A": row}, 30)
    v = validate(sch, [a])
    assert any("смен" in m for m in _soft_msgs(v))


def test_average_far_from_15_flagged():
    a = Analyst("A", Region.WEST)
    b = Analyst("B", Region.WEST)
    row = [D, D] + [O] * 28
    sch = _sched({"A": row, "B": row}, 30)
    v = validate(sch, [a, b])
    assert any("среднее" in m.lower() for m in _soft_msgs(v))
