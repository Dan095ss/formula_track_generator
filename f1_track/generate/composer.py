"""Track composer: combines parameters and rulesets into ready-made tracks."""
import numpy as np
from f1_track.generate.params import GenParams, Mode
from f1_track.generate.templates import create_demo_track, create_demo_segments
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

    def _build_segments(self, params: GenParams, ruleset: RuleSet) -> list:
        """Build the ordered segment list for the given params and ruleset.

        Args:
            params: Generation parameters specifying mode and config
            ruleset: Track rules and constraints

        Returns:
            Ordered list of Segment instances
        """
        if params.mode == Mode.DEMO:
            return create_demo_segments()
        elif params.mode == Mode.AUTO:
            return self._build_auto_segments(params, ruleset)
        elif params.mode == Mode.MANUAL:
            return self._build_manual_segments(params, ruleset)
        else:
            raise ValueError(f"Unknown mode: {params.mode}")

    def _track_from_segments(
        self, segments: list, ruleset: RuleSet, params: GenParams
    ) -> Track:
        """Compute Track aggregate properties from a segment list.

        For DEMO mode the aggregate values are fixed constants (not derived
        from segments) to preserve backwards-compatibility.

        Args:
            segments: Ordered list of Segment instances
            ruleset: Track rules and constraints
            params: Generation parameters (used to determine mode)

        Returns:
            Track instance with aggregate properties
        """
        if params.mode == Mode.DEMO:
            return create_demo_track()

        current_length = sum(seg.length() for seg in segments)

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
                # Final radius at tightest point: 1 / (k * L)
                final_radius_m = 1.0 / (segment.k * segment.L)
                min_corner_radius = min(min_corner_radius, final_radius_m)
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

        if params.mode == Mode.AUTO:
            # Elevation: conservative estimate
            max_elevation_change = ruleset.max_elevation_change * 0.5
            # Banking: conservative estimate
            max_banking_deg = ruleset.max_banking_degrees * 0.75
        else:
            # MANUAL: elevation based on elevation_style
            elevation_change_ranges = {
                "flat": (0, 20),
                "hilly": (40, 60),
                "mountainous": (70, 90),
            }
            elev_min, elev_max = elevation_change_ranges.get(
                params.elevation_style, (40, 60)
            )
            max_elevation_change = np.random.uniform(elev_min, elev_max)
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

    def _compose_demo(self) -> Track:
        """Compose DEMO mode: return predefined demo track."""
        return create_demo_track()

    def _compose_auto(self, params: GenParams, ruleset: RuleSet) -> Track:
        """Compose AUTO mode: automatic generation with difficulty level."""
        segments = self._build_auto_segments(params, ruleset)
        return self._track_from_segments(segments, ruleset, params)

    def _compose_manual(self, params: GenParams, ruleset: RuleSet) -> Track:
        """Compose MANUAL mode: full user control over parameters."""
        segments = self._build_manual_segments(params, ruleset)
        return self._track_from_segments(segments, ruleset, params)

    def _build_auto_segments(self, params: GenParams, ruleset: RuleSet) -> list:
        """Build segment list for AUTO mode."""
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

        return segments

    def _build_manual_segments(self, params: GenParams, ruleset: RuleSet) -> list:
        """Build segment list for MANUAL mode."""
        # Map user-provided segment preference names to actual segment types
        segment_preference_map = {
            "hairpin": "hairpin",
            "chicane": "chicane",
            "high_speed": "high_speed_turn",
            "straight": "straight",
            "esses": "esses",
            "parabolica": "parabolica",
            "tightening_radius": "tightening_radius",
            "off_camber": "off_camber",
            "blind_crest": "blind_crest",
        }

        # Convert user preferences to normalized segment weights
        user_prefs = params.segment_preferences or {}
        segment_weights = {}
        total_weight = 0

        for pref_name, pref_value in user_prefs.items():
            if pref_name in segment_preference_map:
                segment_type = segment_preference_map[pref_name]
                segment_weights[segment_type] = pref_value
                total_weight += pref_value

        # Normalize weights to sum to 1.0
        if total_weight > 0:
            segment_weights = {k: v / total_weight for k, v in segment_weights.items()}

        # Elevation style affects segment length ranges
        elevation_ranges = {
            "flat": (150, 400),
            "hilly": (200, 500),
            "mountainous": (300, 600),
        }

        seg_len_min, seg_len_max = elevation_ranges.get(params.elevation_style, (200, 500))

        # Segment generator functions with length range consideration
        segment_generators = {
            "straight": lambda: Straight(np.random.uniform(seg_len_min, seg_len_max)),
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
                np.random.uniform(seg_len_min, seg_len_max),
                np.random.uniform(100, 150),
                np.random.uniform(50, 100),
            ),
            "blind_crest": lambda: BlindCrest(
                np.random.uniform(seg_len_min, seg_len_max), np.random.uniform(80, 150)
            ),
        }

        # Target length at 95% of desired to leave margin for final adjustments
        target_length = params.target_length * 0.95

        # Build segments iteratively according to weighted preferences
        segments = []
        current_length = 0.0

        while current_length < target_length:
            # Randomly select segment type based on user preferences
            if segment_weights:
                segment_type = np.random.choice(
                    list(segment_weights.keys()), p=list(segment_weights.values())
                )
            else:
                # Fallback if no preferences specified (shouldn't happen in validation)
                segment_type = "straight"

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

        return segments
