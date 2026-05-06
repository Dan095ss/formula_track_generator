"""Tests for track generation parameters."""
import pytest
from f1_track.generate.params import GenParams, Mode


class TestGenParamsDemo:
    """Test DEMO mode for GenParams."""

    def test_gen_params_demo_mode(self):
        """GenParams should accept DEMO mode with minimal configuration."""
        params = GenParams(mode=Mode.DEMO, ruleset_name="f1_grade1")
        assert params.mode == Mode.DEMO
        assert params.ruleset_name == "f1_grade1"


class TestGenParamsAuto:
    """Test AUTO mode for GenParams."""

    def test_gen_params_auto_mode(self):
        """GenParams should accept AUTO mode with difficulty parameter."""
        params = GenParams(
            mode=Mode.AUTO,
            ruleset_name="f1_grade1",
            difficulty="medium"
        )
        assert params.mode == Mode.AUTO
        assert params.difficulty == "medium"
        assert params.ruleset_name == "f1_grade1"


class TestGenParamsManual:
    """Test MANUAL mode for GenParams."""

    def test_gen_params_manual_mode(self):
        """GenParams should accept MANUAL mode with full configuration."""
        params = GenParams(
            mode=Mode.MANUAL,
            ruleset_name="f1_grade1",
            target_length=5500.0,
            sector_count=3,
            segment_preferences={"hairpin": 0.2, "chicane": 0.15},
            elevation_style="hilly",
            difficulty="hard"
        )
        assert params.mode == Mode.MANUAL
        assert params.target_length == 5500.0
        assert params.sector_count == 3
        assert params.segment_preferences == {"hairpin": 0.2, "chicane": 0.15}
        assert params.elevation_style == "hilly"
        assert params.difficulty == "hard"
        assert params.ruleset_name == "f1_grade1"


class TestGenParamsValidation:
    """Test validation rules for different modes."""

    def test_demo_mode_ignores_optional_fields(self):
        """DEMO mode should not require AUTO/MANUAL fields."""
        params = GenParams(mode=Mode.DEMO, ruleset_name="f1_grade1")
        assert params.difficulty is None
        assert params.target_length is None
        assert params.sector_count is None

    def test_auto_mode_requires_difficulty(self):
        """AUTO mode should require difficulty parameter."""
        with pytest.raises(ValueError, match="difficulty is required for AUTO mode"):
            GenParams(mode=Mode.AUTO, ruleset_name="f1_grade1")

    def test_manual_mode_requires_target_length(self):
        """MANUAL mode should require target_length."""
        with pytest.raises(ValueError, match="target_length is required for MANUAL mode"):
            GenParams(
                mode=Mode.MANUAL,
                ruleset_name="f1_grade1",
                sector_count=3,
                segment_preferences={"hairpin": 0.2},
                elevation_style="hilly"
            )

    def test_manual_mode_requires_sector_count(self):
        """MANUAL mode should require sector_count."""
        with pytest.raises(ValueError, match="sector_count is required for MANUAL mode"):
            GenParams(
                mode=Mode.MANUAL,
                ruleset_name="f1_grade1",
                target_length=5000.0,
                segment_preferences={"hairpin": 0.2},
                elevation_style="hilly"
            )

    def test_manual_mode_requires_segment_preferences(self):
        """MANUAL mode should require segment_preferences."""
        with pytest.raises(ValueError, match="segment_preferences are required for MANUAL mode"):
            GenParams(
                mode=Mode.MANUAL,
                ruleset_name="f1_grade1",
                target_length=5000.0,
                sector_count=3,
                elevation_style="hilly"
            )

    def test_manual_mode_requires_elevation_style(self):
        """MANUAL mode should require elevation_style."""
        with pytest.raises(ValueError, match="elevation_style is required for MANUAL mode"):
            GenParams(
                mode=Mode.MANUAL,
                ruleset_name="f1_grade1",
                target_length=5000.0,
                sector_count=3,
                segment_preferences={"hairpin": 0.2}
            )

    def test_target_length_must_be_positive(self):
        """target_length must be positive when provided."""
        with pytest.raises(ValueError, match="target_length must be positive"):
            GenParams(
                mode=Mode.MANUAL,
                ruleset_name="f1_grade1",
                target_length=-100.0,
                sector_count=3,
                segment_preferences={"hairpin": 0.2},
                elevation_style="hilly"
            )

    def test_sector_count_must_be_positive(self):
        """sector_count must be positive when provided."""
        with pytest.raises(ValueError, match="sector_count must be positive"):
            GenParams(
                mode=Mode.MANUAL,
                ruleset_name="f1_grade1",
                target_length=5000.0,
                sector_count=0,
                segment_preferences={"hairpin": 0.2},
                elevation_style="hilly"
            )

    def test_segment_preferences_values_in_range(self):
        """segment_preferences values must be in [0, 1]."""
        with pytest.raises(ValueError, match="segment_preferences\\[hairpin\\] must be in \\[0, 1\\]"):
            GenParams(
                mode=Mode.MANUAL,
                ruleset_name="f1_grade1",
                target_length=5000.0,
                sector_count=3,
                segment_preferences={"hairpin": 1.5},
                elevation_style="hilly"
            )

    def test_segment_preferences_negative_values(self):
        """segment_preferences values must not be negative."""
        with pytest.raises(ValueError, match="must be in \\[0, 1\\]"):
            GenParams(
                mode=Mode.MANUAL,
                ruleset_name="f1_grade1",
                target_length=5000.0,
                sector_count=3,
                segment_preferences={"hairpin": -0.1},
                elevation_style="hilly"
            )
