# Week 1 — Why we visualize, and choosing the right chart

Five tasks, each a self-contained notebook committed with its outputs.

| Task | Notebook | Dataset | Question it answers |
|---|---|---|---|
| 1 | [`task1_datasaurus.ipynb`](task1_datasaurus.ipynb) | Datasaurus Dozen | Why summary statistics are not enough |
| 2 | [`task2_gapminder.ipynb`](task2_gapminder.ipynb) | Gapminder | Trends over time, and the spaghetti-chart problem |
| 3 | [`task3_penguins.ipynb`](task3_penguins.ipynb) | Palmer Penguins | Distributions, relationships and Simpson's paradox |
| 4 | [`task4_mpg.ipynb`](task4_mpg.ipynb) | Auto MPG | Picking the right chart for five different questions |
| 5 | [`task5_flights.ipynb`](task5_flights.ipynb) | Airline passengers | Trend vs seasonality in a real time series |

Each notebook explains its chart choice inline, under a **"Why this chart"** note beside every figure.

## Setup

```bash
python download_assignment_data.py   # writes data/
jupyter notebook
```

Task briefs and the marking guide are in [`TASKS.md`](TASKS.md).

## Chart analysis

**Task 1 — Datasaurus.** All 13 datasets share the same mean x (≈54.26), mean y (≈47.83) and correlation (≈−0.06), so the summary table says they are identical. The scatter grid shows a dinosaur, a star, a bullseye and a set of lines. Correlation only measures a straight-line relationship, so it cannot see shape.

**Task 2 — Gapminder.** The 142-line chart is unreadable and its legend is bigger than the plot; averaging to five continent lines recovers the trend, and greying everything except China, Rwanda and Zimbabwe recovers the exceptions. On a log scale the 90th/10th percentile gap roughly doubled, from about 15× to 38× — the poorest got richer, the richest much faster.

**Task 3 — Penguins.** The body-mass histogram has a long right tail and a second hump, which splitting by species explains: Adelie and Chinstrap sit near 3,700 g, Gentoo near 5,000 g. The bill scatter is Simpson's paradox — overall r = −0.24, but positive inside every species (0.39, 0.65, 0.64), because species is a hidden third variable.

**Task 4 — Auto MPG.** Fuel efficiency rose from 1970 to 1982, and the weight–mpg scatter curves rather than falling straight. Redrawing Q2 as a box plot with every car plotted shows what the bar of means hid: the groups overlap, and 44 American cars beat the median European one. Median weight fell about 440 lbs, but at 3,000 lbs the late cars still gain ~5 mpg, so weight is only part of it.

**Task 5 — Airline passengers.** The full time series carries both the growth and the seasonality, which is why it is the one chart for the report. July and August are always the top two months. Dividing each month by its year's average makes the lines almost coincide, so the swings are mostly proportional — though the peak/low ratio does creep from about 1.4 to 1.6.
