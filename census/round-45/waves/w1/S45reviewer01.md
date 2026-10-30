# S45reviewer01 — Independent historical register identity audit #1 of 66

Seat: S45reviewer01 (leaf reviewer, no dispatch). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Freeze: `019bccc9ac97f3cec1a1dea574cc2f81f57fc967` (ancestor of HEAD `18e6ec5f`; worktree dirty only with untracked round-45 record files, all reads via `git show` at pinned revs).
Base for derivation: `55d7af6f5a22340f7a3de1c386e514ababfaa75f` (BASE).
Read-only: no production bytes, counters, lessons or evidence edited; no git/jj mutation; scratch `/fast/scratch/hyaku/souji-r45/S45reviewer01/` removed after receipts retained.

## Assigned identity

Identity #1 of 66 = zero-based index 0 over unique `(line, token, class)` keys in first-occurrence order of `census/round-44/c1-population.tsv`:

```
14  65817d0d  mismatch:rev-unresolved  not a commit or object in this repository
```

Confirmed population integrity: sha256 `42287544…b0c1e2c` (matches preregistration), 70 data rows, 66 unique tuples, first row = this key, key occurs exactly once.

Filed registration (`corpus/lessons/round-44.md:25` at freeze):

```
CORRECTION-R44 id=R44-01 file=SCORECARD.md line=14 class=mismatch:rev-unresolved stale=65817d0d derived=UNRESOLVED rev=55d7af6f… scope=base-SCORECARD-token-referents
```

## Independent derivation (not a repeat of the counter)

Derivation rule for `mismatch:rev-unresolved` from the frozen counter source (`census/round-45/c1-counter.py`): scan `SCORECARD.md` line `n` **at BASE** for full `[0-9a-f]{64}` digests starting with the stale token; if present derive `sha256prefix:<digest>`, else `UNRESOLVED`.

Steps executed (receipts: `receipt-derivation-id1.txt`, `receipt-instrument-line14.txt`):

