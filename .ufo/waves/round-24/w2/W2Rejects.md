# W2Rejects — souji r24 wave 2 (FALSIFY): the two rejects and the r25 partial admit

## Status
STATUS: PARTIAL. Both rejects stand: each has at least one reason that is TRUE of the staged bytes and enough on its own. Two Gate reasons are not true as written. Entry line 145 says the lane's ids S130–S153 name other documents, but the lane has no such ids. Entry line 144 calls S131 payload-absent, but the lane's own hand-check committed at the same revision found the payload present. The r25 partial admit is **falsified on provenance**. Its content survives: I re-ran all five modes and each reads 1. But its "committed witness" (C1 case 4) runs only one creation mode, and that mode is a spelling not among the five. The seat report the admit leans on did not exist at the admitting revision 778747e.

## Evidence
- Lane revisions read: admit/after-state `778747eb671f8e85ef5387bc3d7023337b30467c`, after-receipts `ca7fc1c`. The lane tip has moved to `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`: `git rev-parse master`, and `git log a65fac98..master` shows `c3ca7ad round-24: wave-1 seat reports, drafts and registry (38 seats)`. The context's `ca7fc1cb` is no longer the tip.
- Staged bytes (shokuknow, read-only; opened and hashed this run, numbered with `cat -n`; line 1 is blank in all three):
  - `garbage-false-positive-modes-r26.md`: sha256 `2ce3dc31…0c6f`, 52 lines.
  - `count-objects-garbage-semantics-r23.md`: sha256 `c140aee8…031c`, 79 lines.
  - `garbage-false-positive-modes-r25.md`: sha256 `0b44a08f…d769`, 57 lines.
- Gate under attack: `corpus/knowledge/count-objects-linked-worktree-garbage.md`. At 778747e and at the tip, lines 141–145 hold the r25 ADMIT, the r25 REJECT, the r26 REJECT, the r23 REJECT and the provenance REJECT.
- Receipts:
  - `python3 -B tools/souji-receipt-run.py verify --root … census/round-24/records/c1-after.tsv` → `verify=ok rev=778747eb…`, rc 0.
  - Same for `gate-check-r24-entry.tsv` → `verify=ok`, rc 0.
  - The `c1-after.tsv` stdout reads `CASE 4 linked PASS exit=0 counts=0,0,0,0 manifest_changed=0 raw_linked_garbage=1`.
- Presence per revision (`git cat-file -e`):

  | path | 778747e | ca7fc1c | c3ca7ad |
  |---|---|---|---|
  | `.ufo/waves/round-24/w1/ProbeLinkedModes.md` | absent | absent | present |
  | `.ufo/waves/round-24/w1/ProbeGarbageKinds.md` | absent | absent | present |
  | `.ufo/waves/round-24/w1/ScoutPkgEntries.md` | absent | absent | present |
  | `census/round-24/records/c1-after.tsv` | absent | present | present |
  | `tests/fixtures/r24-size-census.py` | present | present | present |

