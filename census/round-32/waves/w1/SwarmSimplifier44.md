# Spec hygiene — souji r32 wave 1 (item SpecHygiene, role simplifier)

Plan under audit: `souji-shokunin/.ufo/waves/round-32/w1-dispatch.json` (sha256 `60d633cded3c0316d9375026675623f04d2e756fdc2e6a1c8d2489a9fba44759`, 98992 bytes) and its generator `make-spec-w1.py` (sha256 `42efdc70…77389c2f`, 42098 bytes), both untracked because `.gitignore:1` ignores `.ufo/waves/`. Lane tip `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`, base `85b61a151923986e7e6b48f7084b9122561b5f3d`, preregistration `3ec84fc81b3243429c834a051880b0bcde06291c`. Quotes from the dispatch are its JSON-decoded prompt text (the file escapes `"` as `\"`); line numbers are file lines.

## Status
STATUS: PARTIAL — the eight structural predicates hold (44 seats; 44 distinct item ids and 44 distinct prompts; roles only from the 10 allowed names; flash 34/44 = 77.3 %; attack 11/44 = 25.0 %; 34/34 scratch tokens under `/fast/scratch/hyaku/souji-r32/`, each inside its own item dir; 44/44 report paths distinct and under `w1/`; zero deliverable-name collisions and zero overlaps among the declared C2 file sets, though D8 shows the realized run has already departed from those sets; every rendered prompt is byte-identical to its `w1-spec.json` item after stripping the three dispatcher-added lines). The "every path absolute" predicate fails on 23/44 prompts, and seven further defects (D2-D8: two shared integration targets, one realized cross-seat edit of a file another item owns, one contradiction with the frozen context, one acceptance command that cannot pass as written, one with unfilled deterministic placeholders, one triplicated attack set, one C2 file list not closed under runtime dependency) need the L1's ruling; the wave is already dispatched (`w1.ready.dispatched` 2026-10-26T05:28:15), so these are wave-2 / integration findings, not pre-dispatch gate failures. No claim predicate, target or counter is contested here.

## Evidence

E1 — structural audit (single heredoc over the dispatch, `python3 -B -`):
```
seats 44 names_distinct True prompts_distinct True
roles_ok True flash 34 77.3% attack 11 25.0%
scratch_tokens 34 outside_prefix []
reports 44 distinct 44 all_in_w1 True
deliver_names_colliding {}
c2_owned_files 27 colliding {}
```
Roles: executor 19, scribe 7, critic 5, reviewer 3, mutation-tester 3, scout 2, connector 2, revenger 1, sentinel 1, simplifier 1.

E2 — enumeration coverage (`python3 -B -` over `census/round-32/c1-items.tsv`, `c2-items.tsv` and the dispatch):
```
C2 unique 27 dupes {} tsv 27 missing_from_plan [] extra []
C1 ranges {'C1BindA':('N01','N05',5),'C1BindB':('N06','N11',6),'C1BindC':('N12','N19',8),'C1BindD':('N20','N26',7),'C1BindE':('N27','N34',8),'C1BindF':('N35','L29',10)}
C1 unique 44 dupes {} tsv 44 diff []
```
Plan item ids partition the frozen item tables exactly; no id is assigned twice.

E3 — C2 file ownership (`python3 -B -`, tsv file column × plan owner): `files 26 multi-owner {}`; per seat C2Gate 3, C2Decl 3, C2Cert 2, C2Pres 2, C2Struct 2, C2Census 1, C2Receipt 4, C2Fix20 2, C2Fix23 3, C2Fix24 2, C2Fix27 2. C2Struct additionally owns `tests/fixtures/r13-repo-structure.sh` (27th file), claimed by no other item. `w1/sources/` has one writer (C3Snapshots); CredScan only reads it.

E4 — absolute-path census (`python3 -B -`, all `/…` tokens in the 44 prompts, first matching class wins): W 48, lane 152 (31 distinct paths), scratch 34, shokuknow 5 (read-only), fleet-root 8 (read/guard: `AXES.md`, the round prompt, the prior report, `scripts/sources-census.sh`, the bare fleet root as a TMPDIR guard), system/URL 170 (`/var/tmp`, `/tmp`, `/dev/shm`, `/skill`, git tag URLs). 23 items carry at least one lane-relative filesystem reference outside contract vocabulary (E8).

