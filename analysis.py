"""
analysis.py
===========
Generates 8 LinkedIn-ready charts from da_arg_eeuu_2025.csv.

Charts produced:
  1. Median salary by seniority — Argentina vs USA
  2. Salary distribution (scatter) — Argentina vs USA
  3. Advanced English: adoption + salary impact in Argentina
  4. Work modality by country and seniority
  5. Tech stack comparison — Argentina vs USA
  6. Tools heatmap by seniority — Argentina
  7. Tools heatmap by seniority — USA
  8. KPI summary dashboard

Output: charts/ folder with 8 PNG files (180 dpi)

Usage:
  pip install pandas numpy matplotlib
  python analysis.py

Author: Facundo Iván Ramírez Boll
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter
import warnings
warnings.filterwarnings("ignore")

# ── Load data ─────────────────────────────────────────────────────────────────
df = pd.read_csv("da_arg_eeuu_2025.csv")

# ── Output folder ─────────────────────────────────────────────────────────────
os.makedirs("charts", exist_ok=True)
OUT = "charts/"

# ── Color palette ─────────────────────────────────────────────────────────────
BG       = "#080B12"
SURFACE  = "#0F1320"
SURFACE2 = "#161B2E"
BORDER   = "#1E2440"
TEXT     = "#EEF0F8"
MUTED    = "#6B7494"
ARG_C    = "#00D4FF"   # cyan  → Argentina
USA_C    = "#FF6B6B"   # coral → USA
GOLD     = "#FFD166"
GREEN    = "#06D6A0"
PURPLE   = "#A78BFA"

SENS = ["Junior", "Semi-Senior", "Senior"]

SKILL_LABELS = {
    "skill_python":                  "Python",
    "skill_sql":                     "SQL",
    "skill_power_bi":                "Power BI",
    "skill_tableau":                 "Tableau",
    "skill_excel":                   "Excel",
    "skill_r":                       "R",
    "skill_dbt_airflow":             "dbt / Airflow",
    "skill_cloud_aws_gcp_azure":     "Cloud (AWS/GCP/Azure)",
    "skill_inteligencia_artificial": "IA / AI Tools",
}
SKILL_COLS = list(SKILL_LABELS.keys())

# ── Formatters ────────────────────────────────────────────────────────────────
def fmt_usd(x, _): return f"${x:,.0f}"
def fmt_pct(x, _): return f"{x:.0f}%"

# ── Helper: base figure ───────────────────────────────────────────────────────
def make_fig(w=14, h=8):
    return plt.figure(figsize=(w, h), facecolor=BG)

# ── Helper: title block ───────────────────────────────────────────────────────
def title_block(fig, title, subtitle, y1=0.97, y2=0.916):
    fig.text(0.5, y1, title, ha="center", va="top",
             fontsize=18, fontweight="bold", color=TEXT, fontfamily="monospace")
    fig.text(0.5, y2, subtitle, ha="center", va="top",
             fontsize=10, color=MUTED, fontfamily="monospace")

# ── Helper: watermark ─────────────────────────────────────────────────────────
def watermark(fig):
    fig.text(0.99, 0.01,
             "Facundo Ramírez Boll  ·  Data Analyst  ·  Argentina vs USA · 2025",
             ha="right", va="bottom", fontsize=7.5,
             color=MUTED, fontfamily="monospace", alpha=0.7)

# ── Helper: clean axis ────────────────────────────────────────────────────────
def clean_ax(ax, grid="y"):
    ax.set_facecolor(SURFACE)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=9, length=0)
    if grid:
        ax.grid(axis=grid, color=BORDER, linewidth=0.8)
        ax.set_axisbelow(True)

# ── Helper: figure legend ─────────────────────────────────────────────────────
def fig_legend(fig, items: dict, y=0.03):
    patches = [
        mpatches.Patch(facecolor=c, label=l, edgecolor="none")
        for l, c in items.items()
    ]
    fig.legend(handles=patches, loc="lower center", ncol=len(patches),
               framealpha=0, labelcolor=TEXT, fontsize=9.5,
               prop={"family": "monospace"}, bbox_to_anchor=(0.5, y))

# ── Pre-compute medians ───────────────────────────────────────────────────────
meds = df.groupby(["pais", "seniority"])["salario_usd"].median()


# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Median salary by seniority
# ══════════════════════════════════════════════════════════════════════════════
fig = make_fig(13, 8)
title_block(fig,
    "💰  Data Analyst Salaries — Argentina vs USA",
    "Monthly median · USD · by seniority level · synthetic dataset calibrated 2025")
watermark(fig)

ax = fig.add_axes([0.08, 0.16, 0.88, 0.72])
clean_ax(ax)

x = np.arange(3)
w = 0.32
av = [float(meds["Argentina"][s]) for s in SENS]
uv = [float(meds["EEUU"][s])      for s in SENS]

ax.bar(x - w/2, av, width=w, color=ARG_C, alpha=0.92, zorder=3)
ax.bar(x + w/2, uv, width=w, color=USA_C, alpha=0.92, zorder=3)

for i, (a, u) in enumerate(zip(av, uv)):
    ax.text(i - w/2, a + 130, f"${a:,.0f}", ha="center", va="bottom",
            color=ARG_C, fontsize=10, fontweight="bold", fontfamily="monospace")
    ax.text(i + w/2, u + 130, f"${u:,.0f}", ha="center", va="bottom",
            color=USA_C, fontsize=10, fontweight="bold", fontfamily="monospace")
    ax.text(i, u * 0.50, f"ARG = {a/u*100:.0f}%\nof US salary",
            ha="center", va="center", color=GOLD, fontsize=8.5,
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.35", facecolor=SURFACE2,
                      edgecolor=BORDER, linewidth=0.8))

ax.set_xticks(x)
ax.set_xticklabels(SENS, color=TEXT, fontsize=12, fontfamily="monospace")
ax.yaxis.set_major_formatter(FuncFormatter(fmt_usd))
ax.set_ylim(0, max(uv) * 1.22)
fig_legend(fig, {"🇦🇷 Argentina": ARG_C, "🇺🇸 USA": USA_C})

fig.savefig(OUT + "chart1_salario_seniority.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅  chart1 — salary by seniority")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — Salary distribution (scatter + median dot)
# ══════════════════════════════════════════════════════════════════════════════
fig = make_fig(14, 8)
title_block(fig,
    "📊  Salary Distribution — Data Analyst 2025",
    "Each dot = 1 professional · ⬤ = median · Argentina vs USA")
watermark(fig)

ax = fig.add_axes([0.07, 0.13, 0.90, 0.75])
clean_ax(ax, "x")

offset = 0.0
ytpos, ytlab = [], []

for sen in SENS:
    for pais, color in [("Argentina", ARG_C), ("EEUU", USA_C)]:
        vals = df[(df["pais"] == pais) & (df["seniority"] == sen)]["salario_usd"].values
        jit  = np.random.uniform(-0.16, 0.16, len(vals))
        ax.scatter(vals, np.full(len(vals), offset) + jit,
                   color=color, alpha=0.18, s=9, zorder=2)
        ax.scatter([np.median(vals)], [offset], color=color,
                   s=130, zorder=5, edgecolors="white", linewidths=1.2)
        ax.axhline(offset, color=BORDER, linewidth=0.5, zorder=1)
        offset += 0.62
    ytpos.append(offset - 0.93)
    ytlab.append(sen)
    offset += 0.85

ax.set_yticks(ytpos)
ax.set_yticklabels(ytlab, color=TEXT, fontsize=12, fontfamily="monospace")
ax.xaxis.set_major_formatter(FuncFormatter(fmt_usd))
ax.tick_params(axis="x", labelcolor=MUTED)
ax.set_xlabel("Monthly salary (USD)", color=MUTED, fontsize=9, fontfamily="monospace")

for lbl, color, xpos in [
    ("🇦🇷 Argentina", ARG_C, 0.16),
    ("🇺🇸 USA",       USA_C, 0.42),
]:
    ax.text(xpos, 1.045, lbl, transform=ax.transAxes, color=color,
            fontsize=10, fontweight="bold", fontfamily="monospace", ha="center")
ax.text(0.76, 1.045, "⬤ = median", transform=ax.transAxes,
        color=MUTED, fontsize=9, fontfamily="monospace")

fig.savefig(OUT + "chart2_distribucion.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅  chart2 — salary distribution")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — English adoption & salary impact
# ══════════════════════════════════════════════════════════════════════════════
fig = make_fig(14, 8)
title_block(fig,
    "🗣️  Advanced English: Adoption & Salary Impact",
    "% of analysts with advanced English · and salary premium in Argentina · 2025")
watermark(fig)

# Left panel: adoption rate
ax1 = fig.add_axes([0.06, 0.14, 0.41, 0.73])
clean_ax(ax1)

x = np.arange(3)
w = 0.30
ing = df.groupby(["pais", "seniority"])["ingles_avanzado"].mean().mul(100)
ai  = [float(ing["Argentina"][s]) for s in SENS]
ui  = [float(ing["EEUU"][s])      for s in SENS]

ax1.bar(x - w/2, ai, width=w, color=ARG_C, alpha=0.90, zorder=3)
ax1.bar(x + w/2, ui, width=w, color=USA_C, alpha=0.90, zorder=3)

for xi, val in enumerate(ai):
    ax1.text(xi - w/2, val + 1.5, f"{val:.0f}%", ha="center", va="bottom",
             color=ARG_C, fontsize=10, fontweight="bold", fontfamily="monospace")
for xi, val in enumerate(ui):
    ax1.text(xi + w/2, val + 1.5, f"{val:.0f}%", ha="center", va="bottom",
             color=USA_C, fontsize=10, fontweight="bold", fontfamily="monospace")

ax1.set_xticks(x)
ax1.set_xticklabels(SENS, color=TEXT, fontsize=10, fontfamily="monospace")
ax1.yaxis.set_major_formatter(FuncFormatter(fmt_pct))
ax1.set_ylim(0, 115)
ax1.set_title("% with advanced English", color=TEXT,
              fontsize=11, fontfamily="monospace", pad=10)

# Right panel: salary premium in Argentina
ax2 = fig.add_axes([0.56, 0.14, 0.41, 0.73])
clean_ax(ax2)

premiums = []
for sen in SENS:
    sub = df[(df["pais"] == "Argentina") & (df["seniority"] == sen)]
    med_yes = float(sub[sub["ingles_avanzado"] == True]["salario_usd"].median())
    med_no  = float(sub[sub["ingles_avanzado"] == False]["salario_usd"].median())
    premiums.append(((med_yes - med_no) / med_no * 100, med_no, med_yes))

ax2.bar(x - w/2, [p[1] for p in premiums], width=w, color=MUTED, alpha=0.50, zorder=3)
ax2.bar(x + w/2, [p[2] for p in premiums], width=w, color=GREEN, alpha=0.90, zorder=3)

for xi, (pr, mn, my) in enumerate(premiums):
    ax2.text(xi + w/2, my + 65, f"+{pr:.0f}%", ha="center", va="bottom",
             color=GREEN, fontsize=10, fontweight="bold", fontfamily="monospace")

ax2.set_xticks(x)
ax2.set_xticklabels(SENS, color=TEXT, fontsize=10, fontfamily="monospace")
ax2.yaxis.set_major_formatter(FuncFormatter(fmt_usd))
ax2.set_ylim(0, max(p[2] for p in premiums) * 1.22)
ax2.set_title("Salary impact of English 🇦🇷", color=TEXT,
              fontsize=11, fontfamily="monospace", pad=10)

fig.add_artist(plt.Line2D([0.505, 0.505], [0.14, 0.88], color=BORDER, linewidth=1))
fig_legend(fig, {"Without advanced English": MUTED, "With advanced English": GREEN})

fig.savefig(OUT + "chart3_ingles.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅  chart3 — english adoption & impact")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Work modality by country and seniority
# ══════════════════════════════════════════════════════════════════════════════
fig = make_fig(13, 8)
title_block(fig,
    "🏠  Work Modality — Data Analyst 2025",
    "Remote · Hybrid · On-site · by country and seniority")
watermark(fig)

MOD_COLORS = {"Remoto 100%": GREEN, "Híbrido": PURPLE, "Presencial": GOLD}
MOD_LABELS = {"Remoto 100%": "Remote 100%", "Híbrido": "Hybrid", "Presencial": "On-site"}
MODS = ["Remoto 100%", "Híbrido", "Presencial"]

for pi, pais in enumerate(["Argentina", "EEUU"]):
    ax = fig.add_axes([0.06 + pi * 0.50, 0.13, 0.42, 0.73])
    ax.set_facecolor(SURFACE)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0)

    piv = df[df["pais"] == pais].groupby(["seniority", "modalidad"]).size().unstack(fill_value=0)
    for m in MODS:
        if m not in piv.columns: piv[m] = 0
    piv = piv[MODS]
    piv_pct = piv.div(piv.sum(axis=1), axis=0).mul(100).reindex(SENS)

    x = np.arange(3)
    bottom = np.zeros(3)
    for mod in MODS:
        vals = piv_pct[mod].values
        ax.bar(x, vals, bottom=bottom, color=MOD_COLORS[mod],
               width=0.55, zorder=3, alpha=0.90)
        for i, (b, v) in enumerate(zip(bottom, vals)):
            if v > 7:
                ax.text(i, b + v / 2, f"{v:.0f}%", ha="center", va="center",
                        color="white", fontsize=10, fontweight="bold",
                        fontfamily="monospace")
        bottom += vals

    flag = "🇦🇷" if pais == "Argentina" else "🇺🇸"
    name = "Argentina" if pais == "Argentina" else "USA"
    ax.set_title(f"{flag} {name}", color=TEXT, fontsize=13,
                 fontweight="bold", fontfamily="monospace", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(SENS, color=TEXT, fontsize=10, fontfamily="monospace")
    ax.set_ylim(0, 108)
    ax.yaxis.set_major_formatter(FuncFormatter(fmt_pct))
    ax.tick_params(axis="y", labelcolor=MUTED)

fig_legend(fig, {v: MOD_COLORS[k] for k, v in MOD_LABELS.items()})
fig.savefig(OUT + "chart4_modalidad.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅  chart4 — work modality")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 — Tech stack: Argentina vs USA
# ══════════════════════════════════════════════════════════════════════════════
fig = make_fig(14, 9)
title_block(fig,
    "🛠️  Tech Stack — Data Analyst: Argentina vs USA",
    "% of analysts using each tool · all seniority levels · 2025")
watermark(fig)

ax = fig.add_axes([0.20, 0.11, 0.76, 0.75])
clean_ax(ax, "x")

arg_pct = df[df["pais"] == "Argentina"][SKILL_COLS].mean().mul(100)
usa_pct = df[df["pais"] == "EEUU"][SKILL_COLS].mean().mul(100)
order   = (arg_pct + usa_pct).sort_values().index
arg_s   = arg_pct[order]
usa_s   = usa_pct[order]
labs    = [SKILL_LABELS[c] for c in order]

y = np.arange(len(labs))
h = 0.32
b1 = ax.barh(y + h/2, arg_s.values, height=h, color=ARG_C, alpha=0.90, zorder=3)
b2 = ax.barh(y - h/2, usa_s.values, height=h, color=USA_C, alpha=0.90, zorder=3)

for bar, val in zip(b1, arg_s.values):
    ax.text(val + 0.8, bar.get_y() + bar.get_height() / 2, f"{val:.0f}%",
            va="center", ha="left", color=ARG_C, fontsize=9,
            fontweight="bold", fontfamily="monospace")
for bar, val in zip(b2, usa_s.values):
    ax.text(val + 0.8, bar.get_y() + bar.get_height() / 2, f"{val:.0f}%",
            va="center", ha="left", color=USA_C, fontsize=9,
            fontweight="bold", fontfamily="monospace")

ax.set_yticks(y)
ax.set_yticklabels(labs, color=TEXT, fontsize=11, fontfamily="monospace")
ax.xaxis.set_major_formatter(FuncFormatter(fmt_pct))
ax.set_xlim(0, 110)
ax.tick_params(axis="x", labelcolor=MUTED)
fig_legend(fig, {"🇦🇷 Argentina": ARG_C, "🇺🇸 USA": USA_C})

fig.savefig(OUT + "chart5_herramientas.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅  chart5 — tech stack")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 6 & 7 — Tools heatmap by seniority (one per country)
# ══════════════════════════════════════════════════════════════════════════════
def make_heatmap(pais: str, color_end: str, filename: str, flag: str, label: str):
    fig = make_fig(13, 7)
    title_block(fig,
        f"📐  Tools by Seniority — {flag}",
        f"% of analysts using each skill · {label} · 2025")
    watermark(fig)

    ax = fig.add_axes([0.23, 0.11, 0.73, 0.73])
    ax.set_facecolor(SURFACE)
    ax.tick_params(length=0)
    for sp in ax.spines.values(): sp.set_visible(False)

    piv = (df[df["pais"] == pais]
           .groupby("seniority")[SKILL_COLS]
           .mean().mul(100)
           .reindex(SENS))

    # Sort skills by overall adoption (descending)
    order_idx = piv.mean().sort_values(ascending=False).index
    piv  = piv[order_idx]
    labs = [SKILL_LABELS[c] for c in order_idx]

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "custom", ["#080B12", "#0A2030", color_end])
    im = ax.imshow(piv.T.values, aspect="auto", cmap=cmap, vmin=0, vmax=100)

    ax.set_xticks(range(3))
    ax.set_xticklabels(SENS, color=TEXT, fontsize=11, fontfamily="monospace")
    ax.set_yticks(range(len(labs)))
    ax.set_yticklabels(labs, color=TEXT, fontsize=10, fontfamily="monospace")

    for i in range(len(labs)):
        for j in range(3):
            val = piv.T.values[i, j]
            tc  = BG if val > 55 else TEXT
            ax.text(j, i, f"{val:.0f}%", ha="center", va="center",
                    color=tc, fontsize=10, fontweight="bold",
                    fontfamily="monospace")

    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.ax.tick_params(colors=MUTED, labelsize=8)
    cbar.ax.yaxis.set_major_formatter(FuncFormatter(fmt_pct))

    fig.savefig(filename, dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close()


make_heatmap("Argentina", ARG_C, OUT + "chart6_heatmap_arg.png",
             "🇦🇷 Argentina", "Argentina")
print("✅  chart6 — heatmap Argentina")

make_heatmap("EEUU", USA_C, OUT + "chart7_heatmap_eeuu.png",
             "🇺🇸 USA", "USA")
print("✅  chart7 — heatmap USA")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 8 — KPI summary dashboard
# ══════════════════════════════════════════════════════════════════════════════
fig = make_fig(14, 9)
title_block(fig,
    "📊  Data Analyst 2025 — Argentina vs USA · Summary",
    "Synthetic dataset calibrated against public sources · n = 2,200",
    y1=0.98, y2=0.935)
watermark(fig)

ssa = df[(df["pais"] == "Argentina") & (df["seniority"] == "Semi-Senior")]
ssu = df[(df["pais"] == "EEUU")      & (df["seniority"] == "Semi-Senior")]

KPIS = [
    ("Median salary\nSemi-Senior",
     f"${ssa['salario_usd'].median():,.0f}",
     f"${ssu['salario_usd'].median():,.0f}"),
    ("Advanced English\nSemi-Senior",
     f"{ssa['ingles_avanzado'].mean() * 100:.0f}%",
     f"{ssu['ingles_avanzado'].mean() * 100:.0f}%"),
    ("Works fully remote\n(all levels)",
     f"{(df[df['pais']=='Argentina']['modalidad']=='Remoto 100%').mean()*100:.0f}%",
     f"{(df[df['pais']=='EEUU']['modalidad']=='Remoto 100%').mean()*100:.0f}%"),
    ("Uses AI tools\n(all levels)",
     f"{df[df['pais']=='Argentina']['skill_inteligencia_artificial'].mean()*100:.0f}%",
     f"{df[df['pais']=='EEUU']['skill_inteligencia_artificial'].mean()*100:.0f}%"),
]

for i, (label, arg_val, usa_val) in enumerate(KPIS):
    col = i % 2
    row = i // 2
    ax  = fig.add_axes([0.05 + col * 0.50, 0.50 - row * 0.40, 0.44, 0.34])
    ax.set_facecolor(SURFACE2)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    for sp in ["top", "bottom", "left", "right"]:
        ax.spines[sp].set_visible(True)
        ax.spines[sp].set_color(BORDER)
        ax.spines[sp].set_linewidth(0.8)

    ax.text(0.5, 0.88, label, ha="center", va="top",
            color=MUTED, fontsize=10, fontfamily="monospace")
    ax.text(0.26, 0.50, arg_val, ha="center", va="center",
            color=ARG_C, fontsize=26, fontweight="bold", fontfamily="monospace")
    ax.text(0.74, 0.50, usa_val, ha="center", va="center",
            color=USA_C, fontsize=26, fontweight="bold", fontfamily="monospace")
    ax.text(0.26, 0.14, "🇦🇷 Argentina", ha="center", va="bottom",
            color=ARG_C, fontsize=9, fontfamily="monospace")
    ax.text(0.74, 0.14, "🇺🇸 USA", ha="center", va="bottom",
            color=USA_C, fontsize=9, fontfamily="monospace")
    ax.axvline(0.5, color=BORDER, linewidth=1)

fig.savefig(OUT + "chart8_kpis.png", dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print("✅  chart8 — KPI dashboard")

print("\n🎉  All 8 charts saved to /charts")
