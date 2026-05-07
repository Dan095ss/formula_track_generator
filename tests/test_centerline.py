"""Tests for TrackGeometry dataclass and build_centerline."""
import numpy as np
import pytest
from f1_track.geometry import Straight, CircularTurn, Hairpin
from f1_track.viz.geometry import TrackGeometry, build_centerline


class TestTrackGeometryDataclass:
    def test_fields_exist(self):
        n = 5
        tg = TrackGeometry(
            x=np.zeros(n),
            y=np.zeros(n),
            s=np.zeros(n),
            heading=np.zeros(n),
            curvature=np.zeros(n),
            elevation=np.zeros(n),
            segment_labels=["Straight"] * n,
            segment_boundaries=np.array([0, n - 1]),
        )
        assert len(tg.x) == n
        assert len(tg.segment_labels) == n


class TestBuildCenterlineBasic:
    def test_single_straight(self):
        seg = Straight(100.0)
        g = build_centerline([seg])
        assert g.x[0] == pytest.approx(0.0)
        assert g.y[0] == pytest.approx(0.0)
        assert g.x[-1] == pytest.approx(100.0)
        assert g.y[-1] == pytest.approx(0.0)
        assert g.s[0] == pytest.approx(0.0)
        assert g.s[-1] == pytest.approx(100.0)

    def test_arc_lengths_match_segment_lengths(self):
        segs = [Straight(100.0), CircularTurn(50.0, np.pi / 2)]
        g = build_centerline(segs)
        total = sum(s.length() for s in segs)
        assert g.s[-1] == pytest.approx(total, abs=1e-6)

    def test_segment_boundaries_align_with_segment_count(self):
        segs = [Straight(100.0), CircularTurn(50.0, np.pi / 2), Straight(80.0)]
        g = build_centerline(segs)
        # 3 segments → 4 boundaries (start, after seg0, after seg1, end)
        assert len(g.segment_boundaries) == 4
        assert g.segment_boundaries[0] == 0
        assert g.segment_boundaries[-1] == len(g.x) - 1

    def test_segment_labels_length_matches_points(self):
        segs = [Straight(100.0), Hairpin(60.0, 0.001)]
        g = build_centerline(segs)
        assert len(g.segment_labels) == len(g.x)
        assert g.segment_labels[0] == "Straight"
        assert g.segment_labels[-1] == "Hairpin"

    def test_elevation_default_zero(self):
        segs = [Straight(100.0)]
        g = build_centerline(segs)
        assert np.allclose(g.elevation, 0.0)
        assert len(g.elevation) == len(g.x)


class TestBuildCenterlineContinuity:
    def test_no_position_jumps_between_segments(self):
        segs = [Straight(100.0), CircularTurn(50.0, np.pi / 2),
                Straight(80.0), Hairpin(60.0, 0.001)]
        g = build_centerline(segs)
        deltas = np.hypot(np.diff(g.x), np.diff(g.y))
        assert deltas.max() < 11.0  # ds=10m on lines, slack for boundary transitions

    def test_s_monotonic_increasing(self):
        segs = [Straight(100.0), CircularTurn(50.0, np.pi / 2)]
        g = build_centerline(segs)
        assert np.all(np.diff(g.s) > 0)
