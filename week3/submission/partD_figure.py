"""
Week 3 - Part D: the 2x2 clinical review figure from vitals_10k.csv.
Inspect -> clean (every rule logged with a count) -> one 2x2 figure at 300 dpi.
Also writes the appendix version without the heart-rate exclusion.

Run from anywhere:  python submission/partD_figure.py
Generated from the notebook partD_clinical_figure.ipynb (same code, same outputs).
"""


# # Week 3 - Part D: the clinical review figure
#
# 10,000 patient vital-sign records have to be checked before a safety review. The plan:
#
# 1. **Look before plotting.** Run the four inspection commands from the brief and read them.
# 2. **Clean, and write every rule down.** Each fix goes into `LOG` with the rule, the count, and (where it matters) what the mean moved from and to. This log is what Part E item 3 is built from.
# 3. **Build one 2x2 figure:** a distribution, a box plot across wards, a scatter of the one pair worth plotting, and a correlation heatmap done to the Lecture 6 rules.
# 4. **Export at 300 dpi**, plus an appendix version with the heart-rate faults left in, so nobody can say I hid them.


import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Works both as a notebook (opened from week3/) and as a script (week3/submission/x.py)
try:
    ROOT = Path(__file__).resolve().parents[1]
    IN_NOTEBOOK = False
except NameError:
    ROOT = Path.cwd()
    IN_NOTEBOOK = True
sys.path.insert(0, str(ROOT))

import vizlib
from vizlib import PALETTE, MARKERS, save_fig, style_defaults

DATA = ROOT / "data"
CHARTS = ROOT / "charts"
SUB = ROOT / "submission"
CHARTS.mkdir(exist_ok=True)
SUB.mkdir(exist_ok=True)

style_defaults()                      # house rcParams, set once
BLUE, ORANGE, GREEN = PALETTE["series"]
PINK = PALETTE["series_4th"]
GREY = PALETTE["muted"]
INK = PALETTE["ink"]
INK_SOFT = PALETTE["ink_soft"]
SRC = "Synthetic data generated for CDB601220 (Week 3)."
pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 30)
warnings.filterwarnings("ignore", category=FutureWarning)


def finish(fig, name, note, folder=None):
    """Save FIRST (300 dpi, source note), then show. Never the other way round."""
    path = save_fig(fig, (folder or CHARTS) / f"{name}.png", note)
    if IN_NOTEBOOK:
        plt.show()
    plt.close(fig)
    print("saved ->", Path(path).relative_to(ROOT))
    return path



# ## Step 0 - look at the data first


raw = pd.read_csv(DATA / "vitals_10k.csv")
raw.info()


print(raw.describe().T.round(2))


print(raw.ward.value_counts())
print()
print(raw.admit_date.head(20).tolist())


# A few extra checks the four commands do not cover
print("duplicate patient_id:", raw.patient_id.duplicated().sum(),
      "| fully duplicated rows (ignoring id):", raw.drop(columns="patient_id").duplicated().sum())
print("blank cells:", int(raw.isna().sum().sum()))
print("diastolic >= systolic:", (raw.diastolic >= raw.systolic).sum())
print("map_mmhg == (sys + 2*dia)/3 :", np.allclose(raw.map_mmhg, (raw.systolic + 2 * raw.diastolic) / 3, atol=0.06))
print()
for col in ["heart_rate", "bmi", "spo2", "los_days", "age", "chol_mmol_l", "risk_score"]:
    vc = raw[col].value_counts().sort_index()
    print(f"{col:15s} lowest values {dict(list(vc.head(3).items()))}   highest {dict(list(vc.tail(3).items()))}")


# **What I found** (nothing in the file announces any of these):
#
# | # | Problem | How I saw it |
# |---|---|---|
# | 1 | `ward` has **12 spellings for 4 wards**, including a leading space in `" I.C.U"` | `value_counts()` |
# | 2 | `admit_date` is in **three formats** (`2026-01-19`, `08-Mar-2026`, `27/02/2026`), and the slash one is ambiguous | `head(20)` |
# | 3 | `bmi` uses **0 and 999 as "missing"** - that is why the mean BMI is 66 | `describe()` max = 999, min = 0 |
# | 4 | `heart_rate` has **device faults**: zeros and readings of 331-415 bpm | `describe()` max = 415 |
# | 5 | `los_days` has a cluster of **139-274 day stays** with nothing between 30 and 100 days | `describe()` max = 273.65 |
# | 6 | `map_mmhg` is **derived** from systolic and diastolic, so its correlation with them is arithmetic | data dictionary + the `allclose` check |
# | 7 | `risk_score` is a **ratio** (events / days), so its mean is not the overall rate | data dictionary |
# | 8 | `age` is **piled up at 18 and 97** (90 and 133 patients vs about 20 at neighbouring ages) - the ends were clipped | `value_counts()` |
# | 9 | `bmi` piles at **14.0** and `chol_mmol_l` at **2.10**, again a clipped floor; `spo2` sits on its ceiling of 100 | `value_counts()` |
#
# No duplicates, no blank cells, and no diastolic above systolic, so those are fine.


