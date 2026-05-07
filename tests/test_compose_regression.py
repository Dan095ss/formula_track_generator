"""Pre-refactor regression baseline for TrackComposer.compose()."""
import numpy as np
import pytest
from f1_track.generate import GenParams, Mode, TrackComposer
from f1_track.rules import create_ruleset_f1_grade1


def _aggregates(track):
    return (
        track.total_length,
        track.avg_width,
        track.first_corner_radius,
        track.min_corner_radius,
        track.max_elevation_change,
        track.max_banking_deg,
    )


class TestComposeRegressionDemo:
    def test_demo_unchanged(self):
        params = GenParams(mode=Mode.DEMO, ruleset_name="f1_grade1")
        composer = TrackComposer()
        track = composer.compose(params, create_ruleset_f1_grade1())
        assert track.total_length == pytest.approx(5493.14, abs=0.5)
        assert 12.0 <= track.avg_width <= 15.0


class TestComposeRegressionAuto:
    def test_auto_seeded_reproducible(self):
        np.random.seed(123)
        params = GenParams(mode=Mode.AUTO, ruleset_name="f1_grade1", difficulty="medium")
        composer = TrackComposer()
        ruleset = create_ruleset_f1_grade1()
        t1 = composer.compose(params, ruleset)

        np.random.seed(123)
        t2 = composer.compose(params, ruleset)
        assert _aggregates(t1) == _aggregates(t2)


class TestComposeRegressionManual:
    def test_manual_seeded_reproducible(self):
        np.random.seed(456)
        params = GenParams(
            mode=Mode.MANUAL,
            ruleset_name="f1_grade1",
            target_length=5500.0,
            sector_count=3,
            segment_preferences={"straight": 0.4, "hairpin": 0.2, "chicane": 0.4},
            elevation_style="hilly",
        )
        composer = TrackComposer()
        ruleset = create_ruleset_f1_grade1()
        t1 = composer.compose(params, ruleset)

        np.random.seed(456)
        t2 = composer.compose(params, ruleset)
        assert _aggregates(t1) == _aggregates(t2)
