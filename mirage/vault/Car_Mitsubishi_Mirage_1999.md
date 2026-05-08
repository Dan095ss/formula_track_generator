---
type: vehicle
make: Mitsubishi
model: Mirage
year: 1999
generation: "5th gen (CJ/CK/CL)"
vin: ""
engine_code: ""
engine_displacement_l: 1.5
transmission: ""
purchase_date: ""
purchase_mileage_km: 0
current_mileage_km: 0
manual_volumes:
  - "[[Volume_1_Engine]]"
  - "[[Volume_2_Chassis]]"
  - "[[Wiring_Diagrams]]"
tags: [vehicle, mirage]
---

# Mitsubishi Mirage 1999

Главная карточка автомобиля. Все журналы (`Maintenance_Log`, `Issue_Report`, `Part_Catalog`, идеи модификаций) ссылаются сюда полем `vehicle: [[Car_Mitsubishi_Mirage_1999]]`.

## Быстрые ссылки

- 📘 Мануал: `00_Manual/`
- 🔧 Журнал ТО: `10_Maintenance/`
- ⚠️ Проблемы: `20_Issues/`
- 📦 Запчасти: `30_Parts/`
- 🛠️ Идеи и моды: `40_Mods/`
- 📊 Отчёты: `99_Dataview/`

## Заполни перед использованием

- [ ] VIN
- [ ] Точный engine code (`engine_code` в YAML)
- [ ] Тип трансмиссии (`transmission`)
- [ ] Дата покупки и пробег (`purchase_date`, `purchase_mileage_km`)
- [ ] Текущий пробег (`current_mileage_km`) — обновлять с каждой записью ТО

## Связанные мануалы

- `Volume 1` — двигатель, трансмиссия, сцепление
- `Volume 2` — подвеска, тормоза, кузов, электрика шасси
- `Wiring Diagrams` — электрические схемы

```dataview
TABLE WITHOUT ID
  file.link AS "Раздел",
  chapter_code AS "Код",
  page_range AS "Стр."
FROM "00_Manual"
WHERE type = "manual_section"
SORT chapter_code ASC, file.name ASC
```
