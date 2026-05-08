<%*
const today = tp.date.now("YYYY-MM-DD");

const category = await tp.system.suggester(
  ["Масло/жидкость", "Фильтр", "Тормозные колодки", "Тормозной диск", "Датчик",
   "Шина", "Ремень", "Свеча", "Прочее"],
  ["fluid", "filter", "brake_pads", "brake_disc", "sensor",
   "tyre", "belt", "spark_plug", "other"],
  true,
  "Категория запчасти"
);

const name = await tp.system.prompt("Название запчасти (на русском)", "");
const oem = await tp.system.prompt("OEM-номер (артикул производителя)", "");
const manufacturer = await tp.system.prompt("Производитель (OEM)", "Mitsubishi");
const price = await tp.system.prompt("Последняя цена (руб)", "0");
const vendor = await tp.system.prompt("Поставщик (где брал)", "");
const lifespan = await tp.system.prompt("Типичный ресурс, км (0 если неизвестно)", "0");

const slug = (oem || name).replace(/[^A-Za-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "part";
const fileTitle = `${category}_${slug}`;
await tp.file.rename(fileTitle);
await tp.file.move(`/30_Parts/${fileTitle}`);
-%>
---
type: part
vehicle: "[[Car_Mitsubishi_Mirage_1999]]"
name: "<% name %>"
part_number_oem: "<% oem %>"
aftermarket_numbers: []
manufacturer: "<% manufacturer %>"
category: <% category %>
compatible_models:
  - "Mirage 1999"
price_last_rub: <% price %>
price_currency: RUB
vendor_last: "<% vendor %>"
vendor_url: ""
supersedes: []
superseded_by: ""
stock_on_hand: 0
typical_lifespan_km: <% lifespan %>
install_count: 0
last_installed: ""
tags: [part, <% category %>]
---

# 📦 <% name %>

> **OEM:** `<% oem %>`  
> **Производитель:** <% manufacturer %>  
> **Категория:** `<% category %>`  
> **Авто:** [[Car_Mitsubishi_Mirage_1999]]

## Цена и поставщики

| Дата | Цена, руб | Поставщик | URL |
| --- | --- | --- | --- |
| <% today %> | <% price %> | <% vendor %> |  |

## Аналоги (aftermarket)

| Бренд | Артикул | Цена | Где брать |
| --- | --- | --- | --- |
|  |  |  |  |

## История установок

```dataview
TABLE WITHOUT ID
  file.link AS "Запись ТО",
  date AS "Дата",
  mileage_km AS "Пробег"
FROM "10_Maintenance"
WHERE contains(parts_used, this.file.link)
SORT date DESC
```

## Связанные разделы мануала

- `[[]]`
