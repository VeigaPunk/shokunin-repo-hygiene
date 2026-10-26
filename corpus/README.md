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
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md`, `knowledge/git-auto-maintenance-trigger-set.md`, `knowledge/git-auto-maintenance-trigger-set-r23.md`, `knowledge/jj-keep-ref-expiry.md`, `knowledge/jj-dropped-keep-object-lifetime.md`, `knowledge/jj-abandoned-object-mtime-clock.md` |
| F2 repository size census | frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` → 0, 2026-10-19); superseded by Round 24 F2 row (:517) | — |
| F3 duplicate verdicts | frontier, entries held | `knowledge/dupe-finders-detect-then-act.md`, `knowledge/duplicate-verdict-identity.md`, `knowledge/duplicate-verdict-byte-equality.md` |
| F4 restorable quarantine, file-system semantics | frontier; layout and staging held; read-side fields admitted r24; reference writer + mechanism set admitted r27 (implementation evidence only) | `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md`, `knowledge/quarantine-staging-no-copy-r23.md`, `knowledge/quarantine-origin-record-fields-r24.md`, `knowledge/origin-record-writer-r27.md`, `knowledge/origin-record-mechanism-set-r33.md`, `knowledge/origin-record-exclusivity-r28.md`, `knowledge/origin-record-durability-r28.md` |

## Frontier

- F1 git-native housekeeping vs receipts — next: the trigger set and the measured prune are now held (round-26 entries `knowledge/git-auto-maintenance-trigger-set{,-r23}.md`, S128-S132); remaining: keep-ref expiry unmeasured, fleet exposure numerator re-census.
- F2 repository size census — next: the /var/tmp write-safety fixture for `git repo structure`.
- F3 duplicate verdicts — next: a `duplicate` receipt class is an operator decision (taxonomy change).
- F4 restorable quarantine — next: the receipt's per-item format and any staging-tool change remain operator decisions; r27 adds a pinned GLib reference writer and mechanism set, not a normative Souji format.

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
| F2 repository size census | bounded structure-census capability acquired; wider size attribution remains frontier. **r23: the read side now holds three entries** (`git-repo-structure-readonly.md`, `repo-size-census-readonly.md`, `count-objects-garbage-readings-r25.md`); the write-safety fixture and any measurement remain owed (see § Round 23) | `knowledge/git-repo-structure-readonly.md` (S035/S036/S037); `../tools/souji-repo-structure.sh`; `../tests/fixtures/r13-repo-structure.sh`; `../census/round-13/verification.json` |
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

## Round22 result-contract calibration

The existing acceptance surface is deepened, not new frontier ground:
`../tests/fixtures/r22-result-oracle.py` regrades the pinned public eighteen-step
output using `../tests/fixtures/r22-result-oracle.json` and fabricated deltas.
The current `../census/round-21/run-acceptance.py` enforces decoded scalar types,
empty summary stderr, and independently reviewed cache-check/ordered-phase
identity. S104/S105 ground the type distinction; S106 rejects treating decoder
strictness as schema validation. Current result counts and their measured
revision are recorded in `lessons/round-22.md`, never inferred from source.

The original r21 outputs/frozen inventory remain immutable at their recorded
revisions. No new knowledge path, frontier promotion, deletion authority or
F5 scope expansion follows. F5 bytes and its synthetic-only160-byte reason
boundary remain unchanged; inherited reap/NAMESPACE/exposure decisions stay
operator-owned. Certification OFF, K5 HELD.

## Non-author round22 judgment and forward hold

`lessons/round-22-verifier-spotcheck.md` records Main's negative admission judgment:
finite calibration receipts remain useful, but original independent/strict-adequacy
proof is incomplete and VOID reports do not supply it. Existing report-only accounting
is distinct from author training. Forward dispatch remains held while the inherited
policy-stop boundary is unresolved; no refused item, dead seat or workflow is reissued.


## Round22 attempt 2 — assimilated quarantine-staging ground

