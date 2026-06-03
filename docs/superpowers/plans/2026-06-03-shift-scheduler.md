# Shift Scheduler (2/2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Terminal-only CLI that generates a 2-on/2-off shift schedule for a two-region analyst team, with correct month-to-month phase inheritance and an independent rule validator.

**Architecture:** Pure core (no I/O) split into model / generator / validator / render, plus a thin argparse CLI. A 4-day phase cycle expresses the base 2/2 pattern; month inheritance is a phase shift; vacations, day-off requests and coverage-driven night shifts are layered as ordered passes; the validator checks rules independently of the generator.

**Tech Stack:** Python 3.12, stdlib only (`dataclasses`, `enum`, `calendar`, `argparse`, `datetime`), pytest for tests.

---

## File Structure

```
shift_scheduler/
├── __init__.py        # package marker
├── model.py           # Region, ShiftType, Analyst, MonthSchedule
├── roster.py          # demo_roster() -> list[Analyst]
├── generator.py       # generate(), inherit_offsets()
├── validator.py       # Violation, validate()
├── render.py          # render_lines(), print_schedule()
├── cli.py             # main(): argparse + UTF-8 stdout
└── tests/
    ├── __init__.py
    ├── test_model.py
    ├── test_generator.py
    ├── test_inheritance.py
    ├── test_validator.py
    └── test_render.py
```

Run tests with: `python -m pytest shift_scheduler/tests/ -v`

---

### Task 1: Package skeleton + model enums

**Files:**
- Create: `shift_scheduler/__init__.py`
- Create: `shift_scheduler/tests/__init__.py`
- Create: `shift_scheduler/model.py`
- Test: `shift_scheduler/tests/test_model.py`

- [ ] **Step 1: Create empty package markers**

Create `shift_scheduler/__init__.py` with a single line:

```python
"""2-on/2-off shift schedule generator (terminal CLI)."""
```

Create `shift_scheduler/tests/__init__.py` as an empty file (0 bytes).

- [ ] **Step 2: Write the failing test**

Create `shift_scheduler/tests/test_model.py`:

```python
from shift_scheduler.model import Region, ShiftType


def test_region_has_two_members_with_labels():
    assert Region.WEST.label == "Запад"
    assert Region.EAST.label == "Восток"


def test_shifttype_glyphs():
    assert ShiftType.DAY.glyph == "Д"
    assert ShiftType.NIGHT.glyph == "Н"
    assert ShiftType.VACATION.glyph == "О"
    assert ShiftType.OFF.glyph == "·"


def test_shifttype_is_working():
    assert ShiftType.DAY.is_working
    assert ShiftType.NIGHT.is_working
    assert not ShiftType.OFF.is_working
    assert not ShiftType.VACATION.is_working
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python -m pytest shift_scheduler/tests/test_model.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'shift_scheduler.model'`

- [ ] **Step 4: Write minimal implementation**

Create `shift_scheduler/model.py`:

```python
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest shift_scheduler/tests/test_model.py -v`
Expected: PASS (3 passed)

- [ ] **Step 6: Commit**

```bash
git add shift_scheduler/__init__.py shift_scheduler/tests/__init__.py shift_scheduler/model.py shift_scheduler/tests/test_model.py
git commit -m "feat: shift_scheduler model enums (Region, ShiftType)"
```

---

### Task 2: Analyst + MonthSchedule dataclasses

**Files:**
- Modify: `shift_scheduler/model.py` (append `Analyst`, `MonthSchedule`)
- Test: `shift_scheduler/tests/test_model.py` (append)

- [ ] **Step 1: Write the failing test**

Append to `shift_scheduler/tests/test_model.py`:

```python
from shift_scheduler.model import Analyst, MonthSchedule


def _analyst(name="A", region=Region.WEST, **kw):
    return Analyst(name=name, region=region, **kw)


def test_analyst_defaults():
    a = _analyst()
    assert a.allows_night is False
    assert a.offset == 0
    assert a.vacation == set()
    assert a.day_off_requests == set()


def test_monthschedule_counts():
    w1 = _analyst("W1", Region.WEST)
    w2 = _analyst("W2", Region.WEST)
    grid = {
        "W1": [ShiftType.DAY, ShiftType.OFF, ShiftType.NIGHT],
        "W2": [ShiftType.OFF, ShiftType.DAY, ShiftType.VACATION],
    }
    sch = MonthSchedule(year=2026, month=6, n_days=3, grid=grid)
    assert sch.shift_count("W1") == 2          # DAY + NIGHT
    assert sch.shift_count("W2") == 1          # DAY only (VACATION excluded)
    assert sch.working_count(0) == 1           # W1 day0 DAY
    assert sch.region_working(2, Region.WEST, [w1, w2]) == 1  # only W1 NIGHT
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest shift_scheduler/tests/test_model.py -v`
Expected: FAIL with `ImportError: cannot import name 'Analyst'`

