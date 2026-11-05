# S68ScoutReplace — git replace-ref facts for round-68 PK6 / `GIT_NO_REPLACE_OBJECTS=1` pin

Seat: `S68ScoutReplace` (wave `round-68/w1`). Read-only against the lane. Host git: `git version 2.56.0`.

## Summary of verdicts

| # | Point | Verdict |
|---|-------|---------|
| 1 | git-replace(1): "Replacement references will be used by default by all Git commands except those doing reachability traversal (prune, pack transfer and fsck)." | **SUPPORTED** (exact, with newlines) |
| 1 | git-replace(1): "The GIT_NO_REPLACE_OBJECTS environment variable can be set to achieve the same effect as the --no-replace-objects option." | **SUPPORTED** (exact, with newlines) |
| 2 | Do `git status` / `git ls-files -v` read replaced objects? | **SUPPORTED** for `git status` (via the general default-use rule + observed), **SILENT** in git-status(1)/git-ls-files(1) text; behaviour observed empirically |
| 3 | `GIT_NO_REPLACE_OBJECTS` in lane capture `census/round-66/sources/git-environment.txt` | **SUPPORTED** — PRESENT, 2 occurrences (byte 10748 / 46183; grep -bo bytes 10850 / 46311) |
| 4 | Does `refs/replace/<HEAD>` change what `git show <HEAD>:<path>` returns? | **SUPPORTED** — YES it does, and `GIT_NO_REPLACE_OBJECTS=1` restores the real bytes |
| 5 | Per-point verdict table | see above |

---

## 0. Fetches (own capture, not relying on the L1's read)

```
$ cd /fast/scratch/hyaku/souji-r68/S68ScoutReplace
$ curl -sS -w '\nHTTP=%{http_code} BYTES=%{size_download} URL=%{url_effective}\n' \
      -o git-replace.html https://git-scm.com/docs/git-replace
HTTP=200 BYTES=38351 URL=https://git-scm.com/docs/git-replace
$ sha256sum git-replace.html
70ca75f4baa4bcbb2f5ebdb9fe510036ce54c653ccb044424521f26fbfeedec0  git-replace.html
```

```
$ curl -sS -w "HTTP=%{http_code} BYTES=%{size_download}\n" -o git-status.html https://git-scm.com/docs/git-status
HTTP=200 BYTES=99934
$ sha256sum git-status.html
af1fbb494104a6bcbfb44d65f8d75b2dad850fc9e9b5d43501cc2a6c995f58f6  git-status.html

$ curl -sS -w "HTTP=%{http_code} BYTES=%{size_download}\n" -o git-ls-files.html https://git-scm.com/docs/git-ls-files
HTTP=200 BYTES=69017
$ sha256sum git-ls-files.html
39bbbe6af002214f7ee3075ab4915fc7af05943869a469b89e3393c8cd6f5f08  git-ls-files.html

$ curl -sS -w "HTTP=%{http_code} BYTES=%{size_download}\n" -o git.html https://git-scm.com/docs/git
HTTP=200 BYTES=244227
$ sha256sum git.html
534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1  git.html
```

Version headers observed in the raw HTML:

- `git-replace last updated in 2.55.0` and the note `2.56.0 no changes` (i.e. the git-replace(1) text is unchanged in 2.56.0).
- `git-status last updated in 2.53.0`
- `git-ls-files last updated in 2.55.0`
- `git last updated in 2.56.0`

**Note (HIGH, useful for the corpus entry):** the git(1) HTML I fetched today is byte-identical to the lane's committed r66 capture of the same page:
`git.html` sha256 `534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1` ==
`census/round-66/sources/git-environment.html` sha256 `534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1`.
The r66 capture is therefore still live-current for git(1).

Tag-stripped text was produced with the lane's own frozen recipe
`census/round-66/sources/recipe.py` (so the offsets are directly comparable with the r66 census):

```
$ python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-66/sources/recipe.py \
      git.html git-recipe.txt
recipe.py: git.html -> git-recipe.txt bytes=58863 sha256=624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035
$ cmp git-recipe.txt /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-66/sources/git-environment.txt
   # (no output — IDENTICAL to the lane capture)
$ sha256sum git-recipe.txt
624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035  git-recipe.txt
```

```
$ python3 .../recipe.py git-replace.html git-replace-recipe.txt
recipe.py: git-replace.html -> git-replace-recipe.txt bytes=6975 sha256=96d141fd458c0638ab22647a1f13a37d21c34d6982eb35eabbb5ed42c28f78d4
```

---

## Point 1 — the two sentences, byte-for-byte

