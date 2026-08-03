"""
PACE journey — straight-line running-track roadmap (replaces the flight path).
8 stages: Warm-up Exercise → Training → Reflect → Implement Change → Reflect
          → Training - Tempo → Race 'up your PACE' → Finish Line
"""
from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle, Ellipse

from .engine import DepartmentJourney, STAGE_TO_INDEX, ACTIVATION_THRESHOLD, COLOUR_HEX, badges_earned
from ..config_loader import BRAND

BG_TOP = "#EAF3FB"; BG_BOTTOM = "#F7FAFD"
NAVY = "#1F3864"; NAVY_MID = "#3D5A80"; GOLD = "#BF9000"; GOLD_SOFT = "#E8C766"
GREEN = "#548235"; GREEN_SOFT = "#8FBE6D"; GREY_MUTE = "#B8C1CC"; GREY_TEXT = "#4A5568"
WHITE = "#FFFFFF"; TRACK = "#C0522D"; TRACK_DK = "#A8461F"; LANE = "#E8E8E8"

# 8 running stages in a straight line
STAGE_SHORT = [
    "Warm-up\nExercise", "Training", "Reflect", "Implement\nChange",
    "Reflect", "Training\nTempo", "Race up\nyour PACE", "Finish\nLine",
]
# maps to engine PACE_STAGES indices 1..8
ENGINE_STAGES = [
    "Warm-up Exercise", "Training", "Reflect", "Implement Change",
    "Reflect Again", "Training - Tempo", "Race up your PACE", "Finish Line",
]


def _runner(ax, cx, cy, colour, size=1.0, alpha=1.0):
    """A clean, dynamic running figure (side profile, mid-stride)."""
    s = size
    # shadow
    ax.add_patch(Ellipse((cx, cy - 2.2 * s), 2.6 * s, 0.5 * s, facecolor="#0B2545",
                         edgecolor="none", alpha=0.12 * alpha, zorder=8))
    # head
    ax.add_patch(Circle((cx + 0.55 * s, cy + 1.9 * s), 0.55 * s, facecolor=colour,
                        edgecolor=WHITE, linewidth=1.2, alpha=alpha, zorder=11))
    # torso (leaning forward)
    torso = [(cx + 0.35 * s, cy + 1.5 * s), (cx + 0.6 * s, cy + 1.4 * s),
             (cx + 0.15 * s, cy - 0.2 * s), (cx - 0.15 * s, cy - 0.1 * s)]
    ax.add_patch(Polygon(torso, closed=True, facecolor=colour, edgecolor=WHITE,
                        linewidth=1.0, alpha=alpha, zorder=10))
    lw = max(1.6, 2.2 * s)
    # arms (pumping)
    ax.plot([cx + 0.45 * s, cx + 1.15 * s], [cy + 1.2 * s, cy + 1.55 * s],
            color=colour, linewidth=lw, solid_capstyle="round", alpha=alpha, zorder=10)
    ax.plot([cx + 0.35 * s, cx - 0.35 * s], [cy + 1.0 * s, cy + 0.5 * s],
            color=colour, linewidth=lw, solid_capstyle="round", alpha=alpha, zorder=10)
    # legs (mid-stride)
    ax.plot([cx + 0.05 * s, cx + 0.9 * s], [cy - 0.1 * s, cy - 1.9 * s],
            color=colour, linewidth=lw, solid_capstyle="round", alpha=alpha, zorder=10)
    ax.plot([cx - 0.05 * s, cx - 0.8 * s], [cy - 0.05 * s, cy - 1.7 * s],
            color=colour, linewidth=lw, solid_capstyle="round", alpha=alpha, zorder=10)


def _draw_background(ax):
    n = 100
    for i in range(n):
        t = i / n
        def hx(a, b, t): return int(int(a, 16) * (1 - t) + int(b, 16) * t)
        r = hx(BG_TOP[1:3], BG_BOTTOM[1:3], t); g = hx(BG_TOP[3:5], BG_BOTTOM[3:5], t)
        b = hx(BG_TOP[5:7], BG_BOTTOM[5:7], t)
        ax.add_patch(Rectangle((0, 60 - t * 60), 100, 60 / n,
                                 facecolor=f"#{r:02X}{g:02X}{b:02X}", edgecolor="none", zorder=0))


