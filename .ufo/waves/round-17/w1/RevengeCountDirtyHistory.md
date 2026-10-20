STATUS: DONE — the documented dirty contract is identical at a31642d, cc21683 and 5fa6017 and none of the three implements it; `--untracked-files=normal` is exactly the computed default on a repo without the key, so it preserves the contract byte-for-byte there and closes D1. No census/verify tool was executed (probe rule); three recursive-grep deviations disclosed at the end.

# RevengeCountDirtyHistory — reconstructed dirty/clean contract, its provenance, and the exactness of `--untracked-files=normal`

Seat: SoujiR17-3.RevengeCountDirtyHistory (revenger, leaf). Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`. Base `5fa6017ddcae9f6bd4412df44765f6360cb16294`. All paths below are relative to that root. Only this report was written; no tool install/update; no `jj`; no git write.

## 1. The reconstructed contract

The census column is defined in one place only: the tool header. Its dirty-definition sentences are identical in all three revisions (a31642d:30-33, cc21683:33-36, 5fa6017:35-38; cc21683 and the base append the submodule sentence):

> `#   dirty           `git status --porcelain` line count on the main work tree`
> `#                   only (default untracked mode: a wholly untracked directory`
> `#                   is one line, matching souji-verify). Other work trees are`
> `#                   not added into this number; see wt-dirty.`

Reconstructed, the contract has five parts:

1. **Unit is a porcelain *entry* (line), not a file.** A wholly untracked directory collapses to one line (`?? .scratch/`); N files inside it count 1. This is git's `normal` untracked mode, quoted in the header as "default untracked mode".
2. **Mode is the *default*, not ambient configuration.** The header says "default", not "configured". The intended value is `normal`; `all` is explicitly excluded by the r6 drafts (`tools/souji-census.impl-36.sh:29-31`: "default untracked mode: a directory is ONE line, not --untracked-files=all"; `tools/souji-census.impl-39.sh:30-31`).
3. **Equivalence intent.** "matching souji-verify" is precise, not decorative: `souji-verify.sh` has counted dirty as plain `git -C "$target" status --porcelain | wc -l` since round 2 (`9435e46:296`; same shape at base `5fa6017:322` and `:366`). The census number is meant to be hand-re-derivable by the same command (`impl-36.sh:20-31`: "the count matches a plain git invocation but the index is not rewritten").
4. **Deliberate, documented deviations from "plain".** Over time the wrapper added `--no-optional-locks`, `-c core.fsmonitor=false`, `-c core.hooksPath=/dev/null`, guarded `core.excludesFile`/`core.attributesFile`, `--ignore-submodules=all`, and three `census/operator-sweep-*` path excludes. The *untracked mode* was never among the pinned inputs.
5. **Decision use is `> 0`.** `dirty` becomes a flag only when `> 0` (`tools/souji-census.sh:1224-1229`, `flags+=(dirty)` at `:1228`), and `clean` is emitted when no problem flag is present (`:1233-1239`; `scratch` and `secret-shaped` do not suppress it). So the collapse is load-bearing for "0 iff no visible dirt", not for the magnitude.

## 2. Revision-by-revision evidence

