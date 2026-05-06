"""Track segment palette: compositions of curves for track geometry."""
import numpy as np
from .curve import Curve, ClothoidCurve, CircularArc, Line


class Segment:
    """Base class for track segment (composition of curves)."""

    def length(self) -> float:
        """Total length of segment (m)."""
        raise NotImplementedError

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        """Displacement (Δx, Δy) and heading change at end of segment."""
        raise NotImplementedError

    def end_heading(self, initial_heading: float) -> float:
        """Heading angle at end of segment."""
        _, _, heading = self.end_point(initial_heading)
        return heading

    def _build_curves(self, initial_heading: float) -> list:
        """Return ordered list of sub-curves (Curve instances).
        Chaining them reproduces this segment's geometry exactly.
        """
        raise NotImplementedError


class Straight(Segment):
    """Straight line segment."""

    def __init__(self, length: float):
        self.L = length

    def length(self) -> float:
        return self.L

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        line = Line(self.L, heading=initial_heading)
        return line.point(self.L)

    def _build_curves(self, initial_heading: float) -> list:
        return [Line(self.L, heading=initial_heading)]


class CircularTurn(Segment):
    """Circular turn (e.g., high-speed corner)."""

    def __init__(self, radius: float, angle_rad: float):
        self.R = radius
        self.angle = angle_rad

    def length(self) -> float:
        return self.R * abs(self.angle)

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        arc = CircularArc(self.R, self.angle, initial_heading=initial_heading)
        x, y, heading = arc.point(self.length())
        return (x, y, heading)

    def _build_curves(self, initial_heading: float) -> list:
        return [CircularArc(self.R, self.angle, initial_heading=initial_heading)]


class Hairpin(Segment):
    """Hairpin turn (180° turn with entry/exit spirals).

    Composed of:
    - Clothoid entry (0 → κ)
    - Circular arc (κ constant)
    - Clothoid exit (κ → 0)
    """

    def __init__(self, radius: float, k_entry: float = 0.001):
        """Initialize hairpin.

        Args:
            radius: radius of circular section (m)
            k_entry: curvature rate of clothoid entry (1/m²)
        """
        self.R = radius
        self.k = k_entry
        # Spiral length: curvature reaches 1/R when k*L_spiral = 1/R
        self.L_spiral = (1.0 / self.R) / self.k
        self.arc = CircularArc(radius, np.pi)  # 180° turn

    def length(self) -> float:
        return 2 * self.L_spiral + self.arc.arc_length()

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        x_total, y_total = 0.0, 0.0
        heading = initial_heading

        # Entry spiral
        entry = ClothoidCurve(self.k, self.L_spiral, heading)
        x1, y1, heading = entry.point(self.L_spiral)
        x_total += x1
        y_total += y1

        # Circular arc (180°)
        arc = CircularArc(self.R, np.pi, heading)
        x2, y2, heading = arc.point(arc.arc_length())
        x_total += x2
        y_total += y2

        # Exit spiral (mirrored entry)
        exit_spiral = ClothoidCurve(-self.k, self.L_spiral, heading)
        x3, y3, heading = exit_spiral.point(self.L_spiral)
        x_total += x3
        y_total += y3

        return (x_total, y_total, heading)

    def _build_curves(self, initial_heading: float) -> list:
        h0 = initial_heading
        entry = ClothoidCurve(self.k, self.L_spiral, h0)
        h1 = entry.point(entry.arc_length())[2]
        arc = CircularArc(self.R, np.pi, initial_heading=h1)
        h2 = arc.point(arc.arc_length())[2]
        exit_spiral = ClothoidCurve(-self.k, self.L_spiral, h2)
        return [entry, arc, exit_spiral]


class Chicane(Segment):
    """Chicane: alternating left-right turns."""

    def __init__(self, radius: float, num_turns: int = 2):
        """Initialize chicane.

        Args:
            radius: radius of each turn (m)
            num_turns: number of turns (L-R pairs)
        """
        self.R = radius
        self.turns = num_turns

    def length(self) -> float:
        return self.turns * 2 * self.R * (np.pi / 2)  # num_turns pairs of 90° turns

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        x_total, y_total = 0.0, 0.0
        heading = initial_heading

        for _ in range(self.turns):
            # Left turn (90°)
            left = CircularArc(self.R, np.pi / 2, heading)
            x1, y1, heading = left.point(left.arc_length())
            x_total += x1
            y_total += y1

            # Right turn (90°)
            right = CircularArc(self.R, -np.pi / 2, heading)
            x2, y2, heading = right.point(right.arc_length())
            x_total += x2
            y_total += y2

        return (x_total, y_total, heading)

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


