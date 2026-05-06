"""Track geometry model: centerline + width + elevation + banking."""
from dataclasses import dataclass
from pydantic import BaseModel, field_validator


class Track(BaseModel):
    """Track geometry specification (simplified for MVP).

    Full implementation would include:
    - Centerline: list of (x, y, heading) points
    - Width profile: width as function of arc length
    - Elevation profile: height as function of arc length
    - Banking profile: bank angle as function of arc length

    For MVP validation, we use aggregate properties.
    """

    total_length: float  # Total track length (m)
    avg_width: float  # Average track width (m)
    first_corner_radius: float  # Radius of first corner (m)
    min_corner_radius: float  # Minimum corner radius on track (m)
    max_elevation_change: float  # Max elevation change (m)
    max_banking_deg: float  # Max banking angle (degrees)

    @field_validator("total_length", "avg_width", "first_corner_radius", "min_corner_radius")
    @classmethod
    def validate_positive(cls, v):
        if v <= 0:
            raise ValueError("Must be positive")
        return v

    @field_validator("max_elevation_change", "max_banking_deg")
    @classmethod
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError("Must be non-negative")
        return v
