import { useCallback, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, Eraser, Wand2 } from "lucide-react";
import { api } from "../api/client";
import type {
  Analyst,
  CalendarAbsence,
  CalendarOffPreference,
  CalendarShift,
  ClearMonthResponse,
  GenerateNextMonthResponse,
  Schedule,
} from "../api/types";
import { useAuth } from "../context/AuthContext";
import { formatMonthYear, getAnalystRegion, getShiftRegion, toDateKey, type Region } from "../utils/calendarRegion";
import { isAdmin, isAnalyst } from "../utils/roles";
import {
  cellKey,
  getCellShifts,
  getCellState,
  getOverlappingShifts,
  nextCellAction,
  shiftRangeIso,
  stateAfterAction,
  type CellAction,
  type CellState,
  toUTCDateKey,
} from "../utils/shiftGrid";
import { AnalystShiftGrid } from "./AnalystShiftGrid";
import styles from "./CalendarPage.module.css";

function scheduleForRegion(
  schedules: Schedule[],
  analysts: Analyst[],
  region: Region,
  year: number,
  month: number,
): Schedule | undefined {
  const teamIds = new Set(
    analysts.filter((a) => getAnalystRegion(a) === region && a.team_id).map((a) => a.team_id!),
  );
  const candidates = schedules.filter((s) => teamIds.has(s.team_id));
  if (candidates.length === 0) return schedules[0];

  const midMonth = new Date(year, month, 15);
  const covering = candidates.find((s) => {
    const start = new Date(s.period_start);
    const end = new Date(s.period_end);
    return midMonth >= start && midMonth <= end;
  });
  return covering ?? candidates[0];
}

