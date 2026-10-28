# R41w2scribe01 — wave 2 scribe report (round 41, falsify)

Role: scribe. Item: draft the final QUALITY rows Q98–Q101 for `corpus/QUALITY.md` and verify every cited path. Lane tip read: `1d41c13574db80fdd9a4bde490b712da7ce2a85f`. Read-only on the lane; no git mutation; no tool installed (no `sudo`, `uv`, `npm`, or `cargo` used). Scratch `/fast/scratch/hyaku/souji-r41/R41w2scribe01/` (c1/c2/c3 subdirs) deleted before yield; every receipt below is copied into `.ufo/waves/round-41/w2/R41w2scribe01/receipts/`.

Deliverable: `.ufo/waves/round-41/w2/R41w2scribe01/quality-rows.md` (draft rows, not written to `corpus/QUALITY.md`).

## Verdict

- **Q98 (draft R41scribe06): ACCEPT WITH EDITS.** The reject-by-count rule is correct and its evidence reproduces. Edited: lesson pointers given as `### Assimilation gate (merge/souji/)` line 49 (the draft's `## Assimilation gate` heading does not exist; the real heading is level 3, line 35), the three counts at `bffcc0f` added, and "which kind of count" made explicit.
- **Q99 (draft R41scribe07): ACCEPT WITH EDITS.** The draft named the protocol because the tool was absent at e2a7431. The tool is landed (`119c26f`, bytes unchanged at tip). The check now names the tool command, the observed outputs, and the tool's own rules. Corrected: "predates the freeze commit" becomes the tool's rule "added at or before the freeze commit" (tool line `c == freeze or repo.is_ancestor(c, freeze)`). Added limits the draft omitted (see Findings F1, F2).
- **Q100 (new): DRAFTED, evidence verified.** The rule rests on M41-3 and N1–N6. Substance evidence for the landed C3 fixture was measured in this seat (below).
- **Q101 (new): DRAFTED, evidence verified.** The rule rests on M41-4; the scope of `occurrences=0` was re-derived lane-wide in this seat (below).

All cited paths in `quality-rows.md` exist at tip `1d41c13` (`git cat-file -e` for repo paths, `test -e` for the rest). The two "missing" hits from the scan are template placeholders (`census/round-<N>/...`, `.ufo/waves/round-<N>/`), not paths.

## Commands run and outputs

Every line below was executed in this seat. Receipts are in `.ufo/waves/round-41/w2/R41w2scribe01/receipts/`.

1. Freeze check at tip (receipt `freeze-check-r41-tip.txt`):
   `python3 -B tools/souji-freeze-check.py --root <lane> --prereg census/round-41/preregistration.txt --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f` → `SUMMARY claims=3 findings=0`, EXIT=0.
2. Same tool over the round-40 preregistration at tip (`freeze-check-r40-tip.txt`) → `SUMMARY claims=3 findings=18`, EXIT=1. All 18 findings are `FIELD-MISSING` (each of C1–C3 lacks Base, Counter, Population, Control, Target, Kill), because the round-40 file has no key lines.
3. Same tool over the round-41 preregistration at its freeze commit `e2a74312…` (`freeze-check-r41-freeze.txt`) → `SUMMARY claims=3 findings=0`, EXIT=0.
4. `git diff --stat 119c26f 1d41c13 -- tools/souji-freeze-check.py` → empty (bytes unchanged since landing). `git show 119c26f:tools/souji-freeze-check.py | sha256sum` → `3c3e80baedd8…`, equal to `tool_sha=3c3e80baedd8` in `census/round-41/records/c2-after.txt`.
5. C2 counter at tip (`c2-tip.txt`): `SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8`, EXIT=0. Matches the frozen target.
6. C1 counter at tip (`c1-tip.txt`): `ITEM I3 … derived=before=6,after=3`, `ITEM I4 … derived=occurrences=0`, `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`, EXIT=0. Matches the frozen target.
7. C3 counter at landed `a1144120` (`c3-a1144120.txt`): `SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=f32022e28fe2`, EXIT=0. Matches the frozen target; `fixture_sha` equals the shim-audit row for R41executor04 (`sha256=f32022e28fe2`).
8. I1 counts at `bffcc0f` (`i1-counts.txt`): `grep -E '^\| S[0-9]+ ' | grep -c 'worktree\.c'` → 2; `… | grep -c 'v2\.56\.0/worktree\.c'` → 0; `… | grep -c 'worktree\.config'` → 0; raw-line `grep -c 'worktree\.c'` on the whole file → 3. Same registry count at tip → 3 (S009, S033, and S258, added this round). The 9 printed in round-40 line 49 matches none of these.
9. S258 substance (`s258-substance.txt`): `sha256sum -c SHA256SUMS` → `git-v2.56.0-builtin-worktree.c: OK` (and v2.55.0 OK); `grep -n -F 'prune missing working trees older than <time>'` → `255: N_("prune missing working trees older than <time>")),`. Matches the registry quote.
10. Dispatch and ready files (`dispatch-untracked.txt`): `.ufo/waves/round-41/{w1-dispatch.json, w1.ready, w2-dispatch.json, w2.ready}` exist on disk (mtimes 18:58 and 20:13, machine local time); `git check-ignore -v` → `.gitignore:1:.ufo/waves/`; `git ls-files .ufo/waves/round-41 | wc -l` → 0; freeze commit `e2a74312…` author time `2026-10-28 18:55:17 -0300`. The freeze tool therefore cannot see them (see F1).
11. Lane-wide `Codex error` / `flagged as potentially` search at `bffcc0f` (`git grep -c … -- .`): `flagged as potentially` → `LOG.md:1` only (waves: 0). Confirms round-41 I4 derivation scope (waves 0, lane 1).
12. QUALITY tail (`quality-grammar.txt`): round-40 table header `| id | criterion | applies to | check | motivating evidence |`; `grep -c '^| Q(9[89]|10[0-9]) '` on tip → 0.

## Findings

F1 — Q99 dispatch clause is blind to this round's own dispatch files (real limit, not fixed; the frozen tool is not edited).
`tools/souji-freeze-check.py` `dispatch_findings` reads `git log --name-only -- .ufo/waves/round-<N>/`. `.ufo/waves/` is gitignored at `.gitignore:1`, so `w1-dispatch.json`, `w1.ready`, `w2-dispatch.json` and `w2.ready` never enter history. The tool's `findings=0` for DISPATCH is therefore vacuous for this lane; the C2 case `dispatch-before-freeze` passes only because its fixture commits the file. Ordering by mtime (18:58/20:13 against a 18:55:17 -0300 freeze) is observed but is not a receipt, and the machine's timezone against the commit offset is not verified `[INFERENCE]`. Q99 now states this limit in its row. Route: L1 decides whether the dispatch clause needs an untracked-file reader (a frozen-instrument change, so a named limit this round).

F2 — the round-40 red is grammar-only (Q99 must say so).
`freeze-check-r40-tip.txt` reports 18 `FIELD-MISSING` findings and no freeze-specific class. The C2 retro leg therefore shows that the gate fires on a file without key lines; it does not show the tool would have caught M40-3/M40-4/M40-5 on the prose of that file. Q99 states this.

F3 — M41-2 overstates "the only committed Codex error text" (lesson defect, routed to L1; append-only fix suggested).
`git grep -c 'Codex error' bffcc0f -- .` finds, in addition to `LOG.md:1909` (which carries the text, as the I4 block says): `census/round-20/recovery-seat-outcomes.json` (4 occurrences), `.ufo/waves/round-21/provider-error-excerpts.json`, `corpus/lessons/round-22.md`, and `census/round-26/…/round-22.md`. M41-2 says "the only committed Codex error text in the lane is a different message (`census/round-20/recovery-seat-outcomes.json`)". That sentence is false at `bffcc0f`. The I4 derivation itself is unaffected (the derived string `flagged as potentially` occurs only in `LOG.md`).

F4 — M41-4 scope claim confirmed (Q101 evidence).
Lane-wide `flagged as potentially` at `bffcc0f` = 1 (`LOG.md`); waves-only = 0. The I4 token `occurrences=0` is true only under `census/round-40/waves/`. Reviewer F-I4-1/F-I4-2 (`R41reviewer03.md` lines 79–80) are consistent with this.

F5 — Q98 count is revision-bound (confirmed; the rule has teeth).
The same command gives 2 at `bffcc0f` and 3 at tip (S258 added). A rationale that quotes "2" without `bffcc0f` is not re-runnable at tip, so Q98's "at the cited revision" requirement is load-bearing here, not decorative.

F6 — Q100 substance check status.
The C3 execution-count shim (`shim-audit.txt`, `tool_invocations=21` for R41executor01–06) is an audit outside the frozen counter; the frozen `c3-counter.py` still admits sniffing candidates (N6; `R41critic04` trick B reads `mut-S<NN>.py`). Q100 therefore says the mutant battery is a substance check only when its labels are unreadable to the candidate, and records the gap as a named limit. I did not run any sniffing variant (out of this seat's scope; R41critic04 reported it).

## Scope and bounds

- No file under `tests/`, `tools/`, `census/`, `corpus/`, `SKILL.md`, or any tracked file was written. Only `.ufo/waves/round-41/w2/R41w2scribe01.md` and `.ufo/waves/round-41/w2/R41w2scribe01/` (quality-rows.md and receipts/) were created.
- Not measured here: any landed-candidate change, the wave-1 critic sniffing candidates, the full C1 item population (only the frozen three), and the DISPATCH clause over untracked files (F1).
- No subagent dispatched (leaf member).
- Tools installed: none. Pacman untouched.
