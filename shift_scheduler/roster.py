"""Built-in deterministic demo roster (mirrors the reference screenshot)."""
from __future__ import annotations

from shift_scheduler.model import Analyst, Region


def demo_roster() -> list[Analyst]:
    return [
        Analyst("Акрамжонов Азиз", Region.WEST, offset=0),
        Analyst("Роговский Дмитрий", Region.WEST, offset=2, day_off_requests={3}),
        Analyst("Арапова Евгения", Region.EAST, offset=2, vacation={13, 14}),
        Analyst("Карелин Вячеслав", Region.EAST, offset=1),
        Analyst("Мишкин Никита", Region.EAST, offset=0, day_off_requests={3}),
        Analyst("Новиков Иван", Region.EAST, offset=0, allows_night=True),
    ]
