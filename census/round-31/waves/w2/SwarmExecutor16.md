## Status

STATUS: PASS — the L1's C3 reading is re-derived exactly and the committed record reproduces byte-for-byte on this host; C3's frozen targets hold at its landing commit and at the tip. No target is refuted. Three advisory C3 defects and one reproduced counter blind spot are recorded below; none moves a frozen target.

## Evidence

Environment: jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5, git 2.56.0, Python 3.14.8 — the versions the record names. Scratch `/fast/scratch/hyaku/souji-r31/w2-ReRunC3/`, TMPDIR inside it, removed after delivery.

Counter identity (so the numbers compare to the amendments, not to a modified file):
- `sha256sum census/round-31/c3-counter.py` -> `c978ad7ce6…d59154`; its git blob is `6c3f3fb`, identical to the blob at prereg `1d45496`, so v1 was never edited after freezing.
- v2 -> `72a946e3cc…` (A0 line), v3 -> `5553b6d861…` (A3 line).
- `git ls-tree` at both `1baf4da` and `2c16d01` gives blobs `6c3f3fb / e3cc549 / 4fd8eb1`; `git diff --stat 1baf4da 2c16d01 -- <entry, fixture, record, sources, SOURCES.md, counters>` printed nothing. Running the tip's counters is therefore running the landing commit's counters on landing-commit bytes.

Six runs, serial, one process at a time (`--root <lane> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --scratch <scratch>/cnt`), all lines in `deliver-c3-rerun.txt`:

| counter | rev | SUMMARY | rc |
|---|---|---|---|
| c3-counter.py | 1baf4da | `legs=11 fail=0 f1_entries=4` | 0 |
| c3-counter-v2.py | 1baf4da | `legs=12 fail=0 f1_entries=4` | 0 |
| c3-counter-v3.py | 1baf4da | `legs=13 fail=0 f1_entries=4` | 0 |
| c3-counter.py | 2c16d01 | `legs=11 fail=0 f1_entries=4` | 0 |
| c3-counter-v2.py | 2c16d01 | `legs=12 fail=0 f1_entries=4` | 0 |
| c3-counter-v3.py | 2c16d01 | `legs=13 fail=0 f1_entries=4` | 0 |

Every leg line is in the delivery; shared lines were identical across all six runs: `L1 PASS f1_entries=4`, `L2 PASS coverage="grounded=17 mapped=17 dangling=0 mismatches=0"`, `L3 PASS gate="entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0" rc=0`, `L4 PASS snapshots=3 bad=[]`, `L5 PASS quotes=9 bad=[]`, `L6 PASS cited=['S002','S054','S063','S117','S220','S222'] missing=[] new_opened_today=['S222'] url_unbound=[]`, `L8 PASS run_record=present results=17`, `L9 PASS replays=[(0, 17, True), (0, 17, True)]`, `L10 PASS result_spans=6 not_in_record=[]`, `L11 PASS sources-census rc=0`, `L12 PASS … jj_calls=26 git_calls=111 missing=[]`, `L13 PASS M1:rc=0,lines=17,differs=True,no=0<4=True M2:…`.

Fixture, three independent runs (`TMPDIR=<scratch>/manual{1,2,3} bash tests/fixtures/r31-jj-object-clock.sh`): `rc=0`, 19 lines, 0 stderr bytes each; `diff census/round-31/records/jj-object-clock-run.txt manual<N>.out` was empty for all three — whole file, not just the RESULT subset. Committed record `sha256sum` -> `085b87c781dcd323a1576ee92a4a2779c1fa69dce3b62e978e0db315bad207e5`, the value the entry states.

Red control (extra): `c3-counter.py --rev 9f17a1ef… --base 9f17a1ef…` -> `SUMMARY legs=11 fail=10 f1_entries=3`, `L3 FAIL entry absent`; same shape as the frozen row `C3-do-nothing(base) c3` in `census/round-31/records/controls.tsv`. The legs are not vacuous.

Independent re-derivations, not via the counters: `tools/souji-coverage-agreement.py --rev 2c16d01` -> `grounded=17 mapped=17 dangling=0 mismatches=0` and `--rev 9f17a1e` -> `grounded=16 mapped=16 …`; `git grep -c '^| S222 ' 9f17a1e -- corpus/SOURCES.md` -> nothing (row absent at base), row unique at tip (line 167, opened 2026-10-26, 5657 B, sha256 `59e7f0f1…`); entry absent at base; F1 files 3 -> 4.

Source authenticity (A5 disclosed that L4 trusts a committed receipt): five upstream files re-fetched at their tags — `git-reflog.adoc` 5657 B `59e7f0f15204…`, `config/gc.adoc` 7753 B `0ab75f6f40eb…`, `docs/git-compatibility.md` 12284 B `0fb71f992b0e…`, `lib/src/git_backend.rs` 102068 B `95147270e5bc…`, `cli/src/commands/util/gc.rs` 2235 B `9c4d6a3704ab…`. Every hash equals the entry, `SHA256SUMS` and the receipts, so the snapshots are genuine upstream bytes, not fabricated captures.

## Findings