- [ ] **Step 3: Write minimal implementation**

Append to `shift_scheduler/model.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest shift_scheduler/tests/test_model.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add shift_scheduler/model.py shift_scheduler/tests/test_model.py
git commit -m "feat: Analyst and MonthSchedule with counting helpers"
```

---

### Task 3: Base 2/2 generation from phase offset

**Files:**
- Create: `shift_scheduler/generator.py`
- Test: `shift_scheduler/tests/test_generator.py`

- [ ] **Step 1: Write the failing test**

Create `shift_scheduler/tests/test_generator.py`:

```python
from shift_scheduler.model import Analyst, Region, ShiftType
from shift_scheduler.generator import generate

D, O, N, V = ShiftType.DAY, ShiftType.OFF, ShiftType.NIGHT, ShiftType.VACATION


def test_base_pattern_offset_0():
    a = Analyst("A", Region.WEST, offset=0)
    sch = generate([a], 2026, 6)          # June = 30 days
    # offset 0 -> D D O O D D O O ...
    assert sch.grid["A"][:6] == [D, D, O, O, D, D]
    assert sch.n_days == 30


def test_base_pattern_offset_2():
    a = Analyst("A", Region.WEST, offset=2)
    sch = generate([a], 2026, 6)
    # offset 2 -> O O D D O O ...
    assert sch.grid["A"][:6] == [O, O, D, D, O, O]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest shift_scheduler/tests/test_generator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'shift_scheduler.generator'`

- [ ] **Step 3: Write minimal implementation**

Create `shift_scheduler/generator.py`:

```python
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
        grid[a.name] = [_base_cell(a.offset, d) for d in range(n_days)]
    return MonthSchedule(year=year, month=month, n_days=n_days, grid=grid)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest shift_scheduler/tests/test_generator.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add shift_scheduler/generator.py shift_scheduler/tests/test_generator.py
git commit -m "feat: base 2/2 schedule generation from phase offset"
```

---

### Task 4: Vacation + day-off-request passes

**Files:**
- Modify: `shift_scheduler/generator.py` (add passes inside `generate`)
- Test: `shift_scheduler/tests/test_generator.py` (append)

- [ ] **Step 1: Write the failing test**

Append to `shift_scheduler/tests/test_generator.py`:

```python
def test_vacation_overrides_work_day():
    a = Analyst("A", Region.WEST, offset=0, vacation={1})  # day 1 is a work day
    sch = generate([a], 2026, 6)
    assert sch.grid["A"][0] == V


def test_day_off_request_forces_off():
    a = Analyst("A", Region.WEST, offset=0, day_off_requests={2})  # day 2 work day
    sch = generate([a], 2026, 6)
    assert sch.grid["A"][1] == O


def test_request_on_off_day_is_noop():
    a = Analyst("A", Region.WEST, offset=0, day_off_requests={3})  # day 3 is OFF
    sch = generate([a], 2026, 6)
    assert sch.grid["A"][2] == O
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest shift_scheduler/tests/test_generator.py -v`
Expected: FAIL — `test_vacation_overrides_work_day` asserts `V` but gets `D`.

- [ ] **Step 3: Write minimal implementation**

In `shift_scheduler/generator.py`, replace the body of the `for a in roster` loop in `generate` with:

```python
    for a in roster:
        row = [_base_cell(a.offset, d) for d in range(n_days)]
        for day_num in a.vacation:
            if 1 <= day_num <= n_days:
                row[day_num - 1] = ShiftType.VACATION
        for day_num in a.day_off_requests:
            if 1 <= day_num <= n_days:
                row[day_num - 1] = ShiftType.OFF
        grid[a.name] = row
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest shift_scheduler/tests/test_generator.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add shift_scheduler/generator.py shift_scheduler/tests/test_generator.py
git commit -m "feat: vacation and day-off-request passes"
```

---

### Task 5: Coverage-driven night-shift pass

**Files:**
- Modify: `shift_scheduler/generator.py` (add `_assign_nights`, call from `generate`)
- Test: `shift_scheduler/tests/test_generator.py` (append)

