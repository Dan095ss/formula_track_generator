"""Tests for TrackSession dataclass and TrackComposer.compose_full."""
import numpy as np
import pytest
from f1_track.geometry import Track, Straight
from f1_track.generate import GenParams, Mode
from f1_track.viz.geometry import TrackGeometry
from f1_track.viz.session import TrackSession


class TestTrackSessionDataclass:
    def test_construction(self):
        track = Track(
            total_length=100.0,
            avg_width=12.0,
            first_corner_radius=200.0,
            min_corner_radius=50.0,
            max_elevation_change=10.0,
            max_banking_deg=5.0,
        )
        geometry = TrackGeometry(
            x=np.zeros(2), y=np.zeros(2), s=np.array([0.0, 100.0]),
            heading=np.zeros(2), curvature=np.zeros(2), elevation=np.zeros(2),
            segment_labels=["Straight", "Straight"],
            segment_boundaries=np.array([0, 1]),
        )
        params = GenParams(mode=Mode.DEMO, ruleset_name="f1_grade1")
        session = TrackSession(
            track=track,
            segments=[Straight(100.0)],
            geometry=geometry,
            speed_profile={"speed_kmh": np.array([100.0, 200.0]),
                           "v_mps": np.array([27.7, 55.5]),
                           "lap_time_s": 5.0},
            seed=42,
            params=params,
        )
        assert session.track.total_length == 100.0
        assert len(session.segments) == 1
        assert session.seed == 42
        assert session.speed_profile["lap_time_s"] == 5.0


from f1_track.generate import TrackComposer
from f1_track.rules import create_ruleset_f1_grade1
from f1_track.viz import TrackSession


class TestComposeFullDemo:
    def test_returns_track_session(self):
        params = GenParams(mode=Mode.DEMO, ruleset_name="f1_grade1")
        composer = TrackComposer()
        ruleset = create_ruleset_f1_grade1()
        session = composer.compose_full(params, ruleset, seed=42)

        assert isinstance(session, TrackSession)
        assert isinstance(session.geometry, TrackGeometry)
        assert len(session.segments) == 16  # demo has 16 segments
        assert session.seed == 42

    def test_geometry_total_length_matches_track(self):
        params = GenParams(mode=Mode.DEMO, ruleset_name="f1_grade1")
        composer = TrackComposer()
        session = composer.compose_full(params, create_ruleset_f1_grade1(), seed=1)
        assert session.geometry.s[-1] == pytest.approx(session.track.total_length, rel=0.01)

    def test_speed_profile_keys_present(self):
        params = GenParams(mode=Mode.DEMO, ruleset_name="f1_grade1")
        composer = TrackComposer()
        session = composer.compose_full(params, create_ruleset_f1_grade1(), seed=1)
        assert "speed_kmh" in session.speed_profile
        assert "v_mps" in session.speed_profile
        assert "lap_time_s" in session.speed_profile
        assert session.speed_profile["lap_time_s"] > 0


class TestComposeFullSeeded:
    def test_auto_reproducible_with_same_seed(self):
        params = GenParams(mode=Mode.AUTO, ruleset_name="f1_grade1", difficulty="medium")
        composer = TrackComposer()
        ruleset = create_ruleset_f1_grade1()
        s1 = composer.compose_full(params, ruleset, seed=99)
        s2 = composer.compose_full(params, ruleset, seed=99)
        assert s1.track.total_length == s2.track.total_length
        assert np.allclose(s1.geometry.x, s2.geometry.x)

    def test_auto_different_with_different_seed(self):
        params = GenParams(mode=Mode.AUTO, ruleset_name="f1_grade1", difficulty="hard")
        composer = TrackComposer()
        ruleset = create_ruleset_f1_grade1()
        s1 = composer.compose_full(params, ruleset, seed=1)
        s2 = composer.compose_full(params, ruleset, seed=2)
        assert s1.track.total_length != s2.track.total_length or \
               not np.allclose(s1.geometry.x, s2.geometry.x)
