STATUS: DONE — git-config states the variable is overridden by the option; the D1 fix is grounded, no page statement contradicts the claim, and one mode trap (`-u` bare = `all`, not `normal`) is located; the same false-clean exposure exists in `tools/souji-verify.sh:322/:366/:820` (routed, not fixed).

# Source opening — `status.showUntrackedFiles` and `--untracked-files` (round 17, W1)

Seat: SrcGitShowUntracked. Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Question: does a repository-local `status.showUntrackedFiles=no` hide untracked files from
`git status`, and does an explicit `--untracked-files=normal` override that config?

## 1. Access record (opened 2026-10-20)

| page | URL | version line the page serves | opened |
|---|---|---|---|
| git-config(1) | https://git-scm.com/docs/git-config | “git-config last updated in 2.56.0”; version list dates 2.56.0 to *2026-09-28* | 2026-10-20 |
| git-status(1) | https://git-scm.com/docs/git-status | “git-status last updated in 2.53.0”; first entry “2.54.0 → 2.56.0 no changes” | 2026-10-20 |

Local mirror used as a reproducibility anchor: host `git version 2.56.0`; installed man pages
`/usr/share/man/man1/git-config.1.gz` and `/usr/share/man/man1/git-status.1.gz`, both dated
`2026-09-27` in their roff headers. The corresponding sentences are present in the installed
pages (git-config for the override sentence, git-status for the default and mode text), so the
web text is not a version-drift artefact.

Transcription convention for every quote below: page markup (backticks, `[1]` link brackets)
rendered as plain text; no word added, removed or reordered.

## 2. Located quote(s)

Primary quote — the override, which is the operationally decisive half (13 words), at
**git-config(1) § status.showUntrackedFiles**, last paragraph of that entry:

> This variable can be overridden with the -u|--untracked-files option of git-status[1] and git-commit[1].

Reproducible anchor: installed `git-config(1)` roff lines 11936-11939, section heading at line
11884. Web page position: artifact of the served page, § `status.showUntrackedFiles`, the
sentence immediately after “All usual spellings for Boolean value true are taken as normal and
false as no.”

Supporting quote — the hiding half (20 words), at **git-status(1) § UNTRACKED FILES AND
PERFORMANCE**, first bullet:

> The --untracked-files=no flag or the status.showUntrackedFiles=no config (see above for both): indicate that git status should not report untracked files.

Reproducible anchor: installed `git-status(1)` roff line 1131 (`status.showUntrackedFiles=no`);
the section also states the default at roff 137-140: “The default can be changed using the
status.showUntrackedFiles configuration variable documented in git-config(1).”

Mode boundary that makes `=normal` the correct token (git-status(1) § OPTIONS, mode list,
roff 98-111): `normal` — “Show untracked files and directories.”; `all` — “Also show
individual files in untracked directories.” So `normal` keeps the one-line directory collapse;
`all` breaks it.

**Verdict: the claim holds, as documentation.** Both halves are stated by primary Git docs:
the variable suppresses enumeration, and the command-line option overrides the variable.
Confidence high for the documented semantics (tier A, official manual, no version drift
against the installed 2.56.0 pages).

## 3. Contradiction check

No statement on either page contradicts the claim text. Three adjacent statements constrain a
careless reading and are reported so the integrator does not inherit a wrong one:

1. **Bare `-u` is not `normal`.** git-status(1) § OPTIONS (roff 90-94):

   > It is optional: it defaults to all, and if specified, it must be stuck to the option

   The mode defaults to `all` when `-u`/`--untracked-files` is given without a mode, while
   omitting the option entirely means `normal` (“When -u option is not used, untracked files
   and directories are shown (i.e. the same as specifying normal)”, roff 113-116). Consequence:
   an “explicit --untracked-files” without `=normal` would expand untracked directories and
   break the collapse D1 says must be kept. The context's `--untracked-files=normal` spelling is
   the correct one; a bare `-u` would be a regression.

2. **`--porcelain` stability is about format, not enumeration.** git-status(1) § OPTIONS,
   `--porcelain` (roff-equivalent sentence):

   > This is similar to the short output, but will remain stable across Git versions and regardless of user configuration.

   This is why the existing `status --porcelain` invocation can still yield a false clean: the
   sentence promises format stability under user configuration, not that untracked enumeration
   is exempt from configuration. It does not contradict the claim; it bounds it.

3. **`config.worktree` outranks the other config files, but is still a config file.**
   git-config(1) § extensions.worktreeConfig:

   > The settings in the config.worktree file will override settings from any other config files.

   This supports the context's “repo-local/included/config.worktree” enumeration and means a
   pin that only edited `.git/config` would be insufficient. It also means the fix must be a
   command-line option (which the first quote says overrides the variable), not another config
   write. The page states no precedence between `-c`/`GIT_CONFIG_COUNT` and `config.worktree`;
   do not substitute `-c status.showUntrackedFiles=normal` for the option.

