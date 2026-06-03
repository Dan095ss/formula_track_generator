"""Terminal rendering: calendar table + validator report. Pure line builder."""
from __future__ import annotations

import calendar
from datetime import date

from shift_scheduler.model import Analyst, MonthSchedule, Region, ShiftType
from shift_scheduler.validator import Violation

_MONTHS_RU = [
    "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
]
_WEEKDAYS_RU = "ПВСЧПСВ"

_COLORS = {
    ShiftType.DAY: "\033[44;97m",
    ShiftType.NIGHT: "\033[45;97m",
    ShiftType.VACATION: "\033[46;30m",
    ShiftType.OFF: "\033[90m",
}
_RESET = "\033[0m"
_NAME_W = 24


def _cell(s: ShiftType, use_color: bool) -> str:
    text = f"{s.glyph:^3}"
    if use_color:
        return f"{_COLORS[s]}{text}{_RESET}"
    return text


def render_lines(roster: list[Analyst], schedule: MonthSchedule,
                 violations: list[Violation], use_color: bool) -> list[str]:
    n = schedule.n_days
    lines: list[str] = []
    lines.append(f"Календарь смен — {_MONTHS_RU[schedule.month]} {schedule.year}")

    nums = " " * (_NAME_W + 1)
    wds = " " * (_NAME_W + 1)
    for d in range(n):
        day_num = d + 1
        wd = date(schedule.year, schedule.month, day_num).weekday()
        nums += f"{day_num:^3}"
        wds += f"{_WEEKDAYS_RU[wd]:^3}"
    lines.append(nums)
    lines.append(wds)

    for region in (Region.WEST, Region.EAST):
        members = [a for a in roster if a.region == region]
        if not members:
            continue
        lines.append("")
        lines.append(region.label)
        for a in members:
            name = a.name[:_NAME_W].ljust(_NAME_W)
            cells = "".join(_cell(schedule.grid[a.name][d], use_color) for d in range(n))
            lines.append(f"{name} {cells}")

    lines.append("")
    lines.append("── Проверки ──")
    hard = [v for v in violations if v.severity == "hard"]
    soft = [v for v in violations if v.severity == "soft"]
    if not hard:
        lines.append("Жёстких нарушений нет.")
    for v in hard:
        lines.append(f"  [!] {v.message}")
    for v in soft:
        lines.append(f"  [~] {v.message}")

    lines.append("")
    lines.append("── Смены в месяце ──")
    for a in roster:
        count = schedule.shift_count(a.name)
        flag = "" if 12 <= count <= 18 else "  <- вне диапазона"
        lines.append(f"  {a.name[:26]:28} {count:2} смен{flag}")
    return lines


def print_schedule(roster: list[Analyst], schedule: MonthSchedule,
                   violations: list[Violation], use_color: bool) -> None:
    for ln in render_lines(roster, schedule, violations, use_color):
        print(ln)
