<%*
const today = tp.date.now("YYYY-MM-DD");

const severity = await tp.system.suggester(
  ["🟢 Низкая", "🟡 Средняя", "🟠 Высокая", "🔴 Критическая"],
  ["low", "medium", "high", "critical"],
  true,
  "Серьёзность"
);

const system = await tp.system.suggester(
  ["Двигатель", "Тормоза", "Подвеска", "Электрика", "Трансмиссия", "Кузов", "Прочее"],
  ["engine", "brakes", "suspension", "electrical", "transmission", "body", "other"],
  true,
  "Подозреваемая система"
);

const mileage = await tp.system.prompt("Пробег при обнаружении (км)", "0");
const shortTitle = await tp.system.prompt("Короткое название проблемы", "проблема");
const symptom = await tp.system.prompt("Главный симптом одной фразой", "");

const fileTitle = `${today}_${shortTitle.replace(/[^\p{L}\p{N}_-]+/gu, "_")}`;
await tp.file.rename(fileTitle);
await tp.file.move(`/20_Issues/${fileTitle}`);
-%>
---
type: issue
vehicle: "[[Car_Mitsubishi_Mirage_1999]]"
date_reported: <% today %>
mileage_km: <% mileage %>
severity: <% severity %>
status: open
symptoms:
  - "<% symptom %>"
suspected_systems: [<% system %>]
related_manual: []
related_parts: []
diagnosis_steps: []
root_cause: ""
resolution_maintenance: ""
resolved_date: ""
cost_to_resolve_rub: 0
tags: [issue, <% system %>]
---

# ⚠️ <% shortTitle %>

> **Авто:** [[Car_Mitsubishi_Mirage_1999]]  
> **Обнаружено:** <% today %> на <% mileage %> км  
> **Серьёзность:** <% severity %> · **Система:** <% system %>  
> **Статус:** `open`

## Симптомы

- <% symptom %>

## Условия проявления

- Когда: (на холодную / прогретом / в дождь / на скорости / при торможении ...)
- Как часто: (постоянно / периодически / один раз)

## Подозреваемые узлы

`[[]]`

## Шаги диагностики

- [ ] Визуальный осмотр
- [ ] Проверка кодов ошибок
- [ ] Проверка по мануалу: `[[]]`

## Гипотеза

(описать предполагаемую причину)

## Resolution

- **Что сделано:** —
- **Замена:** `[[]]`
- **Ремонт-запись:** `[[]]`
