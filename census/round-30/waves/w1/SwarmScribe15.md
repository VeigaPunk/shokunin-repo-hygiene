# SwarmScribe15 — round-29 carry block for the lesson's seat failure lines

STATUS: PASS

The carry block is drafted, gate-checked in a throwaway clone, and delivered: the base gate at `--round 29` goes from 7 `LG-SEAT-UNCARRIED` to 0 with `carry_heading=1`, and a one-entry deletion control puts exactly the deleted one back. Lane bytes were not modified.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, read-only throughout.

| # | command | output excerpt | rev |
|---|---|---|---|
| E1 | `git -C <lane> rev-parse HEAD`; `git status --porcelain` | `df6afe817d096e4ad71ba2b9cc21a83f126eb658`; one untracked path `?? corpus/lessons/round-30.md` | HEAD |
| E2 | `git -C <lane> diff --stat 9420341d… HEAD -- <the 7 reports> corpus/lessons/round-29.md`; same with `-- tools/souji-landing-gate.py` | both printed nothing — quoted paragraphs byte-identical base..tip, base gate in force | base vs HEAD |
| E3 | `python3 -B tools/souji-landing-gate.py --root <lane> --rev df6afe8… --round 29` | `SUMMARY findings=6 … checked_markers=0 status_lines=0 carry_heading=0 checked_reports=0` then `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-29/ at df6afe817d096e4ad71ba2b9cc21a83f126eb658`, rc 2 | HEAD |
| E4 | scratch: `mktemp -d /fast/scratch/hyaku/souji-r30/SwarmScribe15/r.XXXXXX`, `git clone -q --no-local <lane> "$C"`, `git -C "$C" remote remove origin` | `rev-parse --show-toplevel` printed the scratch root; `remote -v` printed 0 lines; identity set with `git -C "$C" config` only | — |
| E5 | `cp -r "$C/census/round-29/waves" "$C/.ufo/waves/round-29"`; `git -C "$C" add -f .ufo/waves/round-29`; commit; `find … -name '*.md' \| wc -l` | `86` md reports committed under `.ufo/waves/round-29/w1/` | `f9dd108bb25576430c646652ee4ed80d37022d51` |
| E6 | base gate on the capture-only commit | 7× `LG-SEAT-UNCARRIED`, `SUMMARY findings=12 … checked_markers=7 status_lines=69 carry_heading=0 checked_reports=86`, rc 1 | `f9dd108b…` |
| E7 | append block; `git -C "$C" add corpus/lessons/round-29.md`; commit; prefix diff of first 88 lines vs pre-append file | no difference above the block | `170908a094a279a3228051019bc4b60a4e8c2f1f` |
| E8 | base gate on the appending commit | 0 `LG-SEAT-UNCARRIED`, `SUMMARY findings=5 … checked_markers=7 status_lines=69 carry_heading=1 checked_reports=86`, rc 1 | `170908a0…` |
| E9 | delete only the `SwarmCritic51` bullet, commit, base gate, then `reset --hard 170908a0…` | 1 `LG-SEAT-UNCARRIED` for `SwarmCritic51.md` line 7, `SUMMARY findings=6 … carry_heading=1`, rc 1 | `5cf6612a3dbf39a1656a006c7fad4afbb03f5d14` |
| E10 | `git grep -c -iE 'admitted[[:space:]]*:[[:space:]]*true' -- corpus/lessons/round-29.md`; `grep -c 'resolved@' corpus/lessons/round-29.md`; `grep -rn -E 'resolved@[0-9a-f]{7,}' corpus/lessons/round-29.md census/round-29/records/` | `0`, `0`, no lines | HEAD |
| E11 | `grep -n -E '^(FAILURES_HEADING_RE\|CARRY_TOKEN_RE\|WRAP_STRICT_FROM_ROUND\|ELLIPSIS_RE\|def (norm_line\|failures_section_lines\|_continues_paragraph\|status_paragraph\|carry_entries\|carries\|check_carry))' tools/souji-landing-gate.py` | 108, 110, 122, 123, 330, 383, 407, 421, 431, 446, 467 | HEAD |

