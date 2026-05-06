# Stage 5 Visualization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a real geometry layer (centerline, curvature, pseudo-elevation) on top of `Track` aggregates and an interactive Streamlit app to generate and visualize tracks. Foundation for Stage 6 (Assetto Corsa export).

**Architecture:** `Segment.sample()` produces dense local-frame samples → `build_centerline()` chains segments into global XY → `TrackSession(track, segments, geometry)` from `TrackComposer.compose_full()` → Streamlit app renders 2D/3D/Analysis tabs via pure Plotly builders.

**Tech Stack:** Python 3.12, NumPy, SciPy (Fresnel + cubic spline), Plotly, Streamlit, Pydantic, pytest.

**Spec:** `docs/superpowers/specs/2026-05-06-stage5-visualization-design.md`
**Beads epic:** CLAUDE-8nt

---

## Conventions Used in This Plan

- All paths are absolute relative to repo root `C:/Users/Sevryuk.DA/Documents/CLAUDE`.
- Test runner is `pytest` from repo root: `python -m pytest tests/<file>.py::<test> -v`.
- Each task ends with a `bd update <id> --claim` at start and `bd close <id>` after final commit.
- TDD per task: write failing test → run (RED) → implement → run (GREEN) → refactor → commit.
- Commit message convention: `<type>(stage5): <subject>` where type ∈ {feat, refactor, test, fix, docs}.
- **Model strategy:** Tasks 1–11 implementation is mechanical TDD — use Sonnet 4.6. Tasks 12–13 (verification, smoke test) use Opus 4.7 for judgment. Switch with `/model`.

---

## File Structure

**Modified:**
- `f1_track/geometry/segment.py` — add `_build_curves()` per subclass; refactor `end_point()` into base; add `sample()` in base.
- `f1_track/generate/composer.py` — extract `_build_segments()`, `_track_from_segments()`, add `compose_full()`.
- `f1_track/generate/templates.py` — add `create_demo_segments()` returning the segment list, refactor `create_demo_track()` to use it.
- `f1_track/generate/__init__.py` — export `compose_full` (via TrackComposer) and TrackSession.
- `f1_track/geometry/__init__.py` — no change (Segment already exported).
- `pyproject.toml` — add `streamlit>=1.31`; replace `f1track` script with `f1track-app`.

**Created:**
- `f1_track/viz/__init__.py`
- `f1_track/viz/session.py` — `TrackSession` dataclass.
- `f1_track/viz/geometry.py` — `TrackGeometry` dataclass + `build_centerline()`.
- `f1_track/viz/elevation.py` — `generate_elevation()`.
- `f1_track/viz/plots.py` — Plotly figure builders.
- `f1_track/viz/app.py` — Streamlit application + `run()` entry.
- `tests/test_segment_sample.py`
- `tests/test_centerline.py`
- `tests/test_elevation.py`
- `tests/test_track_session.py`
- `tests/test_compose_regression.py`
- `tests/test_viz_plots.py`

---

## Task 1: `Segment._build_curves()` for all segment types

**Goal:** Each `Segment` subclass exposes its sub-curve composition uniformly. This is a refactor preserving existing behavior of `end_point()`.

**Files:**
- Modify: `f1_track/geometry/segment.py`
- Test: `tests/test_segment_sample.py` (new file, used by Tasks 1–3)

**Beads:** `bd create --title="Stage 5 T1: Segment._build_curves" --type=task --priority=2`, then `bd dep add <new-id> CLAUDE-8nt --type parent-child`.

- [ ] **Step 1.1: Add abstract `_build_curves` to `Segment` base + regression test scaffold**

Edit `f1_track/geometry/segment.py`, add to `class Segment`:

```python
class Segment:
    """Base class for track segment (composition of curves)."""

    def length(self) -> float:
        raise NotImplementedError

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        raise NotImplementedError

    def end_heading(self, initial_heading: float) -> float:
        _, _, heading = self.end_point(initial_heading)
        return heading

    def _build_curves(self, initial_heading: float) -> list:
        """Return ordered list of sub-curves (Curve instances) whose
        chained traversal equals this segment's geometry. Each curve's
        initial_heading is set so that chaining tangents continuous.

        Used by sample() and (after Task 2) end_point().
        """
        raise NotImplementedError
```

Create `tests/test_segment_sample.py`:

```python
"""Tests for Segment._build_curves and Segment.sample()."""
import numpy as np
import pytest
from f1_track.geometry import (
    Curve, Line, CircularArc, ClothoidCurve,
    Straight, CircularTurn, Parabolica, BlindCrest,
    OffCamber, TighteningRadius,
    Hairpin, HighSpeedTurn, Chicane, Esses,
)


def _chain_endpoints(curves, initial_heading):
    """Reference: chain curve endpoints; returns (x, y, heading) at end."""
    x, y, h = 0.0, 0.0, initial_heading
    for c in curves:
        cx, cy, ch = c.point(c.arc_length())
        x += cx
        y += cy
        h = ch
    return x, y, h


class TestBuildCurvesContract:
    """_build_curves must reconstruct the same end_point as the existing impl."""

    def _check_segment(self, seg, heading=0.0, tol=1e-6):
        curves = seg._build_curves(heading)
        assert len(curves) >= 1
        for c in curves:
            assert isinstance(c, Curve)
        x_ref, y_ref, h_ref = seg.end_point(heading)
        x_chain, y_chain, h_chain = _chain_endpoints(curves, heading)
        assert abs(x_ref - x_chain) < tol
        assert abs(y_ref - y_chain) < tol
        assert abs(h_ref - h_chain) < tol
```

(Test classes for individual segments are added in subsequent steps.)

- [ ] **Step 1.2: Run scaffolding to confirm collection works**

```
python -m pytest tests/test_segment_sample.py -v --collect-only
```

Expected: collected 0 items (no test methods yet, just helper class). Or 1 item if collector picks up `_check_segment` — doesn't matter, just needs no errors.

- [ ] **Step 1.3: RED — failing test for `Straight._build_curves`**

Append to `tests/test_segment_sample.py`:

```python
class TestStraight(TestBuildCurvesContract):
    def test_build_curves_matches_endpoint(self):
        self._check_segment(Straight(300.0), heading=0.5)

    def test_build_curves_returns_one_line(self):
        seg = Straight(300.0)
        curves = seg._build_curves(0.0)
        assert len(curves) == 1
        assert isinstance(curves[0], Line)
        assert curves[0].arc_length() == 300.0
```

Run:
```
python -m pytest tests/test_segment_sample.py::TestStraight -v
```

Expected: FAIL with `NotImplementedError`.

- [ ] **Step 1.4: GREEN — implement `Straight._build_curves`**

In `f1_track/geometry/segment.py`, add to `class Straight`:

```python
    def _build_curves(self, initial_heading: float) -> list:
        return [Line(self.L, heading=initial_heading)]
```

Run the test from Step 1.3. Expected: PASS.

- [ ] **Step 1.5: RED + GREEN — `CircularTurn`**

Append to `tests/test_segment_sample.py`:

```python
class TestCircularTurn(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(CircularTurn(150.0, np.pi / 4), heading=0.0)
        self._check_segment(CircularTurn(80.0, -np.pi / 3), heading=1.2)

    def test_returns_one_arc(self):
        seg = CircularTurn(150.0, np.pi / 4)
        curves = seg._build_curves(0.5)
        assert len(curves) == 1
        assert isinstance(curves[0], CircularArc)
        assert curves[0].R == 150.0
```

Run, expect FAIL.

In `class CircularTurn`, add:

```python
    def _build_curves(self, initial_heading: float) -> list:
        return [CircularArc(self.R, self.angle, initial_heading=initial_heading)]
```

Run, expect PASS.

- [ ] **Step 1.6: RED + GREEN — `Parabolica` and `OffCamber`**

Append:

```python
class TestParabolica(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(Parabolica(400.0), heading=0.3)


class TestOffCamber(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(OffCamber(220.0, 150.0, 100.0), heading=-0.4)
```

Run, expect FAIL.

In `class Parabolica`:

```python
    def _build_curves(self, initial_heading: float) -> list:
        return [CircularArc(self.R, np.pi / 3, initial_heading=initial_heading)]
```

In `class OffCamber`:

```python
    def _build_curves(self, initial_heading: float) -> list:
        R_avg = (self.R_start + self.R_end) / 2
        angle = self.L / R_avg
        return [CircularArc(R_avg, angle, initial_heading=initial_heading)]
```

Run, expect PASS.

- [ ] **Step 1.7: RED + GREEN — `BlindCrest` and `TighteningRadius`**

Append:

```python
class TestBlindCrest(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(BlindCrest(150.0, 100.0), heading=0.0)


class TestTighteningRadius(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(TighteningRadius(200.0, 0.001), heading=0.2)
```

Run, expect FAIL.

In `class BlindCrest`:

```python
    def _build_curves(self, initial_heading: float) -> list:
        return [Line(self.L, heading=initial_heading)]
```

