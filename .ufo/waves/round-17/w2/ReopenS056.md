STATUS: DONE — S056's quote is verbatim and 21 words, but the anchor lines are wrong (v0.46.0 1439-1440, main 1508-1509) and the teaches cell claims a deletion symptom the page does not state; status/used-by are unsupported at ddb7347.

# ReopenS056 — independent re-open of the jj nested-repo changelog row

Question attacked: does the wave-1 S056 draft (`.ufo/waves/round-17/w1/SrcJjNestedRepo.md`) put a verbatim, ≤25-word quote at the anchor it names, and do its tier/status/scope/teaches cells claim no more than the served page states?

Re-opened independently on 2026-10-20: the assigned URL (`https://github.com/jj-vcs/jj/blob/main/CHANGELOG.md`), the raw file at the pinned tag v0.46.0, the blob HTML actually served at main, the GitHub release and commit API, the v0.46.0 `lib/src/local_working_copy.rs`, and the two `docs.jj-vcs.dev` pages the draft's version note names. No jj run; no lane script executed.

## 1. Version / "last updated" line served

| item | observed |
|---|---|
| Assigned URL | https://github.com/jj-vcs/jj/blob/main/CHANGELOG.md |
| Ref and commit served | `main`; `currentOid` 5176b1d8a3b0e569bb79b5e681c37874543ec617 (blob JSON `refInfo.currentOid`). API `commits/main` returns the same sha, committer date 2026-10-20T13:05:03Z, subject `index_store: move to core along with its dependencies`. |
| "last updated" line | None. The blob serves `Latest commit`, `History` and `main`; no `last updated` string. The file body's first version marker is `## [Unreleased]` (main line 9) whose `### Breaking changes` (lines 13-34) contains no sub-repo text. No `## [0.47...]` section exists. |
| Latest release | v0.46.0, published 2026-10-07T21:28:17Z (`api.github.com/repos/jj-vcs/jj/releases/latest`), matching `## [0.46.0] - 2026-10-07` at main line 90 and v0.46.0 line 21. |
| Version heading enclosing the quote | `## [0.36.0] - 2025-12-03`: v0.46.0 line 1389, main line 1458. `### Breaking changes` at v0.46.0 line 1410; the next heading `### Deprecations` is at 1442. |
| Raw bytes pinned | v0.46.0 `CHANGELOG.md` sha256 54ee00e57a9bdf652204f0f31458a62af0b39e42f3dbd54f8d547cb212719caf; main at the served OID sha256 c370eefe0637034150d5a09bc7622378e0b9726787d4dedc9454201a40053c68. |
| docs.jj-vcs.dev check | `/latest/working-copy/` (47,694 bytes): no version stamp, no `last updated`, no semver. `/latest/git-compatibility/` (61,334 bytes): no `last updated`; one prose hit `version 0.30.0 ) and this functionality can be turned off` (HTML line 2352). The draft's "no version stamp" claim holds. |

No `last updated` line is served for the changelog, so the defensible pin is the blob OID plus the release tag, which the draft does. The draft's `<25 words>` quote is pinned at v0.46.0, a stronger anchor than main and textually identical.

## 2. Primary quote: verbatim, word count, anchor

Draft quote (`SrcJjNestedRepo.md:13`), introduced at `:11` as "Primary (≤25 words; 21 words)":

> "Sub-repos are no longer tracked. Any directory containing `.jj` or `.git` is ignored. Note that Git submodules are unaffected by this."

Raw file at v0.46.0 (immutable tag), `nl -ba` lines 1439-1440:

```
1439 * Sub-repos are no longer tracked. Any directory containing `.jj` or `.git`
1440   is ignored. Note that Git submodules are unaffected by this.
```

Main at 5176b1d, lines 1508-1509: identical text.

- Character-exact except inline markup: joining the two raw lines with one space and stripping the list bullet equals the draft quote exactly (Python equality `True`). The rendered blob embeds the same two lines as one list item; the backticks are code-span markup. **PASS.**
- Word count: 21 (≤25). **PASS.**
- At the anchor it names: **FAIL.** The draft says `lines 1438-1439` (`:15` and row `:54`) and "main ... lines 1506-1508" (`:23`). Line 1438 is blank; the entry starts at 1439 and ends at 1440. v0.46.0 is an immutable tag, so this is not drift; at main's 5176b1d — the very OID the draft names — the entry is 1508-1509, not 1506-1508. The line-number derivation is off by one at the tag and by two at main.

