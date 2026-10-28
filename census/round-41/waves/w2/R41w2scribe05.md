# R41w2scribe05 — PROVINCE "Round 41 boundary note" draft (souji round 41, wave 2, scribe)

Seat: scribe (leaf, no dispatch). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, tip `1d41c13574db80fdd9a4bde490b712da7ce2a85f`, freeze `e2a74312af4233963e44e4dbb38838ece07b8bd2`.
Deliverable: `.ufo/waves/round-41/w2/R41w2scribe05/province-note.md` (draft; PROVINCE.md not edited; L1 lands it).
Scratch: `/fast/scratch/hyaku/souji-r41/R41w2scribe05` (used for `fc.py` extract and counter `--scratch`; removed before yield). No git or jj mutation; `git status --porcelain` in the lane = 0 lines after my runs. No tool installs.

## 1. Inputs read

- `PROVINCE.md` full (289 lines): `## Owns` (:6-17), `## Refuses` (:32-47), `## Adjacency` (:48-57), Core/Frontier (:58-88), Round 13 (:89), Round 14 (:99), Round 29 (:174), Round 30 (:195), Round 31 (:213), Round 32 (:238), Round 39 (:276, last section).
- **No "Round 40" boundary note exists** in `PROVINCE.md` (`grep -n "^## " PROVINCE.md`; `git log -S "Round 40 boundary" -- PROVINCE.md` empty). The task's "Round 29/40 notes" therefore resolves to Round 29 plus Round 39 (the most recent, used as the format precedent).
- `.ufo/waves/round-41/w1/R41connector01.md` (full, 111 lines).
- `.ufo/waves/round-41/w1/R41scout02.md` (grep for sibling names; see §4 correction).
- Landed artifacts: `tools/souji-freeze-check.py` at `119c26fa…` (215 lines, read in full); `census/round-41/preregistration.txt` (frozen; read in full); `census/round-41/c2-counter.py` lines 1-60 and retro leg (`:292-310`).
- Receipts: `census/round-41/records/{c1,c2,c3,r1}-after.txt`, `shim-audit.txt`.

## 2. Commands run and observed output

Setup and identity (lane root, scratch dir created):

```
$ mkdir -p /fast/scratch/hyaku/souji-r41/R41w2scribe05 .../round-41/w2/R41w2scribe05
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel
/home/vgpnk/Projects/shokunin/souji-shokunin
$ git ... cat-file -t {119c26f,a114412,97eeb01,31e4d3e,e2a7431}   -> commit (all five)
$ git ... merge-base --is-ancestor e2a7431 1d41c13 && echo freeze-is-ancestor-of-tip    -> freeze-is-ancestor-of-tip
$ git ... merge-base --is-ancestor 119c26f 1d41c13 && echo 119-ancestor-of-tip           -> 119-ancestor-of-tip
$ git ... log --oneline -8 1d41c13   -> 1d41c13 measurement receipts; 31e4d3e C1 lesson/S258/snapshots; 119c26f C2 tool;
                                        97eeb01 R1 fixture; a114412 C3 battery; e2a7431 freeze prereg; 6682b98; e9dc38d
```

Tool bytes (tip vs landed vs candidate):

```
$ git show 1d41c13:tools/souji-worktree-drift.py | sha256sum
b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6   (matches prereg rule 1 pin)
$ git show 1d41c13:tools/souji-freeze-check.py | sha256sum
3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b
$ git show 119c26f:tools/souji-freeze-check.py | sha256sum                                     -> 3c3e80ba…340b
$ sha256sum .ufo/waves/round-41/w1/R41executor07/souji-freeze-check.py                         -> 3c3e80ba…340b
```

Freeze-check on the frozen prereg at tip (read-only, `-B`):

```
$ python3 -B tools/souji-freeze-check.py --root <lane> --prereg census/round-41/preregistration.txt --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f
SUMMARY claims=3 findings=0
exit=0
```

Freeze-check on the round-40 prereg at tip (the retro case):

```
$ python3 -B tools/souji-freeze-check.py --root <lane> --prereg census/round-40/preregistration.txt --rev 1d41c13...
(18 lines) FINDING C1|C2|C3 FIELD-MISSING {Base,Control,Counter,Kill,Population,Target}
SUMMARY claims=3 findings=18
exit=1
$ ... | awk '{print $3}' | sort | uniq -c
     18 FIELD-MISSING
```

