STATUS: DONE — no fleet checker C2 should reuse; resolve path-at-rev inside the landing gate.

# ConnFleetPointerTools — reuse sweep for LG-DANGLING-PTR

Seat: SoujiR18.ConnFleetPointerTools-5. Axes: calibration (judged), operability, coverage. No tools installed (pacman paused; nothing required). Checkers were not executed. Probe forbids running them against a real tree, and this seat has no ALLOWED-EXEC. Verdicts are from the named sources below.

Question: does the fleet already have an evidence-pointer checker that C2 (`LG-DANGLING-PTR` in `tools/souji-landing-gate.py`, `--round` ≥ 18, path tokens at `REV`) should reuse instead of reinventing?

Answer: **none.**

## Contradiction (do not collapse)

Three different “resolves” predicates are already in the fleet. They are not interchangeable with C2.

| Predicate | Where | What a hit proves | What C2 needs |
|---|---|---|---|
| Worktree existence (`[ -e ]`, `Path.exists()`) | `scripts/sources-census.sh` E11; kagi `cite_target`; kotoba `citation_resolve` and report pointers | The path exists on the disk being read now | No. C2 grades `--rev`, including the before-count at `b576341` |
| `git cat-file -e <hex>^{commit}` | kotoba commit citations | That hex is a commit object | No. That is not a path in a tree |
| `git show <rev>:<path>` over a pinned table | kaidoku `citation-drift-probe.py` | Those pre-listed entries’ bytes exist at that rev | The rev binding only. The table cannot discover a new dangling token |
| `git cat-file -e <commit>:<path>` | souji `SKILL.md:129` quarantine post-check | One named path is or is not in that commit | The git question, not the checklist. It is not a scanner |

Importing any of the first three changes which tokens are findings. That moves calibration the wrong way. Importing them also pulls another lane’s process into the landing gate (operability) and scans the wrong file set (coverage).

## Fleet script named by the assignment

`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (read). Header lines 21–29 and `usedby_findings` at 538–568.

E11 is real and narrow. It walks only a `## Registry` table, only rows whose status cell is `mined`, splits the used-by cell on commas, and emits `<lane>\tE11\t<id> missing used-by <path>` when `[ ! -e "$dir/$path" ]` (line 566). Selftest name `E11-dangling-usedby` is line 136. No `--rev`, no brace expansion, no `round-A..B` ranges, no fleet-versus-lane class, no exemptions file, no prose scan of `SKILL.md` / `SCORECARD.md` / `LOG.md` / `corpus/knowledge`. A citation of `census/round-17/gate-replays-ddb7347.json` in `SKILL.md` never becomes E11.

`scripts/` was not inventoried beyond this file. A tree walk is outside the probe. The lane `SKILL.md` files are the registry of checkers those lanes tell a reader to run.

## SKILL.md sweep

Command: `ls -1d /home/vgpnk/Projects/shokunin/*-shokunin` (exit 0, 21 directories).

`ls -1 /home/vgpnk/Projects/shokunin/*-shokunin/SKILL.md` exited 2. These three lane directories exist and have no `SKILL.md`: `audio-shokunin`, `game-dev-2d-shokunin`, `revenger-shokunin`. Nothing to grep.

One ripgrep per existing `SKILL.md`, pattern `dangling|pointer|cat-file -e` (the assignment’s alternation). Hits below. “No matches”: `kasegi-shokunin/SKILL.md`, `kumitate-shokunin/SKILL.md`.

### Rejected as the C2 implementation

**kagi — closest scanner, wrong oracle and wrong exemption.** `kagi-shokunin/SKILL.md:241` points at `bash corpus/claim-ledger.sh citations`. The script header (`corpus/claim-ledger.sh:31-46`) and `cite_target` (`453-466`) resolve with `[ -e $ROOT/… ]` on the worktree. `.ufo/…` and `ufo/…` are looked up at `$ROOT/../.ufo/` and a miss is `UNRESOLVED` (`460-463`, `569-571`). C2 says a token that exists only in the fleet repo is class `fleet` and is not a finding. This lookup would file L1’s fleet-relative `.ufo/scopes/…` and `.ufo/waves/hyaku/…` tokens as failures. A citing line matching `scratch|ephemeral|relocat|formerly|no longer|removed|renamed|historical` (`440`, `566-568`) is `LABELED` and does not fail. C2’s only exemption is a committed `corpus/pointer-exemptions.tsv`. The skip set is `*`, `<`, `…`, `...` (`545`), not C2’s `<` `>` `*` `round-N`, and there is no `round-6..11` expansion. Braces are single-group `{a,b}` with spaces stripped (`548-556`). Docs are read from the live files (`499-507`), not from `git show REV:path`.