1. **C3 Gate anchor under-bounds its quote** — `corpus/knowledge/jj-dropped-keep-object-lifetime.md:218` reads "section Garbage collection line 52" for "It should be safe to run `git gc` in the Git repo, but it's not tested"; in the committed snapshot that sentence starts on line 52 and ends on line 53 ("repo, but it's not tested,"). Body line 79 cites `52-54` for the same bytes, so the entry is internally inconsistent too. All other eight Gate anchors do bound their quotes (five as option/config-item ranges, e.g. `--expire-unreachable` 119-121 holding a quote at 120-121). Harmed axis: calibration — L5 checks word count only, so nothing measures anchor containment. Advisory; the quote itself is verbatim.

2. **One Gate quote has no registry row, though a held row exists** — the git-compatibility.md quote at line 218 is backed by no `S`-id: the entry's `source:` lines (1-6) name S222, S063, S002, S117, S220, S054 only, and `grep -c S051` over the entry is 0, while `corpus/SOURCES.md:72` holds S051 = jj git-compatibility at tag v0.45.1. The entry flags the analogous gap for `cli/src/commands/util/gc.rs` ("no registry row yet", line 74) but not this one. Wave-1 `SwarmScribe21.md` recommended "no new row (cite S051)" for exactly this quote; the recommendation did not reach the landed file. Harmed axis: coverage (provenance); L6 checks only that cited ids are rows, never that each quoted source has a row.

3. **Claim 2's mechanism sentence is refuted by the same function it cites** — line 27-28 states "a keep ref survives only when `new_heads.contains(&id)` (git_backend.rs:925)". Upstream v0.45.1 `git_backend.rs:925` is `if new_heads.contains(&id) && name_good {`, and lines 939-945 keep a ref *not* in `new_heads` when its loose-ref mtime is newer than `keep_newer`. The entry lists 939-945 as its own anchor on source line 6, so "only when" contradicts its own citation. The measured conclusions (roles 1-4) do not depend on the sentence — they come from the record. Harmed axis: coverage (source-claim precision).

4. **The record's ref-state columns are fixture self-reports and no leg guards them** (reproduced) — with a doctored fixture whose `result()` prints `keep_refs`, `target_keep` and `reflog_hits` from a hard-coded table and leaves `object_present` on the real `git cat-file -e`, all three counters stay green: `legs=11 fail=0`, `legs=12 fail=0`, `legs=13 fail=0` (scratch commit `0ef172c447d433ae5edb20f06f67c6a7c9af06f6`, origin removed). L12 does notice nothing: its logged `git_calls` fell from 111 to 60 because the fabrication skipped three real calls, and the leg only tests a required-call set. A1 disclosed this for `reflog_hits` only; `keep_refs` and `target_keep` are equally unguarded and they carry the entry's role-3 narrative ("`keep_refs` 6 to 2", `target_keep=no`). Harmed axis: coverage/calibration; the claim's core clock (`object_present`) *is* guarded, by L9 plus L13.

All four are advisory: none changes a frozen target, and the landed C3 reading stands as measured.

## Attack log

- A1 Read preregistration and amendments A0-A5 first; confirmed the C3 target lines (`legs=11/12/13 fail=0 f1_entries=4`) and the frozen enumerate command before running anything.
- A2 Counter identity: v1 blob equals the prereg blob; v2/v3 sha256 equal the amendment digests; C3 subject bytes identical landing..tip. Refuted the "counter edited after measurement" attack.
- A3 Six serial counter runs (v1/v2/v3 at each rev) — matched the L1 reading line for line.
- A4 Fixture determinism: three fresh TMPDIRs, whole-file equality with the record; also proved the record's own sha256 claim.
- A5 Base red control — counters fail loudly at base, so the greens are not vacuous.
- A6 Re-fetched all five upstream sources at their tags and compared hashes — refuted the A5-disclosed "fabricated snapshot plus self-written receipt" attack (J6c) empirically.
- A7 Verified all nine Gate quotes as whitespace-collapsed substrings of the named snapshot and located each quote's exact line span; verified the body anchors for `git-gc.adoc` (16-20, 81-87, 141-146, 148-151, 160-161), `git_backend.rs` (900, 925, 939-945, 970-987) and `gc.rs` (44-66) against upstream bytes. Findings 1-3 came from this pass.
- A8 Independently read coverage agreement at both revisions, S222 base-absence/uniqueness and entry novelty (Finding none).
- A9 Doctored-fixture attack in a scratch clone (Finding 4): fabricated `keep_refs`/`target_keep`/`reflog_hits`, all 13 legs green.
- No tool installs were needed; no lane mutation, no `git add/commit` outside scratch, no signal, no fleet-path write. Network reachable; nothing blocked.

## Deliveries

- `souji-shokunin/.ufo/waves/round-31/w2/deliver-c3-rerun.txt` — seven counter runs with every leg line, the three fixture runs with the diff result, digest/blob identity, the upstream re-fetch table, the attack reproduction and the verdict.
- This report: `souji-shokunin/.ufo/waves/round-31/w2/SwarmExecutor16.md`.
- Scratch `/fast/scratch/hyaku/souji-r31/w2-ReRunC3/` (clone, doctored fixture, counters' temp trees) removed after the delivery was written.
