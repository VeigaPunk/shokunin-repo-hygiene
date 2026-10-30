# Round 43 — souji lesson

Round: 43. Attempt 2 inherits instruments from attempt 1. Claims: C1 calibration (three historical self-assessment corrections), C2 operability (freeze-check grammar), C3 coverage (drift survivor fixture and leaf-symlink refusal). Formal registration: `census/round-43/preregistration.txt`, committed at `8dfad888d7b7673de41cdcd92f30244c16e38519`. Lowest non-retired axis is calibration 7; operability 8 and coverage 8 remain non-normalized scores, not earned numeric deltas.

## Historical self-assessment corrections (C1)

These correct the dated records at revision `0242085909fb6a4ee041c5443d76316ac6d59d4b`, not the present registry. The SOURCES S-row population at that revision is 174; its duplicated-URL warning population is 48. The receipt `census/round-39/records/census-after.txt` carries stale 173/47. The file `census/round-39/records/final-tip-measure.txt` names the measured revision `544104503a3ad70687ba399fcafd12bd30648169`, not its later carrier revision. Its instrument scope is `census tools tests`; these lines do not establish the current registry census or current tool behavior. Re-derivation command: `python3 -B census/round-43/c1-counter.py --root LANE --rev FULL40 --scratch SCRATCH`.

CORRECTION-R39 id=R43-D1 file=census/round-39/records/census-after.txt field=rows stale=173 derived=rows=174 rev=0242085909fb6a4ee041c5443d76316ac6d59d4b
CORRECTION-R39 id=R43-D2 file=census/round-39/records/census-after.txt field=W04 stale=47 derived=W04=48 rev=0242085909fb6a4ee041c5443d76316ac6d59d4b
CORRECTION-R39 id=R43-D3 file=census/round-39/records/final-tip-measure.txt field=header-rev stale=0242085909fb6a4ee041c5443d76316ac6d59d4b derived=544104503a3ad70687ba399fcafd12bd30648169 rev=0242085909fb6a4ee041c5443d76316ac6d59d4b

## Gate

Opened by SoujiR43a2 on 2026-10-30:

- **Admit S260**, https://man7.org/linux/man-pages/man2/symlink.2.html, Linux man-pages 6.19 (2026-02-08), DESCRIPTION dangling-link paragraph: “A symbolic link (also known as a soft link) may point to an existing file or to a nonexistent one”. This grounds C3's requirement to refuse a dangling as well as existing-target leaf symlink. It supplies no deletion receipt or race-proofness claim.
- **Admit S261**, https://docs.python.org/3/library/subprocess.html, served Python 3.15.2, `subprocess.run` env paragraph: “these are used instead of the default behavior of inheriting the current process’ environment.” `CompletedProcess.stderr`: “Captured stderr from the child process.” Separate stderr capture grounds C3 traceback attribution; the harness must distinguish a traceback naming the fixture from forwarded tool diagnostics. Environment replacement alone is not a filesystem sandbox.
- **Reject S262**, https://man7.org/linux/man-pages/man2/symlink.2.html, NOTES: “No checking of target is done.” Candidate inference that link creation proves target preservation is rejected: this explicitly supplies no target check, let alone a receipt. Flip: independent operator-approved preservation receipt, not merely link existence.
- No existing status/recheck/used-by cell changed. New rows: S260/S261 mined; S262 rejected. The registered scope is documentary grounding for C2/C3, not new core ground.
- Outside admit/reject spot-check: not supplied by lane seats; reserved for non-author closure. No self-attested agreement.
- Assimilation: none. No staged payload is adopted. The inherited claim predicates remain unchanged. No `considerthese/` input was found in the lane root inventory.

## Mistakes

| class | evidence pointer | captured-by | fix and failability |
|---|---|---|---|
| landing | Attempt 1 committed instruments `41e69c38cf9420e0304530f32a02c72ad72b7fe5` and `f8c805dbfa7f45814cf9a7270fa8bbffb41a8373` without a formal preregistration; attempt 2 handed off w1 before adding it | Q99 | Registration added without changing counter/population/target bytes. Timing defect is irreversible this round and is disclosed, not claimed repaired. |
| number-drift | `census/round-43/records/census-before.txt` ends `W04=0` while containing W04 warnings | CORPUS count carries command | Preserve the inherited receipt; recount actual W04 rows with a tab-delimited field reader. The old footer is not the warning count. |
| vacuous | C1 no-work state at `13de0e84b45efd1113f077d58fc1e89bc586a013`, `controls/c1-resume-before.txt`: registered=0 missing=3, EXIT=1 | Q95, Q100 | Three explicit correction lines replace no correction; frozen counter must read missing=0 and rederived=3. Before is demonstrably red for missing corrections. |