Two knowledge entries adopted from the `corpus-expansion-1` package
(`/home/vgpnk/Projects/shokuknow/merge/souji/`), re-grounded this round from
snapshots committed under `../census/round-22/attempt2/sources/` and gated by
`../tools/souji-gate-check.py` (2/2 entries, 8/8 register-slice verdicts):

- `knowledge/quarantine-staging-no-copy-r23.md` — the no-clobber rename
  primitive (`RENAME_NOREPLACE`, `mv --no-copy`) with the five-device
  measurement vendored and labelled, not re-run here. Sources S109–S111.
- `knowledge/quarantine-origin-record-fields-r24.md` — the restore side of a
  per-item origin record: the original path is the field restore consumes.
  Sources S112–S114 plus the existing S022 layout row.

Coverage-map effect: F4 moves from "frontier, entries held" to "frontier,
entries admitted for the staging primitive and the record read side"; the
operator still owns the record format and any staging tool change.
The lane's absent-defect register slice (8 rows) now carries a verdict each —
5 accepted with corrected quotes, 2 present, 0 refused, 1 unverifiable
(unreachable DOI). Verdict table:
`../census/round-22/attempt2/slice-verdicts.tsv`. (Corrected in round 23: this
sentence's two middle cells disagreed with the receipt until r23 — one verdict
class was undercounted and one was counted that the receipt does not hold. The
receipt above is the authority; the correction is recorded in `../LOG.md`
`Round22 attempt2 corrections`, which names both superseded cells.)

The r22 attempt-1 result-contract material above is unchanged and not
re-claimed; the non-author judgment in
`lessons/round-22-verifier-spotcheck.md` still controls that claim.

## Round 23 — record agreement, blob-bound receipts, F2 read side

| claim | axis | before → after | counting command |
|---|---|---|---|
| C1 record agreement | calibration (7) | `mismatches=6` at the base revision → `0` at the landing tip | `python3 -B tools/souji-record-agreement.py --rev <full40>` (`keys=4 records=… occurrences=… mismatches=M`, exit 0 iff M=0) |
| C2 blob-bound receipts | operability (8) | receipts carrying `tool_sha256=` under `census/`: `0` → `5`, each `verify=ok` | `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ \| wc -l` |
| C3 F2 read side | coverage (8) | registry `114 → 119` rows; F2 entries `1 → 3`; gate `entries=2 ok=2 fail=0` | `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`; `tools/souji-gate-check.py --entries … --snapshot-dir census/round-23/sources` |

**C1** is one instrument, four keys, all derived from receipts and committed bytes: K1 the r22
C1 after-state is bound to the revision SCORECARD names (`census/round-23/records/declared-evidence-after.tsv`,
rev `9301d98c…`, `assertions=63 resolved=63 skipped=40 mismatches=0`); K2 every superseded
scalar in `../LOG.md`'s round-22 section is named by a later `superseded by` line while the
filed bytes survive; K3 the register-slice tally in this file and in `lessons/round-22.md`
equals `../census/round-22/attempt2/slice-verdicts.tsv`; K4 no uncommitted round work outside
`../census/round-23/records/uncommitted-exemptions.tsv`. The base run is the do-nothing control
(`census/round-23/records/agreement-control-base.txt`), and `../tests/fixtures/r23-record-agreement.py`
rejects an always-zero emitter on eight of its nine cases.

**C2** is `../tools/souji-receipt-run.py`: a counter is re-derived at a full durable revision in a
private `--no-local` clone, and the receipt binds the revision, the tool path, the sha256 of the
bytes the command actually ran against, the argv, the exit code and redacted output. `verify`
re-reads the tree at the receipt's revision and refuses a digest that is not the committed blob
(`RECEIPT-TOOL-DIGEST-MISMATCH`). Named limit: a receipt binds bytes, not execution — a typed
receipt passes `verify`; and K4 is a worktree observation, so C1's K4 is not revision-reproducible.

**C3** adopts the `corpus-expansion-1` theme for F2's read side, re-grounded from sources opened
this round: `knowledge/repo-size-census-readonly.md` (S115–S117, installed git 2.56.0 manual pages
snapshotted under `../census/round-23/sources/` with sha256) and
`knowledge/count-objects-garbage-readings-r25.md` (S118–S119, two community pages fetched live and
kept as bounded extracts). The staged package's own-work fleet census row is **rejected**: its
evidence lives outside this repository. No fleet size figure is claimed anywhere in either entry.

