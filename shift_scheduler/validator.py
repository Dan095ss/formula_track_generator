"""Independent rule validator. Generator does not influence these checks."""
from __future__ import annotations

import dataclasses

from shift_scheduler.model import Analyst, MonthSchedule, Region, ShiftType


@dataclasses.dataclass
class Violation:
    severity: str   # "hard" | "soft"
    subject: str    # analyst name or "день N"
    message: str


def _max_consecutive_work(row: list[ShiftType]) -> int:
    best = cur = 0
    for s in row:
        cur = cur + 1 if s.is_working else 0
        best = max(best, cur)
    return best


def validate(schedule: MonthSchedule, roster: list[Analyst]) -> list[Violation]:
    out: list[Violation] = []
    even_team = len(roster) > 2 and len(roster) % 2 == 0

    for a in roster:
        row = schedule.grid[a.name]

        if _max_consecutive_work(row) > 2:
            out.append(Violation("hard", a.name, f"{a.name}: >2 рабочих смен подряд"))

        for d, s in enumerate(row):
            if s == ShiftType.NIGHT:
                if not a.allows_night:
                    out.append(Violation("hard", a.name,
                                         f"{a.name}: ночная без разрешения (день {d+1})"))
                if d == 0 or row[d - 1] not in (ShiftType.OFF, ShiftType.VACATION):
                    out.append(Violation("hard", a.name,
                                         f"{a.name}: нет выходного перед ночной (день {d+1})"))

        for day_num in a.vacation:
            if 1 <= day_num <= schedule.n_days and row[day_num - 1] != ShiftType.VACATION:
                out.append(Violation("hard", a.name,
                                     f"{a.name}: отпуск не соблюдён (день {day_num})"))

        for day_num in a.day_off_requests:
            if 1 <= day_num <= schedule.n_days and row[day_num - 1].is_working:
                out.append(Violation("hard", a.name,
                                     f"{a.name}: запрос выходного не соблюдён (день {day_num})"))

    if even_team:
        for region in (Region.WEST, Region.EAST):
            members = [a for a in roster if a.region == region]
            if len(members) < 2:
                continue
            for d in range(schedule.n_days):
                if schedule.region_working(d, region, roster) >= 2:
                    continue
                day_num = d + 1
                approved_absence = any(
                    day_num in a.vacation or day_num in a.day_off_requests
                    for a in members
                    if not schedule.grid[a.name][d].is_working
                )
                if approved_absence:
                    continue
                out.append(Violation("soft", f"день {day_num}",
                                     f"{region.label}: покрытие < 2 чел (день {day_num})"))

    counts = [schedule.shift_count(a.name) for a in roster]
    for a, c in zip(roster, counts):
        if not (12 <= c <= 18):
            out.append(Violation("soft", a.name,
                                 f"{a.name}: {c} смен (желательно 12..18)"))
    if counts:
        avg = sum(counts) / len(counts)
        if abs(avg - 15) > 2:
            out.append(Violation("soft", "команда",
                                 f"среднее по команде {avg:.1f} (цель ~15)"))

    return out
