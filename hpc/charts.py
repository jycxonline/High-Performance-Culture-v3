"""Compact chart generation for the High Performance Diagnostic Tool. PACE."""
from __future__ import annotations
import io
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from .config_loader import PILLARS, BRAND

NAVY = "#1F3864"
GOLD = "#BF9000"


def _to_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def radar_chart(focus, company, label="Selected", figsize=(4.6, 4.0)):
    labels = PILLARS
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    dv = [focus[p] for p in labels] + [focus[labels[0]]]
    cv = [company[p] for p in labels] + [company[labels[0]]]
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("white")
    ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1)
    ax.plot(angles, cv, color=GOLD, linewidth=1.8, label="Company")
    ax.fill(angles, cv, color=GOLD, alpha=0.10)
    ax.plot(angles, dv, color=NAVY, linewidth=2.2, label=label)
    ax.fill(angles, dv, color=NAVY, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8.5, fontweight="bold")
    ax.set_yticks([2, 4, 6, 8, 10]); ax.set_yticklabels(["2","4","6","8","10"], fontsize=6.5)
    ax.set_ylim(0, 10)
    ax.grid(color="#CCCCCC", linewidth=0.6)
    ax.set_title("PACE Radar", fontsize=10, fontweight="bold", color=NAVY, pad=12)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, frameon=False, fontsize=7)
    plt.tight_layout()
    return fig


def radar_chart_multi(depts, company, figsize=(5.0, 4.4)):
    labels = PILLARS
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2); ax.set_theta_direction(-1)
    cv = [company[p] for p in labels] + [company[labels[0]]]
    ax.plot(angles, cv, color=GOLD, linewidth=2.0, linestyle="--", label="Company avg")
    palette = ["#1F3864", "#548235", "#C00000", "#7030A0", "#ED7D31"]
    for i, (dept, means) in enumerate(depts.items()):
        vals = [means[p] for p in labels] + [means[labels[0]]]
        c = palette[i % len(palette)]
        ax.plot(angles, vals, color=c, linewidth=1.8, label=dept)
        ax.fill(angles, vals, color=c, alpha=0.08)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, fontsize=8.5, fontweight="bold")
    ax.set_ylim(0, 10); ax.grid(color="#CCCCCC")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False, fontsize=7)
    plt.tight_layout()
    return fig


def correlation_heatmap(corr, figsize=(4.2, 3.4)):
    fig, ax = plt.subplots(figsize=figsize)
    cmap = mpl.colors.LinearSegmentedColormap.from_list("h", ["#C00000", "#FFFFFF", "#1F3864"])
    im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
    ax.set_xticks(range(len(PILLARS))); ax.set_yticks(range(len(PILLARS)))
    ax.set_xticklabels(PILLARS, fontsize=7.5, fontweight="bold", rotation=20, ha="right")
    ax.set_yticklabels(PILLARS, fontsize=7.5, fontweight="bold")
    for i in range(len(PILLARS)):
        for j in range(len(PILLARS)):
            v = corr.values[i, j]
            col = "white" if abs(v) > 0.55 else "#222"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8, fontweight="bold", color=col)
    ax.set_title("Element Inter-Correlation", fontsize=10, fontweight="bold", color=NAVY, pad=8)
    plt.tight_layout()
    return fig


def ranking_bar(all_depts, company_overall, focus=None, figsize=(5.2, 3.4)):
    ordered = all_depts["Overall"].sort_values()
    fig, ax = plt.subplots(figsize=figsize)
    colors = [NAVY if d == focus else "#B4C7E7" for d in ordered.index]
    bars = ax.barh(ordered.index, ordered.values, color=colors, edgecolor="white")
    ax.axvline(company_overall, color=GOLD, linestyle="--", linewidth=1.6,
               label=f"Company ({company_overall:.2f})")
    for bar, val in zip(bars, ordered.values):
        ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2, f"{val:.2f}", va="center", fontsize=7.5)
    ax.set_xlim(0, 10)
    ax.set_title("Overall PACE Score by Department", fontsize=10, fontweight="bold", color=NAVY, pad=8)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=7.5)
    ax.legend(loc="lower right", frameon=False, fontsize=7)
    plt.tight_layout()
    return fig


