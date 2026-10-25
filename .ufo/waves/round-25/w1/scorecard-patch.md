# SCORECARD.md patch — round 25 (draft; the L1 integrates; SCORECARD.md not edited)

Author seat: `L1Souji25.ScribeScorecard-2`. Base bytes: `SCORECARD.md` sha256
`efcc897613310dcb0213478a4670d578b85b589d082c445c027709a9b0567d52`, identical at lane base
`a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe` and at the prereg commit
`6e4737eab43d8fde1b85eb9f57023d29046705b4` (`git show <rev>:SCORECARD.md | sha256sum`, both). All line
numbers below are of those bytes (228 lines). `ScoutScorecardLines.md` was not present in
`.ufo/waves/round-25/w1/` at draft time, so the line numbers were taken directly from the committed bytes.
Cross-check them against that report when it lands.

Placeholders are `{{L1: …}}`. Before landing, `grep -n '{{L1:' SCORECARD.md` must print nothing.
Several placeholders sit inside backticks. The declared-evidence and pointer gates read backticked paths,
so every one of them has to be filled with a path that exists at the tip.

---

## P0 — prerequisite: the r24 block is still a fenced draft (`:169–:228`)

Commit `315422b` appended `.ufo/waves/round-24/w2/W2ScorecardDraft.md` to the file verbatim, with its
scribe instructions still in it. As a result the Round 24 table is a `markdown` code block under `## Retired`,
not a table above Round 23. The two r24 capability rows are outside the Capabilities table. The r24 done and
r25 planned lines are outside `## Planned`. "Insert above Round 24 measurements" only renders correctly once
this block is integrated. Content-preserving moves, no number or wording changed:

| from (base lines) | action |
|---|---|
| `:171` "Insert the table below directly above …" | delete (instruction to the integrator) |
| `:173` ` ```markdown ` and `:207` ` ``` ` | delete (fence) |
| `:174–:206` Round 24 heading, table, notes, limits, lane-bound paragraph | move to directly above `:17` `### Round 23 measurements`, followed by one blank line |
| `:209` "Capabilities rows (append …)" | delete (instruction) |
| `:211` / `:214` fences | delete |
| `:212–:213` `debris census (r24)`, `coverage-map agreement (r24)` rows | move to directly after `:93` `record agreement audit (r23)` |
| `:216–:219` "Optional same-landing correction …" | delete; carried out by H3 below |
| `:221` "Planned (append after …)" | delete (instruction) |
| `:223` / `:226` fences | delete |
| `:224–:225` r24 done line, r25 planned line | move to directly after `:134` `- **r24 — planned:** …` |
| `:169–:170`, `:208`, `:210`, `:215`, `:220`, `:222`, `:227` blank lines; `:228` `---` | delete; file ends `## Retired` / blank / `None.` |

After P0, `## Retired` is again the last section (`:166–:168`). If the L1 declines P0, insert H1 directly
above `:17` instead. The rendered order is then r25, r23, with r24 still fenced at the end, and that has to be
disclosed in the lesson.

---

## H1 — `### Round 25 measurements` (insert directly above `### Round 24 measurements`; after P0 that heading is at `:17`)

