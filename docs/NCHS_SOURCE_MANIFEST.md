# NCHS source-data SHA manifest

> **Scope.** SHA-256 checksums for every raw NCHS public-use zip that this monorepo's harmonization pipelines consume. 100 zips total: 43 fetal-death + 35 natality + 19 linked-cohort + 3 matched-multiples.
>
> **Purpose.** A downstream user re-running the pipeline from a fresh NCHS download can verify that their inputs are byte-identical to what produced the shipped harmonized parquets. If a zip's SHA differs from this manifest, the user's download is either truncated, corrupted, or NCHS has silently re-released the file with the same name. Either case is a signal to halt and re-resolve before proceeding.
>
> **Cross-product consistency.** Each row keys on `year × raw_filename`, matching the corresponding row in each subproject's `file_inventory.csv`:
> - Fetal-death rows match [`fetal_death/file_inventory.csv`](../fetal_death/file_inventory.csv) (43 rows, year 1982-2024).
> - Natality + linked rows match [`natality/metadata/file_inventory.csv`](../natality/metadata/file_inventory.csv) (54 rows: 35 natality 1990-2024 + 19 linked-cohort with `2005_linked` through `2023_linked` keys).
>
> **Generation.** SHAs computed via `shasum -a 256` on the canonical NCHS public-use zips as downloaded from `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/` paths recorded in each inventory's `source_url` column. Generated 2026-05-13 at the C8.11 DO step under the Phase C Tier-2 plan; carries forward unchanged until a new latest-year refresh + a corresponding `[plan-update]` commit names the next manifest revision.
>
> **Verification.** From a fresh download checkout:
>
> ```bash
> shasum -a 256 \
>   /path/to/fetal_death/raw_data/*.zip \
>   /path/to/natality/raw_data/*.zip \
>   /path/to/natality/raw_data/linked/*.zip \
>   | sort
> ```
>
> Then compare line-by-line to the tables below (also sorted by raw_filename within each section).

---

## Section 1 — Fetal-death raw zips (43; year 1982-2024)

Coverage envelope: V3b (1982-1988, 1978-revision uniform) + V3a (1989-1991, 1989-revision uniform) + V2 (1992-2002, 1989-revision uniform) + V2.1 (2003-2004, mixed 1989/2003-revision transition) + V1 (2005-2017, mixed A/S revision) + V1 OE-based (2014-2017 COD variants) + V1 COD-only (2018-2024).

