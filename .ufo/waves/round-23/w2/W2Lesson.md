# W2Lesson — falsify corpus/lessons/round-23.md (Mistakes rows M1–M8 + Gate quotes)

author: L1Souji23.W2Lesson (leaf seat, round 23 w2)
date: 2026-10-25; lane tip `102690017115cb202f292828c90b72705f69bf09`
scope read: `.ufo/waves/round-23/preregistration.txt`, `corpus/lessons/round-23.md`, every named
receipt/fixture/snapshot, plus the wave-1 seats each row cites. Read-only seat: no lane write
outside this file; no git/jj mutation; scratch under `/var/tmp/souji-r23-w2-Lesson/` (removed).
No installs. Certification OFF, K5 HELD; no credentials, no /proc, no operator-sweep contents.

## Status

**FALSIFIED in part** — the artifact survives on 6 of 8 rows, but its C1 after-state is
unsupported at the tip and two Mistakes rows (M3, M7) carry clauses the bytes at the tip
contradict. Per-row verdicts below; each finding names the file/line, the command, and the
required action (fix / disclose / accept).

The assignment named lane commits `4765250` and `c0eeaa7`; the actual tip is `1026900`
("runner decode hardening"), which changed `tools/souji-receipt-run.py` after every receipt
was produced (tip blob sha256 `6bb623b8…` vs the `0d36ce98…` the receipts bind). Every
receipt still verifies at its own `rev=` (all five `verify=ok` below), so C2's design holds.

## Row-by-row verdicts

| row | verdict | witness can fail? | pointer resolves at tip? |
|---|---|---|---|
| R23-M1 (D1 uncommitted wave files) | survives | yes — base control 23 K4 rows | yes |
| R23-M2 (D2 unbound after-state) | survives (see F1) | yes — K1 receipt-absent + value-disagree both fire | yes |
| R23-M3 (D3 stale digest) | **falsified** (F2) | yes — refusal re-run exits 2 | partially — transcript is a placeholder |
| R23-M4 (D4 single-site sweep) | survives | yes — tally-disagree + class-absent (self-tested, F9) | yes |
| R23-M5 (D5 superseded numbers) | survives | yes — 3× K2 uncorrected at base | yes |
| R23-M6 (D6 overbroad reject) | survives with finding (F10) | no executable witness | yes |
| R23-M7 (D7 no criterion) | **falsified** (F4, F5) | yes — 0 bad / 6 bad / selftest 2/2 | evidence clause false at tip |
| R23-M8 (scope, `__pycache__`) | survives with finding (F3) | yes — base control `__pycache__` row | yes |

## Findings (by severity)

### F1 — HIGH: the C1 after-state has no receipt at the final bytes

`corpus/lessons/round-23.md:21` claims "After: `0` (`census/round-23/records/agreement-after.tsv`)".
The cited file says otherwise:

```
$ head -20 census/round-23/records/agreement-after.tsv
receipt=v1
rev=476525026cdb179f2d49441e1cb6c6f7316f3124
rc=1
--- stdout ---
MISMATCH	K1	SCORECARD.md:14	value-disagree	assertions=55 resolved=52 skipped=33 mismatches=3 != receipt assertions=63 resolved=63 skipped=40 mismatches=0 at 9301d98c…
keys=4 records=4 occurrences=18 mismatches=1
```

The K1 defect was real at `4765250`; `SCORECARD.md:14` gained the `at 4edb25df…` token at
`c0eeaa7` (`git diff 4765250 1026900 -- SCORECARD.md` word-diff: `+at \`4edb25df…\``), and K1
passes at tip — but **no receipt binds the fixed bytes**: the only after receipt records `rc=1,
mismatches=1`. The same line cites `…/agreement-after.txt`, which does not exist (actual: `.tsv`),
and `SCORECARD.md:21` repeats the nonexistent `.txt` path with `mismatches=0 at the landing tip`.
Under the round's own new Q55 a quoted count must name a receipt binding revision and tool digest;
`0` has none. — Action: **fix** (regenerate `agreement-after` at the tip, commit it, correct both
`.txt`→`.tsv`, or record after=`1` at `4765250` with the fix commit named).

### F2 — MEDIUM: R23-M3's "unrecoverable" is contradicted by the seat it cites

