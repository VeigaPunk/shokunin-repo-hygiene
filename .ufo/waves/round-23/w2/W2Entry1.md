# W2Entry1 — falsify `corpus/knowledge/repo-size-census-readonly.md`

Round 23, wave 2 (falsify). Claim under attack: **C3 — F2 read side (coverage)**.
Certification OFF, K5 HELD. Read-only; no credentials, no live `/proc`, no operator-sweep contents.

## Verdict

- **Gate quote block: survives.** All 7 `ADMIT` quotes are verbatim substrings of the
  snapshot each row names and of the installed man page, and every `§` locator on a Gate
  row is the section that actually contains the quote.
- **Artifact as a whole: does not survive unamended.** Three prose statements in the body
  are wrong against the same page bytes (F1, F2, F3); one Gate quote silently drops a
  materially relevant sentence (F4); three provenance/wording items need disclosure (F5–F7).
- **C3's substance is not falsified.** The three-instrument split, the `--lost-found` write
  trap, and the "prune's set ≠ fsck's set" claim all reproduce on the host (see
  § Behavioral corroboration). The defects are provenance/wording, not a wrong instrument.

## Target binding

```
$ sha256sum corpus/knowledge/repo-size-census-readonly.md
06ed503be3210a753da67f521c1029110fab56ce477fc56e775b8c1b62880e41
$ git rev-parse HEAD
102690017115cb202f292828c90b72705f69bf09
$ git log --oneline -- corpus/knowledge/repo-size-census-readonly.md
4765250 round-23: record-agreement and blob-bound-receipt instruments, F2 read-side entries, D1-D7 repairs
$ git status --porcelain
?? census/operator-sweep-20261019/
```

The file was created at `4765250` and has not been touched since; the only worktree delta is
an untracked directory outside this attack.

```
$ sha256sum census/round-23/sources/git-*.txt
4c540915483da5175da373ef697763f61f7959c903a06473dc0920ac89d5c2ee  git-count-objects.1.txt
8ef1170bf5de37e85e96a416ffa5e7f0e12c4e5671e0bab0b1ca357497eaaf32  git-fsck.1.txt
5282b2e11ece7b45df9561df76303712f3daecab496d3a798845331cc02fdd4b  git-prune.1.txt
```

Snapshots are tracked at `4765250` (`git ls-tree --name-only 4765250 census/round-23/sources/`).

## Method

Snapshots are hard-wrapped at 100 columns (and the installed `man` output is additionally
justified and hyphenated), so a raw `grep -F` cannot match a multi-line quote as one string.
I did both:

1. raw `grep -F` on the exact line ranges each quote spans (line numbers below);
2. `tr '\n' ' ' | tr -s '[:space:]' ' '` on snapshot and on `MANWIDTH=400 man … | col -bx`,
   then `grep -F` the whole quote (counts in the table are `1`/`1` for all seven).

Host: `git version 2.56.0`, `pacman -Q git` → `git 2.56.0-1`, `man 2.13.1`.
Man page identity check (whitespace-collapsed diff snapshot vs installed man):

```
git-count-objects: IDENTICAL
git-prune:         IDENTICAL
git-fsck:          only "git-\nrefs(1)" (snapshot hyphenation) vs "git-refs(1)"
```

So the snapshots are the installed 2.56.0 manual pages, byte-for-byte modulo wrapping.

## Quote-by-quote