Related observed fact in the lane (not from the web page): the census already neutralises the
global and system layers — `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1` at `tools/souji-census.sh:153-154` — so the surviving sources are
exactly the repo-local `.git/config`, a file it includes, and `config.worktree`. That matches
the claim's source list; the option pin covers all three.

## 4. Smallest fix (operability)

`tools/souji-census.sh:1037` currently runs

```
-c core.attributesFile="$at" status --porcelain --ignore-submodules=all -- . \
```

Add the documented option to the same invocation:

```
-c core.attributesFile="$at" status --untracked-files=normal --porcelain --ignore-submodules=all -- . \
```

One token, on the only `git status` call in the file (`count_dirty`, `:1021-1047`; callers
`:1162` and `:1205`). Do not use bare `-u` (section 3, item 1). Do not add a `-c` pin (section 3,
item 3). Also correct the header comment at `:35-37`, which currently describes the mode as
“default untracked mode” — after the pin it is explicit, not default; a stale comment here is
exactly the kind of claim-vs-code mismatch the corpus rules forbid.

### 4.1 Falsifier found outside the declared C1 scope (reported, not fixed here)

The same documented mechanism reaches `tools/souji-verify.sh`, which the census header comment
at `:35-37` claims to match. That tool calls `git status --porcelain` with **no** untracked
mode at three safety-relevant sites:

- `tools/souji-verify.sh:322` — `dirty=$(git -C "$target" status --porcelain ...)` in the
  receipt path;
- `tools/souji-verify.sh:366` — the second receipt/dirty probe;
- `tools/souji-verify.sh:820` — the SAFE-gate dirty probe (`R_RECEIPT=dirty`).

so a repository-local `status.showUntrackedFiles=no` yields the same false clean there; the
primary quote in section 2 applies to those calls exactly as it does to the census. A fourth
call, `:658`, pins `--untracked-files=all` on a target-scoped status (`--ignored=matching`), so
the verifier currently runs three different untracked modes across four status calls. Two
consequences for the integrator:

1. Pinning only the census makes the two tools **diverge** on precisely the config-`no` repos:
   the census would report the dirty truth while the verifier keeps certifying a clean receipt.
   The `:35-37` comment's “matching souji-verify” would become false rather than true.
2. The declared C1 text scopes the fix to `tools/souji-census.sh`, so extending it to the
   verifier is an L1 decision (extend D1, or file a separate defect). This seat did not edit
   either file.

## 5. Drafted SOURCES row (exact registry column order)

Columns are the registry's: `id | source | kind | tier | scope | anchor | teaches | status |
opened | recheck | used-by`. One line; no `|` inside any cell.

```
| S0?? | git-config(1) status.showUntrackedFiles — https://git-scm.com/docs/git-config | docs | A | documented precedence of the -u/--untracked-files option over status.showUntrackedFiles for git-status enumeration, and the normal-versus-all mode boundary, not a runtime proof on this host | web manual "git-config last updated in 2.56.0" (2.56.0 dated 2026-09-28), opened 2026-10-20; § status.showUntrackedFiles; companion git-status "last updated in 2.53.0", "2.54.0 → 2.56.0 no changes", § OPTIONS -u and --untracked-files, § UNTRACKED FILES AND PERFORMANCE; installed git 2.56.0 git-config(1) roff 11884 and 11936, git-status(1) roff 90-94, 98-111, 137-140, 1131 | a command-line untracked-files option overrides the config that suppresses untracked enumeration, and normal keeps one line per untracked directory while all expands it, so the census can pin normal without changing the collapse | mined | 2026-10-20 | on-release | corpus/lessons/round-17.md |
```

Integration notes for L1:

- **id**: `S0??` per the assignment; the next unused id in the registry is **S051** (last row is
  S050). Replace `S0??` with the number L1 assigns.
- **status `mined`** is justified only because the C1/D1 change (adding the option at
  `tools/souji-census.sh:1037`) is grounded by the primary quote. If the round-17 Gate does not
  actually carry the quote, or `corpus/lessons/round-17.md` does not land, downgrade the row to
  `queued` and set `used-by` to `—`; a `mined` row with an absent `used-by` path would break the
  contract.
- **S044 interplay**: S044 (git-status, rejected) already records “Its status.showUntrackedFiles
  statement exposes a repo-local setting the census does not pin (open, r17)”. This row answers
  that open item. S044 itself stays rejected for its own scope (porcelain stability and
  value/effect guard); do not flip it, and do not rewrite its cells. Record the resolution in the
  round-17 Gate only.
- **Tier**: A, scoped as written. The page is authoritative for documented option/config
  precedence; it is not evidence that this host's census produced or now produces any particular
  row. Keep that disclaimer in `scope`.
- **Append-only**: this is a new row; no existing cell is edited by this seat.

## 6. Search-log sentence (paste-ready, `## Search log`)