1. `git show 55d7af6f…:SCORECARD.md`, line 14 → **0** full 64-hex matches. The line does contain the literal prefix once, in the phrase ``(tool_sha256 65817d0d…, rev 9301d98c…)`` — deliberately truncated prose, not a bindable digest. Two 40-hex git revs (`4edb25df…`, `9301d98c…`) are also present and resolve, as the instrument run below confirms.
2. Rule replication (own Python, `re.findall(r'[0-9a-f]{64}', line14)` filtered by prefix) → `expected-derived = UNRESOLVED`.
3. `git cat-file -e 65817d0d^{commit}` → rc 128 (not a commit or object) — consistent with the population reason.
4. Ran the r44-era instrument itself, extracted as a blob from BASE (`tools/souji-declared-evidence.py`, sha256 `a3324916…`), against `SCORECARD.md` at BASE, format tsv, rc 1, 503 fact lines. Its line-14 output reproduces the population row exactly: `14  65817d0d  B  mismatch:rev-unresolved  not a commit or object in this repository`. (Same instrument is embedded in the new counter's population-consistency gate.)

## Verdict on identity #1

**MATCH.** Expected derived token `UNRESOLVED` = filed derived token `UNRESOLVED` (R44-01). No duplicate, no fence, no retraction for this key.

## New-counter run (bounded probe)

`python3 -B census/round-45/c1-counter.py --root <lane> --rev 019bccc9ac97f3cec1a1dea574cc2f81f57fc967 --scratch <my scratch>` → rc 0 (receipt `receipt-counter-freeze.txt`):

```
SUMMARY population=70 unique=66 registered=66 missing=0 derived_mismatches=0 junk=0 fenced=0 duplicate=0 retracted=0 historical_credit=0
```

Byte-identical to the preregistered target SUMMARY. Counter sha256 `46d5fc68…34125` matches preregistration.

## Prior r42 accounting under Q76

Q76 (canonical, `corpus/QUALITY.md` @ freeze): a calibration before-state counts only mismatches the lane's self-assessment *still carries*; items already bound by prior correction/supersession rows are excluded or counted agreeing; a before-state a correction-row pointer would erase is an instrument artifact, not a gap.

r42-era accounting (SCORECARD row preserved under `census/round-42/waves/`, e.g. `R42critic01/h1/SCORECARD.md:512`): the r33 C1 currency gain (19→24 agree) came from five cells restated at r30/r31 — "the gain is executed cause provenance, not a new correction (lesson M3, Q76)". The r45 lesson repeats the rule for this exact population: "Historical correction credit is exactly zero (Q76); the prior 70-occurrence population was already accounted for." This identity (R44-01) is one of those already-accounted occurrences; its registration adds binding/provenance only.

## Why zero new factual credit

1. The fact `mismatch:rev-unresolved` for line 14/65817d0d was *produced by the frozen r44 instrument* and is frozen into the r44 population; r45 re-derives the same 70 occurrences and only checks the filed register's bookkeeping tokens against closed-form derivation rules.
2. Nothing about repo state is newly corrected: expected values are computed from BASE blobs that were never disputed; the register filing is the only new artifact, and it agrees.
3. Q76 bars counting already-carried mismatches as fresh calibration gain; `historical_credit=0` is hard-wired in both the target and the emitted SUMMARY. Round-45 claim is instrument acquisition (0/66 → 66/66 accepted unique identities with token discrimination), explicitly not a numerical score move (calibration stays 7).

## Attack: derivation proves a referent, not historical runtime truth

1. **Negative existential over one revision's bytes.** `UNRESOLVED` certifies only: "SCORECARD.md:14 at BASE contains no full sha256 starting `65817d0d`". It is silent on whether a referent existed at filing time or at r22 runtime. In fact a referent demonstrably exists elsewhere in the BASE tree: `census/round-22/attempt2/instrument-digests.txt` @ BASE pins `65817d0d0d48…f48f4` for `tools/souji-declared-evidence.py`, and the tool blob at commit `dd8a6b70` (r22 attempt-2 digest freeze) hashes to exactly that. The derivation rule never looks outside the filed line, so "UNRESOLVED" must not be read as "unknowable" or "never existed".
2. **Runtime unmeasured.** Whether the bytes on disk during the actual r22 run hashed to the pinned digest is a historical-runtime fact this instrument does not re-measure; committed bytes at a named commit are verified, not the past environment. Likewise the "mismatch:rev-unresolved" class is a category observation (a sha256 prefix was fed to git-object resolution, the wrong resolution domain), not evidence the underlying r22 claim (`assertions=63 resolved=63 skipped=40 mismatches=0` at `9301d98c`) is false.
3. **Consistency bonus finding (bounded):** the BASE tool blob hashes to `a3324916…` because the tool was edited after r22 (`4a6ee90a`, `98e5203d`, both ancestors of BASE). So the filed line's prefix refers to a *superseded* tool generation; the register's `UNRESOLVED` remains the honest derived value under the finite rule, and the lane's own later edits make "prefix no longer matches current tool" expected, not anomalous. No defect: the counter and the register agree, and the preregistration's finite rules anticipate UNHELD/UNRESOLVED outcomes.
4. **Boundedness holds.** The lesson itself disclaims derived authority ("No deletion authority, filesystem safety or authenticated execution follows"); my audit confirms the claim saturates at tuple identity + discrimination, nothing more.

## Limitations

- Depth on identity #1 only, per assignment; identities #2–#66 are covered solely by the aggregate SUMMARY (registered=66, derived_mismatches=0), not by per-key re-derivation in this seat.
- My "independent" derivation re-implements the published rule from the frozen counter source; the rule's intent is corroborated by the round-44 lesson "Correction scope" paragraph but was not re-derived from first principles alone.
- Runs were read-only but not load-stabilized (no flock); the counter is deterministic over committed blobs, so load does not affect its output.
- Worktree at HEAD `18e6ec5f` with untracked sibling-seat files present; all measurements used `git show`/`git cat-file` at pinned revs, insulating them from worktree state.

## Commands (exact)

```
sha256sum census/round-44/c1-population.tsv census/round-45/c1-counter.py
git show 019bccc9…:corpus/lessons/round-44.md | grep -n '^CORRECTION-R44 id=R44-01 '
git show 55d7af6f…:SCORECARD.md | awk 'NR==14'                      # filed line bytes
git show 55d7af6f…:SCORECARD.md | awk 'NR==14' | grep -oE '[0-9a-f]{64}' | sort -u | wc -l   # → 0
git cat-file -e 65817d0d^{commit}                                    # rc 128
git show 55d7af6f…:tools/souji-declared-evidence.py > instrument-at-base.py
TMPDIR=<scratch>/inst-run python3 -B instrument-at-base.py --root <lane> --rev 55d7af6f… --file SCORECARD.md --format tsv   # rc 1, 503 lines
git show dd8a6b70:tools/souji-declared-evidence.py | sha256sum       # → 65817d0d…f48f4
git show 55d7af6f…:tools/souji-declared-evidence.py | sha256sum      # → a3324916…
python3 -B census/round-45/c1-counter.py --root <lane> --rev 019bccc9… --scratch <scratch>/counter-run   # rc 0, target SUMMARY
```

Result: **identity #1 MATCH (UNRESOLVED = UNRESOLVED); counter green at freeze; zero new factual credit confirmed under Q76; claim bounded to referent-level calibration, not historical runtime truth.**
