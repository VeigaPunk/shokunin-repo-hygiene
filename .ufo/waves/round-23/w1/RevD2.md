# RevD2 — routed defect D2 (r22 C1 after-state receipt binding)

Lane base and read revision `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (= HEAD, `git rev-parse`).
Sources read: `corpus/lessons/round-22-verifier-spotcheck.md` §6 (D2) / §2 (its evidence),
`.ufo/waves/round-23/preregistration.txt` (C1/K1), `SCORECARD.md` at base, the round-22 report at
fleet root, and the draft instrument `tools/souji-record-agreement.py` (untracked, L1-owned).

## Status

STATUS: PASS — D2 is **real as a binding defect and closed nowhere at the lane base**; the value half
of the spot-check's suspicion is **overstated** (the after 4-tuple re-derives exactly, twice, from
committed bytes). The round's planned K1 repair **does not close D2** as drafted: K1's per-line value
clause demands the *control-end* tuple equal the *after* receipt, which is unsatisfiable, and no wave
item emits the receipt K1 reads. Append-only alternative for the report-token half is given below.

## Evidence

### E1 — the one-command reproduction (D2's first half)

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -nE 'rev=9301d98|resolved=63 skipped=40' HEAD -- census/
$ echo rc=$?
rc=1
```
Empty: **no committed byte under `census/` binds `9301d98` or quotes the after tuple.** Two independent
confirmations:

```
$ git grep -lE '^rev=[0-9a-f]{40}$' HEAD -- census/          # any receipt with a rev= header at all
(no output)                                                   # = C2's declared before-target of 0
$ git cat-file -e 9301d98:census/round-23/records/declared-evidence-after.tsv
fatal: path 'census/round-23/records/declared-evidence-after.tsv' does not exist in '9301d98'
$ git ls-tree -r --name-only HEAD -- census/round-23 | wc -l
0
```

The only committed occurrences of the after tuple are the record itself and the spot-check quoting it:

```
$ git grep -n 'resolved=63 skipped=40' HEAD -- .
HEAD:SCORECARD.md:14:| calibration | 7 | R22 **attempt 2** ... tip 9301d98c1c689c79741f0f1ba1f171138d20af07 `assertions=63 resolved=63 skipped=40 mismatches=0` ...
HEAD:corpus/lessons/round-22-verifier-spotcheck.md:114:assertions=63 resolved=61 skipped=39 mismatches=2 rc=1` (`ResClaims.md:24`). SCORECARD names `9301d98` ...
```

### E2 — the after tuple is reproducible at the named revision (contra the spot-check's inference)

The spot-check explicitly did not run the lane tool (§preamble: "did not execute either lane tool"), so
its "the *exact* after figure does not [survive]" is an absence-of-receipts inference. It is wrong about
the number. The tool blob is identical at `9301d98`, `77d6595` and HEAD (`git rev-parse` →
`c6b150438299b2036c9acf5ca73924bc7768644d`, sha256 `65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4`,
i.e. the digest `census/round-22/attempt2/instrument-digests.txt` already pins):

```
$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev 9301d98c1c689c79741f0f1ba1f171138d20af07 --format counts
assertions=63 resolved=63 skipped=40 mismatches=0
rc=0
$ ... --rev 77d659524c777276bcef33568be3c4cbcb9d1052 --format counts
assertions=63 resolved=63 skipped=40 mismatches=0
rc=0
```

So the defect is **not** a wrong number; it is (a) no receipt, and (b) two records naming two different
revisions for the same tuple with no committed statement that they agree.

### E3 — the second half: which revision each record names

- `SCORECARD.md:14` verdict cell: `tip 9301d98c1c689c79741f0f1ba1f171138d20af07`; its
  `measured commit` cell names **only** `measured at 4edb25dfe262515d0da63224bbba71e02e36cba5 (before)`;
  its counting-command cell still carries an unresolved placeholder `--rev <tip>`.
- Report `/home/vgpnk/Projects/shokunin/.ufo/reports/round-22/souji.md:12`:
  "**Lane tip and measured revision: `77d659524c777276bcef33568be3c4cbcb9d1052`**"; `:179`
  "tip `77d6595`: `assertions=63 resolved=63 skipped=40 mismatches=0`, exit 0".
- `git merge-base --is-ancestor 9301d98 77d6595` → true; `git diff 77d6595 1208bfb -- SCORECARD.md` →
  empty; `git diff 9301d98 77d6595 -- SCORECARD.md` changes only that one cell's token
  (`8990ae4`/`62 62 39 0` → `9301d98`/`63 63 40 0`).

Three revisions are therefore in play (column `4edb25d`, prose `9301d98`, report `77d6595`), and no
committed file reconciles them. That part of D2 is real.

### E4 — does the planned repair close it? (K1 as drafted)

`tools/souji-record-agreement.py` (untracked draft, sha256 `f4a442790ee8e31f9e00350a2b36e83d2c2bcbf17edcaa8301ec7e8bb607fe34`,
mtime 2026-10-25 05:13:10, 14187 B — a moving target; the L1 edited it between my two reads):

- `:41` `K1_RECEIPT = "census/round-23/records/declared-evidence-after.tsv"` — single receipt.
- `:136` the receipt is read **at `self.rev`**, `:145-146` it must carry a `rev=` header.
- `:155-164` for **every** `COUNTS_RE` match on an `r22`/`round-22`-scoped line of SCORECARD.md:
  the tuple must equal the receipt's value, else `value-disagree`; the receipt's rev must appear in
  the same line, else `rev-disagree`.

`SCORECARD.md:14` is one physical table row in scope (`\br22\b` matches "R22") carrying **four**
matches — base `55 52 33 3` (verdict cell), after `63 63 40 0` (verdict cell), after `63 63 40 0`
(counting-command cell), base `55 52 33 3` (before-receipt description). Simulation of the exact loop
against committed bytes with a hypothetically perfect receipt (`rev=9301d98…`, value `63 63 40 0`):

```
$ python3 -B - <<'PY'   # replays K1's loop verbatim over git show 1208bfb:SCORECARD.md
  L14: assertions=55 resolved=52 skipped=33 mismatches=3 VALUE-DISAGREE  rev-present
  L14: assertions=63 resolved=63 skipped=40 mismatches=0 PASS            rev-present
  L14: assertions=63 resolved=63 skipped=40 mismatches=0 PASS            rev-present
  L14: assertions=55 resolved=52 skipped=33 mismatches=3 VALUE-DISAGREE  rev-present
