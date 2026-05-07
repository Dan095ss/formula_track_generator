"""Deterministic pseudo-elevation generation.

Places control points at segment boundaries, biases each by segment
type, interpolates with cubic spline, normalizes into [0, max_change].
"""
import numpy as np
from scipy.interpolate import CubicSpline

from .geometry import TrackGeometry


_TYPE_BIAS = {
    "BlindCrest": 1.0,
    "OffCamber": -0.5,
    "Hairpin": -0.3,
    "Chicane": -0.1,
    "Esses": 0.1,
    "Straight": 0.0,
    "CircularTurn": 0.0,
    "HighSpeedTurn": 0.0,
    "Parabolica": 0.0,
    "TighteningRadius": -0.2,
}


def generate_elevation(segments, geometry: TrackGeometry, max_change: float, seed: int) -> np.ndarray:
    """Generate deterministic pseudo-elevation along the centerline.

    Args:
        segments: list of Segment instances (same order as used for geometry).
        geometry: TrackGeometry from build_centerline.
        max_change: target elevation range (m). Output is in [0, max_change].
        seed: PRNG seed for reproducibility.

    Returns:
        Array of elevations (m), same length as geometry.s.
    """
    if max_change <= 0:
        return np.zeros_like(geometry.s)

    rng = np.random.default_rng(seed)

    cp_s = geometry.s[geometry.segment_boundaries]

    cp_h = np.zeros(len(cp_s))
    for i in range(len(cp_s)):
        biases = []
        if i > 0:
            biases.append(_TYPE_BIAS.get(type(segments[i - 1]).__name__, 0.0))
        if i < len(segments):
            biases.append(_TYPE_BIAS.get(type(segments[i]).__name__, 0.0))
        bias = np.mean(biases) if biases else 0.0
        cp_h[i] = bias + rng.uniform(-0.1, 0.1)

    cp_h[0] = 0.0

    spline = CubicSpline(cp_s, cp_h, bc_type="natural")
    raw = spline(geometry.s)

    raw_min, raw_max = raw.min(), raw.max()
    if raw_max - raw_min < 1e-9:
        return np.zeros_like(geometry.s)
    normalized = (raw - raw_min) / (raw_max - raw_min) * max_change
    return normalized
