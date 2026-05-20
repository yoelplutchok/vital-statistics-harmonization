# NCHS source-data SHA manifest

> **Scope.** SHA-256 checksums for every raw NCHS public-use zip that this monorepo's harmonization pipelines consume. 141 zips total: 43 fetal-death + 57 natality + 38 linked-cohort + 3 matched-multiples.
>
> **Purpose.** A downstream user re-running the pipeline from a fresh NCHS download can verify that their inputs are byte-identical to what produced the shipped harmonized parquets. If a zip's SHA differs from this manifest, the user's download is either truncated, corrupted, or NCHS has silently re-released the file with the same name. Either case is a signal to halt and re-resolve before proceeding.
>
> **Cross-product consistency.** Each row keys on `year × raw_filename`, matching the corresponding row in each subproject's `file_inventory.csv`:
> - Fetal-death rows match [`fetal_death/file_inventory.csv`](../fetal_death/file_inventory.csv) (43 rows, year 1982-2024).
> - Natality + linked rows match [`natality/metadata/file_inventory.csv`](../natality/metadata/file_inventory.csv) (95 rows: 57 natality 1968-2024 + 38 linked-cohort with `1983_linked` through `2023_linked` keys; permanent 1992-1994 gap).
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

## Section 2 — Natality raw zips (57; year 1968-2024)

Coverage envelope: 57 years contiguous. Filename convention: `Nat<YYYY>.zip` (1968-1993) → `Nat<YYYY>us.zip` (1994+). All produce one parquet per year via `natality/scripts/01_import/`. Pre-1990 pipeline scaffolding lands at C8.17 DO step 5 (`parse_all_pre1990_years.py`); the 22 pre-1990 zips are SHA-anchored here at C8.17 DO step 1 but are not yet parser-consumed (each `file_inventory.csv` row has `imported=false` until DO step 5).

| Year | raw_filename | SHA-256 |
|---|---|---|
| 1968 | `Nat1968.zip` | `bd791cf53de5b55bea293ea9db5a6347fbc6facbd59ddb71de1b0957b8cbda20` |
| 1969 | `Nat1969.zip` | `1a36e591748def54c77a5a609d03b0fe658d63c8fd3277b1f7c14a2ecdf8d757` |
| 1970 | `Nat1970.zip` | `328d6fca738794820591b61c820057926c5984f04cd03dab758a9ccc0483d9d2` |
| 1971 | `Nat1971.zip` | `c3e44a73c9d323832cd1f16cf21ddd529b75f022d6bc1043ae5815ebd8ee0673` |
| 1972 | `Nat1972.zip` | `b4de8ffa0a68920d93fb9e2b0277da4dbc786f06ef54c2117f52e5ba51512403` |
| 1973 | `Nat1973.zip` | `5675bddf7a155d272e497d55914044f964d0b2ef82f2ba42e3ac4e9ea1bd1243` |
| 1974 | `Nat1974.zip` | `0543600a969aa5dbb047da2b2abf84846bf05469aa1b8570d120de9f2a52fd81` |
| 1975 | `Nat1975.zip` | `f6a6fffc9451804afc0f158076f82f08ee305de155935abf11cb53c1e63ca500` |
| 1976 | `Nat1976.zip` | `f76a04cd0b7e79a9c5091efad579015648ed13aad71e7828a0d14b38c513c084` |
| 1977 | `Nat1977.zip` | `356a4044966a3962a5127664e7d354b7f9b0e88a7e1f4a23358a7b907aefc29b` |
| 1978 | `Nat1978.zip` | `9d9a9e52c9e4a3d0605f15620e4a31529a8f159fdfbf32bbaa4ba7b7bd552cc0` |
| 1979 | `Nat1979.zip` | `11a71bc761e9f8185d025952e2c64ffaf4248291d55d7c53d2904abb530313b2` |
| 1980 | `Nat1980.zip` | `e7afa568e2431bf1a4e02b43d8fcc5141e7483170c533f7474a9f714459f800f` |
| 1981 | `Nat1981.zip` | `02618389ec8f84d0282dfb8e8a08091e583366610070c6258b8193e941584e4e` |
| 1982 | `Nat1982.zip` | `7721362f6fd0df946d791cb1556b4e31839518d36b3a09eda91b1e28f5b750f3` |
| 1983 | `Nat1983.zip` | `ce5762494fb4cbcbefd6ebee7cbe2a974399ea30234c6a8127b968f54871f13d` |
| 1984 | `Nat1984.zip` | `37aec54d0bc11090f5f86de4051b2da99f6558aded0675e5d1064cb0480249f0` |
| 1985 | `Nat1985.zip` | `e7e93ba09ef0096ee4a7b258b643eabee1d4d9cd4d1d8fcef189fc1ecc18ed7a` |
| 1986 | `Nat1986.zip` | `24ccdaf5efea34b1ca8109dfb301061e5ab4e5b835148c84b620ab4e4d6ddfee` |
| 1987 | `Nat1987.zip` | `461ad32f7ef10fca9882f2c7bd813d3341b3002e67befbf352a08280b00aa903` |
| 1988 | `Nat1988.zip` | `5599d3685141a55651e497d2828db92395c2e5343b02199e8901ed3cc4bda4b2` |
| 1989 | `Nat1989.zip` | `21e39c8040981148d1ea2bb7236f14ca499c1651d30032f7507de0a959630ed3` |
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

