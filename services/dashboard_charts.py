# services/dashboard_charts.py
# Reusable chart builders for the LC Pipeline dashboard.
# Each function accepts a filtered DataFrame and returns a matplotlib Figure.
# Used by: notebooks/06_visualization.ipynb AND streamlit_apps/*.py
#
# Architectural notes:
# - Functions accept df (the filtered data), never load CSV themselves
# - Functions return fig (the matplotlib Figure), never call plt.show()
# - Colors come from constants.PIPELINE_PALETTE (single source of truth)
# - Each function = ONE chart (single responsibility principle)


from __future__ import annotations
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

from config.constants import PIPELINE_PALETTE, SEVERITY_COLORS

import io


def figure_to_png_bytes(fig: plt.Figure, dpi: int = 150) -> bytes:
    """Render a matplotlib Figure to PNG bytes for st.image().

    Used to get exact pixel control in Streamlit — bypasses st.pyplot's
    browser-scaling behavior on high-DPI monitors.

    Args:
        fig: matplotlib Figure to render.
        dpi: Dots per inch for the rendered image.

    Returns:
        PNG image as bytes.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor='white')
    buf.seek(0)
    return buf.getvalue()

# Add this function to services/dashboard_charts.py
# Same file as build_pareto_chart — just append at the bottom

# Update services/dashboard_charts.py — TWO functions, same change
# Both functions get an explicit `dpi` parameter passed to plt.subplots

def build_status_donut(
    df: pd.DataFrame,
    *,
    figsize: tuple[float, float] = (3.5, 3),
    dpi: int = 150,
) -> plt.Figure:
    """Build the 'Clean vs Flagged' donut chart with RAG colors."""
    status_counts = df['validation_status'].value_counts()

    # dpi=150 + small figsize = sharp small image, monitor-agnostic
    fig, ax = plt.subplots(figsize=figsize, facecolor='white', dpi=dpi)

    STATUS_COLORS = {
        'CLEAN':   PIPELINE_PALETTE['clean'],
        'FLAGGED': PIPELINE_PALETTE['flagged'],
    }
    donut_colors = [STATUS_COLORS[status] for status in status_counts.index]

    wedges, texts, autotexts = ax.pie(
        status_counts.values,
        labels=status_counts.index,
        colors=donut_colors,
        autopct='%1.0f%%',
        startangle=90,
        wedgeprops=dict(width=0.35, edgecolor='white', linewidth=2),
        textprops=dict(fontsize=10),
    )

    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_color(PIPELINE_PALETTE['primary'])

    ax.set_title(
        f'Clean vs Flagged ({len(df)} LCs)',
        fontsize=11,
        fontweight='bold',
    )

    fig.tight_layout()
    return fig


def build_pareto_chart(
    df: pd.DataFrame,
    *,
    figsize: tuple[float, float] = (5, 3),
    dpi: int = 150,
) -> plt.Figure:
    """Build the 'Errors by Validator' Pareto bar chart."""
    errors = (
        df.dropna(subset=['error_codes'])
          ['error_codes']
          .str.split(', ')
          .explode()
          .str.extract(r'^([A-Z]+)', expand=False)
          .value_counts()
    )

    fig, ax = plt.subplots(figsize=figsize, facecolor='white', dpi=dpi)

    bar_colors = [PIPELINE_PALETTE['flagged']] * len(errors)
    bars = ax.bar(errors.index, errors.values, color=bar_colors)
    ax.bar_label(bars, padding=3, fontsize=8)

    ax.set_title(
        f'Errors by Validator ({errors.sum()} total)',
        fontsize=11,
        fontweight='bold',
    )
    ax.set_xlabel('Validator', fontsize=9)
    ax.set_ylabel('Error Count', fontsize=9)

    ax.tick_params(axis='both', labelsize=8)
    ax.grid(axis='y', alpha=0.3, color=PIPELINE_PALETTE['secondary'])
    ax.grid(axis='x', visible=False)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    return fig

# Append to services/dashboard_charts.py — below build_pareto_chart
def build_severity_bars(
        df: pd.DataFrame,
        *,
        figsize: tuple[float, float] = (5,3),
        dpi: int = 100,

) -> plt.Figure:

    """Build the 'Errors by Severity' bar chart with RAG colors.

        Bars are color-coded by their severity using SEVERITY_COLORS dict
        lookup — order-independent, no positional bugs.

        Args:
            df: DataFrame with 'severity' column (string values like
                'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', or 'NONE' for clean).
            figsize: Figure size in inches.
            dpi: Resolution. Default 100 — actual display size controlled
                by st.image(width=N) downstream.

        Returns:
            matplotlib Figure with the chart drawn on it.
    """
    # Filter to actual severities (drop 'NONE' = clean rows)
    severity_counts = (
        df[df['severity'] != 'NONE']['severity']
        .value_counts()
    )

    fig, ax = plt.subplots(figsize=figsize, facecolor='white', dpi=dpi)

    # Color lookup by severity label (NOT by position)
    bar_colors = [SEVERITY_COLORS[sev] for sev in severity_counts.index]

    bars = ax.bar(
        severity_counts.index,
        severity_counts.values,
        color=bar_colors
    )
    ax.bar_label(bars, padding=3, fontsize=9)

    ax.set_title(
        f'Errors by Severity ({severity_counts.sum()} flagged)',
        fontsize=11,
        fontweight='bold',
    )
    ax.set_xlabel('Severity', fontsize=9)
    ax.set_ylabel('Error Count', fontsize=9)

    ax.tick_params(axis='both', labelsize=8)
    ax.grid(axis='y', alpha=0.3, color=PIPELINE_PALETTE['secondary'])
    ax.grid(axis='x', visible=False)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    return fig


# Append to services/dashboard_charts.py — final chart function

def build_country_bars(
    df: pd.DataFrame,
    *,
    figsize: tuple[float, float] = (6, 4),
    dpi: int = 100,
    top_n: int = 8,
) -> plt.Figure:
    """Build the 'Top Countries — Flagged LCs' horizontal bar chart.

    Includes dynamic annotation pointing at the dominant country with
    its percentage share.

    Args:
        df: DataFrame with 'validation_status' and 'applicant_country'.
        figsize: Figure size in inches.
        dpi: Resolution.
        top_n: Number of countries to display (default 8).

    Returns:
        matplotlib Figure with chart + annotation.
    """
    # Filter to flagged LCs, count by country, take top N
    flagged_by_country = (
        df[df['validation_status'] == 'FLAGGED']
          ['applicant_country']
          .value_counts()
          .head(top_n)
          .sort_values(ascending=True)   # ascending for barh = biggest on top
    )

    fig, ax = plt.subplots(figsize=figsize, facecolor='white', dpi=dpi)

    bars = ax.barh(
        flagged_by_country.index,
        flagged_by_country.values,
        color=PIPELINE_PALETTE['flagged'],
    )
    ax.bar_label(bars, padding=3, fontsize=8)

    # Dynamic annotation — compute top country's share
    # In services/dashboard_charts.py — UPDATE build_country_bars
    # Find the annotation block and replace it with this version

    # In services/dashboard_charts.py — FIX the annotation block again
    # Use position 2.5 from bottom (lower-middle area, away from top bars)

    if len(flagged_by_country) > 0:
        top_country = flagged_by_country.idxmax()
        top_count = flagged_by_country.max()
        top_pct = (top_count / flagged_by_country.sum()) * 100

        # Y anchor in LOWER half — empty space below the dominant bars
        # 2.5 = between 3rd and 4th bar from bottom (clean gap)
        n_bars = len(flagged_by_country)
        y_anchor = n_bars * 0.3  # 30% up = lower-middle

        ax.annotate(
            text=f'{top_pct:.0f}% of flagged LCs\n← train branch ops',
            xy=(top_count, top_country),
            xytext=(top_count * 0.55, y_anchor),  # 55% along X, 30% up Y
            fontsize=8,
            color=PIPELINE_PALETTE['primary'],
            fontweight='bold',
            arrowprops=dict(
                arrowstyle='->',
                color=PIPELINE_PALETTE['primary'],
                lw=1.0,
            ),
        )

    ax.set_title(
        'Top Countries — Flagged LCs',
        fontsize=11,
        fontweight='bold',
    )
    ax.set_xlabel('Flagged Count', fontsize=9)
    ax.set_ylabel('Applicant Country', fontsize=9)

    ax.tick_params(axis='both', labelsize=8)
    # For HORIZONTAL bars, grid on X-axis (where values are)
    ax.grid(axis='x', alpha=0.3, color=PIPELINE_PALETTE['secondary'])
    ax.grid(axis='y', visible=False)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    return fig