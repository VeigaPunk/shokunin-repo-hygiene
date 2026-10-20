STATUS: DONE — gate at landing verified against landed bytes: the authorized run exits 2 with ZERO findings because no wave-17 report is committed at d7e648d (the carry axis never executes; the missing lesson is NOT the blocker); parse/pin/measured classes are genuinely exercised at 21/13/3 checks and all clean, so they must hold 0 at landing; latent defects found are outside every exercised path.

Seat: SoujiR17-3.RevGateAtLanding-2 (reviewer, FALSIFY wave 2). Target: D6 as landed at
`ddb73474433977ff54b015ac3e77669ff2537353`, lane head `d7e648d5a1931e6dbacfd5be0587547afee15de3`.
Own writes: this report + `/var/tmp/souji-r17-RevGateAtLanding/` (deleted at the end). No commits,
no `jj`, no git writes, no tool installs.

## Axes

- **Calibration (judged)** — classify every finding the landing run emits, and say exactly which
  classes survive once the lesson lands.
- **Falsify the landed D6 claims** — record vs expected vs actual gate bytes.
- **Defects in the changed gate code** — every affected caller/path of the new branches.

## 1. The authorized run (exact command, exact output)

```
$ python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev d7e648d5a1931e6dbacfd5be0587547afee15de3 --round 17 \
    --json /var/tmp/souji-r17-RevGateAtLanding/g.json
```

stdout:
```
SUMMARY	findings=0	checked_reg=21	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
```
stderr:
```
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-17/ at d7e648d5a1931e6dbacfd5be0587547afee15de3
```
process exit **2**. `g.json` written: `{"exit": 2, "findings": [], "error": "no .md reports under
.ufo/waves/round-17/ at d7e648d…", "summary": {checked_reg 21, checked_pins 13, checked_measured 3,
all other counters 0}, "resolved_rev": "d7e648d…"}`.

Byte provenance of the run: `sha256sum tools/souji-landing-gate.py` = `c7e8eea554b73f8183833af42e
6ab9d78e66681ad41eb15394e0befdf728917f` — equal to the gate sha recorded in
`census/round-17/gate-replays-ddb7347.json`, and `git diff --stat d7e648d -- tools/souji-landing-gate.py
census/round-17/gate-replays.py census/round-17/gate-replays-expected.json
census/round-17/gate-replays-ddb7347.json` is empty, so the worktree file I executed IS the landed
`ddb7347` gate. The run is a landing-rev run, not a worktree-drift run.

## 2. Findings by class (the deliverable)

| class | ids | findings now (d7e648d) | checks actually run | once lesson+reports land |
|---|---|---|---|---|
| parse | LG-PARSE-REG, LG-MISSING-REG | **0** | 21 (every SKILL.md-cited script parsed at the rev) | **0 expected to hold** — same cited set, all parse; only a newly cited broken script could break it |
| pin | LG-FROZEN-PIN | **0** | 13 (three committed frozen sets at d7e648d: `tests/fixtures/r13-cert-frozen`, `r14-cache-frozen`, `r15-preservation-frozen` — verified via `git ls-tree`; 12 file pins + record_sha256 comparisons) | **0 expected to hold** provided the frozen sets and their `expected.json` are not touched by landing commits |
| measured | LG-FROZEN-MEASURED | **0** | 3 (r15-preservation pins vs its `record.measured_commit`; the record regenerated at ddb7347 resolves and all three pins match — this run positively re-verifies the regenerated record at d7e648d) | **0 expected to hold** unless the record is repinned to a commit where pinned bytes differ |
| carry | LG-SEAT-UNCARRIED, LG-OPEN-ADMITTED | **UNEVALUATED — not 0** | 0 (axis aborted: exit 2 before any report read; `checked_markers=0`, `status_lines=0`, `checked_reports=0`, `carry_heading=0`) | the ONLY class that can be nonzero; fires once per uncarried failure marker until `corpus/lessons/round-17.md` carries it |

`findings=0` in the run is therefore **not** a green light: three classes passed with real checks,
one class never ran. That is exactly the docstring's zero rule (`tools/souji-landing-gate.py:36-46`),
and the observed exit-2 is pinned behavior, not a crash: selftest case `no-wave-dir-exit2`
(`tools/souji-landing-gate.py:1142-1144`) asserts exit 2 with `expect_err="no .md reports under"`;
the raise is `tools/souji-landing-gate.py:372-373`.

**Ticket-premise correction (calibration-critical).** The assignment said "the round-17 lesson does
not exist yet, so carry findings are expected". The run proves the converse ordering: the missing
lesson would NOT have blocked anything — `check_carry` treats an absent lesson as zero carry lines
and would have emitted one LG-SEAT-UNCARRIED per marker (`tools/souji-landing-gate.py:375-380`).
What actually blocks is that **no wave-17 report is committed**: `git ls-tree -r --name-only
d7e648d -- .ufo/waves/round-17/ corpus/lessons/` lists 21 lesson files and **zero** round-17 wave
paths. The carry axis for round 17 is unreachable via the authorized command until the wave
reports are committed — which is itself part of landing. L1 should plan the landing-day sequence:
commit wave-17 reports → run gate (expect LG-SEAT-UNCARRIED rows, r16's pre-carry replay showed
29) → write `corpus/lessons/round-17.md` carrying every marker → re-run → exit 0.