In `class TighteningRadius`:

```python
    def _build_curves(self, initial_heading: float) -> list:
        return [ClothoidCurve(self.k, self.L, initial_heading=initial_heading)]
```

Run, expect PASS.

- [ ] **Step 1.8: RED + GREEN — `Hairpin`**

Append:

```python
class TestHairpin(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(Hairpin(60.0, 0.001), heading=0.0)
        self._check_segment(Hairpin(70.0, 0.0008), heading=1.5)

    def test_three_curves(self):
        seg = Hairpin(60.0, 0.001)
        curves = seg._build_curves(0.0)
        assert len(curves) == 3
        assert isinstance(curves[0], ClothoidCurve)
        assert isinstance(curves[1], CircularArc)
        assert isinstance(curves[2], ClothoidCurve)
```

Run, expect FAIL.

In `class Hairpin`:

```python
    def _build_curves(self, initial_heading: float) -> list:
        h0 = initial_heading
        entry = ClothoidCurve(self.k, self.L_spiral, initial_heading=h0)
        h1 = entry.point(entry.arc_length())[2]
        arc = CircularArc(self.R, np.pi, initial_heading=h1)
        h2 = arc.point(arc.arc_length())[2]
        exit_spiral = ClothoidCurve(-self.k, self.L_spiral, initial_heading=h2)
        return [entry, arc, exit_spiral]
```

Run, expect PASS.

- [ ] **Step 1.9: RED + GREEN — `HighSpeedTurn`**

Append:

```python
class TestHighSpeedTurn(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(HighSpeedTurn(300.0, 0.0001), heading=0.0)
        self._check_segment(HighSpeedTurn(250.0, 0.0001), heading=-0.7)
```

Run, expect FAIL.

In `class HighSpeedTurn`:

```python
    def _build_curves(self, initial_heading: float) -> list:
        h0 = initial_heading
        entry = ClothoidCurve(self.k, self.L_spiral, initial_heading=h0)
        h1 = entry.point(entry.arc_length())[2]
        arc = CircularArc(self.R, np.pi / 2, initial_heading=h1)
        h2 = arc.point(arc.arc_length())[2]
        exit_spiral = ClothoidCurve(-self.k, self.L_spiral, initial_heading=h2)
        return [entry, arc, exit_spiral]
```

Run, expect PASS.

- [ ] **Step 1.10: RED + GREEN — `Chicane`**

Append:

```python
class TestChicane(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(Chicane(80.0, num_turns=2), heading=0.0)
        self._check_segment(Chicane(100.0, num_turns=3), heading=0.4)

    def test_curve_count(self):
        seg = Chicane(80.0, num_turns=2)
        assert len(seg._build_curves(0.0)) == 4  # 2 turns × 2 arcs
```

Run, expect FAIL.

In `class Chicane`:

```python
    def _build_curves(self, initial_heading: float) -> list:
        curves = []
        heading = initial_heading
        for _ in range(self.turns):
            left = CircularArc(self.R, np.pi / 2, initial_heading=heading)
            heading = left.point(left.arc_length())[2]
            curves.append(left)

            right = CircularArc(self.R, -np.pi / 2, initial_heading=heading)
            heading = right.point(right.arc_length())[2]
            curves.append(right)
        return curves
```

Run, expect PASS.

- [ ] **Step 1.11: RED + GREEN — `Esses`**

Append:

```python
class TestEsses(TestBuildCurvesContract):
    def test_build_curves(self):
        self._check_segment(Esses(120.0), heading=0.0)
        self._check_segment(Esses(80.0), heading=-1.0)

    def test_three_arcs(self):
        seg = Esses(100.0)
        assert len(seg._build_curves(0.0)) == 3
```

Run, expect FAIL.

In `class Esses`:

```python
    def _build_curves(self, initial_heading: float) -> list:
        h = initial_heading
        left = CircularArc(self.R, np.pi / 2, initial_heading=h)
        h = left.point(left.arc_length())[2]
        right = CircularArc(self.R, -np.pi / 2, initial_heading=h)
        h = right.point(right.arc_length())[2]
        left2 = CircularArc(self.R, np.pi / 2, initial_heading=h)
        return [left, right, left2]
```

Run, expect PASS.

- [ ] **Step 1.12: Run all existing tests to confirm no regression**

```
python -m pytest tests/ F1/tests/ -v
```

Expected: all 47 existing tests still PASS, plus all `tests/test_segment_sample.py` tests PASS (~13 new tests).

- [ ] **Step 1.13: Commit**

```
git add f1_track/geometry/segment.py tests/test_segment_sample.py
git commit -m "refactor(stage5): expose Segment._build_curves() per subclass

Each segment now exposes its sub-curve composition uniformly,
preserving end_point() behavior. Foundation for sample() in Task 2.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

`bd close <task-id> --reason "T1 done"`.

---

## Task 2: Refactor `Segment.end_point()` into base class

**Goal:** Eliminate duplicated chain-the-curves logic by computing `end_point()` once in the base class via `_build_curves()`. Subclass overrides removed.

**Files:**
- Modify: `f1_track/geometry/segment.py`

**Beads:** `bd create --title="Stage 5 T2: Refactor end_point into base"` + parent-child to epic + `bd dep add T2 T1` (T2 depends on T1).

- [ ] **Step 2.1: Implement `end_point` in base class**

Edit `Segment` base class (in `f1_track/geometry/segment.py`):

```python
class Segment:
    """Base class for track segment (composition of curves)."""

    def length(self) -> float:
        raise NotImplementedError

    def _build_curves(self, initial_heading: float) -> list:
        raise NotImplementedError

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        x_total, y_total = 0.0, 0.0
        heading = initial_heading
        for curve in self._build_curves(initial_heading):
            cx, cy, heading = curve.point(curve.arc_length())
            x_total += cx
            y_total += cy
        return (x_total, y_total, heading)

    def end_heading(self, initial_heading: float) -> float:
        _, _, heading = self.end_point(initial_heading)
        return heading
```

- [ ] **Step 2.2: Remove subclass `end_point` overrides**

Delete the `end_point()` method from each of: `Straight`, `CircularTurn`, `Hairpin`, `Chicane`, `Esses`, `HighSpeedTurn`, `Parabolica`, `TighteningRadius`, `OffCamber`, `BlindCrest`. Keep `__init__`, `length()`, and `_build_curves()`.

(`BlindCrest`'s `self.line = Straight(length)` field becomes unused — also remove it from `__init__`.)

- [ ] **Step 2.3: Run full test suite**

```
python -m pytest tests/ F1/tests/ -v
```

Expected: all tests PASS (47 existing + Task 1 tests).

- [ ] **Step 2.4: Commit**

```
git add f1_track/geometry/segment.py
git commit -m "refactor(stage5): unify Segment.end_point in base class

Removed 10 redundant end_point overrides. Each subclass now only
defines length() and _build_curves(); base computes end_point by
chaining curves. Resolves Stage 4 review note about logic duplication.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

`bd close <task-id>`.

---

## Task 3: `Segment.sample()` method

**Goal:** Sample dense points along a segment using its sub-curves with adaptive `ds`. Returns arrays in the segment-start frame, rotated by `initial_heading`.

**Files:**
- Modify: `f1_track/geometry/segment.py`
- Test: `tests/test_segment_sample.py`

**Beads:** depends on T1, T2.

- [ ] **Step 3.1: RED — failing test for sample on Straight**

Append to `tests/test_segment_sample.py`:

```python
class TestSampleStraight:
    def test_sample_starts_at_origin(self):
        seg = Straight(100.0)
        s = seg.sample(initial_heading=0.0)
        assert s["x"][0] == pytest.approx(0.0)
        assert s["y"][0] == pytest.approx(0.0)
        assert s["s_local"][0] == pytest.approx(0.0)

    def test_sample_ends_at_endpoint(self):
        seg = Straight(100.0)
        ex, ey, eh = seg.end_point(0.5)
        s = seg.sample(initial_heading=0.5)
        assert s["x"][-1] == pytest.approx(ex, abs=1e-6)
        assert s["y"][-1] == pytest.approx(ey, abs=1e-6)
        assert s["heading"][-1] == pytest.approx(eh, abs=1e-6)
        assert s["s_local"][-1] == pytest.approx(100.0, abs=1e-6)

    def test_sample_curvature_zero_for_straight(self):
        seg = Straight(100.0)
        s = seg.sample(initial_heading=0.0)
        assert np.allclose(s["curvature"], 0.0)

    def test_sample_uses_large_ds_for_line(self):
        seg = Straight(100.0)
        s = seg.sample(initial_heading=0.0)
        # ds=10m → ~11 points for 100m line
        assert len(s["x"]) <= 12
        assert len(s["x"]) >= 5
```

Run:
```
python -m pytest tests/test_segment_sample.py::TestSampleStraight -v
```

Expected: FAIL with `AttributeError` or similar (no `sample` method).

- [ ] **Step 3.2: GREEN — implement `Segment.sample` in base class**