The 7 reports and their marker lines: `SwarmCritic49` 5, `SwarmCritic51` 7, `SwarmCritic53` 5, `SwarmExecutor17` 3, `SwarmReviewer40` 3, `SwarmReviewer42` 5, `SwarmReviewer43` 5 — all under `census/round-29/waves/w1/`.

## Findings

1. **The C2 red-before reproduces from the lane alone, without any capture copy.** At HEAD the gate's `check_carry` (`tools/souji-landing-gate.py:467-476`) builds `prefix = ".ufo/waves/round-%d/" % round_no` and raises `no .md reports under %s at %s` when nothing matches at the rev, so a round whose capture is committed under `census/round-N/waves/` is never read: E3 shows `checked_markers=0 status_lines=0 carry_heading=0 checked_reports=0` and rc 2. The same read also emits `LG-DANGLING-PTR .ufo/waves/round-29/ corpus/lessons/round-29-verifier-spotcheck.md:132`, i.e. the capture-mapped pointer C2 must stop flagging.
2. **The round-29 lesson had no carry section at all.** `corpus/lessons/round-29.md` is 88 lines with headings at 5 (`## Gate`), 47, 57, 65, 75, 86 (`## Wave`); `FAILURES_HEADING_RE` (line 108) finds none, hence `carry_heading=0` at E3 and E6. Appending a new `## Seat-reported failures` section at EOF is legal because `failures_section_lines` (line 383) re-enters on every matching heading, and E7's prefix diff proves nothing above moved.
3. **Five of the seven failure lines are wrapped paragraphs, so a one-line quote would not carry.** `status_paragraph` (line 421) yields 4 lines for `SwarmCritic49`, 6 for `SwarmCritic53`, 5 for `SwarmExecutor17`, 8 for `SwarmReviewer40` and 8 for `SwarmReviewer43`; `SwarmCritic51` and `SwarmReviewer42` are single lines. Round 29 is above `WRAP_STRICT_FROM_ROUND=18`, so the old first-physical-line match is off; the block therefore quotes each paragraph whole and needs no ellipsis cut.
4. **The carry token has to be supplied by the entry, not by the report.** `CARRY_TOKEN_RE` (line 110) needs `open` or `resolved@<7+hex>`, and none of the seven STATUS paragraphs contains either word. Each bullet therefore carries `open`, which is honest per E10 (no `resolved@` marker names any of the seven) and adds no `LG-OPEN-ADMITTED` finding only because no `admitted: true` exists in the lesson (`ADMITTED_TRUE_RE`, line 111; sweep 0). If the L1 later declares `admitted: true` in that lesson, all seven entries become `LG-OPEN-ADMITTED` — a trap the L1 should know about before touching that line.
5. **The block adds no dangling-pointer finding.** E8's five `LG-DANGLING-PTR` rows are the same five E6 reports minus nothing (`corpus/README.md:217` twice, `corpus/knowledge/jj-colocation-receipts.md:148`, `corpus/QUALITY.md:150` twice), so the four-square difference between E6 (12) and E8 (5) is exactly the seven carried markers; every path the block names (`census/round-29/waves/w1/<Seat>.md`) exists at the rev.
6. **Scratch hygiene.** All work lived under `/fast/scratch/hyaku/souji-r30/SwarmScribe15/` with `TMPDIR` exported there; the clone's `origin` was removed before the first commit; the scratch tree was `rm -rf`'d after the receipts were embedded in the delivery file, so no tree is left on disk.

## Deliveries

- `.ufo/waves/round-30/w1/deliver-r29-carry-block.md` — paste-ready append block, the gate's carry contract with line anchors, and the three raw gate runs (capture-only, appended, deletion control).