| # | Artifact line | Quote (short) | Snapshot hit | Man hit | Section named → section that contains it | Verdict |
|---|---|---|---|---|---|---|
| 1 | 78 | `garbage: the number of files…` | `git-count-objects.1.txt:30-31` | yes | § OPTIONS -v/--verbose (line 13 OPTIONS, 14 -v) → same | **survives** |
| 2 | 79 | `alternate: absolute path…one line per path.` | `git-count-objects.1.txt:35-36` | yes | § OPTIONS -v/--verbose → same | **survives**, truncated at a sentence boundary; see F4 |
| 3 | 80 | `Print out objects that exist but that aren’t reachable…` | `git-fsck.1.txt:23` | yes | § OPTIONS --unreachable (22) → same | **survives** |
| 4 | 81 | `Do not consider commits that are referenced only by an entry in a reflog…` | `git-fsck.1.txt:39` | yes | § OPTIONS --no-reflogs (38) → same | **survives** |
| 5 | 82 | `Write dangling objects into .git/lost-found/commit/ or …/other/, depending on type.` | `git-fsck.1.txt:71-72` | yes | § OPTIONS --lost-found (70) → same | **survives**, truncated at a sentence boundary; omission is carried in prose (line 30); see F4 note |
| 6 | 83 | `prunes all unpacked objects unreachable from any of these head objects from the object database` | `git-prune.1.txt:16-18` | yes | § DESCRIPTION (9) → same | **survives** (clause quote; see F9) |
| 7 | 84 | `Do not remove anything; just report what it would remove.` | `git-prune.1.txt:25` | yes | § OPTIONS -n, --dry-run (23-24) → same | **survives** |

No quote is paraphrased: each is an exact substring, including the U+2019 apostrophe in
`aren’t` (quote 3) — `grep -F` matched the literal bytes. Quote lengths: 18, 15, 15, 17, 10,
15, 10 words, all within the ≤25-word Gate rule.

**Truncation details.**

- Quote 2 stops after `one line per path.` The page continues: *"Note that if the path
  contains non-printable characters, it may be surrounded by double-quotes and contain
  C-style backslashed escape sequences."* (`git-count-objects.1.txt:36-37`). The quoted span
  keeps its meaning, but the omitted sentence is the parsing rule for the very field the
  entry says "must be read", and the entry never mentions quoting/escapes
  (`grep -i -E "printable|escape|double-quote"` → no match). Sentence-boundary, not
  mid-sentence, so not a falsification — disclosure required (F4).
- Quote 5 stops after `depending on type.` The page continues: *"If the object is a blob,
  the contents are written into the file, rather than its object name."*
  (`git-fsck.1.txt:72-73`). That sentence is asserted in prose at artifact line 30, so the
  Gate row's truncation does not lose evidence. Accept.

## Section-attribution audit

Gate rows: all seven locators are correct (table above).

Body text: one wrong attribution.

- Artifact line 27: `§ DESCRIPTION fixes the default head set: the index file, all SHA-1
  references in the refs namespace, and all reflogs.` **Wrong section.** `§ DESCRIPTION`
  is `git-fsck.1.txt:12-13` and contains only *"Verifies the connectivity and validity of
  the objects in the database."* The head-set sentence is under `§ OPTIONS`, option
  `<object>`, at `git-fsck.1.txt:15-20`:

  ```
  15:OPTIONS
  16:     <object>
  17:	 An object to treat as the head of an unreachability trace.
  18:
  19:	 If no objects are given, git fsck defaults to using the index file, all SHA-1 references
  20:	 in the refs namespace, and all reflogs (unless --no-reflogs is given) as heads.
  ```

  The lane's own registry already has it right: `corpus/SOURCES.md:136` records
  "§ OPTIONS --unreachable, --dangling/--no-dangling, --no-reflogs, --lost-found, and the
  `<object>` default head set". The entry contradicts its registry row.

- Front matter line 2 (`source: S116 …`) lists the same four options but not the
  `<object>` head-set section, so if the body citation is corrected the source line should
  name it too.

Why this passed the round's gate check: `tools/souji-gate-check.py:42` accepts any locator
token (`§|section|line|paragraph|DESCRIPTION|OPTIONS|COMMANDS|SYNOPSIS|heading`) and
`check4` only tests quote presence in the named snapshot (fail sites at lines 98-112). It never checks
that the named section contains the quote — Gate rows are fine here anyway; the defect is
in body prose, which the tool does not read.

