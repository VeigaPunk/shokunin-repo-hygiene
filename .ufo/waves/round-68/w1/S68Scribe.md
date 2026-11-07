# S68Scribe — round-68 corpus knowledge entry and SOURCES registry row

Seat: scribe (prose drafting only; no code, no counter run, no writer byte touched).
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Round 68, wave 1.

## Verdict per item

| item | verdict | evidence |
|---|---|---|
| 1. knowledge-replace-ref-receipt-writer.md (corpus entry for the replace-ref route) | PASS | file written; 36 lines (< 90); opens with the provenance trio in the required order `source:` / `verified-at:` / `recheck:`; both body quotes are the sentences the L1 located (corpus/lessons/round-68.md `## Gate`, S301) and no other doc sentence is quoted; every claim cites S301, S298 or a committed path |
| 2. registry-row-S301.md (one 11-column SOURCES row) | PASS | exactly one table row; 11 cells; 12 `|` characters; 0 escaped pipes; anchor names the page and its version header |
| 3. row pipe check | PASS | `grep -o '\|' registry-row-S301.md \| wc -l` → **12**; `awk -F'\|' '{print NF-2}'` → **11** cells |

## Files written (both under my seat dir)

- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-68/w1/S68Scribe/knowledge-replace-ref-receipt-writer.md
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-68/w1/S68Scribe/registry-row-S301.md
- this report: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-68/w1/S68Scribe.md

## Exact commands run

```
bash /home/vgpnk/Projects/shokunin/scripts/hyaku/disk-guard.sh status          # before and after; EXIT=0, /fast/scratch/hyaku 50% used, 404.0G free
cd "$HYAKU_SCRATCH/souji-r68/S68Scribe"                                        # HYAKU_SCRATCH=/fast/scratch/hyaku
curl -sSL -w "HTTP=%{http_code} BYTES=%{size_download} URL=%{url_effective}\n" -o s301-git-replace.html https://git-scm.com/docs/git-replace
sha256sum s301-git-replace.html ; wc -c s301-git-replace.html
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-66/sources/recipe.py s301-git-replace.html mine-recipe.txt
sha256sum mine-recipe.txt                                  # vs the scout's copies/git-replace-recipe.txt
grep -bo "Replacement references will be used by default" mine-recipe.txt
grep -bo "The GIT_NO_REPLACE_OBJECTS environment variable" mine-recipe.txt
python3 -c "... find both quotes in census/round-66/sources/git-environment.txt ..."
awk -F'|' '{print NF-2}' .ufo/waves/round-68/w1/S68Scribe/registry-row-S301.md
grep -o '|' .ufo/waves/round-68/w1/S68Scribe/registry-row-S301.md | wc -l
```

## Observed output lines that decide the verdicts

```
HTTP=200 BYTES=38351 URL=https://git-scm.com/docs/git-replace
70ca75f4baa4bcbb2f5ebdb9fe510036ce54c653ccb044424521f26fbfeedec0  s301-git-replace.html
recipe.py: s301-git-replace.html -> mine-recipe.txt bytes=6975 sha256=96d141fd458c0638ab22647a1f13a37d21c34d6982eb35eabbb5ed42c28f78d4
96d141fd458c0638ab22647a1f13a37d21c34d6982eb35eabbb5ed42c28f78d4  mine-recipe.txt
96d141fd458c0638ab22647a1f13a37d21c34d6982eb35eabbb5ed42c28f78d4  scout-recipe.txt      # byte-identical to the scout seat's capture
2953:Replacement references will be used by default
3440:The GIT_NO_REPLACE_OBJECTS environment variable
11	git-environment	GIT_NO_REPLACE_OBJECTS	46311	624e85ef…	…	200	1413	GIT_NO_REPLACE_OBJECTS	46311	GIT_NO_REPLACE_OBJECTS\nSetting and exporting this environment variable tells Git to\nignore replacement refs and do not replace Git objects.
12:git-environment	Setting and exporting this environment variable tells Git to	46334	…
pipes: 12
cells: 11
escaped pipes: 0
```

Header check on my own fetch of the S301 page: `git-replace last updated in 2.55.0`, and the version list carries `2.56.0 no changes` — identical to what the L1 recorded in corpus/lessons/round-68.md `## Gate` and to what the scout seat reported.

## file:line evidence cited in the entry

