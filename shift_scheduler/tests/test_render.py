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
    assert "Смены в месяце" in text or "смен" in text.lower()


def test_render_lines_is_color_free_when_disabled():
    roster = [Analyst("A", Region.WEST, offset=0)]
    sch = generate(roster, 2026, 6)
    lines = render_lines(roster, sch, [], use_color=False)
    assert all("\033[" not in ln for ln in lines)