export function CalendarPage() {
  const { user } = useAuth();
  const qc = useQueryClient();
  const canManage = isAdmin(user?.role);
  const canRequestOff = isAnalyst(user?.role);

  const [error, setError] = useState("");
  const [generateMessage, setGenerateMessage] = useState("");
  const [optimistic, setOptimistic] = useState<Record<string, CellState>>({});
  const [savingCells, setSavingCells] = useState<Set<string>>(new Set());

  const today = useMemo(() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d;
  }, []);

  const [viewDate, setViewDate] = useState(() => new Date(today.getFullYear(), today.getMonth(), 1));

  const { data: shifts = [], isLoading } = useQuery({
    queryKey: ["calendar-shifts"],
    queryFn: async () => {
      const { data } = await api.get<CalendarShift[]>("/calendar/shifts");
      return data;
    },
  });

  const { data: schedules = [] } = useQuery({
    queryKey: ["schedules"],
    queryFn: async () => {
      const { data } = await api.get<Schedule[]>("/schedules");
      return data;
    },
    enabled: canManage,
  });

  const { data: analysts = [] } = useQuery({
    queryKey: ["analysts"],
    queryFn: async () => {
      const { data } = await api.get<Analyst[]>("/analysts");
      return data;
    },
  });

  const myAnalystId = useMemo(
    () => analysts.find((a) => a.user_id === user?.id)?.id ?? null,
    [analysts, user?.id],
  );

  const westAnalysts = useMemo(
    () => analysts.filter((a) => !a.is_archived && getAnalystRegion(a) === "west"),
    [analysts],
  );
  const eastAnalysts = useMemo(
    () => analysts.filter((a) => !a.is_archived && getAnalystRegion(a) === "east"),
    [analysts],
  );

  const westShifts = useMemo(() => shifts.filter((s) => getShiftRegion(s) === "west"), [shifts]);
  const eastShifts = useMemo(() => shifts.filter((s) => getShiftRegion(s) === "east"), [shifts]);

  const year = viewDate.getFullYear();
  const month = viewDate.getMonth();

  const { data: offPreferences = [] } = useQuery({
    queryKey: ["calendar-off-preferences", year, month],
    queryFn: async () => {
      const { data } = await api.get<CalendarOffPreference[]>("/calendar/off-preferences", {
        params: { year, month: month + 1 },
      });
      return data;
    },
    enabled: canManage || canRequestOff,
  });

  const offPreferenceKeys = useMemo(() => {
    const set = new Set<string>();
    for (const pref of offPreferences) {
      const dateKey = pref.date.slice(0, 10);
      set.add(`${pref.analyst_id}:${dateKey}`);
    }
    return set;
  }, [offPreferences]);

  const { data: absences = [] } = useQuery({
    queryKey: ["calendar-absences", year, month],
    queryFn: async () => {
      const { data } = await api.get<CalendarAbsence[]>("/calendar/absences", {
        params: { year, month: month + 1 },
      });
      return data;
    },
    enabled: canManage || canRequestOff,
  });

  const absenceKeys = useMemo(() => {
    const set = new Set<string>();
    for (const a of absences) {
      const dateKey = a.date.slice(0, 10);
      set.add(`${a.analyst_id}:${dateKey}`);
    }
    return set;
  }, [absences]);

  const monthShiftCount = useMemo(
    () =>
      shifts.filter((s) => {
        const d = new Date(s.starts_at);
        return d.getFullYear() === year && d.getMonth() === month;
      }).length,
    [shifts, year, month],
  );

  const selectedMonthLabel = useMemo(() => formatMonthYear(viewDate), [viewDate]);

  const getDisplayState = useCallback(
    (analystId: string, dateKey: string): CellState => {
      const key = cellKey(analystId, dateKey);
      if (key in optimistic) return optimistic[key];
      return getCellState(shifts, analystId, dateKey);
    },
    [shifts, optimistic],
  );

  const patchCellInCache = useCallback(
    (analystId: string, dateKey: string, created: CalendarShift | null) => {
      qc.setQueryData<CalendarShift[]>(["calendar-shifts"], (old) => {
        if (!old) return old;
        const rest = old.filter(
          (s) => !(s.analyst_id === analystId && toUTCDateKey(new Date(s.starts_at)) === dateKey),
        );
        return created ? [...rest, created] : rest;
      });
    },
    [qc],
  );

  const applyCell = useCallback(
    async (region: Region, analystId: string, dateKey: string, action: CellAction) => {
      const key = cellKey(analystId, dateKey);
      const regionAnalysts = region === "west" ? westAnalysts : eastAnalysts;
      const schedule = scheduleForRegion(schedules, regionAnalysts, region, year, month);

      if (!schedule) {
        setError("Нет графика для этого региона. Сгенерируйте график на месяц.");
        return;
      }

      const newState = stateAfterAction(action);
      setOptimistic((prev) => ({ ...prev, [key]: newState }));
      setSavingCells((prev) => new Set(prev).add(key));
      setError("");

      try {
        if (action !== "clear") {
          const { starts_at, ends_at } = shiftRangeIso(dateKey, action);
          const overlapping = getOverlappingShifts(shifts, analystId, starts_at, ends_at);
          await Promise.all(overlapping.map((s) => api.delete(`/shifts/${s.id}`)));

          const { data: created } = await api.post<CalendarShift>("/shifts/with-assignment", {
            schedule_id: schedule.id,
            analyst_id: analystId,
            shift_type: action,
            starts_at,
            ends_at,
            is_on_call: false,
          });
          patchCellInCache(analystId, dateKey, created);
        } else {
          const existing = getCellShifts(shifts, analystId, dateKey);
          await Promise.all(existing.map((s) => api.delete(`/shifts/${s.id}`)));
          patchCellInCache(analystId, dateKey, null);
        }

        setOptimistic((prev) => {
          const next = { ...prev };
          delete next[key];
          return next;
        });
      } catch (err: unknown) {
        setOptimistic((prev) => {
          const next = { ...prev };
          delete next[key];
          return next;
        });
        const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
        setError(String(detail ?? "Ошибка изменения смены"));
        void qc.invalidateQueries({ queryKey: ["calendar-shifts"] });
      } finally {
        setSavingCells((prev) => {
          const next = new Set(prev);
          next.delete(key);
          return next;
        });
      }
    },
    [schedules, westAnalysts, eastAnalysts, shifts, year, month, qc, patchCellInCache],
  );

  const handleWestClick = useCallback(
    (analystId: string, dateKey: string, currentState: CellState) => {
      void applyCell("west", analystId, dateKey, nextCellAction(currentState));
    },
    [applyCell],
  );

  const handleEastClick = useCallback(
    (analystId: string, dateKey: string, currentState: CellState) => {
      void applyCell("east", analystId, dateKey, nextCellAction(currentState));
    },
    [applyCell],
  );

  const hasOffPreference = useCallback(
    (analystId: string, dateKey: string) => offPreferenceKeys.has(`${analystId}:${dateKey}`),
    [offPreferenceKeys],
  );

  const hasAbsence = useCallback(
    (analystId: string, dateKey: string) => absenceKeys.has(`${analystId}:${dateKey}`),
    [absenceKeys],
  );

  const toggleAbsence = useMutation({
    mutationFn: (payload: { analyst_id: string; date: string }) =>
      api.post("/calendar/absences/toggle", {
        analyst_id: payload.analyst_id,
        date: payload.date,
        absence_type: "vacation",
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["calendar-shifts"] });
      void qc.invalidateQueries({ queryKey: ["calendar-absences", year, month] });
      setError("");
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setError(String(err.response?.data?.detail ?? "Не удалось сохранить отпуск"));
    },
  });

  const handleToggleAbsence = useCallback(
    (analystId: string, dateKey: string) => {
      if (!canManage) return;
      const key = `abs:${analystId}:${dateKey}`;
      setSavingCells((prev) => new Set(prev).add(key));
      toggleAbsence.mutate(
        { analyst_id: analystId, date: dateKey },
        {
          onSettled: () => {
            setSavingCells((prev) => {
              const next = new Set(prev);
              next.delete(key);
              return next;
            });
          },
        },
      );
    },
    [canManage, toggleAbsence],
  );

  const toggleOffPreference = useMutation({
    mutationFn: (dateKey: string) =>
      api.post("/preferences/toggle-off", { date: dateKey }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["calendar-off-preferences"] });
      setError("");
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setError(String(err.response?.data?.detail ?? "Не удалось сохранить пожелание"));
    },
  });

  const handleToggleOffPreference = useCallback(
    (analystId: string, dateKey: string) => {
      if (myAnalystId !== analystId) return;
      const key = `off:${analystId}:${dateKey}`;
      setSavingCells((prev) => new Set(prev).add(key));
      toggleOffPreference.mutate(dateKey, {
        onSettled: () => {
          setSavingCells((prev) => {
            const next = new Set(prev);
            next.delete(key);
            return next;
          });
        },
      });
    },
    [myAnalystId, toggleOffPreference],
  );

  const generateSchedule = useMutation({
    mutationFn: (replace = false) =>
      api.post<GenerateNextMonthResponse>("/schedules/generate-next-month", null, {
        params: { replace },
      }),
    onSuccess: ({ data }) => {
      qc.invalidateQueries({ queryKey: ["calendar-shifts"] });
      qc.invalidateQueries({ queryKey: ["schedules"] });
      setError("");
      const created = data.teams.filter((t) => t.status === "created");
      const skipped = data.teams.filter((t) => t.status === "skipped");
      const failed = data.teams.filter((t) => t.status === "failed");
      const totalShifts = created.reduce((sum, t) => sum + t.shifts_created, 0);
      if (failed.length > 0) {
        setError(failed.map((t) => `${t.team_name}: ${t.message}`).join(". "));
      }
      if (created.length > 0) {
        setGenerateMessage(
          `График на ${data.month_label} создан: ${totalShifts} дневных смен — ${created.map((t) => t.team_name).join(", ")}`,
        );
        const start = new Date(data.period_start);
        setViewDate(new Date(start.getFullYear(), start.getMonth(), 1));
      } else if (skipped.length > 0) {
        const onlyHasShifts = skipped.every((t) => t.message.includes("уже есть"));
        if (onlyHasShifts) {
          const retry = window.confirm(
            `${skipped.map((t) => t.team_name + ": " + t.message).join("\n")}\n\nПересоздать смены за этот месяц?`,
          );
          if (retry) generateSchedule.mutate(true);
          else setGenerateMessage(skipped.map((t) => `${t.team_name}: ${t.message}`).join(". "));
        } else {
          setGenerateMessage(skipped.map((t) => `${t.team_name}: ${t.message}`).join(". "));
        }
      }
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setGenerateMessage("");
      setError(String(err.response?.data?.detail ?? "Ошибка генерации"));
    },
  });

  const nextMonthLabel = useMemo(() => {
    const d = new Date(today.getFullYear(), today.getMonth() + 1, 1);
    return d.toLocaleDateString("ru-RU", { month: "long", year: "numeric" });
  }, [today]);

  const clearMonth = useMutation({
    mutationFn: () =>
      api.delete<ClearMonthResponse>("/calendar/shifts", {
        params: { year, month: month + 1 },
      }),
    onSuccess: ({ data }) => {
      qc.invalidateQueries({ queryKey: ["calendar-shifts"] });
      setOptimistic({});
      setError("");
      if (data.shifts_deleted > 0) {
        setGenerateMessage(`Календарь за ${data.month_label} очищен: удалено ${data.shifts_deleted} смен`);
      } else {
        setGenerateMessage(`В ${data.month_label} нет смен для удаления`);
      }
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      setGenerateMessage("");
      setError(String(err.response?.data?.detail ?? "Ошибка очистки календаря"));
    },
  });

  return (
    <div className={styles.page}>
      <div className={styles.toolbar}>
        <div className={styles.toolbarLeft}>
          <h1>Календарь смен</h1>
          <span className={styles.liveBadge}>
            {isLoading ? "..." : `${shifts.length} смен · Запад ${westShifts.length} · Восток ${eastShifts.length}`}
          </span>
        </div>
        <div className={styles.toolbarRight}>
          {canManage && (
            <>
              <button
                type="button"
                className={`btn ${styles.clearBtn}`}
                disabled={clearMonth.isPending || monthShiftCount === 0}
                onClick={() => {
                  if (
                    window.confirm(
                      `Очистить календарь за ${selectedMonthLabel}?\n\nБудет удалено ${monthShiftCount} смен (Запад и Восток).`,
                    )
                  ) {
                    setGenerateMessage("");
                    clearMonth.mutate();
                  }
                }}
              >
                <Eraser size={16} />
                {clearMonth.isPending ? "Очистка..." : "Очистить месяц"}
              </button>
              <button
                type="button"
                className={`btn ${styles.generateBtn}`}
                onClick={() => {
                  if (
                    window.confirm(
                      `Сгенерировать дневные смены на ${nextMonthLabel} (схема 2 через 2)?`,
                    )
                  ) {
                    setGenerateMessage("");
                    generateSchedule.mutate(false);
                  }
                }}
                disabled={generateSchedule.isPending}
              >
                <Wand2 size={16} />
                {generateSchedule.isPending ? "Генерация..." : "Сгенерировать на след. месяц"}
              </button>
            </>
          )}
          <div className={styles.nav}>
            <button
              className={styles.navBtn}
              type="button"
              onClick={() => setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() - 1, 1))}
            >
              <ChevronLeft size={16} />
            </button>
            <span className={styles.navLabel}>{formatMonthYear(viewDate)}</span>
            <button
              className={styles.navBtn}
              type="button"
              onClick={() => setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 1))}
            >
              <ChevronRight size={16} />
            </button>
            <button
              className={`btn ${styles.todayBtn}`}
              type="button"
              onClick={() => setViewDate(new Date(today.getFullYear(), today.getMonth(), 1))}
            >
              Сегодня
            </button>
          </div>
        </div>
      </div>

      {generateMessage && <p className={styles.generateMessage}>{generateMessage}</p>}
      {error && <p className={styles.pageError}>{error}</p>}

      <div className={styles.legend}>
        <span className={styles.legendItem}>
          <span className={`${styles.legendSwatch} ${styles.swatchDay}`} /> Д — дневная
        </span>
        <span className={styles.legendItem}>
          <span className={`${styles.legendSwatch} ${styles.swatchNight}`} /> Н — ночная
        </span>
        <span className={styles.legendItem}>
          <span className={`${styles.legendSwatch} ${styles.swatchAbsence}`} /> О — отпуск
        </span>
        <span className={styles.legendItem}>
          <span className={`${styles.legendSwatch} ${styles.swatchOffRequest}`} /> Вх — запрос выходного
        </span>
        {canManage && (
          <span className={styles.legendItem}>
            <span className={`${styles.legendSwatch} ${styles.swatchEmpty}`} /> клик: пусто → день → ночь → сброс
          </span>
        )}
        {canRequestOff && !canManage && (
          <span className={styles.legendItem}>клик по своей строке — поставить или снять «Вх»</span>
        )}
      </div>

      <div className={styles.stackedCalendars}>
        <AnalystShiftGrid
          region="west"
          viewDate={viewDate}
          today={today}
          analysts={westAnalysts}
          getCellState={getDisplayState}
          canManage={canManage}
          canRequestOff={canRequestOff}
          myAnalystId={myAnalystId}
          hasOffPreference={hasOffPreference}
          hasAbsence={hasAbsence}
          savingCells={savingCells}
          onCellClick={handleWestClick}
          onToggleOffPreference={handleToggleOffPreference}
          onToggleAbsence={handleToggleAbsence}
        />
        <AnalystShiftGrid
          region="east"
          viewDate={viewDate}
          today={today}
          analysts={eastAnalysts}
          getCellState={getDisplayState}
          canManage={canManage}
          canRequestOff={canRequestOff}
          myAnalystId={myAnalystId}
          hasOffPreference={hasOffPreference}
          hasAbsence={hasAbsence}
          savingCells={savingCells}
          onCellClick={handleEastClick}
          onToggleOffPreference={handleToggleOffPreference}
          onToggleAbsence={handleToggleAbsence}
        />
      </div>
    </div>
  );
}