## Routed-item disposition

The r42 outside review was opened before dispatch (`corpus/lessons/round-42-verifier-spotcheck.md`, §6). Items 3/4 are the inherited C1/C2 targets; item 2 is tested by C3's explicit timeout accounting but load-stability beyond observed runs is not asserted. Item 1's unsatisfiable frozen r42 R1 remains historical and retired as an admission instrument: the already-landed pointer repair stays unchanged; it must not be read as a passing r42 R1. Item 5 (S259/PYTHONPATH scope) remains open: S259 documents sitecustomize import, not PYTHONPATH discovery. Item 6 requires no reconstruction of absent historical results. No historical evidence is rewritten. Certification OFF, K5 HELD, NAMESPACE hold unchanged.

## Defensive implementation and frozen-instrument limits

- **M43-1 (vacuous/oracle disagreement)** — `census/round-43/c2-hidden-audit.py:115-116` expects one literal `C2:FIELD-MISSING*4` class, but `classes()` returns four actual `C2:FIELD-MISSING` entries. Its h6 builder commits duplicate keys after the initial preregistration commit while omitting the required C0 FROZEN-EDITED from its expectation. Evidence: `census/round-43/records/c2-hidden-full.txt` shows 8/10, with only h4/h6 red for those exact discrepancies. Captured-by: Q80/Q102 did not expose the oracle conflict before the inherited freeze. Fix: Q106 prevents future freezes with unexpanded class notation and post-freeze builders that omit their own edit finding. This is shown able to fail by the two committed red scenarios; the frozen audit is not edited and C2's target remains missed.
- **C2 reached work:** the L1 completed a straightforward defensive checker repair after provider-failed candidates: first-wins duplicate evaluation (one finding per further occurrence), explicit unattached-key events, strict positive ASCII Round values, Control symlink refusal and Control/preregistration blob comparisons. Existing 31 self-test cases plus ten new cases pass (`census/round-43/records/c2-selftest.txt`, SELFTEST cases=41 pass=41 fail=0, EXIT=0). The candidate counter reads newtable=9/9, r42table=ok, real=ok, selftest=ok, tmpdir=ok; hidden=RED remains an honest target miss. No hardcoded hidden case or fake finding class is added.
- **M43-2 (scope/contract conflict)** — C3 requires both leaf-symlink refusal and nine prior fixtures green. `tests/fixtures/r38-drift-write-envelope.py` asserts that the same leaf symlink is resolved and its target written. R43executor05's candidate implements the requested refusal while retaining all 22 mutant/equivalent anchors; the L1's independent run reads cases=12 pass=11 fail=1, solely case-json-symlink-resolved (rc=2, resolved_written=False), in `census/round-43/records/c3-contract-conflict.txt`. Captured-by: Q73/Q78; these forbid landing a favorable new behavior while silently discarding an old green consumer. Fix this round is refusal to cut over the tool under the inconsistent frozen target; this is not claimed as a passing C3 repair. Candidate bytes remain evidence, not an installed tool. A later explicitly re-frozen contract must decide which symlink behavior is intended and update its consumer together.
- No third-party target, credential surface, history rewrite or live artifact deletion was exercised. Provider-denied work is unverified; a terminal seat status is not independent review clearance.

## Gate addendum — routed S259 scope corrected

SoujiR43a2 opened https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH on 2026-10-30,
served Python 3.15.2. **Admit S263**: PYTHONPATH entry, “Augment the default search path for module
files.” The -E entry says “Ignore all `PYTHON*` environment variables”. These ground the discovery
channel separately from the sitecustomize-import attempt documented by S259. This supersedes
the open-item status for r42 review §6 item 5 in the earlier paragraph, not S259's correct import
fact. No runtime injection or security-control bypass was attempted. No old registry cell changed.
Search addendum: 1 additional primary page identified/screened/included, 0 excluded; stop at the
discovery-versus-import distinction. Final row count is 187, superseding the intermediate 186.

## Wave documentary findings integrated (not outside admission)