Both quotes are present **exactly**, with the original line breaks preserved, in the recipe-stripped
text of https://git-scm.com/docs/git-replace (capture `captures/git-replace-recipe.txt`).
Match kind: **exact, including newlines** — no whitespace normalization was needed.

### Q1 — default use + reachability-traversal exception

Offset **2896** (byte offset in `git-replace-recipe.txt`), line **197**:

```
Replacement references will be used by default by all Git commands
except those doing reachability traversal (prune, pack transfer and
fsck).
```

Python check, exact (with `\n`) — found at 2896, line 197.

### Q2 — GIT_NO_REPLACE_OBJECTS == --no-replace-objects

Offset **3383** (byte offset in `git-replace-recipe.txt`), line **207**:

```
The GIT_NO_REPLACE_OBJECTS environment variable can be set to
achieve the same effect as the --no-replace-objects option.
```

Python check, exact (with `\n`) — found at 3383, line 207.

Raw-HTML offsets (for the un-stripped page), from `git-replace.html`:
- `Replacement references will be used by default by all Git commands` at char offset **28158**
- `except those doing reachability traversal (prune, pack transfer and` at char offset **28225**
- `GIT_NO_REPLACE_OBJECTS</code></span> environment variable can be set to` at char offset **29100**
- `achieve the same effect as the` at char offset **29172**

(The HTML wraps `GIT_NO_REPLACE_OBJECTS` and `--no-replace-objects` in `<code>` spans, hence the
split raw-HTML fragments; the recipe-stripped text is the byte-for-byte citable form.)

**Verdict Q1: SUPPORTED. Verdict Q2: SUPPORTED.**

---

## Point 2 — do `git status` and `git ls-files -v` read replaced objects?

**Docs are SILENT on these two commands by name.** Evidence:

- `git-status.html` / `git-status.txt`: the string `replace` (case-insensitive) occurs **0** times
  in the whole page (`grep -o -i "replace" git-status.html | wc -l` → `0`). No mention of
  `git-replace(1)`, no `--no-replace-objects`, no `GIT_NO_REPLACE_OBJECTS`.
- `git-ls-files.html` / `git-ls-files.txt`: `replace` occurs **0** times as well.
- git-replace(1) itself lists `git status` and `git ls-files` only in the **left-hand navigation
  sidebar** (git-replace.txt lines 336 and 1201), never in prose.

**The sentence that decides it** is the general rule in git-replace(1) (Q1 above):

> "Replacement references will be used by default by all Git commands except those doing
> reachability traversal (prune, pack transfer and fsck)."

