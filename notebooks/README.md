# Cross-product notebooks

Worked examples that span more than one of the three products. Each notebook should be runnable end-to-end against the shipped parquets (or a downloaded subset for partial demos).

## Planned

### `joint_use_demo.ipynb` — fetal mortality rate by maternal race, 2022

Loads the fetal-death and natality parquets, applies each product's canonical analytic filter, joins on `data_year` and `maternal_race_bridged`, and computes the fetal mortality rate per 1,000 (live births + fetal deaths) by race. Compares each cell against *NVSR 73-09* Table A.

The pseudocode is in [`docs/JOINT_USE_GUIDE.md`](../docs/JOINT_USE_GUIDE.md).

### `paper_companion.ipynb` — reproduce every numeric claim in the manuscript

Loads all three parquets, computes every count, rate, and validation metric cited in the Data Resource Profile manuscript directly from the data, and emits a Markdown table mapping each paper claim to its source artifact. Intended to demonstrate the reproducibility claim from outside the manuscript.

### `era_boundary_walkthrough.ipynb` — what changes at each NCHS layout boundary

A pedagogical notebook that loads the same demographic stratum across each of the era boundaries described in Table 1 of the manuscript, and shows where the harmonization made decisions (renames, value-level normalizations, comparability classifications). Useful for new users and reviewers who want to verify the harmonization choices.

## Status

All three are stubs as of the initial monorepo migration. The `joint_use_demo.ipynb` is the highest-leverage one for the manuscript's "designed for joint use" claim and should be filled in first.
