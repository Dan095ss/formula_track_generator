# Stage 5: Visualization — Documentation

## Overview

Stage 5 builds a real geometry layer on top of the Stage 4 parametric generator and exposes it through an interactive Streamlit web application. It is the foundation for Stage 6 (Assetto Corsa export).

**Completed:** 2026-05-07
**Tests:** 77/77 passing
**Entry point:** `streamlit run f1_track/viz/app.py`

---

## What Was Built

### 1. Geometry layer — `f1_track/geometry/segment.py`

Two new capabilities added to every `Segment` subclass:

**`_build_curves(initial_heading) → list[Curve]`**
Returns the ordered list of sub-curves whose chained traversal exactly reproduces the segment's geometry. Used by `sample()` and by the refactored `end_point()`.

**`sample(initial_heading, ds_default=2.0) → dict`**
Dense sampling along all sub-curves with adaptive `ds`:
- `Line` → 10 m per point (straights need fewer points)
- `CircularArc` → 1 m per point (corners need detail for curvature accuracy)
- `ClothoidCurve` → 2 m per point (transition zones)

Returns arrays: `x`, `y`, `heading`, `curvature`, `s_local` — all in the segment-start frame, rotated to match `initial_heading`.

`end_point()` was also refactored into the base class (chains `_build_curves`), eliminating 123 lines of duplicated logic across 10 subclasses.

---

### 2. `TrackGeometry` + `build_centerline` — `f1_track/viz/geometry.py`

```python
@dataclass
class TrackGeometry:
    x: np.ndarray          # global X positions (m)
    y: np.ndarray          # global Y positions (m)
    s: np.ndarray          # arc length 0..total_length (m)
    heading: np.ndarray    # tangent angle (rad)
    curvature: np.ndarray  # exact κ = 1/R from curve.curvature_at(s)
    elevation: np.ndarray  # pseudo-elevation (m), filled by generate_elevation
    segment_labels: list[str]     # per-point segment type name
    segment_boundaries: np.ndarray  # indices of segment start/end points
```

`build_centerline(segments)` walks the segment list, calls `seg.sample()` on each, and chains them into the global XY frame by accumulating translations (no redundant rotations — `sample()` already rotates).

---

### 3. `generate_elevation` — `f1_track/viz/elevation.py`

Deterministic pseudo-elevation via cubic spline:

1. Places control points at segment boundaries (indices from `segment_boundaries`).
2. Biases each control point by segment type:
   - `BlindCrest` → +1.0 × max_change (peaks)
   - `OffCamber` → -0.5 × max_change (camber-heavy descents)
   - `Hairpin` → -0.3 × max_change (valley turns)
   - Others → near zero ± small random noise
3. Cubic spline interpolation across all sample points.
4. Normalizes output to `[0, max_change]`.
5. Seeded `numpy.random.default_rng(seed)` → fully reproducible.

---

### 4. `TrackSession` — `f1_track/viz/session.py`

```python
@dataclass
class TrackSession:
    track: Track            # FIA-validated aggregates
    segments: list          # ordered Segment instances
    geometry: TrackGeometry # dense centerline arrays
    speed_profile: dict     # {"speed_kmh", "v_mps", "lap_time_s"}
    seed: int
    params: GenParams
```

---

### 5. `TrackComposer.compose_full()` — `f1_track/generate/composer.py`

New public method that returns a full `TrackSession`:

```python
def compose_full(self, params: GenParams, ruleset: RuleSet, seed: int = 0) -> TrackSession:
    np.random.seed(seed)
    segments = self._build_segments(params, ruleset)
    track = self._track_from_segments(segments, ruleset, params)
    geometry = build_centerline(segments)
    geometry.elevation = generate_elevation(segments, geometry,
                                            max_change=track.max_elevation_change,
                                            seed=seed)
    speed_profile = LapSimulator(F1Car()).simulate(geometry.s, geometry.curvature)
    return TrackSession(track, segments, geometry, speed_profile, seed, params)
```