`round-23.md:64` fix column: "the before-state is reported unrecoverable rather than
reconstructed (`ExecGateReproduce`, `RevD3`, `RevGateHistory` agree)". But
`.ufo/waves/round-23/w1/ExecGateReproduce.md:42` is literally headed "Before-state reconstruction
(the only state that yields the recorded number)" and reproduces `fail=10` with ten verbatim
lines under blob `4309d769` (`a211e4d`). `RevGateHistory.md:120` agrees only that "the fail=10
state exists only as prose" — i.e., no **receipt**, not that the state is unrecoverable. The
state is deterministically reconstructible from committed bytes (tool@`a211e4d` + r22 corpus).
The evidence clause "the `fail=10` before-state exists in no commit" is therefore also wrong
read literally. — Action: **fix** wording to "no before receipt exists; recoverable only under
the `4309d769` blob the frozen C2 rule forbids".

### F3 — MEDIUM: R23-M8's "every later run uses `python3 -B`" is false

SimplTouched's bytecode write was at 05:12:51 (-0300) = 08:12:51 UTC. Three committed receipts
were produced *after* it with no `-B` in argv: `declared-evidence-after.tsv` (`utc=08:12:53Z`,
two seconds later), `gate-check-at-first-landing.tsv` (`08:14:08Z`), `gate-check-at-lane-base.tsv`
(`08:18:48Z`). `grep -n '\-B\|PYTHONDONTWRITEBYTECODE' tools/souji-receipt-run.py` → no match: the
runner does not force it. The runs happen in the private `/var/tmp` clone, so the lane tree was
never at risk — the policy that matters holds, but the universal as written is falsified. —
Action: **fix** to "every later lane-tree run uses `-B`; the receipt runner should force
`PYTHONDONTWRITEBYTECODE=1`" (or add the flag to the runner).

### F4 — MEDIUM: R23-M7's evidence clause "`corpus/QUALITY.md` was unchanged base→tip" is false at tip

`git diff --stat 1208bfb 1026900 -- corpus/QUALITY.md` → `7 +++++++` insertions (the Q54/Q55
criteria, landed `c0eeaa7`). A reader resolving the pointer at the tip finds a changed file. The
truthful statement is "unchanged through `1208bfb`; Q54/Q55 land this round". — Action: **fix**
wording; cite the commit where the change landed.

### F5 — MEDIUM: Q54 is not carried by the tool it names, and its own check command fails on the corpus

`corpus/QUALITY.md:128` lists `tools/souji-gate-check.py` as the criterion's carrier. That tool
does read the named snapshot — but only to check that the *quote* appears in it
(`check4-quote-absent-from-snapshot`, lines 98–112) and that the snapshot exists under
`--snapshot-dir`; the `§` locator itself is checked only for *shape* (`LOCATOR_RE`, lines 42,
87–89). No code path resolves the `§ <NAME>` heading against snapshot bytes — exactly the gap
M17 named. The only heading resolver is `tests/fixtures/r23-locator-heading.py`, invoked by
nothing (`grep -rn r23-locator-heading` → only QUALITY.md, the fixture, the lesson, the draft).
Worse, Q54's own documented check command fails on the corpus it claims to govern:

```
$ python3 -B tests/fixtures/r23-locator-heading.py --entries corpus/knowledge/*.md \
    --snapshot-dir census/round-23/sources ; echo exit=$?
LOCATOR-BAD … 'DESCRIPTION' appears in none of: census/round-22/attempt2/sources/man7-mv.1.txt …
entries=12 locators=20 locators_bad=17
exit=1
```

