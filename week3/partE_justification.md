# Week 3 · Part E — justification for the clinical review figure

Syed Sami Ullah - BSAI-7B · figure: *partD_figure.png* (script *partD_figure.py*) · vitals_10k.csv, synthetic data (CDB601220)

## 1 · Per panel: question, chart type, channel rule

**Panel 1 - Is systolic BP one population or two?** Histogram, because the question is about the shape of one numeric variable. It encodes count as **position/length on a common baseline**, the top of the Cleveland-McGill ranking, so the dip at 140 mmHg and the two peaks read directly. One hue only; orange is spent on the 140 mmHg reference line.

**Panel 2 - Which ward keeps patients longest?** Box plot, because I am comparing a skewed distribution across four groups and the median and spread matter more than the mean. Median is **position on a common scale**; wards are sorted by median so the order itself carries the ranking (Week 2: sort unordered categories by value). One colour, because ward is already named on the axis.

**Panel 3 - Does any risk marker move with age?** Scatter, the chart for a relationship between two numbers. Both variables are on **position** (x and y), the strongest channel; the fit line is the one highlight colour. Alpha and subsampling stop 10,000 points becoming a solid block.

**Panel 4 - Which pairs are worth a closer look?** Lower-triangle correlation heatmap, used as a screening tool. Colour is the weakest channel, so every cell also carries the number (**redundant coding**), and a diverging map is used because r has a sign: hue = direction, lightness = strength, white = zero.

## 2 · Every parameter, and why

**binwidth = 2 mmHg, edges on half-integers**: systolic is recorded in whole mmHg, so each bin holds exactly two values. I tried 3, 45 and 400 bins (Part A case 8); 3 hides the second peak and 400 is mostly empty bins. **log y-axis on panel 2**: length of stay runs from 0.01 to 24 days, and on a linear axis Day Surgery collapses to a line. **showfliers=True**: outliers are shown, not hidden. **2 stays of 0.00 days** are left out of panel 2 only, because log(0) cannot be drawn, and this is stated on the figure. **3,000-point random sample (seed 42), alpha 0.35, marker size 7** for panel 3, while r and the fit line use all 10,000 points. **cmap RdBu_r, vmin -1, vmax +1, center 0, upper triangle masked, fmt .2f**: r is signed and bounded, and the upper triangle repeats the lower one. **Pearson r**: Spearman gives the same two pairs (0.87, 0.33). **Columns left out of panel 4**: map_mmhg (computed from systolic and diastolic), risk_score (a ratio), readmitted_30d (binary).

## 3 · Every row removed: rule, count, and what moved

Values were set to missing in the affected column only; no patient row was dropped, so n stays 10,000 for every other column. **BMI** 0 or 999 are 'missing' codes: n = 486 (84 zeros, 402 nines), mean BMI 66.18 → 27.35 kg/m2. **Length of stay** above 100 days: n = 18 (139.8-273.7 days, with nothing at all between 30 and 100 days; divided by 24 they would be normal stays, so they look like hours typed as days, 6 of them in Day Surgery). Mean 2.31 → 1.95 days; median unchanged at 1.38. **Ward**: 12 spellings conformed to 4 wards, 0 rows lost. **Dates**: three formats parsed one by one; the slash format is day-first (1,933 have a day above 12); 0 unparsed. **Flagged, kept**: ages piled at 18 (90) and 97 (133), BMI 14.0 (44), cholesterol 2.10 (47) look like clipped ends, but they are real patients at a capped value, so I kept them.

**Heart rate.** Readings below 30 bpm or above 250 bpm were removed as device faults (n = 37: eight readings of 0 bpm and 29 between 331 and 415 bpm). Mean heart rate moves from 78.83 to 78.05 bpm. The figure was also produced without the exclusion; it is in the appendix (*charts/partD_appendix_no_exclusion.png*), and no heart-rate correlation changes by more than 0.03.

**Symmetry test.** Yes, I would make exactly the same removal if it weakened my conclusion. The rule was fixed from physiology before I looked at any result: 0 bpm is a detached probe and nothing above 250 bpm is a resting human heart. The removal does not help any finding either, since heart rate correlates with nothing in panel 4 with or without the faults. It is a cleaning rule, not an edit.