## Findings

Ordered by severity. Each names file:line and the action the round must take.

### F1 — fix — wrong section for the fsck default head set

`corpus/knowledge/repo-size-census-readonly.md:27` says `§ DESCRIPTION`; the sentence is
`§ OPTIONS <object>` (`census/round-23/sources/git-fsck.1.txt:15-20`). Evidence above;
`corpus/SOURCES.md:136` already records the correct section.
**Action:** change the locator to `§ OPTIONS <object>` and add that section to the S116
source line (front matter line 2). No quote changes.

### F2 — fix — "objects" where the page counts files

`corpus/knowledge/repo-size-census-readonly.md:15-16`: "`git count-objects -v` is the size
instrument, and **it reports objects git considers garbage**." The page defines the field as
*"the number of **files** in the object database that are neither valid loose objects nor
valid packs"* (`git-count-objects.1.txt:30-31`). The entry's own NOT-establish bullet
(line 44) says "`garbage` counts **files**, not objects" — the artifact contradicts itself
in the one distinction the entry exists to make precise. Empirical: `git count-objects -v`
prints `garbage: 0` as a file count.
**Action:** reword line 15-16 to "reports files the object database does not recognise as
loose objects or packs" (or "reports a garbage **file** count").

### F3 — fix — "documented as a low-level command" is not in the cited page

`corpus/knowledge/repo-size-census-readonly.md:50`: "`git prune` is documented as a
low-level command, and the page's own note says users should run `git gc`, which calls it."

- `grep -n -i -F "low-level" census/round-23/sources/git-prune.1.txt` → no match (rc=1).
  The word does not occur on the cited page.
- The installed `git(1)` puts `git-prune(1)` under **Ancillary Commands / Manipulators**
  (man git lines 266, 267, 287) and has a separate **LOW-LEVEL COMMANDS (PLUMBING)**
  section at line 402 that does not list prune.

The second clause is supported: `git-prune.1.txt:10-11` (DESCRIPTION Note: "In most cases,
users should run git gc, which calls git prune") and `:49-51` (NOTES).
**Action:** drop "low-level" (or say "listed under Ancillary Commands in `git(1)`"). The
bullet's operative content — do not recommend running prune — is unaffected.

### F4 — disclose — `alternate` quote drops the field's parsing rule

`corpus/knowledge/repo-size-census-readonly.md:79` truncates the sentence after
`one line per path.` and the artifact nowhere records the quoting/escape caveat
(`git-count-objects.1.txt:36-37`). The ≤25-word Gate cap (quote is already 15 words) makes
extending the quote impossible without breaking the gate check.
**Action:** add one prose clause in claim 1 (around line 21-23): a census that reads
`alternate` must unquote paths containing non-printable characters (C-style escapes), per
the same option. Disclose, do not silently accept.

### F5 — disclose — "the two halves that entry names as missing" overstates the sibling

`corpus/knowledge/repo-size-census-readonly.md:66-69` claims
`corpus/knowledge/git-repo-structure-readonly.md` names both halves as missing. Its decision
table names only the unreachable half explicitly (`Need unreachable-object accounting | Use
a separate read-only object census`, line 19); the size half is named as *"obtain
per-artifact receipts and actual filesystem measurements"* (line 18), which is not a
`count-objects` size census with `garbage`/`size-garbage`/`alternate`.
**Action:** reword to "supplies the unreachable half that entry names, and a size half that
its decision table leaves to per-artifact receipts/measurements" — or cite line 18 as the
size half rather than claiming it named this instrument.

### F6 — disclose — lane-link parenthetical can misbind the structure selftest's commit

`corpus/knowledge/repo-size-census-readonly.md:64-66`: "recorded in
`census/round-13/verification.json` (measured_commit `6f8ee0f3…`, `structure-selftest`
exit 0, `artifacts_unchanged_during_run` true)."

All three facts exist, but not at one commit:

```
top-level measured_commit            = 6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6
top-level artifacts_unchanged…       = true
results[3] name=structure-selftest   measured_commit = 6ed10a7cd6c7b26f8068dd6e02497e860f9c4317
                                     exit_code=0 expected=0 matched=true
$ git rev-parse 6ed10a7c^{tree} 6f8ee0f3^{tree}
bf005a68038ac20bc23e4e080ad63b8630c93d57
802811983c12d5af9f7df2c887a75c5b3bcf95a0
```

The selftest row ran at `6ed10a7c` (different tree from `6f8ee0f3`). A reader can take the
parenthetical as binding the selftest to `6f8ee0f3`. In an entry about receipt binding this
matters.
**Action:** cite `6ed10a7c` for the `structure-selftest` row and keep `6f8ee0f3` only as
the file's top-level `measured_commit`. (Selftest itself passes: `selftest=PASS ids=5/5`,
including `write-free … verdict=PASS`.)

