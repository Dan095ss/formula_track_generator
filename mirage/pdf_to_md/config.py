"""Static config: chapter codes, volume layout, file-naming rules."""

from __future__ import annotations

import re
from dataclasses import dataclass

VEHICLE_LINK = "[[Car_Mitsubishi_Mirage_1999]]"

CHAPTER_TITLES_RU: dict[str, str] = {
    "00":  "Общая информация",
    "00E": "Общая электрика",
    "11A": "Двигатель 1.5L",
    "11B": "Двигатель 1.5L — капремонт",
    "11C": "Двигатель 1.8L",
    "11D": "Двигатель 1.8L — капремонт",
    "12":  "Смазка двигателя",
    "13A": "MFI 1.5L (впрыск)",
    "13B": "MFI 1.8L (впрыск)",
    "13C": "Топливная система",
    "14":  "Охлаждение двигателя",
    "15":  "Впуск и выпуск",
    "16":  "Электрика двигателя",
    "17":  "Двигатель и контроль выбросов",
    "21A": "Сцепление",
    "21B": "Сцепление — капремонт",
    "22A": "Механическая трансмиссия",
    "22B": "МКПП — капремонт",
    "23A": "Автоматическая трансмиссия",
    "23B": "АКПП — капремонт",
    "26":  "Передний мост",
    "27":  "Задний мост",
    "31":  "Колёса и шины",
    "32":  "Опоры силового агрегата",
    "33A": "Передняя подвеска",
    "34":  "Задняя подвеска",
    "35A": "Тормозная система (основа)",
    "35B": "Антиблокировочная система (ABS)",
    "36":  "Стояночный тормоз",
    "37A": "Рулевое управление",
    "42":  "Кузов",
    "51":  "Экстерьер",
    "52A": "Интерьер",
    "52B": "SRS (подушки безопасности)",
    "54":  "Электрика шасси",
    "55":  "HVAC (отопитель/кондиционер)",
    "70":  "Расположение компонентов",
    "80A": "Схемы конфигурации",
    "80B": "Расположение сростков",
    "90":  "Принципиальные схемы",
}

VOLUME_DIR_NAMES: dict[str, str] = {
    "Volume 1":        "Volume_1_Engine",
    "volume 2":        "Volume_2_Chassis",
    "Wiring Diagrams": "Wiring_Diagrams",
}

CHAPTER_CODE_RE = re.compile(r"^([0-9]{2}[A-Z]?)\s+(.*?)\.pdf$", re.IGNORECASE)


@dataclass(frozen=True)
class PdfTarget:
    """A single source PDF + how to address it in the vault."""
    volume: str
    volume_slug: str
    file_name: str
    chapter_code: str
    chapter_title_en: str
    chapter_title_ru: str

    @property
    def out_subdir(self) -> str:
        return f"{self.volume_slug}/{self.chapter_code}_{slugify(self.chapter_title_en)}"


def parse_pdf_filename(volume: str, file_name: str) -> PdfTarget | None:
    m = CHAPTER_CODE_RE.match(file_name)
    if not m:
        return PdfTarget(
            volume=volume,
            volume_slug=VOLUME_DIR_NAMES.get(volume, slugify(volume)),
            file_name=file_name,
            chapter_code="",
            chapter_title_en=file_name.removesuffix(".pdf"),
            chapter_title_ru=file_name.removesuffix(".pdf"),
        )
    code, title_en = m.group(1).upper(), m.group(2).strip()
    return PdfTarget(
        volume=volume,
        volume_slug=VOLUME_DIR_NAMES.get(volume, slugify(volume)),
        file_name=file_name,
        chapter_code=code,
        chapter_title_en=title_en,
        chapter_title_ru=CHAPTER_TITLES_RU.get(code, title_en),
    )


_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(text: str) -> str:
    out = _SLUG_RE.sub("_", text).strip("_")
    return out or "untitled"