Add to base `Segment` class in `f1_track/geometry/segment.py` (after `end_heading`):

```python
    def sample(self, initial_heading: float, ds_default: float = 2.0) -> dict:
        """Sample dense points along all sub-curves.

        Coordinates are in the segment-start frame, rotated to
        match initial_heading. build_centerline() only needs to
        translate when chaining segments (no extra rotation).

        Returns dict with keys: x, y, heading, curvature, s_local.
        """
        from .curve import Line, CircularArc, ClothoidCurve

        def _ds_for(curve):
            if isinstance(curve, Line):
                return 10.0
            if isinstance(curve, CircularArc):
                return 1.0
            if isinstance(curve, ClothoidCurve):
                return 2.0
            return ds_default

        xs, ys, headings, curvatures, s_globals = [], [], [], [], []
        x_offset, y_offset, s_offset = 0.0, 0.0, 0.0

        for i, curve in enumerate(self._build_curves(initial_heading)):
            L = curve.arc_length()
            ds = _ds_for(curve)
            n = max(2, int(np.ceil(L / ds)) + 1)
            s_local = np.linspace(0.0, L, n)
            # First curve: include all points; later curves skip s=0
            # (it equals previous curve's endpoint).
            start_idx = 0 if i == 0 else 1
            for j in range(start_idx, n):
                cx, cy, ch = curve.point(s_local[j])
                xs.append(cx + x_offset)
                ys.append(cy + y_offset)
                headings.append(ch)
                curvatures.append(curve.curvature_at(s_local[j]))
                s_globals.append(s_local[j] + s_offset)

            ex, ey, _ = curve.point(L)
            x_offset += ex
            y_offset += ey
            s_offset += L

        return {
            "x": np.array(xs),
            "y": np.array(ys),
            "heading": np.array(headings),
            "curvature": np.array(curvatures),
            "s_local": np.array(s_globals),
        }
```

Run Step 3.1's test, expect PASS.

- [ ] **Step 3.3: RED + GREEN — sample on CircularTurn**

Append:

```python
class TestSampleCircularTurn:
    def test_sample_curvature_constant(self):
        R = 150.0
        seg = CircularTurn(R, np.pi / 2)
        s = seg.sample(initial_heading=0.0)
        assert np.allclose(s["curvature"], 1.0 / R, atol=1e-9)

    def test_sample_endpoint_matches(self):
        seg = CircularTurn(150.0, np.pi / 2)
        ex, ey, eh = seg.end_point(0.0)
        s = seg.sample(initial_heading=0.0)
        assert s["x"][-1] == pytest.approx(ex, abs=1e-4)
        assert s["y"][-1] == pytest.approx(ey, abs=1e-4)
        assert s["heading"][-1] == pytest.approx(eh, abs=1e-4)

    def test_sample_dense_for_arc(self):
        seg = CircularTurn(150.0, np.pi / 2)
        s = seg.sample(initial_heading=0.0)
        # ds=1m → ~235 points for 235m arc length
        assert len(s["x"]) >= 100
```

Run, expect PASS (no implementation change needed; the base class handles it).

- [ ] **Step 3.4: RED + GREEN — sample on Hairpin (curvature continuity through clothoid)**

Append:

```python
class TestSampleHairpin:
    def test_curvature_starts_and_ends_at_zero(self):
        seg = Hairpin(60.0, 0.001)
        s = seg.sample(initial_heading=0.0)
        # Entry/exit clothoids guarantee κ=0 at both ends
        assert s["curvature"][0] == pytest.approx(0.0, abs=1e-9)
        assert s["curvature"][-1] == pytest.approx(0.0, abs=1e-9)

    def test_curvature_max_in_middle(self):
        seg = Hairpin(60.0, 0.001)
        s = seg.sample(initial_heading=0.0)
        # Peak curvature should be ~ 1/R within the arc
        assert s["curvature"].max() == pytest.approx(1.0 / 60.0, rel=0.01)

    def test_endpoint_matches(self):
        seg = Hairpin(60.0, 0.001)
        ex, ey, eh = seg.end_point(0.4)
        s = seg.sample(initial_heading=0.4)
        assert s["x"][-1] == pytest.approx(ex, abs=1e-3)
        assert s["y"][-1] == pytest.approx(ey, abs=1e-3)
```

Run, expect PASS.

- [ ] **Step 3.5: RED + GREEN — sample on Chicane (alternating curvature sign)**

Append:

```python
class TestSampleChicane:
    def test_curvature_changes_sign_pattern(self):
        seg = Chicane(80.0, num_turns=2)
        s = seg.sample(initial_heading=0.0)
        # First arc curvature > 0 (left), second < 0 (right)
        # CircularArc.curvature_at returns 1/R always positive (per Stage 1 impl).
        # Verify magnitude: all roughly 1/R = 0.0125
        assert np.all(np.abs(s["curvature"] - 1.0 / 80.0) < 1e-9)

    def test_no_duplicate_points_at_curve_boundaries(self):
        seg = Chicane(80.0, num_turns=2)
        s = seg.sample(initial_heading=0.0)
        # No two consecutive points should be identical
        deltas = np.diff(s["s_local"])
        assert np.all(deltas > 0)
```

Run, expect PASS.

- [ ] **Step 3.6: Commit**

```
git add f1_track/geometry/segment.py tests/test_segment_sample.py
git commit -m "feat(stage5): Segment.sample() with adaptive ds

Dense per-segment sampling using existing curve.point() and
curve.curvature_at(). Adaptive ds: 10m on lines, 1m on arcs,
2m on clothoids. No duplicate points at sub-curve boundaries.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

`bd close <task-id>`.

---

## Task 4: `viz/` package + `TrackGeometry` dataclass

**Goal:** Skeleton for the viz package and the data structure that holds dense geometry arrays.

**Files:**
- Create: `f1_track/viz/__init__.py`, `f1_track/viz/geometry.py`
- Test: `tests/test_centerline.py`

**Beads:** depends on T3.

- [ ] **Step 4.1: Create empty package**

Create `f1_track/viz/__init__.py`:

```python
"""Visualization layer: geometry, plots, Streamlit app."""
from .geometry import TrackGeometry, build_centerline

__all__ = ["TrackGeometry", "build_centerline"]
```

- [ ] **Step 4.2: RED — failing test for TrackGeometry shape**

Create `tests/test_centerline.py`:

```python
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
```

Run:
```
python -m pytest tests/test_centerline.py::TestTrackGeometryDataclass -v
```

Expected: FAIL — module doesn't exist yet.

- [ ] **Step 4.3: GREEN — create `TrackGeometry`**

Create `f1_track/viz/geometry.py`:

```python
"""Track centerline geometry: dense XY coordinates with curvature and elevation."""
from dataclasses import dataclass
import numpy as np


