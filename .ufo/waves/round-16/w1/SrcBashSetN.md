# SrcBashSetN — GNU Bash `-n` source opening (round 16, W1)

Scout: `SoujiR16.SrcBashSetN`. Question: locate the vendor `-n` text that grounds C2's
`bash -n` parse check, state what it does not check, and draft the SOURCES row.
Verdict: source opened through a Wayback capture (live gnu.org unreachable), quote located,
one row proposed as **S043**. `corpus/SOURCES.md` untouched.

## Source access

- Requested live: `https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html`.
  On 2026-10-20 the fetch failed twice through the `read` device (https and http) and
  `curl -fsSIL` exited 28 after 25 s; `https://www.gnu.org/` itself timed out after 12 s.
  Control hosts answered 200 (`man.archlinux.org`, `tiswww.case.edu`), so the failure is
  host-specific, not a dead network.
- Served instead: Wayback capture **20260930073822** of the exact URL
  (`/web/2026id_/…` returned 302 to that capture). Page meta: generator `makeinfo`,
  title `The Set Builtin (Bash Reference Manual)`.
- Served version / last-updated line (manual Top node, capture **20260927102039**):
  "This is Edition 5.3, last updated 18 May 2025, of The GNU Bash Reference Manual,
  for `Bash`, Version 5.3." The Top node also says "Bash shell (version 5.3, 18 May 2025)".
  The `html_node` page carries no per-page last-updated stamp; the edition line is the
  version statement.
- Installed corroboration: `/usr/share/man/man1/bash.1.gz`
  (sha256 `b68beb3e385f7d8aead26bf7887c12f93ca769dcd528fd7282d70938b09bdffe`),
  `.TH BASH 1 "2025 April 7" "GNU Bash 5.3"` at roff line 24.

## Located quote (≤25 words)

Set Builtin `-n` bullet, web manual (18 words):

> "Read commands but do not execute them. This may be used to check a script for syntax errors."

Same bullet, third sentence (7 words):

> "This option is ignored by interactive shells."

Same page, sentence that binds the option to invocation (11 words):

> "The options can also be used upon invocation of the shell."

Installed `bash(1)` variant, roff lines 11466-11469 (19 words) — differs from the web page by
one word:

> "Read commands but do not execute them. This may be used to check a shell script for syntax errors."

Supporting anchors opened in the same manual edition:

- §3.1.1 Shell Operation (capture 20260918164633): steps 3 (parse), 4 (expansions),
  6 (execute) are distinct stages.
- §3.7.2 Command Search and Execution (capture 20260921231239): function lookup and
  "If that function is not defined, the shell prints an error message and returns an exit
  status of 127" happen during command execution.
- Installed `bash(1)` roff 5943-5945: bash "exits with a non-zero value" on a syntax error
  (the web Exit Status node was not opened; no claim about exit code 2).

## What `-n` does NOT check

Grounded in the located text:

- **Runtime.** Nothing is executed, so failing commands, missing files, permission errors,
  side effects, expansions and redirections are never reached.
- **Unset variables.** The same page's `-u` bullet makes unset variables an error "when
  performing parameter expansion"; expansion is stage 4 and `-n` stops after parsing.
  Composition of two facts from one page; not a single explicit sentence.
- **Interactive context.** Interactive shells ignore the option, so a gate must invoke
  `bash -n file` (a fresh non-interactive shell), not rely on `set -n` typed interactively.
- **Scope.** The manual frames the use as checking "for syntax errors" — a parse-only claim.

Inference (marked, from the two located nodes):

- **Unset functions.** `[INFERENCE]` A call to a function defined nowhere parses clean:
  function lookup happens in command search at execution (3.7.2 steps 1-3), and the
  not-found result (status 127) is an execution-time outcome.
- `[INFERENCE]` `bash -n` is not shellcheck: style/robustness findings (e.g. SC2115) are not
  syntax errors, so a clean parse says nothing about them.
- `[INFERENCE]` It proves bash-grammar well-formedness only, not that the file is a runnable
  program (shebang, exec bit, valid paths) — implied by "do not execute them".

Not measured this round (open):

