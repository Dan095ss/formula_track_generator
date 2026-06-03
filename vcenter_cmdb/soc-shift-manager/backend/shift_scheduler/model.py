"""Domain model: regions, shift types, analysts, month schedule."""
from __future__ import annotations

import dataclasses
from enum import Enum


class Region(Enum):
    WEST = ("Запад", "Europe / Americas")
    EAST = ("Восток", "Asia / Pacific")

    def __init__(self, label: str, timezone_note: str) -> None:
        self.label = label
        self.timezone_note = timezone_note


class ShiftType(Enum):
    DAY = ("Д", True)
    NIGHT = ("Н", True)
    OFF = ("·", False)
    VACATION = ("О", False)

    def __init__(self, glyph: str, is_working: bool) -> None:
        self.glyph = glyph
        self.is_working = is_working


@dataclasses.dataclass
class Analyst:
    name: str
    region: Region
    allows_night: bool = False
    offset: int = 0
    vacation: set[int] = dataclasses.field(default_factory=set)
    day_off_requests: set[int] = dataclasses.field(default_factory=set)


@dataclasses.dataclass
class MonthSchedule:
    year: int
    month: int
    n_days: int
    grid: dict[str, list[ShiftType]]

    def shift_count(self, name: str) -> int:
        return sum(1 for s in self.grid[name] if s.is_working)

    def working_count(self, day_index: int) -> int:
        return sum(1 for row in self.grid.values() if row[day_index].is_working)

    def region_working(self, day_index: int, region: Region,
                       roster: list[Analyst]) -> int:
        names = {a.name for a in roster if a.region == region}
        return sum(1 for n in names if self.grid[n][day_index].is_working)