# ## Step 1 - clean it, and log every rule


LOG = {}
df = raw.copy()
LOG["rows loaded"] = f"{len(df):,}"

# 1. ward: strip + lower, then map every spelling onto one of four names
WARD_MAP = {
    "general medicine": "General Medicine", "gen medicine": "General Medicine",
    "cardiology": "Cardiology", "cardio": "Cardiology",
    "day surgery": "Day Surgery", "day-surgery": "Day Surgery",
    "intensive care": "ICU", "icu": "ICU", "i.c.u": "ICU",
}
df["ward_clean"] = df.ward.str.strip().str.lower().map(WARD_MAP)
assert df.ward_clean.nunique() == 4 and df.ward_clean.isna().sum() == 0
LOG["ward spellings conformed"] = (f"{df.ward.nunique()} spellings -> 4 wards (strip, lower, map); 0 rows lost")
print(df.groupby("ward_clean").ward.unique())
print(df.ward_clean.value_counts())


# 2. admit_date: parse each format explicitly. Never let pandas guess day vs month.
iso = pd.to_datetime(df.admit_date, format="%Y-%m-%d", errors="coerce")
mon = pd.to_datetime(df.admit_date, format="%d-%b-%Y", errors="coerce")
dmy = pd.to_datetime(df.admit_date, format="%d/%m/%Y", errors="coerce")
df["admit_dt"] = iso.fillna(mon).fillna(dmy)

slash = df.admit_date[df.admit_date.str.contains("/")].str.split("/", expand=True).astype(int)
print(f"ISO: {iso.notna().sum()}, dd-Mon-yyyy: {mon.notna().sum()}, dd/mm/yyyy: {dmy.notna().sum()}, unparsed: {df.admit_dt.isna().sum()}")
print(f"slash dates with first part > 12: {(slash[0] > 12).sum()}, with second part > 12: {(slash[1] > 12).sum()}  -> day comes first")
wrong = pd.to_datetime(df.admit_date, format="%m/%d/%Y", errors="coerce").notna().sum()
print(f"if I had read them as mm/dd, {wrong} dates would have parsed silently to the wrong day")
print("range:", df.admit_dt.min().date(), "to", df.admit_dt.max().date())
assert df.admit_dt.isna().sum() == 0
LOG["dates parsed"] = (f"3 formats parsed separately (ISO {iso.notna().sum()}, dd-Mon {mon.notna().sum()}, dd/mm {dmy.notna().sum()}); "
                       f"slash = day-first because {(slash[0] > 12).sum()} have day > 12; 0 unparsed")


# 3. bmi sentinels 0 and 999 -> missing
bmi_before = df.bmi.mean()
sent = df.bmi.isin([0, 999])
df.loc[sent, "bmi"] = np.nan
LOG["bmi sentinels removed"] = (f"bmi == 0 ({(raw.bmi == 0).sum()}) or 999 ({(raw.bmi == 999).sum()}) -> NaN, n = {sent.sum()}; "
                                f"mean {bmi_before:.2f} -> {df.bmi.mean():.2f} kg/m2")
print(LOG["bmi sentinels removed"])


# 4. heart_rate device faults. Rule: keep 30-250 bpm. 0 bpm is a disconnected probe,
#    >250 is not survivable at rest. This is the ethics item: removed AND reported.
HR_LO, HR_HI = 30, 250
hr_fault = (df.heart_rate < HR_LO) | (df.heart_rate > HR_HI)
hr_before = df.heart_rate.mean()
df["heart_rate_raw"] = df.heart_rate
df.loc[hr_fault, "heart_rate"] = np.nan
print("faulty readings:", sorted(int(v) for v in raw.heart_rate[hr_fault].unique()))
LOG["heart-rate device faults removed"] = (f"heart_rate < {HR_LO} ({(raw.heart_rate < HR_LO).sum()}, all 0 bpm) or > {HR_HI} "
                                           f"({(raw.heart_rate > HR_HI).sum()}, 331-415 bpm) -> NaN, n = {hr_fault.sum()}; "
                                           f"mean {hr_before:.2f} -> {df.heart_rate.mean():.2f} bpm")
