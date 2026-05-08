<%*
const today = tp.date.now("YYYY-MM-DD");

const serviceType = await tp.system.suggester(
  ["Замена масла", "Фильтры", "Тормоза", "Плановое ТО", "Шины", "Ремонт", "Осмотр"],
  ["oil_change", "filter", "brakes", "scheduled_TO", "tyres", "repair", "inspection"],
  true,
  "Тип работы"
);

const status = await tp.system.suggester(
  ["Запланировано", "В работе", "Сделано", "Отменено"],
  ["planned", "in_progress", "done", "cancelled"],
  true,
  "Статус"
);

const performedBy = await tp.system.suggester(
  ["Сам", "СТО"],
  ["self", "shop"],
  true,
  "Кто выполнял"
);

const mileage = await tp.system.prompt("Пробег на момент работы (км)", "0");
const shop = performedBy === "shop"
  ? await tp.system.prompt("Название/ссылка СТО (можно пусто)", "")
  : "";
const costParts = await tp.system.prompt("Стоимость запчастей (руб)", "0");
const costLabor = await tp.system.prompt("Стоимость работ (руб)", "0");
const notes = await tp.system.prompt("Краткие заметки", "");

const fileTitle = `${today}_${serviceType}`;
await tp.file.rename(fileTitle);
await tp.file.move(`/10_Maintenance/${fileTitle}`);

const total = (parseInt(costParts) || 0) + (parseInt(costLabor) || 0);
-%>
---
type: maintenance
vehicle: "[[Car_Mitsubishi_Mirage_1999]]"
date: <% today %>
mileage_km: <% mileage %>
service_type: <% serviceType %>
status: <% status %>
parts_used: []
parts_qty: []
cost_parts_rub: <% costParts %>
cost_labor_rub: <% costLabor %>
cost_total_rub: <% total %>
labor_hours: 0
performed_by: <% performedBy %>
shop: "<% shop %>"
next_due_date: ""
next_due_mileage_km: 0
related_issue: ""
related_manual: []
notes_short: "<% notes %>"
tags: [maintenance, <% serviceType %>]
---

# <% serviceType %> — <% today %> (<% mileage %> км)

> **Авто:** [[Car_Mitsubishi_Mirage_1999]]  
> **Статус:** <% status %> · **Кто:** <% performedBy %><% performedBy === "shop" && shop ? ` · ${shop}` : "" %>

## Что делал

<% notes %>

## Запчасти и расходники

| Артикул | Название | Кол-во | Цена за ед., руб |
| --- | --- | --- | --- |
| `[[]]` |  |  |  |

## Связанная проблема

`[[]]` — если работа была реактивной (по проблеме).

## Связанные разделы мануала

- `[[]]`

## Следующее ТО

- Дата: ?
- Пробег: ?