- tools/souji-receipt-write.py:97-106 — the single `git()` helper; `env["GIT_NO_REPLACE_OBJECTS"] = "1"` at line 104. Read call sites: 119, 158, 304, 347, 372, 381, 393, 414, 433, 494, 495.
- tools/souji-receipt-write.py:325 — `RECEIPT-ENV-REDIRECT-SET` refusal naming `GIT_REPLACE_REF_BASE`.
- census/round-68/c1-matrix.tsv:40-41 — PK6 `refuse` / `lane worktree is dirty`; PK6h `accept` / `-`.
- census/round-68/c1-counter.py:32-37 (counter header on PK6), :75-76 (row E6), :322-323 (case registration), :581-628 (fixture build), :616 (`update-ref refs/replace/<head>`), :710-712 (no caller env for the route).
- census/round-68/mutate-writer.py:28-29 — mutant K6 "remove git() GIT_NO_REPLACE_OBJECTS=1 pin".
- census/round-68/battery/SHA256SUMS — K6 digest 698fedc2143cecdbd15a36e59da749ec598be344d020cd81930189afe08713b7.
- census/round-66/sources/git-environment.txt — committed S298 capture, sha256 624e85ef…8035; GIT_NO_REPLACE_OBJECTS quote at byte offset 46334 (grep -bo 46311 for the variable name).
- census/round-66/sources/quotes.tsv:12-13 — the S298 located-quote rows.
- census/round-66/sources/absences.tsv:20 — GIT_REPLACE_REF_BASE ABSENT from git(1)/git-config(1); :22 — GIT_NO_REPLACE_OBJECTS PRESENT 2/2.
- census/round-68/preregistration.txt — the C1 Target block quoted in the entry's `recheck:`.
- corpus/SOURCES.md row S298 — the S298 registry row.

## Findings

- **LOW — the entry's `recheck:` points at an uncommitted path.** `.ufo/waves/round-68/w1/S68ScoutReplace/replace-check.md` is under the gitignored wave tree, and QUALITY Q31 resolves repo-relative path tokens under `.ufo/waves/` against the landing revision. The entry therefore states the mirror obligation (round 67 mirrored `.ufo/waves/round-67/w1/` to `census/round-67/wave/w1/`); the L1 must either mirror the scout's `captures/` and `replace-check.md` into a committed path such as `census/round-68/wave/w1/S68ScoutReplace/` and re-point the citation, or drop the path and cite the L1's own Gate record in corpus/lessons/round-68.md. Not mine to land.
- **LOW — the two located quotes appear twice in the entry and in the registry row, with the git-replace(1) backtick-free rendering.** The page's HTML wraps `GIT_NO_REPLACE_OBJECTS` and `--no-replace-objects` in `<code>` spans, so the byte-for-byte sentence only matches the tag-stripped text; the entry and the row quote it without backticks and name the tag-stripped offsets (text 2896 / 3383, byte 2953 / 3440 in the 6975-byte recipe output). The reviewer seat should read that as the page text, not as the r68-lesson Gate's backticked rendering.
- **LOW — `GIT_REPLACE_REF_BASE` has no documentation basis.** Recorded by the scout (0 occurrences in git(1) and git-replace(1)) and by the lane's own census (census/round-66/sources/absences.tsv:20). The entry names this explicitly so no reader infers a doc basis for the writer's `RECEIPT-ENV-REDIRECT-SET` refusal of that name.
- **INFO — no source claim was made by me for `git status` or `git ls-files -v`.** git-status(1) and git-ls-files(1) contain no occurrence of "replace" (scout), so the entry states the general default and the switch, and explicitly declines per-command claims. The scout's scratch fixture observed `git status --porcelain` flipping to `M  tools/instr.sh` under a replace ref while `git ls-files -v`/`-s` were unaffected; that observation belongs to the scout's report and is not restated as a documented fact here.

## Gates

- No writer byte changed: `git status --porcelain` in the lane shows only the untracked `corpus/lessons/round-68.md` (written by the L1 before my seat ran); my seat wrote nothing under census/, tools/, corpus/, or any tracked lane file.
- No mutating git/jj command was run in the lane or the fleet repo; all git calls were read-only (`log`, `status`, `show`, `rev-parse`, `cat-file`).
- No fixture repository was needed for this seat (prose drafting only); the one scratch repo experiment belongs to the scout seat.
- Scratch discipline: all scratch under /fast/scratch/hyaku/souji-r68/S68Scribe/, removed before yield; nothing under /tmp, /var/tmp or TMPDIR was used or cited.
- Tooling: no install or upgrade was needed or performed this seat (curl, python3, git and the lane's own `census/round-66/sources/recipe.py` were already present), so there is no tool/version/channel entry for the report.

## Out of scope

- No counter or battery run (the L1 and the executor seats own the C1/C2 arms); the `recheck:` command in the entry is transcribed from census/round-68/preregistration.txt, not executed here.
- No edit to corpus/SOURCES.md, corpus/knowledge/, corpus/lessons/round-68.md, or any census/round-68/ file — all read-only for this seat.
- The corpus landing path (`corpus/knowledge/replace-ref-receipt-writer.md`, named in the row's used-by cell) is the L1's to create; this seat delivers the draft under its own seat dir only.
