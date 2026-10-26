# SwarmCritic03 — r33 w1, C1 item K03 falsification

## Status
STATUS: PASS — verdict **HOLDS**. At 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 the frozen argv is deterministic
(4 identical runs, including TMPDIR unset), exits 0, prints `SUMMARY total=5 failed=0 hung=0`, and the predicate is
exactly as strict as the cell's stated outcome (`→ 5/5`); no out-of-set residual in that cell is stale. Two reproduced
residuals are reported (host-coupled scratch root; cell prose wider than the named command) that do not change this
item's verdict under the frozen rule.

## Evidence

Item contract read: `census/round-33/c1-items.tsv:19` → line 154, exit 0, predicate
`\b5/5\b || \btotal=5\b && \bfailed=0\b`, argv `bash tests/fixtures/r13-quarantine-bounds.sh`.

Row at base (`git -C <lane> show 6017a482e7068d5afb7617640198fbb0fe743357:SCORECARD.md | sed -n 154p`):
`| bounded quarantine operations | bounded move/digest/inspection with explicit refusal/abort and residue diagnostics;
stable special-file refusals; no new deletion authority | ` + backticked
`bash tests/fixtures/r13-quarantine-bounds.sh` → 5/5; same corrected fixture baseline red,
`census/round-13/verification.json` ` + ` | r13 |`.

Scratch clone `/fast/scratch/hyaku/souji-r33/AuditK03/c` (`git clone -q --no-local`, origin removed,
detached 2d9bca55a9f042a2c9ed60a797a8069e74c41f46; `rev-parse --show-toplevel` = the clone).

E1 — three runs at 2d9bca55, rc and stdout identical (runs 1-2 with `TMPDIR=<fresh dir>`, run 3 with TMPDIR unset):
```
TOOL	<clone>/tools/souji-quarantine.sh	sha256=e2f2d083d679f1da165866c6190af1a948c43e080d7ae629e5b08a7199849e4d
VERIFY	<clone>/tools/souji-verify.sh
CASE	R13Q8-01	PASS	regular stale file fully staged and cleaned
CASE	R13Q8-02	PASS	FIFO target refused before any read
CASE	R13Q8-03	PASS	FIFO descendant refused before any digest
CASE	R13Q8-04	PASS	delayed mv bounded; failure reported, nothing deleted
CASE	R13Q8-05	PASS	delayed sha256sum bounded; stage 1 refused
SUMMARY	total=5	failed=0	hung=0
run1 rc=0  run2 rc=0  run3(TMPDIR unset) rc=0
```
Deterministic; TMPDIR is inert for this command (see Finding 4).

E2 — counter (task item 4), verbatim:
```
$ TMPDIR=…/tmp python3 -B census/round-33/c1-counter.py --root <lane> --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch …/cnt --only K03
ITEM	K03	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=5 failed=0 hung=0
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
counter rc=0
```
Same at the lane tip: `--rev fef88f2159f6380a4d1360f73365b3d595973a37` → `ITEM K03 AGREE … mismatches=0`, rc=0.

E3 — red arm re-derived. Fixture blob is identical at 6f8ee0f (the record's measured_commit), 6017a48 and 2d9bca55
(`rev-parse 2d9bca55…:tests/fixtures/r13-quarantine-bounds.sh` = `52a8338939ba226bfb30d4b9b6876506719c7adb`).
Baseline tool = `git show 31984f473ce4bdab61a99b16cca194b28108cb81:tools/souji-quarantine.sh`,
`sha256sum` = `141c0fdc4eaf9d0a3d628b381cc5386f6d4be71565ddfb98aa10f6eb3c9573c9` = the record's
`quarantine-red-before` baseline. Run: `bash tests/fixtures/r13-quarantine-bounds.sh --tool <baseline>` → `red rc=1`,
`SUMMARY total=5 failed=4 hung=2`, CASE lines byte-identical to `census/round-13/verification.json`
(`quarantine-red-before`, exit 1, matched true, measured_commit 6f8ee0f38a14).

E4 — environment probe: same argv inside the C2 counter's own sandbox form
(`bwrap --dev-bind / / --ro-bind <empty> /tmp --ro-bind <empty> /var/tmp --ro-bind <empty> /dev/shm`) →
`sandbox rc=1`, stderr `mktemp: failed to create directory via template '/var/tmp/r13-qbounds.XXXXXX': Read-only file system`.

E5 — laxness probe: mutant `mut2` (socket treated as regular in `q_special_type`, socket accepted in
`content_digest`; 3 changed diff lines, sha256 `ffec2681f884c811c538a249af19c7c5caea8c732870bb675e4c6f5bd4fdaa0a`):
socket target → `RESULT … DRY-RUN-PASS stale`, `SUMMARY … dryrun-pass=1`, rc=0; yet
`bash tests/fixtures/r13-quarantine-bounds.sh --tool <mut2>` → `fixture rc=0`, `SUMMARY total=5 failed=0 hung=0`
(all five CASE lines PASS).

E6 — record pins: `git show 6f8ee0f38a14:tools/souji-quarantine.sh | sha256sum` =
`df4075112c36bae804b98766c4eb66b0e5b2b80b76d7333475ede27b06b168c4` = the record's `quarantine-bounds` pin.

## Findings
1. Determinism (attack 1): HOLDS. Three independent runs plus the counter's own run print an identical 6-line verdict
   body; TMPDIR unset changes nothing. No hang, no residue from any of my runs (`ls -d /var/tmp/r13-qbounds.*` = 0 after
   each pass run and after the red run's cleanup settled).
2. Predicate faithfulness (attack 2): HOLDS for the stated outcome. The row states `→ 5/5`; the fixture emits
   `SUMMARY total=5 failed=0 hung=0`, and `total` is the run count (`RAN`), `failed` is incremented for FAIL *and* HANG
   (fixture `finish_case`), and the exit is `[ "$FAILED" -eq 0 ]` — so `exit 0` ∧ `total=5` ∧ `failed=0` is exactly
   5 of 5 PASS, neither laxer nor stricter. Not lax: a plainly regressed tool (r13 baseline, no per-target bound) prints
   `failed=4 hung=2` and exits 1 → predicate fails (E3). Not stricter: no PASS-path output of a correct tool lacks the
   SUMMARY line. The predicate's first alternative `\b5/5\b` is dead for this command (nothing prints `5/5`); it is
   redundant, not lax (the second alternative carries the check and the exit gate is conjunctive).
3. Out-of-set residual, no staleness: the cell's only other stated outcome, "same corrected fixture baseline red", was
   re-derived on identical fixture bytes and returns the record's exact CASE/SUMMARY lines (E3). The record's two
   relevant pins both match committed bytes (E6, baseline `141c0fdc…`). Nothing in the cell is stale.
4. Residual R1 — host-coupled scratch root (out of set, unrouted). `tests/fixtures/r13-quarantine-bounds.sh:88` is
   `SCRATCH=$(mktemp -d /var/tmp/r13-qbounds.XXXXXX) || exit 1`, so K03 ignores `TMPDIR` and the C1 counter's
   per-item fresh `TMPDIR` is decorative for this item. Under read-only `/var/tmp` (E4) the same bytes exit 1 with no
   SUMMARY, i.e. K03 flips AGREE→MISMATCH on host state alone. r32 `## Routed defects` item 2 names five scratch
   targets; this fixture is not among them, so the r33 C2 legs do not cover it and the exposure survives this round.
   This is a measurement coupling, not a predicate flaw; the frozen predicate must not change.
