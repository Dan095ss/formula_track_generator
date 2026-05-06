"""FIA Appendix O track validation."""
from f1_track.rules import RuleSet
from .track import Track


class ValidationError(Exception):
    """Raised when track fails validation against ruleset."""

    pass


class TrackValidator:
    """Validates track geometry against FIA (or other) standard."""

    def __init__(self, ruleset: RuleSet):
        """Initialize validator with ruleset constraints.

        Args:
            ruleset: RuleSet defining track constraints
        """
        self.ruleset = ruleset

    def validate(self, track: Track) -> None:
        """Validate track against ruleset.

        Raises:
            ValidationError: If track violates any constraint
        """
        # Length check
        if track.total_length < self.ruleset.track_length_min:
            raise ValidationError(
                f"Track length {track.total_length} m is below minimum "
                f"{self.ruleset.track_length_min} m"
            )
        if track.total_length > self.ruleset.track_length_max:
            raise ValidationError(
                f"Track length {track.total_length} m exceeds maximum "
                f"{self.ruleset.track_length_max} m"
            )

        # Width check
        if track.avg_width < self.ruleset.track_width_min:
            raise ValidationError(
                f"Track width {track.avg_width} m is below minimum "
                f"{self.ruleset.track_width_min} m"
            )
        if track.avg_width > self.ruleset.track_width_max:
            raise ValidationError(
                f"Track width {track.avg_width} m exceeds maximum "
                f"{self.ruleset.track_width_max} m"
            )

        # First corner radius check
        if track.first_corner_radius > self.ruleset.first_corner_radius_max:
            raise ValidationError(
                f"First corner radius {track.first_corner_radius} m exceeds maximum "
                f"{self.ruleset.first_corner_radius_max} m (must be tighter)"
            )

        # Minimum corner radius check
        if track.min_corner_radius < self.ruleset.min_corner_radius:
            raise ValidationError(
                f"Minimum corner radius {track.min_corner_radius} m is below "
                f"{self.ruleset.min_corner_radius} m"
            )

        # Elevation change check
        if track.max_elevation_change > self.ruleset.max_elevation_change:
            raise ValidationError(
                f"Max elevation change {track.max_elevation_change} m exceeds "
                f"maximum {self.ruleset.max_elevation_change} m"
            )

        # Banking check
        if track.max_banking_deg > self.ruleset.max_banking_degrees:
            raise ValidationError(
                f"Max banking {track.max_banking_deg}° exceeds maximum "
                f"{self.ruleset.max_banking_degrees}°"
            )