### Frontier (r23)

- F2 — the read side now has entries; what remains is actable work, not reading: the `/var/tmp`
  write-safety fixture that must exclude `git fsck --lost-found` (S116), a lane-bound size/debris
  measurement of this repo (never a claim about the fleet), and the colocated/plain precondition
  from the r17 section. `alternate` object databases must be read by any size figure (S115).
- F1, F3, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.

### Round 23 corrections

- The r22 slice tally sentence above was corrected **in place** (2 present, 0 refused) rather
  than by an appended block. This departs from this file's "corrections below" convention
  deliberately: C1's K3 key reads the tally from this file and has no quoted-historical
  allowance, so a stale pair quoted in a correction block would re-open the defect. The
  superseded cells are named in words instead of numbers, and the append-only record lives in
  `../LOG.md` `Round22 attempt2 corrections`.
- The sweep for the D4 class found exactly one tally sentence (the one corrected above);
  the other r22 mentions in this file state no class counts.

## Round 24 — F2 write-safety census, coverage-map agreement, receipt verify symmetry

Appended; the sections above stand. For the entries column only, this table supersedes the F2
rows at :40 (r12 map), :68 (Round 13) and the r17 "F2 caveat" row at :217; their status prose
stays as history (:40's "frontier, no entry" is stale and superseded here). F4's r12 row
(:42) already names both F4-grounded entries and is not repeated. Landing record (r24 W2ReadmeRow / W2C2Game): the
row landed in 778747eb671f8e85ef5387bc3d7023337b30467c with the entry it names; the tool and
fixture had landed earlier (1efe406e7f39b8fe736be2a566053703a571ffc0), and
`../census/round-24/size-census-lane.txt` was a forward citation at 778747e that resolves only
from ca7fc1cb6dd1333096c6f3bdbad304686691d126 on.

| ground | status | entries / runnable evidence |
|---|---|---|
| F2 repository size census | frontier; read side (three entries, r13/r23) plus a write-safety debris census (r24 C1): `count-objects -v` read against the common git dir so a linked worktree's `garbage: 1` is not reported, `fsck` unreachable count without `--lost-found`, alternates counted; `--lost-found`, promisor/partialClone and non-repositories refused (exit 2). Fixture cases 1-6 assert the common-dir `.git` manifest unchanged across the tool run (case 7 proves the detector sees `fsck --lost-found`, case 8 rejects a stub); a tool that restores directory mtimes after writing is invisible to that manifest; the counter does not cover an `extensions.partialClone`-only repo or bare/subdirectory inputs (the tool refuses or handles them). Formerly: the 8 frozen fixture cases fence the no-write envelope; one lane-bound measurement, no fleet figure | `knowledge/git-repo-structure-readonly.md` (S035–S037); `knowledge/repo-size-census-readonly.md` (S115–S117); `knowledge/count-objects-garbage-readings-r25.md` (S118–S119); `knowledge/count-objects-linked-worktree-garbage.md` (r24, assimilated); `../tools/souji-size-census.py`; `../tests/fixtures/r24-size-census.py`; `../census/round-24/size-census-lane.txt` |
| Coverage-map agreement (calibration of this file; not a ground) | tool change, outside admission pending: `MISSING-FROM-MAP` and `DANGLING-MAP-PATH` over every table in this file whose header reads `ground` / … / `entries…` | `../tools/souji-coverage-agreement.py`; `../tests/fixtures/r24-coverage-agreement.py` |
| Receipt verify/run symmetry (r23 residuals) | runner change, outside admission pending: `verify` refuses a non-durable rev (`RECEIPT-REV-NOT-DURABLE`) and a `tool=` absent from `cmd=` argv (`RECEIPT-TOOL-NOT-IN-ARGV`) — the two counted clauses, with the five r23 receipts still verifying. Not counted by the fixture: `run` refuses `TOOL-NOT-IN-ARGV`, `TOOL-PATH-REDACTED`, `CMD-SECRET-SPANS-ARGV` and `--out` outside `/var/tmp/`; `verify` mirrors run's command refusals (`RECEIPT-COMMAND-REFUSED`), reports an unparsable `cmd=` as `RECEIPT-MALFORMED`, and reads counts only from a stdout line that starts with one | `../tools/souji-receipt-run.py`; `../tests/fixtures/r24-receipt-verify.py` |

### Frontier (r24)

- F2 — next after the write-safety fixture: put `../tools/souji-repo-structure.sh` under the same
  common-git-dir manifest the r24 fixture uses (its own manifest is rooted at `--absolute-git-dir`) (its r13 no-change result is bounded, see
  `knowledge/git-repo-structure-readonly.md`), then the colocated/plain byte-comparison
  precondition (:233-234) before any `git repo structure` size baseline. Size attribution by
  object or path stays frontier; a fleet figure stays unclaimed.
- F1, F3, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.

Routed defect from `lessons/round-23-verifier-spotcheck.md` :41 (map table versus the "read side
now holds three" prose): answered by the F2 row above, which names every F2 entry in its entries
column. C2's `MISSING-FROM-MAP` catches a grounded entry that no F<k> row's entries column
names; it does not read status prose, and an entry still named by an older F2 row (:68) stays
mapped if the r24 row drops it, so a prose/table disagreement of the r23 kind can recur
undetected (r24 W2ReadmeRow, W2C2Calib).

## Round 25 — common-directory structure census and routed-defect corrections

Appended; the sections above stand. The F2 entries below supersede only the F2 entries column at :517; its status prose stays as history. The stale r12 map status at :40 carries an appended superseded marker (R24-M2/D4), with no line added and no coverage-counter change. The F2 knowledge entry and this map row land together (Q56).

| ground | status | entries / runnable evidence |
|---|---|---|
| F2 repository size census | frontier; five sourced entries now cover the read-side facts, r24 debris counter, and r25 common-directory envelope. C2 refusal fixture: 12/12 (8 inherited plus bare/nonempty, bare/empty, subdirectory, partialClone-only); red on pre-fix 1efe406 is 11/12 (subdirectory), while the actual bare regression at 778747e is 10/12 (bare cases 9–10). Seven of twenty tool-clause mutants survive the 12-case fixture; their survivors are disclosed in `corpus/lessons/round-25.md`. C3 structure fixture: selftest=PASS ids=7/7 (was 5/5), including common-dir and colocated/plain checks. Limits: the r25 fixture checks exit/stderr but not manifest equality on cases 11–12; atime/ctime are excluded; content changes remain detected by hashes, but transient byte-identical writes/deletes with restored directory mtime can escape. No size baseline, deletion authority, or F2 promotion to Core is claimed. | `knowledge/git-repo-structure-readonly.md` (SOURCES S035–S037); `knowledge/repo-size-census-readonly.md` (S115–S117); `knowledge/count-objects-garbage-readings-r25.md` (S118–S119); `knowledge/count-objects-linked-worktree-garbage.md` (SOURCES S120–S123); `knowledge/git-repo-structure-common-dir.md` (SOURCES S124–S126); `../tests/fixtures/r24-size-census.py`; `../tests/fixtures/r13-repo-structure.sh`; `../census/round-25/sources/` |

### Frontier (r25)

- F2 — the common-directory no-write envelope and colocated/plain precondition are now measured for the r13 structure probe. Next: one lane-bound structure baseline from a plain `--no-local` clone (this lane is jj-colocated, so its `refs/jj/keep/*` refs make its own figures non-comparable to plain); include alternates and retain the fixture manifest. Size attribution by object/path and any fleet figure remain frontier/unclaimed.
- F1, F3, F4 — unchanged. F5 stays list-only; reap and NAMESPACE remain operator-held. Certification OFF, K5 HELD.

### Round 25 corrections and limits

- R24-M25 title overclaim: the r24 receipt change closes R1 (non-durable `verify` revision) and narrows R2 (`tool=` occurs in `cmd=` argv); it does not establish general `run`/`verify` symmetry. Further R2/R3/R7/R15/R17 shapes remain disclosed in `corpus/lessons/round-25.md`.
- R3: the old `tool_sha256=` grep is a candidate-file count, not a verified-receipt count. At base a6d2d15, `git grep -lE '^tool_sha256=[0-9a-f]{64}$' a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe -- census/` finds 21 tracked files; 19 verify, while two false positives are malformed/non-receipt files. A verify=ok result binds labelled committed bytes, not the executed program or command success.
- D6: `census/round-24/records/slice-verdicts.tsv` is the authoritative gate table; `.ufo/waves/round-24/assimilation/slice-verdicts.tsv` is the detailed reading. Both point to the mapping and vocabulary in `corpus/lessons/round-25.md`; rows are joined by (souji, campaign-id), never bare S-id. Q57's executable check and limits are recorded there.
- superseded by corpus/README.md:504; correction in corpus/lessons/round-25.md § R24-M25: R1 closed, R2 narrowed; general verify/run symmetry is not established.
- superseded by corpus/README.md:519; correction in corpus/lessons/round-25.md § R24-M25: the two measured refusal clauses do not witness the run-side and verify-side refusal matrix.
- R3 correction for the historical sentence at corpus/README.md:471-472: `tool_sha256` binds the labelled committed file bytes and argv text, not the executed program; full correction in corpus/lessons/round-25.md.

## Round 29 — F3 duplicate verdicts re-grounded

Appended; the sections above stand. Two knowledge entries are admitted for F3, re-grounded
this round from the four probe rows S216–S219 opened this round, snapshotted under
`../census/round-29/sources/` and gated by `../tools/souji-gate-check.py`:

- `knowledge/duplicate-verdict-identity.md` — `link(2)`/`statx(2)`: a second name for an
  existing file works exactly as the original name and no name is the original, so a
  duplicate verdict compares identity — the `stx_ino` and `stx_nlink` fields of
  `struct statx` — not path strings; Broder's resemblance and containment enter as
  vocabulary only. Sources S216, S217, S218.
- `knowledge/duplicate-verdict-byte-equality.md` — `cmp(1)`'s three-valued exit contract
  ("Exit status is 0 if inputs are the same, 1 if different, 2 if trouble.") plus the same
  identity rule; supersedes nothing. Sources S219, S218.

Coverage-map effect: the F3 row at `:41` now reads "frontier, entries held" and names all
three F3 entries. F3 stays frontier — no `duplicate` receipt class is created (taxonomy
change, operator decision), no near-duplicate threshold is admitted, and no tool changes.

### Frontier (r29)

- F3 — the identity half and the byte-equality half are now held as entries, and a SKILL
  classify row states the rule; remaining: a `duplicate` receipt class is an operator
  decision (taxonomy change), and any near-duplicate measure or threshold is outside this
  frontier's byte-identical scope (the Broder rows are vocabulary only).
- F1, F2, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.

### Round 29 corrections

- The r12 F3 row at `:41` was replaced in place rather than superseded by a later table:
  its status cell changed from "frontier, entry held" to "frontier, entries held" and its
  entries cell gained `knowledge/duplicate-verdict-identity.md` and
  `knowledge/duplicate-verdict-byte-equality.md`. Map rows are edited in place (r28 did the
  same to the F4 row at `:42`); the append-only record is this section.
- The `## Frontier` bullet at `:48` stands as written: "a `duplicate` receipt class is an
  operator decision (taxonomy change)" remains the next step; the r29 entries do not take it.

## Round 30 — F1 keep-ref expiry measured

Appended; the sections above stand. One knowledge entry is admitted for F1, measured this round
with real jj 0.45.1 and git 2.56.0 in scratch repositories under the round's scratch root, never
against a lane:

- `knowledge/jj-keep-ref-expiry.md` — what removes a `refs/jj/keep/*` ref and when. One run of
  an eight-step fixture (steps 1-5 on a main repository, steps 6-8 on a control repository):
  `git gc --prune=now` leaves the keep ref naming the abandoned commit in place,
  `jj util gc --expire=now` removes it, and `jj op abandon ..@-` before a second
  `jj util gc --expire=now` leaves two keep refs where eight stood. The commit object stayed
  present in every step, so a dropped keep ref is not a deleted object and the object-prune
  clock is a separate question. The default threshold is two weeks, and `--expire` accepts only
  the string `now`; a future timestamp is refused, so the "not yet expired" arm is the default
  run. Fixture `../tests/fixtures/r30-jj-keep-expiry.sh`; measured record
  `../census/round-30/records/jj-keep-expiry-run.txt` (`jj-version: jj 0.45.1`, eight `RESULT`
  lines).

Coverage-map effect: the F1 row at `:39` now names a fifth entry with its status cell unchanged
(`frontier, entries held`); the four entries it already carried are unchanged. F1 stays
frontier — the entry measures a ref's lifetime, and one entry does not promote a frontier ground
to Core (PROVINCE `## Round 30 boundary note`).

### Frontier (r30)

- F1 — keep-ref expiry is now measured (the entry above; jj 0.45.1, eight `RESULT` steps,
  `../census/round-30/records/jj-keep-expiry-run.txt`). Remaining: the fleet exposure numerator
  re-census named at `:46`; and, disclosed rather than measured here, when the commit object
  behind a dropped keep ref is pruned by git's own clock — the run records `object_present=yes`
  at every step and stops before that question.
- F2, F3, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.

### Round 30 corrections

- The r12 F1 row at `:39` was replaced in place rather than superseded by a later table: its
  entries cell gained `knowledge/jj-keep-ref-expiry.md` and its status cell, already
  `frontier, entries held`, was not reworded. Map rows are edited in place (r28 did the same to
  the F4 row at `:42`, r29 to the F3 row at `:41`); the append-only record is this section.
- `knowledge/jj-colocation-receipts.md` §3 marked the keep-ref timing `[INFERENCE]` and its
  `Limits` first bullet said the docs read do not state the lifetime. The r30 entry now carries
  the measured timing (ref removed by `jj util gc` with the operation log still naming the
  commit); the r17 text stands as history and is not rewritten. What remains unmeasured is the
  object-prune clock, not the ref's removal.

## Round 31 — F1 object lifetime behind a dropped keep ref

Appended; the sections above stand. One knowledge entry is admitted for F1, measured this round
with real jj 0.45.1 and git 2.56.0 in scratch repositories under the round's scratch root, never
against a lane:

- `knowledge/jj-dropped-keep-object-lifetime.md` — what keeps an abandoned commit's object
  present after its own keep ref is gone, and what removes it. Three arms of a seventeen-step
  fixture, each in its own colocated repository under the round's scratch root: `solo` (A, then B
  on A, B abandoned, nothing built on B), `descendant` (A, B, C on B; B abandoned while C stays
  alive) and `reflog-only` (the keep refs dropped by hand instead of by jj). In every arm B's own
  keep ref goes and B's object stays. In `solo` and `descendant` the ref goes under
  `git pack-refs --all` with `jj util gc --expire=now`, and B then survives `git gc --prune=now`,
  `git reflog expire --expire=now --expire-unreachable=now --all` before another
  `git gc --prune=now`, and `jj op abandon ..@-` with a third `jj util gc --expire=now`. Each arm
  isolates one holder: in `solo` B goes only when the keep refs whose commits descend from B are
  deleted and git is pruned; in `descendant` only when C is abandoned and the operation log
  dropped; in `reflog-only`, where no keep ref names B or a descendant of B, only when the reflog
  entries naming B are expired before the prune. So a dropped keep ref leaves the object held by
  a descendant's keep ref, by a reflog entry naming it, or — sourced from git-gc(1) rather than
  measured here — by its own modification time inside the two-week `gc.pruneExpire` window.
  Presence is not a receipt: a `git cat-file -e` that succeeds says no deletion has completed,
  and a receipt that cannot name both the reflog expiry and the prune date has not established
  one. Fixture `../tests/fixtures/r31-jj-object-clock.sh`; measured record
  `../census/round-31/records/jj-object-clock-run.txt` (`jj-version: jj 0.45.1`,
  `git-version: git version 2.56.0`, seventeen `RESULT` lines, deterministic across runs).

Coverage-map effect: the F1 row at `:39` now names a sixth entry with its status cell unchanged
(`frontier, entries held`); the five entries it already carried are unchanged. F1 stays frontier
— the entry closes the object-prune question, and a measured edge class does not promote a
frontier ground to Core (PROVINCE `## Round 31 boundary note`).

### Frontier (r31)

- F1 — the ref's removal is measured (`knowledge/jj-keep-ref-expiry.md`) and so is the object's
  lifetime behind it (the entry above; `../census/round-31/records/jj-object-clock-run.txt`).
  Remaining: the fleet exposure numerator re-census named at `:46`; and, disclosed rather than
  measured here, which reflog file carries the entry that names B, whether git's cruft-pack
  handling changes the mtime keeper's reach, and the real 90/30-day windows (sourced from
  git-reflog(1) and the `gc.*` config, not waited out by any arm).
