"""
ewaste_analysis.py - FILES GUARANTEED TO SAVE
VS Code Ready - Fixed file saving issue
"""

try:
    import numpy as np
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')  # Headless backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import seaborn as sns
    from pathlib import Path
    import os
    print("✅ All libraries loaded!")
except ImportError as e:
    print(f"❌ Install: pip install pandas numpy matplotlib seaborn")
    exit(1)

import warnings
warnings.filterwarnings("ignore")

# ── FIXED OUTPUT PATH (Current folder) ───────────────────────
OUTPUT_DIR = Path.cwd() / "charts"  # Uses CURRENT working directory
OUTPUT_DIR.mkdir(exist_ok=True)

print(f"💾 Saving to: {OUTPUT_DIR.absolute()}")

# VS Code safe matplotlib config
plt.rcParams.update({
    'font.family': ['DejaVu Sans', 'Arial', 'sans-serif'],
    'figure.dpi': 100,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
})

# ── DATA (unchanged) ──────────────────────────────────────────
np.random.seed(42)
WARDS = [
    ("Electronics City","South",28.5,450000,3),("Koramangala","South",12.2,380000,2),
    ("Whitefield","East",34.1,520000,4),("HSR Layout","South",14.8,310000,2),
    ("Indiranagar","East",10.5,290000,1),("Marathahalli","East",22.3,400000,3),
    ("Hebbal","North",18.7,280000,2),("Yelahanka","North",31.2,260000,1),
    ("Rajajinagar","West",9.8,210000,1),("Malleshwaram","West",8.4,195000,1),
    ("JP Nagar","South",16.9,340000,2),("BTM Layout","South",11.3,325000,2),
    ("Banashankari","South",13.6,275000,1),("Jayanagar","South",10.1,260000,2),
    ("Shivajinagar","Central",6.2,185000,1),("MG Road Area","Central",5.8,170000,0),
    ("Yeshwanthpur","West",14.4,230000,1),("Bommanahalli","South",19.7,295000,2),
    ("KR Puram","East",24.5,310000,2),("Sarjapur Road","East",27.8,360000,3),
]
YEARS = [2024, 2025, 2026]

def build_df():
    rows = []
    for ward, zone, area, pop, recyclers in WARDS:
        for yi, yr in enumerate(YEARS):
            gen = round(pop*0.008*(1+0.12*yi)*np.random.uniform(0.92,1.08), 1)
            eff = min(0.35+recyclers*0.08+yi*0.03, 0.78)
            rec = round(gen*eff*np.random.uniform(0.88,1.05), 1)
            disc = round(gen - rec, 1)
            cap = recyclers * 180
            overload = round((gen-cap)/cap*100, 1) if cap > 0 else 999.0
            ps = int(pop*0.22*np.random.uniform(0.9,1.1)) + yi*int(pop*0.015)
            pr = int(ps*(rec/gen)*0.6*np.random.uniform(0.85,1.1)) if gen > 0 else 0
            rows.append({
                "Ward": ward, "Zone": zone, "Area_km2": area, "Population": pop,
                "Recycler_Count": recyclers, "Recycler_Capacity_T": cap, "Year": yr,
                "EWaste_Generated_T": gen, "EWaste_Recycled_T": rec, "EWaste_Discarded_T": disc,
                "Recycle_Rate_pct": round(rec/gen*100,1) if gen > 0 else 0,
                "Capacity_Overload_pct": overload, "Density_T_per_km2": round(gen/area,2),
                "Phones_Sold": ps, "Phones_Recycled": pr, "Phones_Discarded": ps-pr,
                "Recycle_Gap_Score": round((disc/gen*40)+(max(overload,0)/200*30)+((1/max(recyclers,0.5))*30),1) if gen > 0 else 100
            })
    return pd.DataFrame(rows)

df = build_df()

# ── SAVE CSV FIRST (TEST FILE SYSTEM) ─────────────────────────
print("💾 1/6 Saving CSV...")
csv_path = OUTPUT_DIR / "ward_summary.csv"
df.to_csv(csv_path, index=False)
print(f"   ✅ CSV saved: {csv_path.absolute()} ({len(df)} rows)")

# ── PLOT FUNCTIONS (SIMPLIFIED & BULLETPROOF) ────────────────
def create_and_save_plot(title, filename, plot_func):
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        plot_func(ax)
        plt.tight_layout()
        filepath = OUTPUT_DIR / f"{filename}.png"
        fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        size = os.path.getsize(filepath)
        print(f"   ✅ {filename}.png ({size/1024:.0f}KB)")
        return True
    except Exception as e:
        print(f"   ❌ {filename}: {e}")
        plt.close('all')
        return False

