"""TrackSession: bundles Track aggregates, segment list, geometry,
speed profile, generation parameters, and seed."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from f1_track.geometry.track import Track
from .geometry import TrackGeometry

if TYPE_CHECKING:
    from f1_track.generate.params import GenParams


@dataclass
class TrackSession:
    """Full result of compose_full: everything needed for viz + export."""

    track: Track
    segments: list
    geometry: TrackGeometry
    speed_profile: dict  # {"speed_kmh", "v_mps", "lap_time_s"}
    seed: int
    params: GenParams