print(LOG["heart-rate device faults removed"])
print("largest genuine reading kept:", df.heart_rate.max(), "bpm")


# 5. los_days: a separate cluster of 139-274 day stays, with an empty gap from 30 to 100 days.
print(np.histogram(raw.los_days, bins=[0, 10, 30, 100, 300])[0], "<- stays in [0-10, 10-30, 30-100, 100-300] days")
long_ = df.los_days > 100
print("as hours / 24 these would be", (df.los_days[long_] / 24).round(1).min(), "to", (df.los_days[long_] / 24).round(1).max(), "days")
print(df.loc[long_, "ward_clean"].value_counts().to_dict())
los_before = df.los_days.mean()
df.loc[long_, "los_days"] = np.nan
LOG["implausible stays removed"] = (f"los_days > 100 -> NaN, n = {long_.sum()} (139.8-273.7 'days', likely hours keyed as days, "
                                    f"incl. {raw.loc[long_, 'ward'].str.lower().str.contains('day').sum()} in Day Surgery); "
                                    f"mean {los_before:.2f} -> {df.los_days.mean():.2f} days, median unchanged at {df.los_days.median():.2f}")
print(LOG["implausible stays removed"])


# 6. map_mmhg is derived; 7. risk_score is a ratio. Neither goes in the heatmap.
LOG["derived column excluded"] = "map_mmhg = (sys + 2 x dia)/3 -> left out of the heatmap (its r with sys/dia is arithmetic)"

events = (df.risk_score * raw.los_days).round()
pooled_rate = events.sum() / raw.los_days.sum()
LOG["ratio column not averaged"] = (f"risk_score is events/day: mean of ratios {raw.risk_score.mean():.2f} vs pooled rate "
                                    f"{pooled_rate:.2f} events/day -> not averaged, not in heatmap")
print(LOG["ratio column not averaged"])

# 8 & 9. clipped ends: kept, but flagged, because the values are real patients at a capped value
LOG["clipped values flagged (kept)"] = (f"age = 18 ({(df.age == 18).sum()}) and 97 ({(df.age == 97).sum()}); bmi = 14.0 ({(df.bmi == 14.0).sum()}); "
                                        f"chol = 2.10 ({(df.chol_mmol_l == 2.10).sum()}); spo2 = 100 ({(df.spo2 == 100).sum()}, physical ceiling)")
LOG["duplicates / blanks"] = "0 duplicate ids, 0 blank cells, 0 diastolic >= systolic - nothing removed"

print()
for k, v in LOG.items():
    print(f"  {k:<34} {v}")


# ### The wide file - `.melt()` it
#
# `ward_los_wide.csv` has one column per ward. Seaborn wants one row per observation, so I melt it and check it is the same data as the long file.


wide = pd.read_csv(DATA / "ward_los_wide.csv")
print(wide.head(3))
long_w = wide.melt(var_name="ward", value_name="los_days").dropna()
long_w["ward"] = long_w.ward.replace({"Icu": "ICU"})
cmp = pd.DataFrame({"wide->melt n": long_w.groupby("ward").size(),
                    "long file n": raw.assign(w=df.ward_clean).groupby("w").size(),
                    "wide->melt median": long_w.groupby("ward").los_days.median(),
                    "long file median": raw.assign(w=df.ward_clean).groupby("w").los_days.median()})
print(cmp)
assert (cmp["wide->melt n"] == cmp["long file n"]).all()
print("same counts and medians - the wide file is the same raw los_days, so it also carries the 18 bad stays")


# ## Step 2 - which pair is worth a scatter? Build the heatmap numbers first.


HEAT_COLS = ["age", "systolic", "diastolic", "heart_rate", "spo2", "bmi", "chol_mmol_l", "glucose_mmol_l", "los_days"]
corr = df[HEAT_COLS].corr()
pairs = corr.where(np.tril(np.ones(corr.shape, dtype=bool), -1)).stack().sort_values(key=abs, ascending=False)
print(pairs.head(6).round(3))


