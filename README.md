# U.S. Harmonized Vital Statistics Microdata

A single repository containing harmonized U.S. natality, linked birth–infant death, fetal death, and matched-multiples public-use microdata from the National Center for Health Statistics (NCHS), released under CC BY 4.0. Each product carries one stable column schema spanning all years it covers, despite multiple Standard Certificate revisions and NCHS layout reformats in the underlying source files.

This repository unifies two previously separate projects:

- [yoelplutchok/natality-harmonization](https://github.com/yoelplutchok/natality-harmonization) — natality 1968–2024 + linked birth–infant death 2005–2023
- [yoelplutchok/fetal-death-harmonization](https://github.com/yoelplutchok/fetal-death-harmonization) — fetal death 1992–2022

Future development happens here; the original repos are mirrors.

## Four products at a glance

| Product | Years | Records | Columns | NVSR validation | Source code |
|---|---|---|---|---|---|
| **Natality** | 1968–2024 (57 years) | 201,161,456 | 84 (71 harmonized + 13 derived) | 183/183 *Births: Final Data* targets byte-exact (1990–2024; pre-1990 benchmarking planned) | [`natality/`](natality/) |
| **Linked birth–infant death** | 2005–2023 (19 years) | 74,943,824 | 94 (87 harmonized + 7 derived death-side) | 33/35 byte-exact (2 cells differ by 1 record from NCHS upstream null-weight survivor records) | [`natality/`](natality/) |
| **Fetal death** | 1982–2024 (43 years) | 2,427,233 | 89 (73 harmonized + 16 derived) | 29/29 per-year counts + 26/26 per-year fetal mortality rates byte-exact (V2 era); 13/19 detail cells byte-exact + 6 documented diffs | [`fetal_death/`](fetal_death/) |
| **Matched multiples** | 1995–1997 + 1995–2000 + 2016–2020 (3 windows) | 1,665,568 | 24 harmonized | 5/5 byte-exact cells from 2016-2020 PDF Table 1 *Total* column (Total / Birth / Survivor / Infant death / Fetal death); twin "complete-set" IMR = 10.14/1,000 reproduces PDF prose byte-exact | [`matched_multiples/`](matched_multiples/) |

Each product is also distributed as per-year raw parquets preserving every documented source field for users who need detail outside the harmonized schema.

## Repository layout

```
vital-statistics-harmonization/
├── README.md                     ← this file
├── PROJECT_STRUCTURE.md          ← detailed map (humans + LLMs)
├── VERSION_ROADMAP.md            ← V2.1, V3, joint-use layer, etc.
├── CITATION.cff                  ← how to cite
├── LICENSE                       ← CC BY 4.0 (data) / MIT (code)
├── docs/                         ← cross-product documentation
│   ├── JOINT_USE_GUIDE.md        ← computing rates that need both numerator and denominator
│   ├── COMPARABILITY.md          ← cross-product era boundaries + bilateral race-coding methodology
│   ├── NCHS_SOURCE_MANIFEST.md   ← SHA-256 for 100 raw NCHS zips (43 fetal-death + 35 natality + 19 linked + 3 matched-multiples)
│   └── PRIOR_ART.md              ← literature gap that motivates the harmonization
├── migrations/                   ← per-subproject version-to-version migration guides
│   ├── v2.7.0-to-v2.8.0-natality.md
│   └── v2.0.0-to-v2.4.0-fetal-death.md
├── natality/                     ← natality + linked birth–infant death
│   ├── README.md                 ← product-specific docs
│   ├── scripts/                  ← parsing, harmonizing, validating
│   ├── metadata/                 ← schema, validation targets
│   └── output/validation/        ← per-target pass/fail tables
├── fetal_death/                  ← fetal death harmonization
│   ├── README.md
│   ├── scripts/
│   ├── metadata/
│   └── ...
├── matched_multiples/            ← matched-multiples (twins/triplets/quads + linked infant deaths)
│   ├── README.md
│   ├── ABOUT_SOURCE_DATA.md
│   ├── harmonized_schema.csv
│   ├── file_inventory.csv
│   ├── record_layout_*.csv
│   ├── scripts/
│   └── output/
├── notebooks/                    ← cross-product worked examples
├── paper/                        ← Data Resource Profile manuscript drafts
├── figures/                      ← cross-product figures
└── shared/helpers/               ← Python utilities shared across products
```

See [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) for the full map and where to find specific things.

## Validation

All three products are validated against every per-year figure NCHS publishes in the relevant *National Vital Statistics Reports* series under each product's canonical analytic filter. Validation tables ship inside each subproject's `metadata/` and `output/validation/` directories, and the verification scripts under each `scripts/05_validate/` are runnable end-to-end.

## Reproducibility

Each subproject's pipeline is deterministic and re-runnable end-to-end from the public NCHS source files. SHA-256 checksums for every shipped artifact are committed. Re-deriving the parquets from a fresh download of the NCHS source zips produces byte-identical files. See each subproject's `REPRODUCING.md`.

### Pinned environment via `uv` lockfile

The monorepo ships a [`pyproject.toml`](pyproject.toml) + [`uv.lock`](uv.lock) (generated by [`uv`](https://docs.astral.sh/uv/)) pinning Python 3.13 and every runtime + dev dependency to exact versions matching the canonical build. To reproduce the env on a fresh machine:

```bash
# Install uv (one-time): see https://docs.astral.sh/uv/getting-started/installation/
curl -LsSf https://astral.sh/uv/install.sh | sh

# From the monorepo root:
uv sync          # creates .venv/ matching uv.lock exactly
uv run pytest fetal_death/tests/ natality/tests/ tests/
# expected: 56 passed + 1 xfailed
```

Per-subproject `requirements.txt` files are preserved as discovery pointers for users without `uv`, but `uv.lock` is the canonical pinned env. A Dockerfile providing a one-command full-pipeline rebuild is planned as a follow-up task.

## Companion paper

A Data Resource Profile manuscript covering all three products as a unified resource is being prepared. Drafts live in [`paper/`](paper/). The current preferred draft is [`paper/draft_v2_hmd_styled.md`](paper/draft_v2_hmd_styled.md), modeled on the IJE Data Resource Profile for the Human Mortality Database.

## Citation

See [`CITATION.cff`](CITATION.cff) for citation metadata. Until the unified Zenodo deposit is published, cite the two existing deposits:

- Plutchok Y. *Harmonized U.S. Natality and Linked Birth–Infant Death Microdata*. Zenodo. https://doi.org/10.5281/zenodo.19363074 (concept DOI)
- Plutchok Y. *Harmonized U.S. Fetal Death Microdata, 1992–2022*. Zenodo. https://doi.org/10.5281/zenodo.20031571 (v2.0.0)

## License

Harmonized data: Creative Commons Attribution 4.0 International (CC BY 4.0). Underlying NCHS source data are works of the U.S. Government and are not subject to U.S. copyright (17 U.S.C. § 105). Source code: MIT (see [`LICENSE`](LICENSE)).