Night rule: only `allows_night` analysts; a DAY becomes NIGHT only if the previous day is
non-working (OFF/VACATION) — satisfies "day off before a night". A region's night demand
exists when the *other* region has zero day coverage on that day; nights are placed in
region anti-phase (WEST candidates on `(offset+d)%4==0`, EAST on `(offset+d)%4==1`).

- [ ] **Step 1: Write the failing test**

Append to `shift_scheduler/tests/test_generator.py`:

```python
def test_night_only_for_night_permitted():
    # Lone WEST analyst, no opposite-region coverage -> demand exists every day,
    # but no allows_night => no NIGHT cells.
    a = Analyst("A", Region.WEST, offset=0, allows_night=False)
    sch = generate([a], 2026, 6)
    assert N not in sch.grid["A"]


def test_night_requires_preceding_off():
    a = Analyst("A", Region.WEST, offset=0, allows_night=True)
    sch = generate([a], 2026, 6)
    for d, cell in enumerate(sch.grid["A"]):
        if cell == N:
            assert d > 0
            assert sch.grid["A"][d - 1] in (O, V)


def test_day_one_is_never_night():
    # day index 0 has no preceding day -> cannot be NIGHT
    a = Analyst("A", Region.WEST, offset=0, allows_night=True)
    sch = generate([a], 2026, 6)
    assert sch.grid["A"][0] != N
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest shift_scheduler/tests/test_generator.py -v`
Expected: FAIL — `test_night_requires_preceding_off` finds no `N` at all yet (the assertion
loop passes vacuously) OR passes; the meaningful failure is that `_assign_nights` does not
exist once we call it. To make RED explicit, the implementation step adds the call; if the
function is missing the test errors with `NameError`. Verify at least that the suite errors
on the missing `_assign_nights` import path after Step 3 wiring; if all three pass before
implementation, that is acceptable (they encode invariants the next step must preserve).

- [ ] **Step 3: Write minimal implementation**

In `shift_scheduler/generator.py` add imports and the night pass. Add `Region` to the
import line:

```python
from shift_scheduler.model import Analyst, MonthSchedule, Region, ShiftType
```

Append function:

```python
def _opposite(region: Region) -> Region:
    return Region.EAST if region is Region.WEST else Region.WEST


def _assign_nights(roster: list[Analyst], grid: dict[str, list[ShiftType]],
                   n_days: int) -> None:
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
```

Then call it at the end of `generate`, before constructing `MonthSchedule`:

```python
    _assign_nights(roster, grid, n_days)
    return MonthSchedule(year=year, month=month, n_days=n_days, grid=grid)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest shift_scheduler/tests/test_generator.py -v`
Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add shift_scheduler/generator.py shift_scheduler/tests/test_generator.py
git commit -m "feat: coverage-driven night-shift assignment pass"
```

---

### Task 6: Month-to-month phase inheritance

**Files:**
- Modify: `shift_scheduler/generator.py` (add `inherit_offsets`)
- Test: `shift_scheduler/tests/test_inheritance.py`

- [ ] **Step 1: Write the failing test**

Create `shift_scheduler/tests/test_inheritance.py`:

```python
import calendar

from shift_scheduler.model import Analyst, Region, ShiftType
from shift_scheduler.generator import generate, inherit_offsets

D, O = ShiftType.DAY, ShiftType.OFF


def _last_two(sch, name):
    return sch.grid[name][-2:]


def _first_two(sch, name):
    return sch.grid[name][:2]


def test_rule_off_off_to_work_work():
    # Pick offset so June (30 days) ends on OFF, OFF.
    # offset 0: day28(idx27)->(0+27)%4=3 OFF, day29 idx28 ->0 DAY... find offset giving OFF,OFF at end.
    # n_days=30; last two indices 28,29. Want both OFF: (off+28)%4 in {2,3} and (off+29)%4 in {2,3}.
    # off=2: (30)%4=2 ->OFF? (2+28)=30%4=2 OFF, (2+29)=31%4=3 OFF. Good.
    a = Analyst("A", Region.WEST, offset=2)
    june = generate([a], 2026, 6)
    assert _last_two(june, "A") == [O, O]
    inherit_offsets([a], 2026, 6)
    july = generate([a], 2026, 7)
    assert _first_two(july, "A") == [D, D]


def test_rule_work_work_to_off_off():
    # offset 0: last two indices 28,29 -> (0+28)%4=0 DAY, (0+29)%4=1 DAY.
    a = Analyst("A", Region.WEST, offset=0)
    june = generate([a], 2026, 6)
    assert _last_two(june, "A") == [D, D]
    inherit_offsets([a], 2026, 6)
    july = generate([a], 2026, 7)
    assert _first_two(july, "A") == [O, O]


