# SwarmScribe33 — records draft for round 32 attempt 2, wave a2w1

## Status

STATUS: PASS — `deliver-records-w2.md` drafts all four blocks the L1 lands (SCORECARD `### Round 32
measurements`, `### Round 32 capability rows`, `### Planned (appended at round 32)`, and the LOG.md attempt-2
entry) with every number copied from a committed file and every unresolved number marked `<L1>`. Two blocking
pre-paste defects found (Findings 4, 6) and one unreproducible reading found (Finding 1).

## Evidence

Lane read-only; no clone, no scratch dir created (`ls -d /fast/scratch/hyaku/souji-r32/SwarmScribe33` -> "No
such file or directory"); tip `git -C <lane> rev-parse master` = `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`.

1. Frozen contract and data, opened this run: `census/round-32/records/preregistration.txt`,
   `amendments.txt`, `controls.tsv`, `controls-a0.tsv`, `c1-after-v1.txt`, `c1-after-v2.txt`,
   `c2-after-v1.txt`, `c3-after-v1.txt`, `c3-after-v2.txt`, `m1-red-before.txt`,
   `a2-l1-salvage-tip-measure.txt`, `census/round-32/c2-items.tsv`, `census/round-32/measure.sh`,
   `census/round-32/c3-contract.txt`, `records/jj-mtime-clock-run.txt`, `corpus/SOURCES.md`,
   `corpus/knowledge/jj-abandoned-object-mtime-clock.md`, `SCORECARD.md:340-471`, `LOG.md:1700-1806`,
   `.ufo/waves/round-32/w1/{SwarmCritic34,SwarmExecutor04,SwarmExecutor05,deliver-records-skeleton,deliver-quality-q70-q72}`,
   and the untracked salvage record named above.

Reading triple, each with its own record line:

```
census/round-32/records/controls.tsv:2   SUMMARY items=44 … unbound=44 mismatches=44 rev=3ec84fc8…
census/round-32/records/c1-after-v1.txt:46   SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6 rev=9e8982b7…
census/round-32/records/c1-after-v2.txt:46   (identical) rev=9e8982b7…
census/round-32/records/controls.tsv:3   SUMMARY items=27 pass=1 fail=26 rev=3ec84fc8…
census/round-32/records/c2-after-v1.txt:29   SUMMARY items=27 pass=26 fail=1 rev=98e5203d…
census/round-32/records/controls.tsv:4   SUMMARY legs=14 fail=13 f1_entries=4 rev=3ec84fc8…
census/round-32/records/c3-after-v1.txt:16   SUMMARY legs=14 fail=0 f1_entries=5 rev=a92e1aae…
census/round-32/records/c3-after-v2.txt:19   SUMMARY legs=17 fail=0 f1_entries=5 rev=a92e1aae…
```

2. Landing commits `git show --stat --oneline`: `98e5203d` C2 (27 files: 14 `tests/fixtures/`, 13 `tools/`),
   `a92e1aae` C3 + A1 + r31 defect 2 (17 files incl. `census/round-32/sources/` 4 `.adoc` + `SHA256SUMS`),
   `9e8982b7` C1 (SCORECARD.md, +43 lines), `4e56c48b` salvage (the five after-records only).

3. Supporting facts: SOURCES rows at master `147` (`git show master:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`),
   S223 at `corpus/SOURCES.md:168`, `records/fetch-receipts.tsv` 4 rows, `jj-mtime-clock-run.txt` 22 `RESULT`
   lines + `jj 0.45.1` / `git version 2.56.0`, `census-start.txt` 36 `W04` and `souji ok` `exit=0`,
   `corpus/lessons/round-32.md` absent, `census/round-32/waves/` absent.

4. Quote used in the draft, opened this run: `tools/souji-vault-verify.sh:742` — "export TMPDIR=\"${TMPDIR:-/var/tmp}\"".

## Findings

1. **T12's C2 verdict is not reproducible at one revision** (`census/round-32/records/c2-after-v1.txt:13` vs
   `census/round-32/records/a2-l1-salvage-tip-measure.txt:147`, both at rev `98e5203d`). The first record reads
   `T12 PASS base=rc1:W5903:selftest: 69 checks, 6 failed`, the second `T12 FAIL base=rc0:W5363:selftest: 69
   checks, 0 failed`, and a third base reading appears at `:145` (`base=rc1:W4488:FAIL raw LF path refusal
   exits: root=2 compare=2`). The base revision and argv are fixed by `--base`, so the base run itself varies.
   [INFERENCE] the raw-LF path case is sensitive to the host's filesystem/load; I did not re-run the item. Any
   `fail=0` landing that includes T12 is therefore unstable — this is stronger than the T18 miss already logged.

