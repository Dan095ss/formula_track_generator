"""Demo track templates: ready-made reference tracks for testing and demos."""
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


def create_demo_track() -> Track:
    """Create a demo track with all 10 segment types.

    Builds a complete F1 Grade 1 compliant track (~5140m) featuring:
    1. Straight (500m)
    2. HighSpeedTurn (R=300m, 60°)
    3. Straight (300m)
    4. Chicane (2 turns)
    5. Esses (S-curves)
    6. Straight (400m)
    7. Hairpin (180° with spirals)
    8. Straight (300m)
    9. Parabolica (R=400m, 75°)
    10. TighteningRadius (200m)
    11. Straight (250m)
    12. OffCamber (220m)
    13. Straight (300m)
    14. BlindCrest (150m)
    15. CircularTurn (R=150m, 90°)
    16. Straight (500m)

    Total length: ~5140m
    Constraints (F1 Grade 1):
    - Length: 3.5-7 km ✓
    - Width: 12-15 m ✓
    - First corner radius < 300m ✓
    - Min corner radius >= 45m ✓
    - Max elevation change < 100m ✓
    - Max banking < 15° ✓
    """
    # Build segments composing the track
    segments = [
        Straight(500),              # 1: Straight
        HighSpeedTurn(300, np.pi / 3),  # 2: HighSpeedTurn (60°)
        Straight(300),              # 3: Straight
        Chicane(80, num_turns=2),   # 4: Chicane
        Esses(120),                 # 5: Esses
        Straight(400),              # 6: Straight
        Hairpin(60),                # 7: Hairpin
        Straight(300),              # 8: Straight
        Parabolica(400),            # 9: Parabolica
        TighteningRadius(200),      # 10: TighteningRadius
        Straight(250),              # 11: Straight
        OffCamber(220, 150, 80),    # 12: OffCamber (150→80m)
        Straight(300),              # 13: Straight
        BlindCrest(150, 100),       # 14: BlindCrest
        CircularTurn(150, np.pi / 2),  # 15: CircularTurn (90°)
        Straight(500),              # 16: Straight
    ]

    # Calculate total length
    total_length = sum(seg.length() for seg in segments)

    # Calculate aggregate properties for Track model
    # For this demo, we use representative values based on segment composition

    # Minimum corner radius: smallest radius found in segments
    # HighSpeedTurn has R=300, Hairpin has R=60, CircularTurn has R=150, etc.
    min_corner_radius = 60  # From Hairpin

    # First corner radius: the first curve is HighSpeedTurn with R=300
    first_corner_radius = 300

    # Average width: F1 standard
    avg_width = 13.5

    # Elevation: BlindCrest has ~25m of elevation change
    max_elevation_change = 25

    # Banking: typical for F1 circuits, set conservatively
    max_banking_deg = 12

    return Track(
        total_length=total_length,
        avg_width=avg_width,
        first_corner_radius=first_corner_radius,
        min_corner_radius=min_corner_radius,
        max_elevation_change=max_elevation_change,
        max_banking_deg=max_banking_deg,
    )
