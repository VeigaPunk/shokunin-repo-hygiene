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

- `QUALITY.md` — the admission bar (Q1–Q15 at r12; Q1–Q26 since r16; Q1–Q28 since r17, see the Round 16 and Round 17 sections), each criterion citing its lesson.
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
admitted knowledge is 4→5 (`python3 census/round-13/count-claims.py 31984f473ce4bdab61a99b16cca194b28108cb81`
and `python3 census/round-13/count-claims.py 6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6`; `counts.json`).

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

Inventory `python3 census/round-14/count-claims.py a31642d14006830ec62edf40b0354c3699728c4a` versus the same
command on `552cae4204b3ab818419ad8adbfef3a4da29a3e0` (`../census/round-14/counts.json`): admitted knowledge
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

## Round 16 — repair first: parsing census, landing gate, checker executed

Correction to the r15 section above: the r15 candidate census **did not
parse** (`bash -n` rc 2 at line 1368); it was known broken, not merely
unverified (`lessons/round-16.md` Corrections). Round 16 restored a parsing,
value/effect-aware census (C1) and added a landing-claim gate (C2); it
executed the r15 preservation checker for the first time (24/47 → 47/47)
and regenerated its frozen record from real runs (R4), and audited seat
transcripts (R5). Measurements, revisions and residual contractions are in
`lessons/round-16.md`; round evidence sits under `../census/round-16/` and
wave specifications, dispatch and seat reports under
`../.ufo/waves/round-16/`. `QUALITY.md` now runs Q1–Q26 (Q25 landing
claims, Q26 transcript-audited probe rule). SOURCES gains S043–S050 (six
mined, two rejected). No frontier row advances and no knowledge entry is
added: admitted knowledge stays five, K5 HELD, certification OFF.

## Round 17 — jj-colocated lane repos (bounded receipt-root rule Core; F1 stays frontier)

Supersedes the r12 F1 row (:39) and the F1 next-step (:46) for the
jj-colocated subset only; both stand unchanged for plain repos. Landing
condition (index rule at :3-4): this section and its Core marking land
only in the same commit as `knowledge/jj-colocation-receipts.md` and the
SKILL jj rule; otherwise ship the variant-B row below and F1-jj stays
frontier.

| ground | status | entries / runnable evidence |
|---|---|---|
| F1-jj jj-colocated lane repos (edge class of F1) | Core (candidate, admission pending closure): bounded receipt-root rule — durable roots exclude exactly `refs/jj/*`; keep-only novel-content refusal; plain repos byte-identical. F1 itself stays frontier; keep-ref expiry unmeasured | `knowledge/jj-colocation-receipts.md`; `../tests/fixtures/r17-jj-receipts.sh`; `../census/round-17/jj-receipts-base5fa6017.txt`, `../census/round-17/jj-receipts-4f48343.txt` (changed arm 0 failed; r18 correction: was a `ddb7347` record name never committed) |
| F2 caveat, disclosed only: colocated repos inflate structure counts versus a plain clone (`references.others.count` 15 from `refs/jj/keep/*`; `objects.commits.count` 55 vs 44, sandbox) — no F2 capability claimed | observed, not claimed | `../../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` step 5; `../../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` F3 |

Disclosure carried with the row, not in a footnote: the census `unpushed`
column is branch-based and reads 0 while this lane holds keep-only commits
(structural pair, measured at d7e648d: `git rev-list --count --branches
--not --remotes` → 0; `git for-each-ref refs/jj/keep` refs that are not
ancestors of `master` → 13 of 17). An absent-worktree head held only by a
keep ref is NOT-SAFE, never `SAFE(metadata-prune)`.

### Frontier (r17)

- F1 — plain repos: unchanged (:46). jj-colocated residue: a keep-ref
  expiry measurement (no jj doc read states when jj drops
  `refs/jj/keep/*`; entry Limits) — unrun. The conservative-refusal cost
  stays disclosed, not narrowed: a rewritten predecessor jj hides can
  refuse an artifact no branch carries.
- F2 — unchanged (:47); a colocated/plain byte-comparison is a
  precondition for any `git repo structure` baseline.

## Round 18 — bounded fleet readers, evidence pointers, process residue (F5 opened)

| ground | status | entries / runnable evidence |
|---|---|---|
| Bounded census reads (Core census surface; not F2) | Core tool change, outside admission pending: every repository runs in its own process group under `--repo-timeout`; a post-guard FIFO swap or a static work-tree FIFO is an `error` row instead of a hung fleet run. No knowledge entry — sources S064–S066, S070 cited in the lesson | `../tests/fixtures/r18-census-bounded.py`; `../census/round-18/c1-matrix-worktree.json`; `lessons/round-18.md` |
| Evidence-pointer integrity (calibration of authority files) | gate change, outside admission pending: `LG-DANGLING-PTR` at round ≥ 18; exemptions committed with reasons | `../tools/souji-landing-gate.py`; `../tests/fixtures/r18-landing-pointers.py`; `../corpus/pointer-exemptions.tsv`; `../census/round-18/gate-pointers-before-b576341.json` |
| F5 process residue | frontier (tool + gate, no knowledge entry): own-uid residue listed, never signalled | `../tools/souji-proc-census.sh`; `../tests/fixtures/r18-proc-census.sh`; `../census/round-18/leak-count.py`; `../census/round-18/proc-census-live-1721.tsv` |