# The strongest pair is systolic-diastolic (0.89), but those are two numbers from the same cuff reading and panel 1 already shows their two-cluster shape. The only pair that links **two different risk measures** is **age and cholesterol (r = 0.34)**. Everything else is between -0.03 and +0.03. So panel 3 is age vs cholesterol.


LABELS = {"age": "Age", "systolic": "Systolic", "diastolic": "Diastolic", "heart_rate": "Heart rate",
          "spo2": "SpO2", "bmi": "BMI", "chol_mmol_l": "Cholesterol", "glucose_mmol_l": "Glucose", "los_days": "Length of stay"}
WARD_ORDER = df.groupby("ward_clean").los_days.median().sort_values().index.tolist()
SAMPLE_N = 3000
BINW = 2


def build_figure(d, hr_col="heart_rate", tag=""):
    fig, ax = plt.subplots(2, 2, figsize=(14, 10.5))

    # ---- panel 1: systolic distribution, bin width declared
    a = ax[0, 0]
    edges = np.arange(d.systolic.min() - 0.5, d.systolic.max() + BINW, BINW)
    a.hist(d.systolic, bins=edges, color=BLUE, edgecolor="white", linewidth=0.3)
    a.axvline(140, color=ORANGE, ls="--", lw=1.3)
    share = 100 * (d.systolic > 140).mean()
    a.text(142, a.get_ylim()[1] * 0.93, f"140 mmHg\n{share:.0f}% of patients above", color=ORANGE, fontsize=8.5, va="top")
    a.text(0.99, 0.97, f"binwidth = {BINW} mmHg\nn = {d.systolic.notna().sum():,}", transform=a.transAxes,
           ha="right", va="top", fontsize=8.5, color=INK_SOFT)
    a.set_xlabel("Systolic blood pressure (mmHg)")
    a.set_ylabel(f"Patients per {BINW} mmHg")
    a.set_title(f"1. Systolic BP is two groups: {share:.0f}% sit in a peak near 163 mmHg",
                fontsize=10.5, loc="left")

    # ---- panel 2: length of stay by ward, log scale, sorted by median, fliers SHOWN
    b = ax[0, 1]
    sns.boxplot(data=d[d.los_days > 0], x="ward_clean", y="los_days", order=WARD_ORDER, ax=b, color=BLUE, width=0.55,
                showfliers=True, flierprops=dict(marker="o", markersize=2, alpha=0.3, markerfacecolor=GREY, markeredgecolor="none"),
                medianprops=dict(color="white", lw=2), boxprops=dict(alpha=0.85))
    b.set_yscale("log")
    meds = d[d.los_days > 0].groupby("ward_clean").los_days.median()
    b.text(0.01, 0.02, f"{(d.los_days == 0).sum()} stays of 0.00 days left out (cannot sit on a log axis)", transform=b.transAxes, fontsize=8, color=INK_SOFT)
    for i, w in enumerate(WARD_ORDER):
        b.text(i + 0.3, meds[w], f"{meds[w]:.2f} d", va="center", fontsize=8.5, color=INK)
    b.set_xlabel("Ward (sorted by median stay)")
    b.set_ylabel("Length of stay (days, log scale)")
    b.set_title(f"2. ICU stays are {meds['ICU']/meds['Day Surgery']:.0f}x longer than Day Surgery (median)", fontsize=10.5, loc="left")

    # ---- panel 3: age vs cholesterol (the pair panel 4 points to)
    c = ax[1, 0]
    sub = d[["age", "chol_mmol_l"]].dropna().sample(SAMPLE_N, random_state=42)
    c.scatter(sub.age, sub.chol_mmol_l, s=7, alpha=0.35, color=BLUE, edgecolors="none")
    full = d[["age", "chol_mmol_l"]].dropna()
    slope, icpt = np.polyfit(full.age, full.chol_mmol_l, 1)
    xs = np.array([18, 97])
    c.plot(xs, slope * xs + icpt, color=ORANGE, lw=2)
    r_ac = full.corr().iloc[0, 1]
    c.text(0.02, 0.97, f"r = {r_ac:.2f} (all {len(full):,} patients)\n+{slope*10:.2f} mmol/L per 10 years\n"
           f"showing a random {SAMPLE_N:,}, alpha = 0.35", transform=c.transAxes, va="top", fontsize=8.5, color=INK_SOFT)
    c.set_xlabel("Age (years)")
    c.set_ylabel("Total cholesterol (mmol/L)")
    c.set_title(f"3. Cholesterol climbs with age: +{slope*10:.1f} mmol/L per decade (r = {r_ac:.2f})",
                fontsize=10.5, loc="left")

    # ---- panel 4: correlation heatmap to the rules
    e = ax[1, 1]
    cols = [hr_col if k == "heart_rate" else k for k in HEAT_COLS]
    cm = d[cols].corr()
    cm.index = cm.columns = [LABELS[k] for k in HEAT_COLS]
    mask = np.triu(np.ones_like(cm, dtype=bool))
    sns.heatmap(cm, mask=mask, cmap="RdBu_r", vmin=-1, vmax=1, center=0, annot=True, fmt=".2f",
                annot_kws={"size": 8}, linewidths=0.6, linecolor="white", square=True,
                cbar_kws={"label": "Pearson r", "shrink": 0.75}, ax=e)
    e.grid(False)
    e.tick_params(axis="x", rotation=45)
    for lab in e.get_xticklabels():
        lab.set_ha("right")
    e.set_title("4. Only two pairs correlate: systolic-diastolic and age-cholesterol",
                fontsize=10.5, loc="left")

    for p in ax.flat:
        p.spines["top"].set_visible(False)
        p.spines["right"].set_visible(False)
    fig.suptitle(f"Clinical safety review, 10,000 admissions: {share:.0f}% are hypertensive, ICU patients stay longest, "
                 "and cholesterol is the only risk marker that tracks age" + tag,
                 x=0.01, ha="left", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


n_hr = hr_fault.sum()
NOTE = (f"n = 10,000 admissions, Jan-Apr 2026. Removed (set to missing, row kept): heart rate <30 or >250 bpm as device faults (n = {n_hr}); "
        f"BMI 0/999 sentinels (n = {sent.sum()}); stays >100 days (n = {long_.sum()}); panel 2 also leaves out {(df.los_days == 0).sum()} stays of 0.00 days. 4 wards conformed from 12 spellings. "
        f"map_mmhg (derived) and risk_score (ratio) excluded from panel 4.\n"
        f"Panel 1 binwidth {BINW} mmHg. Panel 2 log y-axis, outliers shown. Panel 3 random {SAMPLE_N:,} of {df[['age','chol_mmol_l']].dropna().shape[0]:,} "
        f"points (seed 42), fit on all. Panel 4 Pearson r, RdBu_r, vmin -1 vmax 1, upper triangle masked. Appendix: same figure without the heart-rate exclusion. "
        + SRC)

fig = build_figure(df)
finish(fig, "partD_figure", NOTE, folder=SUB)


# **What this chart shows.** Systolic blood pressure has two clear groups, and 42% of patients are
# hypertensive. ICU patients stay about 14 times longer than Day Surgery patients. Cholesterol is the
# only thing that rises with age, while most other measures barely relate to each other.


# ### Appendix - the same figure without the heart-rate exclusion
#
# This is the version the ethics clause asks for. Only panel 4 uses heart rate, so that is the only panel that can change.


fig = build_figure(df, hr_col="heart_rate_raw", tag="  [APPENDIX: heart-rate faults NOT removed]")
finish(fig, "partD_appendix_no_exclusion",
       f"APPENDIX. Identical to partD_figure.png except the {n_hr} heart-rate device faults (0 bpm and 331-415 bpm) are kept. " + SRC)

hr_r_clean = df[HEAT_COLS].corr()["heart_rate"].drop("heart_rate")
hr_r_raw = df[[c if c != "heart_rate" else "heart_rate_raw" for c in HEAT_COLS]].corr()["heart_rate_raw"].drop("heart_rate_raw")
print("largest change in any heart-rate correlation:", (hr_r_clean.values - hr_r_raw.values).__abs__().max().round(3))


# **What this chart shows.** This is the same figure with the 37 faulty heart-rate readings left in.
# Nothing important changes: no correlation moves by more than 0.03. So removing them was fair, and
# I'm not hiding anything that would change the results.


# ## Cleaning log (pasted into Part E)


for k, v in LOG.items():
    print(f"  {k:<34} {v}")
pd.Series(LOG).to_csv(SUB / "partD_cleaning_log.csv", header=["detail"])
