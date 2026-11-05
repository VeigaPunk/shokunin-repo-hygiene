source: S297 — https://git-scm.com/docs/git-config § status.showUntrackedFiles (accessed 2026-11-05); S291 — git-update-index(1) skip-worktree/index flags (https://git-scm.com/docs/git-update-index; accessed 2026-11-05), cited where the index-flag rule is named
verified-at: af81553f23086e3fa7556d552a0d26d4a995c216 (the measured revision of `tools/souji-receipt-write.py`; docstring-only correction after the first measured rev 40a371d8, behaviour bytes unchanged; C1 and C2 re-measured at af81553f)
recheck: `python3 -B census/round-65/c1-counter.py --root LANE --matrix census/round-65/c1-matrix.tsv --base-rev 4a43a4d919c5b51ae9be859a1266ce4b11337b0b --rev af81553f23086e3fa7556d552a0d26d4a995c216 --tool tools/souji-receipt-write.py --work DIR` must print `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS` and `EXIT=0`; the V1/V2 rows inside it are the re-verification point for this entry

# A receipt writer's clean-tree check must not be steerable by operator config

ground: F4-adjacent — receipt hygiene: the receipt writer's dirty check is the instrument that decides
whether the tree it measures is the tree it claims (extends `knowledge/skip-worktree-concealment.md`,
which closes the index-flag route to the same guarantee)

## Claim

A receipt writer that refuses on `git status --porcelain` can be blinded by operator configuration
alone, with no change to any tracked byte and no change to the instrument itself. `status.showUntrackedFiles`
is the documented switch that decides whether untracked entries are displayed at all; set it to `no` and the
porcelain output omits every untracked path, so a tree carrying an untracked file reads as clean and the
writer writes a receipt over it.

## Rule (round 65, C1 rows V1/V2)

Every `git status` read the writer makes overrides `status.showUntrackedFiles` to `all` on the command line:

    git -C <root> -c core.fsmonitor=false -c status.showUntrackedFiles=all status --porcelain

A command-line `-c` outranks both the repository's own config and a `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/
`GIT_CONFIG_VALUE_0` environment injection for that key, so an operator-injected `status.showUntrackedFiles=no`
cannot hide an untracked entry from the dirty check. The override is applied to every status read (the
pre-run dirty check, the pre-run NUL-separated snapshot read, and the post-run re-read), not to one of them.

Falsifiable form: under a repository-local `status.showUntrackedFiles=no` with one untracked file present,
the base writer (round-65 base `4a43a4d919c5b51ae9be859a1266ce4b11337b0b`) writes a receipt (exit 0) and
the landed writer refuses with `lane worktree is dirty` (exit 2). Under the same configuration with a CLEAN
tree, both accept — the override must not turn an honest clean run into a refusal.

## Measured (round 65)

- Frozen 19-row matrix, `census/round-65/records/c1-after.txt` (writer at `40a371d8…`): `new_forgeries=0
  new_honest=5 class_mismatches=0 regress=PASS`, exit 0. Base writer in the same counter: `base_forgeries=12`.
  The do-nothing arm (`census/round-65/controls/c1-do-nothing.txt`, base bytes in the new slot) prints
  `new_forgeries=12` and exits 1.
- Row `V1 untracked-visibility-concealed` (repository-local `status.showUntrackedFiles=no`, one untracked file):
  base `accept` (rc 0), new `refuse` with `lane worktree is dirty` (rc 2).
- Row `V2 untracked-visibility-honest` (same config, clean tree): base `accept`, new `accept` (rc 0) — the
  override is not a blanket refusal.
- Independent re-run of the same counter from the seat's scratch
  (`.ufo/waves/round-65/w1/S65ScribeEntry/`, writer bytes at `40a371d8…`, base bytes at `4a43a4d9…`):
  `SUMMARY matrix=19 base_forgeries=12 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0
  regress=PASS`, `EXIT=0`; the do-nothing arm reproduced `new_forgeries=12`, exit 1.