def pillar_bar(pillar_means, company_means, figsize=(4.6, 3.0)):
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(PILLARS)); w = 0.38
    dv = [pillar_means[p] for p in PILLARS]; cv = [company_means[p] for p in PILLARS]
    ax.bar(x - w/2, dv, w, color=NAVY, label="Selected")
    ax.bar(x + w/2, cv, w, color=GOLD, alpha=0.7, label="Company")
    for i, v in enumerate(dv):
        ax.text(i - w/2, v + 0.1, f"{v:.1f}", ha="center", fontsize=7, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(PILLARS, fontsize=8, fontweight="bold")
    ax.set_ylim(0, 10); ax.set_title("Element Means", fontsize=10, fontweight="bold", color=NAVY, pad=8)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=7); ax.legend(frameon=False, fontsize=7, loc="upper right")
    plt.tight_layout()
    return fig


def variance_bar(polarisation, figsize=(4.6, 3.0)):
    """Stacked low/mid/high distribution per element — shows polarisation at a glance."""
    fig, ax = plt.subplots(figsize=figsize)
    pillars = [p.pillar for p in polarisation]
    low = [p.pct_low for p in polarisation]
    mid = [p.pct_mid for p in polarisation]
    high = [p.pct_high for p in polarisation]
    x = np.arange(len(pillars))
    ax.bar(x, low, color="#C00000", label="Low (≤4)")
    ax.bar(x, mid, bottom=low, color="#BFBFBF", label="Mid (5–6)")
    ax.bar(x, high, bottom=[l + m for l, m in zip(low, mid)], color="#548235", label="High (≥7)")
    ax.set_xticks(x); ax.set_xticklabels(pillars, fontsize=8, fontweight="bold")
    ax.set_ylim(0, 100); ax.set_ylabel("% of responses", fontsize=7.5)
    ax.set_title("Polarisation Profile", fontsize=10, fontweight="bold", color=NAVY, pad=8)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=7); ax.legend(frameon=False, fontsize=6.5, ncol=3, loc="upper center",
                                            bbox_to_anchor=(0.5, -0.12))
    plt.tight_layout()
    return fig


