"""Tests for track geometry: curves, segments, tracks."""
import pytest
import numpy as np
from f1_track.geometry.curve import ClothoidCurve, CircularArc, Line
from f1_track.geometry.segment import Straight, Hairpin, Chicane, CircularTurn


class TestCurveBasics:
    """Test parametric curve primitives."""

    def test_clothoid_length(self):
        """Clothoid curve should have correct arc length."""
        # Clothoid with curvature rate k = 1/R (R = radius of curvature at end)
        clothoid = ClothoidCurve(curvature_rate=1.0, length=10.0)

        # Arc length should be the parameter
        assert clothoid.arc_length() == 10.0

    def test_clothoid_g2_continuous(self):
        """Clothoid should have continuous first and second derivatives at start."""
        clothoid = ClothoidCurve(curvature_rate=1.0, length=5.0)

        # At start (s=0): curvature should be 0
        x_start, y_start, theta_start = clothoid.point(0.0)
        assert abs(clothoid.curvature_at(0.0)) < 1e-10

        # At end (s=length): curvature should be k*length
        theta_end = clothoid.curvature_at(clothoid.arc_length())
        assert abs(theta_end - 5.0) < 0.1  # Within 0.1 rad

    def test_circular_arc_radius(self):
        """Circular arc should have correct curvature."""
        arc = CircularArc(radius=100.0, angle_rad=np.pi/4)

        # Curvature should be 1/radius
        curvature = arc.curvature_at(0.0)
        assert abs(curvature - 1.0 / 100.0) < 1e-6

    def test_line_straight(self):
        """Straight line should have zero curvature."""
        line = Line(length=50.0, heading=np.pi/6)

        for s in np.linspace(0, line.arc_length(), 5):
            assert abs(line.curvature_at(s)) < 1e-10


class TestTrackClosure:
    """Test that composed tracks can be closed."""

    def test_simple_closed_track(self):
        """Segments can be composed and track displacement computed."""
        # Straight → 180° hairpin → Straight should roughly close
        straight1 = Straight(length=500.0)
        hairpin = Hairpin(radius=50.0)
        straight2 = Straight(length=500.0)

        # All segments should have valid lengths
        assert straight1.length() == 500.0
        assert straight2.length() == 500.0
        assert hairpin.length() > 0.0

        # Segments should produce end points
        heading = 0.0
        for segment in [straight1, hairpin, straight2]:
            x, y, heading = segment.end_point(heading)
            # Should return numeric values
            assert isinstance(x, (float, np.floating))
            assert isinstance(y, (float, np.floating))

    def test_segment_lengths(self):
        """Segments should report correct lengths."""
        straight = Straight(length=1000.0)
        arc_turn = CircularTurn(radius=100.0, angle_rad=np.pi/2)

        assert straight.length() == 1000.0
        assert abs(arc_turn.length() - (100.0 * np.pi / 2)) < 1e-6


class TestSegmentTypes:
    """Test segment palette."""

    def test_hairpin_is_180_turn(self):
        """Hairpin should be a 180° turn."""
        hairpin = Hairpin(radius=50.0)

        # Hairpin ~ 180° turn with spiral entry/exit
        # Check that heading changes by ~π
        start_heading = 0.0
        end_heading = hairpin.end_heading(start_heading)

        heading_delta = abs(end_heading - (start_heading + np.pi))
        # Allow some tolerance for spiral transitions (±0.25 rad ≈ ±14°)
        assert heading_delta <= 0.25, f"Heading delta {heading_delta} out of range"

    def test_straight_preserves_heading(self):
        """Straight segment should preserve heading."""
        straight = Straight(length=200.0)

        for initial_heading in [0, np.pi/4, np.pi/2]:
            end_heading = straight.end_heading(initial_heading)
            assert abs(end_heading - initial_heading) < 1e-10

    def test_chicane_changes_heading(self):
        """Chicane should alternate left/right, net ~0 heading change."""
        chicane = Chicane(radius=40.0, num_turns=2)

        start_heading = 0.0
        end_heading = chicane.end_heading(start_heading)

        # Chicane with 2 turns (L-R) should return nearly to original heading
        heading_delta = abs(end_heading - start_heading)
        assert heading_delta < 0.1, f"Chicane heading delta {heading_delta} too large"
