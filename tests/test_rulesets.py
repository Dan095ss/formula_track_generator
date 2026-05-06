"""Tests for track standards and rule sets."""
import pytest
from f1_track.rules import RuleSet, SegmentType, create_ruleset_f1_grade1, create_ruleset_karting_cik


class TestRuleSetBasics:
    """Test RuleSet creation and validation."""

    def test_f1_grade1_preset(self):
        """F1 Grade 1 RuleSet should have correct length and width constraints."""
        ruleset = create_ruleset_f1_grade1()
        assert ruleset.track_length_min == 3500
        assert ruleset.track_length_max == 7000
        assert ruleset.track_width_min == 12
        assert ruleset.track_width_max == 15
        assert ruleset.first_corner_radius_max == 300
        assert ruleset.min_corner_radius == 45

    def test_karting_cik_preset(self):
        """CIK-FIA Karting RuleSet should have appropriate constraints."""
        ruleset = create_ruleset_karting_cik()
        assert ruleset.track_length_min == 1000
        assert ruleset.track_length_max == 2500
        assert ruleset.track_width_min == 7
        assert ruleset.track_width_max == 10
        assert ruleset.min_corner_radius == 25

    def test_ruleset_constraints_invalid(self):
        """RuleSet should reject invalid constraints (length_min >= length_max)."""
        with pytest.raises(ValueError):
            RuleSet(
                track_length_min=7000,
                track_length_max=3500,  # Invalid: min > max
                track_width_min=12,
                track_width_max=15,
                first_corner_radius_max=300,
                min_corner_radius=45,
                max_elevation_change=100,
                max_banking_degrees=10,
                runoff_width_min=10,
                allowed_segments=[SegmentType.STRAIGHT],
                avg_speed_target_kmh=200,
                max_drs_zones=2,
            )

    def test_segment_types_f1(self):
        """F1 Grade 1 should have all standard segment types."""
        ruleset = create_ruleset_f1_grade1()
        expected_segments = {
            SegmentType.STRAIGHT,
            SegmentType.HAIRPIN,
            SegmentType.CHICANE,
            SegmentType.ESSES,
            SegmentType.HIGH_SPEED_TURN,
            SegmentType.PARABOLICA,
        }
        assert expected_segments.issubset(set(ruleset.allowed_segments))

    def test_segment_types_karting(self):
        """Karting should support all segment types."""
        ruleset = create_ruleset_karting_cik()
        # Karting should also have most types (more restricted track)
        assert SegmentType.STRAIGHT in ruleset.allowed_segments
        assert SegmentType.HAIRPIN in ruleset.allowed_segments