### F7 — disclose — "not the set `git gc` would free" is not on the cited page

`corpus/knowledge/repo-size-census-readonly.md:39-40`. `git-prune.1.txt` documents prune's
own scope and the advice to prefer `git gc`; it does not document gc's expiry window. The
lane registry's own scope cell for S117 says the row is "not the grace periods of S002"
(`corpus/SOURCES.md:137`).
**Action:** mark the gc clause as an inference, or cite the gc page/grace-period row. The
fsck-vs-prune clause is independently verified (below).

### F8 — accept with note — head-set bullet omits the refs namespace

`corpus/knowledge/repo-size-census-readonly.md:47`: "default head set depends on the
**index** and the **reflogs**". The page's default set is the index, **all SHA-1 references
in the refs namespace**, and all reflogs (`git-fsck.1.txt:19-20`). The bullet's operative
claim (head set varies per repository/worktree) holds; the enumeration is incomplete.
**Action:** none required for C3; if edited, add "refs namespace" for symmetry with line 27.

### F9 — accept — prune quote is a clause, not a sentence

Line 83 starts at "prunes all …" (source: "and prunes all …") and drops the final period.
It is a self-contained clause; meaning is intact and the locator is right. No action.

### F10 — accept — "unrecognised files" paraphrase

Line 20-21 ("they are unrecognised files") restates the page's definition-by-exclusion
(`git-count-objects.1.txt:30-31`) without quoting it. Consistent with the page. No action.

## `## What this does NOT establish` — bullet by bullet (lines 43-58)

| Bullet | Line | Against the page | Verdict |
|---|---|---|---|
| `garbage` counts **files**, not objects; a file may be a valid loose object, a valid pack, or neither | 44-46 | Page: "number of files … neither valid loose objects nor valid packs" (`git-count-objects.1.txt:30-31`); `size-garbage` is their KiB (33) | **holds** |
| default head set depends on the **index** and the **reflogs** | 47-49 | Page adds the refs namespace (19-20); both named sources do vary per repo | **holds**, enumeration incomplete (F8) |
| `git prune` is documented as a low-level command … page's note says run `git gc`, which calls it | 50-52 | "low-level" absent from `git-prune.1.txt`; `git(1)` files it under Ancillary Commands; the gc note is present (10-11, 49-51) | **falsified in the first clause** (F3); second clause holds |
| no claim of concurrency safety; the `/var/tmp` fixture would have to establish it and is still owed | 53-55 | Pages make no concurrency claim; artifact makes none | **holds** |
| no fleet repository was censused; no `count-objects`/`fsck`/`prune` run reported; no size figure claimed | 56-58 | Artifact contains no run output and no size figure; only the round-13 *structure* probe is cited | **holds** |

## Behavioral corroboration (scratch repos, `/var/tmp/souji-r23-w2-Entry1`)

Not required for quote fidelity; run because the entry's operative claims are about what the
instruments do.

