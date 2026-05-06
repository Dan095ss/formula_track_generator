# Stage 5: Visualization — Design Spec

**Date:** 2026-05-06
**Status:** Draft (awaiting review)
**Beads epic:** CLAUDE-8nt

## Goal

Build a real geometry layer (centerline coordinates, curvature, pseudo-elevation) on top of existing `Track` aggregates, plus an interactive Streamlit application for parameter input and visualization (2D map, 3D view, analysis charts). Stage 5 is the foundation for Stage 6 (Assetto Corsa export).

## Non-Goals

- Real elevation modeling (deferred to Stage 6 with terrain generation)
- AC export formats (`.kn5`, `.ai`) — Stage 6
- Native desktop GUI — out of scope, use Streamlit web UI
- Multi-track comparison view — out of scope for v1

## Architecture

### Data flow

```
GenParams (user input via Streamlit form)
    ↓
TrackComposer.compose_full(params, ruleset, seed)
    ↓
TrackSession
├── track: Track          ← existing aggregates (FIA-validated)
├── segments: list[Segment]  ← previously discarded, now preserved
└── geometry: TrackGeometry
    ├── x[], y[]          ← global XY centerline (m)
    ├── s[]               ← arc length 0..total_length
    ├── heading[]         ← rad, useful for AC export
    ├── curvature[]       ← exact, from curve.curvature_at()
    ├── elevation[]       ← deterministic pseudo-elevation (m)
    ├── segment_labels[]  ← per-point segment-type label
    └── segment_boundaries[] ← indices marking segment transitions
    ↓
LapSimulator.simulate(s, curvature)
    ↓
speed_kmh[], lap_time_s
    ↓
Streamlit app (sidebar form + tabbed visualizations)
```

### Module structure

```
f1_track/
├── geometry/
│   └── segment.py            ← extended with Segment.sample(initial_heading, ds)
├── generate/
│   ├── composer.py           ← refactor: _build_segments + compose_full
│   └── templates.py          ← returns (Track, segments) for DEMO
└── viz/                       ← new package
    ├── __init__.py
    ├── session.py            ← TrackSession dataclass
    ├── geometry.py           ← TrackGeometry + build_centerline
    ├── elevation.py          ← deterministic pseudo-elevation
    ├── plots.py              ← Plotly figure builders (pure functions)
    └── app.py                ← Streamlit entry point
```

## Components

### 1. `Segment.sample(initial_heading, ds)` — geometry/segment.py

Each segment subclass overrides this method to return dense local-frame samples. The method uses each segment's known sub-curve composition and calls existing `Curve.point(s)` and `Curve.curvature_at(s)`.

**Signature:**
```python
def sample(self, initial_heading: float, ds: float = 2.0) -> dict:
    """Sample dense points along this segment.

    Coordinates are relative to the segment's start (origin),
    but rotated to match `initial_heading` — i.e. the same convention
    `Curve.point(s)` already uses. `build_centerline()` only needs to
    translate (not rotate) when chaining segments.

    Returns:
        x, y: arrays of positions in the segment-start frame, headed
              along `initial_heading`.
        heading: array of headings at each sample (rad, absolute).
        curvature: array of curvature values from underlying curves.
        s_local: array of arc lengths within this segment.
    """
```

**Adaptive ds rule** (per sub-curve):
- `Line` → `ds = 10m`
- `CircularArc` → `ds = 1m` (corners need detail)
- `ClothoidCurve` → `ds = 2m` (transition zones)

If a sub-curve is shorter than `ds`, use 2 samples (start, end).

### 2. `build_centerline(segments)` — viz/geometry.py

Walks the segment list, calls `sample()` on each, transforms local frames into the global frame:

```
For each segment:
    1. Get samples from sample(accumulated_heading, ds) — already
       rotated to current heading.
    2. Translate by accumulated_offset (no rotation needed).
    3. Append global (x, y, heading, curvature); s = s_offset + s_local.
    4. Update accumulated_offset and accumulated_heading from
       segment.end_point(accumulated_heading).
```

Returns a `TrackGeometry` dataclass with all arrays plus `segment_labels` and `segment_boundaries` (indices into the arrays).

### 3. `generate_elevation(segments, max_change, seed)` — viz/elevation.py

Generates a deterministic pseudo-elevation profile:

1. Place control points at segment boundaries.
2. Bias each control point by segment-type:
   - `BlindCrest` → +max_change
   - `OffCamber` → -max_change × 0.5
   - `Hairpin` → -max_change × 0.3 (typical valley)
   - `Straight`, others → small random ±max_change × 0.1
3. Use cubic spline interpolation across `s` array.
4. Normalize to fit within `[0, max_change]`.
5. Seed RNG with hash of GenParams + caller-provided seed → reproducibility.

### 4. `TrackSession` — viz/session.py

Plain dataclass tying everything together:
```python
@dataclass
class TrackSession:
    track: Track
    segments: list[Segment]
    geometry: TrackGeometry
    speed_profile: dict  # {"speed_kmh", "v_mps", "lap_time_s"}
    seed: int
    params: GenParams
```