```markdown
### Round 25 measurements (2026-10-25, lane base a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 kill-rule tool row | calibration 7 | at base the tool (`tools/souji-coverage-agreement.py` sha256 `71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897`) refuses `--base-rev`: rc 2, `refused: argv: unrecognized arguments: --base-rev …` (`census/round-25/records/c1-control-base.tsv`; this v1 receipt has empty stdout, so `verify` refuses it with `RECEIPT-COUNTS-ABSENT`); the map at base reads `grounded=6 mapped=6 dangling=0 mismatches=0`, rc 0 (`census/round-25/records/coverage-agreement-at-base.tsv`); red arm, the old tool bytes against the extended fixture: `cases={{L1: C}} pass={{L1: P}} control={{L1}}`, rc {{L1}}, k1–k4 {{L1: FAIL list}} (`{{L1: red-arm receipt path}}`) | `grounded={{L1: G}} mapped={{L1: M}} dangling=0 mismatches=0 kill_tested=4 kill_violations=0`, rc 0 (`{{L1: after receipt path}}`, `rev={{L1: tip40}}`); fixture `cases={{L1: C}} pass={{L1: C}} control=FALSE-GREEN-REJECTED`, rc 0 (`{{L1: fixture receipt path}}`) | `python3 -B tools/souji-coverage-agreement.py --root . --rev <tip40> --base-rev a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`; `python3 -B tests/fixtures/r25-coverage-agreement.py --tool tools/souji-coverage-agreement.py` | tool `tools/souji-coverage-agreement.py` sha256 `{{L1}}`; fixture `tests/fixtures/r25-coverage-agreement.py` sha256 `{{L1}}` |
| C2 size-census refusal surfaces covered | operability 8 | fixture at base: `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc 0 (`census/round-25/records/c2-control-base.tsv`, fixture sha256 `373ef1f0a02f8ca11fccd4ff32d8511c1eaaf3ede672c37ed11ef2b10968084f`, `rev=a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`); no bare, subdir or partialClone-only case; red arm, the old tool blob `1efe406e7f39b8fe736be2a566053703a571ffc0:tools/souji-size-census.py` against the extended fixture: `cases=12 pass={{L1: P}}`, failing {{L1: case ids among 9–12}} (`{{L1: red-arm receipt path}}`) | `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc 0 (`{{L1: after receipt path}}`, `rev={{L1: tip40}}`): case 9 bare-nonempty rc 0 `census.invoked_from=bare`, case 10 bare-empty rc 1 "No default references", case 11 subdir rc 2, case 12 partialClone-only rc 2 | `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` | fixture `tests/fixtures/r24-size-census.py` sha256 `{{L1}}`; tool unchanged since base (`git diff --quiet a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe {{L1: tip40}} -- tools/souji-size-census.py`) |
| C3 structure probe under the common-git-dir envelope; colocated/plain precondition | coverage 8 | `selftest=PASS ids=5/5`, rc 0 (`census/round-25/records/c3-control-base.tsv`, fixture sha256 `b6bf52056d037b2251632b409be3d31852588480c392ddc50ca8f8dbf101179f`, `rev=a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`) | `selftest=PASS ids=7/7`, rc 0 (`{{L1: after receipt path}}`, `rev={{L1: tip40}}`): `SOUJI-R13-STRUCT-linked-common-dir` (common and private gitdir manifests unchanged; `probe.git_common_dir` equals A's git dir) and `SOUJI-R13-STRUCT-colocated-vs-plain` (`references.others.count` {{L1: plain}} → {{L1: colocated-like}}); entry `corpus/knowledge/git-repo-structure-common-dir.md` (ground: F2; S124/S125) in the README F2 entries column | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` | fixture sha256 `{{L1}}`; probe `tools/souji-repo-structure.sh` sha256 `{{L1}}` |
| r23 C2 counter re-read as a `verify=ok` count (routed; not a claim) | operability 8 | `receipts_verify_ok=19 grep_hits=21` at `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`; the two that fail are `census/round-24/size-census-lane.txt` and `census/round-24/records/r23-agreement-regress.out`, both `RECEIPT-MALFORMED` (23 of 26 at `6e4737eab43d8fde1b85eb9f57023d29046705b4`, where `census/round-25/records/c1-control-base.tsv` adds `RECEIPT-COUNTS-ABSENT`) | `receipts_verify_ok={{L1}} grep_hits={{L1}}` at `{{L1: tip40}}` | the rev-pinned recipe in H4 | runner `tools/souji-receipt-run.py` sha256 `279a64739a12f6816392329fe3b9526b0e59cc3ab7b24188b95b1966e065e191` at base; at tip `{{L1}}` |
| r23 record-agreement counter at the tip (routed; not a claim) | calibration 7 | `keys=4 records=4 occurrences=17 mismatches=0`, rc 0 (`census/round-25/records/record-agreement-at-base.tsv`, tool sha256 `41db9ca8c76bf530a4d1dd57dba079f53d5f66cc44b40dc9e45c5444bcc1036d`, `rev=a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`) | `keys={{L1}} records={{L1}} occurrences={{L1}} mismatches={{L1}}`, rc {{L1}} (`{{L1: receipt path}}`, `rev={{L1: tip40}}`) | `python3 -B tools/souji-record-agreement.py --rev <tip40> --no-worktree` | tool sha256 `{{L1}}` |
| R15/R17 record-agreement fixture cases (routed; not a claim) | calibration 7 | old tool bytes against the extended fixture: `selftest=14/15` ({{L1: failing case}}; `{{L1: red-before receipt path}}`) | `selftest=15/15`, `control=FALSE-GREEN-REJECTED` (`{{L1: receipt path}}`) | `python3 -B tests/fixtures/r23-record-agreement.py --tool tools/souji-record-agreement.py` | fixture sha256 `{{L1}}` |

The base controls were committed in `6e4737e` before any after-data, and the claim counters are the frozen
`.ufo/waves/round-25/preregistration.txt` bytes. Named limits:

- **C1.** The kill rule covers entries that carry `ground: F<k>` at the base revision only. An entry grounded
  after the base cannot trigger it. C3's new entry raises `grounded` without raising `kill_tested`.
- **C2.** The no-write envelope still excludes atime/ctime, so a write that restores mtimes is invisible to it.
  Hostile config/env, the `census.warning=` stderr contract and the not-a-repository exit 2 still have no case.
  Tool-clause mutant survivors before/after the extension: {{L1: N/11 → N/11}}.
- **C3.** The colocated case simulates jj keep refs under `refs/jj/keep/*`; no jj binary runs. It records
  a precondition (a colocated figure is not a plain baseline). It is not a `git repo structure` size
  baseline.
- **Receipt count.** `verify` does not read `rc=`. A `verify=ok` count therefore counts bound receipts, not
  passing runs (three r24 rc 1 controls verify ok). A refusal receipt with empty stdout can never reach
  `verify=ok`. That applies to `census/round-25/records/c1-control-base.tsv`, C1's own before-control.
```

---

## H2 — D1 retitle of the r24 C3 claim (R24-M25)

Lines are given after P0. At base they are `:180` and `:224`. The filed title is kept as an append-only marker.

`:180` (table row, claim cell). Replace

```markdown
| C3 receipt verify/run symmetry | operability 8 |
```

with

```markdown
| C3 receipt verify durability + tool= argv binding (r23 residuals R1/R2) (retitled r25, D1 / R24-M25; filed as "receipt verify/run symmetry", which the counter does not witness: `verify` refuses 19 of 36 `run`-written shapes) | operability 8 |
```

`:224` (r24 done line in `## Planned`). Replace

```markdown
C3 receipt verify/run symmetry (refusals 0/2 → 2/2, regress 5/5)
```

with

```markdown
C3 receipt verify durability + tool= argv binding (r23 residuals R1/R2; retitled r25 D1, filed as "receipt verify/run symmetry") (refusals 0/2 → 2/2, regress 5/5)
```

No other SCORECARD occurrence (`rg -n -i symmetry SCORECARD.md` → `:180`, `:224` only). The other
occurrences are outside this file and outside this seat's scope: `LOG.md:1628`,
`corpus/README.md:504`, `corpus/README.md:519`, `corpus/lessons/round-24.md:1`, `:20`.

---

## H3 — R3 note on the `blob-bound receipts (r23)` capabilities row (`:92`)

Append to the end of the "what it can now do" cell. Insert immediately before the cell separator
` | \`tools/souji-receipt-run.py\`; \`tests/fixtures/r23-receipt-run.py\` 8/8;`. The r23 sentence is not
rewritten.

```markdown
 *(r25 note, R3, 2026-10-25: "tool sha256 of the bytes the command ran against" overstates the binding. Since r24 the digest binds the committed bytes of the file named by `tool=` at `rev=`, and `verify` requires that label to be an exact argv element of `cmd=` (`RECEIPT-TOOL-NOT-IN-ARGV`); it does not bind the executed program: a tool named as an operand while another program runs still verifies.)*
```

The same r23 sentence is also at `LOG.md:1588` ("tool sha256 of the bytes the command ran against"), which
is outside this seat's scope. The prereg's R3 "SCORECARD/LOG append-only note" needs the LOG half as well.

---

## H4 — r23 C2 counter line: `tool_sha256` grep → `verify=ok` count (`:22`)

The r23 numbers (0 → 5) stay as filed. Append to the end of the counting-command cell, i.e. after
``python3 tools/souji-receipt-run.py verify --root . <receipt>` for each``:

```markdown
; *r25 (routed): superseded as the counter by `receipts_verify_ok`, the number of `verify=ok ` lines when each `git grep -lE '^tool_sha256=[0-9a-f]{64}$' <rev> -- census/` hit is extracted with `git show <rev>:<path>` into /var/tmp scratch and passed to `python3 -B tools/souji-receipt-run.py verify --root . <file>`, reported with `grep_hits` as the denominator: 19 of 21 at `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`, {{L1}} of {{L1}} at `{{L1: tip40}}`. The grep alone counts any file with a 64-hex `tool_sha256=` line (`census/round-24/records/r23-agreement-regress.out` is fixture output, not a receipt), and `grep -r` over the working tree also reads untracked trees under `census/`. A `verify=ok` receipt is bound, not green: `verify` does not read `rc=`.*
```

Rev-pinned recipe (executed by this seat at `a6d2d15` → `files=21 verify_ok=19` and at `6e4737e` →
`files=26 verify_ok=23`). The `|| :` keeps the loop from stopping at the first refusing receipt when
`errexit` is set; see the report's Finding 4.

```bash
REV=<full40>; S=$(mktemp -d /var/tmp/souji-verifyok-XXXXXX)
hits=$(git grep -lE '^tool_sha256=[0-9a-f]{64}$' "$REV" -- census/ ':!census/operator-sweep-*' | sed "s#^$REV:##")
M=$(printf '%s\n' "$hits" | grep -c .)
N=$(printf '%s\n' "$hits" | while read -r f; do git show "$REV:$f" > "$S/r"; python3 -B tools/souji-receipt-run.py verify --root . "$S/r" </dev/null 2>/dev/null || :; done | grep -c '^verify=ok ')
echo "receipts_verify_ok=$N grep_hits=$M rev=$REV"; rm -r "$S"
```

---

## H5 — `## Planned`: r25 done entry and r26 planned line