| Year | raw_filename | SHA-256 |
|---|---|---|
| 1982 | `Fetal1982US.zip` | `56ddf02376cb17116ea4ac58b65908cb68aaca6b1efcef3a0ea062c1dc74bc2b` |
| 1983 | `Fetal1983US.zip` | `c44b65d1aac15d76032b91a591831635dfdba234bf7619506586ebe1d5a67d5a` |
| 1984 | `Fetal1984US.zip` | `e74c45516a90adcd26c1723b9f593f5c34088c0e2dcc699f00d0e00fb8a6fec8` |
| 1985 | `Fetal1985US.zip` | `cb57279c3bc430ca40154fdf17a489308b542f5cd35522eaf8060513c0ea25e2` |
| 1986 | `Fetal1986US.zip` | `864d93dd255c33f5f876585ff0c19b8f3ceb504eaa7522f92978d3a1647d0e92` |
| 1987 | `Fetal1987US.zip` | `5bbd2b356ce6ab720873d7b2cf7cd1bbbfdf57d0da43e42d8cb4376e0789cb6a` |
| 1988 | `Fetal1988US.zip` | `e6c733dbda5cd5a5d389cb1400c9b1b5d16082fcf42dbfc137b741a2453b20fd` |
| 1989 | `Fetal1989US.zip` | `1d30d285a6558da697716879b05f3984c4f2bea15246b6deac7271ee9cb372bd` |
| 1990 | `Fetal1990US.zip` | `bcca5deb5de534d3d42e61abc4274bb39d68efd9f635548fcc0f4d546679987f` |
| 1991 | `Fetal1991US.zip` | `aaa3e23250aac121c04c1068a645ff3a13deee94107917c2c30001936e701dd4` |
| 1992 | `Fetal1992US.zip` | `9fabf21c6bcf12fdd968459e8a721454921b5ce44d03a34a34af574b43b7c112` |
| 1993 | `Fetal1993US.zip` | `8c0b5f8e4a8a2a688369f207ed641f78b220fbf78b814d3658765bc2723ff93a` |
| 1994 | `Fetal1994US.zip` | `9313b232bcb8f24098013311463f89497a315f062bc710a66b4cfcfbb78d6e4e` |
| 1995 | `Fetal1995US.zip` | `fca01c022410ae244c2dede445a062afe270d9fa1b99ed242bce90e4abfe1429` |
| 1996 | `Fetal1996US.zip` | `5e4fd1f1600797d103544e07f6830dae1e80e79ae9f61f4f1824564ca02d79e5` |
| 1997 | `Fetal1997US.zip` | `87dc7b2946280f37ad312bb845860d20924536138f3f705be07ca559aa88f93d` |
| 1998 | `Fetal1998US.zip` | `534f0ca541dc87f61d2829666cd8a02bb4e3f7ab620cb1c26a552b742e53e2b3` |
| 1999 | `Fetal1999US.zip` | `8cfa7f9d37e0ba1883f1631843f7d56c36281ef982e82f1c28256f2de6109029` |
| 2000 | `Fetal2000US.zip` | `d04caad64f13fbebf09d8eb27f872a575ac1bf939423337246bc827a190bb1d9` |
| 2001 | `Fetal2001US.zip` | `63aafe00ff6df26821417c8a3ec8616a2a5d4099f8885f093005944e561896e5` |
| 2002 | `Fetal2002US.zip` | `754ace45032aba35a02bb481359b183013306a4d51a8c7e31f52b6efad22eb92` |
| 2003 | `Fetal2003US.zip` | `7311ffab3314bf8f7ebb1465b153cc569be88d3126edabab680b90c7a4844f99` |
| 2004 | `Fetal2004US.zip` | `42d68172ea1976cc5c371ecce36f5b33bb0efb6b6f139443bbec729674395c41` |
| 2005 | `Fetal2005US.zip` | `b505986d6578ed0f5542a90741d783936bedf6133a0da98bb906ba30ebabff9b` |
| 2006 | `Fetal2006US.zip` | `6072f3924a223285b43e4f25c204f2d056eb55ae8a4b876d50b0c248c8587838` |
| 2007 | `Fetal2007US.zip` | `884c3f646e7c70dcf5539b1e3d2f42d6195fa78fd0d654ac0db993d0cfee5a05` |
| 2008 | `Fetal2008US.zip` | `2911d940f04542a55ffef5dbd9298fd8f6320790a81ad50f63993f0e684a9c74` |
| 2009 | `Fetal2009US.zip` | `2e9b253b72125539ac9a54565a1acb41eb2dbe7da2cecba76662cfeb2ccd1379` |
| 2010 | `Fetal2010US.zip` | `50e9bdb3218a3880dbc60b132683fd8bcefbb34c7bb1f7dfd878b8f2567cd2eb` |
| 2011 | `Fetal2011US.zip` | `34c4d343e4e6843adafd3bcd328ab990c39a06f16c811b1c552c72361d0ef0c7` |
| 2012 | `Fetal2012US.zip` | `c0e3b01af3eebab34dd12fcaa08c454b9724c014d922cbb675f39f653ccce48a` |
| 2013 | `Fetal2013US.zip` | `425d2dd965026ff0ca95aa8c95126ffee529413a41de3ace492564cdd4dc6f07` |
| 2014 | `Fetal2014US_COD.zip` | `b5b0e2313bde48b869ed9fc50f21ab27444e71822e8564593ca0c589ce364d33` |
| 2015 | `Fetal2015US_COD.zip` | `be992d8d336debef2febfe9c68277f264fb7832ddd8371ac4080d030e3d46cf5` |
| 2016 | `Fetal2016US_COD.zip` | `01ebec5ecb3e8617309992aa8ff1b5018df7b4dcad10f415c79297bf9a1ab094` |
| 2017 | `Fetal2017US_COD.zip` | `bdfd36862bd1de6cf085e2f2bc898a00133924f9e62afa9cda163e96d09701dd` |
| 2018 | `Fetal2018US_COD.zip` | `11b56092229932ce5ad0503f8803ce09d627e66855474bd757b7bb258daf6538` |
| 2019 | `Fetal2019US_COD.zip` | `c1ec8b7702deca5d73c6657f34dcddde1be2a03da2c1b2c776916dc136582da7` |
| 2020 | `Fetal2020US_COD.zip` | `1e289b816ff401c21cd4bb2ff0dd48f4b6261edf4920cbb3b1eb13355593fef0` |
| 2021 | `Fetal2021US_COD.zip` | `e12feaf0c8aff693a6c874ff62838936ea7ee8cc161bbdb07b744304ddac8c77` |
| 2022 | `Fetal2022US_COD.zip` | `b95db4fa2240175fd054dcc870c365dd42044191814d96c11f243b3da128c4d2` |
| 2023 | `Fetal2023US_COD.zip` | `54c89017ad1365a939a4889ea93d9c91583a5007384709df8379cc89f7bdcdd4` |
| 2024 | `Fetal2024US_COD.zip` | `180d19915869dcbd7c3106e82a8e08d4cb6a092d7d4861bda2866bf471424fc8` |

