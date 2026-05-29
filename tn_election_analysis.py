"""
TN Election 2026 Analysis — Codebasics RPC #21
Author: AtliQ Media Data Analyst
Data Sources:
  - tn_2026_results.csv : ECI Results Portal (results.eci.gov.in/ResultAcGenMay2026)
  - tn_2021_results.csv : TCPD / Ashoka University (sourced from ECI)
  - constituency_master.csv : Codebasics starter pack

Stories Covered:
  Q2  — The Flip Story
  Q3  — The Vote Share Story (TVK debut)
  Q6  — The Margin of Victory Story
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os

# ---------------------------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------------------------
DATA_DIR = "/mnt/project"

df21 = pd.read_csv(os.path.join(DATA_DIR, "tn_2021_results.csv"))
df26 = pd.read_csv(os.path.join(DATA_DIR, "tn_2026_results.csv"))
master = pd.read_csv(os.path.join(DATA_DIR, "constituency_master.csv"))

print(f"2021: {len(df21)} rows, {df21['ac_number'].nunique()} constituencies")
print(f"2026: {len(df26)} rows, {df26['ac_number'].nunique()} constituencies")

# ---------------------------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def get_winners(df: pd.DataFrame) -> pd.DataFrame:
    """Return the winning candidate row per constituency (highest votes)."""
    idx = df.groupby("ac_number")["votes"].idxmax()
    return df.loc[idx][
        ["ac_number", "constituency", "party", "votes", "reserved", "region"]
    ].reset_index(drop=True)


def get_vote_share(df: pd.DataFrame) -> pd.Series:
    """Return percentage vote share per party across all constituencies."""
    total = df["votes"].sum()
    return (df.groupby("party")["votes"].sum() / total * 100).sort_values(ascending=False)


def get_margin_stats(df: pd.DataFrame) -> pd.DataFrame:
    """For each constituency return winner votes, runner votes, total, margin."""
    def _margin(g):
        s = g["votes"].sort_values(ascending=False).reset_index(drop=True)
        return pd.Series({
            "winner_votes": s.iloc[0],
            "runner_votes": s.iloc[1] if len(s) > 1 else 0,
            "total_valid": s.sum(),
            "margin": s.iloc[0] - (s.iloc[1] if len(s) > 1 else 0),
        })
    result = df.groupby("ac_number").apply(_margin).reset_index()
    result["win_pct"] = result["winner_votes"] / result["total_valid"] * 100
    result["margin_pct"] = result["margin"] / result["total_valid"] * 100
    return result


# ---------------------------------------------------------------------------
# 3. COMPUTE ALL METRICS
# ---------------------------------------------------------------------------

w21 = get_winners(df21)
w26 = get_winners(df26)
vs21 = get_vote_share(df21)
vs26 = get_vote_share(df26)
m21 = get_margin_stats(df21)
m26 = get_margin_stats(df26)

# --- Seat tallies ---
print("\n=== SEAT TALLY ===")
print("2021:", w21["party"].value_counts().head(10).to_dict())
print("2026:", w26["party"].value_counts().head(10).to_dict())

# --- State-wide vote share (key parties) ---
KEY_PARTIES = ["DMK", "AIADMK", "TVK", "NTK", "BJP", "INC", "PMK", "VCK"]
print("\n=== STATE-WIDE VOTE SHARE ===")
for p in KEY_PARTIES:
    s21 = vs21.get(p, 0.0)
    s26 = vs26.get(p, 0.0)
    print(f"  {p:12s}  2021={s21:5.1f}%  2026={s26:5.1f}%  Δ={s26-s21:+5.1f}%")

# --- Flip story ---
merged = w21.merge(w26, on="ac_number", suffixes=("_21", "_26"))
flipped = merged[merged["party_21"] != merged["party_26"]].copy()
flip_counts = (
    flipped[["party_21", "party_26"]]
    .value_counts()
    .reset_index()
    .rename(columns={0: "count"})
)
flip_counts.columns = ["from_party", "to_party", "count"]
print(f"\n=== FLIP STORY ===")
print(f"  Total flips: {len(flipped)} / 234 ({len(flipped)/234*100:.0f}%)")
print(flip_counts.head(10).to_string(index=False))

# --- Margin stats ---
print("\n=== MARGIN OF VICTORY ===")
print(f"  2021 avg margin (votes): {m21['margin'].mean():,.0f}")
print(f"  2026 avg margin (votes): {m26['margin'].mean():,.0f}")
print(f"  2021 avg margin (%):     {m21['margin_pct'].mean():.1f}%")
print(f"  2026 avg margin (%):     {m26['margin_pct'].mean():.1f}%")
print(f"  2021 won >50% votes:     {(m21['win_pct'] > 50).sum()} seats")
print(f"  2026 won >50% votes:     {(m26['win_pct'] > 50).sum()} seats")
print(f"  2021 won <35% votes:     {(m21['win_pct'] < 35).sum()} seats")
print(f"  2026 won <35% votes:     {(m26['win_pct'] < 35).sum()} seats")

# --- Regional breakdown ---
print("\n=== REGIONAL SEAT BREAKDOWN 2026 ===")
print(
    w26.groupby(["region", "party"])["ac_number"]
    .count()
    .unstack(fill_value=0)[["TVK", "DMK", "AIADMK"]]
)

# ---------------------------------------------------------------------------
# 4. CHARTS
# ---------------------------------------------------------------------------
os.makedirs("charts", exist_ok=True)

# Chart 1: Vote share comparison
fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(KEY_PARTIES))
w = 0.35
v21_vals = [vs21.get(p, 0) for p in KEY_PARTIES]
v26_vals = [vs26.get(p, 0) for p in KEY_PARTIES]
bars1 = ax.bar(x - w/2, v21_vals, w, label="2021", color="#1C7293", alpha=0.9)
bars2 = ax.bar(x + w/2, v26_vals, w, label="2026", color="#E84C3D", alpha=0.9)
ax.set_xticks(x); ax.set_xticklabels(KEY_PARTIES, fontsize=12, fontweight="bold")
ax.set_ylabel("Vote Share (%)"); ax.set_ylim(0, 42)
ax.set_title("State-wide Vote Share: 2021 vs 2026", fontsize=14, fontweight="bold")
ax.legend(); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.grid(axis="y", alpha=0.3)
for bars in [bars1, bars2]:
    for bar in bars:
        h = bar.get_height()
        if h > 0.5:
            ax.text(bar.get_x()+bar.get_width()/2, h+0.5, f"{h:.1f}%",
                    ha="center", va="bottom", fontsize=8)
plt.tight_layout()
plt.savefig("charts/vote_share_comparison.png", dpi=150, bbox_inches="tight")
plt.close()

# Chart 2: Flip flows (horizontal bar)
top_flows = flip_counts[flip_counts["count"] >= 2].copy()
labels_f = [f"{r['from_party']} → {r['to_party']}" for _, r in top_flows.iterrows()]
vals_f = top_flows["count"].values
colors_f = ["#E84C3D" if "TVK" in l else "#1C7293" if "DMK" in l else "#F39C12"
            for l in labels_f]
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(labels_f, vals_f, color=colors_f, alpha=0.85)
for bar in bars:
    ax.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2,
            str(int(bar.get_width())), va="center", fontsize=11, fontweight="bold")
ax.set_xlabel("Number of Constituencies"); ax.set_xlim(0, 75)
ax.set_title("Seat Flips: Where Each Constituency Went (2021→2026)", fontsize=13, fontweight="bold")
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("charts/flip_flows.png", dpi=150, bbox_inches="tight")
plt.close()

# Chart 3: Winner vote share distribution histogram
fig, ax = plt.subplots(figsize=(10, 5))
bins = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]
ax.hist(m21["win_pct"], bins=bins, alpha=0.7, label="2021", color="#1C7293")
ax.hist(m26["win_pct"], bins=bins, alpha=0.7, label="2026", color="#E84C3D")
ax.axvline(50, color="#2C3E50", linestyle="--", linewidth=2, label="50% threshold")
ax.axvline(35, color="#F39C12", linestyle="--", linewidth=2, label="35% threshold")
ax.set_xlabel("Winner Vote Share (%)"); ax.set_ylabel("Number of Constituencies")
ax.set_title("Winner Vote Share Distribution: 2021 vs 2026", fontsize=13, fontweight="bold")
ax.legend(); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("charts/winner_share_dist.png", dpi=150, bbox_inches="tight")
plt.close()

# Chart 4: Regional stacked bar
regions = ["Chennai Metro", "North", "Central", "Kongu", "Delta", "South"]
party_colors = {"TVK": "#C0392B", "DMK": "#1C7293", "AIADMK": "#F39C12", "Others": "#95A5A6"}

def region_party_seats(w, regions):
    data = {}
    for r in regions:
        wr = w[w["region"] == r]
        row = {p: int((wr["party"] == p).sum()) for p in ["TVK", "DMK", "AIADMK"]}
        row["Others"] = len(wr) - sum(row.values())
        data[r] = row
    return data

d21r = region_party_seats(w21, regions)
d26r = region_party_seats(w26, regions)

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
for ax, data, title in [(axes[0], d21r, "2021"), (axes[1], d26r, "2026")]:
    bottoms = np.zeros(len(regions))
    for party in ["TVK", "DMK", "AIADMK", "Others"]:
        vals = np.array([data[r][party] for r in regions])
        ax.bar(regions, vals, bottom=bottoms, label=party, color=party_colors[party], alpha=0.9)
        for i, (v, b) in enumerate(zip(vals, bottoms)):
            if v > 1:
                ax.text(i, b + v/2, str(v), ha="center", va="center",
                        fontsize=10, fontweight="bold", color="white")
        bottoms += vals
    ax.set_title(f"{title} Seats by Region", fontsize=12, fontweight="bold")
    ax.tick_params(axis="x", rotation=15, labelsize=9)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
axes[1].legend(loc="upper right", fontsize=9)
plt.tight_layout()
plt.savefig("charts/regional_seats.png", dpi=150, bbox_inches="tight")
plt.close()

# Chart 5: Seat distribution pie (2021 vs 2026)
seat_21 = w21["party"].value_counts()
seat_26 = w26["party"].value_counts()
MAIN_PARTIES = ["DMK", "AIADMK", "TVK", "INC", "PMK", "VCK"]

def pie_data(seat_series):
    vals, labs, cols = [], [], []
    color_map = {"TVK": "#C0392B", "DMK": "#1C7293", "AIADMK": "#F39C12",
                 "INC": "#8E44AD", "PMK": "#27AE60", "VCK": "#E67E22", "Others": "#95A5A6"}
    for p in MAIN_PARTIES:
        v = seat_series.get(p, 0)
        if v > 0: vals.append(v); labs.append(p); cols.append(color_map[p])
    others = 234 - sum(vals)
    if others > 0: vals.append(others); labs.append("Others"); cols.append(color_map["Others"])
    return vals, labs, cols

fig, axes = plt.subplots(1, 2, figsize=(11, 5))
for ax, seat_s, title in [(axes[0], seat_21, "2021"), (axes[1], seat_26, "2026")]:
    vals, labs, cols = pie_data(seat_s)
    wedges, texts, autotexts = ax.pie(
        vals, labels=labs, colors=cols, autopct="%d", startangle=90,
        pctdistance=0.7, labeldistance=1.15)
    for t in texts: t.set_fontsize(11)
    for t in autotexts: t.set_fontsize(10); t.set_color("white"); t.set_fontweight("bold")
    ax.set_title(f"{title}: 234 Seats", fontsize=13, fontweight="bold")
fig.suptitle("Seat Distribution: 2021 vs 2026", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("charts/seat_distribution.png", dpi=150, bbox_inches="tight")
plt.close()

print("\nAll charts saved to charts/")
print("\n=== ANALYSIS COMPLETE ===")