def _draw_track(ax, x0, x1, y):
    """A straight running track band with lane lines."""
    h = 6.0
    ax.add_patch(FancyBboxPatch((x0 - 2, y - h/2), (x1 - x0) + 4, h,
                                boxstyle="round,pad=0.2,rounding_size=1.2",
                                facecolor=TRACK, edgecolor=TRACK_DK, linewidth=1.5, zorder=2))
    # lane lines
    for dy in (-h/2 + 1.5, 0, h/2 - 1.5):
        ax.plot([x0 - 1, x1 + 1], [y + dy, y + dy], color=WHITE, linewidth=1.0, alpha=0.5,
                zorder=3, dashes=(6, 5))
    # start line
    for k in range(6):
        ax.add_patch(Rectangle((x0 - 1.6, y - h/2 + k * (h/6)), 0.8, h/6,
                                facecolor=(WHITE if k % 2 == 0 else "#111"), edgecolor="none", zorder=3))
    # finish line (checkered)
    for k in range(6):
        ax.add_patch(Rectangle((x1 + 0.8, y - h/2 + k * (h/6)), 1.2, h/6,
                                facecolor=(WHITE if k % 2 == 0 else "#111"), edgecolor="none", zorder=3))


def _milestone(ax, cx, cy, index, state):
    if state == "current":
        for r, a in [(3.4, 0.10), (2.9, 0.18), (2.5, 0.28)]:
            ax.add_patch(Circle((cx, cy), r, facecolor=GOLD, edgecolor="none", alpha=a, zorder=6))
    if state == "completed":
        ax.add_patch(Circle((cx, cy), 1.7, facecolor=GREEN, edgecolor=WHITE, linewidth=2.0, zorder=7))
        ax.plot([cx - 0.65, cx - 0.12, cx + 0.85], [cy + 0.1, cy - 0.55, cy + 0.55],
                color=WHITE, linewidth=2.4, solid_capstyle="round", solid_joinstyle="round", zorder=8)
    elif state == "current":
        ax.add_patch(Circle((cx, cy), 2.05, facecolor=WHITE, edgecolor=GOLD, linewidth=2.8, zorder=7))
        ax.text(cx, cy, str(index), fontsize=12, ha="center", va="center", color=NAVY, fontweight="bold", zorder=8)
    else:
        ax.add_patch(Circle((cx, cy), 1.7, facecolor=WHITE, edgecolor=GREY_MUTE, linewidth=1.7, zorder=7))
        ax.text(cx, cy, str(index), fontsize=10.5, ha="center", va="center", color=GREY_MUTE, fontweight="bold", zorder=8)


def _milestone_label(ax, cx, cy, label, above, state):
    y_off = 5.4 if above else -5.4; ly = cy + y_off
    line_col = GREEN if state == "completed" else (GOLD if state == "current" else GREY_MUTE)
    ax.plot([cx, cx], [cy + (2.3 if above else -2.3), ly - (0.8 if above else -0.8)],
            color=line_col, linewidth=1.3, linestyle=("-" if state != "upcoming" else ":"),
            zorder=6, alpha=0.75)
    fw = "bold" if state != "upcoming" else "normal"
    col = NAVY if state != "upcoming" else GREY_TEXT
    ax.text(cx, ly, label, fontsize=8.2, ha="center", va=("bottom" if above else "top"),
            color=col, fontweight=fw, zorder=8,
            bbox=dict(boxstyle="round,pad=0.32", facecolor=WHITE, edgecolor=line_col, linewidth=1.0))