@dataclass
class TrackGeometry:
    """Dense centerline geometry of a track.

    All arrays have the same length N (number of sample points).
    `segment_boundaries` are indices into these arrays where one
    segment ends and the next begins (inclusive of first/last point).
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
    """Walk a list of Segment instances, building global XY centerline.

    Args:
        segments: ordered list of Segment instances.
        ds_default: fallback sample spacing for unknown sub-curves.

    Returns:
        TrackGeometry with elevation initialized to zeros (filled in
        later by generate_elevation).
    """
    raise NotImplementedError("Implemented in Step 4.5")
```

Run Step 4.2's test, expect PASS (only checks dataclass).

- [ ] **Step 4.4: RED — test for `build_centerline` basic shape**

Append to `tests/test_centerline.py`:

```python
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
        # Last point must belong to Hairpin
        assert g.segment_labels[-1] == "Hairpin"

    def test_elevation_default_zero(self):
        segs = [Straight(100.0)]
        g = build_centerline(segs)
        assert np.allclose(g.elevation, 0.0)
        assert len(g.elevation) == len(g.x)
```

Run, expect FAIL with `NotImplementedError`.

- [ ] **Step 4.5: GREEN — implement `build_centerline`**

Replace the `build_centerline` body in `f1_track/viz/geometry.py`:

```python
def build_centerline(segments, ds_default: float = 2.0) -> TrackGeometry:
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
        # their first sample (it equals previous segment's endpoint).
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

        # Update offsets via segment.end_point
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
```

Run Step 4.4's tests, expect PASS.

- [ ] **Step 4.6: RED + GREEN — test continuity (no jumps between segments)**

Append:

```python
class TestBuildCenterlineContinuity:
    def test_no_position_jumps_between_segments(self):
        segs = [Straight(100.0), CircularTurn(50.0, np.pi / 2),
                Straight(80.0), Hairpin(60.0, 0.001)]
        g = build_centerline(segs)
        # Distance between consecutive points should never exceed ds_max=10m
        # (we use 10m on lines, 1m on arcs, 2m on clothoids)
        deltas = np.hypot(np.diff(g.x), np.diff(g.y))
        assert deltas.max() < 11.0  # allow small slack for ds=10m line points

    def test_s_monotonic_increasing(self):
        segs = [Straight(100.0), CircularTurn(50.0, np.pi / 2)]
        g = build_centerline(segs)
        assert np.all(np.diff(g.s) > 0)
```

Run, expect PASS.

- [ ] **Step 4.7: Commit**

```
git add f1_track/viz/__init__.py f1_track/viz/geometry.py tests/test_centerline.py
git commit -m "feat(stage5): TrackGeometry + build_centerline

Walks segment list, chains samples into global XY frame.
Adaptive ds preserved per sub-curve. No duplicate points at
segment boundaries; s monotonic; labels per point.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

`bd close <task-id>`.

---

## Task 5: `generate_elevation()`

**Goal:** Deterministic pseudo-elevation profile via cubic spline through segment-boundary control points biased by segment type.

**Files:**
- Create: `f1_track/viz/elevation.py`
- Test: `tests/test_elevation.py`

**Beads:** depends on T4.

- [ ] **Step 5.1: RED — failing test for elevation determinism**

Create `tests/test_elevation.py`:

```python
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
```

Run:
```
python -m pytest tests/test_elevation.py::TestElevationDeterministic -v
```

Expected: FAIL — module doesn't exist.

- [ ] **Step 5.2: GREEN — implement `generate_elevation`**

Create `f1_track/viz/elevation.py`:

```python
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
        segments: list of Segment instances (same as used to build geometry).
        geometry: TrackGeometry from build_centerline.
        max_change: target elevation range (m). Output is in [0, max_change].
        seed: PRNG seed for reproducibility.

    Returns:
        Array of elevations (m), same length as geometry.s.
    """
    if max_change <= 0:
        return np.zeros_like(geometry.s)

    rng = np.random.default_rng(seed)

    # Control point s positions: segment boundaries.
    cp_s = geometry.s[geometry.segment_boundaries]

    # Bias per control point: average bias of segments adjacent to that boundary.
    cp_h = np.zeros(len(cp_s))
    for i in range(len(cp_s)):
        biases = []
        if i > 0:
            biases.append(_TYPE_BIAS.get(type(segments[i - 1]).__name__, 0.0))
        if i < len(segments):
            biases.append(_TYPE_BIAS.get(type(segments[i]).__name__, 0.0))
        bias = np.mean(biases) if biases else 0.0
        # Mix bias with random jitter ±0.1
        cp_h[i] = bias + rng.uniform(-0.1, 0.1)

    # Anchor: start elevation = 0
    cp_h[0] = 0.0

    spline = CubicSpline(cp_s, cp_h, bc_type="natural")
    raw = spline(geometry.s)

    # Normalize to [0, max_change]
    raw_min, raw_max = raw.min(), raw.max()
    if raw_max - raw_min < 1e-9:
        return np.zeros_like(geometry.s)
    normalized = (raw - raw_min) / (raw_max - raw_min) * max_change
    return normalized
```

Run Step 5.1's tests, expect PASS.

- [ ] **Step 5.3: RED + GREEN — bounds**

Append to `tests/test_elevation.py`:

```python
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
```

Run, expect PASS.

- [ ] **Step 5.4: RED + GREEN — BlindCrest bias detectable**

Append:

```python
class TestElevationBias:
    def test_blind_crest_creates_high_point(self):
        # BlindCrest in middle of straights should produce a local maximum
        # in the normalized profile.
        segs = [Straight(200.0), BlindCrest(150.0, 100.0), Straight(200.0)]
        g = build_centerline(segs)
        # Try several seeds to avoid flakiness on adverse jitter
        peaks_in_crest = 0
        for seed in range(10):
            e = generate_elevation(segs, g, max_change=50.0, seed=seed)
            # Crest spans s ∈ [200, 350]
            crest_mask = (g.s >= 200) & (g.s <= 350)
            crest_max = e[crest_mask].max() if crest_mask.any() else 0
            global_max = e.max()
            if abs(crest_max - global_max) < 1.0:
                peaks_in_crest += 1
        # Most seeds should put the global max within the BlindCrest region
        assert peaks_in_crest >= 6
```

Run, expect PASS.

- [ ] **Step 5.5: Export from `viz` package**

Edit `f1_track/viz/__init__.py`:

```python
"""Visualization layer: geometry, plots, Streamlit app."""
from .geometry import TrackGeometry, build_centerline
from .elevation import generate_elevation

__all__ = ["TrackGeometry", "build_centerline", "generate_elevation"]
```

- [ ] **Step 5.6: Commit**

```
git add f1_track/viz/elevation.py f1_track/viz/__init__.py tests/test_elevation.py
git commit -m "feat(stage5): deterministic pseudo-elevation profile

Cubic spline through segment-boundary control points, biased by
segment type (BlindCrest=peak, OffCamber/Hairpin=valley).
Seeded RNG → reproducible profiles. Output normalized to [0, max].

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

`bd close <task-id>`.

---

## Task 6: `TrackSession` dataclass

**Goal:** Plain container tying Track, segments, geometry, speed profile, params, seed.

**Files:**
- Create: `f1_track/viz/session.py`
- Modify: `f1_track/viz/__init__.py`
- Test: `tests/test_track_session.py`

**Beads:** depends on T5.

- [ ] **Step 6.1: RED — failing test for TrackSession shape**

Create `tests/test_track_session.py`:

```python
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
```

Run:
```
python -m pytest tests/test_track_session.py::TestTrackSessionDataclass -v
```

Expected: FAIL — module doesn't exist.

- [ ] **Step 6.2: GREEN — create `TrackSession`**

Create `f1_track/viz/session.py`:

```python
"""TrackSession: bundles Track aggregates, segment list, geometry,
speed profile, generation parameters, and seed."""
from dataclasses import dataclass

from f1_track.generate.params import GenParams
from f1_track.geometry.track import Track
from .geometry import TrackGeometry


@dataclass
class TrackSession:
    """Full result of compose_full: everything needed for viz + export."""

    track: Track
    segments: list
    geometry: TrackGeometry
    speed_profile: dict  # {"speed_kmh", "v_mps", "lap_time_s"}
    seed: int
    params: GenParams
```

- [ ] **Step 6.3: Export from `viz` package**

Edit `f1_track/viz/__init__.py`:

```python
"""Visualization layer: geometry, plots, Streamlit app."""
from .geometry import TrackGeometry, build_centerline
from .elevation import generate_elevation
from .session import TrackSession

__all__ = ["TrackGeometry", "build_centerline", "generate_elevation", "TrackSession"]
```

Run Step 6.1's test, expect PASS.

- [ ] **Step 6.4: Commit**

```
git add f1_track/viz/session.py f1_track/viz/__init__.py tests/test_track_session.py
git commit -m "feat(stage5): TrackSession dataclass

Container for compose_full: track, segments, geometry,
speed_profile, seed, params.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

`bd close <task-id>`.

---

## Task 7: Refactor `TrackComposer` to expose segments

**Goal:** Extract `_build_segments()` and `_track_from_segments()` from existing `_compose_auto`/`_compose_manual`. Keep `compose()` returning the same `Track` (regression-safe). Eliminate the duplicate aggregate-calculation logic flagged in Stage 4 review.

**Files:**
- Modify: `f1_track/generate/composer.py`
- Modify: `f1_track/generate/templates.py` (split `create_demo_track` into segments + Track)
- Test: `tests/test_compose_regression.py`

**Beads:** depends on T6.

- [ ] **Step 7.1: RED — regression tests pinning current `compose()` output**

Create `tests/test_compose_regression.py`:

```python
"""Pre-refactor regression baseline for TrackComposer.compose()."""
import numpy as np
import pytest
from f1_track.generate import GenParams, Mode, TrackComposer
from f1_track.rules import create_ruleset_f1_grade1


def _aggregates(track):
    return (
        track.total_length,
        track.avg_width,
        track.first_corner_radius,
        track.min_corner_radius,
        track.max_elevation_change,
        track.max_banking_deg,
    )


class TestComposeRegressionDemo:
    def test_demo_unchanged(self):
        params = GenParams(mode=Mode.DEMO, ruleset_name="f1_grade1")
        composer = TrackComposer()
        track = composer.compose(params, create_ruleset_f1_grade1())
        # Pin demo track aggregates: ~5535.7m total
        assert track.total_length == pytest.approx(5535.71, abs=0.5)
        assert 12.0 <= track.avg_width <= 15.0


class TestComposeRegressionAuto:
    def test_auto_seeded_reproducible(self):
        # Use np.random.seed for legacy AUTO/MANUAL (which use np.random)
        np.random.seed(123)
        params = GenParams(mode=Mode.AUTO, ruleset_name="f1_grade1", difficulty="medium")
        composer = TrackComposer()
        ruleset = create_ruleset_f1_grade1()
        t1 = composer.compose(params, ruleset)

        np.random.seed(123)
        t2 = composer.compose(params, ruleset)
        assert _aggregates(t1) == _aggregates(t2)


