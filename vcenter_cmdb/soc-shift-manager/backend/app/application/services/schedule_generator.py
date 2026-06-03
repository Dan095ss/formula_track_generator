"""Schedule generation via shift_scheduler 2/2 engine.

Replaces rotation_22 + schedule_constraints with the pure shift_scheduler package.
Public interface (ScheduleGenerator, TeamGenerateResult, MONTH_NAMES_RU, month_bounds)
is unchanged.
"""
from __future__ import annotations

import calendar
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shift_scheduler.generator import generate
from shift_scheduler.model import Analyst as SchedAnalyst, MonthSchedule, Region, ShiftType as SchedShiftType

from app.application.services.shift_times import shift_times_for_date
from app.domain.enums import PreferenceType, RequestStatus, ShiftType
from app.infrastructure.database.models import (
    Absence,
    Analyst,
    Schedule,
    Shift,
    ShiftAssignment,
    ShiftPreference,
    Team,
    User,
)

MONTH_NAMES_RU = (
    "",
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
)

_DB_SHIFT_TYPE = {
    SchedShiftType.DAY: ShiftType.DAY,
    SchedShiftType.NIGHT: ShiftType.NIGHT,
}


@dataclass
class TeamGenerateResult:
    team_id: uuid.UUID
    team_name: str
    schedule_id: uuid.UUID | None
    schedule_name: str | None
    shifts_created: int
    assignments_created: int
    status: str
    message: str


def next_calendar_month(reference: datetime | None = None) -> tuple[datetime, datetime, int, int]:
    now = reference or datetime.now(UTC)
    if now.month == 12:
        year, month = now.year + 1, 1
    else:
        year, month = now.year, now.month + 1
    period_start, period_end = month_bounds(year, month)
    return period_start, period_end, year, month


def month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    last_day = calendar.monthrange(year, month)[1]
    period_start = datetime(year, month, 1, tzinfo=UTC)
    period_end = datetime(year, month, last_day, 23, 59, 59, tzinfo=UTC)
    return period_start, period_end


def previous_month(year: int, month: int) -> tuple[int, int]:
    if month == 1:
        return year - 1, 12
    return year, month - 1


def _team_is_east(team: Team) -> bool:
    name = team.name.lower()
    return "east" in name or "восток" in name


def _team_sort_key(team: Team) -> tuple[int, str]:
    return (0 if _team_is_east(team) else 1, team.name)


def _phase_from_tail(tail: tuple[bool, bool, bool, bool]) -> int:
    """Derive 2/2 phase offset from last two working days of previous month."""
    penultimate, last = tail[-2], tail[-1]
    if penultimate and last:
        return 2
    if not penultimate and last:
        return 1
    if penultimate and not last:
        return 3
    return 0


