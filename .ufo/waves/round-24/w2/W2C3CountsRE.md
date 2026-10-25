# W2C3CountsRE — attack on the COUNTS_RE widening (souji round 24, wave 2)

Seat `L1Souji24.W2C3CountsRE`. Target: `tools/souji-receipt-run.py` at ca7fc1cb6dd1333096c6f3bdbad304686691d126
(byte-identical through lane `master` d3666c3ef291c0c6c7827ffcfb58471c4b8d54f7: `git diff --stat ca7fc1c master -- tools/` empty).
Read-only on the lane. Scratch `/var/tmp/souji-r24-W2C3CountsRE/` (removed). No tools installed.

## Status
STATUS: FAIL — falsified. At ca7fc1c, `verify` accepts receipts that hold no real final counts line: a counts line only in stderr, a decoy inside prose, `subcases=` prefix junk, and the real C2 fixture receipt with its final line deleted. `run`'s printed `counts=` is the FIRST match, so it can report a crashed or failing fixture as a clean `mismatches=0` run. No lane record was misled. C1/C2/C3 counter verdicts are unaffected, since every committed receipt carries a correct final line.

## Evidence
1. The widened alternation and the unchanged search scope (`git diff a65fac9 ca7fc1c -- tools/souji-receipt-run.py`). Four alternatives were added. `verify` still searches `_body`, which includes both the stdout and stderr fences:
   - ca7fc1c:tools/souji-receipt-run.py line 270, quoted: `header["_body"] = "\n".join(lines[idx:])`.
   - line 294, quoted: `if not COUNTS_RE.search(header["_body"]):`.
   - line 251 (run), quoted: `counts = COUNTS_RE.search(proc.stdout)`.
   - The search is unanchored (`re.search`, no `^`, no token boundary), and nothing checks `rc=`.
2. Forged receipts (header copied from census/round-24/records/c2-fixture-after.tsv, so rev, tool and digest are genuine and durable). Run with `python3 -B <tool> verify --root /home/vgpnk/Projects/shokunin/souji-shokunin <receipt>`. The tip is the ca7fc1c blob; base is the a65fac9 blob.
   - A1, stdout `cases=0 pass=0`: tip exit 0 `verify=ok`; base exit 2 `RECEIPT-COUNTS-ABSENT`.
   - A2, stdout empty, stderr `cases=9 pass=9`: tip 0; base 2.
   - A3, stdout `Traceback ... fixture aborted; would have printed cases=9 pass=9`: tip 0; base 2.
   - A3b, stdout `subcases=9 pass=9xyz`: tip 0; base 2.
   - A4, c2-fixture-after.tsv minus its final `cases=9 pass=9 control=FALSE-GREEN-REJECTED` line: tip 0; base 2. The per-case `got: grounded=2 mapped=2 dangling=0 mismatches=0` substrings satisfy the regex.
   - A5, only the nine `control case=... -> FAIL` lines (`grounded=0 mapped=0 dangling=0 mismatches=0`): tip 0; base 2.
   - A6, stdout `selftest=FAIL ids=0/5`: tip 0; base 2.
   - A7, the C1 tool's shape `garbage=0 size_garbage=0 unreachable=0 alternates=0` under tool=tests/fixtures/r24-coverage-agreement.py: tip 0; base 2.
   - A8, an r23 shape in stderr only, `assertions=0 resolved=0 skipped=0 mismatches=0`: tip 0; **base 0**. The stderr hole is pre-existing (r23); the widening adds many more shapes that can reach it.
   - A9, A1 with `rc=1`: tip 0; base 2.
3. The `run`/`verify` mismatch. A synthetic repo was committed at 1f3f042 in scratch, then `tip.py run ... -- python3 -B tools/<t>.py` and `tip.py verify`:
   - `err-only.py` prints `cases=9 pass=9` to stderr: run prints `rc=0 counts=none`, yet verify gives `verify=ok`.
   - `crash-after-case.py` prints one case line, then `SystemExit`: run prints `rc=1 counts=grounded=2 mapped=2 dangling=0 mismatches=0`; verify gives `verify=ok`.
   - `case-then-final.py` prints a case line, then `cases=9 pass=3 control=FALSE-GREEN-ACCEPTED`, exit 1: run prints `rc=1 counts=grounded=2 mapped=2 dangling=0 mismatches=0`; verify gives `verify=ok`.