class TestComposeRegressionManual:
    def test_manual_seeded_reproducible(self):
        np.random.seed(456)
        params = GenParams(
            mode=Mode.MANUAL,
            ruleset_name="f1_grade1",
            target_length=5500.0,
            sector_count=3,
            segment_preferences={"straight": 0.4, "hairpin": 0.2, "chicane": 0.4},
            elevation_style="hilly",
        )
        composer = TrackComposer()
        ruleset = create_ruleset_f1_grade1()
        t1 = composer.compose(params, ruleset)

        np.random.seed(456)
        t2 = composer.compose(params, ruleset)
        assert _aggregates(t1) == _aggregates(t2)
```

Run:
```
python -m pytest tests/test_compose_regression.py -v
```

Expected: all PASS (with current code).

This is a **safety net** for Tasks 7–8; it must keep passing after refactor.

- [ ] **Step 7.2: Commit baseline**

```
git add tests/test_compose_regression.py
git commit -m "test(stage5): regression baseline for TrackComposer.compose()

Pins compose() outputs across DEMO/AUTO/MANUAL pre-refactor.
Must keep passing throughout Tasks 7-8.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

- [ ] **Step 7.3: Refactor `templates.py` — expose segment list**

Replace `f1_track/generate/templates.py`:

```python
"""Demo track templates: ready-made reference tracks."""
import numpy as np
from f1_track.geometry import (
    Track,
    Straight,
    HighSpeedTurn,
    Chicane,
    Esses,
    Hairpin,
    Parabolica,
    TighteningRadius,
    OffCamber,
    BlindCrest,
    CircularTurn,
)


def create_demo_segments() -> list:
    """Return the demo track's 16 segments (all 10 segment types).

    Sequence:
      Straight 500 → HighSpeedTurn R=300 → Straight 300 →
      Chicane(80,2) → Esses(120) → Straight 400 →
      Hairpin R=60 → Straight 300 → Parabolica R=400 →
      TighteningRadius 200 → Straight 250 → OffCamber 220 →
      Straight 300 → BlindCrest 150 → CircularTurn R=150 → Straight 500.

    Total length: ~5535.7 m. F1 Grade 1 compliant.
    """
    return [
        Straight(500.0),
        HighSpeedTurn(300.0, k_entry=0.0001),
        Straight(300.0),
        Chicane(80.0, num_turns=2),
        Esses(120.0),
        Straight(400.0),
        Hairpin(60.0, k_entry=0.001),
        Straight(300.0),
        Parabolica(400.0),
        TighteningRadius(200.0, k_rate=0.0001),
        Straight(250.0),
        OffCamber(220.0, 150.0, 100.0),
        Straight(300.0),
        BlindCrest(150.0, 100.0),
        CircularTurn(150.0, np.pi / 2),
        Straight(500.0),
    ]


def create_demo_track() -> Track:
    """Demo track Track aggregate (F1 Grade 1 compliant)."""
    segments = create_demo_segments()
    total_length = sum(s.length() for s in segments)
    return Track(
        total_length=total_length,
        avg_width=13.5,
        first_corner_radius=300.0,
        min_corner_radius=60.0,  # Hairpin radius
        max_elevation_change=50.0,
        max_banking_deg=10.0,
    )
```

> **Note:** The exact segment parameters above are taken from the existing `templates.py` (verify by `git show 8f68780:f1_track/generate/templates.py`). If any aggregate value drifts, fix the values here, not the test pin.

Run regression tests:
```
python -m pytest tests/test_compose_regression.py -v
```

Expected: all PASS (we did not change `compose()` semantics).

- [ ] **Step 7.4: Refactor `composer.py` — extract helpers**

Replace `f1_track/generate/composer.py` with the version below. The change: extract `_build_segments(params, ruleset)` returning a `list[Segment]`; extract `_track_from_segments(segments, ruleset, params)` for aggregate computation; `_compose_demo`, `_compose_auto`, `_compose_manual` now build segments then call `_track_from_segments`.

```python
"""Track composer: combines parameters and rulesets into ready-made tracks."""
import numpy as np
from f1_track.generate.params import GenParams, Mode
from f1_track.generate.templates import create_demo_segments
from f1_track.geometry.track import Track
from f1_track.geometry import (
    Segment,
    Straight,
    HighSpeedTurn,
    Chicane,
    Esses,
    Hairpin,
    Parabolica,
    TighteningRadius,
    OffCamber,
    BlindCrest,
    CircularTurn,
)
from f1_track.rules import RuleSet


_DIFFICULTY_WEIGHTS = {
    "easy": {"straight": 0.3, "high_speed_turn": 0.3, "circular_turn": 0.2, "parabolica": 0.2},
    "medium": {"straight": 0.2, "circular_turn": 0.2, "high_speed_turn": 0.2,
               "chicane": 0.15, "esses": 0.15, "hairpin": 0.1},
    "hard": {"chicane": 0.2, "hairpin": 0.2, "esses": 0.2,
             "tightening_radius": 0.15, "off_camber": 0.15, "blind_crest": 0.1},
}

_PREF_TO_TYPE = {
    "hairpin": "hairpin",
    "chicane": "chicane",
    "high_speed": "high_speed_turn",
    "straight": "straight",
    "esses": "esses",
    "parabolica": "parabolica",
    "tightening_radius": "tightening_radius",
    "off_camber": "off_camber",
    "blind_crest": "blind_crest",
    "circular_turn": "circular_turn",
}

_ELEVATION_LEN_RANGES = {
    "flat": (150, 400),
    "hilly": (200, 500),
    "mountainous": (300, 600),
}

_ELEVATION_CHANGE_RANGES = {
    "flat": (0, 20),
    "hilly": (40, 60),
    "mountainous": (70, 90),
}


def _make_generators(seg_len_min: float, seg_len_max: float) -> dict:
    return {
        "straight": lambda: Straight(np.random.uniform(seg_len_min, seg_len_max)),
        "high_speed_turn": lambda: HighSpeedTurn(np.random.uniform(200, 350), 0.0001),
        "circular_turn": lambda: CircularTurn(
            np.random.uniform(100, 200), np.random.uniform(np.pi / 6, np.pi / 2)
        ),
        "parabolica": lambda: Parabolica(np.random.uniform(300, 450)),
        "hairpin": lambda: Hairpin(np.random.uniform(50, 80), 0.001),
        "chicane": lambda: Chicane(np.random.uniform(60, 100), num_turns=2),
        "esses": lambda: Esses(np.random.uniform(80, 150)),
        "tightening_radius": lambda: TighteningRadius(np.random.uniform(150, 250), 0.001),
        "off_camber": lambda: OffCamber(
            np.random.uniform(seg_len_min, seg_len_max),
            np.random.uniform(100, 150),
            np.random.uniform(50, 100),
        ),
        "blind_crest": lambda: BlindCrest(
            np.random.uniform(seg_len_min, seg_len_max), np.random.uniform(80, 150)
        ),
    }


def _grow_segments(weights: dict, generators: dict, target_length: float, max_length: float) -> list:
    """Iteratively pick segment types by weight until target_length reached."""
    segments: list[Segment] = []
    current = 0.0
    types = list(weights.keys())
    probs = list(weights.values())

    while current < target_length:
        seg_type = np.random.choice(types, p=probs)
        seg = generators[seg_type]()
        L = seg.length()

        if current + L <= max_length:
            segments.append(seg)
            current += L
        else:
            short = Straight(50.0)
            if current + short.length() <= max_length:
                segments.append(short)
                current += short.length()
            else:
                break

    return segments


def _min_corner_radius(segments: list, fallback: float) -> float:
    r = fallback
    for seg in segments:
        if isinstance(seg, (CircularTurn, HighSpeedTurn, Hairpin, Parabolica, Chicane, Esses, BlindCrest)):
            r = min(r, seg.R)
        elif isinstance(seg, OffCamber):
            r = min(r, seg.R_start, seg.R_end)
        elif isinstance(seg, TighteningRadius):
            # Final radius after clothoid tightening: 1 / (k * L)
            kappa_max = seg.k * seg.L
            if kappa_max > 0:
                r = min(r, 1.0 / kappa_max)
    return r


def _first_corner_radius(segments: list, fallback: float) -> float:
    for seg in segments:
        if isinstance(seg, (CircularTurn, HighSpeedTurn, Hairpin)) and hasattr(seg, "R"):
            return min(seg.R, fallback)
    return fallback


class TrackComposer:
    """Compose Track aggregates (and, via compose_full, full TrackSession)
    from generation parameters and rulesets."""

    def compose(self, params: GenParams, ruleset: RuleSet) -> Track:
        segments = self._build_segments(params, ruleset)
        return self._track_from_segments(segments, ruleset, params)

    def _build_segments(self, params: GenParams, ruleset: RuleSet) -> list:
        if params.mode == Mode.DEMO:
            return create_demo_segments()
        if params.mode == Mode.AUTO:
            difficulty = params.difficulty or "medium"
            weights = _DIFFICULTY_WEIGHTS.get(difficulty, _DIFFICULTY_WEIGHTS["medium"])
            generators = _make_generators(seg_len_min=250.0, seg_len_max=500.0)
            target = ruleset.track_length_min + (ruleset.track_length_max - ruleset.track_length_min) * 0.5
            return _grow_segments(weights, generators, target, ruleset.track_length_max)
        if params.mode == Mode.MANUAL:
            user_prefs = params.segment_preferences or {}
            segment_weights: dict[str, float] = {}
            total = 0.0
            for name, val in user_prefs.items():
                if name in _PREF_TO_TYPE:
                    segment_weights[_PREF_TO_TYPE[name]] = val
                    total += val
            if total > 0:
                segment_weights = {k: v / total for k, v in segment_weights.items()}

            seg_len_min, seg_len_max = _ELEVATION_LEN_RANGES.get(params.elevation_style, (200, 500))
            generators = _make_generators(seg_len_min, seg_len_max)
            target = params.target_length * 0.95
            return _grow_segments(segment_weights, generators, target, ruleset.track_length_max)
        raise ValueError(f"Unknown mode: {params.mode}")

    def _track_from_segments(self, segments: list, ruleset: RuleSet, params: GenParams) -> Track:
        if params.mode == Mode.DEMO:
            # DEMO uses fixed values reflecting the curated track.
            from f1_track.generate.templates import create_demo_track
            return create_demo_track()

        total_length = sum(s.length() for s in segments)
        avg_width = (ruleset.track_width_min + ruleset.track_width_max) / 2

        if params.mode == Mode.MANUAL:
            elev_min, elev_max = _ELEVATION_CHANGE_RANGES.get(params.elevation_style, (40, 60))
            max_elevation = float(np.random.uniform(elev_min, elev_max))
        else:
            max_elevation = ruleset.max_elevation_change * 0.5

        return Track(
            total_length=total_length,
            avg_width=avg_width,
            first_corner_radius=_first_corner_radius(segments, ruleset.first_corner_radius_max),
            min_corner_radius=_min_corner_radius(segments, ruleset.min_corner_radius),
            max_elevation_change=max_elevation,
            max_banking_deg=ruleset.max_banking_degrees * 0.75,
        )
```

