"""Charts for the High Performance Diagnostic Tool. PACE. Clear, individual figures."""
from __future__ import annotations
import io
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from .config_loader import PILLARS

NAVY = "#1F3864"
GOLD = "#BF9000"


def _to_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def radar_chart(focus, company, label="Selected", figsize=(5.6, 5.0)):
    """Outline-style radar so BOTH series stay visible (no heavy solid fill)."""
    labels = PILLARS
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    dv = [focus[p] for p in labels] + [focus[labels[0]]]
    cv = [company[p] for p in labels] + [company[labels[0]]]
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("white")
    ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1)
    # Company: gold dashed outline + tiny fill
    ax.plot(angles, cv, color=GOLD, linewidth=2.4, linestyle="--", label="Company", zorder=3)
    ax.fill(angles, cv, color=GOLD, alpha=0.06, zorder=1)
    # Selected: navy solid outline, light fill so company remains visible underneath
    ax.plot(angles, dv, color=NAVY, linewidth=3.0, label=label, zorder=4, marker="o", markersize=5)
    ax.fill(angles, dv, color=NAVY, alpha=0.10, zorder=2)
    # value labels on the selected series
    for ang, val in zip(angles[:-1], dv[:-1]):
        ax.text(ang, val + 0.5, f"{val:.1f}", ha="center", va="center",
                fontsize=8.5, fontweight="bold", color=NAVY, zorder=5)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11, fontweight="bold", color="#333")
    ax.set_yticks([2, 4, 6, 8, 10]); ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=8, color="#888")
    ax.set_ylim(0, 10)
    ax.grid(color="#CCCCCC", linewidth=0.8)
    ax.set_title("PACE Radar — Selected vs Company", fontsize=12, fontweight="bold", color=NAVY, pad=18)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, frameon=False, fontsize=10)
    plt.tight_layout()
    return fig


def radar_chart_multi(depts, company, figsize=(6.0, 5.2)):
    labels = PILLARS
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1)
    cv = [company[p] for p in labels] + [company[labels[0]]]
    ax.plot(angles, cv, color=GOLD, linewidth=2.4, linestyle="--", label="Company avg")
    palette = ["#1F3864", "#548235", "#C00000", "#7030A0", "#ED7D31"]
    for i, (dept, means) in enumerate(depts.items()):
        vals = [means[p] for p in labels] + [means[labels[0]]]
        c = palette[i % len(palette)]
        ax.plot(angles, vals, color=c, linewidth=2.2, label=dept)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 10); ax.grid(color="#CCCCCC")
    ax.set_title("PACE Radar — multi-department", fontsize=11, fontweight="bold", color=NAVY, pad=16)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False, fontsize=8)
    plt.tight_layout()
    return fig


def pillar_bar(pillar_means, company_means, figsize=(5.6, 4.2)):
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(PILLARS)); w = 0.38
    dv = [pillar_means[p] for p in PILLARS]; cv = [company_means[p] for p in PILLARS]
    ax.bar(x - w/2, dv, w, color=NAVY, label="Selected")
    ax.bar(x + w/2, cv, w, color=GOLD, alpha=0.75, label="Company")
    for i, v in enumerate(dv):
        ax.text(i - w/2, v + 0.12, f"{v:.1f}", ha="center", fontsize=8.5, fontweight="bold", color=NAVY)
    ax.set_xticks(x); ax.set_xticklabels(PILLARS, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 10.5); ax.set_title("Element Means — Selected vs Company",
                                       fontsize=12, fontweight="bold", color=NAVY, pad=10)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8.5); ax.legend(frameon=False, fontsize=9, loc="upper right")
    plt.tight_layout()
    return fig


def polarisation_bar(polarisation, figsize=(5.6, 4.2)):
    fig, ax = plt.subplots(figsize=figsize)
    pillars = [p.pillar for p in polarisation]
    low = [p.pct_low for p in polarisation]; mid = [p.pct_mid for p in polarisation]
    high = [p.pct_high for p in polarisation]
    x = np.arange(len(pillars))
    b1 = ax.bar(x, low, color="#C00000", label="Low (≤4)")
    b2 = ax.bar(x, mid, bottom=low, color="#BFBFBF", label="Mid (5–6)")
    b3 = ax.bar(x, high, bottom=[l + m for l, m in zip(low, mid)], color="#548235", label="High (≥7)")
    for i in range(len(pillars)):
        if low[i] >= 12: ax.text(i, low[i]/2, f"{low[i]:.0f}%", ha="center", va="center", fontsize=7.5, color="white", fontweight="bold")
        if high[i] >= 12: ax.text(i, low[i]+mid[i]+high[i]/2, f"{high[i]:.0f}%", ha="center", va="center", fontsize=7.5, color="white", fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(pillars, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 100); ax.set_ylabel("% of responses", fontsize=9)
    ax.set_title("Polarisation Profile — score distribution", fontsize=12, fontweight="bold", color=NAVY, pad=10)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8.5)
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.09))
    plt.tight_layout()
    return fig


def correlation_heatmap(corr, figsize=(5.2, 4.4)):
    fig, ax = plt.subplots(figsize=figsize)
    cmap = mpl.colors.LinearSegmentedColormap.from_list("h", ["#C00000", "#FFFFFF", "#1F3864"])
    im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
    ax.set_xticks(range(len(PILLARS))); ax.set_yticks(range(len(PILLARS)))
    ax.set_xticklabels(PILLARS, fontsize=9, fontweight="bold", rotation=20, ha="right")
    ax.set_yticklabels(PILLARS, fontsize=9, fontweight="bold")
    for i in range(len(PILLARS)):
        for j in range(len(PILLARS)):
            v = corr.values[i, j]
            col = "white" if abs(v) > 0.55 else "#222"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=9.5, fontweight="bold", color=col)
    ax.set_title("Element Inter-Correlation", fontsize=12, fontweight="bold", color=NAVY, pad=10)
    fig.colorbar(im, ax=ax, shrink=0.8)
    plt.tight_layout()
    return fig


def ranking_bar(all_depts, company_overall, focus=None, figsize=(6.4, 4.2)):
    ordered = all_depts["Overall"].sort_values()
    fig, ax = plt.subplots(figsize=figsize)
    colors = [NAVY if d == focus else "#B4C7E7" for d in ordered.index]
    bars = ax.barh(ordered.index, ordered.values, color=colors, edgecolor="white")
    ax.axvline(company_overall, color=GOLD, linestyle="--", linewidth=1.8,
               label=f"Company ({company_overall:.2f})")
    for bar, val in zip(bars, ordered.values):
        ax.text(val + 0.06, bar.get_y() + bar.get_height() / 2, f"{val:.2f}", va="center", fontsize=8.5)
    ax.set_xlim(0, 10)
    ax.set_title("Overall PACE Score by Department", fontsize=12, fontweight="bold", color=NAVY, pad=10)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=8.5)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    plt.tight_layout()
    return fig


# PNG helpers for the PDF
def radar_png(f, c, l="Selected"): return _to_png(radar_chart(f, c, l))
def pillar_png(f, c): return _to_png(pillar_bar(f, c))
def polar_png(p): return _to_png(polarisation_bar(p))
def heatmap_png(c): return _to_png(correlation_heatmap(c))
def ranking_png(a, c, focus=None): return _to_png(ranking_bar(a, c, focus))