Smallest fix: cite `1439-1440` for v0.46.0 and `1508-1509` for main at 5176b1d.

## 3. Cell verdicts

| cell | draft (row `SrcJjNestedRepo.md:54`) | verdict | corrected text |
|---|---|---|---|
| source | Jujutsu CHANGELOG, 0.36.0 Breaking changes — v0.46.0 URL | agree | unchanged |
| kind | docs | agree | unchanged |
| tier | A | agree | unchanged |
| scope | jj 0.36.0+ worktree snapshotting of a directory containing a `.git` or `.jj` entry (nested repository); not jj ref, bookmark or receipt semantics | partial — agree on the 0.36.0+ threshold, wording overreaches the page | jj 0.36.0+ tracking of a directory containing a `.git` or `.jj` entry (nested repository; sub-repos no longer tracked, Git submodules unaffected); not jj ref, bookmark or receipt semantics |
| anchor | CHANGELOG.md at tag v0.46.0 (published 2026-10-07) lines 1438-1439 ... implementation ... :822 and directory presence check at :1745-1756 | disagree — line numbers wrong, source range imprecise | CHANGELOG.md at tag v0.46.0 (published 2026-10-07T21:28:17Z) lines 1439-1440 (main at 5176b1d: 1508-1509), section `## [0.36.0] - 2025-12-03` (:1389) then `### Breaking changes` (:1410); implementation lib/src/local_working_copy.rs RESERVED_DIR_NAMES at :822, comment :1745-1751, presence loop :1753-1757 with `return Ok(None)` at :1755 |
| teaches | a directory merely containing `.git` or `.jj` is skipped whole, so tracked files beneath it snapshot as deleted and an empty fixture `.git` stub fakes deletions | disagree — the page states the rule and the submodule carve-out only; the deletion symptom is issue #8285 (tier C) plus a downstream inference, and the fixture consequence is lane context | a directory containing a `.git` or `.jj` entry is ignored whole (sub-repos no longer tracked) and Git submodules are unaffected; the snapshotter tests only name presence with `symlink_metadata().is_ok()` (:1753-1755) and returns `Ok(None)`, so an empty `.git` stub also triggers it |
| status | mined | disagree as landed-now | queued |
| opened | 2026-10-20 | agree | unchanged |
| recheck | on-release | agree | unchanged |
| used-by | corpus/lessons/round-17.md | disagree as landed-now | — (or the citing lesson path, in the commit that adds that lesson) |

### tier: agree, with a contract caveat
An official project changelog at a named tag is primary documentation; the registry's own precedent is S010 (Git release notes, `docs`, `A`) and S042-S050 (official docs, `A`). Caveat: `corpus/SOURCES.md:3-5` says tier definitions live in `SOURCES-CONTRACT-v1`, which is not present under `corpus/` (that directory holds `SOURCES.md`, `QUALITY.md`, `README.md`, `knowledge/`, `lessons/`). I judged A from the registry's precedent, not from the contract text.

### scope: partial
The 0.36.0+ threshold is supported: the entry sits under `## [0.36.0] - 2025-12-03` and no later revision appears anywhere in the served changelog (one `sub-repo` hit in the whole file, at main 1508; the Unreleased Breaking-changes block lines 13-34 has zero). But "snapshotting" is not page language — the page says "tracked"/"ignored". It is defensible only because the row's anchor already cites `local_working_copy.rs`; if scope is meant to describe what the page states, use "tracking". The exclusion clause is fine.

### anchor: disagree
Line 1438 is blank. The changelog entry is 1439-1440 at the tag and 1508-1509 at main's 5176b1d. The source range should name :1753-1757 for the presence loop (the comment rationale is :1745-1751; the `if`/`return` are :1754-1755; the loop closes at :1757). `RESERVED_DIR_NAMES` at :822 is correct.