**Filename casing note.** The on-disk filenames for the 2021 + 2022 natality zips are lowercase (`nat2021us.zip` + `nat2022us.zip`) on the original NCHS download; on the case-insensitive macOS filesystem they resolve to the same inode as the inventory-recorded capital-N convention (`Nat2021us.zip` + `Nat2022us.zip`). The inventory's capital-N casing is the canonical reference; any downstream user on a case-sensitive filesystem may need to rename the on-disk files to match. The 22 pre-1990 zips were downloaded with `.ZIP` upstream extension served by the NCHS FTP and saved lowercase `.zip` to match the canonical inventory convention.

**Boundary notes.** Filename changes from `Nat<YYYY>.zip` (1968-1993) to `Nat<YYYY>us.zip` (1994+) at the 1994 publication-suffix introduction. Sample-frame changes at 1972 (50% sample for 1968-1971 → 100% for 1972+). Certificate-revision boundaries: 1968-revision (1968-1977) → 1978-revision (1978-1988) → 1989-revision (1990+ canonical; 1989 is the rollout-year standalone, reconciled at C8.17 DO step 4 per soft-flag (t)). Record lengths for the 22 pre-1990 zips were resolved at C8.17 DO steps 2-4 (`field_specs.py` per-era extensions); the 35 1990-2024 record lengths follow the existing per-era `natality/scripts/01_import/` codepath. All 22 pre-1990 zips are SHA-anchored here (C8.17 DO step 1); `imported=true` as of C8.17 DO step 6 (parser `parse_all_pre1990_years.py` landed at DO step 5a; canonical 1968-2024 re-harmonize + the `imported` flip at DO step 6).

---

## Section 3 — Linked-cohort raw zips (38; cohort years 1983-2023, permanent 1992-1994 gap)

