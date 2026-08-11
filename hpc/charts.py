"""Charts for the High Performance Diagnostic Tool. PACE. Robust + professional.

`polarisation_bar` is kept as a BACKWARDS-COMPAT alias -> variance_chart.
"""
from __future__ import annotations
import io
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from .config_loader import PILLARS

mpl.rcParams["font.family"] = "DejaVu Sans"
mpl.rcParams["axes.edgecolor"] = "#C9D2DE"

NAVY = "#1F3864"
GOLD = "#BF9000"
LOW_C = "#C0392B"
MID_C = "#C9CDD4"
HIGH_C = "#3F7D3A"


def _to_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def _style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8.5, colors="#333333")
    ax.grid(axis="y", color="#EAEEF3", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def radar_chart(focus, company, label="Selected", figsize=(5.6, 5.0)):
    labels = PILLARS
    ang = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist(); ang += ang[:1]
    dv = [float(focus[p]) for p in labels] + [float(focus[labels[0]])]
    cv = [float(company[p]) for p in labels] + [float(company[labels[0]])]
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("white")
    ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1)
    ax.plot(ang, cv, color=GOLD, linewidth=2.4, linestyle="--", label="Company", zorder=3)
    ax.plot(ang, dv, color=NAVY, linewidth=3.0, label=label, zorder=4, marker="o", markersize=5)
    ax.fill(ang, dv, color=NAVY, alpha=0.08, zorder=2)
    for a, v in zip(ang[:-1], dv[:-1]):
        ax.text(a, min(v + 0.6, 10.2), f"{v:.1f}", ha="center", va="center",
                fontsize=8.5, fontweight="bold", color=NAVY, zorder=5)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels, fontsize=11, fontweight="bold", color="#333")
    ax.set_yticks([2, 4, 6, 8, 10]); ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=8, color="#9AA5B1")
    ax.set_ylim(0, 10); ax.grid(color="#D9DFE7", linewidth=0.8)
    ax.set_title("PACE Radar — Selected vs Company", fontsize=12.5, fontweight="bold", color=NAVY, pad=18)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, frameon=False, fontsize=10)
    plt.tight_layout()
    return fig


def radar_chart_multi(depts, company, figsize=(6.0, 5.2)):
    labels = PILLARS
    ang = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist(); ang += ang[:1]
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1)
    cv = [float(company[p]) for p in labels] + [float(company[labels[0]])]
    ax.plot(ang, cv, color=GOLD, linewidth=2.4, linestyle="--", label="Company avg")
    palette = [NAVY, "#3F7D3A", LOW_C, "#7030A0", "#ED7D31"]
    for i, (dept, means) in enumerate(depts.items()):
        vals = [float(means[p]) for p in labels] + [float(means[labels[0]])]
        ax.plot(ang, vals, color=palette[i % len(palette)], linewidth=2.2, label=dept)
    ax.set_xticks(ang[:-1]); ax.set_xticklabels(labels, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 10); ax.grid(color="#D9DFE7")
    ax.set_title("PACE Radar — multi-department", fontsize=11, fontweight="bold", color=NAVY, pad=16)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False, fontsize=8)
    plt.tight_layout()
    return fig


def pillar_bar(pillar_means, company_means, figsize=(5.6, 4.2)):
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(PILLARS)); w = 0.38
    dv = [float(pillar_means[p]) for p in PILLARS]; cv = [float(company_means[p]) for p in PILLARS]
    ax.bar(x - w / 2, dv, w, color=NAVY, label="Selected", zorder=3)
    ax.bar(x + w / 2, cv, w, color=GOLD, alpha=0.75, label="Company", zorder=3)
    for i, v in enumerate(dv):
        ax.text(i - w / 2, v + 0.12, f"{v:.1f}", ha="center", fontsize=8.5, fontweight="bold", color=NAVY)
    ax.set_xticks(x); ax.set_xticklabels(PILLARS, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 10.5)
    ax.set_title("Element Means — Selected vs Company", fontsize=12.5, fontweight="bold", color=NAVY, pad=10)
    _style(ax); ax.legend(frameon=False, fontsize=9, loc="upper right")
    plt.tight_layout()
    return fig


def _dist_field(item, name, default=0.0):
    try:
        if isinstance(item, dict):
            return item.get(name, default)
        return getattr(item, name, default)
    except Exception:
        return default


