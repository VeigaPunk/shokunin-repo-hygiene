# W2Log — attack on LOG.md's Round23 entry (wave 2, falsify)

Target artifact: `LOG.md:1561-1620` (Round23, committed at `1026900`).
Lane tip at read: `102690017115cb202f292828c90b72705f69bf09`; round commits `4765250`, `c0eeaa7`.
Every check below is a re-run of the claim's own counter or an open of the named artifact.
Scratch (`/var/tmp/souji-r23-w2-W2Log`) removed; no repo mutation.

**Measurement base.** The live worktree moved while this seat read it (wave-2 siblings editing
`LOG.md`, `SCORECARD.md`, `corpus/README.md`, `corpus/lessons/round-23.md`, the tools and the
fixtures), so every finding is stated against `git show 1026900:<path>` bytes, and the quoted
LOG line numbers are those of the committed file (verified identical to the tree at read time).
Reproductions used the **committed** instrument, extracted with
`git show 1026900:tools/souji-record-agreement.py`, whose sha256 is
`617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9` — the same digest the
receipts record as `tool_sha256`, so the counter ran against exactly the bound bytes.

**Verdict: falsified.** The entry survives on the wave tally, the C2 counter, the C3
registry/entry numbers, and D1/D2/D3/D4/D5/D6/D8 — but it fails on five numeric/path claims
(C1 control, C1 after + receipt path, fixture case count, C2 receipt revision, C3 F2 framing),
one evidence claim (snapshot sha256) and one citation claim (Q54's cited lesson rows).

## Axes

- A1 record agreement: does each number equal the committed receipt's own counts line?
- A2 citation resolvability: does each named path exist at the lane tip?
- A3 reproducibility: does the claim's own command reproduce the number today?

## Findings, by severity

### F1 — HIGH, falsified. C1 after-state: cited receipt does not exist, and the receipt that does exist records the opposite.

`LOG.md:1577-1578` — "After: mismatches=0 at the landing tip (receipt
census/round-23/records/agreement-after.txt)".

- Path: `census/round-23/records/agreement-after.txt` exists at no round commit.
  `git ls-tree -r --name-only 1026900 census/round-23/records/` lists
  `agreement-after.tsv` and no `.txt`; same at `c0eeaa7` and `4765250`.
- Content of the file that does exist (`census/round-23/records/agreement-after.tsv`):
  ```
  rev=476525026cdb179f2d49441e1cb6c6f7316f3124
  rc=1
  MISMATCH K1 SCORECARD.md:14 value-disagree assertions=55 resolved=52 skipped=33 mismatches=3 != receipt assertions=63 resolved=63 skipped=40 mismatches=0 at 9301d98c…
  keys=4 records=4 occurrences=18 mismatches=1
  ```
  It binds the **pre-repair** revision `4765250`, records **mismatches=1, rc=1**, and its K1
  line is exactly the disagreement the C1 claim says is repaired.
- Reproduction with the committed tool blob (`sha256 617f4c96…`, extracted from `1026900`):
  `python3 -B tool.py --root . --rev 102690017115cb202f292828c90b72705f69bf09` → the single K4 hit
  `.ufo/waves/round-23/report-draft.md` (a wave-2 draft, mtime 05:37, written after the tip
  commit), `keys=4 records=4 occurrences=17 mismatches=1` rc=1. With `--no-worktree`:
  `keys=4 records=4 occurrences=17 mismatches=0`. At `4765250` (`--no-worktree`):
  `keys=4 records=4 occurrences=18 mismatches=1` — exactly the receipt's line.
- So the number 0 is reachable only on the revision-scoped arm at the tip and **no committed
  receipt binds it**; the LOG neither names the arm nor cites the receipt that records 1.
