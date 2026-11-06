# S70Connector — sibling overlap and cross-claim scan (round 70, read-only)

Seat: S70Connector. Scratch: `/fast/scratch/hyaku/souji-r70/S70Connector` (removed before yield).
No lane tracked file was written; no mutating git/jj command was run.

## 1. Sibling hits — pathspec-limited reads that inherit the caller's environment

Sweep: Python walk of the 12 sibling tool/script dirs under `/home/vgpnk/Projects/shokunin`
(chousa/tools, kaidoku/tools, kake/scripts, kama/tools, kotodama/tools, kumitate/scripts,
lore/corpus/tools, mado/tools, mori/tools, tabi/scripts, tameshi/tools, tsukuroi/tools):
1033 `.py/.sh/.mjs/.js` files; 14 match `ls-files|update-index|--error-unmatch`; 160 match
`ls-tree`; 6 name one of the four pathspec variables. Fleet grep for `:\(top\)` outside `.ufo`:
**zero sibling hits** (only `.ufo/reports/round-64/souji.md:9,101` and `round-65/souji.md:75,98`).

| # | sibling tool | file:line (helper) | call | inherits env? | scrubs the four? | polarity |
|---|---|---|---|---|---|---|
| 1 | kaidoku prefile-gate | `kaidoku-shokunin/tools/round-42/prefile-gate.py:311-327` (`_git` :53-64, no `env=`) | `ls-files -z -- '.ufo/waves/round-N/*.err' 'corpus/evidence/round-N/*.err'` (+`--others`) | **yes** | **no** | **vacuous pass** under `GIT_LITERAL_PATHSPECS=1`: both lists empty, stray `.err` never warned (warn slot; the hard gate at :303 is a Python `glob`) |
| 2 | kumitate round-gate | `kumitate-shokunin/scripts/round-gate.mjs:491,562` (`git` :223-227, no `env`) | `ls-files --error-unmatch -- <rel>` | **yes** | **no** — `GIT_LOCAL_ENV_VARS` :708-712 omits them; `scrubGitLocalEnv()` is called only from `selfTest()` :715 | `GIT_ICASE_PATHSPECS=1` can satisfy `--error-unmatch` on a case-differing path → `REPORT_UNTRACKED` false pass |
| 3 | tsukuroi run-receipt | `tsukuroi-shokunin/tools/run-receipt.py:90` (`env` :36-48) | `ls-files --error-unmatch -- <rel>` | no (whitelist env) | effective yes | hermetic |
| 4 | tsukuroi check-line-endings | `tsukuroi-shokunin/tools/check-line-endings-r64.py:126` (`git_env` :114-119 copies `os.environ`) | `ls-files -z` (no pathspec) | **yes** | **no** | inert (no pathspec arg) |
| 5 | kaidoku r36/r38 c2-counters, r38 gen-controls | `.../round-36/c2-counter.py:314`, `.../round-38/c2-counter.py:326`, `.../round-38/gen-controls.py:143` | `ls-files` (no pathspec) | yes | no | inert |
| 6 | kama gate-registry-check | `kama-shokunin/tools/gate-registry-check.py:120,417` (`run_git`, no `env=`) | `ls-files -z` (no pathspec) | yes | no | inert |
| 7 | mori-census | `mori-shokunin/tools/mori-census.sh:2389` via `git_cap` :591-595; `GIT_SCRUB` :580-590 | `ls-files -mo --exclude-standard` | yes, partial scrub | **no** (pathspec vars absent from `GIT_SCRUB`) | inert today; latent for any future pathspec |
| 8 | tameshi trace-inputs | `tameshi-shokunin/tools/trace-inputs.py:545`; env built :512 | `ls-files -z --cached --full-name` | no (drops all `GIT_*`) | effective yes | hermetic |
| 9 | tabi check-round-contract / check-user-round-contract | `tabi-shokunin/scripts/check-round-contract.mjs:75`, `check-user-round-contract.mjs:135` (pin `GIT_LITERAL_PATHSPECS:'1'`), `:194`/`:249` `--literal-pathspecs` | `ls-tree`/`grep` | inherits but pins literal | pins, not scrubs (literal dominates magic in git's pathspec init) | neutralized |
| 10 | kaidoku instrument-custody | `kaidoku-shokunin/tools/round-25/instrument-custody.py:119` | `ls-tree -- <path>` | pinned `GIT_LITERAL_PATHSPECS=1` | pins | neutralized |
| 11 | mori retention-reconcile | `mori-shokunin/tools/mori-retention-reconcile.py:56-57` | — | no (drops `GIT_*`) | yes + pins literal | hermetic |
| 12 | kumitate anchor-truth | `kumitate-shokunin/scripts/anchor-truth.mjs:119-125` (`GIT_ENV_KEEP`) | `ls-files` suffix resolve | no (whitelist) | effective yes | hermetic |

Secondary class — tree reads through a pathspec (160 files; `ls-tree` reads a tree, not the index,
but it is the r70 GA/ICA over-refusal route). All those helpers inherit and none scrub:
`kaidoku-shokunin/tools/round-35/c1-coverage-counter.py:38` (`git` :28-29),
`round-26/c1-id-identity.py:93`, `round-29/freeze-gate.py:161` (`git` :70-74 raises
`git_failed` — under GLOB/ICASE the honest read aborts the instrument),
`kama-shokunin/tools/report-landing-audit.py:431,681-682`.

**Net:** exactly one sibling reads the *index* through a pathspec in the forgery polarity with no
scrub (row 1, warn-level), one in the ICASE polarity (row 2), and 160 files carry the unscrubbed
tree-pathspec read. `:(top)` is unused outside souji. No sibling adopts the r70 remedy.

## 2. C1 / C2 separability

Verdict: **separable as frozen predicates; not separable as instruments.** Both receipts come from
the same counter file.

- C1 receipt `census/round-70/records/c1-after.txt` is 133 lines; its only terminal lines are
  `:131 REGRESS base=PASS new=PASS`, `:132 SUMMARY matrix=59 ... regress=PASS`, `:133 EXIT=0`. It
  contains **no** `BATTERY` or `SELFTEST` line, so the C2 payload never ran inside it.
- `census/round-70/c1-counter.py:1567-1594` decides C1: `evaluate` → `summary_line` →
  `:1588-1589 rc = 0 if claim_upheld(res) else 1` → `EXIT`. That path calls
  `selftest`/`verify_members`/`battery_verdict` nowhere.
- The battery branch is gated on `ns.battery_manifest` at `:1497`; the frozen C1 invocation has no
  such flag, and `verify_members` is called only inside it (`:1516`).
  ⇒ Reverting selftest §7, `verify_members` (`:1139`) or `battery_verdict` (`:1125`) cannot move
  C1's SUMMARY or EXIT.
- `census/round-70/c2-harness.py:125-140` invokes the counter with `--selftest` and
  `--battery-manifest` only (no `--rev`/`--tool`), and the battery members are r69 base-writer
  mutants under `census/round-69/battery`. ⇒ C2 cannot read the writer change at
  `93a051b2`; the converse direction is genuinely free.

Two couplings the prereg sentence does not name (it says only "C1 reads no selftest or battery
code; C2 reads no writer change" — literally true, so this is a disclosure, not a contradiction):

1. `clean_env()` `c1-counter.py:377-398` drops `PATHSPEC_VARS` at **`:395-396`**, and each new row
   applies its own caller env afterwards (`:726-737`). Revert `:395-396` and the 59-row verdicts
   become functions of the runner's ambient env — C1's after-arm can move with **zero** writer
   bytes changed. The scrub is therefore C1-critical code living in the counter file that C2 scores.
2. The battery scoring calls `evaluate(rows, base_slot, mpath, ...)` at **`:1533`** over the same
   59-row matrix, so the matrix/row design (12 rows added this round) is a shared instrument: a
   revert of those rows could move C2's `killed=4`.

## 3. "New ground" — `corpus/README.md:1005`

Sentence under test: "New ground: no earlier entry covers pathspec semantics as a concealment
route." Verdict: **FALSE as written** (true only if "entry" is narrowed to `corpus/knowledge/`).

Greps run at base `e063a2fcb3f5f3fb8fb19d2ae1592b1f22e6a333`:

```
git show e063a2fc:corpus/lessons/round-69.md | grep -n LITERAL_PATHSPECS
 38:- C2 (ambient): ... GIT_LITERAL_PATHSPECS=1 makes the writer's `:(top)` flag reads empty and the
     writer writes receipts over skip-worktree, gitlink, absent and unmerged rows with rc ...
 44:**Routed to round 70 ... (a) HIGH — writer: refuse or scrub GIT_LITERAL_PATHSPECS (and the other
     pathspec routes) in `tools/souji-receipt-write.py` ...
git show e063a2fc:corpus/lessons/round-69-verifier-spotcheck.md | grep -c LITERAL_PATHSPECS
 1     (line 79: "writer forges under GIT_LITERAL_PATHSPECS=1 (predates r69)")
for f in $(git ls-tree -r --name-only e063a2fc corpus/knowledge); do
  git show e063a2fc:$f | grep -qi 'LITERAL_PATHSPECS\|ICASE_PATHSPECS' && echo HIT $f; done
 (no output — zero knowledge entries at base carry the variables)
```

So at the r70 base the corpus already stated the concealment route verbatim (lesson + routed HIGH),
while `corpus/knowledge/` did not. r70's genuine delta is the four-variable set with the GLOB/ICASE
over-refusal polarity and the two negative controls (F1 `new_honest=11`, F2 `new_honest=13`) — not
first coverage of pathspec semantics.

## Findings

- **HIGH (cross-lane, not a r70-claim falsification):** `kaidoku-shokunin/tools/round-42/prefile-gate.py:311-327`
  reads the index through a glob pathspec with no env scrub; under `GIT_LITERAL_PATHSPECS=1` both
  `ls-files` calls return nothing and the stray-`.err` warning is silently suppressed. Same class as
  the r70 LD/LN4/LG1/LA9 rows, in a warning slot.
- **MEDIUM:** `corpus/README.md:1005`'s novelty clause is false against `corpus/lessons/round-69.md:38,44`
  and `corpus/lessons/round-69-verifier-spotcheck.md:79` at the r70 base.
- **LOW:** `kumitate-shokunin/scripts/round-gate.mjs:491,562` (ICASE false-pass) and
  `mori-shokunin/tools/mori-census.sh:580-590` (`GIT_SCRUB` omits the four; inert only because no
  call passes a pathspec).
- **LOW (instrument coupling):** `census/round-70/c1-counter.py:395-396` is C1-critical code in the
  counter file C2 scores; the prereg's separability sentence is true of the predicates only.

## Proposed move (one, bounded; both axes)

Amend `corpus/README.md:1005` to a delta claim — name `corpus/lessons/round-69.md:38` and the
spotcheck `:79` as prior coverage, and state the new content as the four-variable set plus the
GLOB/ICASE over-refusal and the F1/F2 negative controls — and file
`kaidoku-shokunin/tools/round-42/prefile-gate.py:311-327` as the cross-lane recheck target.
Risks: prose-only, so no frozen number moves; the land verdict is untouched (C1/C2 receipts are
byte-identical either way). Verification: the three greps above for the rewording, and the frozen
C1/C2 commands re-run unchanged, which must still print `SUMMARY matrix=59 ... regress=PASS` /
`EXIT=0` and `SUMMARY label=c2-after-r70 ... score=0` / `EXIT=0`.
