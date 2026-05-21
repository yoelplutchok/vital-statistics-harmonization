# RECEIPT — D.2 unified Zenodo deposit prep (agent portion)

**Task:** Phase D.2 — prepare the metadata + upload bundle + post-publish edit plan for a **new unified HVS concept DOI** covering all four in-repo products. **Agent prepares; human uploads at zenodo.org.**
**UTC:** 2026-05-21T13:30:00Z
**Authorization:** user 2026-05-21 ("authorize D.2 prep"). The actual Zenodo publish (externally irreversible) is NOT authorized by this — it remains a separate, explicit human step.
**Canonical-state mutation:** none. No parquet/schema/validation-target/test/script touched. New files only: `.zenodo.json`, this receipt. (`.gitignore` + the uncommitted-tree commits were the preceding cleanup, not part of D.2.)

---

## 1. What was prepared

1. **`.zenodo.json`** (repo root) — Zenodo deposit metadata: `upload_type=dataset`, `access_right=open`, `license=cc-by-4.0`, `version=1.0.0`, creators (Plutchok, Yoel), 14 keywords, full HTML description (four-product envelope + validation + reproducibility + CC-BY/MIT/§105 licensing + geography note), and three `related_identifiers` (`continues` the two prior concept DOIs; `isSupplementedBy` the GitHub repo). Validated as well-formed JSON.
2. **This runbook** (bundle manifest + pre-upload gate re-hash + upload steps + post-publish edits).

---

## 2. Deposit bundle manifest

**Build-host parquet locations** (NOT in a typical git clone — gitignored):
- Fetal death: `~/Desktop/fetal-death-harmonization-build/output/harmonized/`
- Natality + linked: `~/Desktop/natality-harmonization/output/harmonized/`
- Matched multiples: `matched_multiples/output/harmonized/` (present in this clone)

### Primary harmonized/derived parquets (recommended core deposit; ~8.27 GB)

| # | File | Product | Rows × cols | Size | Documented SHA-256 | Gate? |
|---|---|---|---|---|---|---|
| 1 | `fetal_death_harmonized.parquet` | Fetal death v2.4.0 | 2,427,233 × 73 | 27.3 MB | `38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` | ✓ |
| 2 | `fetal_death_derived.parquet` | Fetal death v2.4.0 | 2,427,233 × 89 | 34.1 MB | `185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` | ✓ (preferred entry) |
| 3 | `natality_v2_harmonized.parquet` | Natality v3.0.0 | 201,161,456 × 71 | 2.0 GB | `c8a740eb48d4f3de66759da27eef94143c315846885bf905a88cbc0fa6237153` | |
| 4 | `natality_v2_harmonized_derived.parquet` | Natality v3.0.0 | 201,161,456 × 84 | 2.7 GB | `acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974` | ✓ (preferred entry) |
| 5 | `natality_v3_linked_harmonized.parquet` | Linked v4.0.0 | 149,386,620 × 81 | 1.5 GB | `ea89ab3c009de00cddb88aad84aa50fde376a47f96b6865113a600fb5a0907c7` | |
| 6 | `natality_v3_linked_harmonized_derived.parquet` | Linked v4.0.0 | 149,386,620 × 97 | 2.0 GB | `f630d8cf20db72eaf5e482e856e621ff73a6ad1c932de0fc832b237546b09073` | ✓ (preferred entry) |
| 7 | `matched_multiples_harmonized.parquet` | Matched multiples | 1,665,568 × 24 | 12.4 MB | `adbec1087370941fd373b933566b7dfd24dbbc2f957d998f92ac14ef45dc1549` | (verified locally this session ✓) |

Plus, in the same record:
- `SHA256SUMS.txt` — generated on the build host at upload time (step 3 below).
- `README.md`, `LICENSE`, `CITATION.cff` — copied from repo root for a self-describing deposit.

### Optional second-tier: per-year raw parquets (large; reproducible from NCHS source)
- `fetal_death_yearly_raw_1982-2024.zip` (43 files)
- natality per-year raw 1968–2024 (57 files) — **largest component; size TBD on build host**
- linked per-year raw 1983–2023 (38 files; 1992–1994 gap)
- matched-multiples 3 per-window raw parquets (`5c22308b…`, `7c682668…`, `d98b4296…`)

**Recommendation:** deposit the 7 primary parquets + manifest + README/LICENSE/CITATION as the core scientific artifact; raw per-year bundles are optional (fully reproducible from the GitHub pipelines + public NCHS zips). **Decision needed from human** — see §6.

**Excluded from the deposit:** regression-baseline parquets (`*_baseline.parquet`) — PROVENANCE marks them "not gate artifacts; do not use for production."

---

## 3. MANDATORY pre-upload gate re-hash (build host) — §9-#15 / §7-#18

Zenodo is immutable once published. A prior PASS proves correctness *at that time*; this step proves **these are the bytes you publish**. Run on the build host immediately before zipping/uploading:

```bash
cd ~/Desktop   # adjust if your build trees live elsewhere
shasum -a 256 \
  fetal-death-harmonization-build/output/harmonized/fetal_death_harmonized.parquet \
  fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet \
  natality-harmonization/output/harmonized/natality_v2_harmonized.parquet \
  natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet \
  natality-harmonization/output/harmonized/natality_v3_linked_harmonized.parquet \
  natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet \
  <monorepo>/matched_multiples/output/harmonized/matched_multiples_harmonized.parquet \
  | tee SHA256SUMS.txt
```

