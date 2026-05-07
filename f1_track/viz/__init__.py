"""Visualization layer: geometry, plots, Streamlit app."""
from .geometry import TrackGeometry, build_centerline
from .elevation import generate_elevation
from .session import TrackSession
from .plots import (
    build_2d_map_figure,
    build_3d_figure,
    build_speed_profile_figure,
    build_curvature_profile_figure,
    build_elevation_profile_figure,
    build_segment_breakdown_figure,
)

__all__ = [
    "TrackGeometry", "build_centerline",
    "generate_elevation", "TrackSession",
    "build_2d_map_figure", "build_3d_figure",
    "build_speed_profile_figure", "build_curvature_profile_figure",
    "build_elevation_profile_figure", "build_segment_breakdown_figure",
]
