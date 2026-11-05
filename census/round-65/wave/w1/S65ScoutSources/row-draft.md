# S297 registry row — draft (scout seat S65ScoutSources, round 65)

> **NOT appended to `corpus/SOURCES.md`.** The L1 owns the registry. The lane registry was read
> read-only for id state; the row shape below was validated against a **scratch copy** of the
> registry in the seat's scratch root (deleted with the scratch root on exit). No capture was
> written to `census/` — the L1 owns that copy too.

## Id state (read read-only from the lane registry at the tip)

- `corpus/SOURCES.md` at tip `16da2445088ccca15aa32c66841d878ee57a8706` contains **219 rows**.
- Highest id present: **S296**. `S293` is a hole (drafted in round 63, ruled out of integration);
  `S295`/`S296` were drafted in round 64 and landed.
- **Next free id: S297.**
- Verified: `grep -oE '^\| S[0-9]{3} ' corpus/SOURCES.md | sort | uniq -d` → no duplicate ids.
- Verified: `awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13'` → no output
  (every existing row is a well-formed 11-content-cell row).

## The row

The registry's column order is
`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`
(11 content cells; `awk -F'|'` therefore sees NF=13 including the leading and trailing empty
fields). The row below has **no `|` character inside any cell**.

```markdown
| S297 | git-config(1) § status.showUntrackedFiles — https://git-scm.com/docs/git-config | docs | A | the writer's untracked-visibility refusal (receipt hygiene, C1 V1/V2 rows) | § status.showUntrackedFiles, accessed 2026-11-05; HTTP 200; 830605 bytes; sha256 37aa8407…9226; capture census/round-65/sources/s297-git-config.html; tag-stripped text census/round-65/sources/s297-git-config.txt; located quote census/round-65/sources/s297-located-quote.txt | `So, this variable controls how the commands display the untracked files.` (11 words) — the page's own words, located at byte offset 299266 of the tag-stripped text capture with `assert text[299266:299338] == quote_bytes` PASSED; the three documented values are `no` (show no untracked files), `normal` (show untracked files and directories) and `all` (show also individual files in untracked directories), and the default is `normal`; the page does not say that a tool must override the variable, and it says nothing about the precedence of `-c` or of `GIT_CONFIG_COUNT` | queued | 2026-11-05 | 180d | corpus/knowledge/untracked-visibility-concealment.md |
```

Cell-by-cell:

| column | value |
|---|---|
| id | `S297` |
| source | `git-config(1) § status.showUntrackedFiles` — `https://git-scm.com/docs/git-config` |
| kind | `docs` |
| tier | `A` |
| scope | `the writer's untracked-visibility refusal (receipt hygiene, C1 V1/V2 rows)` |
| anchor | `§ status.showUntrackedFiles, accessed 2026-11-05; HTTP 200; 830605 bytes; sha256 37aa8407…9226; capture census/round-65/sources/s297-git-config.html; tag-stripped text census/round-65/sources/s297-git-config.txt; located quote census/round-65/sources/s297-located-quote.txt` |
| teaches | `` `So, this variable controls how the commands display the untracked files.` (11 words) `` + the three documented values + the default + the two named limits |
| status | `queued` |
| opened | `2026-11-05` |
| recheck | `180d` |
| used-by | `corpus/knowledge/untracked-visibility-concealment.md` |

## Quote-cell compliance (checked mechanically)

| item | value | limit | carrier | mechanical proof |
|---|---|---|---|---|
| primary quote | `So, this variable controls how the commands display the untracked files.` | 11 words | `s297-git-config.txt` offset 299266 | `assert text[299266:299338] == quote_bytes` → **PASSED** |
| same sentence, raw HTML | first-word offset 762393 (line 14685) | — | `s297-git-config.html` | NOT byte-contiguous in the raw HTML (`find` = −1): the page wraps the sentence across one source newline; a whitespace-flexible collapse of the HTML window at that offset does contain the quote → `True` |
| S1 | `normal - Show untracked files and directories.` | 7 words | text 299390 / man 330827 | both slice assertions **PASSED** |
| S2 | `all - Show also individual files in untracked directories.` | 9 words | text 299437 / man 330890 | both slice assertions **PASSED** |
| S3 | `no - Show no untracked files.` | 6 words | text 299360 / man 330781 | both slice assertions **PASSED** |

Every quote is ≤ 25 words, contains no `|` character, and is the page's own words (no paraphrase).
The full offset table with the raw-HTML anchors is in `s297-located-quote.txt`, which is regenerated
by `s297-make-located-quote.py` so the offsets are re-run assertions rather than recorded numbers.

**One line, one recipe.** The text capture is produced by `s297-tagstrip.py`, delivered beside it:

```
python3 s297-tagstrip.py s297-git-config.html s297-git-config.txt
```

## Shape validation actually run (on a scratch copy of the registry, never on the lane)

```
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {print NR": "NF}'  -> (no output)   EXIT 0
duplicate ids                                                                            -> (no output)   EXIT 0
kind enum (book|code|community|docs|own-work|paper|spec)                               -> (no output)   EXIT 0
tier enum (A|B|C)                                                                       -> (no output)   EXIT 0
status enum (mined|queued|rejected)                                                    -> (no output)   EXIT 0
'|' inside any cell of the new row                                                      -> (no output)   EXIT 0
new row: 11 content cells, NF=13                                                       -> PASSED
tier histogram before: A=209 B=7 C=3 (219 rows)   after: A=210 B=7 C=3 (220 rows)      -> PASSED
```

## Integration facts the L1 must handle

