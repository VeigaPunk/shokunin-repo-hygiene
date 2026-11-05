# S61ExecRealRecord — round-61 w1 findings (real-record chronology, read-only)

Scope: independently verify the round-60 real-record chronology facts and the r60 spot-check routed-defect claims. Read-only git (`log`, `show`, `cat-file`, `ls-tree`, `merge-base`, `grep`, `ls`, `cmp`) against lane `/home/vgpnk/Projects/shokunin/souji-shokunin`. No lane instruments run, no writes outside the delivery dir, no subagent spawned, no tool installed.

Delivery dir: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-61/w1/S61ExecRealRecord/`
- `erratum-evidence.txt` — exact commands, full outputs with `EXIT=`, per-receipt verdicts
- `erratum-evidence.sh` — the script that produced the transcript (verbatim)
- `critic-finding-1.txt` — verbatim critic Finding 1 with path:line

## Verdicts

1. **Both r60 control receipts VIOLATE the Q120 chronology rule.** `census/round-60/controls/c1-do-nothing.txt` and `c2-do-nothing.txt` are both added by `2670e96af1b81c7aa793acc34d40361b4beecff8` (`2026-11-04T21:05:50-03:00`, "round-60: freeze the two claim predicates after executed red controls") — the freeze commit itself. Neither is a strict ancestor of the freeze (add == freeze; `merge-base --is-ancestor` returns 0 only because a commit is trivially its own ancestor). This matches the critic's Finding 1.
2. **The prose claim is false.** `census/round-60/preregistration.txt` line 4 says controls were "executed and committed at `3b5525099356e15ff9d17b7fbd2835c2d3512eee`". At `3b5525...`, `git cat-file -e 3b55...:census/round-60/controls/c1-do-nothing.txt` → `fatal: ... exists on disk, but not in '3b55...'`, EXIT=128; same for c2 (EXIT=128). `git ls-tree -r --name-only 3b55... census/round-60/controls` prints nothing; `grep -c controls` over the `census/round-60` tree at 3b55 → 0, EXIT=1. At the freeze commit, `ls-tree` lists both receipts (EXIT=0). `3b55...` is a strict ancestor of the freeze (`merge-base --is-ancestor` EXIT=0), so the freeze's own chronology is not contradicted — only the receipts' placement is.
3. **Spot-check routed-defect claims hold at `c7228424c3919ecf142bab1aec8181722d86467b`:**
   - (a) `corpus/README.md` is unindexed for `freeze-record-substance-binding`: `git grep -c ... c7228424 -- corpus/README.md` → no matches, EXIT=1; worktree `grep -c` → `0`, EXIT=1. Matches the spot-check's own claim at `corpus/lessons/round-60-verifier-spotcheck.md:216` and `:231`.
   - (b) `census/round-60/w1/S60ExecFreezeArm/byte-identical.txt` → absent (`ls` EXIT=2). `census/round-60/wave/w1/S60ExecFreezeArm/byte-identical.txt` → present (3504 bytes, EXIT=0). The spot-check's path correction at line 234–235 is accurate.
   - (c) `grep -l S60CriticRound -r census/round-60/wave/w1/` lists `census/round-60/wave/w1/S60CriticRound.md` plus its `S60CriticRound/` subtree (EXIT=0). The two copies `S60CriticRound.md` and `S60CriticRound/S60CriticRound.md` are byte-identical (`cmp` EXIT=0). Finding 1 is at lines 44–84 (heading line 44; quoted prereg sentence lines 48–50; verdict VIOLATES) and is extracted verbatim into `critic-finding-1.txt`.

## Commands and exit codes (summary; full transcript in `erratum-evidence.txt`)

- `git -C $L rev-parse --show-toplevel` → `$L`, EXIT=0
- `git -C $L cat-file -t` on c7228424, 2670e96a, 3b552509, d05a0001 → `commit` ×4, EXIT=0
- `git -C $L log --diff-filter=A --no-renames --full-history --format='%H %cI %s' -- <path>` for both receipts and the prereg → `2670e96a…`, EXIT=0 ×3
- `git -C $L merge-base --is-ancestor 2670e96a… 2670e96a…` (receipts) → EXIT=0, but STRICT=NO (adding commit is the freeze)
- `git -C $L merge-base --is-ancestor 3b552509… 2670e96a…` → EXIT=0 (3b55 is a strict ancestor)
- `git -C $L cat-file -e 2670e96a…:census/round-60/controls/c{1,2}-do-nothing.txt` → EXIT=0 ×2
- `git -C $L cat-file -e 3b552509…:census/round-60/controls/c{1,2}-do-nothing.txt` → EXIT=128 ×2
- `git -C $L show --stat 2670e96a…` → 3 files, 60 insertions (controls c1 15, c2 24; prereg 21)

## Process notes

- An earlier draft of my ancestry loop tested the freeze commit against itself; that run was discarded. The shipped transcript (`erratum-evidence.txt`, section C) is from the corrected script, which tests each receipt's adding commit against the freeze and records STRICT=NO explicitly.
- The `git grep -c` and `grep -c` zero-match results return EXIT=1 by design (no matching lines); recorded as zero matches, not as errors.

## Tools

None installed or upgraded. Only pre-existing `git`, `grep`, `sed`, `cmp`, `ls`, `cat` were used.

## Named limits

- This verifies the chronology facts and the three routed-defect claims only. It does not re-verify the critic's other findings (2–8), the C1/C2 fixtures, or any `--substance` behavior; no lane instruments were run, per the seat spec.
- Scratch `/fast/scratch/hyaku/souji-r61/S61ExecRealRecord/` was used only for the transcript and removed; receipts were copied into the delivery dir before removal.
- The critic's `git ls-tree` excerpt is abbreviated (`matrix/...`); I checked only the claim that `controls/` is absent at 3b55 (verified), not the full listing.

## Calibration signal for C1 (read-only, for the L1)

The real-record arm must refuse this record with `CONTROL-ADDED-NOT-BEFORE-FREEZE` for both control receipts (adding commit `2670e96a`, not a strict ancestor), since the adding commit equals the freeze commit. The base tool's `findings=0` on this record is therefore a real miss, consistent with the critic's Finding 1.
