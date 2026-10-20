# Round 15 · w1 · GitSourceHooks — hooksPath source evidence

Seat: docs/source scout, leaf. Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Source anchor: baseline commit `cc2168325768d5356a82c039dcdf787377c55784`; live
`tools/souji-census.sh` sha256 `fcff8b057b3e…aee9` (identical to that blob when read).
No tests, probes, builds, edits outside this report. No tool installs/upgrades.
`census/operator-sweep-*` was never intentionally opened, copied, staged or
altered, but two pre-reminder recursive searches over the lane root could have
read its files at the filesystem level; see §9 for the exact calls and limitation.
Credentials and `~/.omp/agent`: not opened.

Axes: operability (C1, hooksPath slice), calibration (C2, preservation evidence).

## 1. Direct answer

`core.hooksPath` is **execution-inert for every command the census runs on a fleet
repo except `git status`, and that one invocation already forces
`-c core.hooksPath=/dev/null`.** The documented per-command disable plus documented
`-c` precedence therefore replaces the value-blind key refusal at
`tools/souji-census.sh:505` safely. The ban can be removed for **all values**, not
just `/dev/null`; a value allowlist would still fail benign `.githooks` setups and
would require stat'ing attacker-influenced paths.

Observed (source): line 503 lowercases `--name-only` output; line 505 matches
`*core.hookspath*` on the key list alone; line 506 calls `protected_fail`, which
`exit 2`s from `guard_git_config` (called at 581, 613, 628, 650, 665) and aborts the
whole census via `census_one` → `emit_census` (982–986). Any local value, including
`/dev/null`, is refused. Header line 86 documents that same refusal.

## 2. Located quotes (≤25 words each; all opened 2026-10-20)

Installed pages are Git 2.55.0 (`/usr/share/man/man1|man5`, `.TH ... 2026-06-29`).

| # | Quote | Location |
|---|---|---|
| Q1 | “You can also disable all hooks entirely by setting core.hooksPath to /dev/null.” | git-config(1) §core.hooksPath, installed roff L3897 |
| Q2 | “This is usually only advisable for expert users and on a per-command basis using configuration parameters of the form git -c core.hooksPath=/dev/null.” | git-config(1), installed roff L3898–3903 |
| Q3 | “Pass a configuration parameter to the command. The value given will override values from configuration files.” | git(1) §-c, installed roff L129 |
| Q4 | “By default the hooks directory is $GIT_DIR/hooks, but that can be changed via the core.hooksPath configuration variable” | githooks(5) DESCRIPTION, installed roff L39 |
| Q5 | “A relative path is taken as relative to the directory where the hooks are run” | git-config(1) core.hooksPath, installed roff L3890 |
| Q6 | “By default, git status will automatically refresh the index, updating the cached stat information from the working tree and writing out the result.” | git-status(1) BACKGROUND REFRESH, installed roff L1115 |
| Q7 | “This hook is invoked when the index is written in read-cache.c do_write_locked_index.” | githooks(5) post-index-change, installed roff L540 |
| Q8 | “This hook is invoked by any Git command that performs reference updates.” | githooks(5) reference-transaction, installed roff L342 |
| Q9 | “This hook is invoked by git gc --auto” | githooks(5) pre-auto-gc, installed roff L416 |
| Q10 | “Defaults to off when a specific file is given (e.g., using --file, --global, etc)” | git-config(1) --no-includes, installed roff L539–541 |

Web corroboration: Q1–Q2 appear verbatim in the version pages
`/docs/git-config/2.52.0`, `2.53.0`, `2.54.0`, `2.55.0`, and the 2.56.0 latest page
(“last updated in 2.56.0”). Q1’s introduction below 2.52.0 was **not** bounded.
Web githooks “last updated in 2.54.0”; git-status “last updated in 2.53.0”.
Q6–Q9 were read from the installed 2.55.0 pages, matching the host git.

## 3. Value classes inspected

| Value class | Census effect | Basis |
|---|---|---|
| `= /dev/null` | Documented full hook disable; status already uses it | Q1, Q2 |
| absolute dir (existing/missing) | Never looked up: no fleet command triggers a hook except status, which overrides | Q1, Q3 + §4 |
| relative dir, e.g. `.githooks` | Relative to hook-run dir (Q5); inert for the same reason | Q4, Q5 |
| value pointing into a protected store | Not stat’d: override wins before hook lookup; hooks lookup only occurs on a triggering event | Q1–Q3; **[INFERENCE]** no triggering event on those calls |
| empty value | Not documented; semantics not asserted | unresolved, see §7 |

