# SwarmReviewer31 — Rev-C2Rows (SOURCES rows S212–S215) — round 28, w1

## Status
STATUS: PARTIAL — structural contract checks pass for all four appended rows (NF=13, no literal/escaped pipe in any cell, ISO opened, tier A, kind enum, status=mined, used-by exactly the admitted entries, all paths exist at tip, fleet validate rc=0); S215 fails one check: its anchor sha256 pin does not match the byte-exact snapshot file (garbled pin), so the row's provenance pin cannot verify.

## Evidence
- Frozen contract read first: `census/round-28/records/preregistration.txt` (raw lines 5–9, 10–24): C2 names S212=open(), S213=rename(), S214=fsync() (status=mined, used-by exactly the admitted entries, 11-column fleet census schema); S215 = decision-time ADMIT row for the routed S119 zh-Hans `git-fetch(1)` edition, used-by `corpus/knowledge/git-auto-maintenance-trigger-set.md`. Kill rule: used-by citing an unadmitted entry fails C2.
- Fleet schema: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` — 11 columns ⇒ NF=13; kind enum `spec|docs|paper|code|tool|dataset|talk|book|community|own-work`; tier `[ABC]`; status `queued|mined|rejected`; opened must be a past/present ISO date (E08); recheck must be ISO date | `NNd` | symbolic `[A-Za-z][A-Za-z0-9 _-]*` (E09); E11 = used-by path missing on disk.
- Row harvest: `awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}'` → `0` (before and after append; rows at `corpus/SOURCES.md:157–160`).
- Row count: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `139` (135 base + S212–S215; C2 claim counts 138 excluding S215 — consistent with ADMIT).
- Grounded F4: `grep -cE '^ground: F4' corpus/knowledge/*.md` → `6` (r33/r27/r24/r23 + r28 exclusivity + r28 durability), confirmed by `grep -l` listing both r28 entries.
- Fleet validate at tip: `bash scripts/sources-census.sh validate --today 2026-10-25 --root /home/vgpnk/Projects/shokunin souji-shokunin` → `validate_rc=0`, lane line `souji-shokunin ok …/corpus/SOURCES.md`; no E01–E11 for S212–S215 (only pre-existing W04 duplicate-URL warnings, unchanged from before-append run).
- Snapshot digests (sha256sum of `census/round-28/sources/`): open.html `57b770918aa3e0c25186972675df8c96da119cf4b973335ed4487405e260dc3a`, rename.html `06671610134b0a52cdf4dcdaf382f72fef85ef51088b8a52b8679c7f03829318`, fsync.html `5c2975abbb2d65fcad92a4da5241f4f4001f0e5d8cf57f752d9486073ca49747` — all byte-match the digests recorded in the two admitted knowledge entries and in `census/round-28/sources/SHA256SUMS`.
- S215 snapshot: `git-fetch-zh-HANS-CN.html` sha256 `a7f4742d99fd515f1811aabd830a61840939ebe3e12cf1e6792662181b574042`; page carries `lang="zh_HANS-CN"` and `git-fetch last updated in 2.56.0`; auto-maintenance sentence located at snapshot line 3117 (`<p>在最后运行 … git maintenance run --auto … 这个功能默认启用。</p>`). Disposition record `census/round-28/records/s119-disposition.tsv:2` records the same digest (field sha256 = `a7f4742d99fd515f1811aabd830a61840939ebe3e12cf1e6792662181b574042`).
- Landing state: `git -C … status --porcelain=v1 --untracked-files=all -- corpus/SOURCES.md corpus/knowledge/` → ` M corpus/SOURCES.md`, `?? corpus/knowledge/origin-record-durability-r28.md`, `?? corpus/knowledge/origin-record-exclusivity-r28.md`; HEAD `0c96332932e66bbaf9cf1c246091d3275a0ab612` (L1 integrates/commits; "at tip" = working-tree landing state).

## Findings
1. **S215 sha256 pin mismatch (medium).** Row `corpus/SOURCES.md:160` anchor cell pins `sha256 a7f4742d99fd515f1811a1abd830a61840939ebe3e12cf1e6792662181b57404`, which is not the digest of `census/round-28/sources/git-fetch-zh-HANS-CN.html` (`a7f4742d99fd515f1811aabd830a61840939ebe3e12cf1e6792662181b574042`; first divergence at index 21 — row carries an extra `1` and a lost trailing `2`). The disposition record and the snapshot agree with each other; only the row pin is garbled. Impact: the row's provenance pin cannot verify against the artifact; it is a data defect in the delivered row, not a counter/predicate/target challenge. Fix (L1/executor, before commit): correct the anchor pin to the snapshot digest `a7f4742d99fd515f1811aabd830a61840939ebe3e12cf1e6792662181b574042`.
2. No other row defect found: S212–S214 anchors name snapshots without inline digests; their digests are verified in the admitted entries (finding 0 evidence bullet). No literal or escaped `|` in any cell (NF=13 + `\|`/`&#124;` scan clean); no empty cells; E02/E03 (id/duplicate) absent.
3. Used-by wiring is exactly the admitted entries: S212/S213 → `corpus/knowledge/origin-record-exclusivity-r28.md`; S214 → `corpus/knowledge/origin-record-durability-r28.md`; S215 → `corpus/knowledge/git-auto-maintenance-trigger-set.md` (tracked at HEAD). All three paths exist on disk; entry-side citation counts confirm the bijection (exclusivity cites S212/S213; durability cites S214; S215 used by the pre-existing admitted entry).
4. Recheck values are schema-valid: S212–S214 `365d`, S215 `on-release` (symbolic cadence); opened = `2026-10-25` for all four (past/present ISO). Kind enum valid: spec for S212–S214, docs for S215. Status=mined for all four.

## Row verdicts
- S212 — **PASS** (NF=13, 11 fields, no pipe escapes, spec/A/mined/2026-10-25/365d, used-by exactly exclusivity entry, exists at tip)
- S213 — **PASS** (same shape; used-by exactly exclusivity entry)
- S214 — **PASS** (same shape; used-by exactly durability entry)
- S215 — **FAIL** (structure/date/tier/kind/status/used-by all pass; anchor sha256 pin does not match the snapshot bytes — see Finding 1)

## Attack log
None — no predicate, target, counter, or case set is contested; the S215 pin defect is a data content error, reported as Finding 1 (severity medium), not a counter game.