### 5. `TrackComposer.compose_full(params, ruleset, seed)` — generate/composer.py

**Refactor existing code** to expose segments, eliminating the duplicated aggregate calculation between AUTO/MANUAL noted in STAGE4_QUICK_REFERENCE:

- Extract `_build_segments(params, ruleset, seed)` from current `_compose_auto`/`_compose_manual`.
- Extract `_track_from_segments(segments, ruleset, params)` for aggregate calculation.
- `compose()` (existing) calls these and returns just the `Track`.
- New `compose_full()` calls these, additionally builds `TrackGeometry`, runs `LapSimulator`, returns full `TrackSession`.

Existing tests for `compose()` must continue to pass unchanged.

### 6. Plot builders — viz/plots.py

Pure functions, no Streamlit dependencies. Each returns a `plotly.graph_objects.Figure`:

- `build_2d_map_figure(geometry, speeds)` — top-down centerline scatter, colored by speed, hover with (s, speed, segment, curvature).
- `build_3d_figure(geometry, speeds)` — 3D scatter with elevation, rotatable.
- `build_speed_profile_figure(geometry, speeds)` — speed vs s.
- `build_curvature_profile_figure(geometry)` — curvature vs s.
- `build_elevation_profile_figure(geometry)` — elevation vs s.
- `build_segment_breakdown_figure(segments)` — pie chart of segment types.

### 7. Streamlit app — viz/app.py

Single-page application:

**Sidebar:**
- Mode radio (DEMO / AUTO / MANUAL)
- DEMO: no fields
- AUTO: difficulty dropdown
- MANUAL: target_length slider, sector_count slider, segment_preferences sliders, elevation_style dropdown
- Seed input (auto/manual)
- "Generate Track" button

**Main area:**
- Stats bar (always visible): length, lap time, min/max/avg speed, FIA-validation indicators
- Tabs:
  - "Track Map" — 2D visualization
  - "3D View" — 3D rotatable
  - "Analysis" — speed/curvature/elevation subplots + segment breakdown + segment table
- "Export to AC" button (placeholder, raises `NotImplementedError("Stage 6")`)

**State management:**
- `st.session_state["track_session"]` holds last generated `TrackSession`.
- `@st.cache_data` on `compose_full` keyed by `(params_hash, seed)`.

## Error Handling

| Scenario | Behavior |
|---|---|
| FIA validation fails inside `compose_full` | Raise `ValidationError`; Streamlit shows red banner with message |
| MANUAL params out of constraints | Caught at Pydantic-level when form submits; UI shows inline error |
| Track shorter than minimum segment | `compose_full` raises `ValueError("Track too short")` |
| Empty geometry passed to plot builder | Defensive `assert len(geometry.s) > 0`; never reached in normal flow |
| `streamlit` not installed | `app.py` imports inside try/except with friendly "pip install streamlit" message |

## Testing

| File | Coverage |
|---|---|
| `tests/test_geometry_centerline.py` | `Segment.sample()` per type, `build_centerline()` continuity, length, adaptive ds |
| `tests/test_track_session.py` | `compose_full()` for all three modes, geometry/track consistency |
| `tests/test_elevation.py` | Determinism with seed, bounds, BlindCrest peak |
| `tests/test_viz_plots.py` | Figure data length matches geometry, no exceptions on edge cases |
| `tests/test_compose_regression.py` | Existing `compose()` returns identical Track post-refactor |

**Out of scope**: Streamlit UI tests, visual rendering correctness. Smoke test by manual run during verification.

## Dependencies

`pyproject.toml`:
```toml
dependencies = [
    "pydantic>=2.0",
    "scipy>=1.10",
    "numpy>=1.24",
    "matplotlib>=3.8",
    "plotly>=5.17",
    "streamlit>=1.31",  # added
]

[project.scripts]
f1track-app = "f1_track.viz.app:run"  # replaces broken f1track entry
```

## Open Questions / Risks

- **Adaptive ds may produce uneven s spacing** — QSS expects monotonic but not necessarily uniform `s`. Verify `LapSimulator.simulate()` handles non-uniform ds (it uses `np.diff(s)` so should be fine, but test explicitly).
- **Segment.sample() refactor risk** — modifies existing tested files. Mitigate via regression tests (`test_compose_regression.py`) before changing anything.
- **Streamlit on Windows** — first-time install. May surface platform issues; surface early in the implementation plan.

## Implementation Order

1. Add `Segment.sample()` to all 10 segment types (TDD, no behavior change yet).
2. Build `TrackGeometry` + `build_centerline()`.
3. Build `generate_elevation()`.
4. Refactor `TrackComposer` — extract `_build_segments`, `_track_from_segments`, add `compose_full`.
5. Build Plotly figure builders.
6. Build Streamlit app.
7. Update `pyproject.toml`, fix CLI entry.
8. Manual smoke test, verification, push.

Detailed task breakdown will be produced via `superpowers:writing-plans`.