```

**K1 cannot report mismatches=0** while the calibration row quotes both ends, which is the row's whole
claim ("Same instrument, both ends"). C1's target `M_after = 0` is therefore unreachable as drafted.

Second gap: **no w1 item produces the K1 receipt.** Of the 41 frozen items, none names
`census/round-23/records/declared-evidence-after.tsv` or runs `souji-receipt-run.py run`
(`grep` over `w1-spec.json`: only `ScoutCommunity`, `RevRecords`, `ExecFixtureAgreement` mention
`census/round-23` at all, none as an emitter). The receipt D2 needs is L1 work outside the wave.

## Findings

1. **D2 first half is real and open.** Zero `rev=`-headed receipts anywhere under `census/` at
   `1208bfb`; `census/round-23/` does not exist; `9301d98` appears in committed bytes only as
   `SCORECARD.md:14` prose and as the spot-check's quotation of it. Location: `SCORECARD.md:14`,
   `census/` (absent file `census/round-23/records/declared-evidence-after.tsv`).
2. **D2's value implication is overstated.** `assertions=63 resolved=63 skipped=40 mismatches=0`
   re-derives at both `9301d98` and `77d6595` with the committed tool blob (`65817d0d…`), rc=0 (E2).
   The defect is binding + token agreement, not an unsupported number. Location: `SCORECARD.md:14`
   vs `.ufo/reports/round-22/souji.md:179`.
3. **D2 second half is real but benign in substance.** Report `77d6595` vs SCORECARD `9301d98`, and
   the row's `measured commit` cell names neither (it says `4edb25d (before)`), while the counting
   command still says `--rev <tip>`. Location: `SCORECARD.md:14`, `.ufo/reports/round-22/souji.md:12`.
4. **The planned K1 repair does not close D2 — unsatisfiable value clause.** `:155-164` requires every
   r22-scoped tuple to equal the single after receipt, including the two control-end `55 52 33 3`
   occurrences on the same physical row (E4). Location: `tools/souji-record-agreement.py:155-164`.
5. **The receipt K1 reads has no producer in the frozen wave.** Location: `.ufo/waves/round-23/w1-spec.json`
   (41 items; none emits `census/round-23/records/declared-evidence-after.tsv`).
6. **Nothing at the lane base closes it.** No `census/round-23` tree, no exemption, no superseding
   LOG line naming either revision for this tuple.

## Minimal repair that closes D2

Not achievable by editing filed evidence or operator files: the r22 report lives at
`/home/vgpnk/Projects/shokunin/.ufo/reports/round-22/souji.md`, outside the lane tree (the lane has no
`.ufo/reports/` at all: `git ls-tree -r --name-only HEAD -- .ufo/reports` is empty), so the lane cannot
rewrite the report's `77d6595` token — and must not.

**(R1) The receipt** — new file `census/round-23/records/declared-evidence-after.tsv`, emitted by
`tools/souji-receipt-run.py run --root /home/vgpnk/Projects/shokunin/souji-shokunin
--rev 9301d98c1c689c79741f0f1ba1f171138d20af07 --tool tools/souji-declared-evidence.py
--out <lane>/census/round-23/records/declared-evidence-after.tsv -- python3 -B tools/souji-declared-evidence.py
--root . --file SCORECARD.md --rev 9301d98c1c689c79741f0f1ba1f171138d20af07 --format counts`.
Required content: header order per receipt v1, `rev=9301d98c1c689c79741f0f1ba1f171138d20af07`,
`tool_sha256=65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4` (the blob the tree holds
at that rev, already pinned in `instrument-digests.txt`), `rc=0`, stdout exactly
`assertions=63 resolved=63 skipped=40 mismatches=0`. Wording constraint: the receipt binds `9301d98`
because that is the revision the record names — binding `77d6595` instead would bind a revision
SCORECARD does not name, and binding the round-23 tip would attach a round-23 count to an r22 claim.

**(R2) `SCORECARD.md:14`, three cells only** (no score, no verdict prose change):
- counting-command cell: replace the literal placeholder `--rev <tip>` with
  `--rev 9301d98c1c689c79741f0f1ba1f171138d20af07`, and append
  `; receipt census/round-23/records/declared-evidence-after.tsv (tool_sha256=65817d0d…)`.
- `measured commit` cell: add the after revision beside the existing before revision — wording
  constraint: exactly one after token (`9301d98…`), and it must be the same token the receipt's
  `rev=` header carries; the cell must not claim `77d6595` is the measured revision.
- verdict cell: keep the 4-tuple **unchanged** (E2 shows it is correct); append
  `after-state receipt: census/round-23/records/declared-evidence-after.tsv`.
- Append-only reconciliation for the report token (the report cannot be edited): one new line in the
  same cell or a LOG.md entry, wording constraint: name both tokens and the equality — e.g.
  "report tip 77d6595 and this row's 9301d98 re-derive the identical counts 63/63/40/0 rc=0
  (re-derived 2026-10-25 at both revisions); the report's tip token is not restated as the measured
  revision." Do not delete the report's claim, do not restate it as SCORECARD's.

**(R3) K1's value clause (pre-data, since the tool is still untracked and no receipt exists yet)** —
`:155-164` must scope the value check to the tuple **bound to the receipt's revision**, per the frozen
prose ("the r22 C1 after 4-tuple … must equal the counts line … the revision token on that same
physical line must equal the receipt's `rev=` header"): for each r22-scoped occurrence take the nearest
preceding 40-hex token on that physical line; if it equals the receipt rev the tuple must equal the
receipt value (`value-disagree` otherwise), and at least one such bound occurrence is required
(`occurrence-absent` otherwise); unbound/base-bound occurrences count toward `occurrences` only.
This is a narrowing of the code to the already-frozen prose, not a post-data narrowing of the key set —
but if the L1 prefers not to touch the tool, the alternative record shape is R2 plus moving the
control-end numbers onto a non-r22 line, which I record as the weaker option (it satisfies the counter
by taking a number out of the counter's scope).

**Closure command** (exit 0 both halves; second output byte-equal to the receipt's stdout):

```
python3 tools/souji-receipt-run.py verify census/round-23/records/declared-evidence-after.tsv
python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md \
  --rev 9301d98c1c689c79741f0f1ba1f171138d20af07 --format counts