**kotoba — worktree, host-anchored, wrong prefixes.** `SKILL.md:232-236` and `:472-478` name `verifiers/verify_skill_checklist.py` (`trigger.citation_resolves`, `governance.citation_resolves`) and `verifiers/verify_corpus_integrity.py`. `CITATION_ROOTS` (`verify_skill_checklist.py:347`) are `corpus/`, `verifiers/`, `opencode/`, `.ufo/`, `../`. `census/`, `tests/`, and `tools/` are not subjects. `citation_resolve` (`1295-1316`) uses `safe_resolve` or `Path.exists()`. `verify_corpus_integrity.py:45-46` states both families are read from the working tree, not from HEAD. Report pointers are `.ufo/reports/round-N/*.md` existence via `is_file()` (`16-21`, `605`). The only `cat-file -e` there is `git cat-file -e <hex>^{commit}` (`24-25`, `606-608`), which proves a commit object. `SKILL.md:495-496` already records that pointer resolution is host-anchored, so a clone’s green verdict is not hermetic. C2’s before/after count is a rev property.

**kaidoku — right binding, wrong input.** `SKILL.md:448` registers `citation-drift-probe.py --rev`. The script (`citation-drift-probe.py:4-8`, `120-125`) resolves each entry of a pinned `pointer-table.json` with `git show <rev>:<path>` and says Git objects, never the moving worktree. That is the only lane checker that already refuses the worktree. It still cannot be the C2 scan: a path becomes visible only after a human adds a table row and re-pins `expected.json` (`34-40`). The 18 unresolved tokens at `b576341` would not be found. Findings are `citation_file_absent` / `citation_dead` / content drift, not `LG-DANGLING-PTR`. `git show` also materializes file bytes; C2 only needs existence. Round-18 rev policy (`42-49`) rejects a detached jj `HEAD`. Souji is jj-colocated. Calling this probe from the landing gate imports that refusal.

**chousa — ids, not paths.** `SKILL.md:74` `verify-integrity` emits `REF_UNRESOLVED`. `SKILL.md:270-281`: tokens resolve against declared source/claim/sweep ids. Local paths, globs, and prose are not integrity tokens. `SKILL.md:386-387`: plain `verify` never opens the file a pointer names.

**kake — line drift after a rewrite, not missing files.** `SKILL.md:389-392` says `.ufo/waves/round-21/` pointer-audit helpers are evidence tools, not gates. `anchor-census.mjs:1-27` maps old `filename:line` ranges through a frozen base (`5009ecaa…`) with `git show <base>:<path>` and flags preservation violations. It does not test whether `census/`, `tests/`, `tools/`, `corpus/`, or `.ufo/waves/` tokens exist.

### Other hits, not path-existence checkers

- `game-dev-3d-shokunin/SKILL.md:47` — card CHECK 4, cited line is in range, content not read. No fleet entry named in the hit.
- `kama-shokunin/SKILL.md:376-379` — a dated pointer to an admission section.
- `kengaku-shokunin/SKILL.md:611` — “in-repo pointers” as a phrase.
- `kotodama-shokunin/SKILL.md:410` — missing/dangling *rows* in a law checker.
- `lore-shokunin/SKILL.md:90-93` — `dual_pointer` is a second pointer inside a map-obligation cell.
- `mado-shokunin/SKILL.md:1365-1368` — dangling theme symlinks. `:577` `fresh-pins.py` is a version-pin score.
- `mori-shokunin/SKILL.md:33` — a triage pointer for a non-fleet unit failure.
- `tabi-shokunin/SKILL.md` — residual and errata pointers (prose index). No resolver named in the hits.
- `tameshi-shokunin/SKILL.md:1827` — a waiver rev that is a dangling git object, not a cited path.
- `tsukuroi-shokunin/SKILL.md:1968` — `tools/check-recheck-commands.py` “pointer/direct command scope” is about recheck directives, not path tokens. Other hits are errata pointers.
- `souji-shokunin/SKILL.md:129` — the only `cat-file -e` in the sweep. It post-checks one quarantine commit: `git -C <repo> cat-file -e <landed>:<rel>` fails and `git -C <repo> cat-file -e <landed>:<qpath>` succeeds. Own lane, not another lane’s checker, and not a document scan. Souji’s `SKILL.md` does not already specify `LG-DANGLING-PTR`.