- F2, F3, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.

### Round 31 corrections

- The r12 F1 row at `:39` was replaced in place rather than superseded by a later table: its
  entries cell gained `knowledge/jj-dropped-keep-object-lifetime.md` and its status cell, already
  `frontier, entries held`, was not reworded. Map rows are edited in place (r28 the F4 row, r29
  the F3 row, r30 this row); the append-only record is this section.
- The r30 boundary note (`PROVINCE.md` `## Round 30 boundary note`) said "the object-prune clock
  that follows a dropped keep ref is unmeasured here", and the r30 `### Frontier (r30)` bullet
  disclosed the same gap. Both stand as history and are not rewritten; the r31 entry is that
  clock's measurement, and the r31 boundary note records the closure.
- The r30 keep-ref section's eight-step description of its own record is unchanged here. What r31
  adds about that record is the packed-ref correction already carried by
  `knowledge/jj-keep-ref-expiry.md` `## Round 30 wave-2 corrections` and now stated in
  `SKILL.md`: a packed keep ref skips the loose-ref age gate, so packedness — not the `--expire`
  threshold — is what the r30 record discriminates.
- Wave-2 corrections (append-only; `census/round-31/waves/w2/SwarmCritic21.md` findings 2-3): the F1 frontier line at `:46` (r12 section) still reads "remaining: keep-ref expiry unmeasured, fleet exposure numerator re-census" and is superseded by `### Frontier (r30)` and `### Frontier (r31)` above — keep-ref expiry was measured in round 30 and the object lifetime behind it in round 31; the remaining F1 item is the fleet exposure numerator re-census. "Closes the object-prune question" above overstates: the object's own mtime clock (`gc.pruneExpire`) is sourced, not measured, and the round-31 run isolates the descendant keep ref and the reflog entry only.