**Boundary notes.** Filename changes from `Fetal<YYYY>US.zip` (1982-2013) to `Fetal<YYYY>US_COD.zip` (2014+) at the 2014 COD-variant introduction; record length changes at the V3b → V3a (200 → 360 bytes), V2 → V2.1 (360 → 1350/1500 bytes), V2.1 → V1 (1500 → 3351 bytes), and V1 → V1-OE (3351 → 3050 bytes) era boundaries — see [`fetal_death/file_inventory.csv`](../fetal_death/file_inventory.csv) `record_length` column for per-year values.

---

## Section 2 — Natality raw zips (35; year 1990-2024)

Coverage envelope: 35 years contiguous. Filename convention: `Nat<YYYY>.zip` (1990-1993) → `Nat<YYYY>us.zip` (1994+). All produce one parquet per year via `natality/scripts/01_import/`.

| Year | raw_filename | SHA-256 |
|---|---|---|
| 1990 | `Nat1990.zip` | `c27320794b267d0745d16a427a2928a709890811556bffe0ba06c37e0004d59b` |
| 1991 | `Nat1991.zip` | `c4081fbc546489aff8a31418a627b0caaf50d94ff4c61302ee806a4b7a53bd68` |
| 1992 | `Nat1992.zip` | `75fe64963335998113dbe48d75312812b4c1fcac81905dc32af4545a30ac550c` |
| 1993 | `Nat1993.zip` | `01ae9492260cba7f1cad57db1315b23eb73028e56961fb071099aa7797c1c5f3` |
| 1994 | `Nat1994us.zip` | `b211aaf88a3f4c5c17859f0ae3c39dd64603abf5c34384522e7cfedc8e4fb475` |
| 1995 | `Nat1995us.zip` | `2c59cbbaeeff2d9448c4644f06870bca02a23f02811467e4c2a1ad3317606075` |
| 1996 | `Nat1996us.zip` | `4ce8c4095022c6c4c7424afdd840f4bcbc52bb7473e523427ce24229f1f7beb3` |
| 1997 | `Nat1997us.zip` | `00431699e8ce46a226b7d49ff8ce4260e6400a7af9b79cc1998b3e838ec7b9c0` |
| 1998 | `Nat1998us.zip` | `4e6b831c3739d3d31c4e2b475e3b90c44c156a6c70f4eee4d4b64fad9b0f1e9c` |
| 1999 | `Nat1999us.zip` | `3467f1709bea69dde194f9419e9542e65423c96e863faf86e90a542c94dfbec4` |
| 2000 | `Nat2000us.zip` | `b7d359a1927f84b229879c054e28353b1ae188e5f287d5b0fa41bbc198925e2b` |
| 2001 | `Nat2001us.zip` | `af582bcf89cc00891f5cfc2ccd9668a48de855499408552cc8bbc85dc513a49d` |
| 2002 | `Nat2002us.zip` | `4dcaf60a86e1b1281bc52c91d5d5aeba785d9c6c5d1d59d892a8a6384847bfe7` |
| 2003 | `Nat2003us.zip` | `13f592e7fa3d3691d34814a2483de23f1dd8f669c7a513f300916d5090110abc` |
| 2004 | `Nat2004us.zip` | `c92cc74866884c8b108bc7e2bb7025b19d9a63e6be0d27540c45a99cf2144105` |
| 2005 | `Nat2005us.zip` | `071a08505f8571bbd8949ca32863b4d455ab6cc7add742033fe3a29f5e389cc8` |
| 2006 | `Nat2006us.zip` | `269704e673d57d7c87801953499ae2ebbf8d6efd4cd551fc201a60a3f241cd1b` |
| 2007 | `Nat2007us.zip` | `150bf64964f281bb9cc3a251cfc3d8da82de3d12efa7ad79f06526a29fadc0e7` |
| 2008 | `Nat2008us.zip` | `3422acc844bfb05648abbe1385756928b68582bd1a63d1a10e6d743966c23748` |
| 2009 | `Nat2009us.zip` | `b3c4e08c97a1e3c469524d46b27573ad9b21d0e76845accf1049aacedad8f30e` |
| 2010 | `Nat2010us.zip` | `4554673b65b259df8f639ad960e077b3b83d13973b84aa8b2415d8bd76f677da` |
| 2011 | `Nat2011us.zip` | `9d9f38999a8a4d3bb5ff6174439e6379e0ccf005e81c8826365062bd5fd2c2f2` |
| 2012 | `Nat2012us.zip` | `d96cd2d523055020ee038618566cfd86de5fb8866cbd534969abb189a4c969a6` |
| 2013 | `Nat2013us.zip` | `1479de693e61b1aadd04458a2961046f263dd81a2a0ad5acf72802091a366bdb` |
| 2014 | `Nat2014us.zip` | `38d009deb578ec93f95b29c2c6cac668c89bbc51d5c7e0a6e2e268876163e55d` |
| 2015 | `Nat2015us.zip` | `b2de4b43a836f2ffafdf6a49c08204d0da836f8887d92a9e0fd88fc24ba4ec00` |
| 2016 | `Nat2016us.zip` | `fc7103274263e97d0103bd125562ac98fadae6d17f5992123290f41b27eff01e` |
| 2017 | `Nat2017us.zip` | `24a19e1137cd44468e198300c729b7c40f4b88f8da0c08502934e463a0b9444d` |
| 2018 | `Nat2018us.zip` | `d1cba3693416697f16f55c0a032e50ce0f7a256afd80690afded06ebd295a1c6` |
| 2019 | `Nat2019us.zip` | `453080600d044766d4549d7ade90b06ae03d6f415844288dbbfd66f7765312b1` |
| 2020 | `Nat2020us.zip` | `0a4d0b50c89a65e83dd94086480ad32150da31be3a67fe528eb9fbb426b92a97` |
| 2021 | `Nat2021us.zip` | `3dea777017a63afce07f9da1b022142b94067b752ebd2d16af4da07291b2ae19` |
| 2022 | `Nat2022us.zip` | `d0b5c283e695e928c51f94aa55b02ed70c6a319bfb09eb95a994728d48416adc` |
| 2023 | `Nat2023us.zip` | `4474daab3475af096397e26ed5fdb541b1df59ee9b555fc0b31db84c44d83663` |
| 2024 | `Nat2024us.zip` | `8ce1c61bc055b3327311985f918db5387ea6a1ed7d34b367afe30f468b92225a` |