class Esses(Segment):
    """S-curves: opposing curves (L-R-L or similar)."""

    def __init__(self, radius: float):
        self.R = radius

    def length(self) -> float:
        return 3 * self.R * (np.pi / 2)  # Left + Right + Left (90° each)

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        x_total, y_total = 0.0, 0.0
        heading = initial_heading

        # Left
        left = CircularArc(self.R, np.pi / 2, heading)
        x1, y1, heading = left.point(left.arc_length())
        x_total += x1
        y_total += y1

        # Right
        right = CircularArc(self.R, -np.pi / 2, heading)
        x2, y2, heading = right.point(right.arc_length())
        x_total += x2
        y_total += y2

        # Left
        left2 = CircularArc(self.R, np.pi / 2, heading)
        x3, y3, heading = left2.point(left2.arc_length())
        x_total += x3
        y_total += y3

        return (x_total, y_total, heading)

    def _build_curves(self, initial_heading: float) -> list:
        h = initial_heading
        left = CircularArc(self.R, np.pi / 2, initial_heading=h)
        h = left.point(left.arc_length())[2]
        right = CircularArc(self.R, -np.pi / 2, initial_heading=h)
        h = right.point(right.arc_length())[2]
        left2 = CircularArc(self.R, np.pi / 2, initial_heading=h)
        return [left, right, left2]


class HighSpeedTurn(Segment):
    """High-speed corner (large radius, smooth entry/exit via clothoid)."""

    def __init__(self, radius: float, k_entry: float = 0.0001):
        self.R = radius
        self.k = k_entry
        self.L_spiral = (1.0 / self.R) / self.k
        self.arc = CircularArc(radius, np.pi / 2)  # 90° turn

    def length(self) -> float:
        return 2 * self.L_spiral + self.arc.arc_length()

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        x_total, y_total = 0.0, 0.0
        heading = initial_heading

        # Entry spiral
        entry = ClothoidCurve(self.k, self.L_spiral, heading)
        x1, y1, heading = entry.point(self.L_spiral)
        x_total += x1
        y_total += y1

        # Circular arc
        arc = CircularArc(self.R, np.pi / 2, heading)
        x2, y2, heading = arc.point(arc.arc_length())
        x_total += x2
        y_total += y2

        # Exit spiral
        exit_spiral = ClothoidCurve(-self.k, self.L_spiral, heading)
        x3, y3, heading = exit_spiral.point(self.L_spiral)
        x_total += x3
        y_total += y3

        return (x_total, y_total, heading)

    def _build_curves(self, initial_heading: float) -> list:
        h0 = initial_heading
        entry = ClothoidCurve(self.k, self.L_spiral, h0)
        h1 = entry.point(entry.arc_length())[2]
        arc = CircularArc(self.R, np.pi / 2, initial_heading=h1)
        h2 = arc.point(arc.arc_length())[2]
        exit_spiral = ClothoidCurve(-self.k, self.L_spiral, h2)
        return [entry, arc, exit_spiral]


class Parabolica(Segment):
    """Parabolica: fast, flowing corner (opposite of hairpin)."""

    def __init__(self, radius: float):
        self.R = radius
        # Large radius, long arc
        self.arc = CircularArc(radius, np.pi / 3)  # 60° turn

    def length(self) -> float:
        return self.arc.arc_length()

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        arc = CircularArc(self.R, np.pi / 3, initial_heading=initial_heading)
        return arc.point(arc.arc_length())

    def _build_curves(self, initial_heading: float) -> list:
        return [CircularArc(self.R, np.pi / 3, initial_heading=initial_heading)]


class TighteningRadius(Segment):
    """Tightening radius: radius decreases along arc (using clothoid)."""

    def __init__(self, length: float, k_rate: float = 0.001):
        self.L = length
        self.k = k_rate

    def length(self) -> float:
        return self.L

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        clothoid = ClothoidCurve(self.k, self.L, initial_heading)
        return clothoid.point(self.L)

    def _build_curves(self, initial_heading: float) -> list:
        return [ClothoidCurve(self.k, self.L, initial_heading)]


class OffCamber(Segment):
    """Off-camber corner: decreasing radius with elevation change."""

    def __init__(self, length: float, radius_start: float, radius_end: float):
        self.L = length
        self.R_start = radius_start
        self.R_end = radius_end

    def length(self) -> float:
        return self.L

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        # Approximate as circular arc with average radius
        R_avg = (self.R_start + self.R_end) / 2
        angle = self.L / R_avg
        arc = CircularArc(R_avg, angle, initial_heading)
        return arc.point(self.L)

    def _build_curves(self, initial_heading: float) -> list:
        R_avg = (self.R_start + self.R_end) / 2
        angle = self.L / R_avg
        return [CircularArc(R_avg, angle, initial_heading=initial_heading)]


class BlindCrest(Segment):
    """Blind crest: rise in elevation creating visual obstruction."""

    def __init__(self, length: float, radius: float):
        self.L = length
        self.R = radius
        self.line = Straight(length)

    def length(self) -> float:
        return self.L

    def end_point(self, initial_heading: float) -> tuple[float, float, float]:
        # Crest is geometrically straight (elevation handled separately)
        return self.line.end_point(initial_heading)

    def _build_curves(self, initial_heading: float) -> list:
        return [Line(self.L, heading=initial_heading)]