def test_rule_off_then_work_to_work_first_day():
    # Want June end = OFF (idx28), DAY (idx29): (off+28)%4 in {2,3} and (off+29)%4 in {0,1}.
    # off=1: (1+28)=29%4=1 DAY no. off=3:(3+28)=31%4=3 OFF,(3+29)=32%4=0 DAY. Good.
    a = Analyst("A", Region.WEST, offset=3)
    june = generate([a], 2026, 6)
    assert june.grid["A"][28] == O and june.grid["A"][29] == D
    inherit_offsets([a], 2026, 6)
    july = generate([a], 2026, 7)
    assert july.grid["A"][0] == D


def test_inherit_clears_one_off_overrides():
    a = Analyst("A", Region.WEST, offset=0, vacation={5}, day_off_requests={6})
    inherit_offsets([a], 2026, 6)
    assert a.vacation == set()
    assert a.day_off_requests == set()
    assert a.offset == (0 + 30) % 4  # 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest shift_scheduler/tests/test_inheritance.py -v`
Expected: FAIL with `ImportError: cannot import name 'inherit_offsets'`

- [ ] **Step 3: Write minimal implementation**

Append to `shift_scheduler/generator.py`:

```python
def inherit_offsets(roster: list[Analyst], year: int, month: int) -> None:
    """Shift each analyst's phase into the next month and clear one-off overrides."""
    n_days = calendar.monthrange(year, month)[1]
    for a in roster:
        a.offset = (a.offset + n_days) % 4
        a.vacation = set()
        a.day_off_requests = set()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest shift_scheduler/tests/test_inheritance.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add shift_scheduler/generator.py shift_scheduler/tests/test_inheritance.py
git commit -m "feat: month-to-month phase inheritance"
```

---

### Task 7: Validator — hard rules

**Files:**
- Create: `shift_scheduler/validator.py`
- Test: `shift_scheduler/tests/test_validator.py`

- [ ] **Step 1: Write the failing test**

Create `shift_scheduler/tests/test_validator.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest shift_scheduler/tests/test_validator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'shift_scheduler.validator'`

- [ ] **Step 3: Write minimal implementation**

Create `shift_scheduler/validator.py`:

```python
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
    by_name = {a.name: a for a in roster}
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
                if schedule.region_working(d, region, roster) < 2:
                    out.append(Violation("hard", f"день {d+1}",
                                         f"{region.label}: покрытие < 2 чел (день {d+1})"))

    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest shift_scheduler/tests/test_validator.py -v`
Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add shift_scheduler/validator.py shift_scheduler/tests/test_validator.py
git commit -m "feat: validator hard rules"
```

---

### Task 8: Validator — soft rules (shift count, average)

**Files:**
- Modify: `shift_scheduler/validator.py` (append soft checks to `validate`)
- Test: `shift_scheduler/tests/test_validator.py` (append)

- [ ] **Step 1: Write the failing test**

Append to `shift_scheduler/tests/test_validator.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest shift_scheduler/tests/test_validator.py -v`
Expected: FAIL — no soft violations produced yet.

- [ ] **Step 3: Write minimal implementation**

In `shift_scheduler/validator.py`, before `return out`, add:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest shift_scheduler/tests/test_validator.py -v`
Expected: PASS (9 passed)

- [ ] **Step 5: Commit**

```bash
git add shift_scheduler/validator.py shift_scheduler/tests/test_validator.py
git commit -m "feat: validator soft rules (shift count, average)"
```

---

### Task 9: Demo roster

**Files:**
- Create: `shift_scheduler/roster.py`
- Test: `shift_scheduler/tests/test_generator.py` (append a roster sanity test)

- [ ] **Step 1: Write the failing test**

Append to `shift_scheduler/tests/test_generator.py`:

```python
from shift_scheduler.roster import demo_roster


def test_demo_roster_is_even_and_has_both_regions():
    r = demo_roster()
    assert len(r) % 2 == 0 and len(r) > 2
    regions = {a.region for a in r}
    assert Region.WEST in regions and Region.EAST in regions
    assert any(a.allows_night for a in r)
    assert any(a.vacation for a in r)
    assert any(a.day_off_requests for a in r)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest shift_scheduler/tests/test_generator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'shift_scheduler.roster'`

- [ ] **Step 3: Write minimal implementation**

Create `shift_scheduler/roster.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest shift_scheduler/tests/test_generator.py -v`
Expected: PASS (9 passed in this file)

- [ ] **Step 5: Commit**

