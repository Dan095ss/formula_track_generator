"""Track standards and rule sets (FIA Grade 1, Karting, etc.)."""
from enum import Enum
from typing import List
from pydantic import BaseModel, field_validator


class SegmentType(str, Enum):
    """Palette of track segment types for geometric composition."""
    STRAIGHT = "straight"
    HAIRPIN = "hairpin"
    CHICANE = "chicane"
    ESSES = "esses"
    HIGH_SPEED_TURN = "high_speed_turn"
    PARABOLICA = "parabolica"
    TIGHTENING_RADIUS = "tightening_radius"
    OFF_CAMBER = "off_camber"
    BLIND_CREST = "blind_crest"


class RuleSet(BaseModel):
    """Track constraints and generation policy for a racing standard.

    Encapsulates FIA or other regulatory requirements (length, width, radius limits,
    banking, runoff) plus generation parameters (allowed segment types, DRS zones, target speed).
    """
    name: str
    track_length_min: float  # meters
    track_length_max: float
    track_width_min: float  # meters
    track_width_max: float
    first_corner_radius_max: float  # meters
    min_corner_radius: float  # meters
    max_elevation_change: float  # meters
    max_banking_degrees: float
    runoff_width_min: float  # meters
    allowed_segments: List[SegmentType]
    avg_speed_target_kmh: float
    max_drs_zones: int

    @field_validator("track_length_max")
    @classmethod
    def validate_length_range(cls, v, info):
        if info.data.get("track_length_min") and v <= info.data["track_length_min"]:
            raise ValueError("track_length_max must be > track_length_min")
        return v

    @field_validator("track_width_max")
    @classmethod
    def validate_width_range(cls, v, info):
        if info.data.get("track_width_min") and v <= info.data["track_width_min"]:
            raise ValueError("track_width_max must be > track_width_min")
        return v

    @field_validator("min_corner_radius")
    @classmethod
    def validate_radius(cls, v, info):
        if info.data.get("first_corner_radius_max") and v > info.data["first_corner_radius_max"]:
            raise ValueError("min_corner_radius must be <= first_corner_radius_max")
        return v


def create_ruleset_f1_grade1() -> RuleSet:
    """FIA Grade 1 F1 track standard (3.5-7 km, 12-15 m wide)."""
    return RuleSet(
        name="FIA F1 Grade 1",
        track_length_min=3500,
        track_length_max=7000,
        track_width_min=12,
        track_width_max=15,
        first_corner_radius_max=300,
        min_corner_radius=45,
        max_elevation_change=100,
        max_banking_degrees=15,
        runoff_width_min=10,
        allowed_segments=list(SegmentType),
        avg_speed_target_kmh=280,
        max_drs_zones=2,
    )


def create_ruleset_karting_cik() -> RuleSet:
    """CIK-FIA International Karting standard (1-2.5 km, 7-10 m wide)."""
    return RuleSet(
        name="CIK-FIA Karting",
        track_length_min=1000,
        track_length_max=2500,
        track_width_min=7,
        track_width_max=10,
        first_corner_radius_max=150,
        min_corner_radius=25,
        max_elevation_change=50,
        max_banking_degrees=10,
        runoff_width_min=6,
        allowed_segments=list(SegmentType),
        avg_speed_target_kmh=100,
        max_drs_zones=0,
    )