**Carry-format traps for the scribe (each one produces false LG-SEAT-UNCARRIED rows at landing):**

1. Carry matching is line-wise: a carry bullet must contain, after the pinned normalization (NFC,
   drop `*` and backticks, collapse whitespace — `norm_line`, `tools/souji-landing-gate.py:301-307`),
   the **complete** marker text as a substring of ONE line, plus `\bopen\b` or
   `resolved@[0-9a-f]{7,}` on that same line (`:402-404`). A wrapped or truncated bullet does not
   carry. Heading-styled markers keep their leading `## ` in the needle (e.g.
   `## STATUS: INCOMPLETE — …`); round-16's lesson quoted them verbatim, one bullet per line.
2. `admitted: true` is searched over the **whole lesson**, not just the failures section
   (`:389`); any carried-open marker while it is anywhere in `round-17.md` becomes
   LG-OPEN-ADMITTED (exit 1). Use `resolved@<rev>` tokens, or keep `admitted: true` out until no
   open carry remains.
3. STATUS lines inside fenced blocks are exempt from the failure channel but still counted by
   `status_lines`; reports (including w2 seats') should keep quoted gate output inside fences so
   they add zero markers.

## 3. Defects and observations, by severity

**F1 — MEDIUM (latent code defect, unexercised): changed-script path splitting is quoting-unsafe.**
`tools/souji-landing-gate.py:635-639`: `git diff --name-only --diff-filter=AM base resolved` output
is split with `changed_out.split()`. A path with a space (or a quoted non-ASCII name under
`core.quotePath`) splits into garbage paths and can both miss a real changed script and fabricate
nonexistent ones (which then report `parse` detail against a missing tree key →
`blob_by_oid` KeyError-style failure path is avoided only because `tree[path]` would KeyError —
an uncaught `KeyError`, i.e. a traceback, not exit 2). Also `--diff-filter=AM` misses a script
whose only change is a rename+edit (`R`). No pinned replay and not my run passes `--base`, and no
lane script path currently contains a space, so this fires only on a future `--base` use.
Smallest fix: `["diff", "--name-only", "-z", "--diff-filter=AM", base, resolved]` +
`changed_out.split("\0")` (binary=False keeps str; use `split("\x00")`), and consider adding `R`.

**F2 — LOW: exit-2 stdout still shows a plain `SUMMARY findings=0` row.** A consumer reading only
stdout could record "0 findings, clean" from this exact run; the truth (could-not-evaluate) is on
stderr and in the JSON `error`/`exit`. Docstring documents zeros≠pass, but the SUMMARY line itself
is not marked unknown on the error path (`emit`, `:675-695`). Smallest fix: when `result["error"]`,
append `\tstate=could-not-evaluate` to the SUMMARY line (or print it to stderr). JSON consumers are
unaffected.

**F3 — LOW (doc gap): exit code 2 is overloaded without documentation.** `emit` returns 2 for
could-not-evaluate AND for `--json` refuse-overwrite (`:697-699`) and `--json` write failure
(OSError branch); the module docstring's exit list (`:30-33`) names only the evaluation causes.
Smallest fix: one docstring line.

**F4 — LOW (dead code): `resolve_commit`'s `if not resolved: raise EvalError("unknown revision")`
(`:218-219`) is unreachable** — `rev-parse --verify --quiet` on an unresolvable rev exits nonzero,
so `_git` raises the wrapped `cannot resolve revision` first (the selftest's
`expect_err="cannot resolve revision"` at `:1160-1161` confirms the live path). Harmless; drop the
branch or leave it as belt-and-braces.

**F5 — OBSERVATION (D6 replay record verified; one inert field).**
`census/round-17/gate-replays-ddb7347.json` confirms, under the **landed** gate bytes
(`c7e8eea5…`): r15-landing `b410186` exit 1 with exactly 5 findings (LG-FROZEN-MEASURED ×2 +
LG-FROZEN-PIN + LG-PARSE-REG + LG-SEAT-UNCARRIED — same (id, path) multiset as
`gate-replays-expected.json`), r13 `a31642d` 0, r14 `cc21683` 0, r16 `6ff91f5` 0,
r16-precarry `79bbe7a` 29 × LG-SEAT-UNCARRIED; every entry `match: true`, top-level `match: true`.
Since expected was derived under the **5fa6017** gate (`e7d2439d…`), this record doubles as an
old-gate→new-gate regression proof. Two properties to keep in mind:
- `expected.gate.sha256` (e7d2439d) will never match again, so `gate_sha256_match=false`
  (`gate-replays.py:296`) is now permanently false and carries no signal — it is the honest,
  disclosed cost of deriving expected at the r16 base. Do **not** "fix" it by re-deriving expected
  under the new gate: that would freeze the new verdicts and silently discard the cross-generation
  property that `gate-replays-ddb7347.json` just exercised.
- `compare()` pins only process/payload exit + the (id, path) multiset (`:170-190`); SUMMARY
  counters are recorded but never compared. That was necessary — the r17 change itself altered
  counter semantics (`checked_pins` 16→13, new `checked_measured=3`) — but it means a future gate
  that silently stops executing a branch (counters drop to 0) still `match: true` as long as
  finding sets hold. The counters are visible in the record for a human; if L1 wants them frozen,
  add an optional per-replay `summary_expect` to expected rather than changing compare's default.

**F6 — OBSERVATION (positive verifications this run contributes).** (a) The 21 cited registry
scripts at d7e648d all parse (no LG-PARSE-REG/MISSING-REG). (b) All 13 pin comparisons across the
three frozen sets pass at d7e648d. (c) The regenerated r15-preservation record is internally
consistent at d7e648d: `measured_commit` resolves and all 3 pins match it (checked_measured=3, no
LG-FROZEN-MEASURED) — independent confirmation of the ddb7347 regeneration claim. (d) Static case
count of the selftest is **28**: 23 single-line `check("` sites + 1 multi-line
(`changed-nonparsing-with-base`, `:920-933`) + 3 loop cases (`files-null/empty/nonobject-exit2`,
one call site) + 1 manual (`ambient-git-dir`) — consistent with the claimed 28/28, whose execution
remains w1 GateExactIds' measurement (I was not authorized to run `--selftest`).

## 4. Commands run (all read-only or the one authorized exec)

```
python3 …/tools/souji-landing-gate.py --root …/souji-shokunin --rev d7e648d… --round 17 --json /var/tmp/souji-r17-RevGateAtLanding/g.json   # exit 2, output in §1
git -C …/souji-shokunin ls-tree -r --name-only d7e648d… -- .ufo/waves/round-17/ corpus/lessons/                                            # 21 lessons, 0 wave-17 paths
git -C …/souji-shokunin ls-tree --name-only d7e648d… -- tests/fixtures/  (+ -r … r15-preservation-frozen/)                                  # 3 -frozen sets present
git diff --stat d7e648d… -- tools/souji-landing-gate.py census/round-17/gate-replays.py census/round-17/gate-replays-expected.json census/round-17/gate-replays-ddb7347.json   # empty
sha256sum tools/souji-landing-gate.py                                                                                                      # c7e8eea5… (== record's gate sha)
```
plus `read` of `tools/souji-landing-gate.py` (full), `census/round-17/gate-replays.py` (full),
`gate-replays-ddb7347.json`, `gate-replays-expected.json`, `g.json`, w1 reports
`GateExactIds.md`, `GateReplayFrozen.md`, `ScribeD6Narrative.md`, `ScoutGateUncarriedCount.md`,
and two targeted `grep` line-number passes over the two tools.

## 5. Verdicts

- Claim "landing gate at d7e648d/round 17 shows carry findings": **fails as stated** — the command
  exits 2 before carry evaluation (no committed wave-17 reports); carry findings become observable
  only after reports are committed. Smallest fix: sequence reports before the landing run (§2).
- Claim "parse, pin, measured classes must be 0 once the lesson lands": **holds and is already
  measured 0 at the landing rev** with 21/13/3 real checks; projected to hold through landing
  unless SKILL.md cites new scripts, a frozen set is edited, or the r15 record is repinned.
- Claim "selftest 28/28, per-branch SUMMARY counts, exit-2 totality": **holds statically** (28
  cases counted; SUMMARY carries all seven counters; every error path observed or read exits 2,
  including this run's live exit-2) — execution numbers rest on w1's authorized runs.
- Claim "five replays match expected (gate-replays-ddb7347.json)": **holds** per the committed
  record, read entry by entry (§3 F5).
- Gate code: **holds** for every exercised path; one medium latent defect (F1) outside all
  exercised paths.

## 6. Residual risk and verification gaps

- I did not rerun `gate-replays.py` or the selftest (not in my ALLOWED-EXEC; rerun lanes exist as
  peers). The replay verdicts rest on the committed record, which I verified internally
  (expected vs record, pair by pair) but did not re-execute.
- The round-17 marker census (how many LG-SEAT-UNCARRIED to expect at landing) is derivable only
  after the wave reports are committed; my probe rules forbid a tree-wide scan of the worktree
  reports, and nothing is committed yet.
- Inherited, previously disclosed, unchanged: hostile-blob resource bounds (unbounded
  `blob_by_oid` reads / snapshot writes), and the emit-partial-findings-on-exit-2 behavior
  (findings collected before an EvalError are still printed next to the error — fail-closed, but
  consumers must gate on `exit`).
- F1's traceback path (`tree[path]` on a split-fabricated name) is code-read, not executed.

Scratch `/var/tmp/souji-r17-RevGateAtLanding/` deleted after evidence capture. No tool installs.
