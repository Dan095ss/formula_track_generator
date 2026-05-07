"""Tests for Segment._build_curves and Segment.sample()."""
import numpy as np
import pytest
from f1_track.geometry import (
    Curve, Line, CircularArc, ClothoidCurve,
    Straight, CircularTurn, Parabolica, BlindCrest,
    OffCamber, TighteningRadius,
    Hairpin, HighSpeedTurn, Chicane, Esses,
)


def _chain_endpoints(curves, initial_heading):
    """Chain curve endpoints; returns (x, y, heading) at end."""
    x, y, h = 0.0, 0.0, initial_heading
    for c in curves:
        cx, cy, ch = c.point(c.arc_length())
        x += cx
        y += cy
        h = ch
    return x, y, h


class TestBuildCurvesContract:
    """_build_curves must reconstruct the same end_point as the existing impl."""

    def _check_segment(self, seg, heading=0.0, tol=1e-6):
        curves = seg._build_curves(heading)
        assert len(curves) >= 1
        for c in curves:
            assert isinstance(c, Curve)
        x_ref, y_ref, h_ref = seg.end_point(heading)
        x_chain, y_chain, h_chain = _chain_endpoints(curves, heading)
        assert abs(x_ref - x_chain) < tol
        assert abs(y_ref - y_chain) < tol
        assert abs(h_ref - h_chain) < tol


class TestStraight(TestBuildCurvesContract):
    def test_build_curves_matches_endpoint(self):
        self._check_segment(Straight(300.0), heading=0.5)

    def test_build_curves_returns_one_line(self):
        seg = Straight(300.0)
        curves = seg._build_curves(0.0)
        assert len(curves) == 1
        assert isinstance(curves[0], Line)
        assert curves[0].arc_length() == 300.0


class TestCircularTurn(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(CircularTurn(150.0, np.pi / 4), heading=0.0)
        self._check_segment(CircularTurn(80.0, -np.pi / 3), heading=1.2)

    def test_returns_one_arc(self):
        seg = CircularTurn(150.0, np.pi / 4)
        curves = seg._build_curves(0.5)
        assert len(curves) == 1
        assert isinstance(curves[0], CircularArc)
        assert curves[0].R == 150.0


class TestParabolica(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(Parabolica(400.0), heading=0.3)


class TestOffCamber(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(OffCamber(220.0, 150.0, 100.0), heading=-0.4)


class TestBlindCrest(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(BlindCrest(150.0, 100.0), heading=0.0)


class TestTighteningRadius(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(TighteningRadius(200.0, 0.001), heading=0.2)


class TestHairpin(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(Hairpin(60.0, 0.001), heading=0.0)
        self._check_segment(Hairpin(70.0, 0.0008), heading=1.5)

    def test_three_curves(self):
        seg = Hairpin(60.0, 0.001)
        curves = seg._build_curves(0.0)
        assert len(curves) == 3
        assert isinstance(curves[0], ClothoidCurve)
        assert isinstance(curves[1], CircularArc)
        assert isinstance(curves[2], ClothoidCurve)


class TestHighSpeedTurn(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(HighSpeedTurn(300.0, 0.0001), heading=0.0)
        self._check_segment(HighSpeedTurn(250.0, 0.0001), heading=-0.7)


class TestChicane(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(Chicane(80.0, num_turns=2), heading=0.0)
        self._check_segment(Chicane(100.0, num_turns=3), heading=0.4)

    def test_curve_count(self):
        seg = Chicane(80.0, num_turns=2)
        assert len(seg._build_curves(0.0)) == 4  # 2 turns × 2 arcs


class TestEsses(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(Esses(120.0), heading=0.0)
        self._check_segment(Esses(80.0), heading=-1.0)

    def test_three_arcs(self):
        seg = Esses(100.0)
        assert len(seg._build_curves(0.0)) == 3


class TestSampleStraight:
    def test_sample_starts_at_origin(self):
        seg = Straight(100.0)
        s = seg.sample(initial_heading=0.0)
        assert s["x"][0] == pytest.approx(0.0)
        assert s["y"][0] == pytest.approx(0.0)
        assert s["s_local"][0] == pytest.approx(0.0)

    def test_sample_ends_at_endpoint(self):
        seg = Straight(100.0)
        ex, ey, eh = seg.end_point(0.5)
        s = seg.sample(initial_heading=0.5)
        assert s["x"][-1] == pytest.approx(ex, abs=1e-6)
        assert s["y"][-1] == pytest.approx(ey, abs=1e-6)
        assert s["heading"][-1] == pytest.approx(eh, abs=1e-6)
        assert s["s_local"][-1] == pytest.approx(100.0, abs=1e-6)

    def test_sample_curvature_zero_for_straight(self):
        seg = Straight(100.0)
        s = seg.sample(initial_heading=0.0)
        assert np.allclose(s["curvature"], 0.0)

    def test_sample_uses_large_ds_for_line(self):
        seg = Straight(100.0)
        s = seg.sample(initial_heading=0.0)
        # ds=10m → ~11 points for 100m line
        assert len(s["x"]) <= 12
        assert len(s["x"]) >= 5


class TestSampleCircularTurn:
    def test_sample_curvature_constant(self):
        R = 150.0
        seg = CircularTurn(R, np.pi / 2)
        s = seg.sample(initial_heading=0.0)
        assert np.allclose(np.abs(s["curvature"]), 1.0 / R, atol=1e-9)

    def test_sample_endpoint_matches(self):
        seg = CircularTurn(150.0, np.pi / 2)
        ex, ey, eh = seg.end_point(0.0)
        s = seg.sample(initial_heading=0.0)
        assert s["x"][-1] == pytest.approx(ex, abs=1e-4)
        assert s["y"][-1] == pytest.approx(ey, abs=1e-4)
        assert s["heading"][-1] == pytest.approx(eh, abs=1e-4)

    def test_sample_dense_for_arc(self):
        seg = CircularTurn(150.0, np.pi / 2)
        s = seg.sample(initial_heading=0.0)
        # ds=1m → many points
        assert len(s["x"]) >= 100


class TestSampleHairpin:
    def test_curvature_starts_at_zero(self):
        seg = Hairpin(60.0, 0.001)
        s = seg.sample(initial_heading=0.0)
        assert s["curvature"][0] == pytest.approx(0.0, abs=1e-9)

    def test_curvature_max_in_middle(self):
        seg = Hairpin(60.0, 0.001)
        s = seg.sample(initial_heading=0.0)
        assert np.max(np.abs(s["curvature"])) == pytest.approx(1.0 / 60.0, rel=0.01)

    def test_endpoint_matches(self):
        seg = Hairpin(60.0, 0.001)
        ex, ey, eh = seg.end_point(0.4)
        s = seg.sample(initial_heading=0.4)
        assert s["x"][-1] == pytest.approx(ex, abs=1e-3)
        assert s["y"][-1] == pytest.approx(ey, abs=1e-3)


class TestSampleChicane:
    def test_curvature_magnitude_correct(self):
        seg = Chicane(80.0, num_turns=2)
        s = seg.sample(initial_heading=0.0)
        assert np.allclose(np.abs(s["curvature"]), 1.0 / 80.0, atol=1e-9)

    def test_no_duplicate_points_at_curve_boundaries(self):
        seg = Chicane(80.0, num_turns=2)
        s = seg.sample(initial_heading=0.0)
        deltas = np.diff(s["s_local"])
        assert np.all(deltas > 0)