- Same defect in two other committed artifacts at the tip: `SCORECARD.md:21` ("`mismatches=0` at
  the landing tip (`census/round-23/records/agreement-after.txt`)") and
  `corpus/lessons/round-23.md:21` ("After: `0` (`census/round-23/records/agreement-after.txt`)",
  continuing on line 22). The path error is systematic across three files, not a typo in one.
- Round must **fix**: either re-run the instrument at the landing tip and commit a receipt with
  `rc=0` (and cite that `.tsv`), or state "revision-scoped arm, `--no-worktree`" and cite
  `agreement-after.tsv` with its real content. This is the D2 defect class (no receipt binds the
  named revision) recurring inside the artifact that claims to close it.

### F2 — HIGH, falsified. C1 control number is 6, not 20.

`LOG.md:1575-1576` — "Control (do nothing) = the same tool bytes at base: keys=4 records=3
occurrences=13 mismatches=20, rc 1 (receipt census/round-23/records/agreement-control-base.txt)".

- The cited receipt, `census/round-23/records/agreement-control-base.txt:14` at the tip, reads
  `keys=4 records=3 occurrences=13 mismatches=6`.
- Reproduced with the committed tool blob (`617f4c96…`):
  `python3 -B tool.py --root . --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd --no-worktree`
  → the same six MISMATCH lines (K1 receipt-absent, K2×3, K3×2) and `mismatches=6`, rc=1.
- 20 is the **pre-hardening** instrument's reading: `.ufo/waves/round-23/w1/CritPrereg.md:35`
  records "333-line bytes : … mismatches=20 rc=1", and the 350-line/`--no-worktree` variant at
  line 37 gives 6. The committed instrument is `617f4c96…`, whose reading is 6.
- The round's own artifacts disagree among themselves: `SCORECARD.md:21` and
  `corpus/lessons/round-23.md:20` say 6; `corpus/README.md:456` says 20. LOG and README are the
  stale pair.
- Minor in the same sentence: the cited receipt is `plain-v1` with **no `rc=` field**; "rc 1" is
  true of the live run but is not in the receipt the sentence cites.
- Round must **fix** LOG:1576 to 6 (and README:456, or the two will keep disagreeing).

### F3 — MEDIUM, falsified. The fixture has 9 cases, not 8, and it does not currently pass them all.

`LOG.md:1578-1580` — "The instrument's own fixture tests/fixtures/r23-record-agreement.py kills an
always-zero emitter on eight cases."

- `tests/fixtures/r23-record-agreement.py:418-429` at the tip — `CASES` has **9** rows
  (`git show 1026900:tests/fixtures/r23-record-agreement.py` → 9 tuple rows):
  `repaired`(False), `receipt-absent`(True), `counts-disagree`(True), `rev-disagree`(True),
  `uncorrected-log`(True), `filed-deleted`(True), `tally-wrong`(True), `dirty-unexempted`(True),
  `exempted-dirty`(False). Fail-expecting rows = **7** (cases 2-8), which the source's own comment
  at line 419 states ("the always-zero control is cases 2-8").
- The recorded run at the final instrument bytes is **8/9**: `.ufo/waves/round-23/w1/ExecFixtureAgreement.md:6,24-34`
  shows `case=4 … -> FAIL` and `selftest=8/9` (the earlier 9/9 was at a different instrument
  sha256, line 39; the mutant is 2/9, line 48).
- `SCORECARD.md:21` claims "9/9", contradicting the seat's own transcript.
- Round must **fix** the count in LOG and **disclose** the 8/9 (case 4 `rev-disagree` reports
  `K1/occurrence-absent`), or repair case 4.

### F4 — MEDIUM, falsified. C2's `record-agreement@<tip>` binds 4765250, not the tip.

`LOG.md:1587-1589` — "0 before, 5 after (declared-evidence@9301d98, gate-check@a211e4d,
gate-check@1208bfb, record-agreement@<tip>, gate-check@<C3 tip>)".

- Count and identity are right: `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l` → **5**
  at the tip and **0** at base (`git grep -lE … 1208bfb -- census/ | wc -l` → 0). The five files
  and revisions are `declared-evidence-after.tsv`@9301d98, `gate-check-at-first-landing.tsv`@a211e4d,
  `gate-check-at-lane-base.tsv`@1208bfb, `agreement-after.tsv`@**4765250**, `gate-check-c3.tsv`@**4765250**.
- "`<tip>`" therefore names a revision that is not the tip (`1026900`), and that receipt is the
  failing one from F1 (rc=1). "`<C3 tip>`" is defensible (the C3 work landed at 4765250).