1. **`--lost-found` writes, and for a blob it writes contents.** In a repo with an orphan
   blob `ca3cc1f5…`:

   ```
   $ git fsck --lost-found
   dangling blob ca3cc1f584366763fa504708f21bb04b6f38f6ac
   $ find .git/lost-found -type f
   .git/lost-found/commit/6834692f…
   .git/lost-found/other/ca3cc1f584366763fa504708f21bb04b6f38f6ac
   $ cat .git/lost-found/other/ca3cc1f5…
   orphan-content
   ```

   Confirms claim 3 and the Gate's REJECT line 85, including the blob-contents sentence the
   Gate quote truncates.

2. **prune's set ≠ fsck's unreachable set, and the difference is the packed objects.**
   Repo with an unreachable commit/tree/blob left inside a pack after `repack -ad`,
   `branch -D`, `reflog expire --expire=now --all`:

   ```
   $ git fsck --unreachable
   unreachable blob   61780798228d17af2d34fce4cfbdf35556832472
   unreachable tree   755a580af1fa7c551239bbea46728ed838a673ab
   unreachable commit 9614616c0cf351c404d1e4ba24d364729a31164f
   $ git prune -n
   [no output]
   ```

   Confirms claim 4 and Gate line 83's reason (unpacked-only scope).

3. **Reflog head-set difference is real.** Same repo before packing: `git fsck
   --unreachable` → 1 object; `git fsck --no-reflogs --unreachable` → 4 objects (the
   reflog-only tree/commit/blobs); `git prune -n` → 1 object (prune reads refs, not
   reflogs). Confirms the `--no-reflogs` Gate row and claim 2.

4. **`count-objects -v` field set.** `garbage: 0`, `size-garbage: 0`, `prune-packable: 0`
   present; `alternate` **absent when no alternate exists** (two scratch repos). The page
   says "may appear multiple times", consistent; the entry's "must be read" is sound but a
   reader should know the line can be missing — worth one clause with F4.

## Round-level gaps (not entry falsifications, but they bound this verdict)

- `corpus/README.md:479` says the snapshots were taken "with sha256", but **no digest of the
  round-23 snapshots is recorded anywhere in the lane**: `ls census/round-23/` has only
  `records/` and `sources/`; grepping the three computed digests across `.md/.tsv/.json/.txt`
  finds nothing, and `tools/souji-gate-check.py` checks quote presence only. The Gate binds
  quotes to *paths*, not to committed bytes. Disclose in the round's receipt or add a digest
  record.
- "the three pages opened live this round" (line 4) is not locally verifiable. It does not
  affect quote fidelity: the snapshots are identical to the installed 2.56.0 man pages
  (modulo wrapping/hyphenation), which is the ground truth I matched against.
- `git(1)` classification of `git-prune` was read from the installed man page, not from the
  entry's cited URLs; it is used only to falsify F3's first clause, which the cited page
  cannot support either way.

## Residual risk

- I did not open the git-scm.com web pages (network) — only the committed snapshots and the
  installed man pages. Per `corpus/SOURCES.md:135-137` the web manuals are older
  (2.51.1 / 2.53.0 / 2.43.0) than the installed 2.56.0 pages; if they differ, the Gate's
  `url:` label (web doc) and its `snapshot:` (man page) would drift. The entry's own
  "verified-at" claims both; I could verify only the man-page half.
- F2/F3/F5/F6/F7 are prose defects; none changes the instrument set, the write trap, or the
  set-difference claim, so C3's coverage conclusion stands if they are fixed or disclosed.
- `alternate` behaviour under a real alternate (path quoting, whether counts include
  alternate objects) was **not** exercised — my two scratch repos had no alternates, so
  `alternate` never printed. [INFERENCE] on the parsing caveat's practical impact.

## Scratch

All work under `/var/tmp/souji-r23-w2-Entry1/` (man renders, normalized text, two throwaway
repos) and removed before finishing. No installs, no upgrades, no git/jj mutation of the lane.
