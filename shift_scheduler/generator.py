"""Schedule generation: base 2/2 cycle + layered passes."""
from __future__ import annotations

import calendar

from shift_scheduler.model import Analyst, MonthSchedule, ShiftType


def _base_cell(offset: int, day_index: int) -> ShiftType:
    return ShiftType.DAY if (offset + day_index) % 4 in (0, 1) else ShiftType.OFF


def generate(roster: list[Analyst], year: int, month: int) -> MonthSchedule:
    n_days = calendar.monthrange(year, month)[1]
    grid: dict[str, list[ShiftType]] = {}
    for a in roster:
        row = [_base_cell(a.offset, d) for d in range(n_days)]
        for day_num in a.vacation:
            if 1 <= day_num <= n_days:
                row[day_num - 1] = ShiftType.VACATION
        for day_num in a.day_off_requests:
            if 1 <= day_num <= n_days:
                row[day_num - 1] = ShiftType.OFF
        grid[a.name] = row
    return MonthSchedule(year=year, month=month, n_days=n_days, grid=grid)
