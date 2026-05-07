"""Plotly figure builders. Pure functions: TrackGeometry + speed_profile → Figure."""
import numpy as np
import plotly.graph_objects as go

from .geometry import TrackGeometry


def build_2d_map_figure(geometry: TrackGeometry, speed_profile: dict) -> go.Figure:
    """Top-down centerline scatter, colored by speed."""
    speeds = speed_profile["speed_kmh"]
    fig = go.Figure()
    # Invisible base line for hover area
    fig.add_trace(go.Scatter(
        x=geometry.x,
        y=geometry.y,
        mode="lines",
        line=dict(width=4, color="rgba(0,0,0,0)"),
        showlegend=False,
        hoverinfo="skip",
    ))
    # Speed-colored markers
    fig.add_trace(go.Scatter(
        x=geometry.x,
        y=geometry.y,
        mode="markers",
        marker=dict(
            size=4,
            color=speeds,
            colorscale="RdYlGn",
            colorbar=dict(title="Speed (km/h)"),
            showscale=True,
        ),
        text=[
            f"s={s:.0f}m<br>v={v:.1f} km/h<br>{lbl}<br>κ={c:.4f}"
            for s, v, lbl, c in zip(
                geometry.s, speeds, geometry.segment_labels, geometry.curvature
            )
        ],
        hoverinfo="text",
        showlegend=False,
    ))
    fig.update_layout(
        title="Track Map (color = speed)",
        xaxis_title="x (m)",
        yaxis_title="y (m)",
        yaxis=dict(scaleanchor="x", scaleratio=1),
        hovermode="closest",
    )
    return fig


def build_3d_figure(geometry: TrackGeometry, speed_profile: dict) -> go.Figure:
    """3D scatter: XY + elevation Z, colored by speed."""
    speeds = speed_profile["speed_kmh"]
    fig = go.Figure(data=[go.Scatter3d(
        x=geometry.x,
        y=geometry.y,
        z=geometry.elevation,
        mode="markers",
        marker=dict(
            size=2,
            color=speeds,
            colorscale="RdYlGn",
            showscale=True,
            colorbar=dict(title="Speed (km/h)"),
        ),
        text=[
            f"s={s:.0f}m<br>z={z:.1f}m<br>v={v:.1f} km/h"
            for s, z, v in zip(geometry.s, geometry.elevation, speeds)
        ],
        hoverinfo="text",
    )])
    fig.update_layout(
        title="3D Track View",
        scene=dict(
            xaxis_title="x (m)",
            yaxis_title="y (m)",
            zaxis_title="elevation (m)",
            aspectmode="data",
        ),
    )
    return fig


def build_speed_profile_figure(geometry: TrackGeometry, speed_profile: dict) -> go.Figure:
    """Line chart of speed vs distance along track."""
    fig = go.Figure(data=[go.Scatter(
        x=geometry.s,
        y=speed_profile["speed_kmh"],
        mode="lines",
        line=dict(color="firebrick"),
        name="speed",
    )])
    fig.update_layout(
        title="Speed vs s",
        xaxis_title="s (m)",
        yaxis_title="speed (km/h)",
    )
    return fig


def build_curvature_profile_figure(geometry: TrackGeometry) -> go.Figure:
    """Line chart of curvature vs distance along track."""
    fig = go.Figure(data=[go.Scatter(
        x=geometry.s,
        y=geometry.curvature,
        mode="lines",
        line=dict(color="steelblue"),
        name="curvature",
    )])
    fig.update_layout(
        title="Curvature vs s",
        xaxis_title="s (m)",
        yaxis_title="κ (1/m)",
    )
    return fig


def build_elevation_profile_figure(geometry: TrackGeometry) -> go.Figure:
    """Line chart of elevation vs distance along track."""
    fig = go.Figure(data=[go.Scatter(
        x=geometry.s,
        y=geometry.elevation,
        mode="lines",
        line=dict(color="darkgreen"),
        name="elevation",
    )])
    fig.update_layout(
        title="Elevation vs s",
        xaxis_title="s (m)",
        yaxis_title="z (m)",
    )
    return fig


def build_segment_breakdown_figure(segments: list) -> go.Figure:
    """Pie chart of segment-type distribution by length."""
    by_type: dict[str, float] = {}
    for seg in segments:
        name = type(seg).__name__
        by_type[name] = by_type.get(name, 0.0) + seg.length()
    fig = go.Figure(data=[go.Pie(
        labels=list(by_type.keys()),
        values=list(by_type.values()),
        hole=0.4,
    )])
    fig.update_layout(title="Segment composition (by length)")
    return fig