4. The C3 fixture does not pin the widening. `git grep -n -i COUNTS master -- tests/fixtures/r24-receipt-verify.py` returns no RECEIPT-COUNTS-ABSENT case. The amendment files the widening outside the claim; preregistration-amendment-1.txt line 42, quoted: "Separate widening (not a C3 clause): verify's COUNTS_RE also accepts the round-24 counts lines".
5. The lane-record check (`rg` over the worktree including untracked files, operator-sweep excluded; `git log --format=%B a65fac9..master`):
   - `c2-fixture-after` is referenced by no file.
   - `grounded=2 mapped=2` occurs only inside that receipt.
   - No round-24 text quotes a `run` summary line (`counts=grounded`, `counts=case`: 0 hits).
   - The ca7fc1c message cites "C2 0 mismatches". That matches c2-after.tsv's `grounded=6 mapped=6 dangling=0 mismatches=0`, not the fixture's case-1 `grounded=2`.
6. Candidate fix, tested in scratch (`fix.py` = ca7fc1c plus the diff in Findings item 6):
   - All 14 genuine lane receipts give the same result under tip and fix: census/round-23/records/{agreement-after, declared-evidence-after, gate-check-at-first-landing, gate-check-at-lane-base, gate-check-c3} and census/round-24/records/{c1-after, c1-control-stub, c2-after, c2-control-base, c2-fixture-after, c3-after, c3-control-base-runner, gate-check-r24-entry, r13-recheck-receipt}, all exit 0.
   - The intentional .ufo/waves/round-23/records/stale-digest-demo.tsv stays at exit 2 `RECEIPT-TOOL-DIGEST-MISMATCH`.
   - Attacks A2, A3, A3b, A4, A5 and A8 become exit 2 `RECEIPT-COUNTS-ABSENT`. A1, A6, A7 and A9 stay exit 0 (by design, see Findings item 4).
   - `python3 -B <scratch copy of master:tests/fixtures/r24-receipt-verify.py> --tool fix.py --lane-root <lane>` gives `cases=8 pass=8 refusals=2/2 regress=5/5`, exit 0, the same as with tip.py.
   - `fix.py run` on the three synthetic tools prints `counts=none`, `counts=none` and `counts=cases=9 pass=3`, and verify refuses the first two.

## Findings
1. **High: the counts check accepts a stderr-only counts line.** Location: ca7fc1c:tools/souji-receipt-run.py lines 270 and 294 (`_body` spans both fences). Evidence: attacks A2 and A8, plus `err-only.py`, which `run` labels `counts=none` while `verify` says ok. This is pre-existing at base for r23 shapes. The widening extends it to `cases=`, `grounded=`, `garbage=` and `selftest=` lines. It is also a `run`/`verify` asymmetry, which is the property C3 is named for.
2. **High: no anchoring and no last-line rule.** Location: line 294 uses `search` over the whole body, and line 68 adds a bare `cases=\d+ pass=\d+` alternative with no left boundary. Evidence: A3, A3b, A4 and A5 verify ok.
   - Every frozen round-24 counter states its counts line is last. preregistration.txt line 35, quoted: "stdout LC_ALL=C key=value lines; last line is the counts line:". The C3 fixture docstring line 26, quoted: "then the last line".
   - The C2 fixture echoes `grounded= mapped= dangling= mismatches=` substrings on every case line. So its receipt would verify even if the fixture died before printing `cases=9 pass=9`.
