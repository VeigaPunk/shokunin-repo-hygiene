# S67ReviewerDesign — design-attack report, souji round 67 C1

Seat: reviewer (design), wave w1, post-freeze v1. Read-only on the lane; scratch
`/fast/scratch/hyaku/souji-r67/S67ReviewerDesign/` (removed before this report was written;
the candidate-selftest run log was copied to `receipts/candidate-selftest-37.log` first).
Targets: frozen C1 design (preregistration-attempt4, c1-counter.py, c1-matrix.tsv) and the landed
candidate bytes. Base `3639087917eaeb28719d7603110a6ec22782100e`; instruments
`05eb2cee2794e42559c5ba15c3ebfdf7caecfee5`; freeze `4c61efcbe8c4e7586590c76965e5b1b29a1fa9a7`.
Host git 2.56.0. Seat scratch removed before yield per the wave contract; no fixture byte survived.

## Verified inputs (all bytes recomputed this session)

- `census/round-67/c1-counter.py` sha256 `69f11706…136b2` = blob at instruments commit (= prereg digest).
- `census/round-67/c1-matrix.tsv` sha256 `5d26b341…76a692` = blob at instruments commit (= prereg digest).
- Base writer blob at base = `a8c47d36…1097fc` = work-tree `tools/souji-receipt-write.py` = r66 landed bytes.
- Frozen counter selftest on this host: **8/8 pass, EXIT=0** (spec/matrix agreement incl. missing/extra row
  refusal at CLI level, and all three judge-gating stub writers rejected; accept-stub shape `new_forgeries=25
  class_mismatches=25` over refuse rows `n_refuse=25`).
- Do-nothing control `census/round-67/controls/c1-do-nothing.txt` re-read line by line: `W1 base=accept
  base_findings=-`, `W2 base=accept`, `W3 accept on both slots`, base honest rows exactly A, B, T4, V2, SY1, W3
  (6), base forgeries exactly W1, W2 (2), every other refuse row carries exactly its expected_class, `EXIT=1`.

## Findings

### MEDIUM-1 — the "scrubs on every git call" claim clause has no kill power in the frozen matrix

`c1-counter.py`'s C1 predicate phrase ("every git call scrubs the variable") is behaviorally unbound:

- On a MISMATCH the writer refuses before any git call (W1/W2), so the scrub is unreachable a fortiori.
- On an EQUAL value (W3), scrubbing versus not scrubbing is observationally identical — git honors the same
  common dir either way, and the writer's own plumbing reads identical bytes and emits identical receipts.

The only arm that could in principle distinguish a scrub-less candidate (caller value left in env during the
wrapped run, e.g. watching a `GIT_TRACE`-free plumbing child) has no row; W1–W3 are the only arms carrying
`GIT_COMMON_DIR` and none reaches the writer's git calls. This is the same shape as the r66 K3/K4 redundant-pin
survivors: defense-in-depth with zero recorded kill power, already routed to S67MutKill (its K3/K4/K6/K7 decision
should absorb it). No falsification possible inside the frozen predicate; noted so the L1 does not count this
clause as tested.

### MEDIUM-2 — the counter's `clean_env` does not scrub a caller-set `GIT_COMMON_DIR`, so operator shell env leaks into the instrument

