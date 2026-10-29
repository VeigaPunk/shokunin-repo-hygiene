# R42w2critic03 — hidden-case audit of the landed C2 tool (`tools/souji-freeze-check.py`)

Seat: R42w2critic03 (role critic, leaf, no subagents). Judged on: operability. Milestone: r42 falsify the landed artifacts.
Lane tip under attack: `3105a63b23481fccf7df58e74d14a6681e0ea0c8`. The lane working tree equals the tip
(`git show 3105a63…:tools/souji-freeze-check.py | cmp - tools/souji-freeze-check.py` → identical, sha256 `9ddd596b…`).
Nothing in the lane, the fleet or any tracked file was written. No tool was installed or upgraded (`uv`, `pacman`, `npm`: not used).
Receipts: `.ufo/waves/round-42/w2/R42w2critic03/receipts/` (copies of every output quoted below; `sha256.txt` pins every input).

## Verdict

- **No regression in the landed tool against the r41 tool.** Across 92 audit scenarios at the pinned seed, exactly one verdict changed
  (`dispatch-lookalike-names-silent`, pass → fail), and it follows the r42 DISPATCH-BEFORE-FREEZE widening exactly. Its second
  changed scenario (`no-claims-header-variants`) stays red and gains two `HEADING-MALFORMED` findings that the r42 grammar defines.
- **The audit's strict tier is partly a stale oracle.** Its expectations are written to the r41 grammar. Four strict scenarios are red
  for the landed tool; three of those are red for the r41 tool too (r41 hardening: no `Round:` → `FIELD-MISSING C0 Round`), and one
  is the r42 widening. None of the four is a defect of the landed tool against the r42 grammar.
- **Held-out harness (wave 1, `R42critic02/heldout-check.py`): landed 11/11.** The r41 tool scores 7/11 on the same harness.
- **Five limits found by probing** (none a regression; each is in the table in §4). The one an operator should weigh: a second
  `Round:` line is ignored (first match wins), so the dispatch scan can be pointed at the wrong round directory. Shared with r41.
- Lane self-checks: `--selftest` 31/31; `census/round-42/preregistration.txt` at the tip reads `claims=3 findings=0`; the r41 preregistration reads `claims=3 findings=0`.

## 1. Audit — three runs of the landed tool (+ r41 tool at the pinned seed)

Harness: `census/round-41/waves/w2/R41w2executor01/hidden-audit.py` (sha256 `5bcdf76b…`), run as the task specifies.
Scratch: `/fast/scratch/hyaku/souji-r42/R42w2critic03/audit`, removed before yield.

Commands (exact):

```
TMPDIR=$S/audit python3 -B $A --tool $S/tools/landed-freeze-check.py --scratch $S/audit --seed 20261028 --out $S/audit/landed-seed20261028.json
TMPDIR=$S/audit python3 -B $A --tool $S/tools/landed-freeze-check.py --scratch $S/audit --out $S/audit/landed-rand1.json      # no seed
TMPDIR=$S/audit python3 -B $A --tool $S/tools/landed-freeze-check.py --scratch $S/audit --out $S/audit/landed-rand2.json      # no seed
TMPDIR=$S/audit python3 -B $A --tool $S/tools/r41-freeze-check.py    --scratch $S/audit --seed 20261028 --out $S/audit/r41-seed20261028.json
```

where `$S/tools/landed-freeze-check.py` is a byte copy of the lane file (sha256 `9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6`)
and `$S/tools/r41-freeze-check.py` is `git -C <lane> show bf618f6c5c09d302994871c94903abbea2deb60d:tools/souji-freeze-check.py`
(sha256 `8131847bcfc5ecef513eb608a67ec18feab44f7a8b6c094824b082ffe52a76e2`).

SUMMARY lines, verbatim:

```
SUMMARY scenarios=92 strict=79/83 literal=0/4 ambig=4/5 seed=20261028 tool_sha256=9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6     (landed, pinned)
SUMMARY scenarios=92 strict=80/83 literal=0/4 ambig=4/5 seed=20261028 tool_sha256=8131847bcfc5ecef513eb608a67ec18feab44f7a8b6c094824b082ffe52a76e2     (r41, pinned)
SUMMARY scenarios=92 strict=79/83 literal=0/4 ambig=4/5 seed=1457458135 tool_sha256=9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6   (landed, random)
SUMMARY scenarios=92 strict=79/83 literal=0/4 ambig=4/5 seed=2132828476 tool_sha256=9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6  (landed, random)
```

Strict failing set, landed (pinned, and identical in both random runs): `round-absent-early-dispatch-silent`, `dispatch-lookalike-names-silent`,
`no-claims-empty-file`, `no-claims-header-variants`. Strict failing set, r41 (pinned): the first, third and fourth of those.
The literal tier (4 scenarios) and ambig tier (5) fail identically for both tools (literal: FIELD-EMPTY instead of the expected
BASE/COUNTER/POPULATION/CONTROL-MISSING/-UNRESOLVED on blank values; ambig-sha256-uppercase-hex: COUNTER-DIGEST) — unchanged, not in scope of r42.
The random-seed runs were not made for the r41 tool; the seed-to-verdict match is shown for the landed tool only.

### Scenario table (every scenario whose verdict or finding set differs between the two tools at seed 20261028, plus the three shared strict reds)

| scenario (tier) | r41 tool | landed tool | follows the r42 grammar? |
|---|---|---|---|
| `dispatch-lookalike-names-silent` (strict) | PASS — exit 0, no findings | FAIL — exit 1, `C0 DISPATCH-BEFORE-FREEZE` ×4 on `x-dispatch.json.bak`, `x.readyy`, `a-dispatch.jsonl`, `<hex>-dispatch.JSON`; `dispatch.json` and `ready` silent | **Yes.** c2-counter docstring: "basename contains `-dispatch` or `.ready`, at any depth". `x-dispatch.json.bak` contains `-dispatch`; `x.readyy` contains `.ready`; `a-dispatch.jsonl` contains `-dispatch`; `…-dispatch.JSON` contains `-dispatch`. `dispatch.json` has no hyphen before `dispatch` and `ready` has no dot: both correctly silent. The scenario's expectation is the r41 grammar (`E(0)`), so the audit's oracle is stale here. Not a regression. |
| `no-claims-header-variants` (strict) | FAIL — exit 1, `C0 NO-CLAIMS` (expected) + `C0 FIELD-MISSING` (extra) | FAIL — exit 1, `C0 NO-CLAIMS` + `C0 FIELD-MISSING` + `C0 HEADING-MALFORMED` ×2 (extra) | **Yes for the two HEADING-MALFORMED.** Input `"# x\n##C1\n## c2\n## C\n# C3\n#### C4\n…"`. Docstring: `##C1` (no space) and `## c2` (lowercase) are malformed → 2 findings, matching. `## C` (no digit) silent (held-out H8 agrees), `# C3` not `##` silent, `#### C4` excluded by `###` rule — all correct. The `FIELD-MISSING C0 Round` (no Round line) is the r41 hardening, shared by both tools; the audit's `E(1, NO-CLAIMS)` predates it. Verdict (red) unchanged. |
| `round-absent-early-dispatch-silent` (strict) — shared | FAIL — exit 1, `C0 FIELD-MISSING Round` (expected exit 0) | FAIL — same | n/a: `FIELD-MISSING C0 Round` when `Round:` is absent is the r41 tool's documented behaviour (r41 docstring, commit 383972c). The audit oracle (exit 0) predates it. Unchanged between tools. |
| `no-claims-empty-file` (strict) — shared | FAIL — `C0 FIELD-MISSING` extra (no Round line) | FAIL — same | n/a, as above. Unchanged. |