3. **Medium: `run`'s printed `counts=` is the first match, not the final line.** Location: line 251. For c2-fixture-after.tsv, `run` would print `counts=grounded=2 mapped=2 dangling=0 mismatches=0`, which is fixture case 1's echo of the C2 tool, not `cases=9 pass=9`. In `case-then-final.py`, a failing fixture (`pass=3`, `FALSE-GREEN-ACCEPTED`, rc=1) is summarised as a clean zero-mismatch run.
   - **Is any lane record misled? No** (Evidence item 5). The summary line is never persisted, and every C2 claim in lane text traces to c2-after.tsv or the receipt body.
   - The risk is latent: any scorer reading the `run` summary for a fixture receipt sees a C2-tool-shaped `mismatches=0`.
4. **Not a defect: `cases=0 pass=0`, `selftest=FAIL`, `rc=1` and a wrong-for-the-tool shape all verify (A1, A6, A9, A7).** `verify` binds where a result came from, not whether it passed. c1-control-stub.tsv (`cases=8 pass=4`, rc=1) and c2-control-base.tsv (`mismatches=2`, rc=1) are honest controls that must keep verifying. Rejecting zero or failing counts would break them.
   - Consumers MUST read the final counts line and `rc=`; `verify=ok` is not a pass.
   - [INFERENCE] Binding a counts shape to a tool would need a per-tool registry. That is not narrow, and it is outside this item.
5. **Residual, not introduced by the widening.** The receipt body is not digest-bound, so a hand-written stdout with a correct final line still verifies. A tool whose stdout prints a literal `--- stderr ---` line makes the fence split ambiguous. Both are format-v1 limits.
6. **Recommended narrowest fix (not applied).** One helper, shared by `run` and `verify`: match only the last non-empty stdout line, anchored at its start with a token boundary. The stdout slice ends at the stderr fence. In the tested scratch diff, `lines[8]` is the redacted stdout element of `run`'s receipt list, so `run` scores exactly the bytes `verify` will read:
   ```
   -    r"|selftest=(?:PASS|FAIL) ids=\d+/\d+)"
   +    r"|selftest=(?:PASS|FAIL) ids=\d+/\d+)(?=\s|$)"
   +def counts_line(stdout: str) -> str | None:
   +    last = next((ln for ln in reversed(stdout.splitlines()) if ln.strip()), "")
   +    m = COUNTS_RE.match(last)
   +    return m.group(0) if m else None
   -    header["_body"] = "\n".join(lines[idx:])
   +    try:
   +        end = lines.index("--- stderr ---", idx + 1)
   +    except ValueError:
   +        return None
   +    header["_stdout"] = "\n".join(lines[idx + 1:end])
   -    if not COUNTS_RE.search(header["_body"]):
   +    if not counts_line(header["_stdout"]):
   -    counts = COUNTS_RE.search(proc.stdout)
   +    counts = counts_line(lines[8])
   ```
   - It changes no case, target or kill rule.
   - The pinned C3 line holds (`cases=8 pass=8 refusals=2/2 regress=5/5`), and regress stays 5/5.
   - It should land with a fixture case asserting `RECEIPT-COUNTS-ABSENT` for a stderr-only receipt and for one whose last stdout line is not a counts line. Without that case, this widening stays unpinned (Evidence item 4).
   - The docstring at lines 33–38 should also say "last non-empty stdout line".
   - Optional: print the whole last line instead of `group(0)`, so `run` shows `control=`/`lost_found=` too.

## Attack log
- A1–A9 forged receipts against the tip and base blobs: Evidence item 2. 9 of 9 pass at the tip; 1 of 9 (A8) passes at base.
- Three synthetic tools through `run` and `verify` at the tip: Evidence item 3. All three show `run`/`verify` disagreement or a misleading summary.
- Lane-record search for consumers of `run`'s summary: Evidence item 5. None found, so the attack on the records **survives**.
- Candidate fix: Evidence item 6. No regression across 14 genuine receipts or the C3 fixture.
- Observed during the run, not by this seat: the worktree `tools/souji-receipt-run.py` gained an uncommitted `OUT-OUTSIDE-VAR-TMP` guard (+4 lines), and `corpus/knowledge/count-objects-linked-worktree-garbage.md` changed (+8 −2). Neither touches the counts logic. All results above use the committed ca7fc1c blob.
