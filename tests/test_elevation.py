"""Tests for deterministic pseudo-elevation."""
import numpy as np
import pytest
from f1_track.geometry import Straight, BlindCrest, OffCamber, Hairpin
from f1_track.viz.geometry import build_centerline
from f1_track.viz.elevation import generate_elevation


class TestElevationDeterministic:
    def test_same_seed_same_output(self):
        segs = [Straight(100.0), Hairpin(60.0, 0.001), Straight(50.0)]
        g = build_centerline(segs)
        e1 = generate_elevation(segs, g, max_change=50.0, seed=42)
        e2 = generate_elevation(segs, g, max_change=50.0, seed=42)
        assert np.allclose(e1, e2)

    def test_different_seed_different_output(self):
        segs = [Straight(100.0), Hairpin(60.0, 0.001), Straight(50.0)]
        g = build_centerline(segs)
        e1 = generate_elevation(segs, g, max_change=50.0, seed=42)
        e2 = generate_elevation(segs, g, max_change=50.0, seed=43)
        assert not np.allclose(e1, e2)


class TestElevationBounds:
    def test_within_max_change(self):
        segs = [Straight(100.0), BlindCrest(150.0, 100.0), Straight(50.0)]
        g = build_centerline(segs)
        e = generate_elevation(segs, g, max_change=50.0, seed=1)
        assert e.min() >= 0.0
        assert e.max() <= 50.0 + 1e-9

    def test_zero_max_change_returns_zeros(self):
        segs = [Straight(100.0)]
        g = build_centerline(segs)
        e = generate_elevation(segs, g, max_change=0.0, seed=1)
        assert np.allclose(e, 0.0)

    def test_length_matches_geometry(self):
        segs = [Straight(100.0), Hairpin(60.0, 0.001)]
        g = build_centerline(segs)
        e = generate_elevation(segs, g, max_change=30.0, seed=7)
        assert len(e) == len(g.s)


class TestElevationBias:
    def test_blind_crest_creates_high_point(self):
        segs = [Straight(200.0), BlindCrest(150.0, 100.0), Straight(200.0)]
        g = build_centerline(segs)
        peaks_in_crest = 0
        for seed in range(10):
            e = generate_elevation(segs, g, max_change=50.0, seed=seed)
            crest_mask = (g.s >= 200) & (g.s <= 350)
            crest_max = e[crest_mask].max() if crest_mask.any() else 0
            global_max = e.max()
            if abs(crest_max - global_max) < 1.0:
                peaks_in_crest += 1
        assert peaks_in_crest >= 6
