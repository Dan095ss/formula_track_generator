"""Tests for FIA Appendix O track validation."""
import pytest
import numpy as np
from f1_track.rules import create_ruleset_f1_grade1
from f1_track.geometry.validate import (
    TrackValidator,
    ValidationError,
)
from f1_track.geometry.track import Track


class TestTrackValidator:
    """Test FIA Appendix O track validation."""

    def test_valid_f1_track_passes(self):
        """Valid F1 Grade 1 track should pass all checks."""
        ruleset = create_ruleset_f1_grade1()
        validator = TrackValidator(ruleset)

        # Create a valid track (values within constraints)
        track = Track(
            total_length=5500.0,  # Within 3.5-7 km
            avg_width=13.0,  # Within 12-15 m
            first_corner_radius=250.0,  # < 300 m
            min_corner_radius=60.0,  # > 45 m
            max_elevation_change=80.0,  # < 100 m
            max_banking_deg=10.0,  # < 15°
        )

        # Should not raise
        validator.validate(track)

    def test_track_too_short(self):
        """Track shorter than 3.5 km should fail."""
        ruleset = create_ruleset_f1_grade1()
        validator = TrackValidator(ruleset)

        track = Track(
            total_length=3000.0,  # < 3500 m
            avg_width=13.0,
            first_corner_radius=250.0,
            min_corner_radius=60.0,
            max_elevation_change=80.0,
            max_banking_deg=10.0,
        )

        with pytest.raises(ValidationError, match="length"):
            validator.validate(track)

    def test_track_too_long(self):
        """Track longer than 7 km should fail."""
        ruleset = create_ruleset_f1_grade1()
        validator = TrackValidator(ruleset)

        track = Track(
            total_length=7500.0,  # > 7000 m
            avg_width=13.0,
            first_corner_radius=250.0,
            min_corner_radius=60.0,
            max_elevation_change=80.0,
            max_banking_deg=10.0,
        )

        with pytest.raises(ValidationError, match="length"):
            validator.validate(track)

    def test_track_too_narrow(self):
        """Track narrower than 12 m should fail."""
        ruleset = create_ruleset_f1_grade1()
        validator = TrackValidator(ruleset)

        track = Track(
            total_length=5500.0,
            avg_width=11.0,  # < 12 m
            first_corner_radius=250.0,
            min_corner_radius=60.0,
            max_elevation_change=80.0,
            max_banking_deg=10.0,
        )

        with pytest.raises(ValidationError, match="width"):
            validator.validate(track)

    def test_first_corner_radius_too_tight(self):
        """First corner radius > 300 m should fail."""
        ruleset = create_ruleset_f1_grade1()
        validator = TrackValidator(ruleset)

        track = Track(
            total_length=5500.0,
            avg_width=13.0,
            first_corner_radius=320.0,  # > 300 m
            min_corner_radius=60.0,
            max_elevation_change=80.0,
            max_banking_deg=10.0,
        )

        with pytest.raises(ValidationError, match="First corner"):
            validator.validate(track)

    def test_corner_radius_too_tight(self):
        """Min corner radius < 45 m should fail."""
        ruleset = create_ruleset_f1_grade1()
        validator = TrackValidator(ruleset)

        track = Track(
            total_length=5500.0,
            avg_width=13.0,
            first_corner_radius=250.0,
            min_corner_radius=40.0,  # < 45 m
            max_elevation_change=80.0,
            max_banking_deg=10.0,
        )

        with pytest.raises(ValidationError, match="corner radius"):
            validator.validate(track)

    def test_elevation_change_too_large(self):
        """Elevation change > 100 m should fail."""
        ruleset = create_ruleset_f1_grade1()
        validator = TrackValidator(ruleset)

        track = Track(
            total_length=5500.0,
            avg_width=13.0,
            first_corner_radius=250.0,
            min_corner_radius=60.0,
            max_elevation_change=120.0,  # > 100 m
            max_banking_deg=10.0,
        )

        with pytest.raises(ValidationError, match="elevation"):
            validator.validate(track)

    def test_banking_too_steep(self):
        """Banking > 15° should fail."""
        ruleset = create_ruleset_f1_grade1()
        validator = TrackValidator(ruleset)

        track = Track(
            total_length=5500.0,
            avg_width=13.0,
            first_corner_radius=250.0,
            min_corner_radius=60.0,
            max_elevation_change=80.0,
            max_banking_deg=20.0,  # > 15°
        )

        with pytest.raises(ValidationError, match="banking"):
            validator.validate(track)