`git status` and `git ls-files` are not reachability-traversal commands, so under that rule they
honour replacement refs by default. The git-status(1) DESCRIPTION ("Displays paths that have
differences between the index file and the current HEAD commit…", git-status.txt lines 2266-2268)
makes the mechanism visible: status compares the index against **HEAD**, and HEAD is what a replace
ref rewrites. git-ls-files(1) DESCRIPTION says it "merges the file listing in the index with the
actual working directory list" — index-only, so it is *not* expected to consult HEAD.

**Observed (point 4 experiment, section A vs B below):** `git status --porcelain` DID change with
the replace ref present (empty → `M  tools/instr.sh` once the pin was set), i.e. `git status` reads
the replaced object. `git ls-files -v` printed `H tools/instr.sh` identically in both modes
(`ls-files -v` reports the *index* flag letter, and the index entry was forged in both modes —
`git ls-files -s` printed the same forged blob `3c6e4369…` in both modes). So:

- `git status` — **SUPPORTED** (reads replaced objects; doc basis = the general default-use rule;
  empirically confirmed).
- `git ls-files -v` — **SILENT in the docs**, and **empirically NOT affected** by the replace ref in
  this experiment (index-driven output, identical bytes both ways). No doc sentence decides it.

**LOW finding:** if the corpus entry asserts that `git ls-files -v` reads replaced objects, the
docs do not support it and the observation contradicts it for this command. `git ls-files -s`
(staged blob ids) *is* index content, so it is likewise unaffected.

---

## Point 3 — lane's committed git(1) capture

File: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-66/sources/git-environment.txt`

```
$ sha256sum census/round-66/sources/git-environment.txt
624e85efcf2f2eb773b4b11a91d10963f922efade5e154b0609ec14f523f8035  census/round-66/sources/git-environment.txt
$ wc -c census/round-66/sources/git-environment.txt
58863 census/round-66/sources/git-environment.txt
```

The sha256 matches the anchor recorded in the r66 census:
`census/round-66/sources/absences.tsv:22` →
`GIT_NO_REPLACE_OBJECTS	git-environment	2	2	PRESENT		624e85ef…	534c674f…`
and `census/round-66/sources/quotes.tsv:12-13` (offset 46311, line 1413).

**GIT_NO_REPLACE_OBJECTS DOES appear there — 2 occurrences.**

| Occurrence | Python char offset | `grep -bo` byte offset | Line | Context |
|---|---|---|---|---|
| 1 | 10748 | 10850 | 485 | `--no-replace-objects` option text: "Do not use replacement refs to replace Git objects. This is equivalent to exporting the GIT_NO_REPLACE_OBJECTS environment variable with any value." (offset 10712 = start of "This is equivalent to exporting the GIT_NO_REPLACE_OBJECTS") |
| 2 | 46183 | 46311 | 1413 | ENVIRONMENT VARIABLES section: "GIT_NO_REPLACE_OBJECTS / Setting and exporting this environment variable tells Git to ignore replacement refs and do not replace Git objects." (start of "Setting and exporting…" at 46206) |

Verbatim from the capture (lines 1413-1415):

```
GIT_NO_REPLACE_OBJECTS
Setting and exporting this environment variable tells Git to
ignore replacement refs and do not replace Git objects.
```

**Verdict: SUPPORTED** — the variable is present in git(1)'s ENVIRONMENT VARIABLES section, twice in
the file, and the r66 census already anchors it as PRESENT with the same sha256.

**HIGH finding (cross-check):** the live git(1) page fetched today is byte-identical to the lane's
r66 HTML capture (same sha256 `534c674f…`), and re-running the lane's own recipe.py over it
reproduces `git-environment.txt` byte-for-byte. The r66 git(1) capture is still current; no
re-capture needed for round 68.

**MEDIUM finding:** neither git(1) nor git-replace(1) mentions `GIT_REPLACE_REF_BASE`
(`grep -c "GIT_REPLACE_REF_BASE" git.html` → `0`; `grep -c "GIT_REPLACE_REF_BASE" git-replace.html`
→ `0`). The lane's r66 census already records this
(`census/round-66/sources/absences.tsv:20`: `GIT_REPLACE_REF_BASE … ABSENT`). The writer refuses
`GIT_REPLACE_REF_BASE` **by name** (`tools/souji-receipt-write.py:325`, class
`RECEIPT-ENV-REDIRECT-SET`) rather than relying on the absence of documentation — that is the
defensible posture and is unaffected by this check.

---

## Point 4 — scratch experiment: does `refs/replace/<HEAD>` change `git show <HEAD>:<path>`?

**Answer: YES.** With a `refs/replace/<HEAD>` ref present, `git show HEAD:<path>` returns the
**forged** bytes; with `GIT_NO_REPLACE_OBJECTS=1` it returns the **real** bytes. `git status
--porcelain` likewise flips from clean to `M  tools/instr.sh`.

Driver script: `captures/replace-exp.sh`; full transcript: `captures/replace-exp.out`.
Fixture root (scratch, under `$HYAKU_SCRATCH/souji-r68/S68ScoutReplace/`), removed at teardown.

### Commands (exact)

```
D=$(mktemp -d -p "$HYAKU_SCRATCH/souji-r68/S68ScoutReplace" replaceexp.XXXXXX)
git -C "$D" init -q
git -C "$D" rev-parse --show-toplevel      # asserted == $D before the first commit
git -C "$D" config user.name "S68 Scratch Fixture"; git -C "$D" config user.email "s68-scratch@invalid"
# commit 1 (real tree) and commit 2 (second real tree), then:
printf 'FORGED-BYTES\n' > forged-instr.sh
BLOB=$(git -C "$D" hash-object -w forged-instr.sh)
GIT_INDEX_FILE=$IDX git -C "$D" read-tree "$HEAD"
GIT_INDEX_FILE=$IDX git -C "$D" update-index --add --cacheinfo "100755,$BLOB,tools/instr.sh"
TREE=$(GIT_INDEX_FILE=$IDX git -C "$D" write-tree)
REP=$(git -C "$D" commit-tree "$TREE" -p "$HEAD" -m "r68 forged replacement")
git -C "$D" update-ref "refs/replace/$HEAD" "$REP"
# worktree + real index carry the forged bytes (mirrors the counter's PK6 fixture, c1-counter.py:581-618)
```

Then the A/B/C/D comparison below. Git identity was set **inside the fixture repo only**
(`git -C "$D" config user.name/user.email`); the fixture's `rev-parse --show-toplevel` was asserted
to equal `$D` before the first commit (`TOPLEVEL_OK=` line in the transcript).

### Observed output (decisive lines)

Fixture identity (from `captures/replace-exp.out`):

```
FIXTURE_DIR=/fast/scratch/hyaku/souji-r68/S68ScoutReplace/replaceexp.aGAD14
TOPLEVEL_OK=/fast/scratch/hyaku/souji-r68/S68ScoutReplace/replaceexp.aGAD14
HEAD1=86cf95020c9fd5be9fd8da34b154da653da8ae5d
HEAD=2b6522c988ea8aa9f8e733cde366754e47eadca0
FORGED_BLOB=3c6e4369507a3e43631c6233de46ba22c12adebb
REPLACEMENT_COMMIT=39758832864036e855de3363fb2539b68a7f4d5c
REPLACE_REF_LIST:
39758832864036e855de3363fb2539b68a7f4d5c commit	refs/replace/2b6522c988ea8aa9f8e733cde366754e47eadca0
```

**A — replacement-honouring (no `GIT_NO_REPLACE_OBJECTS`):**

```
$ git -C "$D" show HEAD:tools/instr.sh
FORGED-BYTES
rc=0
$ git -C "$D" cat-file -p HEAD
tree 771ec71ca989cc236bce3c35c69ced1e3136ccfc        <-- the FORGED tree
parent 2b6522c988ea8aa9f8e733cde366754e47eadca0
author R68 Fixture <r68-fixture@invalid> 1793836800 +0000
committer R68 Fixture <r68-fixture@invalid> 1793836800 +0000

r68 forged replacement
rc=0
$ git -C "$D" status --porcelain
                       <-- EMPTY: the forged index+worktree look clean against the replaced HEAD
rc=0
$ git -C "$D" ls-files -v
H tools/instr.sh
rc=0
$ git -C "$D" rev-parse HEAD
2b6522c988ea8aa9f8e733cde366754e47eadca0
$ git -C "$D" show --stat --oneline HEAD
2b6522c r68 forged replacement
```

**B — `GIT_NO_REPLACE_OBJECTS=1`:**

```
$ GIT_NO_REPLACE_OBJECTS=1 git -C "$D" show HEAD:tools/instr.sh
REAL-BYTES-2
rc=0
$ GIT_NO_REPLACE_OBJECTS=1 git -C "$D" cat-file -p HEAD
tree 12a9c744c5cb151b011cfa3f1ce911518aa452eb        <-- the REAL tree
parent 86cf95020c9fd5be9fd8da34b154da653da8ae5d
author S68 Scratch Fixture <s68-scratch@invalid> 1793901479 -0300
committer S68 Scratch Fixture <s68-scratch@invalid> 1793901479 -0300

second real tree
rc=0
$ GIT_NO_REPLACE_OBJECTS=1 git -C "$D" status --porcelain
M  tools/instr.sh                                     <-- the forgery is now VISIBLE as dirty
rc=0
$ GIT_NO_REPLACE_OBJECTS=1 git -C "$D" ls-files -v
H tools/instr.sh
rc=0
```

**C — the `--no-replace-objects` option (doc cross-check, same effect):**

```
$ git -C "$D" --no-replace-objects show HEAD:tools/instr.sh
REAL-BYTES-2
$ git -C "$D" --no-replace-objects status --porcelain
M  tools/instr.sh
```

**D — a non-replaced commit is unaffected (the replace ref targets one object only):**

```
$ git -C "$D" show "$HEAD1:tools/instr.sh"             -> REAL-BYTES
$ GIT_NO_REPLACE_OBJECTS=1 git -C "$D" show "$HEAD1:tools/instr.sh" -> REAL-BYTES
```

**E — `GIT_REPLACE_REF_BASE` interaction (the redirect namespace):**

```
$ GIT_REPLACE_REF_BASE=refs/replace/ git -C "$D" show HEAD:tools/instr.sh
FORGED-BYTES
$ GIT_REPLACE_REF_BASE=refs/replace/ GIT_NO_REPLACE_OBJECTS=1 git -C "$D" show HEAD:tools/instr.sh
REAL-BYTES-2
$ GIT_REPLACE_REF_BASE=refs/replace/ GIT_NO_REPLACE_OBJECTS=1 git -C "$D" status --porcelain
M  tools/instr.sh
$ git -C "$D" ls-files -s        -> 100755 3c6e4369507a3e43631c6233de46ba22c12adebb 0	tools/instr.sh
$ GIT_NO_REPLACE_OBJECTS=1 git -C "$D" ls-files -s -> 100755 3c6e4369507a3e43631c6233de46ba22c12adebb 0	tools/instr.sh
```

### What this means for the round-68 pins

1. The writer's `GIT_NO_REPLACE_OBJECTS=1` pin (`tools/souji-receipt-write.py:104`, candidate blob
   `f70da577eb1e1624cc63ab8fd0468565927d9b6a`) is **exactly the right pin** for this threat: with it
   set, `git show HEAD:<path>` returns the real object and `git status --porcelain` surfaces the
   forged bytes as `M  tools/instr.sh` — the "lane worktree is dirty" refusal the counter's PK6 row
   (`census/round-68/c1-matrix.tsv:40`, `PK6 refuse lane worktree is dirty`) expects.
2. **HIGH — a real gap in the pin's coverage (E above):** `GIT_REPLACE_REF_BASE` is *not* scrubbed by
   the writer's `git()` helper. The helper scrubs only `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`
   (`tools/souji-receipt-write.py:101`) and then *sets* `GIT_NO_REPLACE_OBJECTS=1` (line 104).
   Setting the variable is a global kill-switch, so a caller-provided `GIT_REPLACE_REF_BASE` cannot
   re-enable replacement — my experiment E confirms the pin wins even when
   `GIT_REPLACE_REF_BASE=refs/replace/` is exported. The writer additionally refuses
   `GIT_REPLACE_REF_BASE` by name at line 325 (`RECEIPT-ENV-REDIRECT-SET`) before it is ever used.
   **The pin is not defeatable by `GIT_REPLACE_REF_BASE`.** No gap; recorded here so the corpus
   entry states it correctly rather than implying the scrub covers it.
3. **MEDIUM — the pin does not defend `ls-files` (observed, and consistent with the docs):** the
   writer reads the index flags with `git ls-files -v` (line 34 of the writer's docstring) and the
   worktree state with `git status --porcelain`. The *index* is never rewritten by a replace ref
   (`ls-files -s` printed the same blob id in both modes), so `ls-files -v` needs no replacement
   defence; the forgery surfaces through `status`, which the pin does cover. This is the correct
   division of labour and it is what makes PK6 discriminate.
4. **LOW — `git cat-file -p HEAD` is affected too:** without the pin it printed the *replacement*
   commit's tree line and message (`r68 forged replacement`), with the pin the real ones. Any writer
   path that reads objects by id is covered by the same pin.

---

## Files written by this seat

Under `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-68/w1/S68ScoutReplace/`:

- `replace-check.md` — this file.
- `captures/git-replace.html` — raw fetch of https://git-scm.com/docs/git-replace (sha256 `70ca75f4…`).
- `captures/git-replace-recipe.txt` — lane-recipe-stripped text of the above (sha256 `96d141fd…`).
- `captures/git-recipe.txt` — lane-recipe-stripped text of https://git-scm.com/docs/git (sha256 `624e85ef…`, byte-identical to the r66 capture).
- `captures/replace-exp.sh` — the scratch fixture driver (exact commands).
- `captures/replace-exp.out` — the full experiment transcript.

Scratch dir `/fast/scratch/hyaku/souji-r68/S68ScoutReplace/` (fixture repo + raw html) was removed at teardown.

## Findings by severity

- **HIGH** — git(1) live page is byte-identical to the r66 capture (sha256 `534c674f…`); re-running
  the lane's `census/round-66/sources/recipe.py` reproduces `git-environment.txt` byte-for-byte. The
  r66 git(1) corpus capture is still current — no re-capture needed. Evidence: Point 0 / Point 3.
- **HIGH** — the writer's `GIT_NO_REPLACE_OBJECTS=1` pin is confirmed to defeat a
  `refs/replace/<HEAD>` forgery end-to-end (experiment B/C/E) and is confirmed to be the mechanism
  that makes the counter's PK6 row discriminate. Evidence: Point 4.
- **MEDIUM** — neither git(1) nor git-replace(1) documents `GIT_REPLACE_REF_BASE`; the lane already
  records ABSENT (`absences.tsv:20`). The writer refuses it by name, so the fact is not load-bearing.
- **MEDIUM** — git-status(1) and git-ls-files(1) contain **zero** occurrences of "replace"; any corpus
  or registry sentence claiming doc support for those two commands must cite the general
  default-use rule in git-replace(1), not those pages.
- **LOW** — `git ls-files -v` / `git ls-files -s` are index-driven and were **not** affected by the
  replace ref in the experiment; the doc basis for that is silence, not a sentence.
- **LOW** — `git cat-file -p HEAD` is replacement-sensitive, exactly like `git show`.
