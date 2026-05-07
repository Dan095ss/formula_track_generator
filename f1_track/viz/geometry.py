"""Track centerline geometry: dense XY coordinates with curvature and elevation."""
from dataclasses import dataclass
import numpy as np


@dataclass
class TrackGeometry:
    """Dense centerline geometry of a track.

    All arrays have the same length N (number of sample points).
    segment_boundaries are indices into these arrays where segments start/end.
    """
    x: np.ndarray
    y: np.ndarray
    s: np.ndarray
    heading: np.ndarray
    curvature: np.ndarray
    elevation: np.ndarray
    segment_labels: list[str]
    segment_boundaries: np.ndarray


def build_centerline(segments, ds_default: float = 2.0) -> TrackGeometry:
    """Walk segment list, chain samples into global XY frame.

    Args:
        segments: ordered list of Segment instances.
        ds_default: fallback sample spacing in metres.

    Returns:
        TrackGeometry with all arrays in a consistent global XY frame.
    """
    if not segments:
        raise ValueError("build_centerline requires at least one segment")

    xs_list, ys_list, headings_list, curv_list, s_list = [], [], [], [], []
    labels: list[str] = []
    boundaries: list[int] = [0]

    x_offset, y_offset, s_offset = 0.0, 0.0, 0.0
    accumulated_heading = 0.0
    point_count = 0

    for seg_idx, seg in enumerate(segments):
        sample = seg.sample(accumulated_heading, ds_default=ds_default)
        local_x = sample["x"]
        local_y = sample["y"]
        local_heading = sample["heading"]
        local_curvature = sample["curvature"]
        local_s = sample["s_local"]

        # First segment includes its start; later segments skip
        # their first sample (it equals the previous segment's endpoint).
        start_idx = 0 if seg_idx == 0 else 1
        if start_idx == 1 and len(local_x) <= 1:
            continue

        xs_list.append(local_x[start_idx:] + x_offset)
        ys_list.append(local_y[start_idx:] + y_offset)
        headings_list.append(local_heading[start_idx:])
        curv_list.append(local_curvature[start_idx:])
        s_list.append(local_s[start_idx:] + s_offset)

        added = len(local_x) - start_idx
        labels.extend([type(seg).__name__] * added)
        point_count += added
        boundaries.append(point_count - 1)

        ex, ey, end_heading = seg.end_point(accumulated_heading)
        x_offset += ex
        y_offset += ey
        s_offset += seg.length()
        accumulated_heading = end_heading

    x = np.concatenate(xs_list)
    y = np.concatenate(ys_list)
    heading = np.concatenate(headings_list)
    curvature = np.concatenate(curv_list)
    s = np.concatenate(s_list)

    return TrackGeometry(
        x=x,
        y=y,
        s=s,
        heading=heading,
        curvature=curvature,
        elevation=np.zeros_like(s),
        segment_labels=labels,
        segment_boundaries=np.array(boundaries, dtype=int),
    )