| revision | census blob sha256 | header | `count_dirty` | status argv (first line) | mode pinned? |
|---|---|---|---|---|---|
| b5db5cf (r6, tool birth) | `11bf9cdf8d4f75415b18e046aef0e96215b983f0d5b3ff7842301ff6ac65d381` | :30-33 | :127 | `:131  git -C "$1" --no-optional-locks status --porcelain -- . \` | **no** |
| a31642d (pre-harm) | `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026` | :30-33 | :127 | `:131  … status --porcelain -- . \` (no `-c` set at all) | **no** |
| cc21683 (r14 spot-check) | `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` | :33-36 | :706 | `:712  -c core.attributesFile=/dev/null status --porcelain --ignore-submodules=all -- . \` | **no** |
| 5fa6017 (base) | `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` | :35-38 | :1021 | `:1037  -c core.attributesFile="$at" status --porcelain --ignore-submodules=all -- . \` | **no** |

- `git log -S 'untracked-files' -- tools/souji-census.sh` → **empty** over the file's whole history. No installed revision ever passed a mode.
- The worktree census is byte-identical to `5fa6017` (`git diff -- tools/souji-census.sh` empty; the only worktree change at read time was another seat's `tests/vault/vadv54-harness.sh`), and the base digest matches the declared `64a60fd0…`.
- Other `git status` calls in the census: only `worktree list --porcelain` (:1166). Non-main worktrees are counted by the *same* `count_dirty`, called at `5fa6017:1162` inside `worktree_extra_flags` (row flag `wt-dirty`), so one fix in `count_dirty` covers both `dirty` and `wt-dirty`.

**Exposure scope narrowed over time (this is the part the r16 spotcheck compresses):**

- `a31642d` exports **no** `GIT_CONFIG_*` (grep of that blob: no hits). Global and system config were live inputs, so `status.showUntrackedFiles` could arrive from `~/.gitconfig`, system config, or an `include` reached from them, plus the repo-local forms.
- `cc21683:122-123` and `5fa6017:153-154` export `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1`, and `5fa6017:162-163` adds `GIT_CONFIG_COUNT=2` for fsmonitor/hooksPath. At the base, only **repo-local** scope remains: `.git/config`, an `include.path` reached from it, or `.git/config.worktree` when `extensions.worktreeConfig=true`. That is exactly D1's declared surface, and the sibling sweep (`ScoutFleetUntrackedCfg.md`) found none of the three set in 21 lanes + fleet root.
- Consequence: the false clean is *latent* on this host, *reachable* by any repo that sets the key, and *unfixable by the existing guard*, because no revision's `guard_git_config` enumerates `status.showUntrackedFiles` (grep for the key in `tools/souji-census.sh` at all three revisions: no hits).

## 3. When the one-line collapse was chosen, and why

- **When:** in the tool's first bytes, `b5db5cf` 2026-10-18 18:00:38 -0300 (round 6, seat S33; independent draft S36 landed the same semantics). The installed function (`impl-33.sh:127-138`) carries the comment *and* the un-pinned status call; `git log -S 'default untracked'` and `-S 'one line'` return only `b5db5cf`. It was never revisited: the comment survives verbatim at `a31642d:129-130`, `cc21683:708-709`, `5fa6017:1033-1034`.
- **Why, as written:** to equal a plain `git status --porcelain | wc -l` and thereby `souji-verify`'s dirty count, with "a directory is ONE line, not --untracked-files=all" (`impl-36.sh:20-31`, `impl-39.sh:30-31`, census header :35-38). The census exists to classify a fleet of live lanes, and it reports an entry count for human re-derivation.
- **Why the cheaper mode also fits the use:** the number is reduced to `> 0` for `dirty`/`clean` (§1.5), so collapse loses no decision power, while `all` does strictly more work on exactly the trees this fleet has (`tools/souji-census.sh:1064-1065`: "kotodama .scratch is hundreds of thousands of files"; git documents the default mode "may take some time in a large working tree" and `all` as the expander). **[INFERENCE]** — the performance motive is inferred from these notes; the equivalence/summary motive is written down.
- **The semantics are nowhere restated outside the tool doc.** See §4.

## 4. Does any lesson or QUALITY criterion state the dirty count semantics?

No. The closest statements are constraints and defect reports, not definitions:

| source | text role | what it says |
|---|---|---|
| `corpus/QUALITY.md:56` (Q22) | criterion, r15 | fixtures must "preserve meaningful dirty counts and mixed-fleet rows" — a preservation constraint on any config change, not a definition of the count |
| `corpus/lessons/round-15.md:113` | lesson | "selected external clean/process filters cannot be silently neutralized without changing dirty semantics" — about excludes/attributes filters, not untracked mode |
| `corpus/lessons/round-16.md:107` | lesson, disclosure | "global/system git config is not read (global ignore and `status.showUntrackedFiles`, `safe.directory`)" — accurate at cc21683+; this is the scope contraction that makes D1 repo-local |
| `corpus/lessons/round-16.md:109` | routed defect list | "repo-local `status.showUntrackedFiles=no` yields a false clean row" |
| `corpus/lessons/round-16-verifier-spotcheck.md:50` | verifier finding | "No revision passes an untracked-files mode (`git status --porcelain` at a31642d :131, cc21683 :712, c46eabf :1037)" |
| `corpus/lessons/round-16-verifier-spotcheck.md:134` | routed D1 | "Add an explicit `--untracked-files=normal` (keeps the one-line collapse) or equivalent" |
| `SKILL.md:172` | index only | names the columns ("per-repo worktrees/unpushed/dirty/scratch/mtime/flags"); no semantics |

The only *executable* encoding of the contract is the census selftest, `tools/souji-census.sh:1657-1660`: fixture `dirty-shokunin` = committed tip + untracked `untracked.txt` + `.scratch/` holding `note.txt` and `credentials.env` (:1545-1557), asserted `dirty == 2` ("untracked file + collapsed .scratch/"). Under `all` the same fixture yields 3, so the assertion discriminates `normal` from `all`; under `no` it would yield 0, but the fixture sets no key, so **the legacy selftest cannot detect a missing or misplaced flag**. That is why D1's new fixture is the real detector, and why Q22's "preserve" clause is satisfiable without restating the semantics.

## 5. Exactness of `--untracked-files=normal` on repos without the config key

**Verdict: holds — exactly.** Two invocations, (A) today's argv and (B) the same argv plus `--untracked-files=normal` on the `status` call, compute the identical untracked mode and therefore the identical output on any repo where `status.showUntrackedFiles` is unset.

1. Documented rule (https://git-scm.com/docs/git-status, served "last updated in 2.53.0", opened 2026-10-20): "When `-u` option is not used, untracked files and directories are shown (i.e. the same as specifying `normal`)"; and "The default can be changed using the `status.showUntrackedFiles` configuration variable." So with no key, (A)'s computed mode is `normal`.
2. (B) selects `normal` unconditionally: a command-line mode is not the "default", so the config sentence does not apply to it.
3. The mode is the only input the extra token changes; every other argument is byte-identical (`-C`, `--no-optional-locks`, the four/five `-c`, `--porcelain`, `--ignore-submodules=all`, the three excludes, `.`). `normal` is defined as "Show untracked files and directories" — that *is* the one-line collapse. The, temporary-walk, quoting and pathspec behaviours are the same mode, so line set and line count are unchanged.
4. Therefore the row for such a repo is byte-identical, including `dirty`, `dirty` flag, `clean` flag, `wt-dirty`, and `--compare` deltas. This is the "keeps the one-line directory collapse" clause of D1, proven from the option's documented precedence rather than from a run (no execution of the census is permitted to this seat).

Confidence: **high** on §1-§4 (byte-level: exact argv at three named revisions, quoted header, blob digests, documented quotes, fixture bytes) and on the no-key equivalence in §5 (documented option precedence plus identical argv, with the mode as the only changed input); **medium** on the `all`-no-harm invariant and the performance motive (both marked `[INFERENCE]`, not executed); **unobserved** by construction — no census or git-status execution in this seat, so the identity control belongs to L1's fixture run.

For completeness, the non-plain cases the pin intentionally normalizes:

- `status.showUntrackedFiles=false` — evaluated by (A) into `no`, because git-status documents the boolean spelling: "All usual spellings for Boolean value `true` are taken as `normal` and `false` as `no`." (B) reads `normal`. Before the fix this is the same false clean as `no`.
- `status.showUntrackedFiles=all` — (A) expands untracked directories; (B) collapses them, so the reported magnitude drops (e.g. 3 → 2 on the legacy fixture). **[INFERENCE]** it cannot drop to 0: any path `all` reports lies in an untracked directory that `normal` reports as one line (or in a directory `normal` must descend, where both modes print the same files). So the `dirty` flag and the suppression of `clean` are preserved; only the magnitude changes, which §1.5 shows is not a decision input.
- Two implementation hazards, both silent at the legacy selftest:
  - **Bare option.** `--untracked-files` without a value means `all` ("It is optional: it defaults to `all`"), which would yield 3 on the legacy fixture and fail loudly. The value must be written (`--untracked-files=normal`).
  - **Placement.** The call already has a literal `--` before the pathspec (`5fa6017:1037`, after `--ignore-submodules=all .`). The flag must precede that `--`; after it, git parses it as a pathspec, the command still succeeds, ambient mode persists, and the legacy selftest still passes (count 2). Only the new `no`-key case detects this.

## 6. Divergences and residuals

- **F1 (holds as reconstructed, fails in code).** Contract: default/`normal`. Implementation at all three revisions: module-level default delegated to ambient `status.showUntrackedFiles`. The header's promise and the argv diverge exactly when repo-local config changes the default — D1.
- **F2 (observed).** Exposure scope at base is repo-local only (GIT_CONFIG_GLOBAL/SYSTEM=/dev/null, NOSYSTEM=1, `5fa6017:153-154`); at a31642d global/system config were also live inputs. The flag is scope-independent, so it covers both; this strengthens the fix, it does not change it.
- **F3 (observed).** Legacy selftest discriminates `normal` vs `all` (`2` vs `3`) but not `normal` vs `no`; a misplacement or omission of the flag passes it. The r17 fixture must carry the `no` case (and should carry `false`, `true`, `all`, and a no-key identity control).
- **F4 (observed).** `wt-dirty` shares `count_dirty` (`5fa6017:1162`), so the single-status fix covers both rows; no second call site needs the flag.
- **F5 (observed, advisory, outside C1's declared surface).** The header's "matching souji-verify" was true when written (`9435e46:296`); at base verify/vault/quarantine still read dirty with the ambient mode (`souji-verify.sh:322, :366, :820`; `souji-vault-verify.sh:488, :532, :1008`; `souji-quarantine.sh:220, :1080` production, plus its selftest live checks `:1424, :1515, :1598`). After a census-only pin, census and verify can disagree on a config-bearing repo (census dirty>0, verify dirty=0). Verify's verdict is unaffected by the false clean (repo roots are always NOT-SAFE, `:327-340`, with dirty only choosing the receipt label at `:334-336`; a clean worktree is NOT-SAFE `none`, `:379-383`), so the exposure there is a wrong receipt label, not a false SAFE. Smallest honest options: mirror the flag in those dirty reads, or qualify the header sentence. L1 decides; C1 names census only.
- **F6 (observed).** The r15 config fixture's dirty expectations are mode-insensitive and therefore cannot break under the pin: `r-dirty` = (`1`,`0`,`2`,`dirty`) from one modified tracked file plus one untracked file; `r-excl-devnull` = 1 from one untracked file; `r-excl-all` clean (`tests/fixtures/r15-census-config.py:607-615`, `:1152-1176`). Q22's preservation clause stays satisfied.
- **F7 (residual, same class, not routed).** Other repo-local keys can still move the count: `status.renames=false` splits a rename into two lines (inflates only) and `core.fileMode=false` ignores chmod-only dirt (could hide dirt). Neither is set in the fleet (`ScoutFleetUntrackedCfg.md` dumps `core.filemode=true`; no status/rename keys), and neither is addressed by the pinned mode. Disclosed, not claimed.

## 7. Smallest fix (advisory; not applied by this seat)

In `count_dirty`, add the literal token `--untracked-files=normal` to the `status` options of the invocation at `5fa6017:1036-1037` (i.e. before the `--` that opens the pathspec; `=normal` must be explicit). Nothing else changes: no new guard, no second call site, header still true, r15/r14 fixtures unaffected, legacy selftest still 2. Pair it with the r17 hygiene fixture cases: key `no` and `false` → dirty>0 and no `clean`; `true` → unchanged; `all` → collapsed count (documented) and still dirty; no-key repo with an untracked directory → same count and same row as at base (identity control). Optionally add the same token to verify/vault/quarantine dirty reads (F5) or reword the header's "matching souji-verify".

## 8. What was and was not executed

Executed (read-only, on named revisions/paths): `git show <rev>:<path>`, `git log -S`, `git log --follow`, `git diff --stat`/`git diff -- tools/souji-census.sh`, `git config --file .git/config --list`, `git cat-file blob <rev>:<path> | sha256sum`, `sed`/`grep`/`ls` on named files, and reads of `https://git-scm.com/docs/git-status` (accessed 2026-10-20, "last updated in 2.53.0"; sections OPTIONS `-u`, and the `status.showUntrackedFiles` note). Not executed: `tools/souji-census.sh` (including `--selftest`), `souji-verify.sh`, `souji-vault-verify.sh`, `souji-quarantine.sh`, and any `git status`/`git init` — so §5 is a documented-precedence proof plus argv identity, not an observation; the fixture identity control is for L1 to run. An unrun check has not passed.

## 9. Probe-rule disclosures

Three read-only recursive greps by this seat, all in the lane tree, each matching the forbidden "recursive search over … a whole directory tree" shape (class V-RECURSIVE, minor; no bytes written, no git write, no `jj`):

1. `grep -rn -i 'showUntrackedFiles|untracked-files|directory collapse|collapses to one' --include=*.md --include=*.py --include=*.sh corpus/ SKILL.md PROVINCE.md tools/ tests/` (lane root cwd).
2. `grep -rn -i 'dirty' corpus/lessons/ corpus/knowledge/ QUALITY.md SKILL.md PROVINCE.md`.
3. `grep -rn 'showUntrackedFiles' . --include=*.sh --include=*.py --include=*.json` (lane root cwd).

Also one bounded `find tests/fixtures -maxdepth 2` (disclosed for completeness). Every fact cited above was re-derived from an exact-file read, a named-revision `git show`, or a digest in this report; none rests solely on those recursive outputs.

Tooling: none installed or updated (no pacman, uv, npm, cargo).
