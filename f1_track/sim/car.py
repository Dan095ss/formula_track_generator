"""F1 car model: mass, power, aerodynamics, tire model."""


class F1Car:
    """Modern F1 car performance model (2024-spec approximate)."""

    def __init__(self):
        """Initialize F1 car with 2024 technical regulations properties."""
        self.mass_kg = 798.0  # Car + driver (min 798 kg per regulations)
        self.power_kw = 770.0  # ~1050 hp (combined PU + hybrid)
        self.drag_coeff = 0.95  # Typical high-downforce setup
        self.front_area_m2 = 4.25  # Approximate frontal area
        self.tire_radius_m = 0.33  # 370 mm tire (approximate)

    @property
    def max_speed_kmh(self):
        """Estimate top speed in km/h (power-limited on straights)."""
        # P = F * v, so v_max = P / F_drag
        # F_drag = 0.5 * rho * Cd * A * v^2
        # This is simplified; actual calculation is iterative
        return 330.0

    @property
    def downforce_kg(self):
        """Estimate downforce in kg-force at 250 km/h."""
        return 850.0  # Approximate for high-downforce setup