> **C8.18 DO step 2 extension (2026-05-17).** 19 pre-2005 **cohort-linked** rows added (cohort years 1983-1991 + 1995-2004) per the C8.18 cohort-only backward extension (DECISION_LOG 2026-05-17T05:30:00Z; §15.D scope-corrected `[plan-update]` `df0675f`). These zips are SHA-anchored + on disk at `raw_data/linked/` and were **harmonized into the linked v4 parquet at C8.18 DO step 6b (2026-05-23; the v3→v4 1983-2023 re-harmonize; DECISION_LOG 2026-05-23T02:00:00Z)**. The `file_inventory.csv` `imported` flag refresh false→true for these 19 pre-2005 cohort rows **was shipped at the `file-inventory-imported-flag-v4` task** (2026-05-23, commit `84a9af3`); `imported` is now uniformly `true` (95/95) across the natality inventory. (C8.18 DO step 7 itself was docs-only — zero parquet/schema/test/script/metadata-CSV mutation; the deferred `imported` flip was discharged as a separate Pre-D-cleanup task per the C8.17 DO step 7 honest-propagation precedent. See the C8.18 DO step 7 receipt's forward-looking HALTs for the original deferral framing; superseded.) Period-linked 1995-2004 (`LinkPE*US.zip`) is **out of C8.18 scope** (Option A; a separate future product). All probed HTTP 200 at the same `cohortlinkedus/` path as 2005-2015.

Naming convention (three eras):
- 1983-1991 (pre-1995, cohort-only): `LinkCO<YY>.zip` (2-digit cohort year, **no `US` suffix**); members `LinkCO<YY>USnum.dat` (infant-death numerator) + `LinkCO<YY>USden.dat` (birth denominator).
- 1995-2015 publication: `LinkCO<YY>US.zip` (cohort year as 2-digit suffix; for 2005+ the suffix corresponds to the **publication year** = cohort_year + 1). 1995-2002 members `LinkCO<YY>USDen/Num/Unl.dat`; 2003-2015 members `VS<YY>LKBC.*`.
- 2017 publication onward: `<YYYY-pub>PE<YYYY-cohort>CO.zip` (4-digit publication year + 4-digit cohort year explicit).

**1992-1994: permanent gap.** NCHS suspended ALL birth-infant-death linkage for the 1992, 1993, and 1994 cohorts (no cohort and no period file published). The gap is permanent and surfaced loud in `harmonized_schema.csv` `years_available`, CODEBOOK, ABOUT_THIS_RELEASE.md, and the manuscript Coverage paragraph (per EXPLORATION_REPORT §A.3 risk (a)).

Each zip contains one publication-year + cohort-year pair. Inventory keys these as `<cohort_year>_linked` to match the cohort year that the parquet pipeline harmonizes against (cohort = year-of-birth of the cohort being followed for infant deaths).

| Cohort year | Inventory key | raw_filename | SHA-256 |
|---|---|---|---|
| 1983 | `1983_linked` | `LinkCO83.zip` | `1eb16d4f185abec566472d6ef00811ff910288b8945c5224c20d1eabf21f0f5c` |
| 1984 | `1984_linked` | `LinkCO84.zip` | `ca36244bc089270b45b8e32f1f4e6b81fa746319de4dabf74019157f697edb5b` |
| 1985 | `1985_linked` | `LinkCO85.zip` | `70874c9952f194569d106f8ae704864cdb43c55147048e4acdc62646ccb6dbab` |
| 1986 | `1986_linked` | `LinkCO86.zip` | `e99694c614e5ac31bf05b240ae092a3681fcc078411ea0f028c7e9c0472ed983` |
| 1987 | `1987_linked` | `LinkCO87.zip` | `15df1eae8cb93119b0b1b2445b77362462a0a092470fc19d5f27e6ef63e5d6d8` |
| 1988 | `1988_linked` | `LinkCO88.zip` | `6f7b8e64c9576b2464c90ec5d01d31a21dba5d664ca415163bd93e91b88e87e8` |
| 1989 | `1989_linked` | `LinkCO89.zip` | `a7f9f0da4bd249d67937055e1f0bb8a9fdc7092ef66be58262abfabf507d7cc7` |
| 1990 | `1990_linked` | `LinkCO90.zip` | `af54e5c32436194a854d4c84750ced3265ec24a3ae4ca5b35d169e824dc65dec` |
| 1991 | `1991_linked` | `LinkCO91.zip` | `92c8d8a4c3299c8b8c399862f98439b4d1c4520f92d643ba9c53c38647f5bb46` |
| 1995 | `1995_linked` | `LinkCO95US.zip` | `ecc03a36a9880f5eb3a946657bfe6b54ae25b0dc1415bad6ae64c90f6a6bfa35` |
| 1996 | `1996_linked` | `LinkCO96US.zip` | `31e3e098b3b455fff293b177f6430e0ff9355459286b0a269c3e638a48cc4965` |
| 1997 | `1997_linked` | `LinkCO97US.zip` | `1b23fe4ed1511c76c5a78b622be0401550b9f3a2f55d7dfdf33ef4c40f90a5df` |
| 1998 | `1998_linked` | `LinkCO98US.zip` | `804c128875e2d8c3865e78f64af8b5144bb5a9772b3f5b2fd4099f8ecd518e83` |
| 1999 | `1999_linked` | `LinkCO99US.zip` | `444be0ec866e8082f373975862ff09ddec7026a0ebe60ab72a2a254ba0594462` |
| 2000 | `2000_linked` | `LinkCO00US.zip` | `61d0d6aad5c903f3d4cec20340d76a417a80d8db7124c01c9d442fd5f128f065` |
| 2001 | `2001_linked` | `LinkCO01US.zip` | `d49b8d36df499dfda85d2fbd20120b38cd811cb7716daac9e8d21bb0910d66ec` |
| 2002 | `2002_linked` | `LinkCO02US.zip` | `d185527f7dab8648fd50058e566065376b250a9d0e24cf52c93d2438409e8788` |
| 2003 | `2003_linked` | `LinkCO03US.zip` | `110fbbeca5e52f0f1ec8bce60cdaefdc4afeb542578d8932cd2d86d9dabe18d9` |
| 2004 | `2004_linked` | `LinkCO04US.zip` | `f5c2fbf9e71fa8a059704e9779427390b6aaac1d9722ab3993af2e712a90393f` |
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

**Linked-file coverage.** The 19 pre-2005 cohort-linked source zips (1983-1991 + 1995-2004) are SHA-anchored in this manifest and on disk, and were **harmonized into the linked v4 parquet at C8.18 DO step 6b (2026-05-23)** — the harmonized linked parquet now covers **cohort years 1983-2023** (38 years; permanent 1992-1994 NCHS-linkage gap; linked v3→v4). The `file_inventory.csv` `imported` flag refresh false→true for these 19 pre-2005 rows **was shipped at the `file-inventory-imported-flag-v4` task** (2026-05-23, commit `84a9af3`); `imported` is now uniformly `true` (95/95) across the natality inventory. The earlier "pre-2005 NOT processed (v2.x scope deferral)" statement is **superseded** by the C8.18 cohort-only backward extension (DECISION_LOG 2026-05-17T05:30:00Z + 2026-05-23T02:00:00Z; `[plan-update]` `df0675f`); see [`natality/docs/COMPARABILITY.md`](../natality/docs/COMPARABILITY.md) § "Pre-2005 cohort backward extension". Period-linked 1995-2004 (`LinkPE*US.zip`) remains out of scope (Option A; separate future product).

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

## Section 5 — Shipped harmonized parquets (cross-product gate artifacts)

> **Scope.** SHA-256 for the **primary derived (or harmonized) parquets** that downstream users load for analysis. These are outputs of the harmonization pipelines, not NCHS source zips. Full per-product tables (including regression baselines and convenience variants) live in each subproject's `PROVENANCE.md`.
>
> **Refreshed:** 2026-05-24 (D-prep.2 `provenance-refresh-current-envelope`); monorepo commit `3926e19`.

| Product | Version | File (canonical name) | Rows | SHA-256 |
|---|---|---|---|---|
| Fetal death | v2.4.0 | `fetal_death_derived.parquet` | 2,427,233 | `185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` |
| Fetal death | v2.4.0 | `fetal_death_harmonized.parquet` | 2,427,233 | `38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` |
| Natality | v3.0.0 | `natality_v2_harmonized_derived.parquet` | 201,161,456 | `acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974` |
| Natality | v3.0.0 | `natality_v2_harmonized.parquet` | 201,161,456 | `c8a740eb48d4f3de66759da27eef94143c315846885bf905a88cbc0fa6237153` |
| Linked | v4.0.0 | `natality_v3_linked_harmonized_derived.parquet` | 149,386,620 | `f630d8cf20db72eaf5e482e856e621ff73a6ad1c932de0fc832b237546b09073` |
| Linked | v4.0.0 | `natality_v3_linked_harmonized.parquet` | 149,386,620 | `ea89ab3c009de00cddb88aad84aa50fde376a47f96b6865113a600fb5a0907c7` |
| Matched multiples | C8.16 | `matched_multiples_harmonized.parquet` | 1,665,568 | `adbec1087370941fd373b933566b7dfd24dbbc2f957d998f92ac14ef45dc1549` |

**Four gate SHAs** (STATUS / D-prep invariant): `38e2cecb…` (fetal harmonized), `185c071e…` (fetal derived), `acb5c48a…` (natality derived), `f630d8cf…` (linked derived).

Per-product detail: [`fetal_death/PROVENANCE.md`](../fetal_death/PROVENANCE.md), [`natality/PROVENANCE.md`](../natality/PROVENANCE.md), [`matched_multiples/PROVENANCE.md`](../matched_multiples/PROVENANCE.md).

---

## Cross-product invariants

The manifest's three sections combine to span the full 1982-2024 fetal-death + 1968-2024 natality + 1983-2023 linked-cohort (38 cohort years; permanent 1992-1994 gap) coverage that this monorepo harmonizes. Cross-product analyses joining numerator + denominator across products (per [`docs/JOINT_USE_GUIDE.md`](JOINT_USE_GUIDE.md)) typically require each input zip's byte-identity to reproduce a published validation cell — this manifest is the verification anchor for that reproducibility.

- **141 zip × 64-char SHA-256 entries** = 141 × 64 = 9,024 hex characters of integrity information at byte-exact fidelity.
- **Inventory cross-reference**: every row of this manifest has a matching row in `fetal_death/file_inventory.csv` (43 rows; matches Section 1), `natality/metadata/file_inventory.csv` (95 rows; 57 match Section 2 + 38 match Section 3), or `matched_multiples/file_inventory.csv` (3 rows; matches Section 4).
- **Coverage envelope**: fetal-death covers 43 contiguous years 1982-2024; natality 57 contiguous years 1968-2024; linked-cohort 38 cohort years 1983-2023 (permanent 1992-1994 gap — not contiguous); matched-multiples 3 publication windows 1995-1997 / 1995-2000 / 2016-2020. Cross-product joint coverage: natality + linked = 1990-2023 (natality starts 1990; less the 1992-1994 linked gap; pre-1990 linked years are linked-only); natality + fetal-death = 33 years 1992-2024 (fetal-death pre-1990 is fetal-death-only). Matched-multiples is an ancillary product spanning natality + fetal-death + linked-cohort within its 3 windows.
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

*Manifest generated 2026-05-13 at the C8.11 DO step of the Phase C Tier-2 plan; cross-references `fetal_death/file_inventory.csv` v2.4.0 + `natality/metadata/file_inventory.csv` v3.0.0. Per Anti-Pattern #1 (append-only state files), any future update revises a NEW manifest revision rather than overwriting this one.*
