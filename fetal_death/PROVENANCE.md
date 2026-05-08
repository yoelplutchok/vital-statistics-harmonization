# PROVENANCE

This file lists SHA-256 checksums for every artifact in this Zenodo deposit, along with the pipeline git commit that produced them.

## Pipeline version

- **GitHub commit**: `bfbcfea7b4ce8c22eb6203bb92b20132a4fff280` (`bfbcfea`)
- **Repository**: https://github.com/yoelplutchok/fetal-death-harmonization
- **Tag**: v2.0.0
- **Built (UTC)**: 2026-05-05T01:20:11Z (= 2026-05-04 21:20:11 EDT — file mtimes are local-time EDT, the build timestamp is UTC)
- **Pipeline runtime**: ~6 minutes (parse → harmonize → derive → validate) on a 2024-vintage laptop

## Self-coverage note

`PROVENANCE.sha256` lists a hash for **every other file** in this deposit, including `PROVENANCE.md` (the human-readable copy of the same hashes). `PROVENANCE.sha256` does not list itself, by convention — verify its integrity via the deposit's published Zenodo file metadata (Zenodo records each file's MD5/SHA-256 server-side). To verify everything else:

```bash
shasum -a 256 -c PROVENANCE.sha256
```

A fresh download should produce 33 `OK` lines.

## Reproducibility

Re-running `scripts/run_pipeline.py` against the same NCHS public-use source zips produces these files bit-equivalent. The checksums below let you verify your downloaded copy is byte-identical to the deposit.

## File checksums

### Top-level files

| File | Size | SHA-256 |
|---|---|---|
| `README.md` | 11757 B | `4f42967650ae6028208742cba18a1c3e755b889e98edec6bff218c004281f805` |
| `REPRODUCING.md` | 5522 B | `be2d41d5355eb86060b15008cc216fc20d8f23e2a96ca157f3c7ecfe2160d91f` |
| `LICENSE` | 1690 B | `f715f0eb4ba500d341d2f3bb84287ef33ebda1ae1c3b7ee1acd48e09af8792cc` |
| `CITATION.cff` | 1945 B | `786884b5a83d1764f5df08a959dc425e4ae5bb61d0ada2c766a4cfba32f94658` |
| `requirements.txt` | 517 B | `7bb74ce8adfdf2b23c1f664f7958bd78c0d80962553ea271e8c356ca4f506646` |
| `quickstart.py` | 6124 B | `21657b67325e6d0e7e468fa6decc4af0edcd3ed29907dee4845cce4181bc7048` |
| `.zenodo.json` | 3092 B | `9572b59e9673e93bf0ea837772a5d8bed0fb31ec3ae136554761236f9a2d4c6c` |

### Primary data files

| File | Size (MB) | SHA-256 |
|---|---|---|
| `fetal_death_harmonized.parquet` | 19.65 | `f09beb4a717e6fd4ef37c2fbf10752f68004e5a261a270cfeb693849b7805928` |
| `fetal_death_derived.parquet` | 24.27 | `90af89b9e659ca2b580d8286b5598588cfb2d17e93f26c1dc1ae00d097f0afdd` |
| `fetal_death_harmonized.V1_baseline.parquet` | 12.99 | `cbcc91d24f2982d74bef0ba87a64495fb5cbd27928f720ee63d4006581bea2c0` |
| `fetal_death_derived.V1_baseline.parquet` | 15.80 | `2795f099380461581a59908b7653f536bb5f1cdbfd78f101097f0495c0232a8d` |

### Yearly raw parquets (bundled archive)

| File | Size (MB) | SHA-256 |
|---|---|---|
| `fetal_death_yearly_raw_1992-2022.zip` | 34.94 | `789f50b7f8b2ba4e8a2a0e954f213a45e8930de2691065eefb1f298c49854864` |

### Documentation

| File | SHA-256 |
|---|---|
| `ABOUT_SOURCE_DATA.md` | `c3d309da9bdf591ba5132e649816a00308d701bc84a0a1441e8deb4fb8c1f9b0` |
| `ABOUT_THIS_RELEASE.md` | `c853c9d0fc90f66f906b3d79746fad67147290a8eedc3212877f15ed089a6985` |
| `CODEBOOK.md` | `5565aee43df71635072b4d8889adb7d647d7b0169872b80064dab1e9f72ff2c9` |
| `COMPARABILITY.md` | `6e46d06b0bd7f757773d55f6592636699e3149825b82b98eec67047f58685344` |
| `FAQ.md` | `eaa65ccc2a79358e3a66d846b04c56b5b5bd0a834cef0c7c0f9c8e14e20af3b0` |
| `GETTING_STARTED.md` | `1259c159d30eb62ed643d4fc790596b7bc20cee03845cc6feb3126bb610f25bd` |
| `REPORTING_THRESHOLDS.md` | `4e77aaecebc3bdaa1d39d86a129a2256b9e60063f2e6584766e3ea199a97db7d` |
| `V2_1992_LAYOUT_DECISIONS.md` | `1f6125767f1da5926dae3158225298f44046d7717a72ae2ada0c53c1a6cc698c` |

### Metadata

| File | SHA-256 |
|---|---|
| `external_validation_targets.csv` | `0d9c361627e898a39533bca0277f01969a9fc8cd34046000d26b99b21d77576f` |
| `file_inventory.csv` | `817124dbbce70b1181f580ea8517350e1a059770486448ad80c8d0eb8e2efab7` |
| `harmonized_schema.csv` | `72272c5537fdfa5b926a6aded69920bb5357a7bb5daef09742dfb494dadfa1ab` |
| `live_births_by_year.csv` | `c32e673451e4374887fd12f4ddec69df209297de4b7c18429eb17f1ecfd56e56` |
| `record_layout_1992.csv` | `45ca1273762db92f992b9255390846a43bc0e90f11b3fa32ebbe6f46f07a5a79` |
| `record_layout_2006.csv` | `7314a1c24830d613af6a7b482b899e659c5a9763e8aa80db64e58e53cbae6866` |
| `record_layout_2014.csv` | `4bda06cedefa84c8ff73f07347e6b5b5960803908ab4f3ee3b4c0e8cd5a011df` |
| `record_layout_2022.csv` | `db60b25192efa7a6818e1a168722cb00978523046e2753be184227d26474747a` |
| `reporting_thresholds.csv` | `902553415882c12cf9878ee243e3da3fc7dd4cba9479a8232aa07708cda445f3` |
| `validation_results.csv` | `8041586dc99f450faf4a3b91505a98652410a31d6caa5da14dfa39c75da7de0e` |
| `validation_tracking.csv` | `d0c8b2860bc2fdb5adaff069590348b3b526a466e90eddd900674a731422083a` |
| `variable_crosswalk_working.csv` | `e72190aac63375bd465613ade4b2b14a2af9ca71fb3f5fab8ddb42e9f767043c` |