> **Behavior parity caveat:** the legacy implementation used `min_corner_radius=ruleset.min_corner_radius` as fallback for `_min_corner_radius`. This is preserved.
> The legacy MANUAL `TighteningRadius` used `final_radius_m`; here we compute `1/(k*L)` which equals `final_radius_m` for the standard clothoid (κ at end = k·L → R = 1/κ). If TighteningRadius has a `final_radius_m` field, prefer using it; otherwise compute. **Verify against existing code** before this step and adjust if `final_radius_m` differs.

- [ ] **Step 7.5: Run all tests**

```
python -m pytest tests/ F1/tests/ -v
```

Expected: all PASS, including:
- `tests/test_compose_regression.py` (4 tests pinning compose())
- `F1/tests/test_generate.py` (Stage 4 tests)
- All Tasks 1–6 tests

If any AUTO/MANUAL test fails because of seeded reproducibility difference, the issue is in `_grow_segments` ordering. Compare with the original `_compose_auto` — operations must be in the same order (np.random.choice → generator → length check → append).

- [ ] **Step 7.6: Commit**

```
git add f1_track/generate/composer.py f1_track/generate/templates.py
git commit -m "refactor(stage5): TrackComposer exposes segments

Extracted _build_segments() and _track_from_segments() from the
mode methods. Eliminated duplicated aggregate-computation block
between AUTO and MANUAL (Stage 4 review item).

create_demo_segments() exposes the demo segment list separately.
Public compose() behavior unchanged (regression tests pinned).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

`bd close <task-id>`.

---

## Task 8: `TrackComposer.compose_full()`

**Goal:** New public method returning `TrackSession` with full geometry, elevation, and speed profile.

**Files:**
- Modify: `f1_track/generate/composer.py`
- Modify: `f1_track/generate/__init__.py`
- Test: `tests/test_track_session.py`

**Beads:** depends on T7.

- [ ] **Step 8.1: RED — failing test for compose_full DEMO**

Append to `tests/test_track_session.py`:

```python
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
        assert np.allclose(s1.geometry.elevation, s2.geometry.elevation)

    def test_auto_different_with_different_seed(self):
        params = GenParams(mode=Mode.AUTO, ruleset_name="f1_grade1", difficulty="hard")
        composer = TrackComposer()
        ruleset = create_ruleset_f1_grade1()
        s1 = composer.compose_full(params, ruleset, seed=1)
        s2 = composer.compose_full(params, ruleset, seed=2)
        # Highly unlikely identical
        assert s1.track.total_length != s2.track.total_length or \
               not np.allclose(s1.geometry.x, s2.geometry.x)
```

Run, expect FAIL (`compose_full` doesn't exist).

- [ ] **Step 8.2: GREEN — implement `compose_full`**

Add imports at top of `f1_track/generate/composer.py`:

```python
from f1_track.viz.geometry import build_centerline
from f1_track.viz.elevation import generate_elevation
from f1_track.viz.session import TrackSession
from f1_track.sim.car import F1Car
from f1_track.sim.qss import LapSimulator
```

Add method to `TrackComposer`:

```python
    def compose_full(self, params: GenParams, ruleset: RuleSet, seed: int = 0) -> TrackSession:
        """Build full TrackSession: track aggregates + geometry + speed profile.

        Args:
            params: GenParams (mode + mode-specific fields).
            ruleset: RuleSet defining FIA constraints.
            seed: PRNG seed; affects AUTO/MANUAL random generation
                  and elevation. DEMO ignores seed for segments
                  (they're fixed) but uses it for elevation.

        Returns:
            TrackSession bundling track, segments, geometry, speed
            profile, seed, and params.
        """
        np.random.seed(seed)
        segments = self._build_segments(params, ruleset)
        track = self._track_from_segments(segments, ruleset, params)

        geometry = build_centerline(segments)
        geometry.elevation = generate_elevation(
            segments, geometry, max_change=track.max_elevation_change, seed=seed
        )

        car = F1Car()
        sim = LapSimulator(car)
        speed_profile = sim.simulate(geometry.s, geometry.curvature)

        return TrackSession(
            track=track,
            segments=segments,
            geometry=geometry,
            speed_profile=speed_profile,
            seed=seed,
            params=params,
        )
```

> **Note:** `np.random.seed(seed)` makes AUTO/MANUAL reproducible. The elevation function takes its own seed; we pass the same value.

- [ ] **Step 8.3: Run new tests + regression**

```
python -m pytest tests/test_track_session.py tests/test_compose_regression.py -v
```

Expected: all PASS.

- [ ] **Step 8.4: Run full test suite**

```
python -m pytest tests/ F1/tests/ -v
```

Expected: all PASS.

- [ ] **Step 8.5: Commit**

```
git add f1_track/generate/composer.py tests/test_track_session.py
git commit -m "feat(stage5): TrackComposer.compose_full → TrackSession

Builds geometry (build_centerline), elevation (generate_elevation),
and speed profile (LapSimulator) on top of compose() pipeline.
Seeded for reproducibility.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

`bd close <task-id>`.

---

## Task 9: Plotly figure builders (2D map + analysis)

**Goal:** Pure functions returning `plotly.graph_objects.Figure` instances. No Streamlit dependency.

**Files:**
- Create: `f1_track/viz/plots.py`
- Modify: `f1_track/viz/__init__.py`
- Test: `tests/test_viz_plots.py`

**Beads:** depends on T8.

- [ ] **Step 9.1: RED — failing test for build_2d_map_figure**

Create `tests/test_viz_plots.py`:

```python
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
        # First trace should be the centerline
        trace = fig.data[0]
        assert len(trace.x) == len(session.geometry.x)
        assert len(trace.y) == len(session.geometry.y)
```

Run, expect FAIL — module doesn't exist.

- [ ] **Step 9.2: GREEN — implement `build_2d_map_figure` (and stubs for others)**

Create `f1_track/viz/plots.py`:

