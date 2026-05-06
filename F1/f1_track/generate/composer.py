"""Track composer: combines parameters and rulesets into ready-made tracks."""
from f1_track.generate.params import GenParams, Mode
from f1_track.generate.templates import create_demo_track
from f1_track.geometry.track import Track
from f1_track.rules import RuleSet


class TrackComposer:
    """Compose tracks from generation parameters and rulesets.

    Supports three composition modes:
    - DEMO: Returns a predefined demo track
    - AUTO: Automatic generation with difficulty level (TODO)
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

        Args:
            params: GenParams with difficulty level
            ruleset: Track rules to respect

        Returns:
            Auto-generated Track

        Raises:
            NotImplementedError: AUTO mode not yet implemented
        """
        raise NotImplementedError("AUTO mode not yet implemented")

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
