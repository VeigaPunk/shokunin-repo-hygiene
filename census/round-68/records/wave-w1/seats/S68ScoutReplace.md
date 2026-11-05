# S68ScoutReplace — replace-ref source check (souji round 68, wave w1)

Scope: verify the git replace-ref facts that round-68 fixture PK6 and the writer's
`GIT_NO_REPLACE_OBJECTS=1` pin depend on. Read-only; deliverables under
`.ufo/waves/round-68/w1/S68ScoutReplace/`.

Full writeup with quotes, offsets and the experiment transcript: `.ufo/waves/round-68/w1/S68ScoutReplace/replace-check.md`.

## Verdicts

| # | Point | Verdict |
|---|-------|---------|
| 1 | git-replace(1) "Replacement references will be used by default by all Git commands except those doing reachability traversal (prune, pack transfer and fsck)." | **SUPPORTED** — exact byte-for-byte incl. newlines, offset 2896 / line 197 of the lane-recipe-stripped text (raw HTML char offsets 28158 / 28225) |
| 1 | git-replace(1) "The GIT_NO_REPLACE_OBJECTS environment variable can be set to achieve the same effect as the --no-replace-objects option." | **SUPPORTED** — exact incl. newlines, offset 3383 / line 207 (raw HTML 29100 / 29172) |
| 2 | Do `git status` / `git ls-files -v` read replaced objects? | `git status`: **SUPPORTED** via the general default-use rule (git-status(1) itself has 0 occurrences of "replace"); observed to change. `git ls-files -v`: **SILENT** in docs; observed **unaffected** (index-driven) |
| 3 | `GIT_NO_REPLACE_OBJECTS` in `census/round-66/sources/git-environment.txt` | **SUPPORTED** — PRESENT, 2 occurrences: char offset 10748 (line 485, `--no-replace-objects` option) and 46183 (line 1413, ENVIRONMENT VARIABLES); `grep -bo` bytes 10850 / 46311; file sha256 `624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035` (matches `absences.tsv:22`, `quotes.tsv:12-13`) |
| 4 | Does `refs/replace/<HEAD>` change `git show <HEAD>:<path>`? | **SUPPORTED — YES.** Forged bytes without the pin, real bytes with `GIT_NO_REPLACE_OBJECTS=1`; `git status --porcelain` flips empty → `M  tools/instr.sh` |

## Commands run (own fetch, not the L1's)

```
curl -sS -w '\nHTTP=%{http_code} BYTES=%{size_download} URL=%{url_effective}\n' -o git-replace.html https://git-scm.com/docs/git-replace
HTTP=200 BYTES=38351 URL=https://git-scm.com/docs/git-replace
70ca75f4baa4bcbb2f5ebdb9fe510036ce54c653ccb044424521f26fbfeedec0  git-replace.html

curl -sS -o git-status.html   https://git-scm.com/docs/git-status    HTTP=200 BYTES=99934  sha256 af1fbb49…
curl -sS -o git-ls-files.html https://git-scm.com/docs/git-ls-files  HTTP=200 BYTES=69017  sha256 39bbbe6a…
curl -sS -o git.html          https://git-scm.com/docs/git           HTTP=200 BYTES=244227 sha256 534c674f…

python3 census/round-66/sources/recipe.py git.html git-recipe.txt
recipe.py: git.html -> git-recipe.txt bytes=58863 sha256=624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035
cmp git-recipe.txt census/round-66/sources/git-environment.txt     # IDENTICAL (lane recipe reproduces the lane capture)
python3 census/round-66/sources/recipe.py git-replace.html git-replace-recipe.txt
recipe.py: git-replace.html -> git-replace-recipe.txt bytes=6975 sha256=96d141fd458c0638ab22647a1f13a37d21c34d6982eb35eabbb5ed42c28f78d4
```

Version headers: `git-replace last updated in 2.55.0` + `2.56.0 no changes`; `git-status last updated in 2.53.0`;
`git-ls-files last updated in 2.55.0`; `git last updated in 2.56.0`. Host git: `git version 2.56.0`.

Fixture (scratch, per the scratch rules; toplevel asserted before the first commit, identity set inside the repo only):
`D=$(mktemp -d -p "$HYAKU_SCRATCH/souji-r68/S68ScoutReplace" replaceexp.XXXXXX)`; `git -C "$D" init -q`;
`git -C "$D" rev-parse --show-toplevel` == `$D` → `TOPLEVEL_OK=…/replaceexp.aGAD14`.
Driver + transcript: `.ufo/waves/round-68/w1/S68ScoutReplace/captures/replace-exp.sh`, `…/captures/replace-exp.out`.

Decisive observed lines:

