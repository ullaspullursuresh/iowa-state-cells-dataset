# Early-Life Battery Lifetime Prediction

Reproduction of *"Predicting battery lifetime under varying usage conditions from early aging data"* (Li, Zhou, Thelen, Howey, Hu; *Cell Reports Physical Science* 5, 101891, 2024), as a part of a project on Predicting Lifetime of in-house batteries using Machine Learning. 

> **Status:** Reproduction on the published ISU-ILCC dataset: **complete**. Extension to in-house data: **in progress** (data processing stage).

<!-- Fill in every [BRACKETED] item. Delete this comment and any section you don't need. -->

---

## Overview

Predicting how long a lithium-ion cell will last from only its early-life data lets you screen cells and cycling conditions without running every cell to end of life. The paper tackles a harder version of this problem than earlier work: cells are cycled under widely varying charge rates, discharge rates and depths of discharge (DoD), so their degradation paths diverge.

This repository:

1. Reproduces the paper's feature engineering and two models (elastic net regression and a hierarchical Bayesian model, HBM) on the public dataset.
2. Compares my results to the paper's, and documents where and why they differ.

**Reproduction approach** 

1. Data processing: Most of the features required for the full the reproduction was aquired from the 'Q-Interpolated' file that was shared as a part of the original dataset. But some of the more trivial features required the charging conditions. Which had to be manually added in.

2. Hold Out split: The data that was held out for final testing was the exact same split that the paper use. 

3. The 

## The problem

- **Input:** features from the first weeks of aging (the paper uses weekly reference performance tests at week 0 and week 3, roughly 18% of the average lifetime).
- **Output:** cell lifetime in weeks, where end of life (EOL) is 80% of rated capacity (200 mAh of 250 mAh).
- **Difficulty:** cells cycled under different conditions show one-, two- and three-stage capacity fade, and well-known features from earlier work (for example the variance of the discharge capacity difference, ΔQ(V)) explain little of the variance here.

## Dataset

**ISU-ILCC NMC/Graphite battery aging dataset** (used for the reproduction)
- 225 commercial 502030 NMC/graphite pouch cells, 250 mAh rated, 3.0 to 4.2 V, tested at 30 °C
- Cycled in groups of four cells per condition, across charge rates 0.5C to 3C, discharge rates 0.5C to 2.5C, and DoD roughly 4% to 100%
- Lifetimes range from 1.5 to 60.9 weeks
- A weekly reference performance test (RPT) with two full-DoD cycles (C/2 and C/5) gives consistent capacity-voltage data even for cells that cycle at partial DoD
- Download: https://doi.org/10.25380/iastate.22582234 (not redistributed here)

**Data notes** (things that affect a reproduction)
- Groups 49 and 57 had no cell reach EOL when the paper was written, so they are not in the paper's results. Group 15 was removed for safety reasons.
- From group 20 onward an extra RPT was run at week 0.5, so index-based selection of "week 3" differs between early and later groups.
- Week 4 data was lost for a large batch of cells.
- [Note anything else you hit, e.g. missing cycles, unit or format issues.]

**In-house dataset** (extension, in progress)
- [Number] cells, [chemistry], [test types available, e.g. formation cycle, EIS, C-rate, cycling stability]
- Current status: [e.g. cleaning cycler files, aligning cycles, building lifetime labels]
- Not included in this repository. [Reason.]

## Method

**Train/test split (by condition group, not by cell).** All cells from one cycling condition stay together. The data is first divided at 40% DoD:

| Set | Cells | What it tests |
|-----|-------|---------------|
| Training (high DoD) | 116 | |
| High-DoD test | 60 | In-distribution prediction |
| Low-DoD test (< 40% DoD) | 49 | Extrapolation to unseen conditions and longer lifetimes |

**Features.** From the week 0 and week 3 RPTs, 29 candidate features were extracted from six sources: incremental capacity (dQ/dV), capacity-voltage differences, differential voltage, constant-voltage charge time, capacity fade, and cycling-condition stress terms. The key one is the mean change in incremental capacity between 3.6 and 3.9 V, whose voltage window was found by an exhaustive grid search (0.01 V steps over 3.0 to 4.2 V, minimum window 0.02 V) maximizing Pearson correlation with lifetime (ρ = −0.848 in the paper).

**Feature selection.** Stepwise forward selection with 5-fold cross-validation repeated 5 times, up to 10 features, on the training set only. The paper's chosen two-feature set is `log(mean ΔdQ/dV, 3.6–3.9 V)` and `log|Δ CV time|`; the three-feature set adds DoD.