2. **The landing PASS for T12 was a reproduced base failure**, not a TMPDIR result: `c2-after-v1.txt:13` shows
   `base=rc1 … sbox=rc1` with equal last lines, which is the predicate's `ok_a` as written
   (`census/round-32/c2-counter.py:174-176`, quoted by `w1/SwarmCritic34.md` Finding 1). The C2 row's after
   cell therefore must not be read as "26 items verified to honour TMPDIR"; the capability row in the draft
   states the weaker, true property.

3. **C1's miss is rule-level, not data-level** (`census/round-32/records/c1-after-v1.txt:29-35`). The six
   unbound items (N28-N31, N33, N34) all sit on `SCORECARD.md:422`; eight integers stand on two SUMMARY lines,
   and one row per `(path,line)` caps the line at two bindings, so the remaining six are `BAD-ROW(shared-
   occurrence)` by construction (`w1/SwarmExecutor05.md` Findings 2-3). Withdrawing them was refused because
   cited records do show those integers, and `withdrawn=17` already exceeds the cap of 8. The cell's integers
   are correct (`w1/SwarmExecutor05.md` Finding 5), so r33's redesign — not a count correction — is the fix.

4. **`measure.sh` has no C3-v2 leg**, so the A1 target `legs=17 fail=0` cannot be re-derived by the frozen
   runner (`census/round-32/measure.sh:18-20` runs only `c3-counter.py`). `c3-after-v2.txt` and the salvage-tip
   `:167` line were produced by hand. The draft's command cell names the explicit invocation and flags the gap.

5. **The salvage records re-derive cleanly otherwise.** `a2-l1-salvage-tip-measure.txt` reproduces the landed
   readings for C1 (`:48` and `:95` = `c1-after-v1/v2.txt:46`), C3 v1 (`:142` = `c3-after-v1.txt:16`) and C3
   A1 (`:167` = `c3-after-v2.txt:19`); the only divergence is T12 (Finding 1) plus T18's expected anchor drift
   (`:113` sbox `baseline_mismatches=32` vs `c2-after-v1.txt:17` `31`).

6. **`census/round-32/records/a2-l1-salvage-tip-measure.txt` is untracked** at `4e56c48` (`git ls-files
   --error-unmatch` -> "Did you forget to 'git add'?"). Eight citations in the draft point into it; the L1 must
   commit it or swap them for the final-tip record before pasting, or the cells rest on an uncommitted blob.

7. **C2's commit message count does not match its own file count**: `98e5203d` says "26 tools and fixtures take
   scratch from TMPDIR" while `git show --stat` lists 27 changed files, and `tests/fixtures/r20-input-binding.py`
   (T18) is one of them and still fails. Read as 26 fixed + 1 touched; not dishonesty, but the message must not
   be paraphrased into "27 fixed" in the LOG entry (the draft says "27 files under `tools/` and `tests/fixtures/`
   were changed so their scratch root comes from the caller's `TMPDIR`", which is what the diff shows, and names
   T18 separately as the miss).

8. **Worktree state at reading time is dirty** (`git status --porcelain`): `M SKILL.md`,
   `M tests/fixtures/r15-preservation-frozen/expected.json`, `M …/record.json`, `?? …/a2-l1-salvage-tip-measure.txt`
   — the L1's in-flight attempt-2 work, untouched by this seat. The draft cites revisions, never the worktree.

9. **Attempt 1 ran a counter without `-B`**: `census/round-32/__pycache__/c1-counter-v2.cpython-314.pyc` exists
   (05:31), gitignored (`.gitignore:3`) and untracked, so no committed artefact carries it. Hygiene note only.

## Attack log

Not an attack seat. The two counter-level observations in Findings 1-2 are recorded for the wave's attackers to
reproduce; I did not run the C2 counter, and no predicate, target or item was proposed for change here.

## Deliveries

- `.ufo/waves/round-32/a2w1/deliver-records-w2.md` — the four paste-ready blocks plus three fill rules
  (landing-vs-tip discipline, the missing `c3v2` leg, the untracked salvage record).
- `.ufo/waves/round-32/a2w1/SwarmScribe33.md` — this report.

No lane file other than these two was written; no `git add/commit/push/stash/checkout/reset`, no `jj` mutation,
no `rm`/`mv`, no signals; nothing outside `/home/vgpnk/Projects/shokunin/souji-shokunin/` was read-modify-written.
No tool installed or upgraded (pacman not invoked); no credentials, `/proc` census or `.scratch/` contents touched.
