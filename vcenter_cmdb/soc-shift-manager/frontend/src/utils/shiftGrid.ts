import type { CalendarShift } from "../api/types";
import { toDateKey } from "./calendarRegion";

export type CellState = "empty" | "day" | "night";
export type CellAction = "day" | "night" | "clear";

export function cellKey(analystId: string, dateKey: string): string {
  return `${analystId}:${dateKey}`;
}

export function getMonthDays(year: number, month: number): Date[] {
  const lastDay = new Date(year, month + 1, 0).getDate();
  return Array.from({ length: lastDay }, (_, i) => new Date(year, month, i + 1));
}

/**
 * Converts a UTC timestamp to a YYYY-MM-DD key using UTC date components.
 * Used for matching server-stored shift starts_at values to calendar cells —
 * avoids timezone drift where 20:00 UTC becomes the next calendar day in UTC+4+.
 */
export function toUTCDateKey(date: Date): string {
  const y = date.getUTCFullYear();
  const m = String(date.getUTCMonth() + 1).padStart(2, "0");
  const d = String(date.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function getCellShifts(
  shifts: CalendarShift[],
  analystId: string,
  dateKey: string,
): CalendarShift[] {
  return shifts.filter(
    (s) =>
      s.analyst_id === analystId &&
      toUTCDateKey(new Date(s.starts_at)) === dateKey &&
      (s.shift_type === "day" || s.shift_type === "night"),
  );
}

export function getCellState(
  shifts: CalendarShift[],
  analystId: string,
  dateKey: string,
): CellState {
  const cellShifts = getCellShifts(shifts, analystId, dateKey);
  const hasDay = cellShifts.some((s) => s.shift_type === "day");
  const hasNight = cellShifts.some((s) => s.shift_type === "night");
  if (hasNight && !hasDay) return "night";
  if (hasDay) return "day";
  return "empty";
}

export function stateAfterAction(action: CellAction): CellState {
  if (action === "clear") return "empty";
  if (action === "day") return "day";
  return "night";
}

/** Следующее действие при клике: пусто → день → ночь → сброс */
export function nextCellAction(current: CellState): CellAction {
  if (current === "empty") return "day";
  if (current === "day") return "night";
  return "clear";
}

export function shiftRangeIso(dateKey: string, shiftType: "day" | "night"): { starts_at: string; ends_at: string } {
  const [y, m, d] = dateKey.split("-").map(Number);
  if (shiftType === "day") {
    return {
      starts_at: new Date(Date.UTC(y, m - 1, d, 8, 0, 0)).toISOString(),
      ends_at: new Date(Date.UTC(y, m - 1, d, 18, 0, 0)).toISOString(),
    };
  }
  const starts = new Date(Date.UTC(y, m - 1, d, 20, 0, 0));
  const ends = new Date(Date.UTC(y, m - 1, d, 20, 0, 0));
  ends.setUTCDate(ends.getUTCDate() + 1);
  ends.setUTCHours(8, 0, 0, 0);
  return { starts_at: starts.toISOString(), ends_at: ends.toISOString() };
}

export function getOverlappingShifts(
  shifts: CalendarShift[],
  analystId: string,
  startsAt: string,
  endsAt: string,
): CalendarShift[] {
  const start = Date.parse(startsAt);
  const end = Date.parse(endsAt);
  return shifts.filter((s) => {
    if (s.analyst_id !== analystId) return false;
    const sStart = Date.parse(s.starts_at);
    const sEnd = Date.parse(s.ends_at);
    return sStart < end && sEnd > start;
  });
}