- All five verify: `python3 -B tools/souji-receipt-run.py verify --root . <receipt>` → `verify=ok …`
  rc=0 for each. Refusal reproduced live on a synthesized stale digest
  (my copy of `gate-check-at-lane-base.tsv` with `tool_sha256=5b8025a83f16…`):
  `RECEIPT-TOOL-DIGEST-MISMATCH receipt 5b8025a83f16 != tree d5ed0805b10f at 1208bfb…`, rc=2 —
  matching `LOG.md:1590` and `census/round-23/records/refusal-stale-digest.txt:4-5`.
- Round must **fix** the label (`record-agreement@4765250`, and note rc=1) — the C2 claim itself
  survives.

### F5 — MEDIUM, falsified. C3's premise: F2 already held an entry before this round.

`LOG.md:1594-1595` — "One assimilation theme on F2 (repository size census), the lane's only
frontier row that held no entry".

- At base, `corpus/README.md:40` does say "F2 repository size census | frontier, no entry (r12
  candidate deferred …)" — but line 64 of the same base file reads
  "## Round 13 current coverage (**supersedes the r12 F2 row**)" and the table under it lists
  `knowledge/git-repo-structure-readonly.md` (S035/S036/S037) as F2's entry.
- The round's own `SCORECARD.md:23` states the correct before: "registry 114 rows; **F2 held one
  entry (`git-repo-structure-readonly.md`)**", and the round's own README edit (line 68) says
  "**the read side now holds three entries** (git-repo-structure-readonly.md,
  repo-size-census-readonly.md, count-objects-garbage-readings-r25.md)".
- LOG therefore contradicts both the superseding README table and the SCORECARD row written in the
  same round. (The prereg's identical wording is frozen and not re-opened; the LOG repeats it as a
  fact about committed bytes, which is what fails.)
- Round must **fix** the sentence to "F2's r12 row said no entry, superseded in round 13; the read
  side now holds three entries".

### F6 — MEDIUM, unsupported. No sha256 exists for the man-page snapshots.

`LOG.md:1597-1598` — "installed git 2.56.0 man pages snapshotted under census/round-23/sources/
with sha256, plus two community pages fetched live".

- `census/round-23/sources/` holds `git-count-objects.1.txt`, `git-fsck.1.txt`,
  `git-prune.1.txt`, `qiita-gc-auto.raw`, `csdn-count-objects-vh.raw`.
  `grep -rn sha256 census/round-23/` returns only the five `tool_sha256=` receipt lines —
  no digest for any of the three `.1.txt` files.
- `corpus/knowledge/repo-size-census-readonly.md:72-84` cites the snapshots by path only, with no
  digest. The two community pages *do* have sha256 (`corpus/knowledge/count-objects-garbage-readings-r25.md:59`:
  qiita `2020b283…`, csdn `5a8b27ed…`), so "with sha256" is true of the fetched pages, not of the
  man pages.
- Round must **fix**: record the three snapshot digests (receipt or Gate line), or drop "with sha256".

### F7 — LOW, falsified. Q54 cites M17 only, not M17/M19/M21.

`LOG.md:1610-1612` — "D7: QUALITY Q54 … citing round-22 M17/M19/M21".

- `corpus/QUALITY.md:128` (Q54) citation cell: "`corpus/lessons/round-22.md` R22-M17
  (captured-by: none); round-22-verifier-spotcheck.md §6 D7; the r22 candidate's reject reason".
  M19 and M21 are not cited. M19 (`.ufo/…` no — `corpus/lessons/round-22.md:406`) and M21
  (line 424) exist but are not referenced by Q54.
- Round must **fix** the citation list to M17 (or add M19/M21 to Q54 if they are meant to be
  grounded there).

### F8 — LOW, unverified. "plus a residual reviewer call" has no committed seat record.

`LOG.md:1617` — "41 seats (…) dispatched as one task call from .ufo/waves/round-23/w1-spec.json,
plus a residual reviewer call."

- `w1-spec.json` items = 41; `.ufo/waves/round-23/w1/swarm-registry.json` members = 41, all
  `kind=spawn`; `.ufo/waves/round-23/w1/` holds 41 reports (one filename differs from the registry
  name: report `ConnSiblingSources.md` vs member `ConnectorSiblingSources`). No artifact names a
  42nd seat, and no file records the residual call.
- If a residual reviewer really ran, the tally is 42 or the registry is incomplete; if not, the
  clause is false. Round must **disclose** which, or drop the clause.

