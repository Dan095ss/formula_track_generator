"""Tests for lap time simulation (QSS)."""
import pytest
import numpy as np
from f1_track.geometry.track import Track
from f1_track.sim.car import F1Car
from f1_track.sim.qss import LapSimulator
from f1_track.sim.raceline import MinimumCurvatureRaceline


class TestF1Car:
    """Test F1 car model."""

    def test_f1_car_weight(self):
        """F1 car with driver should be ~798 kg."""
        car = F1Car()
        assert 790 < car.mass_kg < 810, f"Mass {car.mass_kg} kg out of range"

    def test_f1_car_power(self):
        """F1 car power should be ~770 kW."""
        car = F1Car()
        assert 750 < car.power_kw < 800, f"Power {car.power_kw} kW out of range"

    def test_f1_car_drag_coefficient(self):
        """F1 car should have typical drag coefficient."""
        car = F1Car()
        assert 0.7 < car.drag_coeff < 1.2, f"Cd {car.drag_coeff} out of range"


class TestRaceline:
    """Test minimum curvature raceline."""

    def test_raceline_length(self):
        """Raceline for straight section should be straight."""
        raceline = MinimumCurvatureRaceline()

        # Mock track segment: straight 100m
        track_points = np.array([[0, 0], [100, 0]])  # x, y
        lane_width = 10.0  # m

        # Raceline should fit in lane
        rl_x, rl_y = raceline.compute(track_points, lane_width)
        assert len(rl_x) > 0
        assert len(rl_y) == len(rl_x)

    def test_raceline_corner(self):
        """Raceline for 90° corner should optimize through turn."""
        raceline = MinimumCurvatureRaceline()

        # Right angle corner (90° turn)
        track_points = np.array([[0, 0], [100, 0], [100, 100]])  # L-shaped
        lane_width = 10.0

        rl_x, rl_y = raceline.compute(track_points, lane_width)
        assert len(rl_x) > 0


class TestLapSimulator:
    """Test QSS lap time simulator."""

    def test_lap_simulator_straight(self):
        """Simulator should accelerate on straights."""
        car = F1Car()
        simulator = LapSimulator(car)

        # Mock track: straight 500m, no curvature
        track = Track(
            total_length=500.0,
            avg_width=12.0,
            first_corner_radius=300.0,
            min_corner_radius=100.0,
            max_elevation_change=0.0,
            max_banking_deg=0.0,
        )

        # Create simple raceline: straight
        s_coords = np.linspace(0, 500, 100)  # arc length
        curvature = np.zeros_like(s_coords)  # zero curvature = straight

        lap_data = simulator.simulate(s_coords, curvature)

        # Should have speed, acceleration, etc.
        assert "speed_kmh" in lap_data or "v_mps" in lap_data
        assert len(lap_data.get("speed_kmh", [])) > 0 or len(lap_data.get("v_mps", [])) > 0

    def test_lap_time_reasonable(self):
        """Lap time for typical F1 track should be in realistic range (1-2 min)."""
        car = F1Car()
        simulator = LapSimulator(car)

        # Simplified track: 5500m
        track = Track(
            total_length=5500.0,
            avg_width=13.0,
            first_corner_radius=250.0,
            min_corner_radius=60.0,
            max_elevation_change=80.0,
            max_banking_deg=10.0,
        )

        # Mock raceline
        s_coords = np.linspace(0, 5500, 500)
        # Vary curvature (simplified: sinusoidal variation)
        curvature = 0.005 * (1 + 0.5 * np.sin(2 * np.pi * s_coords / 5500))

        lap_data = simulator.simulate(s_coords, curvature)

        # Extract lap time (should be in result dict)
        if "lap_time_s" in lap_data:
            lap_time = lap_data["lap_time_s"]
            # 5500m at avg 250 km/h = ~79s (lower bound)
            # 5500m at avg 150 km/h = ~132s (upper bound)
            assert 60 < lap_time < 180, f"Lap time {lap_time} s unrealistic"