def variance_chart(distribution, figsize=(5.8, 4.2)):
    """Robust distribution/variance chart: mean +/- 1 SD whiskers on health bands."""
    fig, ax = plt.subplots(figsize=figsize)
    pillars = [str(_dist_field(d, "pillar", "")) for d in distribution]
    means = [float(_dist_field(d, "mean", 0.0) or 0.0) for d in distribution]
    sds = [float(_dist_field(d, "std", 0.0) or 0.0) for d in distribution]
    x = list(range(len(pillars)))

    ax.axhspan(0, 4, color=LOW_C, alpha=0.06, zorder=0)
    ax.axhspan(4, 6, color="#F2C94C", alpha=0.06, zorder=0)
    ax.axhspan(6, 10, color=HIGH_C, alpha=0.06, zorder=0)

    for xi, m, s in zip(x, means, sds):
        lo = max(0.0, m - s); hi = min(10.0, m + s)
        col = LOW_C if m < 4.0 else (GOLD if m < 6.0 else HIGH_C)
        ax.plot([xi, xi], [lo, hi], color=col, linewidth=6, solid_capstyle="round", alpha=0.55, zorder=3)
        ax.plot([xi - 0.14, xi + 0.14], [lo, lo], color=col, linewidth=2, zorder=3)
        ax.plot([xi - 0.14, xi + 0.14], [hi, hi], color=col, linewidth=2, zorder=3)
        ax.scatter([xi], [m], s=110, color=col, edgecolor="white", linewidth=1.5, zorder=4)
        ax.text(xi + 0.22, m, f"{m:.1f}", va="center", fontsize=9, fontweight="bold", color="#333")
        ax.text(xi, hi + 0.25, f"SD {s:.1f}", ha="center", fontsize=7.5, color="#667")

    ax.set_xticks(x); ax.set_xticklabels(pillars, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 10.5); ax.set_ylabel("Score (mean +/- 1 SD)", fontsize=9)
    ax.set_title("Element Distribution & Variance", fontsize=12.5, fontweight="bold", color=NAVY, pad=10)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8.5, colors="#333333")
    ax.grid(axis="y", color="#EAEEF3", linewidth=0.8, zorder=0); ax.set_axisbelow(True)
    plt.tight_layout()
    return fig


# --- Backwards-compat alias ---
def polarisation_bar(distribution, figsize=(5.8, 4.2)):
    """Deprecated name. Routes to variance_chart so old calls don't crash."""
    return variance_chart(distribution, figsize=figsize)


def correlation_heatmap(corr, figsize=(5.2, 4.4)):
    fig, ax = plt.subplots(figsize=figsize)
    cmap = mpl.colors.LinearSegmentedColormap.from_list("h", [LOW_C, "#FFFFFF", NAVY])
    vals = np.asarray(corr.values, dtype=float)
    im = ax.imshow(vals, cmap=cmap, vmin=-1, vmax=1)
    ax.set_xticks(range(len(PILLARS))); ax.set_yticks(range(len(PILLARS)))
    ax.set_xticklabels(PILLARS, fontsize=9, fontweight="bold", rotation=20, ha="right")
    ax.set_yticklabels(PILLARS, fontsize=9, fontweight="bold")
    for i in range(len(PILLARS)):
        for j in range(len(PILLARS)):
            v = float(vals[i, j])
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=9.5, fontweight="bold",
                    color="white" if abs(v) > 0.55 else "#222")
    ax.set_title("Element Inter-Correlation", fontsize=12.5, fontweight="bold", color=NAVY, pad=10)
    fig.colorbar(im, ax=ax, shrink=0.8)
    plt.tight_layout()
    return fig


def ranking_bar(all_depts, company_overall, focus=None, figsize=None, max_rows=None):
    ordered = all_depts["Overall"].sort_values()
    if max_rows and len(ordered) > max_rows:
        keep = set(ordered.index[:max_rows // 2]) | set(ordered.index[-max_rows // 2:])
        if focus: keep.add(focus)
        ordered = ordered[[i in keep for i in ordered.index]]
    n = len(ordered)
    if figsize is None:
        figsize = (7.8, max(3.2, 0.34 * n + 1.0))
    fig, ax = plt.subplots(figsize=figsize)

    def band_col(v):
        return LOW_C if v < 4.0 else (GOLD if v < 6.0 else "#B4C7E7")
    colors = [NAVY if d == focus else band_col(float(v)) for d, v in ordered.items()]
    ax.barh(ordered.index, ordered.values, color=colors, edgecolor="white", zorder=3)
    ax.axvline(float(company_overall), color=GOLD, linestyle="--", linewidth=1.8,
               label=f"Company ({company_overall:.2f})")
    for i, (idx, val) in enumerate(ordered.items()):
        ax.text(float(val) + 0.06, i, f"{val:.2f}", va="center", fontsize=8, color="#333")
    ax.set_xlim(0, 10)
    ax.set_title("Overall PACE Score by Department", fontsize=12.5, fontweight="bold", color=NAVY, pad=10)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8, colors="#333333")
    ax.grid(axis="x", color="#EAEEF3", linewidth=0.8, zorder=0); ax.set_axisbelow(True)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    plt.tight_layout()
    return fig


# PNG helpers for the PDF
def radar_png(f, c, l="Selected"): return _to_png(radar_chart(f, c, l))
def pillar_png(f, c): return _to_png(pillar_bar(f, c))
def variance_png(d): return _to_png(variance_chart(d))
def polar_png(d): return _to_png(variance_chart(d))
def heatmap_png(c): return _to_png(correlation_heatmap(c))
def ranking_png(a, c, focus=None, max_rows=None): return _to_png(ranking_bar(a, c, focus, max_rows=max_rows))