All other 88 scenarios of the 92 (strict 79 of the 83 pass for both; literal and ambig identical): **identical** exit code and (claim, class) multiset in both tools at the pinned seed.

## 2. Held-out harness — wave 1 `R42critic02/heldout-check.py` (sha256 `dab5815a…`)

Header read first: "The fixtures below are NOT in census/round-42/c2-cases.tsv or c2-counter.py CASES … expectations written from the
c2-counter.py docstring grammar before any candidate was run." Each fixture is a synthetic git repo under `--scratch`.

Command: `TMPDIR=$S/audit python3 -B $H --scratch $S/audit $S/tools/landed-freeze-check.py` (and the r41 copy).

```
HELDOUT-SUMMARY landed-freeze-check.py pass=11 fail=0 n=11
HELDOUT-SUMMARY r41-freeze-check.py pass=7 fail=4 n=11
```

| held-out case | r41 tool | landed tool | r42 grammar clause |
|---|---|---|---|
| H1-dispatch-jsonl-before | FAIL (no finding; r41 scans `-dispatch.json` suffix only) | PASS | `-dispatch` anywhere in basename |
| H2-dispatch-deep-ready | PASS | PASS | `.ready` at any depth |
| H3-dispatch-spec-bak | PASS | PASS | `-spec.json.bak` neither suffix nor substring |
| H4-dispatch-other-round | PASS | PASS | only `round-<N>` of the Round line scanned |
| H5-dup-kill-triple | FAIL (first-wins, no KEY-DUPLICATE) | PASS | one finding per duplicated key |
| H6-dup-two-keys | FAIL | PASS | one per duplicated key |
| H7-heading-hash3 | PASS | PASS | `###` excluded |
| H8-heading-C-no-digit | PASS | PASS | `## C` with no digit silent |
| H9-heading-glued-no-digit | PASS | PASS | `##C` with no digit silent |
| H10-counter-symlink-dangling | FAIL (`C1 COUNTER-DIGEST`, not `COUNTER-SYMLINK`) | PASS | symlink at freeze → COUNTER-SYMLINK alone |
| H11-clean-trailing-spaces | PASS | PASS | clean claim stays clean |

