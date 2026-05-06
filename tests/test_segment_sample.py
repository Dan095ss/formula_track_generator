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