Committed counters at landed revisions (scratch `--scratch /fast/scratch/hyaku/souji-r41/R41w2scribe05/{c1,c2,c3,r1}`):

```
$ python3 -B census/round-41/c2-counter.py --root . --rev 1d41c13… --scratch …/c2
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=18 summary=(3, 18)
SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8
EXIT=0

$ python3 -B census/round-41/c3-counter.py --root . --rev a1144120… --scratch …/c3
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=f32022e28fe2
(EXIT=0 per receipt; tail shows the SUMMARY line)

$ python3 -B census/round-41/c1-counter.py --root . --rev 31e4d3e… --scratch …/c1
ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes
ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=1 intact=yes
ITEM I4 present mismatch=yes derived=occurrences=0 corrections=1 intact=yes
SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1

$ python3 -B census/round-41/r1-counter.py --root . --rev 97eeb01… --scratch …/r1
SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=12 tool_sha=b2a603cf4247 fixture_sha=a2880a914106
```

Committed-counter re-runs agree with the receipts in `census/round-41/records/`. These are re-runs of committed counters only; no candidate was scored and `score-candidate.sh` was not used.

Name-family and reference greps:

```
$ for d in *-shokunin; do grep -rIl --exclude-dir=.git --exclude-dir=.jj --exclude-dir=.ufo -F "freeze-check" "$d" | wc -l; done (non-zero only)
chousa-shokunin 7   kake-shokunin 1   kasegi-shokunin 10   kengaku-shokunin 27
kotodama-shokunin 1   lore-shokunin 1   mori-shokunin 1   souji-shokunin 6
$ grep -rIl ... -F "souji-freeze-check" (fleet root, excluding .git/.jj/.ufo)
  -> souji corpus/lessons/round-41.md, census/round-41/{c2-counter.py,score-candidate.sh,controls/c2-control.txt,preregistration.txt}, tools/souji-freeze-check.py   (no hit in any other lane)
$ grep -rIl -F freeze-check kengaku-shokunin/tools kengaku-shokunin/scripts   -> 0 files
$ grep -rIl -F "freeze-check --double-read" kengaku-shokunin                  -> 70 files
$ sed -n 10,14p kumitate-shokunin/scripts/plan-before-ready.sh
#   MARKER = oldest commit that ADDS a top-level .ufo/waves/round-R/*.ready
#            (fallback, only if no .ready was ever added: a top-level *-dispatch.json)
```

Sibling tools (read headers only):

```
kasegi-shokunin/corpus/instruments/freeze-check.py   394 lines; docstring: replays each claim's counter_cmd at base tree; FC-* ids
mori-shokunin/tools/mori-freeze-order.py             708 lines; "Check whether frozen claim inputs predate their implementation commits."; SCHEMA mori-freeze-order-v1
chousa-shokunin/tools/freeze-check.py                round 61; "pre-ready check of a wave's frozen claims, spec and dispatch payload";
                                                     chousa SKILL.md:149 row `freeze-check` (round 61) | tool
```

Read-only-ness of the tool (grep of `tools/souji-freeze-check.py` at 119c26):

```
subprocess git calls: rev-parse --verify, cat-file blob, merge-base --is-ancestor, log --diff-filter=A ... (no write/update/commit/branch/worktree subcommands)
env: LC_ALL=C GIT_OPTIONAL_LOCKS=0 GIT_TERMINAL_PROMPT=0
no open(...,'w'), unlink, rmtree; only file write is stdout/stderr
```

## 3. Verification of each claim in the draft note