5. Residual R2 — the cell's prose claims more than its named command measures. The capability text asserts "stable
   special-file refusals", but the fixture only builds FIFOs (`mkfifo "$t"` at :197, `mkfifo "$d/inner.fifo"` at :211);
   no socket, device or symlink target case exists. E5 shows a mutant that accepts a socket (staging it as SAFE and
   emitting an `rm -rf` step) still scores 5/5 with rc=0, so the item cannot detect that capability loss. Under the
   frozen enumeration the item is (command, stated outcome) = (`bash tests/fixtures/r13-quarantine-bounds.sh`, 5/5), so
   this is a claim-strength gap in the row's prose, not a K03 mismatch.
6. Currency trend is real, not inherited: the tool changed 9 commits since 2026-10-01
   (`git log --oneline --since=2026-10-01 -- tools/souji-quarantine.sh | wc -l` = 9) and still prints 5/5; the row's
   claim survived 20 rounds of tool movement.

## Attack log
- A1 "a regressed tool still passes the predicate" → **REFUTED**. Baseline (unbounded) tool: exit 1, `failed=4 hung=2`
  (E3). HANG increments `FAILED`, so a bounded-but-hanging regression also fails the exit gate.
- A2 "predicate is stricter than the cell" → **REFUTED**. `total=5 ∧ failed=0 ∧ exit 0` ≡ 5/5 for this command;
  no correct-tool output fails it in the default environment (E1).
- A3 "predicate is laxer than the cell's prose (stable special-file refusals)" → **REPRODUCED** as residual R2:
  mut2 (sha256 `ffec268…`) passes 5/5 while staging a socket. Classification: cell-prose overshoot, out of the item's
  frozen (command, stated outcome) pair; no predicate or item change is proposed.
- A4 "verdict is environment-dependent" → **REPRODUCED** as residual R1: identical bytes exit 1 and print no SUMMARY
  under read-only `/var/tmp` (E4). Same classification: residual, no amendment requested.
- A5 "the cited record is stale" → **REFUTED**: both r13 pins match committed bytes (E6), and the red arm reproduces
  the recorded lines byte-for-byte on identical fixture bytes (E3).
- A6 "shared host /var/tmp leaves residue" → **NOT SUSTAINED**. I observed one `/var/tmp/r13-qbounds.*` entry
  immediately after the red run, gone on re-check, and 0 after every pass run; a probe of the same fixture bytes with
  its scratch template relocated into my own tree cleaned up on the red path (probe rc=1, 0 leftovers). Attribution to a
  concurrent peer run of the same fixture is `[INFERENCE]`.

**Verdict: HOLDS** (deterministic, faithful to the stated outcome; residuals R1/R2 reported, predicate untouched).

## Deliveries
- `.ufo/waves/round-33/w1/SwarmCritic03.md` (this file)

Scratch `/fast/scratch/hyaku/souji-r33/AuditK03` removed after copying receipts. No lane file, git index, jj state or
path outside `souji-shokunin` was written; no tool installed or upgraded this seat.