The fixture's `snapshot_texts()` joins `--snapshot-dir` with `os.path.basename(rel)` and stores
`""` on OSError, so every round-22 entry's snapshot list resolves to empty text and every
locator is reported bad — including `DESCRIPTION`, which *does* appear in
`man7-mv.1.txt:29,60`. So the criterion's own command reports 17 bads, several of them false
positives from the basename/OSError path. — Action: **fix** (wire the check into gate-check or
scope the criterion's command per-entry-snapshot-dir; fix the OSError empty-text path) or
**disclose** that Q54 currently applies only to entries whose snapshots live under one dir.

### F6 — MEDIUM: the Gate's "with their sha256" is not recorded anywhere

`round-23.md:76`: "the man-page snapshots are committed under `census/round-23/sources/` with
their sha256". `sha256sum` of the five files: `4c540915…` (count-objects), `8ef1170b…` (fsck),
`5282b2e1…` (prune), `7d2298c1…` (qiita), `96aecd91…` (csdn). `grep -rn` for any of these in
committed lane bytes → **zero** (only the *fetched-page* digests `2020b283…`/`5a8b27ed…` appear,
in `count-objects-garbage-readings-r25.md:59`, and those are digests of the full pages, not of
the committed extracts). No reader can verify the snapshot bytes from any committed digest. —
Action: **fix** (record the five snapshot digests in the entry Gate blocks or a
`census/round-23/sources/SHA256` file) or **disclose** the claim to "fetched-page digests for
the two community pages".

### F7 — LOW: two of the lesson's five Gate quotes (and two entry quotes) are not contiguous byte strings

Strictly verbatim (`q in text`), S115's `garbage:` quote and S116's `--lost-found` quote fail:
each is split by the man-page soft wrap (a `\n\t` intervenes at `git-count-objects.1.txt:30-31`
and `git-fsck.1.txt:71-72`). Two further ADMIT quotes inside
`corpus/knowledge/repo-size-census-readonly.md`'s Gate (`alternate:`, `prunes all unpacked
objects…`) are wrapped the same way. S117's `-n` quote, S118's `6700` quote and S119's
`无法被 Git 识别的垃圾文件大小` are contiguous. Every quote passes the gate's own `squash()`
normalization (`tools/souji-gate-check.py:107-112`), which is why `fail=0` — so this is a
presentation defect only: the lesson prints them as single-line strings without noting the
wrap. — Action: **accept** with a "quoted modulo man-page wrap" note, or quote the wrapped
fragment.

### F8 — LOW: "eight cases require a nonzero mismatch" — actually seven

`tests/fixtures/r23-record-agreement.py` (re-run, `selftest=9/9`, `control=FALSE-GREEN-REJECTED`):
cases 2–8 require nonzero; cases 1 and 9 require zero. `round-23.md:22` says eight. —
Action: **fix** "eight"→"seven".

### F9 — LOW (survives, disclosure): R23-M4's second arm is implemented but not exercised by the committed fixture

The fix names two failure modes; the fixture's 9 cases cover only `tally-disagree`. The
`class-absent` arm exists (`tools/souji-record-agreement.py:272-274`) and fires on my own test —
minimal git repo under `/var/tmp`, `2 **present**, 1 **unverifiable**` → `one **unverifiable**`:

```
MISMATCH	K3	corpus/lessons/round-22.md	class-absent	no occurrence of unverifiable
keys=4 records=4 occurrences=16 mismatches=1  (exit 1)
```

— Action: **disclose** (or add case 10); the arm is demonstrated here.

### F10 — LOW: R23-M6's fix has no executable witness, and its witness lives outside the lane

`round-22.md:486-492` supplies a prose witness pointing at
`/home/vgpnk/Projects/shokuknow/merge/souji/…/quarantine-staging-no-copy-r24.md` — outside this
repository, which the prereg's own REJECT rule declares unresolvable from lane bytes. The
correction itself (entry-level reason + named delta + not-yet-met flip) resolves at tip and is
append-only (filed text preserved at line 338). — Action: **disclose** that M6 is closed by
prose, or bind the correction to a lane-resolvable artifact.

## Verified evidence per row (commands I ran)

- **M1** — 7 wave-22 paths all `COMMITTED` at tip (`git cat-file -e`); fleet report line 98 does
  say "none uncommitted"; base control `grep -c 'MISMATCH\tK4' = 23` ✓; both evidence digests
  re-derived equal committed bytes (`9b343c6c…` tsv, `5899dd50…` counts).
- **M2** — `declared-evidence-after.tsv` re-derived byte-exact:
  `python3 -B tools/souji-declared-evidence.py --rev 9301d98… --file SCORECARD.md` →
  `assertions=63 resolved=63 skipped=40 mismatches=0`; tool sha256 `65817d0d…` = blob at 9301d98.
  K1 `receipt-absent` fires at base control; `value-disagree` fires at `4765250`.
- **M3** — refusal re-run: forged receipt (`tool_sha256=5b8025a8…` over
  `gate-check-at-lane-base.tsv`) → `RECEIPT-TOOL-DIGEST-MISMATCH receipt 5b8025a83f16 != tree
  d5ed0805b10f at 1208bfb…`, `exit=2`, byte-identical to `refusal-stale-digest.txt`. Both cited
  receipts (`gate-check-at-lane-base` `d5ed0805@1208bfb`, `gate-check-at-first-landing`
  `d85c2696@a211e4d1`) `verify=ok`. But see F2.
- **M4** — base control's two K3 rows reproduce (`README.md:440` `1 present != 2 present`,
  `1 refused != 0 refused`); README now reads `2 present, 0 refused` ✓; class-absent arm proven (F9).
- **M5** — `LOG.md:1524-1541` "Round22 attempt2 corrections" names both cells under `superseded
  by` (tuple and the `1 present`/`1 refused` pair); 3× `K2 uncorrected` reproduce at base.
- **M6** — correction present at `round-22.md:467-492`, append-only, names
  `RENAME_EXCHANGE`/`RENAME_WHITEOUT`, the budget/`mv --no-copy` reason, and a flip. No
  executable witness (F10).
- **M7** — fixture reproduces exactly: real entries `locators=11 locators_bad=0`; mutant
  `locators_bad=6`; `selftest=2/2`. M17/M19/M21 `captured-by: none` confirmed in
  `round-22.md`; M22's row does name `QUALITY Q1/Q2` ("overstated" clause ✓). But F4/F5.
- **M8** — `tools/__pycache__` absent from tree and worktree at tip; base control's K4 row names
  it; no `.gitignore`. But F3.

## Counters re-derived independently

- Base control: `python3 -B tools/souji-record-agreement.py --rev 1208bfb… --root . --no-worktree`
  → `keys=4 records=3 occurrences=13 mismatches=6` — byte-identical to `agreement-control-base.txt`.
- `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l` → `5`; all five `verify=ok`.
- Registry `grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `119`
  (base `114`) ✓; `sources-census.sh validate … souji` → exit 0, `W04`=30, `E`=0 ✓.
- C3 gate re-run → `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`, exit 0 ✓.
- Fixtures: `r23-record-agreement.py` `selftest=9/9` `control=FALSE-GREEN-REJECTED`;
  `r23-receipt-run.py` `selftest=8/8`; `r23-locator-heading.py` `selftest=2/2`.
- S118's "`count-objects` occurs zero times" ✓ (grep 0); man snapshot footer `Git 2.56.0` ✓
  (installed `git version 2.56.0`).

## Live-worktree observation (transient, not a row defect)

At my first tip run (`08:4x UTC`) K4 reported `MISMATCH K4 .ufo/waves/round-23/report-draft.md
uncommitted-path ??`; by `08:55` the porcelain set had grown to `M` `W2D1.md`/`W2Lesson.md`/
`W2Q54.md`/`repo-size-census-readonly.md` and `??` `W2Sources.md`,
`tests/fixtures/__pycache__/` (`r23-locator-heading.cpython-314.pyc`, 05:53 — not mine: every
fixture run of mine carried `-B`, and direct script execution never caches itself; most likely a
sibling's `py_compile`/import), plus `census/operator-sweep-20261019/` (exempted). All are
concurrent wave-2 artifacts, not landed defects — but the round's `mismatches=0` after-state is
not observable in the live worktree until w2 seat reports are committed and any stray pycache is
removed or exempted; flag for the landing gate.

## Residual risk / verification gaps

- No LSP device mounted; definition/caller checks done by direct reads and executions.
- Page "last updated" claims (S115's `2.51.1`, S116's `2.53.0`, S117's `2.43.0`) unverified —
  snapshots are committed but the live pages were not re-fetched in this seat.
- MutCounter/MutReceipt mutant inventories (the "12/12 mutants" and residual-call claims) not
  re-derived — outside my assigned slice; W2C2Verify owns C2's counter claims.
- `agreement-after.tsv`'s `occurrences=18` vs my tip run's `occurrences=17` is explained by the
  SCORECARD token fix (one fewer K1 occurrence? — actually the K4 `report-draft.md` row changes
  the count); the counts are consistent with the tool's own output on each rev.

## Tooling

No installs, no upgrades, no pacman transactions (host pause observed). All commands read-only
(git log/diff/show/grep/cat-file/status, sha256sum, grep, sed on scratch only, the lane's own
tools and fixtures). Scratch `/var/tmp/souji-r23-w2-Lesson/` removed before finishing.

**Verdict:** the artifact's *mechanism* is sound — every named witness can and does fail — but
its *record* is not: F1 leaves C1's after-state unsupported by any receipt at the tip, F2
mischaracterizes a reconstructed state as unrecoverable, and F4/F5 let the round's own new
criterion fail on the corpus it governs. `falsified` on M3, M7 (partial), and the C1 after-state;
`survives` on M1, M2, M4, M5, M6, M8, and every named witness.