E5 — round-31 labrat lineage: `grep -c "except your single labrat" round-31/w1-dispatch.json round-30/w1-dispatch.json` → `10`, `7` (this wave: 19).

E6 — D7 reproduction (scratch, `TMPDIR` set, registry copy plus one S223 row at line 169):
```
sources-census.sh validate --file $S/lane/corpus/SOURCES.md --today 2026-10-26   → exit=1, 147 E11 lines
… after linking corpus/knowledge into the copy root                                    → exit=1, 57 E11 lines
file	E11	S223 missing used-by corpus/knowledge/jj-abandoned-object-mtime-clock.md
```
E11's test is `[ ! -e "$dir/$path" ]` with `dir` = the registry file's parent-of-parent (`scripts/sources-census.sh:566`, `:497-505`).

E7 — referenced inputs exist: of the 31 distinct lane paths named absolutely in prompts, 29 are committed at tip `7a6667cd2765`; the only misses are the two gitignored plan files (`.ufo/waves/round-32/make-spec-w1.py`, `.ufo/waves/round-32/w1-dispatch.json`, present on disk, absent from git) — the one remaining unmatched token `corpus/lessons/round-2` is the bracket glob `round-2[8-9].md`. At `--list-rev` `3ec84fc` the blobs the counters read there (`c1-items.tsv`, `c2-items.tsv`, `c3-contract.txt`, preregistration) are present.

E8 — relative-reference inventory (per item, after removing the `Report:` trailer), e.g. `C2Gate ["tests/fixtures/r30-landing-gate-discovery.py","tests/fixtures/r31-landing-gate-precision.py","tools/souji-landing-gate.py"]`, `C3Fixture ["tests/fixtures/r32-jj-mtime-clock.sh"]`, `LessonGate ["census/round-31","corpus/lessons","tools/souji-record-contract.py"]`.

E9 — delivered edit sets vs the plan's lists (`for f in w1/*.diff; do grep '^+++ ' $f; done`): `deliver-SwarmExecutor14-transitive.diff` touches `census/round-13/run-verification.py`, `census/round-14/cache-demonstration.py`, `census/round-14/run-targeted.py`, `census/round-14/run-verification.py` and `tools/souji-seat-audit.py` — the last is C2Pres's declared file (`deliver-souji-seat-audit.py`, `SwarmExecutor10.md:78`). `SwarmExecutor11.md:45-46` states T15 needed `tools/souji-round9-selftest.sh`, verified at base: `tools/souji-verify.sh:1485` calls it, and that script's line 7 is `R9_TMP=$(mktemp -d -p /var/tmp souji-round9-selftest.XXXXXX)` with line 14 `export TMPDIR=/var/tmp GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null`.

No tool installed. Scratch `/fast/scratch/hyaku/souji-r32/SpecHygiene` was created for E6 only and removed; no clone, no lane mutation, no `git add/commit/push/reset/checkout`, no `jj`.

## Findings

1. **D1 — 23/44 prompts name lane files relatively; the absolute-path rule in the same plan is violated.** `C3Fixture` (`w1-dispatch.json:391`): "Write tests/fixtures/r32-jj-mtime-clock.sh to the FROZEN C3 fixture contract" — a creation target with no absolute form anywhere in the item, resolving from the seats' working dir (the fleet root) to `/home/vgpnk/Projects/shokunin/tests/fixtures/`, i.e. outside the lane write scope. `C2Gate` (`:336`): "C2 items T01 T02 T29 T30: tools/souji-landing-gate.py" — the ownership list of all 11 C2 executors (`:336-386`) is relative; mitigated only because the same text pins the clone absolutely ("Work in a scratch clone (/fast/scratch/hyaku/souji-r32/C2Gate/, origin removed)"). The plan's own context (`:301`) states "every lane path must be written as /home/vgpnk/Projects/shokunin/souji-shokunin/<path>". Read/draft targets affected besides the 11 C2 seats: `C1BindE`, `C1BindF`, `C3Docs`, `C3Entry`, `C3Rows`, `LessonGate`, `QualityCriteria`, `RecordsSkeleton`, `CountProvenance`, `CredScan`, `AttackM1`. Vocabulary-only and correctly relative: the `SCORECARD.md:<line>` binding column (six C1 seats, `census/round-32/c1-counter-v2.py:18-19` fixes that literal), `census/round-<K>/` classifier text, `corpus/knowledge/…` used-by cells, the receipt's `snapshot` column, and the `Report:` trailers. Fix: prefix the 23 references with the lane root (identical strings; no semantic change).