## Proposed move

Keep `LG-DANGLING-PTR` inside `tools/souji-landing-gate.py`. Do not shell out to `sources-census.sh`, `claim-ledger.sh`, `citation-drift-probe.py`, `verify_corpus_integrity.py`, or `verify_skill_checklist.py`.

For each token the C2 grammar keeps (prefixes `census/` `tests/` `tools/` `corpus/` `.ufo/waves/`; `:line` stripped; simple `{a,b}` expanded; tokens containing `<` `>` `*` or `round-N` skipped; `round-6..11` expanded):

1. Existence at the graded rev is `git -C <lane> cat-file -e <rev>:<path>` (exit 0 means the tree or blob is in that commit). Do not use `[ -e ]` and do not `git show` the bytes.
2. If that fails, a hit in the fleet repo is class `fleet` and is not a finding. Do not point `.ufo/` at `$lane/../.ufo` and then fail the run the way kagi `cite_target` does. Do not look the fleet path up at the lane’s rev: the fleet history is not souji’s `b576341`.
3. The only deliberate miss is a row in committed `corpus/pointer-exemptions.tsv`. A citing line that says “historical” or “removed” is still a finding when the row is absent. That is the falsifier against reusing kagi’s `MARK_RE`.

Apply the finding only when `--round` ≥ 18, so `census/round-17/gate-replays-expected.json` stays byte-identical.

This improves calibration: the before count at `b576341` and the after count at the round tip are properties of those trees, fleet-relative tokens stay non-findings, and unlabeled dangling paths stay findings. It does not harm operability: no sibling-repo process, no extra caller pipe, no jj `HEAD` policy imported from kaidoku. It does not harm coverage: the scan stays on C2’s file set. The imported checkers would shrink it (E11 sees only mined used-by cells; kotoba misses `census/` `tests/` `tools/`; kaidoku sees only table rows).

## Risks

- Vendoring kotoba `expand_braces` or kagi’s brace loop would expand a different set than C2’s “simple `{a,b}`” (kotoba sorts and expands multiple groups; kagi strips spaces inside one group). Implement the contract’s simple form only.
- `cat-file -e REV:path` succeeds for a tree as well as a blob. A directory token that is in the tree at `REV` is a resolution, which matches “resolve”. A token with `..` or an absolute path must be rejected before git sees it.
- A fleet existence check done with the lane rev, or with kagi’s “miss means UNRESOLVED”, reintroduces the false findings L1 already separated.
- Calling kaidoku’s probe would make a tampered or unpinned table exit 2 (`pointer_table_tampered` / `pointer_table_unpinned`) and would not enumerate prose tokens.

## Verification (not run here)

Fixture contrasts for L1, under `/var/tmp`, not against the live fleet:

- At `--rev b576341 --round 18`, `census/round-17/gate-replays-ddb7347.json` cited from an authority file is `LG-DANGLING-PTR`. The same relative path present only in the fleet repo is `fleet`, exit unchanged.
- A file present only in the worktree and absent at `--rev` is a finding. A file absent in the worktree and present at `--rev` is not.
- A citing line that contains `historical`, with no `corpus/pointer-exemptions.tsv` row, is still a finding.
- `--round 17` replays match `census/round-17/gate-replays-expected.json` with no new finding id.

## Commands

- `ls -1 /home/vgpnk/Projects/shokunin/*-shokunin/SKILL.md` — exit 2; 18 files listed; `audio-shokunin/SKILL.md`, `game-dev-2d-shokunin/SKILL.md`, `revenger-shokunin/SKILL.md` “No such file”.
- `ls -1d /home/vgpnk/Projects/shokunin/*-shokunin` — exit 0; 21 directories, including those three.
- Read `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (header, selftest line 136, `usedby_findings` 538–568).
- One content grep of each existing `SKILL.md` for `dangling|pointer|cat-file -e`. Follow-up reads/greps were only of files those hits name: `kagi-shokunin/corpus/claim-ledger.sh`, `kotoba-shokunin/verifiers/verify_skill_checklist.py`, `kotoba-shokunin/verifiers/verify_corpus_integrity.py`, `kaidoku-shokunin/.ufo/gates/citation-drift/citation-drift-probe.py`, `kake-shokunin/.ufo/waves/round-21/anchor-census.mjs`. A second grep of `game-dev-3d` and `souji` `SKILL.md` added no new candidate.
