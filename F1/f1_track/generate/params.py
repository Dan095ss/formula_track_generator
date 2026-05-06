"""Generation parameters for F1 track generation."""
from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel, field_validator, model_validator


class Mode(str, Enum):
    """Track generation mode."""

    DEMO = "demo"
    AUTO = "auto"
    MANUAL = "manual"


class GenParams(BaseModel):
    """Parameters for track generation with 3 modes.

    - DEMO: Predefined demo track with minimal config
    - AUTO: Automatic generation with difficulty level
    - MANUAL: Full control over all parameters
    """

    mode: Mode
    ruleset_name: str

    # AUTO mode
    difficulty: Optional[str] = None

    # MANUAL mode
    target_length: Optional[float] = None
    sector_count: Optional[int] = None
    segment_preferences: Optional[Dict[str, float]] = None
    elevation_style: Optional[str] = None

    @field_validator("target_length")
    @classmethod
    def validate_target_length(cls, v):
        """target_length must be positive when provided."""
        if v is not None and v <= 0:
            raise ValueError("target_length must be positive")
        return v

    @field_validator("sector_count")
    @classmethod
    def validate_sector_count(cls, v):
        """sector_count must be positive when provided."""
        if v is not None and v <= 0:
            raise ValueError("sector_count must be positive")
        return v

    @field_validator("segment_preferences")
    @classmethod
    def validate_segment_preferences(cls, v):
        """Validate that all segment preference values are in [0, 1]."""
        if v is not None:
            for key, val in v.items():
                if not (0 <= val <= 1):
                    raise ValueError(f"segment_preferences[{key}] must be in [0, 1], got {val}")
        return v

    @model_validator(mode="after")
    def validate_mode_requirements(self):
        """Validate that required fields are provided for each mode."""
        if self.mode == Mode.AUTO:
            if self.difficulty is None:
                raise ValueError("difficulty is required for AUTO mode")
        elif self.mode == Mode.MANUAL:
            if self.target_length is None:
                raise ValueError("target_length is required for MANUAL mode")
            if self.sector_count is None:
                raise ValueError("sector_count is required for MANUAL mode")
            if self.segment_preferences is None:
                raise ValueError("segment_preferences are required for MANUAL mode")
            if self.elevation_style is None:
                raise ValueError("elevation_style is required for MANUAL mode")
        return self
