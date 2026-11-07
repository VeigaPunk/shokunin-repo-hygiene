# ScoutC1FleetDebt — fleet-hosted citations behind the landing gate's `--fleet-root` resolution

## Status
STATUS: PASS — all three fleet-hosted citations resolve to real, content-supporting files in the fleet repo; the citation set is fleet-documented (not stale, not a lane defect), and C1's two planned exemption rows leave all three untouched.

## Evidence

Commands run read-only this run (fleet root `/home/vgpnk/Projects/shokunin`, lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, base `e78ac7c4837b81b634db4a927605a751a7f006ba`, fleet HEAD `ecd8086ccc47f9cddd9305948d0e6f1773762716`, fleet `origin/master` `21d3c09a44bf3bbde480447a6be904e0aaee2563`, remote HEAD `a18d71f445358057b400293072e50f627da9873b`).

**1. The three cited fleet paths exist.**
```
$ ls -la /home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/ | grep -E 'Jj(Audit|Trial)Souji|^d'
drwxr-xr-x 1 vgpnk vgpnk 2346 Oct 20 11:39 ./
-rw-r--r-- 1 vgpnk vgpnk 45699 Oct 20 11:39 JjAuditSouji.md
-rw-r--r-- 1 vgpnk vgpnk 10241 Oct 20 11:33 JjTrialSouji.md
```
`ls -1 … | wc -l` → `68`; `stat -c '%F'` on the directory → `directory` (a real directory, not a symlink or file).

**2. The gate classifies all three as `fleet` (not findings) with `--fleet-root`, and finds them dangling without it.**
```
$ python3 -B tools/souji-landing-gate.py --root …/souji-shokunin --rev e78ac7c4837b81b634db4a927605a751a7f006ba --round 27 --fleet-root /home/vgpnk/Projects/shokunin --json …
ptr_fleet= 3 ptr_exempt= 4
fleet corpus/README.md:217 .ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md
fleet corpus/README.md:217 .ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md
fleet corpus/knowledge/jj-colocation-receipts.md:148 .ufo/waves/hyaku/jj-w1/reports/
findings= 2
```
```
$ … --round 27            # same rev, NO --fleet-root
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	corpus/README.md:217 cites path absent at e78ac7c4837b
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	corpus/README.md:217 cites path absent at e78ac7c4837b
LG-DANGLING-PTR	.ufo/waves/hyaku/jj-w1/reports/	corpus/knowledge/jj-colocation-receipts.md:148 cites path absent at e78ac7c4837b
SUMMARY	findings=5
```
The two remaining findings at base are the C1 targets (`corpus/knowledge/registry`, `corpus/lessons/round-24.md:232:S118`).

**3. Resolution mechanism (why the relative forms are correct).** `tools/souji-landing-gate.py:801` (`_normalize_pointer_path`) turns the README's `../../.ufo/…` (source `corpus/README.md`) into `../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md`, i.e. one level above the lane root = the fleet root; `:964-968` then strips the `../` and joins under `--fleet-root`. The entry's fleet-root-relative form `.ufo/waves/hyaku/jj-w1/reports/` takes the second branch. Gate comment at `:962-963`: "Only an explicit one-level escape or the known hyaku report" / "prefix may resolve under the separately supplied fleet root."

**4. The lane has no `hyaku` tree of its own** — `ls …/souji-shokunin/.ufo/waves/` → `round-13 … round-27`; `git ls-tree e78ac7c… --name-only .ufo/waves/` lists only round-13…round-26. So these three pointers are fleet-hosted by design and can only resolve under `--fleet-root`.