### teaches: disagree
The page states exactly three things: sub-repos are no longer tracked; any directory containing `.jj` or `.git` is ignored; Git submodules are unaffected. It does **not** state that tracked files beneath such a directory report as deleted, and it does not mention empty stubs or fixtures. Those clauses come from issue #8285 (the draft itself labels it tier C) and from a downstream inference over `Ok(None)`. The row's anchor already includes the implementation, so the presence-only test is in scope; the deletion status is not. If L1 wants the symptom in the registry, add `jj issue #8285` to the anchor as tier-C corroboration, or keep the symptom in the round lesson, which already carries it. Do not leave it in the A row's teaches cell.

### status and used-by: disagree as landed-now
`corpus/lessons/round-17.md` is absent at ddb7347 (`git cat-file -e ddb7347:corpus/lessons/round-17.md` exits nonzero) and does not exist in the worktree either. The knowledge-entry draft `corpus/knowledge/jj-colocation-receipts.md` is untracked (16,253 bytes, 2026-10-20 13:35) and contains no S056, `CHANGELOG`, `0.36.0` or nested-repo citation (its only `.git`/`.jj` hits are the colocation definition at line 7 and doc quotes). So at the rev this row would land against, `mined` has no citing path.

Corrected: `queued` with `—`. The row may land as `mined` only in the commit that adds `corpus/lessons/round-17.md` (or a knowledge entry) citing S056; a lesson landed later would leave a dangling used-by.

The draft's parenthetical at `:57` — "the census fails a `mined` row whose used-by paths do not exist" — is **unverified**: `grep -n -E 'used-by|mined|SOURCES|tier'` over `tools/souji-census.sh` and `tools/souji-landing-gate.py` found no registry validation (the gate's "registry" is the SKILL.md script registry, `LG-PARSE-REG`/`LG-MISSING-REG`). If another script owns that check, name it; as written, status discipline here is editorial.

## 4. Corrected row (S056), full line