| # | Draft statement | Evidence | Verdict |
|---|---|---|---|
| 1 | C2 adds `tools/souji-freeze-check.py`; C3/R1 add two fixtures; no receipt class, no deletion authority; no Owns/Refuses/Adjacency row changes | second-pass command `git diff --stat e2a74312af4233963e44e4dbb38838ece07b8bd2 1d41c13574db80fdd9a4bde490b712da7ce2a85f` printed `13 files changed, 3754 insertions(+)`, listing only `census/round-41/*`, `corpus/SOURCES.md`, `corpus/lessons/round-41.md`, `tools/souji-freeze-check.py`, `tests/fixtures/r41-*.py`; `git log e2a7431..1d41c13 -- PROVINCE.md SKILL.md corpus/QUALITY.md` printed nothing | verified |
| 2 | Certification OFF, K5 HELD | carried from `PROVINCE.md` Round 39 (`:276-289`) and Round 14 text; the freeze..tip diff stat above lists no certification file | verified for round-41 commits; restated, not re-derived |
| 3 | Tool reads `census/<round>/preregistration.txt` as blob at 40-hex `--rev`; checks freeze fields and counter/population sha256 | tool `:6-16`, `Repo.blob` `:56-58`, `check_path_sha` `:114-133`; `main` refuses non-40-hex `--rev` `:191-192` | verified |
| 4 | Read-only on `--root`; git objects only | git subcommands in `Repo.run` (`:43-48`); no writes (grep above) | verified |
| 5 | Not fleet orchestration; dispatches, locks, starts nothing | tool contains no process spawn other than `git` (`:45`); no lock/dispatch code | verified (code read) |
| 6 | Not a protocol gate; no fleet addendum, template, script or sibling SKILL invokes it | `souji-freeze-check` string appears only in souji paths (grep above); sibling SKILL hits are their own tools | verified for the name `souji-freeze-check`; the fleet addendum prose was not re-read and is not edited by this round |
| 7 | No authority over other lanes; FINDING is advice to the L1 | Tool takes any `--root` (code read); outputs stdout only, exit 0/1/2 | verified in code; the "advice" wording is the note's framing, not a tool contract |
| 8 | Round 13/14 wording applies | `PROVINCE.md:89-110` read in full | verified |
| 9 | DISPATCH-BEFORE-FREEZE re-derives, does not cite, kumitate's marker rule; rules differ (top-level vs any depth; `.ready` only vs `.ready` with `*-dispatch.json` fallback) | tool `dispatch_findings` `:88-111` (matches `*-dispatch.json` or `*.ready` at any depth; no citation in docstring `:1-17`); kumitate `plan-before-ready.sh:12-13` (quoted above) | verified |
| 10 | Battery covers existing `tools/souji-worktree-drift.py`, pinned sha256 b2a603…; 19 sites, 21 probes; adds no code path or class to that tool | tip sha b2a603… matches prereg rule 1; C3 SUMMARY above; fixture is a test file only (a114412 stat, 91 insertions, one file) | verified |
| 11 | R1 adds mutant kills for the pinned tool; TOTAL repair landed before freeze at `e9dc38d` | r1 SUMMARY above; commit order `e9dc38d` → `6682b98` → `e2a7431` in `git log` | verified |
| 12 | kasegi freeze-check replays counter_cmd at a base tree; FC-* ids; claims-v2 JSON | kasegi docstring lines 1-22 (read) | verified from header |
| 13 | mori-freeze-order checks frozen claim inputs predate implementation commits; `mori-freeze-order-v1` | mori header and SCHEMA line (read) | verified from header |
| 14 | chousa `tools/freeze-check.py` is a pre-ready gate wired into SKILL | chousa header; `chousa-shokunin/SKILL.md:149` | verified |
| 15 | Four-lane naming is at most "two other lanes ship a tool named freeze-check" (kasegi, chousa); kengaku cites an undefined command | grep counts above; kengaku `tools`/`scripts` 0 files | verified; the 70-file count is my grep on `-F "freeze-check --double-read"` |
| 16 | "Round 40 note" does not exist | `grep -n "^## " PROVINCE.md`; `git log -S` empty | verified |

## 4. Corrections to wave-1 reports (for the L1)