**5. The fleet files are git-tracked, unmodified, and byte-identical to the pre-incident revision.**
```
$ git -C /home/vgpnk/Projects/shokunin ls-tree HEAD -- …/JjAuditSouji.md …/JjTrialSouji.md
100644 blob c0bbf687e07ecde2b5e06cafeaa161f1ad831880	.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md
100644 blob 363d8ae310c4c3962972f8d64e2e1a4470b24d79	.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md
$ git -C /home/vgpnk/Projects/shokunin status --porcelain -- .ufo/waves/hyaku/jj-w1/reports/   # empty
$ git -C /home/vgpnk/Projects/shokunin rev-parse 0619111d:…/JjAuditSouji.md   # c0bbf687… (identical)
$ git -C /home/vgpnk/Projects/shokunin rev-parse 0619111d:…/JjTrialSouji.md   # 363d8ae3… (identical)
$ git -C /home/vgpnk/Projects/shokunin ls-tree origin/master -- …/JjAuditSouji.md …/JjTrialSouji.md
100644 blob c0bbf687e07ecde2b5e06cafeaa161f1ad831880	.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md
100644 blob 363d8ae310c4c3962972f8d64e2e1a4470b24d79	.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md
```
Same blobs at fleet HEAD, at `origin/master`, at remote HEAD `a18d71f4`, and at pre-incident `0619111d`.

**6. Content support — JjTrialSouji.md step 5 carries the README:217 numbers.**
`JjTrialSouji.md:53` is the "## Step 5 — lane's own git-touching checks (300 s timeout each)" heading; `:61` (verbatim, 20 words, no `|`):
> Any tool that counts "all refs" or unreachable objects sees them; `git rev-list --all` = 55 vs `--branches` = 44.

and `:57` of the same table row reads `references.others.count=15` from `refs/jj/keep/*` and `objects.commits.count=55` vs 44. The README cell's claim "colocated repos inflate structure counts versus a plain clone" (README.md:217) is therefore supported.

**7. Content support — the entry's inline file:line citations land on the expected fleet content.** Spot-checked, all consistent: `JjTrialSouji.md:23` (symbolic-ref attached→detached), `:48` (HEAD detached at 62fcf62), `:59` (census `dirty=1 unpushed=0`), `:61` (15 keep refs), `:62` (intent-to-add caveat), `:76` (nested `.git`, commit c31a345), `:78` (detached HEAD), `:79` (jj resets the index), `:80` (hazard 5), `:88` (keep `snapshot.auto-track="none()"`); `JjAuditSouji.md:55` (F1 heading), `:97-104` (branch-excluded probe + keep ref), `:107` (tameshi 12 / kama 10 / mado 16), `:154` (index entry not what jj committed), `:156-158` (F5 `measured_commit` `@-`), `:172` (hook bypass), `:58-72` (F1 body), `:122-128` (F3 probe block).

**8. Scratch experiment (contract-compliant copy under `/var/tmp/souji-r27-ScoutC1FleetDebt/`, `git init`ed, `git rev-parse --show-toplevel` verified) — C1's two rows do not touch the fleet set.** Appending the two planned rows `corpus/knowledge/registry` and `corpus/lessons/round-24.md:232:S118` to a scratch `corpus/pointer-exemptions.tsv`: `ptr_fleet` stayed `3`, `ptr_exempt` 4→6, and the two C1 findings disappeared (the single remaining scratch finding, `LG-FROZEN-MEASURED … tests/fixtures/r15-preservation-frozen/expected.json`, is an artifact of re-committing the tree in scratch so the pinned `measured_commit 005f3d37…` no longer exists; the real lane at `e78ac7c` reports `checked_measured=3` and no such finding).

**9. Scratch probe — exemption rows are matched BEFORE fleet classification.** Gate `:959-961` (`if path in exemptions: used_exemptions.add(path); continue`) precedes the fleet branch at `:964-983`. Adding an exemption row `.ufo/waves/hyaku/jj-w1/reports/` to the scratch exemptions file was accepted by `load_pointer_exemptions` (`:876`, `POINTER_ROOTS` at `:136` includes `.ufo/waves/`) and silently reclassified the directory citation: `ptr_fleet` 3→2, `ptr_exempt` 6→7, with **no** `LG-DANGLING-PTR-EXEMPT-STALE` (the row counted as used). C1's two rows are `corpus/`-scoped, so C1 is unaffected.

## Findings

