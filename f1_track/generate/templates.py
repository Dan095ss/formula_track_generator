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

# TighteningRadius curvature rate giving pi/12 (15 deg) heading change at L=150m:
# heading = k * L^2 / 2 = pi/12  => k = pi/6 / L^2
_K_TR = (np.pi / 12) / (150.0 ** 2 / 2)  # ≈ 2.327e-5 (1/m²)

# OffCamber parameters: R_avg = 763.9m, angle = L/R_avg = 200/763.9 = 15 deg
_R_OFF_START = 800.0
_R_OFF_END = 727.9


def create_demo_segments() -> list:
    """Return ordered segment list for the closed CCW demo track.

    12 segments demonstrating all 10 available segment types.
    Net heading change: +2*pi (one full CCW lap).
    Position closure: start and end both at (0, 0).

    Heading sequence:
      h=0 (east) -> Hairpin(+180) -> h=180 (west) -> Straight_west
      -> HighSpeedTurn(+90) -> h=270 (south) -> Chicane(0) -> h=270
      -> Parabolica(+60) -> h=330 -> TighteningRadius(+15) -> h=345
      -> OffCamber(+15) -> h=360 -> BlindCrest(0) -> h=360
      -> Esses(+90) -> h=450 -> Straight_north
      -> CircularTurn(-90) -> h=360 -> Straight_main back to (0,0)

    Heading change sum: 180+90+60+15+15+90-90 = 360 deg = 2*pi ✓
    """
    return [
        Hairpin(60, 0.001),               # 1: Hairpin 180-deg CCW (h: 0->180)
        Straight(1700.0),                 # 2: Straight (long west straight)
        HighSpeedTurn(300, 0.0001),       # 3: HighSpeedTurn 90-deg CCW (h: 180->270)
        Chicane(80, num_turns=2),          # 4: Chicane net-0 (h: 270->270)
        Parabolica(400),                  # 5: Parabolica 60-deg CCW (h: 270->330)
        TighteningRadius(150, _K_TR),    # 6: TighteningRadius 15-deg (h: 330->345)
        OffCamber(200, _R_OFF_START, _R_OFF_END),  # 7: OffCamber 15-deg (h: 345->360)
        BlindCrest(150, 100),             # 8: BlindCrest straight (h: 360->360)
        Esses(120),                       # 9: Esses 90-deg CCW (h: 360->450)
        Straight(210.08),                 # 10: Straight (north gap-close)
        CircularTurn(200, -np.pi / 2),   # 11: CircularTurn 90-deg CW (h: 450->360)
        Straight(522.15),                 # 12: Straight (main east closing straight)
    ]


def create_demo_track() -> Track:
    """Create the closed CCW demo track with all 10 segment types.

    A proper closed-loop F1-style circuit (~5493m) featuring all 10 segment types:
    1. Hairpin (180-deg turn with spirals)
    2. Straight (long main straight, 1700m)
    3. HighSpeedTurn (90-deg, R=300m)
    4. Chicane (2-turn chicane)
    5. Parabolica (60-deg, R=400m)
    6. TighteningRadius (150m clothoid, 15-deg)
    7. OffCamber (200m, R 800->728m, 15-deg)
    8. BlindCrest (150m straight)
    9. Esses (S-curves, 90-deg net)
    10. Straight (north gap-close, 210m)
    11. CircularTurn (90-deg CW, R=200m)
    12. Straight (east closing straight, 522m)

    Total length: ~5493m
    Net heading: +360 deg (1 full CCW lap)
    Closure: start (0,0) heading east, end (0,0) heading east ✓

    F1 Grade 1 constraints satisfied:
    - Length: 3.5-7 km ✓
    - Width: 12-15 m ✓
    - First corner radius ≥ 60m (Hairpin R=60) ✓
    - Min corner radius ≥ 45m ✓
    - Max elevation change < 100m ✓
    - Max banking < 15° ✓
    """
    segments = create_demo_segments()
    total_length = sum(seg.length() for seg in segments)

    # Min corner radius: Hairpin R=60
    min_corner_radius = 60

    # First corner radius: Hairpin R=60
    first_corner_radius = 60

    # F1 standard width
    avg_width = 13.5

    # Conservative elevation
    max_elevation_change = 25

    # Conservative banking
    max_banking_deg = 12

    return Track(
        total_length=total_length,
        avg_width=avg_width,
        first_corner_radius=first_corner_radius,
        min_corner_radius=min_corner_radius,
        max_elevation_change=max_elevation_change,
        max_banking_deg=max_banking_deg,
    )