class ScheduleGenerator:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _analyst_worked_on_date(self, analyst_id: uuid.UUID, work_date: date) -> bool:
        day_start = datetime(work_date.year, work_date.month, work_date.day, tzinfo=UTC)
        day_end = day_start.replace(hour=23, minute=59, second=59)
        result = await self.db.execute(
            select(ShiftAssignment.id)
            .join(Shift, ShiftAssignment.shift_id == Shift.id)
            .where(
                ShiftAssignment.analyst_id == analyst_id,
                Shift.shift_type.in_([ShiftType.DAY.value, ShiftType.NIGHT.value]),
                Shift.starts_at >= day_start,
                Shift.starts_at <= day_end,
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def _load_prev_offset(
        self, analyst_id: uuid.UUID, year: int, month: int, fallback_slot: int
    ) -> int:
        """Compute 2/2 phase offset from last 4 days of previous month.

        If no previous history exists (new analyst), use fallback_slot % 4
        to spread analysts evenly across phase groups.
        """
        py, pm = previous_month(year, month)
        plast = calendar.monthrange(py, pm)[1]
        tail: list[bool] = []
        for d in [plast - 3, plast - 2, plast - 1, plast]:
            if d >= 1:
                tail.append(await self._analyst_worked_on_date(analyst_id, date(py, pm, d)))
            else:
                tail.append(False)
        while len(tail) < 4:
            tail.insert(0, False)
        t = tuple(tail[-4:])
        if not any(t):
            return fallback_slot % 4
        return _phase_from_tail(t)

    async def _load_constraints(
        self, analyst_ids: list[uuid.UUID], year: int, month: int
    ) -> tuple[dict[str, set[int]], dict[str, set[int]]]:
        """Load vacation days (hard) and PREFER_OFF requests (Вх) for the month."""
        month_start, month_end = month_bounds(year, month)
        last_day = calendar.monthrange(year, month)[1]
        vacation: dict[str, set[int]] = {str(aid): set() for aid in analyst_ids}
        day_off: dict[str, set[int]] = {str(aid): set() for aid in analyst_ids}

        abs_result = await self.db.execute(
            select(Absence).where(
                Absence.analyst_id.in_(analyst_ids),
                Absence.status == RequestStatus.APPROVED.value,
                Absence.starts_at <= month_end,
                Absence.ends_at >= month_start,
            )
        )
        for ab in abs_result.scalars().all():
            start = max(ab.starts_at.date(), date(year, month, 1))
            end = min(ab.ends_at.date(), date(year, month, last_day))
            d = start
            while d <= end:
                vacation[str(ab.analyst_id)].add(d.day)
                d = d + timedelta(days=1)

        pref_result = await self.db.execute(
            select(ShiftPreference).where(
                ShiftPreference.analyst_id.in_(analyst_ids),
                ShiftPreference.preference_type == PreferenceType.PREFER_OFF.value,
                ShiftPreference.status == RequestStatus.PENDING.value,
                ShiftPreference.date >= month_start,
                ShiftPreference.date <= month_end,
            )
        )
        for pref in pref_result.scalars().all():
            day_off[str(pref.analyst_id)].add(pref.date.day)

        return vacation, day_off

    async def _find_overlapping_schedule(
        self, team_id: uuid.UUID, period_start: datetime, period_end: datetime
    ) -> Schedule | None:
        result = await self.db.execute(
            select(Schedule)
            .where(
                Schedule.team_id == team_id,
                Schedule.period_start <= period_end,
                Schedule.period_end >= period_start,
            )
            .order_by(Schedule.period_start.desc())
        )
        return result.scalars().first()

    async def _count_shifts_in_month(self, schedule_id: uuid.UUID, year: int, month: int) -> int:
        month_start, month_end = month_bounds(year, month)
        count = await self.db.scalar(
            select(func.count())
            .select_from(Shift)
            .where(
                Shift.schedule_id == schedule_id,
                Shift.starts_at >= month_start,
                Shift.starts_at <= month_end,
            )
        )
        return int(count or 0)

    async def _delete_shifts_in_month(self, schedule_id: uuid.UUID, year: int, month: int) -> None:
        month_start, month_end = month_bounds(year, month)
        shift_ids_result = await self.db.execute(
            select(Shift.id).where(
                Shift.schedule_id == schedule_id,
                Shift.starts_at >= month_start,
                Shift.starts_at <= month_end,
            )
        )
        shift_ids = [row[0] for row in shift_ids_result.all()]
        if not shift_ids:
            return
        await self.db.execute(
            delete(ShiftAssignment).where(ShiftAssignment.shift_id.in_(shift_ids))
        )
        await self.db.execute(delete(Shift).where(Shift.id.in_(shift_ids)))
        await self.db.flush()

    async def _persist_team_shifts(
        self,
        team: Team,
        db_analysts: list[Analyst],
        month_schedule: MonthSchedule,
        period_start: datetime,
        period_end: datetime,
        year: int,
        month: int,
        created_by: uuid.UUID,
        *,
        replace: bool = False,
    ) -> TeamGenerateResult:
        existing = await self._find_overlapping_schedule(team.id, period_start, period_end)
        shifts_in_month = (
            await self._count_shifts_in_month(existing.id, year, month) if existing else 0
        )

        if existing and shifts_in_month > 0:
            if not replace:
                return TeamGenerateResult(
                    team_id=team.id,
                    team_name=team.name,
                    schedule_id=existing.id,
                    schedule_name=existing.name,
                    shifts_created=0,
                    assignments_created=0,
                    status="skipped",
                    message=(
                        f"В {MONTH_NAMES_RU[month]} {year} уже есть {shifts_in_month} смен. "
                        "Повторите с пересозданием."
                    ),
                )
            await self._delete_shifts_in_month(existing.id, year, month)
        elif existing:
            existing.period_start = min(existing.period_start, period_start)
            existing.period_end = max(existing.period_end, period_end)

        schedule_name = f"{team.name} · {MONTH_NAMES_RU[month]} {year}"
        if existing:
            schedule = existing
            schedule.name = schedule_name
            schedule.period_start = period_start
            schedule.period_end = period_end
            schedule.status = "published"
        else:
            schedule = Schedule(
                team_id=team.id,
                name=schedule_name,
                period_start=period_start,
                period_end=period_end,
                status="published",
                created_by=created_by,
            )
            self.db.add(schedule)
        await self.db.flush()

        shifts_created = 0
        assignments_created = 0
        summary_parts: list[str] = []

        for db_analyst in db_analysts:
            key = str(db_analyst.id)
            if key not in month_schedule.grid:
                continue
            row = month_schedule.grid[key]
            day_count = 0
            night_count = 0
            for d, stype in enumerate(row):
                db_shift_type = _DB_SHIFT_TYPE.get(stype)
                if db_shift_type is None:
                    continue
                work_date = date(year, month, d + 1)
                starts_at, ends_at = shift_times_for_date(work_date, db_shift_type)
                shift = Shift(
                    schedule_id=schedule.id,
                    shift_type=db_shift_type.value,
                    starts_at=starts_at,
                    ends_at=ends_at,
                    required_level="L1",
                    required_count=1,
                )
                self.db.add(shift)
                await self.db.flush()
                shifts_created += 1
                self.db.add(ShiftAssignment(
                    shift_id=shift.id,
                    analyst_id=db_analyst.id,
                    assigned_by=created_by,
                    is_on_call=False,
                ))
                assignments_created += 1
                if stype == SchedShiftType.DAY:
                    day_count += 1
                else:
                    night_count += 1

            user_result = await self.db.execute(select(User).where(User.id == db_analyst.user_id))
            user = user_result.scalar_one_or_none()
            name = user.full_name if user else key
            night_part = f", {night_count} ноч." if night_count else ""
            off = month_schedule.n_days - day_count - night_count
            summary_parts.append(f"{name}: {day_count + night_count} смен{night_part}, {off} вых.")

        prev_y, prev_m = previous_month(year, month)
        return TeamGenerateResult(
            team_id=team.id,
            team_name=team.name,
            schedule_id=schedule.id,
            schedule_name=schedule.name,
            shifts_created=shifts_created,
            assignments_created=assignments_created,
            status="created",
            message=(
                f"График {MONTH_NAMES_RU[month]} {year}: {shifts_created} смен, "
                f"стыковка с {MONTH_NAMES_RU[prev_m]} {prev_y}. "
                + " | ".join(summary_parts[:6])
            ),
        )

    async def generate_next_month(
        self,
        created_by: uuid.UUID,
        *,
        team_id: uuid.UUID | None = None,
        replace: bool = False,
    ) -> tuple[datetime, datetime, int, int, list[TeamGenerateResult]]:
        period_start, period_end, year, month = next_calendar_month()

        teams_query = select(Team).order_by(Team.name)
        if team_id:
            teams_query = teams_query.where(Team.id == team_id)
        teams_result = await self.db.execute(teams_query)
        teams = sorted(list(teams_result.scalars().all()), key=_team_sort_key)

        if team_id and not teams:
            raise ValueError("Team not found")

        # Load all analysts across all teams into a single roster so that
        # the shift_scheduler can correctly assign night anti-phase coverage
        # between East and West regions.
        all_db_analysts: list[Analyst] = []
        team_by_analyst_id: dict[str, Team] = {}
        analysts_by_team: dict[uuid.UUID, list[Analyst]] = {}

        for team in teams:
            result = await self.db.execute(
                select(Analyst)
                .where(Analyst.team_id == team.id, Analyst.is_archived.is_(False))
                .order_by(Analyst.created_at)
            )
            team_analysts = list(result.scalars().all())
            analysts_by_team[team.id] = team_analysts
            for a in team_analysts:
                all_db_analysts.append(a)
                team_by_analyst_id[str(a.id)] = team

        if not all_db_analysts:
            return period_start, period_end, year, month, []

        all_ids = [a.id for a in all_db_analysts]
        vacation_by_id, day_off_by_id = await self._load_constraints(all_ids, year, month)

        sched_analysts: list[SchedAnalyst] = []
        for idx, db_analyst in enumerate(all_db_analysts):
            key = str(db_analyst.id)
            team = team_by_analyst_id[key]
            region = Region.EAST if _team_is_east(team) else Region.WEST
            offset = await self._load_prev_offset(db_analyst.id, year, month, idx)
            sched_analysts.append(SchedAnalyst(
                name=key,
                region=region,
                allows_night=db_analyst.accepts_night_shifts,
                offset=offset,
                vacation=vacation_by_id.get(key, set()),
                day_off_requests=day_off_by_id.get(key, set()),
            ))

        month_schedule = generate(sched_analysts, year, month)

        results: list[TeamGenerateResult] = []
        for team in teams:
            team_db_analysts = analysts_by_team.get(team.id, [])
            if not team_db_analysts:
                results.append(TeamGenerateResult(
                    team_id=team.id,
                    team_name=team.name,
                    schedule_id=None,
                    schedule_name=None,
                    shifts_created=0,
                    assignments_created=0,
                    status="skipped",
                    message="Нет активных аналитиков в команде",
                ))
                continue
            result = await self._persist_team_shifts(
                team,
                team_db_analysts,
                month_schedule,
                period_start,
                period_end,
                year,
                month,
                created_by,
                replace=replace,
            )
            results.append(result)

        return period_start, period_end, year, month, results
