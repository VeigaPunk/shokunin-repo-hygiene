# souji-shokunin corpus

Memory of the fleet's hygiene state. Index rows are claims — write the row
when the file exists, not before.

## knowledge/

- `obsidian-ledger.tsv` — the Obsidian-preservation ledger. Columns:
  `source_path`, `source_sha256`, `vault_path`, `vault_sha256`,
  `exported_at`, `note`. A removal qualifies as `moved-to-obsidian` only
  with a matching row (both hashes). Rows enter only when the operator
  records an export; nothing automated writes here.
- (census tables land here from r1 onward) — wrong; corrected r12 below

## lessons/

- per-round training lessons, one file per round, each with a `## Gate`
  section (candidates / admitted / rejected / spot-check) — held from r12 only; corrected below

## Known gaps

- No census data yet (r1). — stale; corrected r12 below
- No gate tool yet (r2). — stale; corrected r12 below
- Numeric rubric: axis scores start at 0 with explicit counting commands;
  a calibrated numeric rubric is a standing gap, per the kotodama precedent.

## r12 additions (2026-10-19 — appended; sections above stand, corrections below)

### Admission and sources

- `QUALITY.md` — the admission bar (Q1–Q15), each criterion citing its lesson.
- `SOURCES.md` — where souji learns (contract v1): 33 rows — `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` 2026-10-19 (full census: `bash census/round-12/sources-census.sh`) — plus `## Paths`, `## Search log`.

### Coverage map

| ground | status | entries |
|---|---|---|
| receipts: pushed / moved-to-obsidian / stale | core (SKILL.md, tools/) | `knowledge/obsidian-ledger.tsv` (operator-fed, header-only) |
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md` |
| F2 repository size census | frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` → 0, 2026-10-19) | — |
| F3 duplicate verdicts | frontier, entry held | `knowledge/dupe-finders-detect-then-act.md` |
| F4 restorable quarantine, file-system semantics | frontier, entries held | `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md` |

## Frontier

- F1 git-native housekeeping vs receipts — next: does `fetch`/`merge`/`rebase` auto-maintenance prune on the fleet's live repos (exposure census, `census/round-12/scout-surfaces.md` §a: 0 prunable, 3 locked today).
- F2 repository size census — next: the /var/tmp write-safety fixture for `git repo structure`.
- F3 duplicate verdicts — next: a `duplicate` receipt class is an operator decision (taxonomy change).
- F4 restorable quarantine — next: per-item origin records (trashinfo-style) and `mv --no-copy` staging are tool changes for the operator.

### Corrections (r12)

- "No census data yet (r1)" and "No gate tool yet (r2)" under Known gaps are stale: census tables exist from r1 (`census/round-1/census.tsv`) and verdict tools from r2 (`tools/souji-verify.sh`).
- "census tables land here from r1 onward" (knowledge/) is wrong: census tables land in `census/round-<N>/` (r2's evidence is in `tests/results/`).
- "each with a `## Gate` section" under lessons/ held for none of rounds 1–11 (`grep -c '^## Gate' corpus/lessons/round-{1..11}.md` → 0 each); `lessons/round-12.md` is the first to carry it.

### Corrections (r12 post-review, 2026-10-19)

- F4's `knowledge/quarantine-same-filesystem-rename.md` is HELD, not admitted (no committed
  fixture; its `/dev/shm` device relied on QUALITY Q15, withdrawn by Q16). F4 still holds an
  admitted entry (`knowledge/trash-spec-restorable-quarantine.md`).
- `QUALITY.md` now runs Q1–Q16 (Q16 withdraws Q15).

## Round 13 current coverage (supersedes the r12 F2 row)

| ground | status | entries / runnable evidence |
|---|---|---|
| F2 repository size census | bounded structure-census capability acquired; wider size attribution remains frontier | `knowledge/git-repo-structure-readonly.md` (S035/S036/S037); `../tools/souji-repo-structure.sh`; `../tests/fixtures/r13-repo-structure.sh`; `../census/round-13/verification.json` |
| Certification evidence integrity | declared-fragment consistency only; deletion certification OFF | `../tools/souji-cert-evidence.py`; `../tests/fixtures/r13-cert-frozen/`; round-13 lesson Gate and Mistakes |
| Quarantine operation bounds | per-target move/digest bound, special-file refusal; not comprehensive certification | `../tests/fixtures/r13-quarantine-bounds.sh`; same-command red-before/after results in `../census/round-13/verification.json` |

Admission bar now includes Q17/Q18, grounded in the prior non-author
missing-fixture finding and r11 wrong-byte/shared-relay failure. K5 stays
HELD; QUALITY Q16 continues to withdraw Q15. A declared author label is
not authenticated independence and an evidence-integrity PASS is not a
safety certificate. No source-row or fixture-count increase is treated as
knowledge expansion without the sourced F2 entry.

Evidence for this round is under `census/round-13/`, with validated wave
specification/registry and author-owned reports under `.ufo/waves/round-13/`.
The untracked `census/operator-sweep-20261019/` remains operator-owned and
is excluded from round staging.


### Round 13 admission correction and observed results