### Frontier (r18)

- F5 — next: a knowledge entry (sources S067–S069 opened) and an
  operator-approved reap protocol bound to (pid, starttime, boot_id); the
  58 souji fixture orphans listed at round start await that ruling.
- F1, F2, F3, F4 — unchanged.

### Final round-18 evidence after falsification

- Census scope is repository-content reading after enumeration, not a
  filesystem/PID sandbox. Final B1–B12: b576341 9 failed →4800fd7 0;
  selftest 49→69; old hygiene/config/namespace suites retain 0 failures
  with the pinned r14 fixture restored. See
  `../census/round-18/c1-matrix-4800fd7.json`.
- Landing gate: selftest 61/0; pointer fixture 11/0; final grammar adds
  quarantine metadata and exact placeholder binding. Seven invalid
  teaches extrapolations got append-only source corrections S072–S078.
- F5 remains frontier/observed, not Core: proc fixture 19/0; literal live
  deleted-suffix names, missing redactions and a counter ancestor-exclusion
  mismatch were repaired. Two final 66=66 pid-identical snapshots are in
  `../census/round-18/proc-agreement-counterfix.json`. The older 65=65
  snapshot is historical, not a promise of constant live counts.
- `../census/round-18/final-verification-4800fd7.json` preserves every L1
  acceptance command/output/exit; raw seat-audit failures and adjudications
  are retained rather than represented as a clean transcript audit.

## Round 19 — F5 first knowledge entry; carry, audit and revision truthfulness

| ground | status | entries / runnable evidence |
|---|---|---|
| F5 process residue | **Core for the observation surface** (outside admission pending): first admitted `knowledge/` entry, list-only, no reap authority | `knowledge/process-residue-observations.md` (S082–S085; S075/S076 rechecked); `../tools/souji-proc-census.sh`; `../tests/fixtures/r18-proc-census.sh` |
| Carry truncation (landing gate) | gate change, outside admission pending: paragraph-aware match, strict branch at `--round >= 18` | `../tools/souji-landing-gate.py`; `../tests/fixtures/r19-carry-wrap.py`; Q36 |
| Durable revision stamps | helper + runner change, outside admission pending: durable-ref and tracked-tree binding, exit 2 with no record | `../tools/souji-rev-pin.py`; `../tests/fixtures/r19-rev-pin.py`; Q37 |
| Seat-audit authorized shapes | gate change, outside admission pending: exact patch/workdir predicates and `V-SIGNAL` | `../tools/souji-seat-audit.py`; `../tests/fixtures/r19-seat-audit-shapes.py`; Q38 |

### Frontier (r19)

- F5 — reap protocol still awaits the operator ruling (L0 `souji | round-16`); the entry grants no reap authority and the listed fixture orphans remain unreaped.
- F1, F2, F3, F4 — unchanged.

Correction to the r18 section above: "admitted knowledge stays five" is wrong. The lane's own
counter (`python3 census/round-13/count-claims.py b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`) reports **6** admitted entries —
eight files under `knowledge/` minus the `.tsv` ledger and the single HELD entry
(`quarantine-same-filesystem-rename.md`). R19's C3 measurement is therefore **6 → 7**, not
5 → 6; the r18 prose is a historical counting defect (R19-M1).

## Round 20 — current replay contract and prior harm correction

The round-19 outside decision is **rejected-harmed** (`lessons/round-19-verifier-spotcheck.md`),
not pending or admitted. Its F5 observation entry remains useful; its blanket sibling-artifact
grant and un-migrated short-ID commands were harms, and its measured-input guarantee was incomplete.
The acceptance at `bbeb73bd4dad181b9b293b242dbf5749acbe3568` was 18/18 at those bytes,
not final-tip-wide evidence. Round20's exact repair evidence belongs under `../census/round-20/`;
no old receipt is rewritten.

### Current full-ID counter commands (also migrated in executable examples above)

Run from the lane root. These are current replacements, not re-executions attributed to old rounds:

```sh
python3 census/round-13/count-claims.py 31984f473ce4bdab61a99b16cca194b28108cb81
python3 census/round-13/count-claims.py 6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6
python3 census/round-14/count-claims.py a31642d14006830ec62edf40b0354c3699728c4a
python3 census/round-14/count-claims.py 552cae4204b3ab818419ad8adbfef3a4da29a3e0
python3 census/round-13/count-claims.py b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
```

The historical LOG, old lessons and `counts.json` command strings retain their filed bytes;
this index is their named current replacement. README executable examples now use full IDs.
HEAD, branches, short IDs and keep-only revisions remain refused; a historical counter reads committed bytes, not the current corpus. A measurement
runner instead must bind all actual owned working-tree inputs; merely adding a durable stamp is
insufficient. SOURCE-only statements are narrowed by S091–S093, with selector semantics in S089.