```python
"""Plotly figure builders. Pure functions: TrackGeometry + speed_profile → Figure."""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .geometry import TrackGeometry


def build_2d_map_figure(geometry: TrackGeometry, speed_profile: dict) -> go.Figure:
    """Top-down centerline scatter; line color = speed."""
    speeds = speed_profile["speed_kmh"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=geometry.x,
        y=geometry.y,
        mode="lines",
        line=dict(width=4, color="rgba(0,0,0,0)"),  # invisible base line, marker overlay below
        showlegend=False,
        hoverinfo="skip",
    ))
    # Colored markers for speed
    fig.add_trace(go.Scatter(
        x=geometry.x,
        y=geometry.y,
        mode="markers",
        marker=dict(
            size=4,
            color=speeds,
            colorscale="RdYlGn",
            colorbar=dict(title="Speed (km/h)"),
            showscale=True,
        ),
        text=[
            f"s={s:.0f}m<br>v={v:.1f} km/h<br>{lbl}<br>κ={c:.4f}"
            for s, v, lbl, c in zip(geometry.s, speeds, geometry.segment_labels, geometry.curvature)
        ],
        hoverinfo="text",
        showlegend=False,
    ))
    fig.update_layout(
        title="Track Map (color = speed)",
        xaxis_title="x (m)",
        yaxis_title="y (m)",
        yaxis=dict(scaleanchor="x", scaleratio=1),
        hovermode="closest",
    )
    return fig


def build_3d_figure(geometry: TrackGeometry, speed_profile: dict) -> go.Figure:
    """3D scatter: XY + elevation Z, colored by speed."""
    speeds = speed_profile["speed_kmh"]
    fig = go.Figure(data=[go.Scatter3d(
        x=geometry.x,
        y=geometry.y,
        z=geometry.elevation,
        mode="markers",
        marker=dict(size=2, color=speeds, colorscale="RdYlGn", showscale=True,
                    colorbar=dict(title="Speed (km/h)")),
        text=[f"s={s:.0f}m<br>z={z:.1f}m<br>v={v:.1f} km/h"
              for s, z, v in zip(geometry.s, geometry.elevation, speeds)],
        hoverinfo="text",
    )])
    fig.update_layout(
        title="3D Track View",
        scene=dict(
            xaxis_title="x (m)",
            yaxis_title="y (m)",
            zaxis_title="elevation (m)",
            aspectmode="data",
        ),
    )
    return fig


def build_speed_profile_figure(geometry: TrackGeometry, speed_profile: dict) -> go.Figure:
    fig = go.Figure(data=[go.Scatter(
        x=geometry.s, y=speed_profile["speed_kmh"], mode="lines",
        line=dict(color="firebrick"), name="speed",
    )])
    fig.update_layout(title="Speed vs s", xaxis_title="s (m)", yaxis_title="speed (km/h)")
    return fig


def build_curvature_profile_figure(geometry: TrackGeometry) -> go.Figure:
    fig = go.Figure(data=[go.Scatter(
        x=geometry.s, y=geometry.curvature, mode="lines",
        line=dict(color="steelblue"), name="curvature",
    )])
    fig.update_layout(title="Curvature vs s", xaxis_title="s (m)", yaxis_title="κ (1/m)")
    return fig


def build_elevation_profile_figure(geometry: TrackGeometry) -> go.Figure:
    fig = go.Figure(data=[go.Scatter(
        x=geometry.s, y=geometry.elevation, mode="lines",
        line=dict(color="darkgreen"), name="elevation",
    )])
    fig.update_layout(title="Elevation vs s", xaxis_title="s (m)", yaxis_title="z (m)")
    return fig


def build_segment_breakdown_figure(segments: list) -> go.Figure:
    """Pie chart of segment-type distribution by length."""
    by_type: dict[str, float] = {}
    for seg in segments:
        name = type(seg).__name__
        by_type[name] = by_type.get(name, 0.0) + seg.length()
    fig = go.Figure(data=[go.Pie(
        labels=list(by_type.keys()),
        values=list(by_type.values()),
        hole=0.4,
    )])
    fig.update_layout(title="Segment composition (by length)")
    return fig
```

Run Step 9.1's test, expect PASS.

- [ ] **Step 9.3: RED + GREEN — tests for remaining builders**

Append to `tests/test_viz_plots.py`:

```python
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
        # Demo has all 10 distinct types (Straight appears multiple times → 10 unique)
        labels = list(fig.data[0].labels)
        assert "Straight" in labels
        assert "Hairpin" in labels
```

Run, expect PASS.

- [ ] **Step 9.4: Export from `viz` package**

Edit `f1_track/viz/__init__.py`:

```python
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
```

- [ ] **Step 9.5: Commit**

```
git add f1_track/viz/plots.py f1_track/viz/__init__.py tests/test_viz_plots.py
git commit -m "feat(stage5): Plotly figure builders

Six pure functions for 2D map, 3D view, speed/curvature/elevation
profiles, and segment breakdown pie. Streamlit-independent.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

`bd close <task-id>`.

---

## Task 10: Streamlit app (`viz/app.py`)

**Goal:** Single-page Streamlit app: sidebar form + tabbed visualizations + stats bar. No automated tests; smoke-tested in Task 12.

**Files:**
- Create: `f1_track/viz/app.py`

**Beads:** depends on T9.

- [ ] **Step 10.1: Install streamlit locally (one-time)**

```
pip install streamlit
```

(`pyproject.toml` is updated in Task 11.)

Verify:
```
python -c "import streamlit; print(streamlit.__version__)"
```

Expected: a version string ≥ 1.31.

- [ ] **Step 10.2: Create the app**

Create `f1_track/viz/app.py`:

```python
"""Streamlit application entry point.

Run with: streamlit run f1_track/viz/app.py
Or via console script (after pip install -e .): f1track-app
"""
from __future__ import annotations

import sys

try:
    import streamlit as st
except ImportError:
    print(
        "ERROR: streamlit is not installed.\n"
        "Install with: pip install streamlit\n"
        "Or: pip install -e .",
        file=sys.stderr,
    )
    raise

import numpy as np
from pydantic import ValidationError as PydanticValidationError

from f1_track.generate import GenParams, Mode, TrackComposer
from f1_track.rules import create_ruleset_f1_grade1
from f1_track.geometry.validate import TrackValidator, ValidationError as FIAValidationError
from f1_track.viz import (
    build_2d_map_figure,
    build_3d_figure,
    build_speed_profile_figure,
    build_curvature_profile_figure,
    build_elevation_profile_figure,
    build_segment_breakdown_figure,
)


SEG_PREF_KEYS = ["straight", "high_speed", "hairpin", "chicane", "esses",
                 "parabolica", "tightening_radius", "off_camber", "blind_crest", "circular_turn"]


def _render_sidebar() -> tuple[GenParams, int] | None:
    """Render parameter form. Returns (params, seed) on submit, else None."""
    st.sidebar.header("Track Parameters")
    mode_label = st.sidebar.radio("Mode", ["DEMO", "AUTO", "MANUAL"], index=1)
    mode = Mode[mode_label]

    difficulty = None
    target_length = None
    sector_count = None
    segment_preferences = None
    elevation_style = None

    if mode == Mode.AUTO:
        difficulty = st.sidebar.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
    elif mode == Mode.MANUAL:
        target_length = st.sidebar.slider("Target length (m)", 3500, 7000, 5500, step=100)
        sector_count = st.sidebar.slider("Sector count", 2, 6, 3)
        elevation_style = st.sidebar.selectbox(
            "Elevation style", ["flat", "hilly", "mountainous"], index=1
        )
        st.sidebar.markdown("**Segment preferences (0..1)**")
        segment_preferences = {}
        for key in SEG_PREF_KEYS:
            v = st.sidebar.slider(key, 0.0, 1.0, 0.1 if key != "straight" else 0.3, step=0.05)
            if v > 0:
                segment_preferences[key] = v

    seed_input = st.sidebar.number_input("Seed (0 = random)", min_value=0, max_value=10_000, value=0, step=1)
    seed = int(seed_input) if seed_input != 0 else int(np.random.randint(1, 10_000))

    if st.sidebar.button("Generate Track", type="primary"):
        try:
            params = GenParams(
                mode=mode,
                ruleset_name="f1_grade1",
                difficulty=difficulty,
                target_length=target_length,
                sector_count=sector_count,
                segment_preferences=segment_preferences,
                elevation_style=elevation_style,
            )
            return params, seed
        except PydanticValidationError as e:
            st.sidebar.error(f"Invalid parameters:\n{e}")
            return None
    return None


@st.cache_data(show_spinner=False)
def _generate(_params_dict: dict, seed: int):
    """Cached generation. Cache key is (params dict, seed)."""
    params = GenParams(**_params_dict)
    composer = TrackComposer()
    ruleset = create_ruleset_f1_grade1()
    return composer.compose_full(params, ruleset, seed=seed)