2. **D2 — two scribes own the same SKILL.md Gate-registry cells.** `C3Docs` (`:421`): "SKILL.md `## Gate registry` rows for" `tests/fixtures/r32-jj-mtime-clock.sh`, `tools/souji-record-contract.py` and `census/round-32/c2-counter.py`; `QualityCriteria` (`:436`): "Also draft the matching SKILL.md `## Gate registry` rows". Both therefore draft rows for `tools/souji-record-contract.py` and `census/round-32/c2-counter.py`; the L1 would merge two conflicting texts for two rows. Fix: C3Docs owns the fixture row and `souji-record-contract.py`; QualityCriteria owns C1/C2 counter rows (or drops the table edit and delivers row text only as Q-row check commands).

3. **D3 — the per-item C2 fix idiom contradicts the frozen context and the operator scratch rule.** Context (`:301`): "shell: `mktemp -d "${TMPDIR:?}/..."`-style or `mktemp -d -t`". Every C2 executor (`:336,341,346,351,356,361,366,371,376,381,386`): "shell — `mktemp -d "${TMPDIR:-/tmp}/name.XXXXXX"` or `mktemp -d -t name.XXXXXX`" — a `/tmp` fallback, which the same prompt then exercises by requiring a run "once with TMPDIR unset". Fix: use the context idiom (`${TMPDIR:?}` / `mktemp -d -t`) so a TMPDIR-unset run refuses instead of writing under `/tmp`.

4. **D4 — C3Rows and LessonGate disagree on whether the git-gc row exists.** `C3Rows` (`:416`): "S224 git Documentation/git-gc.adoc at v2.56.0 raw tag URL ONLY if no held row" (it may refuse the row and only "say so either way"); `LessonGate` (`:431`): "ADMIT for each new C3 source row" naming "git-gc.adoc" unconditionally. If C3Rows refuses S224, the Gate admits a registry row that does not exist, and the entry's `source:` chain (C3Entry, `:411`) cites a source with no row. Fix: make LessonGate's git-gc row conditional on C3Rows' verdict, or have C3Rows decide in the same delivery.

5. **D5 — deterministic placeholders left unfilled in the acceptance commands, and the one that already diverged.** All 17 executor lines (`:306-386`) literally carry "`--only <ids> --scratch <your scratch>/cnt`", although each prompt already names its own absolute scratch dir and its own ids. The counters take comma-separated ids only — `census/round-32/c1-counter-v2.py:189` "comma-separated item ids (diagnostic; SUMMARY then marks partial=1)" — so a seat pasting its range string (`N01-N05`) matches no item and gets `SUMMARY … items=1 partial=1` with zero verdict lines (`:370-371`). The same ambiguity has already split `<YourItemId>` two ways in this wave: `w1/` holds `deliver-SwarmExecutor07.diff`, `deliver-SwarmExecutor08.diff`, `deliver-SwarmExecutor09.diff` (agent names) beside `deliver-C2Fix23.diff`, `deliver-C2Fix27.diff`, `deliver-C2Receipt.diff` (item ids), so the L1 must map six diff files by hand instead of matching item ids. Fix: substitute `/fast/scratch/hyaku/souji-r32/<Item>/cnt`, the expanded comma list, and one explicit rule for `<YourItemId>` = the registry item id (`C2Gate`, not `SwarmExecutor07`).