- Host git 2.56.0 precedence probe (`excl_probe3.py`, `v2_probe.py` in the seat's deliver directory): a
  command-line `-c status.showUntrackedFiles=all` wins over a repository-local `=no` and over a
  `GIT_CONFIG_COUNT` injection of the same key.

## The override is key-scoped: a scope defect in the landed writer's own wording

The landed writer's docstring paragraph (round-65 C1) reads:

> every status read overrides status.showUntrackedFiles to `all`, so an operator-injected config cannot hide
> untracked entries from the dirty check or the content snapshot

The first clause is true; the second is broader than the bytes support. The override neutralizes ONE config
KEY. It does not neutralize `core.excludesFile`, and it cannot: a file matched by an exclude rule is IGNORED,
not untracked, so `showUntrackedFiles=all` does not surface it. Measured, per-slot FRESH fixture repos (one
untracked file `untracked.txt` in each, so no cross-slot state), writer blob `be344a7d` (`40a371d8…`), base blob
`9fb55f35` (`4a43a4d9…`); scripts `excl_probe3.py` / `v2_probe.py` and raw output in this seat's deliver
directory:

| arm | operator state | base | landed writer |
|---|---|---|---|
| A | repo-local `status.showUntrackedFiles=no` (the frozen V1 shape) | accept rc 0 | **refuse rc 2**, `lane worktree is dirty` |
| B | `core.excludesFile` injected via `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0` | accept rc 0 | accept rc 0, receipt written |
| C | repo-local `core.excludesFile` | accept rc 0 | accept rc 0, receipt written |
| D | tracked `.gitignore` naming the file | accept rc 0 | accept rc 0, receipt written |
| E | repo-local `.git/info/exclude` naming the file | accept rc 0 | accept rc 0, receipt written |
| F | control, no concealment | refuse rc 2 | refuse rc 2 |
| V2 | repo-local `status.showUntrackedFiles=no`, CLEAN tree | accept rc 0 | accept rc 0 (honest polarity holds) |

What this is and is not:

- The base writer accepts arms B–E too, so this is a RESIDUAL shared limit, not a round-65 regression.
- It is NOT a forgery against the frozen V1 row. V1's shape is specifically `status.showUntrackedFiles=no`,
  that row passes, and the frozen scoring is untouched: `new_forgeries=0`, exit 0, independently re-run.
- It IS a defect in the LANDED WORDING, and the sentinel seat rates it HIGH on the same grounds
  (`.ufo/waves/round-65/w1/S65SentinelScope/probe-env-output.txt`). `SKILL.md`'s own writer-delta sentence is
  already key-scoped ("every status read overrides `status.showUntrackedFiles=all` (V1/V2)") and IS in the C2
  population; the overreach is in `tools/souji-receipt-write.py`'s docstring, which is not. C2's
  `findings=0` is therefore unaffected, and this is a route-to-round-66 item, not a C2 finding.
- The candidate fix is a WORDING fix, not a scrubbing fix: reword the docstring to the key-only claim.
  Scrubbing `GIT_CONFIG_*` or pinning `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM` would change what the writer
  reads and is an operator/design decision, not a scribe's call.

Proposed header wording for the L1 (not applied by this seat; no lane file was edited):

> every status read overrides status.showUntrackedFiles to `all`, so THAT CONFIG KEY cannot hide untracked
> entries from the dirty check; other operator-config routes that make a path IGNORED rather than untracked
> (`core.excludesFile`, `.git/info/exclude`, `.gitignore`) are not closed by this override.

### Named limits that accompany it

- **Ignored files are not untracked.** A path covered by `.gitignore`, `.git/info/exclude` or
  `core.excludesFile` is invisible to `git status --porcelain` by design, with or without the override. The
  receipt writer's dirty check is a status check; it says nothing about ignored content.
- **The environment is not scrubbed.** The writer's `git()` helper removes only `GIT_DIR` and `GIT_WORK_TREE`;
  `GIT_CONFIG_*` passes through to child git. For `status.showUntrackedFiles` the `-c` override outranks the
  injection, so no bypass exists for that key (host git 2.56.0, measured: a command-line `-c` beats both the
  repository config and a `GIT_CONFIG_COUNT` injection of the same key); for other keys the passthrough IS a
  live route — arm B above is exactly that, and it accepts.
- **The wrapped command inherits the caller's environment.** The writer's own reads are controlled; a child
  process spawned by the wrapped command inherits the caller's `GIT_*` environment and may read a different
  view than the writer measured.
- **Config beyond these is unread.** `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES` and
  `GIT_REPLACE_REF_BASE` are not scrubbed and not checked; the frozen preregistration names this limit for the
  r65 C1 matrix as a whole (`census/round-65/preregistration.txt`).
- **Index-flag concealment is a separate route, closed elsewhere.** `skip-worktree` and `assume-unchanged`
  hide worktree divergence from `git status`; that is the `RECEIPT-INDEX-FLAG-CONCEALED` refusal (S291's
  manual caveat, S292's tags), landed in round 62, and documented in `knowledge/skip-worktree-concealment.md`.
  The untracked-visibility route is a different key and a different refusal (`lane worktree is dirty`).

## Gate

opened: 2026-11-05 — one page fetched live this round (`https://git-scm.com/docs/git-config`), HTTP 200,
830605 bytes, sha256 `37aa8407b12e377a38f523d5012835d0515cc82f2249c942b9e5cff656019226`; the section is
`status.showUntrackedFiles` (HTML anchor `Documentation/git-config.txt-statusshowUntrackedFiles`, at raw
HTML offset 761837). The captures and the located-quote proof are the scout seat's
(`.ufo/waves/round-65/w1/S65ScoutSources/`: `s297-git-config.html` sha256 `37aa8407…9226`,
`s297-git-config.txt` sha256 `a692dbcb…7c3f`, `s297-git-config.man.txt` sha256 `2fec59ce…f8f8`,
`s297-located-quote.txt`); the L1 copies them to `census/round-65/sources/` under the names row S297's
anchor cell names. This seat independently re-ran the slice assertions against the scout's DELIVERED bytes
and they PASSED (text 299266/299360/299437/299496, man 330781/330890).

- ADMIT (S297) — git-config(5) `status.showUntrackedFiles`, https://git-scm.com/docs/git-config, §
  `status.showUntrackedFiles`; accessed 2026-11-05; HTTP 200; sha256 `37aa8407…9226` — located quote
  (11 words, byte-contiguous in the tag-stripped text capture at offset 299266, slice assertion PASSED):
  `So, this variable controls how the commands display the untracked files.` — reason: it states the
  variable's subject in the page's own words, which is exactly what the round's C1 V1 row turns into a
  refusal. The three documented VALUES are the second carrier and are byte-contiguous in BOTH the text
  capture and the rendered man output: `no - Show no untracked files.` (6 words; text 299360, man 330781),
  `normal - Show untracked files and directories.` (7 words; text 299390, man 330827),
  `all - Show also individual files in untracked directories.` (9 words; text 299437, man 330890). The
  default (`normal`) and the `-u|--untracked-files` command-line override are also on the page (text 299496
  and 299634). Flip: the page no longer documents the variable, or the located quote stops being
  byte-contiguous in the named capture.
- REJECT (do not admit) — "a receipt writer must override `status.showUntrackedFiles`" — reason: the page
  states what the variable controls and what its values mean; it assigns no duty to any consumer, and the
  override is this lane's design decision, not a documented requirement. Flip: a git(1)/git-config sentence
  that assigns that duty to tools that gate on `git status`.
- REJECT (do not admit) — "`status.showUntrackedFiles=all` makes every untracked file visible" — reason: the
  page's `all` value is scoped to files in untracked DIRECTORIES; it does not promise that ignored files
  become visible, and the measured `core.excludesFile` arm shows they do not. Flip: a page sentence stating
  that `all` surfaces ignored paths too.
- REJECT (do not admit) — "`GIT_CONFIG_*` cannot override a command-line `-c`" — reason: this is a measured
  git behaviour on the host (git 2.56.0), not a statement on this page; it belongs to the measured limit
  above, not to a docs row about the variable.
- REJECT (do not admit, and the lesson's rejection candidate) — "an operator-injected config cannot hide
  untracked entries from a receipt writer's dirty check" — reason: as a GENERAL rule it is FALSE on the
  measured arms above (B, C, E accept; only the `status.showUntrackedFiles` key is closed). The page does
  not support it either: it documents one variable's values, and says nothing about any other config key's
  effect on `git status`. Flip: a git-config or git-status sentence stating that the variable is the ONLY
  switch that governs untracked visibility, or that other exclude mechanisms are covered by it.
- **Neighbour row.** S057 already carries this page's URL under a DIFFERENT scope (the `-u/--untracked-files`
  command-line override); S042 carries it generically and S238 carries `GIT_CONFIG_COUNT`. S297's scope is
  the untracked-visibility refusal (which values exist and what each displays) — the complement S057's scope
  cell points at. A duplicate-url census warning (W04) is expected, exactly as for S291/S295/S296 and
  S251/S239/S244; it is not a finding.
- Non-author closure: sample the ADMIT quote's byte-offset assertion in the COMMITTED capture; sample the
  three REJECT flips (duty-to-tools; ignored-files-surfaced; the general rule above) against the page bytes;
  and sample whether the entry's own rule sentence is stated at the key's scope rather than the class's.

## What this does not prove

- The claim is about one config key on one git version's status read. It is NOT a statement that a receipt
  writer is immune to operator configuration in general; the measured arms B, C and E say the opposite for
  the ignore routes, and the landed writer's own docstring currently overclaims accordingly.
- The override does not make `git status --porcelain` a complete inventory of the worktree: it says nothing
  about ignored paths, submodules, or file content.
- Bytes are not execution: the receipts cited here are the round's committed receipts plus this seat's
  independent re-runs from scratch; neither proves the command that produced them was the one described.