1. **The `used-by` path does not exist yet.** `corpus/knowledge/untracked-visibility-concealment.md`
   is **absent at the tip** (verified in `used-by-checks.txt`). The K1 check
   (`tools/souji-registry-agreement.py`) requires every `used-by` path to exist at the measured
   revision **and** to name the row id. Until the scribe seat (S65ScribeEntry) lands that entry
   **and** it cites `S297`, K1 reports `K1 used-by-missing` / `K1 used-by-no-cite` for this row.
   Round 63 and round 64 hit the same ordering; the same applies here. **The row and the knowledge
   entry must land together.**
2. **The captures are not in `census/` yet.** The L1 must copy these four files into
   `census/round-65/sources/` under the names the anchor cell names:
   `s297-git-config.html`, `s297-git-config.txt`, `s297-located-quote.txt`. A third independent
   carrier is available and optional: `s297-git-config.man.txt` (the rendered man page, package
   `git 2.56.0-1`).
3. **A duplicate-url warning is expected, not a finding.** `https://git-scm.com/docs/git-config`
   is already carried by **S042** (generic config-value effects), **S057**
   (`status.showUntrackedFiles` — the `-u/--untracked-files` override) and **S238**
   (`GIT_CONFIG_COUNT`). S297 is under a **distinct scope** from all three: S297 is the
   *untracked-visibility refusal* scope (which values exist and what they display), while S057 is
   the *command-line override* scope and S238 is the *environment-injection* scope. The census
   reports W04 for this, exactly as it did for S251/S239/S244 and for S291/S295/S296.
4. **S057 is the closest neighbour.** S057's scope says "not which value the census should use";
   S297 is exactly the row that says which values exist and what each displays, which is the
   complement S057's scope cell points at. The lesson should say so.
5. **`status=queued`, `recheck=180d`.** Both are existing registry enum values (14 rows carry
   `queued`, 15 carry `180d`). The row is left `queued` rather than `mined` because the knowledge
   entry that would mine it does not exist yet; the L1 may flip it to `mined` in the same landing
   that creates the entry.

## Named limits of this source

**What the page documents (and therefore what the row can teach).**

- The variable `status.showUntrackedFiles` exists and **controls how the commands display the
  untracked files** (the primary quote).
- Its three documented values: `no` — show no untracked files; `normal` — show untracked files and
  directories; `all` — show also individual files in untracked directories.
- The default when the variable is not specified is `normal`; the boolean spellings `true`/`false`
  are taken as `normal`/`no`.
- The variable **can be overridden by the `-u|--untracked-files` option** of `git-status` and
  `git-commit`.
- With `normal` (the default), a directory containing only untracked files is shown **by the
  directory name only**; `all` is the value that lists the individual files inside it.

**What the page does NOT document — the row's named limits.**

- It does **not** say that a tool must override, scrub or refuse the variable. The refusal is the
  writer's design decision, not a documented requirement.
- It does **not** document the **precedence** between a command-line `-c` value, a
  `GIT_CONFIG_COUNT`-injected pair and the repository-local config file. That precedence is a
  **probe fact** measured on git 2.56.0 (`probe-log.txt` P9–P12): the `-c` value wins over both
  the env-injected pair and the repo-local file, in both directions. It is not a documented
  guarantee of this page.
- It does **not** document the porcelain **output shape** — that `git status --porcelain` prints
  `?? path` lines, that an untracked directory is printed with a trailing `/`, or that `-z`
  NUL-separates the records. All of that is probe territory.
- It does **not** document anything about **receipt writers**, untracked-file *content* hashing,
  symlink handling inside an untracked directory (the C1 SY1/SY2 rows), or the writer's snapshot
  payload.
- It does **not** state the behaviour of `core.fsmonitor`, sparse checkout, or submodules with
  respect to this variable.
- It does **not** document the `git status -u` / `--untracked-files` **interaction with the
  writer's own `-c …=all` override** — i.e. that a caller passing `-u` would defeat the override.
  The writer never passes `-u`, so this is a design-collision note, not an observed failure.

## Named limits of this seat's work

- One page, one fetch date (2026-11-05), one host (Arch linux 7.2.11-arch1-1). The capture's
  sha256 is the reproducible artifact; the site is versioned ("git-config last updated in 2.56.0",
  banner dated 2026-09-28 in the captured bytes).
- The tag-strip recipe is **mine** (`s297-tagstrip.py`), not a lane-wide standard, and its output
  is **not** byte-identical to any previously committed `.txt` capture in `census/` (the r64
  captures use a different recipe). Every offset in `s297-located-quote.txt` is therefore
  reported **against the delivered capture bytes**, and the recipe is delivered beside them so the
  offsets can be re-derived rather than trusted. The r64 D1 lesson (offsets that no recipe
  reproduces) is the reason the recipe ships with the captures.
- The primary 11-word sentence is **not** byte-contiguous in the raw HTML and **not** in the
  rendered man output; only the whitespace-flexible HTML window and the tag-stripped text carry
  it. The three value-list sentences are byte-contiguous in both the text capture and the man
  output, which is why they are listed as supporting quotes with two independent carriers.
- Probes P5–P12 ran on git 2.56.0 on this host only. `core.fsmonitor` was not consulted and no
  fsmonitor daemon is configured here; a host with one may report differently.
- The semantic probes used one fixture shape (one committed file, one top-level untracked file,
  one untracked directory holding one file). Sparse checkout, submodules, worktrees and
  `GIT_WORK_TREE` were **not** probed.
- No registry row was written to `corpus/SOURCES.md`, no capture was written to `census/`, and no
  knowledge entry was written to `corpus/knowledge/`. The L1 owns all three. The scribe seat
  (S65ScribeEntry) owns the knowledge entry and must cite `S297` in it.
