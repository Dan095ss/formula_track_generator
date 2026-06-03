"""Schedule generation: base 2/2 cycle + layered passes."""
from __future__ import annotations

import calendar

from shift_scheduler.model import Analyst, MonthSchedule, Region, ShiftType


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
            if 1 <= day_num <= n_days and row[day_num - 1] != ShiftType.VACATION:
                row[day_num - 1] = ShiftType.OFF
        grid[a.name] = row
    _assign_nights(roster, grid, n_days)
    return MonthSchedule(year=year, month=month, n_days=n_days, grid=grid)


def _opposite(region: Region) -> Region:
    return Region.EAST if region is Region.WEST else Region.WEST


def _assign_nights(roster: list[Analyst], grid: dict[str, list[ShiftType]],
                   n_days: int) -> None:
    # WEST nights on cycle-pos 0, EAST on 1 — keeps regions in anti-phase so both dark windows are covered
    night_phase = {Region.WEST: 0, Region.EAST: 1}
    by_region: dict[Region, list[Analyst]] = {Region.WEST: [], Region.EAST: []}
    for a in roster:
        by_region[a.region].append(a)

    for d in range(n_days):
        for region in (Region.WEST, Region.EAST):
            opp = _opposite(region)
            opp_day_cover = sum(
                1 for a in by_region[opp] if grid[a.name][d] == ShiftType.DAY
            )
            if opp_day_cover > 0:
                continue  # opposite region's daytime already covers this window
            for a in by_region[region]:
                if not a.allows_night:
                    continue
                if grid[a.name][d] != ShiftType.DAY:
                    continue
                if d == 0 or grid[a.name][d - 1] not in (ShiftType.OFF, ShiftType.VACATION):
                    continue
                if (a.offset + d) % 4 != night_phase[region]:
                    continue
                grid[a.name][d] = ShiftType.NIGHT


def inherit_offsets(roster: list[Analyst], year: int, month: int) -> None:
    """Shift each analyst's phase into the next month and clear one-off overrides."""
    n_days = calendar.monthrange(year, month)[1]
    for a in roster:
        a.offset = (a.offset + n_days) % 4
        a.vacation = set()
        a.day_off_requests = set()