Consequence: refusing by key name is both over-broad (C1 operability) and not the
mechanism that protects the census. The mechanism is the command-line override.

## 4. Invocation audit (`tools/souji-census.sh`, baseline lines)

Fleet-repo path (after `guard_git_surface`):

| Line | Invocation | Hook events possible | Override |
|---|---|---|---|
| 500 | `git config --file … --no-includes --name-only --list` | none (config parse; includes not followed, Q10) | n/a |
| 511 | `git config --file … --no-includes --get core.worktree` | none | n/a |
| 688 | `git -C … worktree list` | none (reads admin data) | not needed |
| 694 | `git -C … for-each-ref … refs/remotes` | none (no advertisement; no `--alternate-refs`) | not needed |
| 698 | `git -C … rev-list --count --branches` | none | not needed |
| 702 | `git -C … rev-list --count --branches --not --remotes` | none | not needed |
| 710–712 | `git -C … --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null … status --porcelain …` | `post-index-change` if the index is written (Q6, Q7); fsmonitor is a separate command, overridden | **yes** |
| 836 | `git -C … worktree list --porcelain` | none | not needed |
| 859 | `git -C … rev-parse --is-inside-work-tree` | none | not needed |

Worktree rows (`worktree_extra_flags`) reuse `count_dirty` (status) on registered
worktrees, so the same override applies there.

Selftest only (synthetic `$ST_TMP` fixtures, never fleet repos):

- 1157 `git add -A` writes the index → `post-index-change` can fire (Q7).
- 1203–1271 `git update-ref` (and 1171/1205 `symbolic-ref`) → `reference-transaction`
  can fire (Q8). 1170 `git init` runs no hook. 1158/1160/1163 plumbing runs none.
- Fixtures set no `core.hooksPath`; 122–123 disable global/system config, and 119
  clears inherited `GIT_*`; fixture hook dirs are sample-only. Risk nil, but this is
  why a uniform override is still the cheaper invariant.

No census command runs `git gc --auto` (Q9), `fetch`, `commit`, `checkout`, or
`rebase` on a fleet repo. `core.alternateRefsCommand` is not triggered by local
`for-each-ref`/plain `rev-list` — [INFERENCE] from its documented “advertising
alternate tips” scope; it remains refused anyway.

## 5. Operability verdict

Remove `*core.hookspath*` from the case at 505 and update header line 86 to state
per-command neutralisation. Do **not** replace it with a `/dev/null`-only value
check: (a) `.githooks` and absolute shared-hook dirs are benign for this command set
and would still abort the census; (b) distinguishing values requires stat’ing
attacker-influenced paths, which is worse than not inspecting them; (c) the
neutralisation is already documented and applied where it matters.

Recommended invariant (defense-in-depth, and the only residual-risk mitigation):
route all census git calls through one wrapper carrying
`-c core.hooksPath=/dev/null -c core.fsmonitor=false --no-optional-locks`
(pattern: `GIT_RO=(…)` at `tools/souji-census.impl-36.sh:162`), and make the
selftest source audit (1484 currently checks only forbidden subcommands) assert each
`git` line carries the override or is provably hook-inert.

## 6. Calibration (C2): the evidence that must be admitted

A green result (“benign hooksPath repo now emits a row, exit 0”) is **not** sufficient
and is green-only: it is equally consistent with hooks never having been able to run.
The admission checker must require all of:

1. **Pre-fix red** at baseline `cc2168`: repos with `core.hooksPath=/dev/null` and
   with `core.hooksPath=.githooks` exit 2 (`git-config-unsupported`), no TSV.
2. **Green benign, two values**: both repos above emit rows and exit 0 after the fix —
   the `.githooks` case is what distinguishes a real repair from a `/dev/null`
   allowlist.
3. **Non-vacuous red oracle** in the same fixture: with an executable
   `post-index-change` hook that writes a sentinel, plain
   `git -C fixture status --porcelain` **without** `-c`/`--no-optional-locks`, run
   after touching a tracked file (stale stat cache forces the index write, Q6/Q7),
   must create the sentinel. Without this step a “sentinel absent under census” green
   is vacuous. `git update-ref` (Q8) is the deterministic fallback oracle, but it
   tests reference-transaction, not the status path.