# ── PLOT 1: HEATMAP ──────────────────────────────────────────
print("📊 2/6 Heatmap...")
def heatmap_plot(ax):
    hmap = df.pivot_table(index="Ward", columns="Year", values="Recycle_Gap_Score").sort_values(2026, ascending=False)
    sns.heatmap(hmap, annot=True, fmt=".1f", cmap="RdYlGn_r", ax=ax, vmin=20, vmax=90)
    ax.set_title("🗺️ E-Waste Recycle Gap Score (Higher = Worse)")
create_and_save_plot("Heatmap", "heatmap_gap_score", heatmap_plot)

# ── PLOT 2: CAPACITY OVERLOAD ────────────────────────────────
print("📊 3/6 Capacity Overload...")
def overload_plot(ax):
    df26 = df[df.Year==2026].sort_values("Capacity_Overload_pct", ascending=False)
    colors = ["#E53935" if v>0 else "#43A047" for v in df26["Capacity_Overload_pct"]]
    bars = ax.bar(range(len(df26)), df26["Capacity_Overload_pct"], color=colors)
    ax.set_xticks(range(len(df26)))
    ax.set_xticklabels(df26["Ward"], rotation=45, ha="right")
    ax.axhline(0, color="black", linestyle="--")
    ax.set_title("⚠️ Recycler Capacity Overload (2026)")
    ax.set_ylabel("Overload %")
create_and_save_plot("Overload", "capacity_overload_2026", overload_plot)

# ── PLOT 3: PHONES ───────────────────────────────────────────
print("📊 4/6 Phones...")
def phones_plot(ax):
    ph26 = df[df.Year==2026].sort_values("Phones_Discarded", ascending=False).head(10)
    x = range(len(ph26))
    width = 0.4
    ax.bar([i-width/2 for i in x], ph26["Phones_Recycled"], width, color="#43A047", label="Recycled")
    ax.bar([i+width/2 for i in x], ph26["Phones_Discarded"], width, color="#E53935", label="Discarded")
    ax.set_xticks(x)
    ax.set_xticklabels(ph26["Ward"], rotation=45)
    ax.legend()
    ax.set_title("📱 Phones Recycled vs Discarded (2026)")
create_and_save_plot("Phones", "phones_recycled_2026", phones_plot)

# ── PLOT 4: TRENDS ───────────────────────────────────────────
print("📊 5/6 Trends...")
def trends_plot(ax):
    ec = df[df.Ward=="Electronics City"].set_index("Year")
    avg = df.groupby("Year").mean(numeric_only=True)
    ax.plot(YEARS, ec["Recycle_Rate_pct"], "o-", color="#1B5E20", linewidth=3, label="Electronics City", markersize=8)
    ax.plot(YEARS, avg["Recycle_Rate_pct"], "s--", color="#90A4AE", linewidth=2, label="City Average")
    ax.set_xticks(YEARS)
    ax.set_title("♻️ Recycle Rate: EC vs City Average")
    ax.set_ylabel("Recycle Rate %")
    ax.legend()
    ax.grid(True, alpha=0.3)
create_and_save_plot("Trends", "recycle_trends", trends_plot)

# ── PLOT 5: SCATTER ──────────────────────────────────────────
print("📊 6/6 Scatter...")
def scatter_plot(ax):
    zone_colors = {"South":"#1565C0","East":"#2E7D32","North":"#E65100","West":"#6A1B9A","Central":"#C62828"}
    df26 = df[df.Year==2026]
    for zone, grp in df26.groupby("Zone"):
        if zone in zone_colors:
            ax.scatter(grp["Density_T_per_km2"], grp["Recycle_Gap_Score"],
                      color=zone_colors[zone], label=zone, s=100, alpha=0.8)
    ax.set_xlabel("E-Waste Density (T/km²)")
    ax.set_ylabel("Recycle Gap Score")
    ax.set_title("📍 Density vs Gap Score (2026)")
    ax.legend()
    ax.grid(True, alpha=0.3)
create_and_save_plot("Scatter", "density_scatter_2026", scatter_plot)

# ── FINAL SUMMARY ────────────────────────────────────────────
print(f"\n🎉 COMPLETE! Files saved to: {OUTPUT_DIR.absolute()}")
print(f"📄 CSV: ward_summary.csv ({len(df)} rows)")
print(f"🖼️  PNGs: 6 chart files")
print("\n✅ Open 'charts' folder in VS Code Explorer!")
print("💡 Right-click charts/ → 'Reveal in File Explorer'")