`c1-counter.py` `clean_env()` drops `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, the config routes and the object
routes — but not `GIT_COMMON_DIR`, the very variable this round's C1 is about. Demonstrated by importing the
counter module and calling `clean_env()` with `GIT_COMMON_DIR=/somewhere/forged` in the caller env: the value
survives into every git call, including the `subprocess.run(env=clean_env(env_extra))` used to launch BOTH slots
on BOTH arms of EVERY row. A stale operator export would:

- repoint witness `git status` reads and witness plumbing in fixture setup; and/or
- leak into the base arm, which honors `GIT_COMMON_DIR` unconditionally (probe P1), making base verdicts a
  function of the operator's shell instead of the instrument.

This cannot produce a false PASS of the frozen target (a forged redirect would most plausibly tip the base rows
into `error`s or an exotic config-redirect state; every such path moves counts away from `regress=PASS` or
`new_forgeries=0`), but it can produce confusing spuriously-`error` verdicts in the frozen instrument bytes and
spurious red runs the round would have to investigate. Design intent per L1: the already-run do-nothing
control's receipt proves the L1 env was clean; this carries only as a named limit or residual-risk note,
not a counter change (frozen bytes; M-class precedent r66 M4/M6: disclosed, not amended).

### LOW-3 — wording: SY3 is listed as r60–r65 machinery in the docstring while CASE_SPECS groups it with the r66 rows

Labeling inconsistency only; every verdict is produced by CASE_SPECS and matches the control. No action needed.

## Candidate review (attack line 6; candidate bytes recomputed at review time)

The executor's candidate landed during this seat's session:
`.ufo/waves/round-67/w1/S67ExecWriter/candidate/souji-receipt-write.py`, sha256
`b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725` (earlier in the session the same path held
base-identical bytes `a8c47d36…`; the real candidate replaced them mid-flight — resolved, no finding; the do-nothing
equal-bytes reading I recorded first was of that placeholder, not of the final candidate).

**Byte review against the spec deltas (spec deltas only, verified):**
1. Module docstring: a new r67 paragraph describing value-check, scrub-on-every-call, realpath canonicalization,
   empty included, name-only echo. Words only; no behavior.
2. `git()` scrub list: `("GIT_DIR", "GIT_WORK_TREE")` → `("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")`.
   Direction supported by the probe results: `git -C D rev-parse` prints `.git` RELATIVE — so every git call the
   writer makes stays `-C`-authoritative under an equal-value caller env, matching the prereg's third clause.
3. `_check_env_commondir(root)` added; refuses RECEIPT-ENV-COMMONDIR-MISMATCH on (empty | resolution failure |
   realpath mismatch), canonicalizing BOTH sides (`os.path.realpath(value)` vs
   `os.path.realpath(os.path.join(root, revparse_output))`), refusing BEFORE any git call reads the caller value
   (the resolution call itself runs through the scrubbed `git()` helper, so no writer git call ever sees the
   forged value), and echoing only the VARIABLE NAME ("value not shown"), matching the r65 F4 redaction posture.
   Placement is before any other git-touching step in the writer's main flow, per the prereg ordering clause.
4. Writer selftest seeds four new cases (c34–c37: mismatch refused with value-not-echoed guard; match accepted
   for absolute AND relative `.git` forms — the exact relative-form case my analysis flagged as the likeliest
   candidate bug (attack line 2) is explicitly covered; empty refused; unresolvable refused under
   `GIT_CEILING_DIRECTORIES=work`). Registered in SELFTEST CASES. No other hunk.
   Counterdiff vs attack line 6 checklist: no r66 behavior moves — the diff's only modifications to existing
   lines are the docstring paragraph and the scrub-list line; E1–E6, MOD2/MOD3, SY3, T-rows code paths are
   untouched (byte-level presence preserved; the four new selftest cases re-run the W shape, not the old ones).

**Selftest run by this seat in seat scratch:** `SELFTEST cases=37 pass=37 fail=0`, true process exit code 0
(re-verified twice; the first backgrounded run's `exit code 1` came from my shell wrapper, not the writer —
the log itself ends `SELFTEST cases=37 pass=37 fail=0`; receipt copied to
`.ufo/waves/round-67/w1/S67ReviewerDesign/receipts/candidate-selftest-37.log`, sha256
`a9de94337e3fcd0a228586ab2b5ecefba3fb33c88b6207a764063151f7422180`, before scratch removal).

## Not found (sweeps that returned zero)

- No `444`/`888` byte-pattern artifacts, no odd-byte/codec terminal writes, no future timestamps, no cover-tracks
  phrases, no VaultDumper-pattern or sed/echo shell-injection strings in the delivered artifacts.
- No additional hidden TOCTOU in the candidate beyond the prereg's declared L2 start-of-run scope: the env read
  is a single `os.environ` access at gate time; subcommand processes cannot mutate the parent's environ; the
  gate precedes every git call; no retry/second-read path exists in `_check_env_commondir`.

## Residual risk and verification gaps

- MEDIUM-1 and MEDIUM-2 above (frozen-design limits, not candidate defects) should be reflected in the round
  report / lesson named limits — the M2 precedent (r66 M-class) is disclose-not-amend.
- The r67 after-receipt chronology arm has NOT been exercised end-to-end on real lane bytes (no candidate commit
  exists yet — seats never commit); the synthetic dry-run above is the grammar evidence. Real binding happens at
  the L1's landing commit via `census/round-67/records/c1-after.txt` carrying `rev=<candidate-rev>`.
- Symlinked-or-traversal forms of GIT_COMMON_DIR (e.g. a symlink pointing at the repo's own `.git`, or
  `<repo>/.git/./`) were checked by-reading (`os.path.realpath` on both sides resolves symlinks and `./`)
  but not exercised as a live run; no behavioral doubt remains (realpath equivalence is the comparison),
  and case_35's relative `.git` form exercises the same code path.
- This seat never executed the full 31-row counter run (the do-nothing control's committed receipt stands as
  that evidence; rerunning the whole matrix in a review seat would duplicate the L1's after-run).

Report trailer: .ufo/waves/round-67/w1/S67ReviewerDesign/report.md
