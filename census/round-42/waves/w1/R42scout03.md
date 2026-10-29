# R42scout03 — R1 scout: landing-gate dangling-pointer exemptions (R41-D-LG-DANGLING)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin (freeze afe17f416eec04dcf3f480b580a8f928de61d19d, base bf618f6c5c09d302994871c94903abbea2deb60d). Read-only in the lane except the seat files named below. No tools installed (none needed). Scratch /fast/scratch/hyaku/souji-r42/R42scout03 deleted before yield; every command/output below is pasted verbatim from the runs.

## Verdict

The assigned three-row candidate reaches the frozen counter target — `SUMMARY findings=0 deleted=0 rows_added=3 stale=0`, exit 0 — but the pass is **vacuous**: the gate never evaluates (exit 2, `malformed exemption row`) and the r1-counter reads the gate's zeroed SUMMARY without checking the gate's exit status. Under honest evaluation R1 is **unreachable**: the exemption grammar (`POINTER_ROOTS` prefix + safe-path) cannot express the printed `../`-collapsed pointer form, so the two `corpus/README.md:217` findings can never be exempted by any admissible TSV row. Findings for the L1 (frozen instruments, not edited here):

- **r1-counter defect**: `census/round-42/r1-counter.py` greps `^SUMMARY\tfindings=(\d+)` from the gate's stdout and never inspects the gate's exit code or stderr. A could-not-evaluate run (exit 2, zeroed `SUMMARY findings=0 checked_*=0` on stdout, `COULD-NOT-EVALUATE ...` on stderr) scores identically to a clean pass.
- **Gate grammar defect**: `load_pointer_exemptions` (tools/souji-landing-gate.py:1030) rejects any row whose path fails `startswith(POINTER_ROOTS)` or `_safe_pointer_path`; the printed finding paths `../.ufo/waves/hyaku/jj-w1/reports/{JjAuditSouji,JjTrialSouji}.md` fail both (`..` component; no POINTER_ROOTS prefix). `check_pointers` (:1059) matches exemptions by raw equality with the yielded pointer, after normalization has already collapsed `corpus/../../.ufo/...` to `../.ufo/...`, so no loader-admissible string equals them. Only the third finding (`.ufo/waves/hyaku/jj-w1/reports/`, cited by corpus/knowledge/jj-colocation-receipts.md:148) is suppressible.
- **Recommendation**: treat the green candidate as the do-nothing-control class (disqualify or fix the counter's gate-exit check first); the honest R1 state is red, as the prereg allows ("R1 ... not a claim; a red R1 is reported").

## 1. Baseline — both gate modes at the base rev (read-only, lane worktree gate = committed afe17f4; `git status --porcelain` empty)

Command: `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev bf618f6c5c09d302994871c94903abbea2deb60d --round 41`

Without `--fleet-root` (exit 1):

```
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	corpus/README.md:217 cites path absent at bf618f6c5c09
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	corpus/README.md:217 cites path absent at bf618f6c5c09
LG-DANGLING-PTR	.ufo/waves/hyaku/jj-w1/reports/	corpus/knowledge/jj-colocation-receipts.md:148 cites path absent at bf618f6c5c09
SUMMARY	findings=3	checked_reg=107	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=165
```

With `--fleet-root /home/vgpnk/Projects/shokunin` (exit 0):

```
SUMMARY	findings=0	checked_reg=107	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=165
```

## 2. Why the modes disagree

`check_pointers` (tools/souji-landing-gate.py:1059-1157) extracts citation pointers from SKILL/SHONEN/SCORECARD/PROVINCE/corpus sources. For each pointer: in-lane-tree resolution first, then the exemption set, then fleet classification, then the finding. Fleet resolution (:1128-1141) applies only to (a) a pointer starting `../` but not `../../` (fleet path = pointer minus the one `../`), or (b) a pointer starting `.ufo/waves/hyaku/` (fleet path = pointer as-is), and only when `os.path.exists(<fleet_root>/<fleet_path>)` — the fleet side is checked on the live disk of `--fleet-root`, never in the lane tree. The cited corpus/README.md:217 bytes at the base are `` `../../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` `` / `.../JjAuditSouji.md`; `_normalize_pointer_path` (:894) does `normpath("corpus" + "/" + "../../.ufo/...")` = `../.ufo/...` (one dot-dot survives, `_safe_pointer_path` = False, so the guard at :952 keeps it and it prints with `../`). Both files exist fleet-side (`/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md`, `.../JjTrialSouji.md`, confirmed by ls) and are absent from the lane tree at the base, hence: no `--fleet-root` → 3 dangling findings; with it → all three classify fleet-only (`ptr_fleet`), findings=0.

The exemptions row 3 suppression happens BEFORE fleet classification, so `.ufo/waves/hyaku/jj-w1/reports/` would be exempt-suppressed in both modes; the two `../` pointers can never be (see verdict).

## 3. r41 N18 and the disagreement

corpus/lessons/round-41.md:236-237: "**N18 landing gate**: `python3 -B tools/souji-landing-gate.py --round 41` raised `LG-DANGLING-PTR` for the lesson's pointer to an untracked round-40 file and for QUALITY pointers into the ignored `.ufo/waves/round-41/`; the lesson was reworded and the QUALITY pointers repointed to `census/round-41/waves/` (captured at the same commit)."

The disagreement: N18 narrates lane-side defects (untracked/ignored lane paths) fixable by lane edits, and r41 fixed exactly those — but the trio measured here pre-dates r41 (verifier-spotcheck R41-D-LG-DANGLING: "the three LG-DANGLING-PTR findings (corpus/README.md:217, corpus/knowledge/jj-colocation-receipts.md:148) pre-date round 41; repoint or mark them") and is fleet-relative: it disappears only under `--fleet-root`. So whichever r41 run N18 reported from was not the same measurement mode as the closure/spot-check run that saw the trio; N18's text implies the no-fleet-root mode was clean after the lane fixes, which it was not (and is not). This is the "which mode was the measurement" crux named in the r1-counter docstring.

## 4. Candidate (assigned repair) — three appended rows

Candidate file (seat dir): .ufo/waves/round-42/w1/R42scout03/pointer-exemptions-append.tsv = the 4 committed rows of corpus/pointer-exemptions.tsv byte-identical, then exactly:

```
../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	fleet-repo wave report (r40 F1-jj receipts) resolved only under --fleet-root; cited by corpus/README.md:217 and absent from the lane tree (R41-D-LG-DANGLING | round-42)
../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	fleet-repo wave report (r40 F1-jj receipts) resolved only under --fleet-root; cited by corpus/README.md:217 and absent from the lane tree (R41-D-LG-DANGLING | round-42)
.ufo/waves/hyaku/jj-w1/reports/	fleet-repo wave report directory (r40 F1-jj receipts) resolved only under --fleet-root; cited by corpus/knowledge/jj-colocation-receipts.md:148 (R41-D-LG-DANGLING | round-42)
```

Scratch clone experiment (git clone --shared; every git call names -C; toplevel asserted = clone; identity via GIT_AUTHOR_*/GIT_COMMITTER_* env; candidate commit 53c1d20778bd1c21b87cec3ffe6da42b2dea68f9):

- Gate WITHOUT fleet-root and WITH fleet-root — identical output both modes, exit 2:

```
SUMMARY	findings=0	checked_reg=0	checked_changed=0	checked_pins=0	checked_measured=0	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	corpus/pointer-exemptions.tsv:5 malformed exemption row (expected unique path<TAB>reason)
```

  (zeroed SUMMARY on stdout by r18-totality design, emit() :1308-1328; the error line goes to stderr; loader raise is at load_pointer_exemptions, POINTER_ROOTS defined :140-143.)

- r1-counter on the same clone (`python3 -B <clone>/census/round-42/r1-counter.py --root <clone> --rev 53c1d20... --base bf618f6... --scratch <sc>`):

```
SUMMARY findings=0 deleted=0 rows_added=3 stale=0
EXIT=0
```

## 5. Official score (the only supported way)

```
$ TMPDIR=/fast/scratch/hyaku/souji-r42/R42scout03 bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/score-candidate.sh r1 /fast/scratch/hyaku/souji-r42/R42scout03 corpus/pointer-exemptions.tsv=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42scout03/pointer-exemptions-append.tsv
SUMMARY findings=0 deleted=0 rows_added=3 stale=0
SCORE_EXIT=0
```

Final r1-counter SUMMARY: `SUMMARY findings=0 deleted=0 rows_added=3 stale=0`, exit code 0 — **vacuous pass** (gate exit 2; see verdict). The do-nothing control receipt (census/round-42/controls/r1-control.txt) reads `SUMMARY findings=3 deleted=0 rows_added=0 stale=0` rc=1 — an honest red.

## 6. The fleet-root stale question (variant experiment)

A loader-admissible spelling of the two file rows exists only in fleet-resolved form (`.ufo/waves/hyaku/jj-w1/reports/<name>.md`). Scratch clone variant with those two rows + the directory row (commit de382d1ff5fecd86633944a51371f1ab0bad20fe):

- WITHOUT fleet-root: exit 1, `findings=4` — the 2 original LG-DANGLING-PTR (rows do not match the printed `../` form) plus `LG-DANGLING-PTR-EXEMPT-STALE` for both file rows; the directory row IS used (suppresses the third pointer).
- WITH fleet-root: exit 1, `findings=2` —

```
LG-DANGLING-PTR-EXEMPT-STALE	.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	exemption does not suppress an unresolved pointer or dangling measured_commit at de382d1ff5fe
LG-DANGLING-PTR-EXEMPT-STALE	.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	exemption does not suppress an unresolved pointer or dangling measured_commit at de382d1ff5fe
SUMMARY	findings=2	checked_reg=107	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=165
```

So yes: fleet-root mode reports `LG-DANGLING-PTR-EXEMPT-STALE` for rows whose pointers resolve there — staleness is pure set difference (`pointer_exemptions - used_exemptions`, :1269-1275); the reason column never affects matching, so **no reason wording avoids it**. The avoidances are: (a) the N18 remedy — re-word the citations in corpus/README.md:217 and corpus/knowledge/jj-colocation-receipts.md:148 to lane-committed capture paths (the `census/round-N/waves/` convention), so both modes resolve in-tree and no rows are needed; or (b) an instrument change (count fleet-resolving pointers as exemption use, or admit the printed `../` form in the loader) — an L1 finding, not a seat edit.

Report: .ufo/waves/round-42/w1/R42scout03.md