```bash
git add shift_scheduler/roster.py shift_scheduler/tests/test_generator.py
git commit -m "feat: built-in demo roster"
```

---

### Task 10: Terminal renderer

**Files:**
- Create: `shift_scheduler/render.py`
- Test: `shift_scheduler/tests/test_render.py`

- [ ] **Step 1: Write the failing test**

Create `shift_scheduler/tests/test_render.py`:

```python
from shift_scheduler.model import Analyst, Region
from shift_scheduler.generator import generate
from shift_scheduler.validator import validate
from shift_scheduler.render import render_lines


def test_render_lines_contains_header_and_glyphs():
    roster = [Analyst("Иванов Иван", Region.WEST, offset=0)]
    sch = generate(roster, 2026, 6)
    violations = validate(sch, roster)
    lines = render_lines(roster, sch, violations, use_color=False)
    text = "\n".join(lines)
    assert "Июнь" in text or "июнь" in text.lower()
    assert "Иванов Иван" in text
    assert "Запад" in text
    assert "Д" in text  # at least one day shift glyph


def test_render_lines_is_color_free_when_disabled():
    roster = [Analyst("A", Region.WEST, offset=0)]
    sch = generate(roster, 2026, 6)
    lines = render_lines(roster, sch, [], use_color=False)
    assert all("\033[" not in ln for ln in lines)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest shift_scheduler/tests/test_render.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'shift_scheduler.render'`

- [ ] **Step 3: Write minimal implementation**

Create `shift_scheduler/render.py`:

```python
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
    return lines


def print_schedule(roster: list[Analyst], schedule: MonthSchedule,
                   violations: list[Violation], use_color: bool) -> None:
    for ln in render_lines(roster, schedule, violations, use_color):
        print(ln)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest shift_scheduler/tests/test_render.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add shift_scheduler/render.py shift_scheduler/tests/test_render.py
git commit -m "feat: terminal renderer (calendar table + report)"
```

---

### Task 11: CLI entry point

**Files:**
- Create: `shift_scheduler/cli.py`
- Test: manual smoke run (no unit test — thin I/O wrapper)

- [ ] **Step 1: Write minimal implementation**

Create `shift_scheduler/cli.py`:

```python
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
    p.add_argument("--month", type=int, default=today.month)
    p.add_argument("--months", type=int, default=1,
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
```

- [ ] **Step 2: Smoke-run the CLI**

Run: `python -m shift_scheduler.cli --year 2026 --month 6 --no-color`
Expected: prints the June calendar table for both regions followed by a `── Проверки ──`
section, no traceback, exit code 0.

- [ ] **Step 3: Smoke-run inheritance demo**

Run: `python -m shift_scheduler.cli --year 2026 --month 6 --months 2 --no-color`
Expected: two month tables (June, July); July's first two days continue the cycle from
June's last two days per the inheritance rules.

- [ ] **Step 4: Commit**

```bash
git add shift_scheduler/cli.py
git commit -m "feat: CLI entry point with UTF-8 stdout and inheritance demo"
```

---

### Task 12: Full suite + verification

**Files:** none (verification only)

- [ ] **Step 1: Run the entire test suite**

Run: `python -m pytest shift_scheduler/tests/ -v`
Expected: all tests PASS (no failures, no errors).

- [ ] **Step 2: Verify no hard violations on the demo roster**

Run: `python -m shift_scheduler.cli --year 2026 --month 6 --no-color`
Expected: the `── Проверки ──` section shows "Жёстких нарушений нет." (soft notes about
shift count near vacation days are acceptable).

- [ ] **Step 3: Commit any final cleanup**

```bash
git add -A shift_scheduler/
git commit -m "test: full shift_scheduler suite green" --allow-empty
```

---

## Self-Review Notes

- **Spec coverage:** base 2/2 (Task 3), vacation/request (Task 4), nights-by-coverage with
  off-before-night (Task 5), inheritance 3 rules (Task 6), validator hard incl. coverage/
  vacation/request (Task 7) + soft (Task 8), demo roster with even team (Task 9), terminal
  render + UTF-8 CLI (Tasks 10–11). All spec sections mapped.
- **Type consistency:** `generate`, `inherit_offsets`, `validate`, `Violation(severity,
  subject, message)`, `render_lines(roster, schedule, violations, use_color)`,
  `MonthSchedule.region_working(day_index, region, roster)` used identically across tasks.
- **Known soft-rule note:** vacation days (`Арапова`, 2 days) slightly lower one analyst's
  count; this surfaces as a soft `[~]` note, which is by design per the spec.