6. **D6 — ReviewControls re-runs the three critics' attack vectors.** `ReviewControls` (`:456`): "C2 — a tool that detects a read-only /var/tmp" versus `AttackC2` (`:471`): "Can the target be met by a tool that notices the read-only /var/tmp"; the same item also restates AttackC1's census-grep binder and AttackC3's "runs jj/git/touch for show and prints a typed record" fixture. Three falsifiers, two seats each: no added falsification, and because it is scored as an attack seat it inflates the ratio that sits exactly at the 25 % floor (see O2). Fix: strip the three cheat vectors from ReviewControls (leave control minimality and the junk-state scoring) or move them there and re-scope the critics to distinct vectors.

7. **D7 — C3Rows' "exit 0 required" acceptance cannot pass in wave 1.** `C3Rows` (`:416`) requires the seat to run `sources-census.sh validate --file <scratch copy>` over the appended registry copy and states "paste output (exit 0 required)", while the row it adds is `mined` with used-by `corpus/knowledge/jj-abandoned-object-mtime-clock.md`, a file that lands only at L1 integration. Reproduced (E6): registry copy alone → exit 1 with 147 E11 findings; with `corpus/knowledge` present in the copy root → still exit 1, the surviving finding being exactly `E11 S223 missing used-by corpus/knowledge/jj-abandoned-object-mtime-clock.md`. Fix: validate against a full scratch clone carrying a stub of the entry at that path, or move the exit-0 acceptance to the L1's post-landing run and let the seat paste the pre-landing E11 with a note.

8. **D8 — the C2 file lists are not closed under runtime dependency, so "no two items own a file" is defeated in practice.** `C2Fix20` (`:371`) names only `tests/fixtures/r20-audit-contract.py` and `tests/fixtures/r20-input-binding.py`, yet its delivered transitive diff edits `tools/souji-seat-audit.py`, which the plan assigns to `C2Pres` (`:351`), plus four `census/round-13|14` scripts (E9); `C2Struct` (`:356`) names `tools/souji-verify.sh`, but T15 cannot pass without `tools/souji-round9-selftest.sh`, a file the C2 enumeration excludes (`census/round-32/c2-items.tsv:2`, "souji-round9-* excluded"). The declared-set check passes (E3: no file has two declared owners) while the run has already produced one file with two editors and four out-of-set record edits, each of which the L1 must accept or reject by hand. Fix: add `tools/souji-round9-selftest.sh` to C2Struct's list, assign `tools/souji-seat-audit.py` to exactly one item, forbid edits under `census/round-1[34]/`, and have the L1 reject diffs touching files no item names.

### Observations (not defects; no action required for wave 1)

- **O1 — executor lane-bounds grant "except your single labrat"** appears on exactly the 19 executor prompts and is inherited (E5: 10 in r31, 7 in r30). No labrat scratch, report path or write scope is assigned anywhere, so the one subagent slot a seat may open is unscoped; inherited text, not introduced by this plan.
- **O2 — attack seats sit exactly on the floor**: 11/44 = 25.0 % (r30 31.4 %, r31 26.3 %); losing one critic/reviewer/mutation-tester seat gives 10/43 = 23.3 %, below the contract.
- **O3 — C1 per-item acceptance is subset-scoped**: each C1 seat runs `--only`, whose SUMMARY sets `partial=1` (`c1-counter-v2.py:370-371`), so a seat's `unbound=0 mismatches=0` covers its slice only; the round target still needs the L1's full 44-item run.
- **O4 — no C1 binding seat runs `c1-counter.py` v1**: all six C1 acceptances use `c1-counter-v2.py` (A0); v1 appears only inside the Q70 text a scribe drafts. The frozen target needs v1 **and** v2, so the v1 run remains an L1 landing check.
- **O5 — `RecordsSkeleton` (`:441`) names the fleet report `{F}/.ufo/reports/round-32/souji.md` as draft content**; its write target is `w1/deliver-records-skeleton.md`. One added clause ("write nothing under the fleet root") would remove the only prompt-adjacent path that a seat could mistake for a destination.
- **O6 — the plan is not revision-pinned** (`.gitignore:1` ignores `.ufo/waves/`), so this audit pins it by sha256 and not by commit; the frozen artefacts it references (items, counters, contract, prereg) are committed.

## Deliveries
- `.ufo/waves/round-32/w1/SwarmSimplifier44.md` (this report). No other file written.