**Models** (target is log lifetime)
- **Elastic net** on the selected features ("degradation-informed" model)
- **Hierarchical Bayesian model (HBM):** cells are grouped by average stress, `Stress_avg = (C_chg^0.5·DoD^0.5 + C_dchg^0.5·DoD^0.5)/2`, using constrained K-means with K = 4. A condition-level model sets the parameters of a cell-level Bayesian linear regression, which also gives prediction uncertainty.
- **Baselines:** a dummy model (predicts the training mean), a cycling-conditions-only model, and the "discharge model" from Severson et al. (2019).

**Metrics:** MAPE and RMSE on lifetime (weeks, linear scale).

## Results

Paper values are from Table 2 of the paper. Cells show *paper / this repo*.

| Model | Features | High-DoD MAPE (%) | Low-DoD MAPE (%) | High-DoD RMSE (wk) | Low-DoD RMSE (wk) |
|-------|----------|-------------------|------------------|--------------------|-------------------|
| Dummy | 0 | 31.5 / [ ] | 47.5 / [ ] | 4.8 / [ ] | 18.5 / [ ] |
| Cycling conditions | 3 | 19.0 / [ ] | 23.7 / [ ] | 3.3 / [ ] | 9.8 / [ ] |
| Discharge model (Severson) | 5 | 28.0 / [ ] | 24.8 / [ ] | 4.7 / [ ] | 11.5 / [ ] |
| Elastic net, degradation-informed | 2 | 16.0 / [ ] | 24.4 / [ ] | 3.0 / [ ] | 7.8 / [ ] |
| Elastic net, degradation-informed | 3 | 15.1 / [ ] | 33.0 / [ ] | 2.8 / [ ] | 9.7 / [ ] |
| HBM | 2 | 16.9 / [ ] | 21.8 / [ ] | 3.1 / [ ] | 7.3 / [ ] |
| HBM | 3 | 15.8 / [ ] | 24.1 / [ ] | 2.9 / [ ] | 7.5 / [ ] |

*(Delete rows you did not reproduce.)*

**Summary:** [1 to 2 sentences, e.g. "Elastic net matched the paper within X points on the high-DoD test set. The HBM improved low-DoD extrapolation as reported, though my gap was Y."]

Add plots: `![Predicted vs actual](figures/pred_vs_actual.png)` and, if you ran the HBM, predictions with uncertainty bars.

## Differences from the paper

Being explicit here makes the reproduction more credible.

- [e.g. "Random seeds and cross-validation folds differ, so exact numbers vary slightly."]
- [e.g. "Feature X was implemented with a different interpolation / smoothing choice."]
- [e.g. "HBM implemented with [library]; priors as in the paper (γ ~ N(0, 10), σ ~ HalfCauchy(1))."]
- [Anything you could not reproduce, and your best explanation.]

## Repository structure

```
.
├── data/               # download instructions (raw data not committed)
├── notebooks/          # exploration and analysis
├── src/                # preprocessing, feature extraction, models, evaluation
├── figures/            # result plots
├── requirements.txt
└── README.md
```

*(Edit to match your actual layout.)*

## Getting started

```bash
git clone [repo url]
cd [repo name]
pip install -r requirements.txt
```

Download the dataset from the link above into `data/`, then run:

```bash
python src/[main script].py [args]
```

Or open `notebooks/[main notebook].ipynb`.

## Limitations

- Trained and evaluated on one cell type (NMC/graphite) tested in a controlled lab setting with constant cycling conditions.
- The optimal voltage window (3.6 to 3.9 V) was tuned on this dataset and may not transfer to other cells; the paper suggests re-running the grid search for new data.
- [Add your own, e.g. small number of test groups, wide error bars.]

## Roadmap

- [x] Reproduce the paper on the published dataset
- [ ] Process and clean in-house cell data
- [ ] Apply the pipeline to in-house data and compare
- [ ] [Next step, e.g. state-of-health estimation toward a BMS-style model]

## References

- T. Li, Z. Zhou, A. Thelen, D. A. Howey, C. Hu. *Predicting battery lifetime under varying usage conditions from early aging data.* Cell Reports Physical Science 5, 101891 (2024). https://doi.org/10.1016/j.xcrp.2024.101891
- Authors' code: https://doi.org/10.5281/zenodo.10648587
- Dataset: T. Li, A. Thelen, J. Liu, C. Tischer, C. Hu (2023). ISU-ILCC Battery Aging Dataset. https://doi.org/10.25380/iastate.22582234
- K. A. Severson et al. *Data-driven prediction of battery cycle life before capacity degradation.* Nature Energy 4, 383 (2019).

This is an independent reproduction for learning purposes and is not affiliated with the original authors.

## Acknowledgements

[Optional: advisors, institution, lab.]

## License

[e.g. MIT for your code. The dataset has its own terms; see the download page.]
