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


def _would_exceed_consecutive(grid: dict[str, list[ShiftType]], name: str,
                               d: int, n_days: int) -> bool:
    """Return True if placing a NIGHT on day d would create >2 consecutive work days."""
    # Count working days immediately after d
    run_after = 0
    for dd in range(d + 1, min(d + 3, n_days)):
        if grid[name][dd].is_working:
            run_after += 1
        else:
            break
    # NIGHT on d + run_after must not exceed 2
    return 1 + run_after > 2


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

            # Pass 1: convert an existing DAY shift to NIGHT (preferred — no extra work day)
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
                break  # one night per day per region is enough

            # Pass 2: if still no coverage, promote a natural OFF day to NIGHT.
            # Only when the OFF is from the 2/2 cycle (not vacation or explicit Вх),
            # preceding day is non-working, and assigning won't create >2 consecutive.
            opp_day_cover_after = sum(
                1 for a in by_region[opp] if grid[a.name][d] == ShiftType.DAY
            )
            region_night_cover = sum(
                1 for a in by_region[region] if grid[a.name][d] == ShiftType.NIGHT
            )
            if opp_day_cover_after > 0 or region_night_cover > 0:
                continue

            for a in by_region[region]:
                if not a.allows_night:
                    continue
                if grid[a.name][d] != ShiftType.OFF:
                    continue
                # Hard constraints block the day
                day_num = d + 1
                if day_num in a.vacation or day_num in a.day_off_requests:
                    continue
                # Preceding day must be non-working (rest before night)
                if d == 0 or grid[a.name][d - 1] not in (ShiftType.OFF, ShiftType.VACATION):
                    continue
                # Safety: don't create >2 consecutive work days
                if _would_exceed_consecutive(grid, a.name, d, n_days):
                    continue
                grid[a.name][d] = ShiftType.NIGHT
                break


def inherit_offsets(roster: list[Analyst], year: int, month: int) -> None:
    """Shift each analyst's phase into the next month and clear one-off overrides."""
    n_days = calendar.monthrange(year, month)[1]
    for a in roster:
        a.offset = (a.offset + n_days) % 4
        a.vacation = set()
        a.day_off_requests = set()