4. **Green sentinel**: the census run over that same repo exits 0, emits the row, and
   the sentinel stays absent.
5. **Namespace control**: a still-refused key (e.g. `include.path` or a
   `filter.*.clean`) in a sibling fixture still exits 2 — proof the repair is
   key-scoped, not blanket weakening.
6. **Static binding**: every hook-capable invocation carries the override (or the
   command set is shown hook-inert). A bare
   `grep -q 'core.hooksPath=/dev/null'` over the whole file is not independent
   evidence and must not be admitted as preservation proof.

`--no-optional-locks` suppressing the status index write is **not** documented
explicitly; Q3/“GIT_OPTIONAL_LOCKS to 0” only says locked optional operations are
skipped. That suppression is [INFERENCE]. Safety does not depend on it because Q1/Q2
already disable hooks for that invocation; the fixture in item 3 is how it would be
settled.

## 7. Residual unknowns

- Fleet incidence of local `core.hooksPath` was not measured; the operator census is
  off-limits to this seat. Round-14 N6 remains “to-verify on the real fleet”.
- Q1 introduction below git 2.52.0 not checked. Host is 2.55.0 (installed man page
  header), where Q1–Q3 are present.
- Empty `core.hooksPath` value semantics are undocumented; admission does not rely on
  interpreting it.
- A future git version could add a hook to a read-only command; only the uniform
  wrapper/audit invariant mitigates that.
- Whether `git status` ever triggers `git maintenance run --auto`: no text found in
  git-status(1); if it did, child git processes inherit `-c` via
  `GIT_CONFIG_PARAMETERS` **[INFERENCE]**, so Q1 still disables hooks. Not exercised.
- Includes remain refused by another key; admitting `hooksPath` cannot smuggle other
  keys through includes because the guard reads with `--no-includes` (Q10) and the
  include key itself is still refused.

## 8. Unrun checks for L1/executor

- `grep -n 'core.hookspath' tools/souji-census.sh` → only the updated header after A1.
- Count of git lines vs override occurrences under the chosen invariant.
- Fixture sequence in §6 (pre-fix red, two greens, red oracle, sentinel, namespace
  control) on host git 2.55.0.

## 9. Boundary disclosure (authoritative reminder received after these calls)

The reminder forbids lane-root recursive grep/glob/search because it queries the
operator sweep. Two calls made before the reminder did exactly that; they are
disclosed verbatim and were not repeated. Neither produced sweep content in any
output I read, and no sweep-derived fact appears in this report, but I cannot
certify at the filesystem level that the tools never read a file under that
directory.

1. Round-start discovery, `grep` tool: `path=/home/vgpnk/Projects/shokunin/souji-shokunin`,
   pattern `hooksPath|core\.hooksPath|hooks_path`. Recursive search over the whole
   lane (gitignore respected). Output listed only `.ufo/waves`, `census/round-3`,
   `corpus/lessons`, `tests`, `results`, `tools` hits; any sweep hit would have been
   suppressed only if gitignored. This is the call that located the source lines.
2. `grep -rn 'impl-36' --include='*.sh' --include='*.md' --include='*.json' . 2>/dev/null | grep -v 'census/operator-sweep-'`
   — recursive shell grep over `.`, with sweep-path lines filtered from *output*
   after reading. Also in the same command (separate call):
   `find . -maxdepth 2 -iname '*source*' -not -path './census/operator-sweep-*'`
   — whole-root walk at depth 2; the sweep was excluded from results but still
   visited/statted by `find`.
3. Name-only listings, no contents opened: `ls` of the lane root, `ls` of
   `.ufo/waves/round-15` and its `w1`, `ls census/round-15/`, and
   `ls census | tail -5` (parent directory names only).

All other reads were explicit known paths: `tools/souji-census.sh`,
`tools/souji-census.impl-36.sh`, `.ufo/waves/round-15/{w1-spec.json,w1/HooksNeutral.md,w1/SourcesDraft.md}`,
`census/round-15/claims.json`, `corpus/SOURCES.md`, `tests/*.sh`,
`tests/fixtures/case-F9/build.sh`, `results/*.json`, installed man pages, and the
named git-scm.com pages. Read-only git commands used: `rev-parse --verify
cc2168…`, `show cc2168…:tools/souji-census.sh | sha256sum`, and
`status --porcelain -- tools/souji-census.sh` (path-scoped metadata only; no
census behavior was executed). No runtime probe or test of the census was run, and
no broad search was performed after the reminder.
