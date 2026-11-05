# S60ReviewerFreeze — C1 falsification (substance arm of tools/souji-freeze-check.py)

Seat: S60ReviewerFreeze (reviewer, leaf, no subagent dispatch). Lane untouched: no edits, no git mutation, no commits.
Target: falsify C1 — `--substance` refuses the forgery classes and accepts honest records, measured against base 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4.

Inputs read: base tool (`git cat-file blob 1e8bfd87…:tools/souji-freeze-check.py`, sha256 d1ca06fd…), candidate `.ufo/waves/round-60/w1/S60ExecFreezeArm/souji-freeze-check.py` (sha256 928745cd7f294320e6a37551334f32f43eb409728169bb5d8606c8b7054cb24e, final per the executor's IRC notice), `census/round-57/record-receipt.sh`, `census/round-57/preregistration.txt`, `.ufo/waves/round-60/w1-spec.json`.

Delivered (copies, `.ufo/waves/round-60/w1/S60ReviewerFreeze/`): `build-probes.py` (11 attack classes + honest control, fixture repo built per run), `build-k2.py` (rev-vs-freeze drift), `base-tool.py`, `candidate-freeze-check.py`, `run-base.txt`, `run-k2-base.txt`, `run-cand-default.txt`, `run-cand-substance.txt`, `run-k2-cand-substance.txt`. The probe bytes are fully determined by the builders; every receipt, prereg and fixture file is generated from them.

## Verdict summary

Default arm (no `--substance`): every forgery is accepted (rc 0). By design (byte-identity), but see Finding 5.
`--substance` arm: refuses kind-only, cross-claim digest copy, rename, the honest-looking orphan/short rev, rev-missing and command-missing forgeries. It accepts a fenced decoy bound as the Counter, a conflicting duplicate `rev=`/`instrument=`/`instrument_sha256=`, a drifted rev-vs-freeze digest, and a substring command. C1's claim "the Control receipt is bound to the declared Counter bytes and to a pre-freeze revision" is falsified for three of those.

## Findings (numbered, severity)

1. **HIGH — fenced decoy key binds as the real Counter (attack e3).** `parse_claims`/KEYLINE is fence-unaware: a column-0 `Counter: decoy.py sha256=…` inside a ``` block is taken as the claim's Counter when the real Counter key is absent. A receipt whose `instrument=decoy.py` and `instrument_sha256=<decoy digest>` matches that decoy passes `--substance`: `CASE e3-fence-decoy-matched expect=refuse observed=accept rc=0` (`run-cand-substance.txt`). Base also accepts (e2 base: accept rc=0). The arm checks the receipt against whatever Counter the parser picked, so binding is only as strong as the prereg grammar. Verdict: **not repaired**. Repair: the substance arm (or parse_claims) must ignore fenced lines, or the claim must refuse when a key appears inside a fence.

2. **HIGH — digest bound to FREEZE blob, not to the blob at `rev=` (attack k2).** Spec and candidate check `instrument_sha256` against the Counter blob at FREEZE; `rev=` is only checked for ancestry. A receipt that says "measured at R, digest = freeze blob" is accepted even when the Counter at R had other bytes: `run-k2-cand-substance.txt`: `CASE k2-rev-vs-freeze-drift expect=refuse rc=0`, `SUMMARY claims=1 findings=0`, with shaOLD≠shaNEW (`shaOLD=ac236224…`, `shaNEW=3c9b9c70…`). The recorder itself digests `git show REV:INSTR`, so a truthful receipt for R would carry the R digest. Verdict: **not repaired**. This falsifies the "bound to ... a pre-freeze revision" half of C1 because `rev=` is decorative with respect to instrument bytes.

3. **MEDIUM-HIGH — conflicting duplicate receipt lines are silently first-wins (attacks g2, g3, g4).** `first()` returns the first column-0 match. The prereg grammar refuses duplicate keys (KEY-DUPLICATE), but the receipt grammar does not. Probes (all accept rc=0 under `--substance`):
   - g2: `rev=<base>` then `rev=<orphan>` → accepted (the orphan second rev is hidden). `CASE g2-second-rev-conflict`.
   - g3: `instrument=c.py` then `instrument=decoy.py` → accepted. `CASE g3-second-instrument-conflict`.
   - g4: `instrument_sha256=<correct>` then `instrument_sha256=<decoy digest>` → accepted. `CASE g4-second-digest-conflict`.
   Verdict: **not repaired**. Repair: refuse any receipt with more than one `instrument=`, `instrument_sha256=`, `rev=` or `command=` line (a new class, e.g. CONTROL-DUPLICATE).

4. **MEDIUM — `command=` check is substring containment (attack f; bytes-vs-execution, attack c).**
   - f: `command=python3 -B xc.py --flag c.py-enabled` passes because `"c.py" in cmd`. `CASE f-command-substring … observed=accept rc=0`. The spec text literally says "whose text contains the declared Counter path", so the arm conforms to the spec while being bypassable. Verdict: **not repaired** (spec-level; repair: exact-token match on argv or a fixed command shape).
   - c: `command=echo 'pretend: python3 -B c.py'` with correct instrument, digest and rev is accepted. The contract binds bytes and ancestry, not execution; `census/round-57/record-receipt.sh` documents "binds BYTES, not execution" as a named limit. Verdict: **out of scope** for C1 as worded, but it must be listed as a named limit of the claim; the matrix cannot claim to refuse it.

5. **HIGH (process) — the arm is opt-in and the default output cannot say so (attack f-bypass).** Without `--substance` the default verdict on every forgery in this battery is rc 0 `SUMMARY … findings=0` (`run-cand-default.txt`): a-kindonly, b-crossclaim, c, d, e2, e3, f, g, g2–g4, h, i, k2. Byte-identity with the base output (required by the executor spec) forbids adding an `arm=` marker to the default SUMMARY, so a freeze record that calls its result "a freeze check" without the flag is not C1 evidence. Verdict: **not repaired** by the tool; route to L1: the freeze record must print the exact argv (with `--substance`) and the matrix runner must reject a run whose argv lacks it.

6. **MEDIUM — matrix case `forgery-rev-at-freeze` is unconstructible as specified.** The receipt is read as the blob at FREEZE, so it cannot contain FREEZE's own commit id (a commit id hashes its tree, which contains the receipt) [INFERENCE from git's content addressing; not probed beyond the j-probe]. The only buildable rev-misbinding is a non-ancestor (an orphan, or a descendant), which yields CONTROL-REV-NOT-BEFORE-FREEZE. My j-probe used the freeze1 ancestor and correctly accepted; it is a vacuous control, not a forgery. Verdict: **out of scope / matrix spec defect**: the matrix should use an orphan rev for that row and say so.

7. **LOW — fenced decoy AFTER the real Counter is refused for the wrong reason (attack e1).** `CASE e1-fence-decoy-after` refuses with KEY-DUPLICATE: an honest prereg that quotes an example key in a code fence is a false refuse. Verdict: **repaired** for forgery purposes; usability limit to record.

8. **LOW — indented decoy correctly ignored (attack e4).** `CASE e4-indent-decoy expect=accept observed=accept rc=0`. Verdict: **repaired** (no false match on column-1 text).

9. **LOW — class mapping ambiguity in the spec.** A wrong instrument path with a matching digest (b, d, e2) emits CONTROL-INSTRUMENT-MISMATCH plus a spurious CONTROL-COMMAND-MISMATCH; the spec does not say which class a path-only mismatch takes. Non-resolving rev → CONTROL-REV-INVALID and non-ancestor → CONTROL-REV-NOT-BEFORE-FREEZE is consistent with the spec text. Verdict: **not repaired** (spec wording; state the mapping in the claim).

## Per-attack verdicts (the six named attacks)

| Attack | Input | Expected | Base (rc) | Candidate `--substance` (rc) | Verdict |
|---|---|---|---|---|---|
| (a) kind-only, plausible labels | `ctl-a.txt` = `kind=counter-red / label-instrument=c.py / note=by-hand / EXIT=1` | refuse | accept 0 | refuse 1: INSTRUMENT-MISSING ×2, REV-MISSING, COMMAND-MISSING | **repaired** |
| (b) copies C2's digest line into C1 | C1 Control = `instrument=c2.py`, `instrument_sha256=<c2 digest>`; C1 Counter = c.py | refuse | accept 0 | refuse 1: INSTRUMENT-MISMATCH (path and digest) | **repaired** (not run: same-Counter copy variant, see Not run) |
| (c) rev strict ancestor, command never ran instrument | command `echo 'pretend: python3 -B c.py'` | (contract: bytes only) | accept 0 | accept 0 | **out of scope** (named limit) |
| (d) rename: byte-identical copy | `instrument=copy_of_c.py`, digest = c.py digest, command `python3 -B copy_of_c.py` | refuse | accept 0 | refuse 1: INSTRUMENT-MISMATCH | **repaired** (path equality) |
| (e) fenced/indented decoy key | e1 after, e2/e3 before with Counter dropped, e4 indented | refuse / refuse / refuse / accept | refuse / accept / accept / accept | refuse / refuse / **accept** / accept | **not repaired** (e3; e2 only refuses by accident) |
| (f) arm bypass with flag off | any forgery, no `--substance` | (n/a) | accept 0 | accept 0 with flag off | **not repaired** (by design; Finding 5) |

## Commands run (exact argv, exit codes; builder exit is always 0 because verdicts are printed, not returned)

Scratch: `/fast/scratch/hyaku/souji-r60/S60ReviewerFreeze/` (fixtures created inside it; toplevel asserted equal to the fixture dir before the first commit; throwaway identity).

1. `python3 -B build-probes.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py --work <S>/fix-base > run-base.txt` → rc 0. Base: all forgeries accepted.
2. `python3 -B build-k2.py --tool <base tool> --work <S>/fix-k2 > run-k2-base.txt` → rc 0. Base: drift accepted.
3. `python3 -B build-probes.py --tool <candidate> --work <S>/cand-off > run-cand-default.txt` → rc 0 (default arm).
4. `python3 -B build-probes.py --tool <candidate> --substance --work <S>/cand-on > run-cand-substance.txt` → rc 0 (substance arm; verdicts in the file).
5. `python3 -B build-k2.py --tool <candidate> --substance --work <S>/k2-cand-on > run-k2-cand-substance.txt` → rc 0; `SUMMARY claims=1 findings=0`.
6. Byte identity, default path, real preregs (base `1e8bfd87…` vs candidate, stdout and stderr compared with `cmp`):
   - round-57: base rc=1, cand rc=1, IDENTICAL (stdout and stderr).
   - round-58: base rc=1, cand rc=1, IDENTICAL.
   - round-59: base rc=1, cand rc=1, IDENTICAL.
7. Selftests:
   - base: `python3 -B base-tool.py --selftest` → `SELFTEST cases=41 pass=41 fail=0`, rc 0.
   - candidate default: `python3 -B candidate.py --selftest` → `SELFTEST cases=41 pass=41 fail=0`, rc 0.
   - candidate substance: `python3 -B candidate.py --selftest --substance` → `SELFTEST cases=12 pass=12 fail=0`, rc 0.

Base `--substance` is not a flag of the base tool (argparse rc 2), which is why the base battery is run without it.

## Not run (named)

- Same-Counter copy variant of (b): two claims with the same Counter path, C1 receipt copied from C2. The digest is then legitimately the same blob, so the substance arm cannot distinguish it; I did not build it. [INFERENCE: accepted by design.]
- Matrix row `forgery-rev-at-freeze` as specified (rev = FREEZE): unconstructible (Finding 6); j-probe used a freeze1 ancestor (vacuous) and is not counted as a forgery test.
- Kill-chain of the whole frozen matrix (`S60ExecMatrix` runner, `c1-counter.py`): not present in the wave dir at my run; not run.
- Mutation-based check of the candidate's own selftest cases (`S60MutMutation`'s job): not run by me.
- Candidate NOTES.md: not read; the executor's final bytes were confirmed by sha256 only.
- Candidate landed mid-round per the executor's IRC message; I ran the final-bytes sha (928745cd…) once. No later change was observed.

## Tooling

No tools installed or upgraded. Python 3 stdlib and git only. No pacman, no uv, no npm.

## Limits of this review

- The candidate was tested in a synthetic fixture repo; it is not run on the lane's real preregistrations (beyond the default-path byte identity).
- I did not verify git's content-addressing claim in Finding 6 by constructing a commit; it is reasoning from hash fixed-point impossibility, marked [INFERENCE].
- Verdicts are about the candidate bytes at sha256 928745cd…; any later edit voids them.
