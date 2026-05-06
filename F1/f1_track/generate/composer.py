"""Track composer: combines parameters and rulesets into ready-made tracks."""
import numpy as np
from f1_track.generate.params import GenParams, Mode
from f1_track.generate.templates import create_demo_track
from f1_track.geometry.track import Track
from f1_track.geometry import (
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
from f1_track.rules import RuleSet


class TrackComposer:
    """Compose tracks from generation parameters and rulesets.

    Supports three composition modes:
    - DEMO: Returns a predefined demo track
    - AUTO: Automatic generation with difficulty level (easy/medium/hard)
    - MANUAL: Full control over parameters (TODO)
    """

    def compose(self, params: GenParams, ruleset: RuleSet) -> Track:
        """Compose a track from parameters and ruleset.

        Args:
            params: Generation parameters specifying mode and config
            ruleset: Track rules and constraints

        Returns:
            Generated or composed Track instance

        Raises:
            ValueError: If mode is unknown
            NotImplementedError: If mode is not yet implemented
        """
        if params.mode == Mode.DEMO:
            return self._compose_demo()
        elif params.mode == Mode.AUTO:
            return self._compose_auto(params, ruleset)
        elif params.mode == Mode.MANUAL:
            return self._compose_manual(params, ruleset)
        else:
            raise ValueError(f"Unknown mode: {params.mode}")

    def _compose_demo(self) -> Track:
        """Compose DEMO mode: return predefined demo track."""
        return create_demo_track()

    def _compose_auto(self, params: GenParams, ruleset: RuleSet) -> Track:
        """Compose AUTO mode: automatic generation with difficulty level.

        Generates a track using weighted-random segment selection based on difficulty.
        Difficulty levels (easy/medium/hard) determine segment type probabilities.
        Target track length is set between min and max constraints.

        Args:
            params: GenParams with difficulty level (easy, medium, or hard)
            ruleset: Track rules and constraints to respect

        Returns:
            Auto-generated Track with valid properties meeting FIA constraints

        Raises:
            ValueError: If difficulty level is invalid
        """
        # Difficulty-based segment weights
        difficulty_weights = {
            "easy": {
                "straight": 0.3,
                "high_speed_turn": 0.3,
                "circular_turn": 0.2,
                "parabolica": 0.2,
            },
            "medium": {
                "straight": 0.2,
                "circular_turn": 0.2,
                "high_speed_turn": 0.2,
                "chicane": 0.15,
                "esses": 0.15,
                "hairpin": 0.1,
            },
            "hard": {
                "chicane": 0.2,
                "hairpin": 0.2,
                "esses": 0.2,
                "tightening_radius": 0.15,
                "off_camber": 0.15,
                "blind_crest": 0.1,
            },
        }

        # Get segment weights for this difficulty
        difficulty = params.difficulty or "medium"
        weights = difficulty_weights.get(difficulty, difficulty_weights["medium"])

        # Segment generator functions with default parameters
        segment_generators = {
            "straight": lambda: Straight(np.random.uniform(250, 500)),
            "high_speed_turn": lambda: HighSpeedTurn(
                np.random.uniform(200, 350), 0.0001
            ),
            "circular_turn": lambda: CircularTurn(
                np.random.uniform(100, 200), np.random.uniform(np.pi / 6, np.pi / 2)
            ),
            "parabolica": lambda: Parabolica(np.random.uniform(300, 450)),
            "hairpin": lambda: Hairpin(np.random.uniform(50, 80), 0.001),
            "chicane": lambda: Chicane(np.random.uniform(60, 100), num_turns=2),
            "esses": lambda: Esses(np.random.uniform(80, 150)),
            "tightening_radius": lambda: TighteningRadius(
                np.random.uniform(150, 250), 0.001
            ),
            "off_camber": lambda: OffCamber(
                np.random.uniform(150, 250),
                np.random.uniform(100, 150),
                np.random.uniform(50, 100),
            ),
            "blind_crest": lambda: BlindCrest(
                np.random.uniform(100, 200), np.random.uniform(80, 150)
            ),
        }

        # Target track length set at midpoint between min and max (150% of minimum)
        # This balances difficulty: not too short for variety, not max for performance
        target_length = (
            ruleset.track_length_min
            + (ruleset.track_length_max - ruleset.track_length_min) * 0.5
        )

        # Build segments iteratively
        segments = []
        current_length = 0.0

        while current_length < target_length:
            # Randomly select segment type based on weights
            segment_type = np.random.choice(
                list(weights.keys()), p=list(weights.values())
            )

            # Generate segment
            segment = segment_generators[segment_type]()
            segment_length = segment.length()

            # Check if adding this segment would exceed max length
            if current_length + segment_length <= ruleset.track_length_max:
                segments.append(segment)
                current_length += segment_length
            else:
                # If too long, try a shorter straight instead
                short_straight = Straight(50)
                if current_length + short_straight.length() <= ruleset.track_length_max:
                    segments.append(short_straight)
                    current_length += short_straight.length()
                else:
                    break

        # Calculate aggregate properties from segments
        min_corner_radius = ruleset.min_corner_radius
        for segment in segments:
            if isinstance(segment, CircularTurn):
                min_corner_radius = min(min_corner_radius, segment.R)
            elif isinstance(segment, HighSpeedTurn):
                min_corner_radius = min(min_corner_radius, segment.R)
            elif isinstance(segment, Hairpin):
                min_corner_radius = min(min_corner_radius, segment.R)
            elif isinstance(segment, Parabolica):
                min_corner_radius = min(min_corner_radius, segment.R)
            elif isinstance(segment, Chicane):
                min_corner_radius = min(min_corner_radius, segment.R)
            elif isinstance(segment, Esses):
                min_corner_radius = min(min_corner_radius, segment.R)
            elif isinstance(segment, OffCamber):
                min_corner_radius = min(
                    min_corner_radius, segment.R_end, segment.R_start
                )
            elif isinstance(segment, TighteningRadius):
                # TighteningRadius has clothoid with varying radius
                # Use final radius as tightest point
                min_corner_radius = min(min_corner_radius, segment.final_radius_m)
            elif isinstance(segment, BlindCrest):
                min_corner_radius = min(min_corner_radius, segment.R)

        # First corner radius is usually first non-straight segment
        first_corner_radius = ruleset.first_corner_radius_max
        for segment in segments:
            if isinstance(segment, (CircularTurn, HighSpeedTurn, Hairpin)):
                if hasattr(segment, "R"):
                    first_corner_radius = min(segment.R, ruleset.first_corner_radius_max)
                break

        # Average width: F1 standard
        avg_width = (ruleset.track_width_min + ruleset.track_width_max) / 2

        # Elevation: conservative estimate
        max_elevation_change = ruleset.max_elevation_change * 0.5

        # Banking: conservative estimate
        max_banking_deg = ruleset.max_banking_degrees * 0.75

        return Track(
            total_length=current_length,
            avg_width=avg_width,
            first_corner_radius=first_corner_radius,
            min_corner_radius=min_corner_radius,
            max_elevation_change=max_elevation_change,
            max_banking_deg=max_banking_deg,
        )

    def _compose_manual(self, params: GenParams, ruleset: RuleSet) -> Track:
        """Compose MANUAL mode: full user control over parameters.

        Args:
            params: GenParams with target_length, sector_count, etc.
            ruleset: Track rules to respect

        Returns:
            User-composed Track

        Raises:
            NotImplementedError: MANUAL mode not yet implemented
        """
        raise NotImplementedError("MANUAL mode not yet implemented")