def render_pace_journey(dept, medal_override=None):
    fig, ax = plt.subplots(figsize=(15, 7))
    fig.patch.set_facecolor(WHITE)
    ax.set_xlim(0, 100); ax.set_ylim(0, 60); ax.set_aspect("equal"); ax.axis("off")
    _draw_background(ax)

    # Header
    ax.add_patch(Rectangle((0, 55), 100, 5, facecolor=NAVY, edgecolor="none", zorder=15))
    ax.add_patch(Rectangle((0, 54.6), 100, 0.4, facecolor=GOLD, edgecolor="none", zorder=15))
    ax.text(2, 57.5, f"PACE — {dept.dept_name.upper()}", fontsize=13, color=WHITE,
            fontweight="bold", va="center", zorder=16)
    ax.text(2, 56.0, BRAND, fontsize=8.5, color="#D9E2F3", va="center", style="italic", zorder=16)
    runner_hex = COLOUR_HEX.get(dept.runner_colour, NAVY)
    ax.text(98, 57.5, dept.dept_code, fontsize=11, ha="right", va="center", color=runner_hex,
            fontweight="bold", zorder=16,
            bbox=dict(boxstyle="round,pad=0.4", facecolor=WHITE, edgecolor=runner_hex, linewidth=1.6))

    # Progress bar
    stage_idx = STAGE_TO_INDEX.get(dept.stage, 0)   # 0..8
    n = 8
    progress = min(1.0, max(0.0, (stage_idx - 1) / max(n - 1, 1))) if stage_idx > 0 else 0.0
    ax.add_patch(FancyBboxPatch((3, 50.5), 60, 0.9, boxstyle="round,pad=0.02,rounding_size=0.45",
                                facecolor="#E0E4EA", edgecolor="none", zorder=6))
    ax.add_patch(FancyBboxPatch((3, 50.5), max(0.05, 60 * progress), 0.9,
                                boxstyle="round,pad=0.02,rounding_size=0.45",
                                facecolor=GOLD, edgecolor="none", zorder=7))
    ax.text(65, 50.95, f"{int(progress*100)}% complete · Stage {max(stage_idx,1)} of {n}",
            fontsize=9, va="center", color=NAVY, fontweight="bold", zorder=8)

    # Straight-line track with 8 evenly spaced milestones
    x0, x1 = 12, 88
    xs = np.linspace(x0, x1, n)
    y = 30
    _draw_track(ax, x0, x1, y)

    current_ms = max(0, stage_idx - 1)
    if stage_idx == 0: current_ms = 0

    for i, cx in enumerate(xs):
        if stage_idx == 0: state = "upcoming"
        elif i < current_ms: state = "completed"
        elif i == current_ms and stage_idx == n: state = "completed"
        elif i == current_ms: state = "current"
        else: state = "upcoming"
        # place label below for the active milestone so the runner has room above
        above = (i % 2 == 0)
        if state == "current" and stage_idx < n:
            above = False
        _milestone(ax, cx, y, index=i + 1, state=state)
        _milestone_label(ax, cx, y, STAGE_SHORT[i], above=above, state=state)

    # Runner sits above the current milestone
    if stage_idx > 0 and stage_idx < n:
        rcx = xs[current_ms]
        _runner(ax, rcx, y + 4.6, colour=runner_hex, size=1.2)
        ax.text(rcx, y + 8.0, dept.dept_code, fontsize=7.5, ha="center", va="center",
                color=WHITE, fontweight="bold", zorder=13,
                bbox=dict(boxstyle="round,pad=0.25", facecolor=runner_hex, edgecolor=WHITE, linewidth=0.8))
    elif stage_idx == n:
        # crossed the finish line
        _runner(ax, xs[-1] + 3.5, y + 4.6, colour=runner_hex, size=1.3)

    # Footer strip
    ax.add_patch(Rectangle((0, 0), 100, 4.5, facecolor=NAVY, edgecolor="none", zorder=14))
    completion_txt = f"{dept.actual} / {dept.expected} responses  ({dept.completion_pct:.0%})"
    activation_txt = "In Training (≥70%)" if dept.is_activated else "Warming up (< 70%)"
    activation_col = GREEN_SOFT if dept.is_activated else GOLD_SOFT
    badges = badges_earned(dept)
    ax.text(2, 2.9, f"Participation:  {completion_txt}", fontsize=9, color=WHITE,
            fontweight="bold", va="center", zorder=15)
    ax.add_patch(Circle((2.5, 1.3), 0.25, facecolor=activation_col, edgecolor="none", zorder=15))
    ax.text(3.4, 1.3, activation_txt, fontsize=8.5, color=activation_col, fontweight="bold", va="center", zorder=15)
    ax.text(50, 2.9, f"Current stage:  {dept.stage_display}", fontsize=9, color=WHITE,
            fontweight="bold", va="center", zorder=15)
    ax.text(50, 1.3, f"Runner:  {dept.runner_type}  ·  {dept.runner_colour}",
            fontsize=8.5, color="#B4C7E7", va="center", zorder=15)
    ax.text(98, 2.9, f"{len(badges)} of 9 badges earned", fontsize=9, color=GOLD_SOFT,
            fontweight="bold", ha="right", va="center", zorder=15)
    ax.text(98, 1.3, ("PACE Setter — Finished!" if len(badges) >= 9 else "Keep your PACE"),
            fontsize=8.5, color="#B4C7E7", ha="right", va="center", zorder=15)

    plt.tight_layout(pad=0)
    return fig
