# Mirage Obsidian Assistant

Цифровой двойник **Mitsubishi Mirage 1999** в Obsidian: заводской service manual в виде Markdown-нот + структурированные журналы (ТО, проблемы, запчасти, моды) + Dataview-отчёты.

Цель — экономия токенов: ассистенту не нужно перечитывать PDF, он работает с локальной структурированной базой и точечно цитирует разделы.

---

## Структура репозитория

```
mirage/
├── pdf_to_md/                  Python-скрипт: PDF → Markdown
│   ├── extract.py              извлечение страниц + running header
│   ├── clean.py                чистка текста, реflow абзацев
│   ├── sectionize.py           группировка страниц в секции
│   ├── render.py               YAML + Markdown
│   ├── config.py               коды глав, переводы EN→RU
│   └── __main__.py             CLI
│
├── vault/                      Obsidian vault
│   ├── Car_Mitsubishi_Mirage_1999.md   главная карточка авто
│   ├── 00_Manual/              864 ноты — заводской мануал
│   │   ├── Volume_1_Engine/    двигатель, трансмиссия, сцепление
│   │   ├── Volume_2_Chassis/   подвеска, тормоза, кузов, электрика
│   │   └── Wiring_Diagrams/    электрические схемы
│   ├── 10_Maintenance/         журнал ТО (создаются через Templater)
│   ├── 20_Issues/              журнал проблем
│   ├── 30_Parts/               справочник запчастей
│   ├── 40_Mods/                идеи и проекты модификаций
│   ├── 90_Templates/           шаблоны Templater (3 шт.)
│   └── 99_Dataview/            готовые отчёты (расходы, открытые проблемы, масло)
│
├── Mirage_1999_Service_Manual/ исходные PDF (47 файлов, ≈2007 страниц)
├── tests/                      smoke-тесты конвертера
└── README.md                   этот файл
```

---

## Этап 1: Конвертация мануала (один раз)

### Установка зависимостей

```bash
python -m pip install pymupdf pyyaml
```

### Запуск

```bash
# Полный прогон (47 PDF → ≈865 нот)
python -m pdf_to_md \
  --src "Mirage_1999_Service_Manual" \
  --out "vault/00_Manual"

# Тестовый прогон одной главы
python -m pdf_to_md --src "Mirage_1999_Service_Manual" --out "vault/00_Manual" --only "35A"

# Без записи на диск (только план)
python -m pdf_to_md --src "Mirage_1999_Service_Manual" --out "vault/00_Manual" --dry-run
```

Каждая нота получает:
- `chapter_code` (`11A`, `35B`...) и человекочитаемые `chapter` + `section`
- `page_range` для точного цитирования
- `topics` и `tags` для поиска
- `aliases` (русский, английский, slug-формы) — Obsidian автоподтянет в графе

---

## Этап 2: Настройка Obsidian

1. Открой папку `vault/` как Obsidian vault.
2. Установи плагины Community: **Dataview**, **Templater**.
3. В настройках **Templater**:
   - Template folder: `90_Templates`
   - (опционально) забинди горячие клавиши на каждый шаблон через «Hotkeys».
4. В настройках **Dataview**: включи "Enable JavaScript Queries" — нужно для `dataviewjs` в отчёте по маслу.
5. Заполни обязательные поля в `Car_Mitsubishi_Mirage_1999.md` (VIN, engine_code, transmission, текущий пробег).

---

## Этап 3: Как вести журнал

### Новая запись ТО
`Cmd/Ctrl+P` → `Templater: Create new note from template` → **Maintenance_Log**.
Шаблон спросит: тип работы, статус, пробег, кто выполнял, цены — и создаст ноту в `10_Maintenance/`.

### Новая проблема
Шаблон **Issue_Report** — спросит серьёзность, систему, симптом. Нота создаётся в `20_Issues/` со `status: open`. Закрывая проблему, поставь `status: resolved` и заполни `resolution_maintenance: "[[ссылка на ТО]]"`.

### Новая запчасть
Шаблон **Part_Catalog** — спросит OEM-номер, цену, поставщика. После замены детали добавь в Maintenance_Log поле `parts_used: ["[[ссылка на эту запчасть]]"]`.

### Правила консистентности
- **Все даты — `YYYY-MM-DD`**. Без них Dataview не отсортирует.
- **Все суммы — в рублях, в полях с суффиксом `_rub`**. Без единицы Dataview не суммирует.
- **Связи — через `[[wiki-links]]` в массивах**. Это даёт обратные ссылки и граф.
- **Status — только из enum**: `open|diagnosing|waiting_parts|resolved|wontfix` для проблем, `planned|in_progress|done|cancelled` для ТО.
- **Каждая запись содержит `vehicle: "[[Car_Mitsubishi_Mirage_1999]]"`** — это позволит фильтровать, если когда-нибудь добавишь второй автомобиль.

---

## Этап 4: Готовые отчёты (Dataview)

В папке `99_Dataview/`:

- **Расходы_за_год.md** — таблица + сумма затрат по типам работ за 365 дней.
- **Открытые_проблемы.md** — все `status: open|diagnosing|waiting_parts`, отсортированные по серьёзности.
- **График_замен_масла.md** — история замен масла + интервалы (км/дни) между ними.

Можно копировать запросы оттуда в свои дашборды.

---

## Известные ограничения

- Service manual двухколоночный — иногда фразы из соседних колонок «слипаются». Текст всё равно читаем для LLM-ассистента; для точного цитирования есть `page_range`, а PDF лежит рядом.
- 6 PDF без текста (HVAC, Wiring 90 Circuit diagrams, Component Locations) пропущены — там только графика. Если нужно — конвертируй их в PNG-страницы и встраивай как `![[diagram.png]]`.
- Шаблонные опечатки исходного PDF (типа `Cvlinder` вместо `Cylinder`) сохраняются — это ОCR-артефакт самого мануала.

---

## Перезапуск конвертации

Безопасно: каждый запуск пишет в `vault/00_Manual/` поверх. Если хочешь полностью пересобрать:

```bash
rm -rf vault/00_Manual/Volume_1_Engine vault/00_Manual/Volume_2_Chassis vault/00_Manual/Wiring_Diagrams
python -m pdf_to_md --src "Mirage_1999_Service_Manual" --out "vault/00_Manual"
```