The held-out harness scores the landed tool **11/11**, matching the wave-1 honest-tool reading. (The memorising candidates' 6/11 is not re-measured here.)

## 3. Lane self-checks (read-only, lane tool at the tip)

```
$ python3 -B tools/souji-freeze-check.py --selftest
SELFTEST cases=31 pass=31 fail=0            (rc 0)
$ python3 -B tools/souji-freeze-check.py --root $L --prereg census/round-42/preregistration.txt --rev 3105a63b…
SUMMARY claims=3 findings=0                 (rc 0)
$ python3 -B tools/souji-freeze-check.py --root $L --prereg census/round-41/preregistration.txt --rev 3105a63b…
SUMMARY claims=3 findings=0                 (rc 0)
$ python3 -B tools/souji-freeze-check.py --root $L --prereg census/round-40/preregistration.txt --rev 3105a63b…
FINDING C3 FIELD-MISSING Kill / Population / Target … SUMMARY claims=3 findings=19   (rc 1; the pre-grammar retro leg, red as designed)
```

## 4. Probes beyond the audit (fixtures under scratch; `probe/probe.py`, `probe/probe-mv.py`; output in receipts)

Each row: the input, what each tool printed, and the verdict on the landed tool. "shared" = same output from the r41 tool.

| probe | r41 tool | landed tool | verdict on landed |
|---|---|---|---|
| `##C2` stray line inside a claim | rc 0, clean | rc 1, `C0 HEADING-MALFORMED line=9` | correct (docstring class) |
| `##C1 x` stray line after `Target:` (before `Kill:`) | rc 0, clean | rc 1, `HEADING-MALFORMED line=8` + `C1 FIELD-MISSING Kill` | correct class; **limit L4**: the malformed line also closes the claim, so later keys go missing. Still red; docstring says "opens no claim" and is silent on closing. |
| `## C1<TAB>x` as the only claim header | rc 0, clean | rc 1, `HEADING-MALFORMED line=2` + `NO-CLAIMS` | correct: `## C1` followed by a tab is not `## C<digits>` + space/EOL |
| `## C1 ` (trailing space) | rc 0 | rc 0 | correct |
| second `## C1` block (two claims, both labelled C1) | `claims=2 findings=0` | `claims=2 findings=0` | **limit L3** (shared): duplicate claim labels are not in the r42 grammar; not detected |
| `Kill:` repeated inside `### notes` sub-heading of a claim | clean | `C1 KEY-DUPLICATE Kill` | correct (the `###` line does not close the block; the key repeats within the block) |
| `Round: 41` on line 1, `Round: 42` in the claim, a `w1-dispatch.json` under `round-42/` committed before freeze | rc 0 | rc 0 | **limit L1** (shared): `ROUND.search` takes the first match; the dispatch scan runs on `round-41/`, which is empty. A dispatch file before freeze goes unreported. |
| `w1-DISPATCH.json` before freeze | rc 0 | rc 0 | **limit L2**: `-dispatch` is matched case-sensitively; the grammar does not say it is case-insensitive. The audit's `%s-dispatch.JSON` only passed because the lowercase `-dispatch` was present. |
| `w1-dispatch.json` before freeze (control) | rc 1, `DISPATCH-BEFORE-FREEZE` | rc 1, same | correct |
| **git mv** `notes.md` → `w1-dispatch.json` before freeze (`probe/probe-mv.py`; git log shows `R100 …notes.md …w1-dispatch.json` and an earlier `A …notes.md`) | rc 1, `DISPATCH-BEFORE-FREEZE w1-dispatch.json` | rc 1, same | correct: `--no-renames` keeps the A on the new name |
| Counter replaced by a symlink **after** freeze (`probe/probe-mv.py`) | rc 1, `FROZEN-EDITED census/c.py` | rc 1, same | correct |

Note on `probe/probe.py` case `dispatch-rename-before-freeze`: its fixture is mis-built (no rename was performed; the file is only added and
then re-committed). Its all-zero output is not evidence; the real rename case is `probe-mv.py`. The receipt keeps the case because it was run.

## 5. Limits and findings for the L1 (none changes a frozen file; each is a named limit)

- **L1 — `Round:` first match wins (shared with r41).** `dispatch_findings` takes `ROUND.search(text)`. A preregistration with two
  `Round:` lines scans the first one's directory only. Not a KEY-DUPLICATE case (the key is prereg-wide, not claim-scoped). Low likelihood
  in practice; the fix is a KEY-DUPLICATE-like rule over `Round:`. Not in the r42 grammar.
- **L2 — `-dispatch` is case-sensitive.** `w1-DISPATCH.json` is silent. The r42 docstring says `-dispatch` literally; a reader could
  expect case-folding. Limit, not a regression.
- **L3 — duplicate claim labels are not detected** (`## C1` twice reads `claims=2 findings=0`). Not in the r42 grammar; shared with r41.
- **L4 — a malformed heading closes the current claim** (landed-only; the r41 tool did not treat `##C1` as a heading at all). The
  extra `FIELD-MISSING` lines are downstream and the prereg stays red, so this is a precision issue, not a false clean.
- **O1 — the audit oracle is stale for r42.** `hidden-audit.py` strict expectations encode the r41 grammar (`dispatch-lookalike`,
  `no-claims-header-variants`) and predate the r41 `FIELD-MISSING C0 Round` hardening (`round-absent-…`, `no-claims-empty-file`). The
  landed tool's 79/83 and the r41 tool's 80/83 therefore measure the oracle as much as the tool. Recommend the L1 treat the audit as informational,
  as the r42 preregistration already does (`retro_clean` instead of a frozen leg); do not edit the audit under this round.

## 6. Commands run (complete list, all read-only against the lane)

```
git -C $L show bf618f6c5c09d302994871c94903abbea2deb60d:tools/souji-freeze-check.py > $S/tools/r41-freeze-check.py
cp $L/tools/souji-freeze-check.py $S/tools/landed-freeze-check.py
sha256sum $S/tools/*.py $L/tools/souji-freeze-check.py ; git -C $L show 3105a63…:tools/souji-freeze-check.py | sha256sum
diff -u $S/tools/r41-freeze-check.py $S/tools/landed-freeze-check.py                 # the r42 changes read in full
TMPDIR=$S/audit python3 -B $A --tool $S/tools/landed-freeze-check.py --scratch $S/audit --seed 20261028 --out …  (rc 1)
TMPDIR=$S/audit python3 -B $A --tool $S/tools/landed-freeze-check.py --scratch $S/audit --out …landed-rand1.json (rc 1)
TMPDIR=$S/audit python3 -B $A --tool $S/tools/landed-freeze-check.py --scratch $S/audit --out …landed-rand2.json (rc 1)
TMPDIR=$S/audit python3 -B $A --tool $S/tools/r41-freeze-check.py --scratch $S/audit --seed 20261028 --out …  (rc 1)
TMPDIR=$S/audit python3 -B $H --scratch $S/audit $S/tools/landed-freeze-check.py   (rc 0; HELDOUT-SUMMARY pass=11 fail=0 n=11)
TMPDIR=$S/audit python3 -B $H --scratch $S/audit $S/tools/r41-freeze-check.py     (rc 0; HELDOUT-SUMMARY pass=7 fail=4 n=11)
python3 -B $L/tools/souji-freeze-check.py --selftest                                      (SELFTEST cases=31 pass=31 fail=0)
python3 -B $L/tools/souji-freeze-check.py --root $L --prereg census/round-42/preregistration.txt --rev 3105a63…   (claims=3 findings=0)
python3 -B $L/tools/souji-freeze-check.py --root $L --prereg census/round-41/preregistration.txt --rev 3105a63…   (claims=3 findings=0)
python3 -B $L/tools/souji-freeze-check.py --root $L --prereg census/round-40/preregistration.txt --rev 3105a63…   (findings=19, rc 1)
python3 -B probe/probe.py ; python3 -B probe/probe.py dispatch-… ; python3 -B probe/probe-mv.py   (receipts/probe-*.txt)
```

Python-level JSON comparison of the two pinned audit runs (name-by-name `ok`, `rc`, `got`) produced the two differing scenarios above and no others.

## 7. Verdict table

| scenario | r41 tool | landed tool | follows the r42 grammar? |
|---|---|---|---|
| dispatch-lookalike-names-silent | PASS | FAIL (4× DISPATCH-BEFORE-FREEZE) | yes (`-dispatch` / `.ready` substring rule) |
| no-claims-header-variants | FAIL (NO-CLAIMS + FIELD-MISSING Round) | FAIL (+ 2× HEADING-MALFORMED) | yes for the 2 HEADING-MALFORMED; the Round finding is shared r41 behaviour |
| round-absent-early-dispatch-silent | FAIL (FIELD-MISSING Round) | FAIL (same) | n/a — shared r41 behaviour, stale oracle |
| no-claims-empty-file | FAIL (FIELD-MISSING Round + NO-CLAIMS) | FAIL (same) | n/a — shared r41 behaviour, stale oracle |
| other 88 audit scenarios | identical | identical | — |
| **held-out (11 cases)** | **7/11** | **11/11** | H1, H5, H6, H10 are r42 clauses the r41 tool lacks |

Limits L1–L4 and O1 are in §5. Tooling: none installed. Scratch dir `/fast/scratch/hyaku/souji-r42/R42w2critic03` removed after this report.