The existing `compose()` method is unchanged — all existing Stage 4 tests still pass.

As part of this, `TrackComposer` was refactored to extract `_build_segments()` and `_track_from_segments()`, eliminating duplicated aggregate-calculation between AUTO and MANUAL modes.

---

### 6. Plotly figure builders — `f1_track/viz/plots.py`

Six pure functions, each returning a `plotly.graph_objects.Figure`. No Streamlit dependency.

| Function | Description |
|---|---|
| `build_2d_map_figure(geometry, speeds)` | Top-down scatter, colored by speed with hover (s, speed, segment, κ) |
| `build_3d_figure(geometry, speeds)` | 3D rotatable scatter with elevation axis |
| `build_speed_profile_figure(geometry, speeds)` | Speed vs arc length |
| `build_curvature_profile_figure(geometry)` | Curvature κ vs arc length |
| `build_elevation_profile_figure(geometry)` | Elevation vs arc length |
| `build_segment_breakdown_figure(segments)` | Donut chart of segment types by length |

---

### 7. Streamlit app — `f1_track/viz/app.py`

**Launch:**
```bash
streamlit run f1_track/viz/app.py
# or after pip install -e .:
f1track-app
```

**Sidebar form:**
- Mode: `DEMO` / `AUTO` / `MANUAL`
- AUTO: difficulty dropdown (easy / medium / hard)
- MANUAL: target_length slider, sector_count slider, segment_preferences sliders (10 types), elevation_style dropdown
- Seed input (0 = random)
- "Generate Track" button

**Main area:**
- Stats bar: length, lap time (M:SS.ss), max/min speed, segment count, FIA Grade 1 badge
- Tabs:
  - **Track Map** — 2D speed-colored scatter
  - **3D View** — rotatable 3D with elevation
  - **Analysis** — speed + elevation + curvature profiles + segment breakdown
- "Export to Assetto Corsa (Stage 6)" button (shows Stage 6 placeholder message)

**Caching:** `@st.cache_data` on `compose_full`, keyed by `(params_dict, seed)` → fast tab switching.

---

## Smoke Test Results

```
length=5535.7m  lap_time=93.78s  segments=16  points=2998  figure_traces=2
```

DEMO track: 5.5 km, 1:33.78 lap time, 2998 centerline sample points.

---

## Files Changed / Created

### Modified
- `f1_track/geometry/segment.py` — `_build_curves()` + `sample()` + refactored `end_point()`
- `f1_track/generate/composer.py` — `_build_segments()` + `_track_from_segments()` + `compose_full()`
- `f1_track/generate/templates.py` — added `create_demo_segments()`
- `pyproject.toml` — added `plotly>=5.17`, `streamlit>=1.31`; fixed CLI entry

### Created
- `f1_track/viz/__init__.py`
- `f1_track/viz/geometry.py` — `TrackGeometry` + `build_centerline`
- `f1_track/viz/elevation.py` — `generate_elevation`
- `f1_track/viz/session.py` — `TrackSession`
- `f1_track/viz/plots.py` — 6 Plotly builders
- `f1_track/viz/app.py` — Streamlit app
- `tests/test_segment_sample.py`
- `tests/test_centerline.py`
- `tests/test_elevation.py`
- `tests/test_track_session.py`
- `tests/test_compose_regression.py`
- `tests/test_viz_plots.py`

---

## Next: Stage 6 — Assetto Corsa Export

Stage 5 `TrackSession` provides everything needed for AC export:
- `geometry.x`, `geometry.y`, `geometry.elevation` → 3D centerline
- `geometry.heading` → tangent directions for road surface normals
- `geometry.s` → arc-length parameterization for `.ai` racing lines
- `segments` → type metadata for surface materials

The Streamlit app already has a placeholder "Export to Assetto Corsa" button that raises `NotImplementedError("Stage 6")`.
