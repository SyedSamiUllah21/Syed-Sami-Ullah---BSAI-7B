# Week 3 — Matplotlib & Seaborn

Nine charts that are wrong, a Lie Factor audit, a colour-blindness proof, and the 2×2 clinical review figure.

**CLO1 — Use Python for basic static chart generation. · CLO2 — Create statistical charts for data exploration.**

← [Back to the course index](../README.md)

## Run it

```bash
cd week3
python vizlib.py                       # self-check that the toolkit works
jupyter notebook                       # open any partX notebook and Run All
```

Or run the hand-in scripts directly. They work from any folder and need nothing else:

```bash
python submission/partA_charts.py
python submission/partD_figure.py      # run before partC (C simulates the Part D figure)
python submission/partB_lie_factor.py
python submission/partC_palette.py
python submission/popout_experiment.py         # panels + results chart
python submission/popout_experiment.py --run   # time one participant (do this 5 times)
```

Requires `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `jupyter`, `ipykernel`. All data is already in `data/`. Nothing to download.

## Contents

| Path | What it is |
|---|---|
| `TASKS.md` | The brief and marking guide |
| `vizlib.py` | Course toolkit: palette, `lie_factor()`, `simulate_cvd()`, `match_stats()` |
| `data/` | Ten synthetic datasets + `DATA_DICTIONARY.md` |
| `starter/` | The three original starter files, untouched |
| `partA_nine_charts.ipynb` | Part A: nine rebuilds, self-checks, diagnoses, redesigns |
| `partB_lie_factor.ipynb` | Part B: Lie Factor audit A–E, plus Chart F |
| `partC_palette.ipynb` | Part C: CVD simulation and OKLab audit of two palettes |
| `partD_clinical_figure.ipynb` | Part D: inspection, cleaning log, the 2×2 figure, the appendix |
| `bonus_popout_experiment.ipynb` | Bonus: four pop-out panels, timing harness, results chart |
| `charts/` | Every rebuilt and redesigned chart (300 dpi PNG) |
| `submission/` | The exact hand-in files from TASKS.md |

### `submission/` — the hand-in

| File | Part |
|---|---|
| `partA_charts.py` · `partA_diagnosis.pdf` | A: rebuilds all nine and plots the nine redesigns; one page per case with both figures |
| `partB_lie_factor.py` · `partB_output.txt` | B: script + its printed output |
| `partC_palette.py` · `partC_palette.png` | C: script + before/after swatch sheet |
| `partD_figure.py` · `partD_figure.png` · `partD_cleaning_log.csv` | D: script, 300 dpi figure, cleaning log |
| `partE_justification.pdf` | E: one page |
| `popout_experiment.py` · `popout_panels.png` | Bonus: experiment + panels (results chart appears after the five runs) |

## Self-checks

All **52** Part A self-checks pass. Every one is an `assert`, so the notebook stops if a rebuild is not faithful.

| Case | Target | Mine |
|---|---|---|
| 1 | Standard 2.15, Premium 5.40 per 1,000 trips | 2.15, 5.40 |
| 2 | r = 0.98 | 0.982 |
| 3 | before 202, after 137, −32% | 202.1, 137.2, −32.1% |
| 4 | mean 18.00 / 14.50, r = 0.816 (all four) | yes |
| 5 | 48.00 / 63.00, SD 12.00 / 15.00, r = 0.420 (all five) | yes |
| 6 | creatinine–hba1c 0.77, systolic–map 0.96, 20 × 20 | 0.765, 0.958, 20 × 20 |
| 7 | cost drawn above revenue Jan–Apr | yes, and not May–Jun |
| 8 | n = 10,000 in all three panels | yes |
| 9 | max spo2 = 100 | 100 (curve reaches 101.1) |

## Chart analysis

**Part A — nine charts.** None of the nine is arithmetically wrong. Each one goes wrong for a reason that is easy to miss:

1. **Helmets:** Simpson's paradox. 85% of Premium trips are on motorways, and inside every road type Premium has about 25% fewer injuries.
2. **Chai:** enrolment tripled, and both counts follow head-count. Per student, r drops from 0.98 to 0.29.
3. **AQI:** on day 61, nine stations went offline, including all six Industrial ones. The 13 stations that kept reporting moved by +0.1%.
4. **Departments:** Anscombe's quartet. One department is a curve, and in another r = 0.816 comes from a single student.
5. **Cohorts:** the statistics were forced with `match_stats`. Inside each of the "two clusters" the correlation is negative.
6. **Heatmap:** creatinine–HbA1c 0.77 is one participant (r = −0.004 without them). The matrix also hides a derived column, a device confound that flips the sign of resting HR vs VO2max, and 20 "significant" pairs where 9.5 are expected by chance. Redrawing the heatmap fixes none of these content problems.
7. **Dual axis:** two independent scales invent the crossing. On one axis revenue beats cost every month, and the margin grows from 15% to 32%.
8. **Bins:** 3 bins hide two populations (peaks near 121 and 163 mmHg). 400 bins on integer data leave 296 empty bins.
9. **KDE:** the smoothing spills 304 readings sitting at 100% over the ceiling. The data itself never goes above 100.

**Part B — Lie Factor.** C is the only honest graphic (1.00). A exaggerates 75× because of a cut baseline. B and E exaggerate 2.5× and 5× because they scale area, and both read as "honest" if `ink_dimension` is left at 1. D understates a 50% rise as 12.5% (LF 0.25). Chart F has no Lie Factor at all: the drawn gap between the lines starts negative while the real gap is positive every month.

**Part C — palette.** Matplotlib's tab10 fails all three simulations. Green and red fall to ΔE 4.1 under deuteranopia, and orange and green to ΔE 0.7 under protanopia. The course palette's three slots never drop below 8. Its fourth slot drops to ΔE 7.5 against green, so whenever it is used it needs direct labels or marker shapes.

**Part D — clinical figure.** I found nine data problems before plotting anything, and each one has a rule and a count in the log. The four panels show:

- systolic BP is two populations, with 42% above 140 mmHg
- ICU stays are 14× longer than Day Surgery stays (median)
- cholesterol rises about 0.2 mmol/L per decade (r = 0.34)
- only two pairs in the heatmap correlate at all

The appendix keeps the 37 heart-rate faults in. No correlation changes by more than 0.03.

**Bonus — pop-out.** The panels and the timing harness are built. *The five-person runs still have to be done:* run `popout_experiment.py --run` once per classmate. The results chart and the three sentences are then generated from the real times. No times are invented.
