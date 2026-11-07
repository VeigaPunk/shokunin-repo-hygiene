# S76ScoutSources — re-open round-76's new source (S320, git-check-ignore(1) v2.56.0) and test the sentences C1 rests on

Verdict: **sha256 MATCH. Anchor ADMIT (18 words ≤25, offset verified). Doc sentence on `-n` VERIFIED. Source answer: the gate's attribution assumption is CORRECT — and one HIGH finding: the anchor does not ground the rule the gate actually implements.**

## 1. Source fidelity — MATCH
`curl -sSL https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-check-ignore.adoc` →
sha256 `940177c7385eb3cf0ffb1f22ffba35661d16800f8ce787ac676e9a8c89d68208`, 4159 bytes.
Lane `census/round-76/srcs/git-check-ignore.adoc` → **same sha256, same 4159 bytes** (byte-identical).
Also byte-identical to the v2.52.0 tag (`cmp` OK) — consistent with the served banner.
**git-scm.com banner:** "git-check-ignore last updated in 2.52.0"; dropdown "2.53.0 → 2.56.0 no changes";
page sha256 `f567cababcf4332ebf5de05fd882527eee6b5bcf86d605da27fb05ab89fc875d`, 38274 bytes, HTTP 200.
Served HTML renders `<source>` as `&lt;source&gt;` and `pattern's` as U+2019 (`&#8217;`), so the ASCII-quote
is **not** byte-literal in the served page; it is literal in the .adoc capture the lane actually cites. No finding.