git grep -c 'rev=9301d98c1c689c79741f0f1ba1f171138d20af07' HEAD -- census/   # >= 1
```

## Attack log

**A1 — K1's receipt-must-exist-at-its-own-`rev=` clause (observed, then self-repaired by the L1).**
An earlier read of the same draft (`tools/souji-record-agreement.py`, before 05:13:10) contained
`if rev != self.rev: … receipt-rev` alongside `read_at(self.rev, K1_RECEIPT)`, i.e. the receipt had to
be committed in the very commit its `rev=` header names — a git fixed point (a commit hash cannot depend
on a blob that names that hash), making `M_after=0` unreachable for any R. The draft at digest
`f4a44279…` replaces it with a `rev=`-presence check and a comment naming the same impossibility. Recorded
so it is not reintroduced: the binding that must be enforced instead is R2's (SCORECARD line names the
receipt's rev) plus C2's verifier (`tool_sha256` vs the blob at that rev), not receipt-in-its-own-commit.

**A2 — K1's per-line all-tuples rule (live).** The cheapest way to make K1 green without closing D2 is to
delete the control-end tuple from the r22 calibration row (harm: the "both ends" claim and the do-nothing
control end disappear from the record) or to move it onto a physical line without `R22`/`round-22` (a
scope dodge). A receipt bound to the round-23 tip while the row keeps an r22 label would be a third: it
attaches a round-23 count to an r22 claim. R3 above removes the first two incentives; the third is
blocked by R1's `rev=9301d98` constraint.

## Residual risk / verification gaps

- I ran the lane's declared-evidence tool read-only at two revisions (git objects only); I did not run
  `souji-receipt-run.py` (does not exist yet) or `souji-record-agreement.py` (untracked, mid-write).
  Whether R1's `verify` accepts a receipt produced at an *earlier* rev than the tree that holds it is
  `[INFERENCE]` from the C2 fixture spec (`verify --root <repo> <receipt>` + `tool_sha256` at `rev`),
  not from executed bytes.
- The draft instrument is untracked and changed under me once; my K1 citations pin digest `f4a44279…`.
  A committed version must be re-checked against R3.
- No tool installed or upgraded; no package manager used (system `git`, `python3` sufficed).