**Confirm the 4 gate SHAs match exactly:** `38e2cecb…` (fetal harmonized), `185c071e…` (fetal derived), `acb5c48a…` (natality derived), `f630d8cf…` (linked derived). **Any mismatch → HALT (§7-#18 reproducibility regression); do NOT upload, do NOT edit docs to match — investigate the build.** Include the resulting `SHA256SUMS.txt` in the deposit.

> This clone could only verify file #7 (`matched_multiples`, `adbec108…` ✓); the other 6 parquets are gitignored and absent here.

---

## 4. Human upload runbook (zenodo.org)

1. Log in at zenodo.org → **New upload**.
2. Drag in the 7 primary parquets + `SHA256SUMS.txt` + `README.md` + `LICENSE` + `CITATION.cff` (and optional raw bundles if chosen). Large parquets may need the chunked uploader / good bandwidth.
3. Zenodo will read `.zenodo.json` if you deposit via the GitHub integration; for a manual web upload, set the form fields to match `.zenodo.json`: Upload type **Dataset**; Title (from `.zenodo.json`); Authors **Plutchok, Yoel**; License **Creative Commons Attribution 4.0 International**; Version **1.0.0**; Keywords (paste the 14); Related/alternate identifiers (the 3 from `.zenodo.json`); paste the Description.
4. **Reserve the DOI** before publishing if you want it for the README/CITATION first; otherwise publish, then capture both the **concept DOI** (version-agnostic) and the **version DOI**.
5. Publish.
6. Record the concept + version DOIs and bring them back here for §5.

---

## 5. Post-publish edits (ready to apply once the DOI exists)

Apply these after the human returns the **concept DOI** (call it `<CONCEPT_DOI>`, e.g. `10.5281/zenodo.XXXXXXXX`).

### 5a. `CITATION.cff`
- Add a top-level preferred-citation DOI and update the message:
  - `message:` → `"If you use the U.S. Harmonized Vital Statistics resource, please cite the unified Zenodo deposit (concept DOI <CONCEPT_DOI>)."`
  - Add top-level: `doi: <CONCEPT_DOI>`
  - Keep the two existing `references` entries (the prior single-product deposits) — they are now historical predecessors.

### 5b. `README.md` (current block ~lines 103–106 under "## Citation")
Replace:
> *Until the unified Zenodo deposit is published, cite the two existing deposits:* … (the two bullets)

with:
> Cite the unified HVS deposit (concept DOI, resolves to the latest version):
> - Plutchok Y. *U.S. Harmonized Vital Statistics (HVS) Microdata: Natality, Linked Birth–Infant Death, Fetal Death, and Matched Multiples.* Zenodo. https://doi.org/<CONCEPT_DOI>
>
> Superseded single-product deposits (immutable): natality + linked 10.5281/zenodo.19363074; fetal death 1992–2022 10.5281/zenodo.20031571.

### 5c. (D.3) Inject the GitHub URL/DOI into the public-repo README at the D.3 sync.

Each 5a/5b edit should be its own small commit with an inline note; re-run nothing (doc-only).

---

## 6. Open questions / decisions for human

1. **Deposit version string** — `.zenodo.json` uses `1.0.0` (first *unified* HVS data deposit). The stale public GitHub snapshot is labeled "v1.0" (2026-05-12); if you'd rather not collide, use `1.1.0`. Confirm before publishing.
2. **Raw per-year bundles** — include in the deposit, or keep deposit to the 7 primary parquets + manifest and rely on GitHub-pipeline reproduction for raw? (Natality raw 1968–2024 is the size driver.) Default if you don't say: primary parquets only.
3. **Related-identifier relations** — I used `continues` for the two prior DOIs and `isSupplementedBy` for the repo; swap to `isNewVersionOf`/`obsoletes` if you prefer a stronger supersession signal.
4. **Creator metadata** — no ORCID/affiliation included (none on file; I did not invent one). Add yours in the Zenodo form if desired.

---

## 7. Status of D.2 + halts

- **D.2 is NOT complete.** Agent prep done; deposit publish (irreversible) + the §5 DOI injection remain. D.2 stays OPEN, human-gated.
- **4 gate parquets absent in this clone** → §3 re-hash must run on the build host before upload (only `matched_multiples` was verifiable here, and it matched).
- Phase D steps remain per-step explicitly human-authorized (KICKOFF Phase D).

## 8. §10 self-check — what could be wrong that VERIFY wouldn't catch?

- **Zenodo web-form field names** may differ slightly from the legacy `.zenodo.json` keys; the human should map by meaning (the JSON is authoritative for *content*, not for the exact UI labels). The GitHub-Zenodo integration consumes `.zenodo.json` directly; a manual web upload does not, hence the §4 mapping.
- **`license: cc-by-4.0`** is the Zenodo identifier I believe is correct; if the picker rejects it, select "Creative Commons Attribution 4.0 International" by name.
- **Documented SHAs/sizes** in §2 come from the per-product PROVENANCE.md (refreshed 2026-05-24 at D-prep.2), not re-verified here for the 6 build-host files — which is exactly why §3 re-hash is mandatory and gating.
- **Version `1.0.0`** is a guess at intent (see §6.1); a wrong choice is cosmetic and editable pre-publish, not a data risk.