## 2. Candidate anchor — ADMIT
Anchor `<source> is the pattern's source file, and <linenum> is the line number of the pattern within that source.`
= **18 words** (whitespace split; ≤25 ✓).
- Whitespace-normalized offset **2355** in `census/round-76/srcs/git-check-ignore.adoc` (= the landed S320 row's "offset 2355 … lines 81-82").
- Raw file: the string is **not** byte-literal (raw lines 81-82 break it: `…and <linenum>` / `is the line number…`); raw tolerant span **bytes 2399–2505**.
- Method check: my `re.sub(r'\s+',' ')` reproduces S318's 3807, S319's 11458, S317's 2497 exactly → the offset convention is the lane's.
- The prereg's shorter fragment `<source> is the pattern's source file` (6 words) IS raw-literal at **2399**.
**HIGH h1 — the anchor does not ground the rule the gate implements.** The doc sentence names the source file of
the deciding pattern; it says nothing about *which* file may decide, nor about repo-relative vs absolute paths.
The gate's rule needs two more sentences the anchor omits:
- `<source> will be an absolute path when referring to the file configured by `core.excludesFile`, or relative to the
  repository root when referring to `.git/info/exclude` or a per-directory exclude file.` — 29 words (>25, cannot
  be one ≤25-word anchor), normalized offset **2555**, raw tolerant span 2601–2802. This is the sentence that licenses
  the gate's `src in tracked` comparison and the `core.excludesFile=/dev/null` attribution-away.
- the ancestor rule (`gitignore(5)`): "Patterns read from a `.gitignore` file in the same directory as the path, or in
  any parent directory …" — 48 words, normalized offset **752** in `census/round-75/srcs/gitignore.adoc` (S318's file).
The landed S320 row's `teaches` cell does cite the source-form sentence ("same page, OUTPUT"), so the *row* is
honest; the **preregistration's** phrasing ("Sourced on S320 … which lets the gate attribute every ignored untracked
path to the file whose pattern decides it") rests on one sentence that carries only part of the rule. The row scope
also says "pattern syntax and exit status not used", yet the gate's `not pat.startswith(b"!")` check depends on the
`!`-prefix preservation sentence (17 words, normalized offset 2462) — in scope by the row's own words, but not in the
anchor. Tag **HIGH** because the prereg names a single source for a rule that needs three sentences across two files.

## 3. `-n/--non-matching` doc sentence — VERIFIED (gate's reliance is sound)
`all fields in each output record except for <pathname> will be empty` — 12 words, normalized offset **3114**
(raw lines 95-96, raw tolerant span 3163-3231). Measured, host git 2.56.0:
`printf 'nope\0' | git check-ignore -v -n -z --stdin` → `^@^@^@nope` (source/linenum/pattern empty, pathname set) —
matches `builtin/check-ignore.c:68` (`printf("%c%c%c%s%c", '\0','\0','\0', path, '\0')`). Non-`-z` form prints `::\t`
(`check-ignore.c:52`). The gate's `-z` parse invariant `len(rec) == 4*len(ign)+1` holds (measured 9 = 4·2+1, tail `b''`).
`core.excludesFile=/dev/null` correctly nulls that source: with it, a core-only path reads unmatched (`::`) and
`ls-files -o -i --exclude-standard` drops it; without it, the same path reports the absolute source path. ✓

## 4. Source answer (file:line) — the gate's assumption is CORRECT
- `builtin/check-ignore.c:112` `last_matching_pattern(dir, index, full_path, &dtype)`; `:119` `output_pattern(...)`.
- `builtin/check-ignore.c:37-56` `output_pattern`: prints `pattern->pl->src` (`:46`), `:srcpos` (`:48`), and the
  `!`/`/` decorations (`:39-40`, so a negated pattern keeps its `!` prefix — verified: `.gitignore:2:!keep.log`).
- `dir.c:1813` `last_matching_pattern` → `:1822` `prep_exclude` → `:1827` `last_matching_pattern_from_lists`;
  `dir.c:1629-1646` scans groups EXC_CMDL→EXC_DIRS→EXC_FILE (dir.h:330-332), deepest-first `for (j = group->nr-1; j >= 0; j--)` (dir.c:1639).
- `dir.c:1731-1746` "Abort if the directory is excluded" — **this is the decisive mechanism**: when the parent
  directory is itself excluded, git does not descend to read the child's `.gitignore`, and the parent's pattern decides.
- `dir.c:1776-1778` builds `pl->src` for a per-directory exclude as `basebuf + exclude_per_dir` → repo-relative, and
  `dir.c:3495-3503` `setup_standard_excludes` adds `core.excludesFile` (absolute) and `.git/info/exclude` (repo-relative).
**Answer to the posed question:** for `dir/file` under a `dir/` pattern the attribution is the **parent's** pattern,
sourced from the **ancestor's** `.gitignore` — exactly as the gate assumes. Measured: root `.gitignore` = `B/`,
`B/inner/.gitignore` = `file.txt` → `git check-ignore -v` reports `.gitignore:1:B/  B/inner/file.txt` (root pattern
wins, deeper file never consulted). Consequence for the gate: the deciding source for a path under an excluded
directory is the ancestor's tracked file, so `f11-committed-dir-rule`/`.jj/` passes as claimed — confirmed live on
the lane: `.gitignore:4:.jj/` decides all 26377 `.jj/**` paths and `.gitignore:5:/.ruff_cache/` decides `.ruff_cache/**`.
The `f7/f9/f10/f14` shapes are the converse: an untracked `.gitignore` that ignores itself is its own deciding source
(`D/.gitignore:1:.gitignore`) → not tracked → undeclared → FAIL, as the population freezes.
Negation: `not pat.startswith(b"!")` is correct — the `!` prefix is preserved in the pattern field, so a `!keep.log`
match is attributed with its source and rejected as undeclared.

## 5. Corpus duplication — NOT a duplicate. Admit.
`grep -c "check-ignore" corpus/SOURCES.md` = **0** before the row landed. The row was appended in the working tree during
this wave (`M corpus/SOURCES.md`, `M corpus/QUALITY.md` Q137, `M corpus/README.md`,
`M corpus/knowledge/filter-filemode-witness.md`, `M SCORECARD.md`, `M SKILL.md`; HEAD was `1a6eaea8`, which has no
S320 row) and committed by the L1 mid-seat in **`5827817c`**; `git show 5827817c:corpus/SOURCES.md` now carries the
S320 row.
No existing souji row carries the git-check-ignore URL or this scope. Nearest neighbours are **S318** (gitignore(5):
which exclude sources are versioned policy) and **S319** (git-ls-files(1): exclude source selection) — different URL,
different scope; S320's scope is the `--verbose`/`-z` record fields and the form of the source field. **Admit.**
Note: `S320` is used for *different* sources in kaidoku-shokunin (open(2)), kengaku-shokunin (Terminal-Bench) and
kotodama-shokunin (Poetic Edda) — sibling lanes number independently (the round-69 sibling-overlap table records
kaidoku's S320 row as an independent scope), so the id is not fleet-unique and is not a conflict.

## Findings
- **HIGH h1** — the preregistration cites one sentence of git-check-ignore(1) as the ground for a rule that also needs
  the source-form sentence (normalized offset 2555, 29 words > the 25-word anchor limit) and gitignore(5)'s ancestor
  rule (normalized offset 752 of `census/round-75/srcs/gitignore.adoc`). The landed S320 row is honest about the first
  of the two; the preregistration's one-sentence framing is not sufficient.
- **MEDIUM m1 (RESOLVED at commit `5827817c`)** — when this seat first read the registry, the S320 row and its
  Q137/knowledge/README edits existed only in the working tree (`M corpus/SOURCES.md`, `M corpus/QUALITY.md` Q137,
  `M corpus/README.md`, `M corpus/knowledge/filter-filemode-witness.md`, `M SCORECARD.md`, `M SKILL.md`; HEAD was
  `1a6eaea8`, which has no S320 row). The L1 committed them mid-seat in `5827817c` ("round-76: integration — S320,
  Q137, knowledge r76, …"); `git show HEAD:corpus/SOURCES.md | grep -c "^| S320 "` = 1. Recorded for the chronology,
  no longer an open defect. The row's "used-by" cites `census/round-76/records/c1-after.txt`, which exists in `113b0072`.
- **LOW l1** — the served git-scm.com page renders the anchor with `&lt;source&gt;` and U+2019, so the anchor is
  byte-literal only in the .adoc capture the row cites (correctly); a re-anchor onto the served HTML would not match.
- **LOW l2** — the gate's `pat.startswith(b"!")` check depends on the `!`-prefix preservation sentence (normalized
  offset 2462), which the row's scope ("pattern syntax … not used") does not obviously cover.
- No disagreement with the frozen predicates; nothing in the C1/C2 claims is falsified by this seat's scope.

## Files I wrote (my seat scope only)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-76/w1/S76ScoutSources.md` (this report)
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-76/w1/S76ScoutSources/` (empty scratch dir)
Scratch (removed before yield): `/fast/scratch/hyaku/souji-r76/S76ScoutSources/` (fixtures `fx*`, fetched
`git-check-ignore.v2.56.0.adoc`, `gitignore.v2.56.0.adoc`, `check-ignore.c`, `dir.c`, `dir.h`, `gscm-check-ignore.html`).
Tooling: none installed (curl/git/python3 already present; git 2.56.0 on PATH) — no pacman/uv/npx action taken.
