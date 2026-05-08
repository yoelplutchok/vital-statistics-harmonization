# Import: U.S. public-use natality zips

## What works today

- **`parse_public_us_year.py`** reads **`Nat{year}us.zip`** and writes a **Parquet** slice with **raw** fixed-width substrings (no harmonization yet).
- **Configured years:** **2005-2015**.
  - 2005: 1500-byte records (`PUBLIC_US_2005_2010_FIELDS`)
  - 2006-2013: 775-byte records (`PUBLIC_US_2005_2010_FIELDS`)
  - 2014-2015: 1345-byte records (`PUBLIC_US_2014_2015_FIELDS`)
- **Compression handling:** stdlib `zipfile` for stored/deflate archives; automatic `7z x -so` fallback for unsupported methods (deflate64 / PPMd). **2009–2013** (deflate64) and **2015** (PPMd) require `7z` on PATH.

## Run

From this directory:

```bash
pip install -r ../../requirements.txt   # once
python parse_public_us_year.py --zip ../../raw_data/Nat2014us.zip --year 2014 \
  --max-rows 50000 --out ../../output/yearly_clean/natality_2014_core_sample.parquet
```

Omit `--max-rows` to stream the **entire** file. By default the script uses **chunked Parquet writes** (`--chunk-rows` default 250,000) so memory stays bounded.

### Parse all V1 years at once

```bash
python parse_all_v1_years.py
```

Writes `output/yearly_clean/natality_{2005..2015}_core.parquet` under the repo root.

## Outputs

Parquet columns: `year` plus one string column per NCHS field in the selected spec set in `field_specs.py`. Values are **exactly** as in the ASCII file (padding, blanks, codes).
