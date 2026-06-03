"""CLI entry point: python -m shift_scheduler.cli [options]."""
from __future__ import annotations

import argparse
import sys
from datetime import date

from shift_scheduler.generator import generate, inherit_offsets
from shift_scheduler.render import print_schedule
from shift_scheduler.roster import demo_roster
from shift_scheduler.validator import validate


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1251 guard
    except (AttributeError, ValueError):
        pass

    today = date.today()
    p = argparse.ArgumentParser(description="Генератор графика смен 2/2 (демо).")
    p.add_argument("--year", type=int, default=today.year)
    p.add_argument("--month", type=int, default=today.month,
                   choices=range(1, 13), metavar="1-12")
    p.add_argument("--months", type=int, default=1,
                   choices=range(1, 25), metavar="1-24",
                   help="сколько месяцев показать подряд (демонстрация наследования)")
    p.add_argument("--no-color", action="store_true")
    args = p.parse_args(argv)

    roster = demo_roster()
    year, month = args.year, args.month
    for i in range(args.months):
        sch = generate(roster, year, month)
        violations = validate(sch, roster)
        if i:
            print()
        print_schedule(roster, sch, violations, use_color=not args.no_color)
        inherit_offsets(roster, year, month)
        month += 1
        if month > 12:
            month, year = 1, year + 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
