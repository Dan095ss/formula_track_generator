"""Tests for Plotly figure builders."""
import numpy as np
import pytest
import plotly.graph_objects as go

from f1_track.generate import GenParams, Mode, TrackComposer
from f1_track.rules import create_ruleset_f1_grade1
from f1_track.viz.plots import (
    build_2d_map_figure,
    build_3d_figure,
    build_speed_profile_figure,
    build_curvature_profile_figure,
    build_elevation_profile_figure,
    build_segment_breakdown_figure,
)


@pytest.fixture
def session():
    params = GenParams(mode=Mode.DEMO, ruleset_name="f1_grade1")
    return TrackComposer().compose_full(params, create_ruleset_f1_grade1(), seed=42)


class Test2DMap:
    def test_returns_figure(self, session):
        fig = build_2d_map_figure(session.geometry, session.speed_profile)
        assert isinstance(fig, go.Figure)

    def test_data_length_matches_geometry(self, session):
        fig = build_2d_map_figure(session.geometry, session.speed_profile)
        # First trace is the invisible baseline line, second has the colored markers
        trace = fig.data[1]
        assert len(trace.x) == len(session.geometry.x)
        assert len(trace.y) == len(session.geometry.y)


class Test3DFigure:
    def test_returns_figure(self, session):
        fig = build_3d_figure(session.geometry, session.speed_profile)
        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].z) == len(session.geometry.elevation)


class TestProfileFigures:
    def test_speed_profile(self, session):
        fig = build_speed_profile_figure(session.geometry, session.speed_profile)
        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].y) == len(session.speed_profile["speed_kmh"])

    def test_curvature_profile(self, session):
        fig = build_curvature_profile_figure(session.geometry)
        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].y) == len(session.geometry.curvature)

    def test_elevation_profile(self, session):
        fig = build_elevation_profile_figure(session.geometry)
        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].y) == len(session.geometry.elevation)


class TestSegmentBreakdown:
    def test_returns_figure(self, session):
        fig = build_segment_breakdown_figure(session.segments)
        assert isinstance(fig, go.Figure)
        labels = list(fig.data[0].labels)
        assert "Straight" in labels
        assert "Hairpin" in labels
