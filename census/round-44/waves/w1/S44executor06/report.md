# S44executor06 — C1 correction-register partition 6/16

Axes: calibration (assigned); operability and coverage were not exercised.

## Result

Created `corrections.txt` with five emitted unique records at 1-based emission ordinals 6, 22, 38, 54, 70 (equivalently zero-based indices 5, 21, 37, 53, 69, all index mod 16 = 5). Each line uses the frozen counter's derivation and required scope/revision, with no optional fields. These are registrations of base SCORECARD token referents, not claims that five new factual errors were discovered; historical corrections remain authoritative and SCORECARD was not rewritten.

## Commands and evidence

Repository identity: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel` → `/home/vgpnk/Projects/shokunin/souji-shokunin`; `rev-parse HEAD` → `d314fd6e85d62565344fa6c4b102f52f62297884`. `git cat-file -e <freeze>^{commit}` and `git cat-file -e 55d7af6f5a22340f7a3de1c386e514ababfaa75f^{commit}` both succeeded (no output, exit 0).

Ran:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor06 --emit
```

The selected exact emitted records were:

```text
R44-06 line=50 class=mismatch:path-absent stale=w2/RevR3Counter.md derived=.ufo/waves/round-25/w2/RevR3Counter.md
R44-22 line=424 class=mismatch:path-absent stale=c3-after-c3-counter-v2.txt derived=census/round-31/records/c3-after-c3-counter-v2.txt
R44-38 line=700 class=mismatch:path-absent stale=c2-after4.txt derived=census/round-38/records/c2-after4.txt
R44-54 line=763 class=mismatch:path-absent stale=c3-before.txt derived=multi:census/round-37/records/c3-before.txt;census/round-38/records/c3-before.txt;census/round-39/records/c3-before.txt
R44-70 line=823 class=mismatch:path-absent stale=controls/c3-control.txt derived=multi:census/round-41/controls/c3-control.txt;census/round-42/controls/c3-control.txt
```

Counter exit status: 0. The counter independently obtains base bytes through `git show BASE:path` and paths through `git ls-tree -r --name-only BASE`, as specified in its source. Thus the single paths and multi-path sets above are committed base referents, not worktree-path guesses. Files/digests for these five are class `mismatch:path-absent`; no unresolved or digest class occurs in this partition.

Q76 prior coverage check: reviewed committed `corpus/lessons/round-42.md` and `corpus/lessons/round-43.md` at the freeze; checked for exact token/line references. **No** r42 or r43 correction already covers any of these five `(line, stale-token)` items. R42's C1 entries concern lines 14, 68 and 92 (plus 175 as distinct scope); R43's C1 corrects r39 census records, not SCORECARD. Therefore the R44 lines register referents not covered by those earlier correction entries, but registration alone remains no new factual correction. Existing R44 register lines R44-06, -22, -38, -54, -70 were also present in the frozen round-44 lesson; this partition is a delivery of those assigned lines, not a claim of novel corrections.

## Limits

Only the assigned five-row derivation/registration was run. The full C1 counter was not run without `--emit`, because the task is partition delivery and the frozen lesson already contains the full register. No SCORECARD, frozen counter/population, lesson, sibling output, shared LOG, or repository state was modified. Scratch directory was removed before handoff. No tool was installed.