**Filename casing note.** The on-disk filenames for the 2021 + 2022 natality zips are lowercase (`nat2021us.zip` + `nat2022us.zip`) on the original NCHS download; on the case-insensitive macOS filesystem they resolve to the same inode as the inventory-recorded capital-N convention (`Nat2021us.zip` + `Nat2022us.zip`). The inventory's capital-N casing is the canonical reference; any downstream user on a case-sensitive filesystem may need to rename the on-disk files to match.

---

## Section 3 — Linked-cohort raw zips (19; cohort years 2004-2023)

Naming convention changes at cohort 2015 / publication 2016:
- 2005-2015 publication: `LinkCO<YY>US.zip` (cohort year embedded as 2-digit suffix; corresponds to the **publication year**, which is cohort_year + 1).
- 2017 publication onward: `<YYYY-pub>PE<YYYY-cohort>CO.zip` (4-digit publication year + 4-digit cohort year explicit).

Each zip contains one publication-year + cohort-year pair. Inventory keys these as `<cohort_year>_linked` to match the cohort year that the parquet pipeline harmonizes against (cohort = year-of-birth of the cohort being followed for infant deaths).

| Cohort year | Inventory key | raw_filename | SHA-256 |
|---|---|---|---|
| 2005 | `2005_linked` | `LinkCO05US.zip` | `d805b77d6971dc7c2e1bcfdf982e368440a0c8747d9a3975e223c74815596257` |
| 2006 | `2006_linked` | `LinkCO06US.zip` | `226f02a8c397619c63a52b2e223ee38cec01bb4146efd13ed28c281487eb681d` |
| 2007 | `2007_linked` | `LinkCO07US.zip` | `d4e44da8274a09afaa232ac809dd5078cfe3a6b5e06ef697ebb9a506b5a32a92` |
| 2008 | `2008_linked` | `LinkCO08US.zip` | `986b151c7f9bb040dec017910b651a6b30ad78b4ab1ce85de21b0fe470361f57` |
| 2009 | `2009_linked` | `LinkCO09US.zip` | `72ba72964e03e09ce8ee5b648c24f61c1183b01c89f1533b1c31a88a7ad0b4c4` |
| 2010 | `2010_linked` | `LinkCO10US.zip` | `f6017ca015ed456c76bad661559caeb425101ab3a87cd78488c3af8e0d55731e` |
| 2011 | `2011_linked` | `LinkCO11US.zip` | `d9eb1be4f730d184762b9d3ed6958db5d5cb6114c2762fde9defc0b325b7570b` |
| 2012 | `2012_linked` | `LinkCO12US.zip` | `55e6516d6f4a04691c38723bb00d64d27eca1fc85083993e25f34ebc1d0d41ea` |
| 2013 | `2013_linked` | `LinkCO13US.zip` | `9fdbc68607c5ecf33e444a935bd285a1c48bcb52238f19174195bbd109312c48` |
| 2014 | `2014_linked` | `LinkCO14US.zip` | `090c8ed7147b286146ab103ee014508e4483c5b59763d98c71f66379b3a39125` |
| 2015 | `2015_linked` | `LinkCO15US.zip` | `b5e520bcce3c4b27d3e2b1beaaa736d5fc0ad682697632930746b8a95682ff78` |
| 2016 | `2016_linked` | `2017PE2016CO.zip` | `10a094e3f3431ca34256fdfb036a7d37884fdff27453866b313f7760a8822ec0` |
| 2017 | `2017_linked` | `2018PE2017CO.zip` | `60963545ea498b47c69a1cbf8810ccaa661dbec5d81edf133a2d052816422510` |
| 2018 | `2018_linked` | `2019PE2018CO.zip` | `25901e1fa512dd57edb0e2a56af62069522ebd66bbec13ee3bb2ac00e5ee945d` |
| 2019 | `2019_linked` | `2020PE2019CO.zip` | `6666ae775e793a33259e6e4ee19e8fa93928e21b9d6ff609c1ca40fb6f82ca6b` |
| 2020 | `2020_linked` | `2021PE2020CO.zip` | `6ea469e22c7e841c32db8c92309ef108f1f5696981b7df16524f3a3704caa685` |
| 2021 | `2021_linked` | `2022PE2021CO.zip` | `d83d1c79734ec8ff4ea21db9dc382a22fea244b2423ff81061242a5ba9e80503` |
| 2022 | `2022_linked` | `2023PE2022CO.zip` | `1c2ad811a4b8c4aecded084162cfcba0ecf6d8c7dd06909aaacddd30967e3fe6` |
| 2023 | `2023_linked` | `2024PE2023CO.zip` | `24742c158e15134383514a0516dbaa0e6f94ba49ec253fe552719ceaa5f735c8` |