def one_page_dashboard(analysis, figsize=(11, 6.4)):
    """A single compact figure: radar, pillar bars, polarisation profile, heatmap."""
    fig = plt.figure(figsize=figsize, facecolor="white")
    gs = fig.add_gridspec(2, 3, hspace=0.55, wspace=0.42,
                          left=0.05, right=0.97, top=0.9, bottom=0.1)

    labels = PILLARS
    # Radar (top-left)
    axr = fig.add_subplot(gs[0, 0], polar=True)
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist(); angles += angles[:1]
    dv = [analysis.focus.pillar_means[p] for p in labels] + [analysis.focus.pillar_means[labels[0]]]
    cv = [analysis.company_pillar_means[p] for p in labels] + [analysis.company_pillar_means[labels[0]]]
    axr.set_theta_offset(np.pi / 2); axr.set_theta_direction(-1)
    axr.plot(angles, cv, color=GOLD, linewidth=1.6); axr.fill(angles, cv, color=GOLD, alpha=0.10)
    axr.plot(angles, dv, color=NAVY, linewidth=2.0); axr.fill(angles, dv, color=NAVY, alpha=0.25)
    axr.set_xticks(angles[:-1]); axr.set_xticklabels(labels, fontsize=7, fontweight="bold")
    axr.set_yticks([2,4,6,8,10]); axr.set_yticklabels([], fontsize=6); axr.set_ylim(0, 10)
    axr.grid(color="#CCCCCC", linewidth=0.5)
    axr.set_title("PACE Radar", fontsize=9, fontweight="bold", color=NAVY, pad=10)

    # Pillar means bar (top-middle)
    axb = fig.add_subplot(gs[0, 1])
    x = np.arange(len(labels)); w = 0.38
    axb.bar(x - w/2, [analysis.focus.pillar_means[p] for p in labels], w, color=NAVY, label="Sel.")
    axb.bar(x + w/2, [analysis.company_pillar_means[p] for p in labels], w, color=GOLD, alpha=0.7, label="Co.")
    axb.set_xticks(x); axb.set_xticklabels([p[:4] for p in labels], fontsize=7)
    axb.set_ylim(0, 10); axb.set_title("Element Means", fontsize=9, fontweight="bold", color=NAVY, pad=8)
    axb.spines["top"].set_visible(False); axb.spines["right"].set_visible(False)
    axb.tick_params(labelsize=6.5); axb.legend(frameon=False, fontsize=6, loc="upper right")

    # Polarisation profile (top-right)
    axp = fig.add_subplot(gs[0, 2])
    low = [p.pct_low for p in analysis.polarisation]; mid = [p.pct_mid for p in analysis.polarisation]
    high = [p.pct_high for p in analysis.polarisation]
    axp.bar(x, low, color="#C00000", label="Low")
    axp.bar(x, mid, bottom=low, color="#BFBFBF", label="Mid")
    axp.bar(x, high, bottom=[l+m for l, m in zip(low, mid)], color="#548235", label="High")
    axp.set_xticks(x); axp.set_xticklabels([p[:4] for p in labels], fontsize=7); axp.set_ylim(0, 100)
    axp.set_title("Polarisation %", fontsize=9, fontweight="bold", color=NAVY, pad=8)
    axp.spines["top"].set_visible(False); axp.spines["right"].set_visible(False)
    axp.tick_params(labelsize=6.5); axp.legend(frameon=False, fontsize=5.5, ncol=3, loc="lower center",
                                               bbox_to_anchor=(0.5, -0.22))

    # Ranking bar (bottom-left, spans 2)
    axk = fig.add_subplot(gs[1, :2])
    ordered = analysis.all_departments["Overall"].sort_values()
    focusname = analysis.focus.department
    colors = [NAVY if d == focusname else "#B4C7E7" for d in ordered.index]
    axk.barh(ordered.index, ordered.values, color=colors, edgecolor="white")
    axk.axvline(analysis.company_overall, color=GOLD, linestyle="--", linewidth=1.4)
    for i, (idx, val) in enumerate(ordered.items()):
        axk.text(val + 0.05, i, f"{val:.2f}", va="center", fontsize=6.5)
    axk.set_xlim(0, 10); axk.set_title("Overall PACE Score by Department", fontsize=9,
                                       fontweight="bold", color=NAVY, pad=8)
    axk.spines["top"].set_visible(False); axk.spines["right"].set_visible(False)
    axk.tick_params(labelsize=6.5)

    # Heatmap (bottom-right)
    axh = fig.add_subplot(gs[1, 2])
    cmap = mpl.colors.LinearSegmentedColormap.from_list("h", ["#C00000", "#FFFFFF", "#1F3864"])
    im = axh.imshow(analysis.correlation.values, cmap=cmap, vmin=-1, vmax=1)
    axh.set_xticks(range(len(labels))); axh.set_yticks(range(len(labels)))
    axh.set_xticklabels([p[:4] for p in labels], fontsize=6.5, rotation=20, ha="right")
    axh.set_yticklabels([p[:4] for p in labels], fontsize=6.5)
    for i in range(len(labels)):
        for j in range(len(labels)):
            v = analysis.correlation.values[i, j]
            axh.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6,
                     color="white" if abs(v) > 0.55 else "#222")
    axh.set_title("Correlation", fontsize=9, fontweight="bold", color=NAVY, pad=8)

    fig.suptitle(f"PACE Diagnostic — {analysis.focus.department}", fontsize=12,
                 fontweight="bold", color=NAVY, y=0.98)
    fig.text(0.5, 0.015, BRAND, ha="center", fontsize=7, color="#8C8C8C", style="italic")
    return fig