## Round 32 — F1 the abandoned object's own mtime clock

Appended; the sections above stand. One knowledge entry is admitted for F1, measured this round
with real jj 0.45.1 and git 2.56.0 in scratch repositories under the round's scratch root, never
against a lane:

- `knowledge/jj-abandoned-object-mtime-clock.md` — how an abandoned commit's object dies by its
  own modification time once neither a keep ref nor a reflog entry names it. Five arms of one
  fixture, each in its own colocated repository, with the `refs/jj/keep/*` refs and the reflog
  entries naming the object already gone: `recent` (a just-created object), `old` (backdated by
  `touch -d` on the object's loose files), `mixed` (an old object and a recent one in one
  repository), `never` (`gc.pruneExpire=never`) and `nocruft` (`gc.cruftPacks=false`). The
  record's `where` field is what separates an object kept loose from one kept inside a cruft
  pack, whose `.mtimes` file carries the clock per object — sourced in the entry's Gate, not
  measured by any arm. The measured lines are
  `RESULT arm=recent step=gc-default obj=B mtime=recent where=cruft object_present=yes`,
  `RESULT arm=old step=gc-default obj=B mtime=old where=absent object_present=no`,
  `RESULT arm=mixed step=gc-default obj=B mtime=old where=absent object_present=no`
  and `obj=C` in the same step, `RESULT arm=never step=gc-pruneexpire-never obj=B mtime=old where=cruft object_present=yes`
  and `RESULT arm=nocruft step=gc-cruft-disabled obj=B mtime=old where=absent object_present=no`.
  Fixture `../tests/fixtures/r32-jj-mtime-clock.sh`; measured record
  `../census/round-32/records/jj-mtime-clock-run.txt` (`jj-version: jj 0.45.1`,
  `git-version: git version 2.56.0`, 22 `RESULT` lines, deterministic across runs and held to
  `../census/round-32/c3-contract.txt` by the C3 counter's L14).

Coverage-map effect: the F1 row at `:39` now names a seventh entry with its status cell unchanged
(`frontier, entries held`); the six entries it already carried are unchanged. F1 stays frontier —
a measured edge class does not promote a frontier ground to Core (PROVINCE
`## Round 32 boundary note (F1 mtime clock)`).

### Frontier (r32)

- F1 — the object's own mtime clock is now measured (the entry above;
  `../census/round-32/records/jj-mtime-clock-run.txt`), including the question the r31 section
  left open: whether git's cruft-pack handling changes that keeper's reach. Remaining: the fleet
  exposure numerator re-census named at `:46`, and the classes the entry's own limits section leaves
  open — no lane or fleet repository gc'd, the mtime keeper not isolated against a live keep ref or
  a reflog entry, the `never` asymmetry read from the docs rather than implemented, and the two-week
  window sourced rather than waited out.