**Linked-file coverage caveat.** This monorepo's harmonization pipeline covers cohort years 2005-2023 (19 years contiguous). The NCHS canonical linked-file series goes back to 1983 cohort year, but pre-2005 files are NOT processed by this resource (the natality harmonization v2.x scope decision deferred them; see [`natality/docs/COMPARABILITY.md`](../natality/docs/COMPARABILITY.md) § V3 Linked birth-infant death comparability). Pre-2005 linked files exist in the NCHS public-use archive but are not included in this manifest.

**2025 cohort release.** The 2025-published cohort-2024 file (`2025PE2024CO.zip`) has not yet been released by NCHS at the time of this manifest's generation (2026-05-13). Once released, a subsequent latest-year refresh task (per the C8.2 / C8.10b carry-forward soft-flag) will append the row and refresh this manifest under a new `[plan-update]` revision.

---

## Section 4 — Matched-multiples raw zips (3; publication windows 1995-1997, 1995-2000, 2016-2020)

NCHS publishes three matched-multiples linkage files at `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/matched-multiples/`. Each file is keyed by **publication window** (not individual cohort year); a single zip ships multiple years of matched twin / triplet / quadruplet records with linked infant deaths. Empirical record counts: 324,490 / 699,144 / 641,934 (total ~1.67 M raw records, 1,665,568 in the harmonized parquet). Companion documentation PDFs ship at the sibling `Dataset_Documentation/DVS/matched-multiples/` path.