1. **Verdict — fleet-documented, not stale, not a lane defect.** All three fleet-hosted citations resolve to present, git-tracked, unmodified files whose bytes equal the pre-incident revision (blobs `c0bbf687…`, `363d8ae3…` at fleet HEAD, `origin/master`, remote HEAD `a18d71f4`, and `0619111d`). Locations: `/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md`, `/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md`, `/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/` (directory, 68 entries).

2. **The citation content genuinely supports the lane's claims.** `corpus/README.md:217` ("colocated repos inflate structure counts versus a plain clone") is backed by `JjTrialSouji.md` step 5 (heading at `:53`; measurement prose at `:61`). `corpus/knowledge/jj-colocation-receipts.md:148` ("Lane reports (cited inline by file and line, not S-rows)") is backed by ~25 inline `file:line` references into the two fleet reports that all resolve to the expected passages (§Evidence item 7), plus the lane-side fixture outputs `census/round-17/jj-receipts-{base5fa6017,4f48343}.txt`, which exist in the lane tree at `e78ac7c` (`git ls-tree` confirms both).

3. **Minor precision note (does not affect C1): README:217's second pointer is mechanism-only.** The quoted counts `references.others.count=15` / `objects.commits.count=55` vs 44 appear **only** in `JjTrialSouji.md` — `grep -c "others.count" JjAuditSouji.md` → `0`, and `objects.commits.count` → no hit. `JjAuditSouji.md:118` is: "### F3 — HIGH: `--not --all` and all-ref roots treat `refs/jj/keep` as durable", which supports the *mechanism* of the inflation (keep refs counted as durable by all-ref roots) but not the numbers. The dual citation is substantively defensible; the numeric claim rests on the trial report alone.

4. **Cross-reference nuance worth the L1's attention (no action required by the prereg).** The lane's own knowledge entry partially withdraws that same finding: `corpus/knowledge/jj-colocation-receipts.md:34` reads "JjAuditSouji F3 (:122-128) is withdrawn as evidence." — the withdrawn span is F3's demonstration block, while `corpus/README.md:217` still cites "F3". This is an internal lane cross-reference tension, not fleet staleness, and it is not one of the two C1 findings (it is fleet-classified, never a finding), so C1's mechanism (two `corpus/pointer-exemptions.tsv` rows, no edits to authority files) neither covers nor is blocked by it.

5. **Risk note for the integrator — exemption rows can mask a fleet classification.** Because `:959-961` precedes `:964-983`, a `corpus/pointer-exemptions.tsv` row naming a fleet path (e.g. `.ufo/waves/hyaku/jj-w1/reports/`) is accepted and silently converts that fleet pointer into an "exempt" one with no stale-exemption finding (measured: `ptr_fleet` 3→2, `ptr_exempt` 6→7). C1's two rows are `corpus/`-scoped and were measured to leave `ptr_fleet=3` unchanged, so C1 is sound; but future rounds must not use exemptions to silence fleet-hosted pointers, since that would hide a genuine fleet-tree break.

6. **Fragility note — the fleet tree at these paths was destroyed and restored on 2026-10-25.** Fleet commit `f47ad6ba8d306f8125597401cb2ce45c1297a593` ("repair: restore fleet tree deleted by stray commit 35b91714 (author t <t@t>, 09:21:14 -03)") restored these reports, byte-identically to `0619111d`. The citations are valid now, but a C1 landing receipt must be produced with the frozen invocation including `--fleet-root /home/vgpnk/Projects/shokunin`; without that flag the same tree yields `findings=5` (the three fleet paths become `LG-DANGLING-PTR` alongside the two C1 findings), so the C1 counter's `findings=0` is only meaningful with the flag present. The frozen counter in `.ufo/waves/round-27/preregistration.txt` C1 does include the flag.

## Attack log
- None. This item is a read-only verification of fleet-hosted citations; no predicate, target, counter or case set was proposed for change, and no production file was edited. `corpus/pointer-exemptions.tsv`, `corpus/QUALITY.md`, `corpus/README.md` and `corpus/knowledge/jj-colocation-receipts.md` were read only; the only writes this run were this report and the throwaway scratch tree under `/var/tmp/souji-r27-ScoutC1FleetDebt/` (removed after use).