- F2, F3, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.

### Round 32 corrections

- The r12 F1 row at `:39` was replaced in place rather than superseded by a later table: its
  entries cell gained `knowledge/jj-abandoned-object-mtime-clock.md` and its status cell, already
  `frontier, entries held`, was not reworded. Map rows are edited in place (r28 the F4 row, r29
  the F3 row, r30 and r31 this row); the append-only record is this section.
- The r31 section's `### Frontier (r31)` disclosed "whether git's cruft-pack handling changes the
  mtime keeper's reach" as unmeasured, and its wave-2 correction said the object's own mtime clock
  (`gc.pruneExpire`) "is sourced, not measured". Both stand as history and are not rewritten; the
  r32 entry is that clock's measurement, and `PROVINCE.md` `## Round 32 boundary note (F1 mtime
  clock)` records the closure.
- The r31 C3 record printed `arm=reflog-only`, which is outside its frozen contract's two arm
  values (`solo`, `descendant`), and the deviation was disclosed only after landing (r31 closure
  routed defect 3, class D1). The record is not rewritten: it stands as landed, and the r31 section
  above stands with it. What changes is instrumentation — `tools/souji-record-contract.py` now
  fails that shape over the r31 record and the reconstructed r31 contract (four `BAD` lines 16-19
  naming `arm=reflog-only`, then `lines=17 bad=4`, exit 1;
  `../census/round-32/records/m1-red-before.txt`), and the r32 C3 counter's L14 holds this round's
  record to `../census/round-32/c3-contract.txt` as frozen at the preregistration.
- Wave a2w1 (`.ufo/waves/round-32/a2w1/SwarmCritic20.md` F13-F14) corrects the `### Frontier (r32)`
  list above: the entry's limits section leaves seven classes open, not four — add the unread `.mtimes`
  contents, the unopened cruft-call argument and `gc.recentObjectsHook`. Both `never` levers are implemented
  and measured (the `never` arm's `gc-pruneexpire-never` step and the `mixed` arm's `gc-prune-never` step);
  what stays documentary is why the flag's date reaches the repack call, which a trace shows and this round's
  record does not carry. The entry's own append-only corrections block lists the remaining sentence fixes.
- Wave a2w1 (`.ufo/waves/round-32/a2w1/SwarmReviewer27.md` finding 6): the `## Round 32` section's
  `jj-version: jj 0.45.1` is a truncated quote; the record's first line is
  `jj-version: jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`.