Keep the r25 planned line where P0 put it, directly after `:134`/the r24 done line. Replacing it would
delete the frozen plan that the done entry's "Of the planned …" accounting cites. The r16–r19 and r24
pairs keep both lines. Append directly after it:

```markdown
- **r25 (planned r24) — done, see `corpus/lessons/round-25.md`:** C1 kill-rule tool row (`kill_tested=4 kill_violations=0`, rc 0; fixture {{L1: C}}/{{L1: C}}, the old tool fails k1–k4), C2 size-census refusal surfaces covered (fixture 8 → 12 cases, 12/12; the old blob fails {{L1: ids}}), C3 structure probe under the common-git-dir envelope with the colocated/plain precondition (ids 5/5 → 7/7; entry `corpus/knowledge/git-repo-structure-common-dir.md`, S124/S125), as measured in the Round 25 table. Of the r25 plan: (a) the kill rule is a tool row (C1); `corpus/README.md:40` carries an append-only superseded marker (D4); the `tool_sha256=` grep counter is replaced by the `verify=ok` count (19 of 21 at base, {{L1}} at the tip); the r23 record-agreement counter is receipted at the tip ({{L1: receipt path}}); R3 note appended (SCORECARD `blob-bound receipts (r23)` row{{L1: , LOG}}), R7 fixed in code with the coverage note in the lesson, R15/R17 docstring corrected and three fixture cases added (14/15 → 15/15); `census/round-24/size-census-lane.txt` {{L1: relabelled / still RECEIPT-MALFORMED, open}}. (b) the structure probe is under the common-dir envelope (C3); of the untested size-census contract parts only bare, subdir and partialClone-only gained cases (C2) — `census.warning=`/other-stderr exit 1, not-a-repository exit 2, hostile `core.fsmonitor`/env and a ctime or read-only-`.git` arm stay open, disclosed; the two git-2.55.0 entries were {{L1: not re-verified / re-verified}}. (c) program-position label binding was not preregistered and stays open. The r24 C3 claim is retitled to the two r23 residuals it closed (D1). No assimilation. Certification OFF, K5 HELD; F5 reap and NAMESPACE holds unchanged.
- **r26 (planned r25):** (a) calibration: preregister the remaining run/verify symmetry shapes as counter cases (R24-M25: the 19-of-36 `run`-written shapes `verify` refuses, the header forge and the quote-eating shape from `W2C3Symmetry`, and the empty-stdout refusal receipt that `run` writes but `verify` refuses with `RECEIPT-COUNTS-ABSENT`, e.g. `census/round-25/records/c1-control-base.tsv`); say in the counter whether `verify=ok` should also bind `rc=`; turn `census/round-24/size-census-lane.txt` into a v1 receipt or relabel it, if r25 did not. (b) coverage: the size-census contract parts still without a case (`census.warning=` and exit 1 on other stderr, not-a-repository exit 2, hostile `core.fsmonitor`/env, a ctime or read-only-`.git` arm against mtime-restoring writes); with the colocated/plain precondition in place, a plain-clone `git repo structure` size baseline for F2 (README `### Frontier`); re-verify `git-auto-maintenance-prunes-worktrees.md` and `git-grace-periods-and-expire-to.md` on git 2.56.0 if r25 did not. (c) operability: bind the receipt label to the program position (the interpreter's first script argument), not just argv membership. Fleet route: the LEARNING.md expansion predicate (capability vs entry-on-uncovered-ground) is still unresolved. Certification stays OFF, K5 HELD; F5 reap and NAMESPACE holds unchanged.
```

Drop any r26 clause whose r25 placeholder resolves to "done".