- Scratch probe, run this session in `/var/tmp/souji-r24-W2Rejects/` (btrfs; `git version 2.56.0`; GIT_* unset; `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`):
  - **Worktree reads:**
    - main worktree: `garbage: 0 size-garbage: 0`
    - `worktree add <path>` (the case-4 spelling): `garbage: 1 size-garbage: 0`, with a new branch named `w_default`, after the path
    - `--detach`, `-b`, `--orphan -b`, `--detach`+commit, `-b`+commit: each `garbage: 1 size-garbage: 0`
    - every linked cell has a private `refs`, and that empty directory has `st_size` 0
  - **Main-worktree debris** (counterexample to r26):
    - 2048 B junk in `objects/pack` → `garbage: 1 size-garbage: 2`
    - `objects/12/zz` → `garbage: 1 size-garbage: 0`
    - a stray file plus a stray directory directly in `objects/` → `garbage: 0 size-garbage: 0` (r26's arms reproduce)
  - **Directory size is counted:** six 250-character file names placed inside one linked worktree's private `refs/` make its `st_size` 3012, and the read becomes `garbage: 1` / `size-garbage: 2`.
  - **The `-v` field set:** with an alternate configured, the fields are `count size in-pack packs size-pack prune-packable garbage size-garbage alternate`, and the alternate line reads `alternate: /var/tmp/souji-r24-W2Rejects/r/.git/objects`.
  - Scratch removed at the end of the run.
- shokuknow (read-only `sha256sum`/`cat`, no tool run):
  - `lanes/souji/round5/evidence/r26-garbage-second-mode.out` sha256 `7714641c15ef…e5ca`, which equals S147's prefix.
  - The same `.out` has a line `--- ARM 1: the LIVE fleet's MAIN worktree (no linked worktree in scope) ---`.
  - `fixtures/r26-garbage-second-mode.sh` line 50 runs `garbage_of /home/vgpnk/Projects/shokunin`.
  - `round2/evidence/r23-worktree-census.out` sha256 `1ac71c4f…92fd`, which equals S131's prefix.
- Lane ids:
  - The `corpus/SOURCES.md` id column at master ends at `S123`.
  - `.ufo/waves/round-24/assimilation/collisions` holds `S109 … S119` only.
  - S130, S131, S134, S141, S147 and S153 appear in neither `reg-ids` nor `collisions`. Lane S112 is "gio(1), GIO commandline tool" and S113 is "GLib GIO g_file_trash() method reference".
  - The `git ls-tree -r master` names grep finds no `r26-garbage`, `r25-garbage-matrix`, `r23-worktree-census` or `r23-garbage-probe` file in the lane.

## Findings

### A. r26 REJECT (entry line 143)
1. **Falsified central claim: TRUE.**
   - Staged line 16: "1. **Nothing else does.** Four arms, git 2.56.0:". Staged line 24: "2. **So the trigger is exclusively the linked-worktree path**".
   - Junk in `objects/pack` and an invalid loose name read `garbage: 1` on a main worktree (scratch run above).
   - The committed lane witness is C1 case 3, whose main arm reads `main[exit=0 counts=1,2,0,0 …]` (`c1-after.tsv`).
   - Staged lines 25–26 are falsified by the same cells: "real debris in the object directory is not counted".
   - The Gate's "12 ProbeGarbageKinds cells" is uncommitted seat evidence at 778747e (Evidence table). The falsification does not depend on it, because one committed counterexample, case 3, is enough.
2. **Fleet arm: TRUE.**
   - Staged line 17: "the live fleet repo's **main** worktree → `garbage=0 size-garbage=0`". Staged line 44: "apart from arm 1, which read the live fleet repo read-only".
   - The shokuknow `.out` and line 50 of its `.sh` confirm that arm 1 read `/home/vgpnk/Projects/shokunin`.
3. **shokuknow-only evidence: TRUE.**
   - Staged line 2: "source: S147 — lanes/souji/round5/fixtures/r26-garbage-second-mode.sh — evidence/r26-garbage-second-mode.out (sha256 7714641c…)".
   - The payload exists only under shokuknow `lanes/souji/round5/` (hash matches). There is no lane copy and no lane S147.
4. **Id collision (fsck pointer): TRUE.** Staged lines 42–43: "must use `git fsck --unreachable` (which the lane's S113 holds)". Lane S113 is g_file_trash; the lane's fsck row is S116.
5. **Unlisted defect, not in the Gate.** Staged lines 40–41, "the counted entries are **directories**, which contribute no byte size", is refuted by the 3012-byte `refs/` that reads `size-garbage: 2`.
6. **Survives inside r26.** Its line-27 mechanism pointer `builtin/count-objects.c:118` matches the committed snapshot. The lane admits that line separately via S122.

### B. r23 REJECT (entry line 144)
7. **Fleet claims: TRUE.**
   - Staged line 13: "and the fleet is not currently exposed".
   - Staged lines 33–34: "**The fleet's live census (S131).** The fleet repo (`/home/vgpnk/Projects/shokunin`) has **5 worktree registrations".
   - Staged lines 77–78: "The live census (S131) shows the fleet is currently clean".
8. **"S131 is quarantined payload-absent": stale; TRUE only of the register tag.**
   - The quarantine slice lists `S131   \`payload-absent\``. But `census/round-24/records/slice-verdicts.tsv` line 7, committed in the same 778747e, reads "S131 accepted census output 1ac71c4f matches; fleet census, not lane-re-derivable".
   - The shokuknow hash matches (`1ac71c4f…`), so the payload is present.
   - The reject still holds, because the census is a fleet census and cannot be re-derived from lane bytes.
9. **Id collision (S112/S113): TRUE.**
   - Staged line 4: "source: S112 — https://git-scm.com/docs/git-count-objects". Staged line 5: "source: S113 — https://git-scm.com/docs/git-fsck".
   - Lane S112 is gio(1) and lane S113 is g_file_trash; both appear in `assimilation/collisions`.
10. **Contradicted "only two fields": TRUE.**
    - Staged lines 26–27: "`garbage`/`size-garbage` are the only two fields of `count-objects -v` that are not object-graph state".
    - Committed `census/round-24/sources/git-count-objects.1.txt` line 32 reads: "alternate: absolute path of alternate object databases; may appear multiple times, one line per path." The scratch run printed that field.
    - The reason is understated, not wrong: `size` and `size-pack` (lines 18, 24, "disk space consumed by") are also disk measures, not graph state.
11. **Directory-size reason wrong: TRUE.**
    - Staged lines 24–25: "`size-garbage` was 0 in both runs, because a directory has no meaningful byte size in the accounting".
    - The snapshot `git-v2.56.0-builtin-count-objects.c` lines 49–50 read "if (!stat(path, &st))" and "size_garbage += st.st_size;".
    - A 3012-byte private `refs/` reads `size-garbage: 2`. The 0 seen in the staged runs comes from btrfs reporting `st_size` 0 for an empty directory, and from floor division by 1024.
12. **Unlisted defect, not in the Gate.**
    - Staged lines 29–31 claim `bits_to_msg()` messages mean "i.e. pack directory debris".
    - The `bits_to_msg` part is true: snapshot lines 24–38 hold exactly the four messages.
    - The "i.e." conclusion is false. "garbage found" is also emitted for loose cruft (`objects/12/zz` → `garbage: 1`) and for the linked sweep, as the entry's own staged line 18 shows.

### C. Provenance REJECT (entry line 145)
13. **"this lane's ids for those numbers name other documents": FALSE.**
    - Lane SOURCES ends at S123, and none of S130, S131, S134, S141, S147 or S153 is in `reg-ids` or `collisions`. Only S109–S119 collide.
    - The first clause ("own-work rows whose evidence lives in shokuknow") is TRUE: the hashes above match shokuknow payloads, and the lane holds none of these files.

### D. r25 partial ADMIT (entry line 141): attack
14. **"Committed witness" covers one mode, and not one of the five.**
    - `tests/fixtures/r24-size-census.py` line 184 runs `s.git('-C', repo, 'worktree', 'add', '-q', linked)`. That is DWIM `worktree add <path>`, an implicit new branch named after the path.
    - The admitted matrix is `--detach`, `-b`, `--orphan -b`, `--detach`+commit and `-b`+commit (staged r25 lines 18–21). Case 4 commits none of them literally, so 0 of the 5 cells are committed by case 4; it is at best a proxy for `-b`.
    - The admit's flip, "reject if C1 case 4 fails at the landing tip", cannot fire on a regression confined to `--detach`, `--orphan` or the post-commit cells.
15. **The cited lane evidence was absent at the admitting revision.**
    - Entry lines 39–41 cite `.ufo/waves/round-24/w1/ProbeLinkedModes.md` as lane-measured evidence. That file is absent at 778747e and ca7fc1c and appears only at c3ca7ad.
    - The same holds for `ProbeGarbageKinds.md` (item 5) and `ScoutPkgEntries.md` (item 4).
    - QUALITY Q17 (`corpus/QUALITY.md` line 41): "A claimed committed fixture or evidence fragment must resolve to a contained regular, non-symlink file at the measured revision".
    - `gate-check-r24-entry.tsv` still reports `entries=1 ok=1 … fail=0`, so the gate checker does not resolve these bracketed evidence paths.
16. **Even at the tip, the five-mode evidence is prose only.**
    - ProbeLinkedModes records "Script `matrix.sh` sha256 `bc1a82a8…`. Output `out.txt` sha256 `0d4036e0…`. Both were removed with the scratch dir".
    - The lane holds a table excerpt, not re-derivable bytes.
17. **Content survives.** This run reproduced `garbage: 1` with a present, empty private `refs` in all five modes plus the case-4 spelling, with the main worktree at 0. The matrix is true on 2.56.0; only its "committed" label is false.
18. **Minor: the r25 REJECT locator (entry line 142) is incomplete.**
    - It says "staged file line 1-30" for "its directory-size reason". Line 24 carries only the observation "with `size-garbage: 0` throughout".
    - The reason itself is at staged lines 48–49: "means the counted entries are **directories**, which have no meaningful byte size in the accounting".

## Attack log
- **ATK-1** (r25 admit, identity and provenance). Counterexample: case 4's spelling is not in the admitted matrix, and the cited seat file is absent at 778747e.
  - Impacted axes: coverage (C1 knowledge side) and calibration (an entry states committed evidence the revision lacks).
  - Smallest safe correction: re-label line 141 and entry item 3. One mode, `worktree add <path>` with an implicit branch, is committed via C1 case 4; the five named modes are seat-observed (ProbeLinkedModes, bytes removed) and re-run by W2Rejects.
  - Alternatively, commit a separate `/var/tmp` mode-matrix probe with a receipt.
  - The frozen case set is not to be changed, and C1's verdict is unaffected.
- **ATK-2** (Gate line 145, false provenance). Counterexample: none of S130/S131/S134/S141/S147/S153 exists in the lane registry. Impacted: calibration. Correction: strike "and this lane's ids for those numbers name other documents", or restrict the collision clause to S112/S113 (r23) and the S113 pointer (r26).
- **ATK-3** (Gate line 144, stale reason). Counterexample: `slice-verdicts.tsv` line 7, same revision, says S131's payload is present and accepted. Impacted: calibration. Correction: "S131 is a fleet census whose payload lives only in shokuknow (1ac71c4f), not lane-re-derivable". The verdict is unchanged.
- **ATK-4** (Gate line 143, evidence weight). The "12 ProbeGarbageKinds cells" were uncommitted at 778747e. The falsification survives on committed C1 case 3 (main arm `counts=1,2`). Correction: cite case 3 as the committed counterexample. The verdict is unchanged.
- **survives**: r26 reasons 1–4 and r23 reasons fleet, collision, two-fields and directory-size are TRUE of the staged bytes (Findings 1–4, 7, 9–11). Both REJECT verdicts stand.
- Tooling: none installed or updated. Writes: this report only. Scratch `/var/tmp/souji-r24-W2Rejects/` was created and then removed. shokuknow was read only, with no tool executed there.