> **Round-17 status enumeration (2026-10-20).** Question: does a repository-local
> `status.showUntrackedFiles=no` hide untracked files from `git status`, and does an explicit
> `--untracked-files=normal` override it? Opened the git-config and git-status web manuals and
> the installed git 2.56.0 counterparts. Identified 2 documents, screened 2; included 1 new
> row (git-config § status.showUntrackedFiles, A, mined on the D1 fix); no new git-status row
> (S044 already covers that page under a rejected scope, and its open r17 item is answered by
> this row). Stop: the override sentence, the hide statement and the normal-versus-all mode
> boundary were all located in primary text and mirrored in the installed manuals; no runtime
> repository was exercised.

## 7. Commands run and observed output

- `read https://git-scm.com/docs/git-config` — served, “git-config last updated in 2.56.0”.
- `read https://git-scm.com/docs/git-status` — served, “git-status last updated in 2.53.0”,
  “2.54.0 → 2.56.0 no changes”.
- `grep 'showUntrackedFiles'` over the served git-config page — heading and the override
  sentence located (§ status.showUntrackedFiles).
- `grep 'showUntrackedFiles|when the -u option is not used'` over the served git-status page —
  the default sentence and the `--untracked-files=no` bullet located.
- `git --version` → `git version 2.56.0`.
- `zcat /usr/share/man/man1/git-config.1.gz | grep -n 'can be overridden with the'` →
  matches; the status.showUntrackedFiles occurrence is at roff **11936-11939**, heading
  **11884**.
- `zcat /usr/share/man/man1/git-status.1.gz | grep -n 'showUntrackedFiles'` → **138** (default
  sentence) and **1131** (`status.showUntrackedFiles=no`).
- `zcat /usr/share/man/man1/git-status.1.gz | sed -n '80,115p'` → the `-u[<mode>]` paragraph,
  including “It is optional: it defaults to all” and the three mode bullets.
- `zcat /usr/share/man/man1/git-status.1.gz | head -5` and the equivalent for git-config →
  both roff headers dated `2026-09-27`.
- Lane reads for grounding only: `tools/souji-census.sh:35-37`, `:1021-1047`, `:153-154`,
  `:1162`, `:1205`; `corpus/lessons/round-16-verifier-spotcheck.md:104`, `:134`.
- `glob tests/fixtures/r17-census-hygiene.py` → **not found** (the executing seat creates it;
  no fixture exists yet, so this seat exercises nothing).
- `grep 'status --porcelain|untracked-files'` on the exact file `tools/souji-verify.sh` →
  four status call sites: **:322**, **:366**, **:820** pass no untracked mode; **:658** passes
  `--untracked-files=all`. No recursive search was run.

No repository behaviour was executed: the assignment carries no `ALLOWED-EXEC:` item, so no
scratch repository was created and no `git status` was run against a real or fixture repo. The
verdict above is documented, not observed at runtime; the r17 fixture arms are what will
observe it.

## 8. Remaining unknowns

- Runtime confirmation that `--untracked-files=normal` restores untracked lines under a
  repo-local `status.showUntrackedFiles=no` is left to `tests/fixtures/r17-census-hygiene.py`
  (absent as of this seat). [INFERENCE, from the documented override.]
- The page does not state precedence between `-c`/`GIT_CONFIG_COUNT` and a repository's
  `config.worktree`; the census already sets two `GIT_CONFIG_KEY_*` entries, so extending that
  mechanism for this pin would be an undocumented bet. The option is the documented lever.
- The page does not say whether `-z`/`--porcelain=v2` change enumeration; porcelain is a format,
  so the mode is the only enumeration control. [INFERENCE]
- `git commit` also honours the variable (git-config quote names it), but the census runs no
  commit; not a live concern for C1.
- Whether D1 extends to the three unpinned `tools/souji-verify.sh` status calls (§4.1) is an
  L1/operator decision; this seat only reports the divergence the declared census-only fix
  would create.

## 9. Tooling record

No install or upgrade was performed this round. `pacman` transactions are host-wide paused and
nothing was needed: the pages are reachable over the web reader and the installed git 2.56.0 man
pages were read with `zcat`/`grep`. Nothing was written outside this report.
