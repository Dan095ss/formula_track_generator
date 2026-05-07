"""Parametric curves for track centerline: clothoid, circular arc, line."""
import numpy as np
from scipy.special import fresnel


class Curve:
    """Base class for parametric curves parameterized by arc length s."""

    def arc_length(self) -> float:
        """Total arc length of curve."""
        raise NotImplementedError

    def point(self, s: float) -> tuple[float, float, float]:
        """Point on curve at arc length s.

        Returns (x, y, heading_rad).
        """
        raise NotImplementedError

    def curvature_at(self, s: float) -> float:
        """Curvature (1/radius) at arc length s."""
        raise NotImplementedError


class ClothoidCurve(Curve):
    """Clothoid (Euler spiral): constant curvature rate.

    Parameterized by arc length s ∈ [0, length].
    Curvature κ(s) = k * s where k = curvature_rate.
    Uses Fresnel integrals for (x, y) computation.
    """

    def __init__(self, curvature_rate: float, length: float, initial_heading: float = 0.0):
        """Initialize clothoid.

        Args:
            curvature_rate: κ(s) = k*s, where k = curvature_rate (1/m²)
            length: arc length of spiral (m)
            initial_heading: heading angle at s=0 (rad)
        """
        self.k = curvature_rate
        self.L = length
        self.theta0 = initial_heading

    def arc_length(self) -> float:
        return self.L

    def point(self, s: float) -> tuple[float, float, float]:
        """Compute (x, y, heading) at arc length s using Fresnel integrals."""
        if s <= 0:
            return (0.0, 0.0, self.theta0)

        abs_k = abs(self.k)
        if abs_k < 1e-12:
            x = s * np.cos(self.theta0)
            y = s * np.sin(self.theta0)
            return (x, y, self.theta0)

        # Fresnel integrals in theta0=0 frame
        t = s * np.sqrt(abs_k / np.pi)
        C, S = fresnel(t)
        scale = np.sqrt(np.pi / abs_k)
        x0 = C * scale
        y0 = S * scale if self.k > 0 else -S * scale  # k<0 mirrors y (CW spiral)

        # Rotate by initial heading
        x = x0 * np.cos(self.theta0) - y0 * np.sin(self.theta0)
        y = x0 * np.sin(self.theta0) + y0 * np.cos(self.theta0)

        # Heading: θ(s) = θ0 + k*s²/2 (works for both signs of k)
        heading = self.theta0 + 0.5 * self.k * s ** 2

        return (x, y, heading)

    def curvature_at(self, s: float) -> float:
        """Curvature κ(s) = k*s."""
        return self.k * s


class CircularArc(Curve):
    """Circular arc of constant radius."""

    def __init__(self, radius: float, angle_rad: float, initial_heading: float = 0.0):
        """Initialize circular arc.

        Args:
            radius: radius of curvature (m)
            angle_rad: angle subtended (rad)
            initial_heading: heading at start (rad)
        """
        self.R = radius
        self.angle = angle_rad
        self.theta0 = initial_heading

    def arc_length(self) -> float:
        return self.R * abs(self.angle)

    def point(self, s: float) -> tuple[float, float, float]:
        """Compute (x, y, heading) at arc length s from start."""
        if self.R <= 0 or s <= 0:
            return (0.0, 0.0, self.theta0)

        sign = np.sign(self.angle)
        phi = s / self.R  # unsigned radians traversed

        # Center is to the left for CCW (sign=+1), right for CW (sign=-1)
        cx = -sign * self.R * np.sin(self.theta0)
        cy = sign * self.R * np.cos(self.theta0)

        # Angle from center to the current point on the circle
        angle_to_point = self.theta0 + sign * phi - sign * np.pi / 2

        x = cx + self.R * np.cos(angle_to_point)
        y = cy + self.R * np.sin(angle_to_point)
        heading = self.theta0 + sign * phi

        return (x, y, heading)

    def curvature_at(self, s: float) -> float:
        """Curvature is constant: κ = 1/R."""
        return 1.0 / self.R if self.R > 0 else 0.0


class Line(Curve):
    """Straight line segment."""

    def __init__(self, length: float, heading: float = 0.0):
        """Initialize line segment.

        Args:
            length: length of line (m)
            heading: direction angle (rad)
        """
        self.L = length
        self.theta = heading

    def arc_length(self) -> float:
        return self.L

    def point(self, s: float) -> tuple[float, float, float]:
        """Compute (x, y, heading) at arc length s."""
        x = s * np.cos(self.theta)
        y = s * np.sin(self.theta)
        return (x, y, self.theta)

    def curvature_at(self, s: float) -> float:
        """Curvature is zero (straight line)."""
        return 0.0