| Window | Inventory key | raw_filename | SHA-256 |
|---|---|---|---|
| 1995-1997 | `1995-1997` | `1995-1997.zip` | `5675d57d198d1870c600500edb72c95a1f9e7cb426c451192f1641ab791a50a7` |
| 1995-2000 | `1995-2000` | `1995-2000.zip` | `8315dd24c9be2f034fd494b55362b4a022e7a69668432461cdacd35c85de28e3` |
| 2016-2020 | `2016-2020` | `2016-2020.zip` | `4e45d5315b24d2c6d7c98a15e8bd9279c057a50b2c4ef651659ad19b19e28d8b` |

Companion PDFs (also SHA-anchored in `matched_multiples/file_inventory.csv`):

| Window | doc_filename | SHA-256 |
|---|---|---|
| 1995-1997 | `1995-1997.pdf` | `f982ad93fbd435484173d6a08014e503e7f45208994cf1305b20ad0cae675d66` |
| 1995-2000 | `1995-2000.pdf` | `07b7260d4284402f9068f9dc160612b0fb0240fdd0536c6c1ad1d0ffd478b886` |
| 2016-2020 | `2016-2020.pdf` | `ed5e96ab662e970dc8fab3295942b3dfffac8c845120b8e92e125cf7d39152be` |

