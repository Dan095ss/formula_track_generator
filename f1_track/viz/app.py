"""Streamlit application entry point.

Run with: streamlit run f1_track/viz/app.py
Or via console script: f1track-app
"""
from __future__ import annotations

import sys

try:
    import streamlit as st
except ImportError:
    print(
        "ERROR: streamlit is not installed.\n"
        "Install with: pip install streamlit",
        file=sys.stderr,
    )
    raise

import numpy as np
from pydantic import ValidationError as PydanticValidationError

from f1_track.generate import GenParams, Mode, TrackComposer
from f1_track.rules import create_ruleset_f1_grade1
from f1_track.geometry.validate import TrackValidator, ValidationError as FIAValidationError
from f1_track.viz import (
    build_2d_map_figure,
    build_3d_figure,
    build_speed_profile_figure,
    build_curvature_profile_figure,
    build_elevation_profile_figure,
    build_segment_breakdown_figure,
)


SEG_PREF_KEYS = [
    "straight", "high_speed", "hairpin", "chicane", "esses",
    "parabolica", "tightening_radius", "off_camber", "blind_crest", "circular_turn",
]


def _render_sidebar():
    """Render parameter form. Returns (params, seed) on submit, else None."""
    st.sidebar.header("Track Parameters")
    mode_label = st.sidebar.radio("Mode", ["DEMO", "AUTO", "MANUAL"], index=1)
    mode = Mode[mode_label]

    difficulty = None
    target_length = None
    sector_count = None
    segment_preferences = None
    elevation_style = None

    if mode == Mode.AUTO:
        difficulty = st.sidebar.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
    elif mode == Mode.MANUAL:
        target_length = float(st.sidebar.slider("Target length (m)", 3500, 7000, 5500, step=100))
        sector_count = int(st.sidebar.slider("Sector count", 2, 6, 3))
        elevation_style = st.sidebar.selectbox(
            "Elevation style", ["flat", "hilly", "mountainous"], index=1
        )
        st.sidebar.markdown("**Segment preferences (0..1)**")
        segment_preferences = {}
        for key in SEG_PREF_KEYS:
            v = st.sidebar.slider(key, 0.0, 1.0, 0.3 if key == "straight" else 0.1, step=0.05)
            if v > 0:
                segment_preferences[key] = v

    seed_input = st.sidebar.number_input(
        "Seed (0 = random)", min_value=0, max_value=10_000, value=0, step=1
    )
    seed = int(seed_input) if seed_input != 0 else int(np.random.randint(1, 10_000))

    if st.sidebar.button("Generate Track", type="primary"):
        try:
            params = GenParams(
                mode=mode,
                ruleset_name="f1_grade1",
                difficulty=difficulty,
                target_length=target_length,
                sector_count=sector_count,
                segment_preferences=segment_preferences if segment_preferences else None,
                elevation_style=elevation_style,
            )
            return params, seed
        except PydanticValidationError as e:
            st.sidebar.error(f"Invalid parameters:\n{e}")
            return None
    return None


@st.cache_data(show_spinner=False)
def _generate(_params_dict: dict, seed: int):
    """Cached generation. Cache key is (params dict, seed)."""
    params = GenParams(**_params_dict)
    composer = TrackComposer()
    ruleset = create_ruleset_f1_grade1()
    return composer.compose_full(params, ruleset, seed=seed)


def _render_stats(session) -> None:
    track = session.track
    speeds = session.speed_profile["speed_kmh"]
    lap_time = session.speed_profile["lap_time_s"]
    minutes = int(lap_time // 60)
    seconds = lap_time - minutes * 60

    cols = st.columns(5)
    cols[0].metric("Length (m)", f"{track.total_length:.0f}")
    cols[1].metric("Lap time", f"{minutes}:{seconds:05.2f}")
    cols[2].metric("Max speed", f"{speeds.max():.1f} km/h")
    cols[3].metric("Min speed", f"{speeds.min():.1f} km/h")
    cols[4].metric("Segments", f"{len(session.segments)}")

    try:
        TrackValidator(create_ruleset_f1_grade1()).validate(track)
        st.success("FIA Grade 1: PASS")
    except FIAValidationError as e:
        st.warning(f"FIA Grade 1: FAIL — {e}")


def _render_tabs(session) -> None:
    tab_map, tab_3d, tab_analysis = st.tabs(["Track Map", "3D View", "Analysis"])
    with tab_map:
        st.plotly_chart(
            build_2d_map_figure(session.geometry, session.speed_profile),
            use_container_width=True,
        )
    with tab_3d:
        st.plotly_chart(
            build_3d_figure(session.geometry, session.speed_profile),
            use_container_width=True,
        )
    with tab_analysis:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                build_speed_profile_figure(session.geometry, session.speed_profile),
                use_container_width=True,
            )
            st.plotly_chart(
                build_elevation_profile_figure(session.geometry),
                use_container_width=True,
            )
        with col2:
            st.plotly_chart(
                build_curvature_profile_figure(session.geometry),
                use_container_width=True,
            )
            st.plotly_chart(
                build_segment_breakdown_figure(session.segments),
                use_container_width=True,
            )


def main() -> None:
    st.set_page_config(page_title="F1 Track Generator", layout="wide")
    st.title("F1 Track Generator — Stage 5 Visualization")

    submission = _render_sidebar()
    if submission is not None:
        params, seed = submission
        try:
            session = _generate(params.model_dump(), seed)
            st.session_state["session"] = session
        except FIAValidationError as e:
            st.error(f"Track failed FIA validation: {e}")
            return
        except ValueError as e:
            st.error(f"Generation error: {e}")
            return

    if "session" in st.session_state:
        session = st.session_state["session"]
        _render_stats(session)
        _render_tabs(session)
        st.caption(f"Seed: {session.seed}")

        if st.button("Export to Assetto Corsa (Stage 6)"):
            st.info("Export will be implemented in Stage 6.")
    else:
        st.info("Configure parameters in the sidebar and click Generate Track.")


def run() -> None:
    """Entry point for the f1track-app console script."""
    import subprocess
    subprocess.run(
        ["streamlit", "run", __file__, "--server.headless=false"],
        check=True,
    )


if __name__ == "__main__":
    main()