```
| S056 | Jujutsu CHANGELOG, 0.36.0 Breaking changes — https://github.com/jj-vcs/jj/blob/v0.46.0/CHANGELOG.md | docs | A | jj 0.36.0+ tracking of a directory containing a `.git` or `.jj` entry (nested repository; sub-repos no longer tracked, Git submodules unaffected); not jj ref, bookmark or receipt semantics | CHANGELOG.md at tag v0.46.0 (published 2026-10-07T21:28:17Z) lines 1439-1440 (main at 5176b1d: 1508-1509), section `## [0.36.0] - 2025-12-03` (:1389) then `### Breaking changes` (:1410); implementation lib/src/local_working_copy.rs RESERVED_DIR_NAMES at :822, comment :1745-1751, presence loop :1753-1757 with `return Ok(None)` at :1755 | a directory containing a `.git` or `.jj` entry is ignored whole (sub-repos no longer tracked) and Git submodules are unaffected; the snapshotter tests only name presence with `symlink_metadata().is_ok()` (:1753-1755) and returns `Ok(None)`, so an empty `.git` stub also triggers it | queued | 2026-10-20 | on-release | — |
```

Flip `queued`/`—` to `mined`/`corpus/lessons/round-17.md` only if that lesson is in the same landing commit and cites S056.

## 5. What holds, what does not, and remaining unknowns

Holds:
- The changelog text, its 0.36.0 Breaking-changes section, and the Git-submodule carve-out (verbatim at v0.46.0 1439-1440 and main 1508-1509).
- The presence-only implementation: `RESERVED_DIR_NAMES = [".git", ".jj"]` at :822; the directory branch returns `Ok(None)` when `symlink_metadata()` succeeds for either name (:1753-1757), so an empty `.git` directory qualifies.
- The version claim: latest release v0.46.0 (2026-10-07), served main at 5176b1d (2026-10-20), no later reversal in the served changelog.
- The docs.jj-vcs.dev pages serve no version stamp and no "last updated" line; the draft's note is accurate.

Does not hold as written:
- The anchor line numbers (both refs).
- The teaches deletion/fixture clauses under the A-tier page.
- `mined`/used-by at ddb7347 (no citing file exists).

Remaining unknowns:
- Whether L1 lands `corpus/lessons/round-17.md` in the same commit; that decides the status cell.
- The `SOURCES-CONTRACT-v1` text (tier A judged by registry precedent, not the contract).
- I did not run jj (probe rule), so I have no local reproduction of the deletion symptom; my finding is about what the title page states, and the symptom's direct evidence remains issue #8285, which I did not re-open.
- The draft's docs sweeps for a config knob were not re-run beyond the changelog; the "no opt-out" statement is the draft's, not mine.

## 6. Commands run (exact, with key output)

1. `curl -sSL -o /var/tmp/souji-r17-ReopenS056/CHANGELOG.md https://raw.githubusercontent.com/jj-vcs/jj/main/CHANGELOG.md` → 222721 bytes, sha256 c370eefe0637034150d5a09bc7622378e0b9726787d4dedc9454201a40053c68.
2. `curl -sSL -o .../CHANGELOG-v0.46.0.md https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/CHANGELOG.md` → sha256 54ee00e57a9bdf652204f0f31458a62af0b39e42f3dbd54f8d547cb212719caf.
3. `grep -n "Sub-repos" CHANGELOG.md CHANGELOG-v0.46.0.md` → main `1508`; v0.46.0 `1439`.
4. `nl -ba CHANGELOG-v0.46.0.md | sed -n '1437,1442p'` → `1438` blank, `1439` first line, `1440` continuation, `1442 ### Deprecations`. `nl -ba CHANGELOG.md | sed -n '1506,1511p'` → `1508` first line, `1509` continuation, `1511 ### Deprecations`.
5. Python equality test on the joined raw lines → `words: 21`, `exact-after-strip: True`.
6. `awk '/^## \[/{print NR": "$0}'` → v0.46.0 `1389: ## [0.36.0] - 2025-12-03`; main `1458: ## [0.36.0] - 2025-12-03`; `grep -c '^## \[0\.47' CHANGELOG.md` → 0.
7. `curl api.github.com/repos/jj-vcs/jj/releases/latest` → `v0.46.0 2026-10-07T21:28:17Z`; `.../commits/main` → `5176b1d8a3b0e569bb79b5e681c37874543ec617`, `2026-10-20T13:05:03Z`.
8. Blob HTML at main → `refInfo.currentOid 5176b1d8...`; `Latest commit` present, `last updated` absent; embedded markdown contains the quote's two exact lines.
9. `curl https://docs.jj-vcs.dev/latest/working-copy/` → 47,694 bytes, no `last updated`, no semver; `/latest/git-compatibility/` → 61,334 bytes, no `last updated`, one `0.30.0` prose hit.
10. `nl -ba lwc-v0.46.0.rs | sed -n '1745,1758p'` → comment 1745-1751, `let disk_dir` 1752, loop 1753-1757, `return Ok(None)` 1755; `grep -n RESERVED_DIR_NAMES` → `822`.
11. `git cat-file -e ddb7347:corpus/lessons/round-17.md` → nonzero (absent); `ls corpus/lessons/round-17.md` → No such file. `grep` in the untracked knowledge draft for `S05[0-9]|S056|CHANGELOG|0\.36\.0|Sub-repos` → no hits.
12. `sha256sum corpus/SOURCES.md` = `git show ddb7347:corpus/SOURCES.md | sha256sum` = b06834735866a1bd18a7d5e2bda7d578716b59543e0305ba65ce93f8ab2c45a4, so the SOURCES line citations are stable at ddb7347.
13. `grep -n -E 'corpus/SOURCES|registry|used_by|used-by' tools/souji-census.sh tools/souji-landing-gate.py` → only the landing gate's SKILL.md script-registry hits; no SOURCES used-by validation.
14. `grep -n -i -E 'sub-repo|subrepo|nested repo' CHANGELOG.md` → only line 1508; `sed -n '13,34p' CHANGELOG.md | grep -c -i ...` → 0.

## 7. Probe and tooling record

- Read only exact named files: the wave-1 draft, `corpus/SOURCES.md`, `corpus/QUALITY.md`, the untracked knowledge draft; read-only git (`cat-file`, `show`, `ls-tree`); web reads of github.com and docs.jj-vcs.dev; `sha256sum`, `nl`, `sed`, `awk`, `grep`, local `python3`. Wrote only `/var/tmp/souji-r17-ReopenS056/` (fetched copies) and this report.
- One probe note: a `glob` invocation with `path=/home/vgpnk/Projects/shokunin` and pattern `*SOURCES*` returned a names-only directory listing (200-result cap) instead of a match. No file contents were read from it and none of it was used as evidence; it is recorded here for the transcript audit.
- No tools installed or upgraded this seat; no network write; no jj and no lane script executed.