The r12 coverage-map word “held” meant entries were held in the corpus, not
the later HELD rejection status: F1's two entries, F3's duplicate-finder
entry and F4's trash-spec entry are admitted. Only K5
`quarantine-same-filesystem-rename.md` is HELD. With the new F2 entry,
admitted knowledge is 4→5 (`python3 census/round-13/count-claims.py 31984f4`
and `python3 census/round-13/count-claims.py 6f8ee0f`; `counts.json`).

Actual final results: evidence selftest 36/36, external replay 5/5,
structure fixture 5/5, corrected bounds fixture baseline 1/5 PASS with two
hangs versus changed tool 5/5 PASS. Four embedded tool suites report
40/51/91/36 checks with zero failures, and `shellcheck -S warning` exits 0.
Exact commands, outputs, installed digests and per-check revisions:
`../census/round-13/verification.json`; first-pass failures are preserved
separately, not erased. Q19 replaces Q8's marker-count test with behavior
and independent expected finding ids.


## Round 14 evidence-integrity and refusal boundaries

This round works calibration and operability, not a new coverage-map ground.
No new knowledge entry is pre-admitted from source-row counts. K5 remains
HELD; F2's wider size attribution and the unexercised quarantine sites remain
frontier. Deletion certification stays OFF.

- `../tools/souji-evidence-cache.py` — declared-dependency eligibility,
  not proof of historical execution, authenticated authorship or complete
  dependency/environment capture. QUALITY Q20 and round-14 R14-M1.
- `../census/round-14/cache-demonstration.py` — synthetic harmless producer,
  authentic historical matched-only red control, migrated consumer decisions.
- `lessons/round-14.md` — named S034 source-location erratum, opened S038/S040,
  prior routed limitations and explicit admit/reject boundaries.
- Evidence and actual per-result revisions land in `../census/round-14/`;
  wave specification, unchanged dispatch, assigned registry and advisory
  reports are in `../.ufo/waves/round-14/`. A seat report is not a runtime
  observation unless it explicitly records one.

Historical `../census/round-13/verification.json` stays unchanged. Reproduce
its old counting commands at their cited measured revision, not by assuming
the current migrated runner contains the same bytes. Neither old retained
observations nor current gate declarations are silently relabelled as a
new execution. Initial operator sweep remains unread and unstaged.

### Round 14 measured outcomes

`../census/round-14/verification-attempt-1.json` preserves the failed first
integration at 48f8945; `../census/round-14/verification.json` records targeted
corrections at 552cae4. Exact commands are in each result. Unchanged earlier
passes are not relabelled: cache selftest 48/48, external fixture 22/22,
two-pin frozen snapshot clean. Corrected consumer 33/33; same boundary
fixture baseline 2/12→installed 12/12; legacy census 38/38; warning-level
ShellCheck clean. The actual source-anchor probe rejects S034 and accepts
S038 without editing the old row.

Inventory `python3 census/round-14/count-claims.py a31642d` versus the same
command on 552cae4 (`../census/round-14/counts.json`): admitted knowledge
5→5, HELD 1→1, source rows 37→40. New eligibility/protected-census
capabilities are demonstrated repertoire, not three rows counted as new
knowledge. The census's newly refused indirect configurations and filesystem
alias/race limits are explicit in SKILL and the lesson; no universal no-harm
or deletion-certification claim is inferred.

## Round 15 — outside harm repair and preservation evidence

The non-author round-14 closure rejected net operability admission as
**rejected-harmed** (`lessons/round-14-verifier-spotcheck.md`): verified
namespace gains did not cancel value-blind benign configuration refusals.
The round-14 authored descriptions above remain historical, not the current
admission verdict. `lessons/round-15.md` and QUALITY Q22–Q24 turn that
disagreement and the routed wording/process defects into explicit criteria.

C1 repairs value/effect-aware local configuration support; C2 checks
declared paired-preservation evidence independently. Final measured commands,
subject revisions and outcomes belong under `../census/round-15/`, with the
64-seat build and 32-seat falsification specifications/dispatch/seat reports
under `../.ufo/waves/round-15/`. Source-only seat reviews are not runtime
acceptance and lane-dispatched seats are not outside verifiers.

The r14 consumer observation remains actual `attempt_reuse` decisions on
synthetic records only. Neither full migrated dispatch nor positive
production retention was demonstrated. Historical JSON and original
observation revisions are preserved; code wiring is not a fresh execution.
The demonstration docstring is corrected without changing its behavior.

No new knowledge-map ground is claimed by these source or fixture additions.
Admitted knowledge stays five and K5 remains the sole HELD entry; F2's wider
size attribution and the unexercised quarantine sites remain frontier.
Certification stays OFF. The operator sweep is never staged, moved or
deleted; read-only seat query deviations against the stricter wave contract
are disclosed in the lesson and their author-owned reports, not used as
evidence for any claim.

### Round 15 final operator stop

Only the 64-seat build wave dispatched. The operator cancelled planned
wave 2 and ordered immediate landing for reboot before runtime acceptance.
C1/C2 are **unprovable, not admitted**; the candidate census must not be
treated as verified. All r15 runtime checks are UNRUN and the frozen
record retains pre-integration pins. Source validation alone exited 0;
`../census/round-15/end-sources.json` records the 42-row inventory. R14
configuration-support harm remains open. Details and exact unrun commands:
`lessons/round-15.md` Final disposition; no new capability is admitted.