**Distinct methodology generations.** The three windows are NOT strict supersession — each represents a separate NCHS publication with its own authoring team, inclusion criteria, and record layout (502 / 754 / 157-byte content; ICD-9-only / mixed-ICD-9-10 / ICD-10-only). See `matched_multiples/ABOUT_SOURCE_DATA.md` for methodology-difference tables. Cross-window analyses use `within_era` comparability for race/education and `full` for set-level identifiers.

**Window-level vs year-level inventory.** Unlike fetal-death / natality / linked which key by single year, matched-multiples keys by multi-year publication window because each zip is a single NCHS publication artifact. Cross-product joins from matched-multiples records to natality / fetal-death by `data_year` are not directly supported (matched-multiples ships no native `data_year` field for the 1995-X windows; window-implicit only).

---

## Cross-product invariants

The manifest's three sections combine to span the full 1982-2024 fetal-death + 1990-2024 natality + 2005-2023 linked-cohort coverage that this monorepo harmonizes. Cross-product analyses joining numerator + denominator across products (per [`docs/JOINT_USE_GUIDE.md`](JOINT_USE_GUIDE.md)) typically require each input zip's byte-identity to reproduce a published validation cell — this manifest is the verification anchor for that reproducibility.

- **100 zip × 64-char SHA-256 entries** = 100 × 64 = 6,400 hex characters of integrity information at byte-exact fidelity.
- **Inventory cross-reference**: every row of this manifest has a matching row in `fetal_death/file_inventory.csv` (43 rows; matches Section 1), `natality/metadata/file_inventory.csv` (54 rows; 35 match Section 2 + 19 match Section 3), or `matched_multiples/file_inventory.csv` (3 rows; matches Section 4).
- **Coverage envelope**: fetal-death covers 43 contiguous years 1982-2024; natality 35 contiguous years 1990-2024; linked-cohort 19 contiguous cohort years 2005-2023; matched-multiples 3 publication windows 1995-1997 / 1995-2000 / 2016-2020. Cross-product joint coverage = 19 cohort years 2005-2023 (natality + linked) intersected with 33 years 1992-2024 (natality + fetal-death; fetal-death pre-1990 is fetal-death-only). Matched-multiples is an ancillary product spanning natality + fetal-death + linked-cohort within its 3 windows.
- **No row collisions**: each `(year, raw_filename)` pair is unique across all four sections. Linked rows use the `<cohort_year>_linked` inventory key to disambiguate from same-year natality rows; matched-multiples rows use a publication-window key (1995-1997 / 1995-2000 / 2016-2020) to disambiguate from individual-year rows.

## Update procedure

When a new NCHS public-use file lands (e.g., 2025-published cohort-2024 linked file):

1. Append a row to the relevant `file_inventory.csv` (`year`, `raw_filename`, `source_url`, etc.).
2. Compute SHA-256 on the downloaded zip: `shasum -a 256 <path>/<filename.zip>`.
3. Append a row to the relevant section of this manifest, in year order.
4. Update the section's row count + the cross-product envelope description.
5. Commit as a `[plan-update]` since this is canonical-state mutation; include a DECISION_LOG entry naming the release date + NCHS canonical URL.
6. The downstream consumer running `shasum -a 256 -c <manifest>` (after extracting the table into a shasum-compatible format) verifies their fresh download is byte-identical to the manifest record.

---

*Manifest generated 2026-05-13 at the C8.11 DO step of the Phase C Tier-2 plan; cross-references `fetal_death/file_inventory.csv` v2.4.0 + `natality/metadata/file_inventory.csv` v2.8.0. Per Anti-Pattern #1 (append-only state files), any future update revises a NEW manifest revision rather than overwriting this one.*