## Verified — no divergence

- **Wave tally and role split** (`LOG.md:1614-1616`): 41 seats; `Counter` over
  `w1/swarm-registry.json` and `w1-spec.json` gives exactly 9 scout, 9 scribe, 9 reviewer,
  4 critic, 3 executor, 2 revenger, 2 mutation-tester, 1 connector, 1 sentinel, 1 simplifier
  (sum 41). ✓
- **Policy path**: `scripts/hyaku/ufo-wave-policy.json` resolves at the fleet root
  (`/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy.json`); the lane has no
  `scripts/`, and earlier rounds' entries use the same fleet-root-relative form (LOG:946, 1515).
  Accepted convention, not a divergence.
- **C2 counter and verifier** (except F4's label): 0 → 5, all five `verify=ok` rc=0, stale-digest
  refusal rc=2 reproduced live. ✓
- **C3 registry/entries**: `corpus/SOURCES.md` 114 rows at `1208bfb`, 119 at the tip, 0 duplicate
  ids; S115-S117 → `repo-size-census-readonly.md`, S118-S119 →
  `count-objects-garbage-readings-r25.md` exactly as stated. `sources-census.sh validate` →
  `souji ok …`, exit 0 (only pre-existing W04 duplicate-url warnings for S098/S099/S106/S108).
  `gate-check-c3.tsv` (rev `4765250`, `verify=ok`) records `entries=2 ok=2 slice_verdicts=0
  slice_total=0 fail=0`, matching "gate `entries=2 ok=2 fail=0`". ✓
- **D1**: the seven inherited round-22 leftovers are all present at the tip
  (`CritC1Axis.md`, `DraftScorecard.md`, `ImplDeclaredA.md`, `evidence/CritC1Axis.md`,
  `evidence/DraftScorecard.md`, `evidence/impl-a/head-c9f1fe3.counts`, `…tsv`), committed at
  `4765250`. ✓
- **D2**: `declared-evidence-after.tsv` binds `assertions=63 resolved=63 skipped=40 mismatches=0`
  at `9301d98c1c689c79741f0f1ba1f171138d20af07`; `SCORECARD.md:14` names that same full rev. ✓
- **D3**: correction 3 exists (LOG:1543-1552) and records the before-state as unrecoverable. ✓
- **D4**: `corpus/README.md:440` now reads "5 accepted …, 2 present, 0 refused, 1 unverifiable",
  matching `census/round-22/attempt2/slice-verdicts.tsv`. ✓
- **D5**: the three-correction block exists at LOG:1524-1552 ("superseded by" at 1533, 1541). ✓
- **D6**: `corpus/lessons/round-22.md:462` "Attempt 2 — round-23 correction to one reject reason
  (D6)" with the corrected entry-level reason at 466-486. ✓
- **D8**: the D8 note (stray backtick, digest-bound, count unaffected) exists at LOG:1553-1556. ✓

## Residual risk and verification gaps

- **K4 is live-worktree state.** My tip run's single mismatch is
  `.ufo/waves/round-23/report-draft.md`, mtime 05:37 (after the tip commit), i.e. a wave-2 draft,
  not a round artifact. The LOG's K4 arm cannot be settled from committed bytes; its own named
  limit (LOG:1591-1592) is honest about this. If the round wants a K4=0 receipt it must be taken
  at a moment when no sibling is writing, and the receipt should say so.
- **`verify` binds the digest, not the outcome.** `agreement-after.tsv` verifies `ok` while
  recording `rc=1` — so C2's verifier would accept a receipt whose recorded run failed. This is
  disclosed by the LOG's named limit ("a typed receipt passes verify") and is not a new finding,
  but it is why F1 slipped through: a green `verify` was mistaken for a green after-state.
- **Not run**: I did not execute `tests/fixtures/r23-record-agreement.py` (it writes to
  `/var/tmp/souji-r23-ExecFixtureAgreement`, outside this seat's scratch bound); the 9-case table
  is read from source and the 8/9 from the seat's committed transcript.
- Cross-artifact note: `SCORECARD.md:21` and `corpus/lessons/round-23.md:21` carry F1's wrong path
  and `corpus/README.md:456` carries F2's `mismatches=20`. Fixing LOG alone leaves the round's
  three records disagreeing about its own C1 numbers.