1. **R41scout02 does not name kasegi `freeze-check.py` or mori `mori-freeze-order.py`.** Its report (grep for `kasegi|mori-freeze|freeze-order|chousa`) names mori only as `mori-round14/15-regressions.py`, and kasegi nowhere. The sibling-tool naming the task attributed to scout02 is in **R41connector01 §2 C2 "Overlap 2"** (`R41connector01.md:44-48`, §5 pointers `:104-105`). The draft note cites the tools directly, not either report.
2. **R41connector01 omitted chousa's `tools/freeze-check.py`.** Its §3 counts list kake, kasegi, kengaku, kotodama, lore, mori only. My same grep finds chousa 7 files and a shipped `tools/freeze-check.py` (round 61) with a SKILL.md row. Chousa's check is the closest sibling to souji's `DISPATCH-BEFORE-FREEZE`, so this changes the adjacency picture and is in the draft note.
3. **R41connector01 recommended citing kumitate's marker definition in the freeze-check docstring.** The landed docstring (`tools/souji-freeze-check.py:1-17`) does not cite kumitate. The draft note records the divergence instead of asking for a docstring edit (no edits are in scope for this seat).
4. **Connector's "PROVINCE.md:17 `gates over own evidence`"** — line 17 reads "Dry-run censuses and removal-list proposals for operator approval." The phrase "gates over own evidence" is not in that line; the closest verbatim wording is Round 13/14 (`:89-110`). The draft cites Round 13/14, not `:17`.

## 5. Calibration limits found (report, do not absorb)

- **C2 retro leg is grammar-only.** `census/round-41/c2-counter.py:292-304` accepts retro as red when exit is 1 and findings ≥ 3. The round-40 file produces exactly 18 `FIELD-MISSING` findings and no freeze-class finding (`uniq -c` above). The freeze-class classes are exercised by the 21 synthetic cases (`census/round-41/c2-cases.tsv`, 22 lines including header), not by the retro file. The draft note says so (Limit paragraph). This does not falsify C2's frozen target as written; it does mean "retro=red" evidences grammar rejection, not detection of the r40 M40-3..5 freeze defects.
- **DISPATCH-BEFORE-FREEZE vs kumitate.** Two different marker rules co-exist (see §3 row 9). Route to kumitate; no change to the frozen tool.
- **Name family.** Three tools share the bare name `freeze-check` plus one undefined command (kengaku). The souji tool keeps its prefixed name.

## 6. Verdict

**Draft ready for L1 to land, with the limits in §5 stated in the note.** Every factual claim in `province-note.md` is traced in §3 to a command or file read in this seat; rows 12-14 rest on sibling headers, not on running those tools. Corrections §4 change two wave-1 attributions and one missed sibling; none changes a frozen counter, population, control or pinned tool. C1, C2, C3 and R1 are not re-scored here (the seat's measured figures are the committed counters' outputs in §2 and the receipts). No candidate was scored; `score-candidate.sh` was not run.

## 7. Evidence pointers

- `PROVINCE.md:6-17` Owns; `:32-47` Refuses; `:48-57` Adjacency; `:89-98` Round 13; `:99-110` Round 14; `:276-289` Round 39.
- `tools/souji-freeze-check.py` at `119c26fa3bbb85e215824de9538bd2eb34e9f874` (sha256 `3c3e80ba…340b`): `:6-16` docstring, `:45-48` git runner, `:88-111` dispatch rule, `:114-133` digest checks, `:182-211` main.
- `census/round-41/preregistration.txt` (frozen C1/C2/C3/R1 blocks, lines 18-54).
- `census/round-41/c2-counter.py:45-57` real/retro legs and target; `:292-310` retro leg code.
- `census/round-41/c2-cases.tsv` (21 cases).
- `census/round-41/records/{c1,c2,c3,r1}-after.txt`, `shim-audit.txt`.
- `tests/fixtures/r41-refusal-sites.py` at `a1144120611b00091ac4839559d8ebf38aa9a83a`; `tests/fixtures/r41-drift-record-order.py` at `97eeb01e73a9baa3e4191b9052fed9e505c70215`.
- `kumitate-shokunin/scripts/plan-before-ready.sh:12-13`.
- `kasegi-shokunin/corpus/instruments/freeze-check.py:1-22`; `mori-shokunin/tools/mori-freeze-order.py:1-12`; `chousa-shokunin/tools/freeze-check.py:1-12`; `chousa-shokunin/SKILL.md:149`.
- `.ufo/waves/round-41/w1/R41connector01.md:32-48, 79-86, 104-105`; `.ufo/waves/round-41/w1/R41scout02.md:39, 53, 56, 61, 69-71, 79-82, 91`.
- Draft: `.ufo/waves/round-41/w2/R41w2scribe05/province-note.md`.