### F5 precision and held requests (supersedes broad r19 wording)

F5 stays **list/nominate only**: `bash tools/souji-proc-census.sh` emits eligible readable own-uid
observations and never signals in census mode. Self/descendants recognized by the bounded
parent-chain snapshot are excluded, and unreadable/racing data skipped; no universal per-process coverage is promised. Raw argv is read before output redaction;
neither a secret-free read nor universally redacted derived output is established. The live
r18 proc fixture is historical and was NOT run or newly authorized in r21; current reason
output is rechecked only through the synthetic --reason-only entry point (below).
The corrected source and byte boundary are appended in `knowledge/process-residue-observations.md`.
Other-uid work is not assigned wholesale to Mori; health/liveness findings may be routed there and
credential concerns to Kagi, with operator arbitration for contested scope.

The specific open requests are `souji | round-18` F5 reap and NAMESPACE_SHA256, not the broad
round16 pointer above. Both remain HELD. A historical58-orphan observation is not a current count
or authority to kill/delete. Certification OFF, K5 HELD, F1–F4 unchanged.

## Round 21 — current reason privacy and independent-path replay

R20 is independently admitted (CloseSouji20, MANIFEST rounds[402]); its closure
is retained at `../census/round-21/r20-closure-excerpt.json`. R21 sources
S100/S101 deepen the existing F5 entry, not a new knowledge pathname/frontier
promotion. The two arbitrary-input output sinks cmd/reason now have shared
secret patterns and160-byte bounds; selected secret-bearing argv provenance
cannot be lost when extracting the reason path. Same27-case oracle:
old6/27 (19 canary leaks) → changed27/27 (0), maximum454→160 bytes.

Current proc-free recheck (extract the old base tool with read-only
`git show 6ff3413bba9c8430c3b0bc4d2052e21d0407183f:tools/souji-proc-census.sh`
into a new scratch file):
`bash tests/fixtures/r21-reason-canary.sh --tool tools/souji-proc-census.sh --base <base-file>`.
Neither this command nor --reason-only reads live /proc. It does not reverify
the entire process scanner, historical exposure or unknown secret syntax.

Current acceptance:
`python3 census/round-21/run-acceptance.py --root <local-clone-or-bare-repository> --rev <full40> --output <new-absolute-file>`.
It runs the fixed18 outcomes in a private no-local clone at the named
revision; caller HEAD/path is not authority. Three-source matrix0/3→3/3,
each18/18 at `4b826a52cb4519b413b874fc9a3d26074c8a33b6`:
`../census/round-21/replay-integrated.txt` and `replay-out-S{1,2,3}.json`.
The r20 runner is retained only as historical evidence; its root/HEAD
restrictions are not a current executable example. The historical agreement
step verifies original revision bytes against the original pin, not the
upgraded proc tool against an old digest. Equal outcomes are not a
bit-identical reproducible-build claim (rejected S103).

Calibration: `../tests/fixtures/r21-read-root.py`32/32 (base18/32), with14
base discriminators. The minor V-READ-ROOT class supplements V-RECURSIVE;
truncated paths remain unknown. Claimed actual r20 transcript counts are
bound in `../census/round-21/read-count-{before,after}.json` (0→2 new flags,
all other class counts unchanged). Q47–Q50 mine the routed r20 mistakes;
`lessons/round-21.md` carries exact source quotes and final dispositions.

### Final r21 correction and measured scope

The earlier128-file census is partial, not final. Original raw-export scope
is restored:192 `.txt` files,3539 tool calls,2372 read/grep/glob keys.
`../census/round-21/oracle-acceptance.json` has tp3/fp0/fn0/missing0/extra0;
the3 raw-export flags are2 distinct attempted reads. All401 prior
per-call verdict tuples are identical. Oracle provenance is1942 direct
independent classifications plus430 byte-identical-call transfers; seven
post-predicate labels and one incorrectly labelled Bash call are excluded.

Final code pin: `195715439a08165ed7319ee6348844fcfba60029`.
`../census/round-21/accepted-matrix.json` records3/3 source shapes, each18/18
under the fixed original r20 predicates. An unborn-HEAD remote-ref-only
source also replays18/18; jj-only source remains exit2/no result
(`remote-source-after.json`, `final-code-verification.json`). Source remote
roots are mapped only into the private clone; source_sample_unchanged
describes sampled fields, not whole-source integrity or cleanliness.

The same final verification records32/32 read controls,4/4 renderer edges,
27/27 reason canaries,8/8 output boundaries and3/3 source-HEAD controls.
Baseline inputs now have exact committed-source digest guards. Four
mutation probes kill the read-class, reason-mask, argv-provenance and
outside-source-output mutants. No live process census was run; the
disclosed seat snapshot-search violation means this is not a scope-clean
process round. Existing inherited r20 result-predicate limitations remain
explicit in the lesson, outside the portability claim.