```
REPLACE_REF_LIST:
39758832864036e855de3363fb2539b68a7f4d5c commit	refs/replace/2b6522c988ea8aa9f8e733cde366754e47eadca0
# A (no pin)
$ git -C "$D" show HEAD:tools/instr.sh          -> FORGED-BYTES
$ git -C "$D" cat-file -p HEAD                   -> tree 771ec71c…  (FORGED tree) / "r68 forged replacement"
$ git -C "$D" status --porcelain                 -> (empty)
# B (pin)
$ GIT_NO_REPLACE_OBJECTS=1 git -C "$D" show HEAD:tools/instr.sh          -> REAL-BYTES-2
$ GIT_NO_REPLACE_OBJECTS=1 git -C "$D" cat-file -p HEAD                   -> tree 12a9c744…  (REAL tree) / "second real tree"
$ GIT_NO_REPLACE_OBJECTS=1 git -C "$D" status --porcelain                 -> M  tools/instr.sh
# C (option)
$ git -C "$D" --no-replace-objects show HEAD:tools/instr.sh               -> REAL-BYTES-2
$ git -C "$D" --no-replace-objects status --porcelain                      -> M  tools/instr.sh
# E (redirect base)
$ GIT_REPLACE_REF_BASE=refs/replace/ GIT_NO_REPLACE_OBJECTS=1 git -C "$D" show HEAD:tools/instr.sh -> REAL-BYTES-2
```

## File:line evidence in the lane

- `tools/souji-receipt-write.py:104` — `env["GIT_NO_REPLACE_OBJECTS"] = "1"` (the pin; candidate blob `f70da577eb1e1624cc63ab8fd0468565927d9b6a`, line 104 of the blob too).
- `tools/souji-receipt-write.py:101` — the `git()` helper scrubs only `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`.
- `tools/souji-receipt-write.py:325` — refuses `GIT_REPLACE_REF_BASE` by name (`RECEIPT-ENV-REDIRECT-SET`).
- `census/round-68/c1-matrix.tsv:40` — `PK6 refuse lane worktree is dirty`; line 41 `PK6h accept -`.
- `census/round-68/c1-counter.py:581-618` — the PK6 fixture: `refs/replace/<head>` → forged commit; forged bytes in index and worktree (mirrors my fixture).
- `census/round-66/sources/absences.tsv:20,22` — `GIT_REPLACE_REF_BASE` ABSENT; `GIT_NO_REPLACE_OBJECTS` PRESENT (2/2) with sha `624e85ef…`.
- `census/round-66/sources/quotes.tsv:12-13` — the ENVIRONMENT VARIABLES quote, offset 46311 / line 1413.

## Findings by severity

- **HIGH** — git(1) live page is byte-identical to the r66 capture (`534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1`), and the lane's own `census/round-66/sources/recipe.py` reproduces `git-environment.txt` byte-for-byte → the r66 git(1) corpus capture is still current, no re-capture needed for r68.
- **HIGH** — the `GIT_NO_REPLACE_OBJECTS=1` pin is confirmed end-to-end against a `refs/replace/<HEAD>` forgery and is confirmed to be the mechanism that makes PK6 discriminate (forgery visible as `M  tools/instr.sh` → "lane worktree is dirty").
- **MEDIUM** — `GIT_REPLACE_REF_BASE` is in neither git(1) nor git-replace(1) (0 occurrences); the writer refuses it by name, so it is not load-bearing — the corpus entry should say so rather than implying doc support.
- **MEDIUM** — git-status(1) and git-ls-files(1) contain zero occurrences of "replace"; any sentence citing doc support for those two commands must cite the general default-use rule in git-replace(1), not those pages.
- **LOW** — `git ls-files -v` / `-s` are index-driven and were unaffected by the replace ref (identical bytes both modes); doc basis for that is silence, not a sentence.
- **LOW** — `git cat-file -p HEAD` is replacement-sensitive exactly like `git show`.

## Files written

- `.ufo/waves/round-68/w1/S68ScoutReplace/replace-check.md`
- `.ufo/waves/round-68/w1/S68ScoutReplace/captures/git-replace.html`
- `.ufo/waves/round-68/w1/S68ScoutReplace/captures/git-replace-recipe.txt`
- `.ufo/waves/round-68/w1/S68ScoutReplace/captures/git-recipe.txt`
- `.ufo/waves/round-68/w1/S68ScoutReplace/captures/replace-exp.sh`
- `.ufo/waves/round-68/w1/S68ScoutReplace/captures/replace-exp.out`
- `.ufo/waves/round-68/w1/S68ScoutReplace.md` (this report)

Scratch `/fast/scratch/hyaku/souji-r68/S68ScoutReplace/` removed at teardown.
No tool was installed or upgraded (nothing needed one; host git 2.56.0 sufficed).
