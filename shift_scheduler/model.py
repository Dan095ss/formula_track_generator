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