- Exact exit code on syntax failure (manual says non-zero, not specifically 2).
- Whether syntax errors inside `$(…)` or here-documents are reported by `bash -n`.
- Whether `tools/souji-landing-gate.py` actually shells out to `bash -n`: the file is absent
  at read time (glob `Path not found`), so this row grounds the primitive, not the tool.

## Proposed row — S043 (not admitted)

`S042` is the last registry row (`corpus/SOURCES.md:54`); no Bash-manual row exists in
S001–S042, and the four gnu.org rows are coreutils pages (different manual path), so the
URL is not a duplicate. Next free id: **S043**. Sibling `SoujiR16.SrcGitStatusRejected` also proposes S043 for
git-status(1); both reports name the collision, so L1 renumbers one of them (this row is the
Bash-manual one and moves as a unit if renumbered). Shape is the 11-column registry.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S043 | GNU Bash Reference Manual, The Set Builtin — https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html | docs | A | `-n` (noexec) parse-only syntax check in Bash 5.3 and the failure classes it cannot detect; not implementation proof | manual Edition 5.3, last updated 18 May 2025 (Top node); accessed 2026-10-20 via Wayback captures 20260930073822 (The-Set-Builtin), 20260927102039 (index), 20260918164633 (Shell-Operation), 20260921231239 (Command-Search-and-Execution), live gnu.org timed out; `-n` bullet and invocation sentence; installed bash(1) GNU Bash 5.3, 2025 April 7, roff 11466-11469 and 5943-5945 | `-n` reads commands but executes none and checks syntax only: unset variables fail at parameter expansion, absent or failing commands and undefined functions fail at command search (status 127), and interactive shells ignore the option | queued | 2026-10-20 | on-release | — |

Integration cells (for L1): flip `status` to `mined` and `used-by` to
`corpus/lessons/round-16.md` when the round lesson exists — the same
draft-`queued`/`—` → admitted-`mined`/lesson path used for S042 in round 15. The operational
consumer named by C2, `tools/souji-landing-gate.py`, does not exist yet.

Column notes:

- `kind`/`tier`: `docs`/`A` — the primary vendor manual for its own option.
- `scope`: parse semantics only; explicitly not a sandbox, execution or lint proof
  (same hedging style as S042).
- `anchor`: served edition and capture ids, plus the installed 5.3 man page for offline
  corroboration and the one-word variant ("a shell script").
- `recheck`: `on-release` (next Bash release), matching the other vendor-doc rows.
- `teaches`: keeps the documented facts and the three non-diagnosed classes in one cell;
  no claim that everything syntactic is caught.

## Calibration notes

- The r15 draft's validator reference `scripts/sources-census.sh` is stale: `git ls-tree`
  at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` lists `tools/` entries and no `scripts/`
  entries, and the working-tree path is not found. The W03 "mined with `—`" rule is cited
  from the round-15 draft prose, not re-verified here, so the draft stays `queued`.
- The page and Top node come from two different captures (2026-09-30 and 2026-09-27) of the
  same 5.3 edition; neither is a per-page date stamp.
- The live-page failure is an availability fact, not evidence that the page changed.
- C2's other two detectors (frozen pin matching no committed bytes; seat-reported failure not
  carried verbatim) are semantic checks. `bash -n` grounds only detector 1 (non-parsing
  script); it cannot ground the other two.

## STATUS

STATUS: live gnu.org unreachable from this host on 2026-10-20 (curl exit 28, 12-25 s timeouts,
both schemes); quote from Wayback capture 20260930073822, edition line from capture
20260927102039, installed GNU Bash 5.3 man page corroborates. `tools/souji-landing-gate.py`
and `scripts/sources-census.sh` are absent at read time.

## Commands

```sh
curl -fsSIL --max-time 25 https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html
curl -fsSI --max-time 15 https://man.archlinux.org/man/bash.1
curl -fsSI --max-time 12 https://www.gnu.org/
curl -fsSI --max-time 15 https://tiswww.case.edu/php/chet/bash/bash.html
curl -fsSI --max-time 20 "https://web.archive.org/web/2026id_/https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html"
sha256sum /usr/share/man/man1/bash.1.gz
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 scripts/ tools/
```

File reads used the `read`/`grep`/`glob` devices on the URLs and paths cited above; no other
shell commands were run.
