"""Quasi-steady-state (QSS) lap time simulator."""
import numpy as np


class LapSimulator:
    """QSS lap time calculator for F1 cars on parameterized tracks."""

    def __init__(self, car):
        """Initialize simulator with car model.

        Args:
            car: F1Car instance with mass, power, drag properties
        """
        self.car = car
        self.g = 9.81  # Gravity (m/s^2)
        self.max_lateral_g = 2.0  # Max lateral acceleration for F1 (2.0 G typical)
        self.rho = 1.225  # Air density (kg/m^3)

    def simulate(self, s_coords, curvature):
        """Simulate lap with QSS model.

        Args:
            s_coords: Arc length coordinates (m), typically 0 to track_length
            curvature: Curvature at each arc length point (1/m)

        Returns:
            Dictionary with keys:
            - "speed_kmh": Speed at each point (km/h)
            - "v_mps": Speed at each point (m/s)
            - "lap_time_s": Total lap time (s)
        """
        speeds_mps = self._calculate_speeds(curvature)

        # Convert to km/h for output
        speeds_kmh = speeds_mps * 3.6

        # Estimate lap time by integration
        # For variable speed: use trapezoidal rule
        ds = np.diff(s_coords)
        if len(ds) > 0:
            avg_speeds = (speeds_mps[:-1] + speeds_mps[1:]) / 2
            time_segments = ds / (avg_speeds + 1e-6)  # Avoid division by zero
            lap_time = np.sum(time_segments)
        else:
            lap_time = 0.0

        return {
            "speed_kmh": speeds_kmh,
            "v_mps": speeds_mps,
            "lap_time_s": lap_time,
        }

    def _calculate_speeds(self, curvature):
        """Calculate speed profile based on curvature constraints.

        At each point:
        - Corner speed limit: v_corner = sqrt(max_lateral_g * g / curvature)
        - Straight speed limit: v_straight ≈ max_power_speed (simplified)

        Args:
            curvature: Array of curvature values (1/m)

        Returns:
            Array of speeds (m/s)
        """
        speeds = np.zeros_like(curvature, dtype=float)

        # Approximate max power speed on straights (simplified)
        # P = F * v, with F_drag ≈ 0.5 * rho * Cd * A * v^2
        # For simplification: use fixed max speed ~330 km/h = 91.7 m/s
        max_power_speed = 90.0  # m/s

        for i, curv in enumerate(curvature):
            if curv < 0.0001:  # Nearly straight
                speeds[i] = max_power_speed
            else:
                # Corner speed limited by grip
                v_corner = np.sqrt(self.max_lateral_g * self.g / curv)
                speeds[i] = min(v_corner, max_power_speed)

        # Smooth the speed profile (avoid abrupt changes)
        speeds = self._smooth_speed_profile(speeds, curvature)

        return speeds

    def _smooth_speed_profile(self, speeds, curvature):
        """Smooth speed profile to avoid instantaneous changes.

        For MVP: apply simple moving average.

        Args:
            speeds: Initial speed profile
            curvature: Curvature profile (not used in MVP, for future)

        Returns:
            Smoothed speed profile
        """
        if len(speeds) < 3:
            return speeds

        # Simple 3-point moving average for smoothing
        smoothed = speeds.copy()
        for i in range(1, len(speeds) - 1):
            smoothed[i] = (speeds[i - 1] + speeds[i] + speeds[i + 1]) / 3.0

        return smoothed