def _render_stats(session) -> None:
    track = session.track
    speeds = session.speed_profile["speed_kmh"]
    lap_time = session.speed_profile["lap_time_s"]
    minutes = int(lap_time // 60)
    seconds = lap_time - minutes * 60
    cols = st.columns(5)
    cols[0].metric("Length (m)", f"{track.total_length:.0f}")
    cols[1].metric("Lap time", f"{minutes}:{seconds:05.2f}")
    cols[2].metric("Max speed", f"{speeds.max():.1f} km/h")
    cols[3].metric("Min speed", f"{speeds.min():.1f} km/h")
    cols[4].metric("Segments", f"{len(session.segments)}")

    # FIA validation badge
    try:
        TrackValidator(create_ruleset_f1_grade1()).validate(track)
        st.success("FIA Grade 1: PASS")
    except FIAValidationError as e:
        st.warning(f"FIA Grade 1: FAIL — {e}")


def _render_tabs(session) -> None:
    tab_map, tab_3d, tab_analysis = st.tabs(["Track Map", "3D View", "Analysis"])
    with tab_map:
        st.plotly_chart(build_2d_map_figure(session.geometry, session.speed_profile),
                        use_container_width=True)
    with tab_3d:
        st.plotly_chart(build_3d_figure(session.geometry, session.speed_profile),
                        use_container_width=True)
    with tab_analysis:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(build_speed_profile_figure(session.geometry, session.speed_profile),
                            use_container_width=True)
            st.plotly_chart(build_elevation_profile_figure(session.geometry),
                            use_container_width=True)
        with col2:
            st.plotly_chart(build_curvature_profile_figure(session.geometry),
                            use_container_width=True)
            st.plotly_chart(build_segment_breakdown_figure(session.segments),
                            use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="F1 Track Generator", layout="wide")
    st.title("F1 Track Generator — Stage 5 Visualization")

    submission = _render_sidebar()
    if submission is not None:
        params, seed = submission
        try:
            session = _generate(params.model_dump(), seed)
            st.session_state["session"] = session
        except FIAValidationError as e:
            st.error(f"Track failed FIA validation: {e}")
            return
        except ValueError as e:
            st.error(f"Generation error: {e}")
            return

    if "session" in st.session_state:
        session = st.session_state["session"]
        _render_stats(session)
        _render_tabs(session)
        st.caption(f"Seed: {session.seed}")

        if st.button("Export to Assetto Corsa (Stage 6)"):
            st.info("Export will be implemented in Stage 6.")
    else:
        st.info("Configure parameters in the sidebar and click Generate Track.")


def run() -> None:
    """Entry point for the `f1track-app` console script.

    Spawns Streamlit on this very file via `streamlit run`.
    """
    import subprocess

    subprocess.run(
        ["streamlit", "run", __file__, "--server.headless=false"],
        check=True,
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 10.3: Manual smoke test**

```
streamlit run f1_track/viz/app.py
```

Expected: browser opens at `http://localhost:8501`, sidebar visible with mode selector. Pick `DEMO`, click `Generate Track`. Within ~5 seconds, see stats bar, three tabs with figures. Try `AUTO` with difficulty `hard`. Then close.

If errors surface, fix before commit. Common failures:
- Missing import → traceback in the terminal where streamlit is running.
- Plotly figure error → check `tests/test_viz_plots.py` passes; the figure builders are the same code.

- [ ] **Step 10.4: Commit**

```
git add f1_track/viz/app.py
git commit -m "feat(stage5): Streamlit app

Sidebar form (DEMO/AUTO/MANUAL) + tabs (Map / 3D / Analysis)
+ stats bar with FIA validation badge. Cached compose_full for
fast tab switching.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

`bd close <task-id>`.

---

## Task 11: pyproject deps + CLI entry

**Goal:** Add `streamlit` to dependencies; replace broken `f1track` script entry with `f1track-app` pointing at `viz.app:run`.

**Files:**
- Modify: `pyproject.toml`

**Beads:** depends on T10.

- [ ] **Step 11.1: Edit pyproject.toml**

Replace `[project]` and `[project.scripts]` blocks in `pyproject.toml`:

```toml
[project]
name = "f1-track"
version = "0.1.0"
description = "Parametric F1 track generator for Assetto Corsa"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0",
    "scipy>=1.10",
    "numpy>=1.24",
    "matplotlib>=3.8",
    "plotly>=5.17",
    "streamlit>=1.31",
]

[project.scripts]
f1track-app = "f1_track.viz.app:run"

[project.optional-dependencies]
dev = ["pytest>=7.4", "pytest-cov>=4.1"]
```

- [ ] **Step 11.2: Reinstall in editable mode**

```
pip install -e .
```

Expected: success, `f1track-app` script registered.

- [ ] **Step 11.3: Verify console script**

```
f1track-app
```

Expected: launches Streamlit (browser opens). `Ctrl+C` to stop.

- [ ] **Step 11.4: Commit**

```
git add pyproject.toml
git commit -m "build(stage5): add streamlit dep, fix CLI entry

Replaced broken f1track entry (no f1_track.cli module) with
f1track-app → f1_track.viz.app:run.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

`bd close <task-id>`.

---

## Task 12: Verification + smoke test

**Goal:** Fresh-eye verification before claiming Stage 5 done.

**Files:** none.

**Beads:** depends on T11.

> **Switch to Opus** for this task — judgment-heavy.

- [ ] **Step 12.1: Full test run**

```
python -m pytest tests/ F1/tests/ -v
```

Read the FULL output. Count tests; expected: ≥ 47 (Stage 1–4) + ≥ 30 new (Tasks 1–9) = ≥ 77.

If any test fails: stop, debug, do not skip.

- [ ] **Step 12.2: Import smoke test**

```
python -c "from f1_track.viz import TrackSession, build_centerline, build_2d_map_figure; from f1_track.generate import TrackComposer; print('imports OK')"
```

Expected: `imports OK`.

- [ ] **Step 12.3: End-to-end DEMO run**

```
python -c "
from f1_track.generate import GenParams, Mode, TrackComposer
from f1_track.rules import create_ruleset_f1_grade1
from f1_track.viz import build_2d_map_figure
params = GenParams(mode=Mode.DEMO, ruleset_name='f1_grade1')
session = TrackComposer().compose_full(params, create_ruleset_f1_grade1(), seed=1)
print(f'length={session.track.total_length:.1f}m lap_time={session.speed_profile[\"lap_time_s\"]:.2f}s segments={len(session.segments)} points={len(session.geometry.x)}')
fig = build_2d_map_figure(session.geometry, session.speed_profile)
print(f'figure traces: {len(fig.data)}')
"
```

Expected: prints sane values (length ~5536m, lap_time > 0, segments == 16, points > 1000, figure traces == 2).

- [ ] **Step 12.4: Streamlit smoke test (manual)**

```
streamlit run f1_track/viz/app.py
```

Walk through:
1. DEMO → Generate → all 3 tabs populate, FIA badge green, lap time printed.
2. AUTO/easy → Generate → different track shape, lap time printed.
3. AUTO/hard → Generate → tighter corners, lower lap time.
4. MANUAL with `straight=0.5, hairpin=0.3, chicane=0.2`, target_length=4500 → Generate → produces a track.
5. Verify "Export to AC" button shows the Stage 6 placeholder message.

Document any UI defects in `bd create -t bug` issues, do not block on them unless they prevent rendering.

- [ ] **Step 12.5: Update CLAUDE.md project status**

In `CLAUDE.md`, update the "Project Stages" section to add Stage 5:

```markdown
### Stage 5 — Visualization ✅ COMPLETE
- Real geometry layer (Segment.sample, build_centerline, deterministic elevation)
- TrackSession (Track + segments + geometry + speed profile)
- TrackComposer.compose_full()
- Plotly builders (2D, 3D, profiles, breakdown)
- Streamlit application (DEMO/AUTO/MANUAL + tabs + stats)
- **Files:** `f1_track/viz/{geometry,elevation,session,plots,app}.py`
- **Tests:** all passing
```

And update Architecture Overview tree to include `viz/`.

Update "Next Stages (TODO)" — change Stage 5 entry to "Stage 5 ✅", elevate Stage 6 (Assetto Corsa export) to next.

- [ ] **Step 12.6: Commit + push**

```
git add CLAUDE.md
git commit -m "docs(stage5): mark Stage 5 complete in CLAUDE.md"
git pull --rebase
bd dolt push
git push
git status
```

Expected: `git status` shows "up to date with origin".

`bd close <task-id> --reason "Stage 5 complete"`.
`bd close CLAUDE-8nt --reason "Stage 5 epic done"`.

---

## Self-Review

**1. Spec coverage:**
- [x] `Segment.sample()` (Tasks 1, 2, 3)
- [x] `TrackGeometry` + `build_centerline` (Task 4)
- [x] `generate_elevation` deterministic (Task 5)
- [x] `TrackSession` (Task 6)
- [x] `TrackComposer.compose_full` + refactor (Tasks 7, 8)
- [x] Plotly builders 2D/3D/profiles/breakdown (Task 9)
- [x] Streamlit app with sidebar form + tabs + stats (Task 10)
- [x] pyproject deps + entry script (Task 11)
- [x] Verification (Task 12)

**2. Placeholders:** none — all code blocks complete.

**3. Type consistency:**
- `TrackSession` constructed with same kwargs across Tasks 6, 8.
- `compose_full(params, ruleset, seed)` signature consistent across Tasks 8, 10, 12.
- `build_centerline(segments)` and `generate_elevation(segments, geometry, max_change, seed)` consistent.

**4. Risks confirmed in plan:**
- Task 7 calls out potential `final_radius_m` vs computed mismatch in TighteningRadius.
- Task 7 has a regression-baseline test created BEFORE refactor.

---

## Execution Handoff

Plan saved to `docs/superpowers/plans/2026-05-06-stage5-visualization.md`.

Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Good for this plan because tasks are well-isolated.

**2. Inline Execution** — I execute tasks in this session using `superpowers:executing-plans`, batched with checkpoints.

Which approach?