`census/round-43/waves/w1/R43reviewer01.md` reviews exact instrument blobs, with bounded probes
and explicit static/injected-evidence limits. `R43critic03.md` independently identifies the
captured-but-uncompared C1 derived token, C2 memorizer's missing `os` import, C3 n10-before label
without a candidate-specific before run, dropped old/equivalent timeout accounting, and the
nine-versus-eight old-fixture scope discrepancy. These frozen instrument defects are retained;
no counter is repaired after scoring. They bar treating a SUMMARY as substantive clearance.

C1's actual three landed correction values are independently checked in
`R43rederiveR43D1.md` (174 rows), `R43rederiveR43D2.md` (48 warning rows) and
`R43rederiveR43D3.md` (literal header revision and scope-limited diff). D3 explicitly observes
that the receipt itself never printed the claimed stale revision: its correction is only a
clarification of later-carrier versus measured revision, not repair of a false receipt header.
The C1 counter also does not enforce arbitrary natural-language retractions or whole-file
append-only preservation; those are not acquired capabilities.

Additional C3 blockers from the exact frozen-source review: WRAPPER contains uninterpolated
doubled percent operators and fails compilation; the sniff control watches MUTANTS anchors
that all six EQUIV substitutions preserve, so its own required positive kill control is zero.
These findings reinforce the missed target independently of the legacy symlink contradiction.
C2's negative memorizer control crashes on its missing import; REJECTED is not proof that a
functioning memorizer was discriminated. Counter infrastructure failures/cleanup and absent
self-invocation modes remain conformance debts, not new passing gates.

The full 30-survivor r42 part-A inventory, general load stability, and the race-only S42 class
are not claimed closed. Existing reports explicitly marked incomplete remain incomplete.

## Settled wave and provenance

WAVE-DONE from the orchestrator confirmed all 68 w1 seats settled before this final integration.
One v2 wave; no residual call or replacement. Roles: executor 11, critic 8, mutation-tester 20,
scout 12, reviewer 6, sentinel 2, revenger 2, connector 3, simplifier 2, scribe 2. The L1 held the
planner seat. Attack share reviewer+critic+mutation-tester = 34/68. Validated spec, dispatch,
ready marker, 68-row results and reports are captured under `census/round-43/waves/`;
capture verified records=228, renames=0, excluded=0, symlinks=0.

The dispatcher result omits status/id fields, so terminal events were read from each owned
seat's session and saved as `census/round-43/records/seat-terminal-evidence.json`.
35 seats ended with provider errors (21 MiniMax quota, 11 Cursor pricing, 2 hardware-key
authentication/cyber-policy denials, 1 Devin account permission); 33 returned nonempty outputs,
some explicitly incomplete. Per-seat exact final error and answering model are preserved.
No denial was routed around and none supplies independent review clearance.

The C1 discrimination-fixture mutation seat reports 19 variants: 10 killed, 9 survived, none
inconclusive (`waves/w1/R43mutationtester01.md`); therefore 20/20 case-table PASS is not exhaustive
correction-language coverage. `R43reviewer05.md` further notes its r42 CRLF case never actually
writes CRLF, so that historical-signature attribution is not proved by the green column.
`R43executor11.md` falsifies the proposed S35 FIFO witness: pristine and mutant both time out
at the earlier list operation, so the proposed witness does not reach the mutated gitdir probe.
These findings remain limits, not completed fixes.

Required misroot sweep: `git -C /home/vgpnk/Projects/shokunin status --porcelain` showed only
the operator's `.scratch/goal-20261029-hyaku-run12.md` and two untracked `count-c1.cover` /
`count-c2.cover` files. `strings` attributes both binaries to mori round 61; they and the operator
file were left untouched. No souji-owned misroot found in this sweep. Receipt:
`census/round-43/records/wave-summary.json`.

Cross-domain scan (`waves/w1/R43connector01.md`, `R43connectorA.md`, `R43connectorB.md`) finds
adjacent freeze-check, correction-reader and symlink mechanisms, not a proven ownership
collision. Chousa's research/evidence checker, kaidoku's replacement policy and kumitate's
input-link policies are not unified with souji's output-leaf hygiene contract.

### M43-3 — capture on disk is not committed capture

Class landing; captured-by the evidence-capture committed-revision verifier. The directory commit
at `db1f1e89738cabd30276dd46acf4ac3860a44718` skipped two new files over 1 MiB, so its manifest
verified on disk but `--verify --rev` read records=228 failed=2, exit 4
(`census/round-43/records/capture-committed-red.txt`). Fix: explicitly name the two existing
connector evidence files in the helper commit, without altering either file or manifest.
The red committed-tree reading is the failability proof, not a disk-only assertion.
