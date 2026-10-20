# ReviewSources — round 13, W1 (S005/S006 usage semantics)

Seat: SoujiR13.ReviewSources (reviewer, leaf). Lane HEAD 31984f4. Review date 2026-10-20.
Write set: this file only. Read-only otherwise. No registry, knowledge, lesson or census file was written.
Tools installed or upgraded: none. Read-only commands: `zcat`/`grep`/`sed`/`awk` on installed man pages, `git --no-optional-locks -C … show HEAD:…`, `git --no-optional-locks -C … status --porcelain`, `test -e`, and reads of lane files.

## Verdict

1. **S005 teaches is truncated.** The cell ends `…lines and nul (-z) are` (`corpus/SOURCES.md:13`). The installed page cannot complete it: the `lines` and `nul` formats are described as key-value output with no stability or machine-readability statement (git-repo(1) roff :168-189).
2. **S006 teaches overstates the source.** It calls GIT_OPTIONAL_LOCKS "the doc basis for a read-only census" (`corpus/SOURCES.md:14`). The installed git(1) page never says "read-only" (zero matches in the GIT_OPTIONAL_LOCKS entry, roff :2195-2202). It says only that optional lock-taking sub-operations are skipped. Measured writers contradict any read-only reading (see §2).
3. **Contract rule 2 forbids fixing either teaches in place.** Only `status`, `recheck` and `used-by` may change in place. A correction is a new row whose teaches opens `supersedes S0NN —` (`.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:49-51`).
4. **The registry is already mutated before admission and without a log.** The working tree shows S005 and S006 flipped `queued → mined` with `used-by = corpus/knowledge/git-repo-structure-readonly.md` (mtime 02:12). The entry does not meet its own gate (§6). `corpus/lessons/round-13.md` does not exist, so the old→new change is unlogged. The draft's gate order (write entry, confirm path, then flip) was not followed. Revert to `queued` / `—` until the entry is admitted.
5. **S034 is contested.** SourceTimeout was asked to take S034 for `timeout` (`.ufo/waves/round-13/w1-dispatch.json`, task SourceTimeout). The new rows below need S035 and S036 unless the integrator orders them differently. Ids are next-unused at write time and never reused.

## 1. Binding rules (cited)

- Contract rule 1: a new row needs URL, access date, and a ≤25-word located quote grounding `teaches` (`SOURCES-CONTRACT-v1.md:45-48`). Recorded in the round lesson `## Gate`.
- Contract rule 2: in-place changes limited to `status`, `recheck`, `used-by`, each logged old→new in the round lesson (`:49-51`). `opened`, `anchor`, `teaches`, `tier`, `kind`, `source`, `scope` are immutable.
- `opened` is the row author's open date (`:38`). Re-opening today does not change it.
- Fleet validator (read, not run; `scripts/sources-census.sh`): E04 flags a repeated URL+scope unless `teaches` contains `supersedes S0NN` (:24-25, :647-649). E08 requires `opened` ≤ today. E11 requires every `mined` `used-by` path to exist (:566-567). W03 warns on `mined` with `—`.
- Contract census commands (`SOURCES-CONTRACT-v1.md:64-81`), copied as `census/round-12/sources-census.sh`.
- QUALITY: Q1 (verified-at names a version), Q2 (docs silent → committed fixture), Q4 (`/var/tmp` + trap), Q9 (`shellcheck -S warning`), Q13 (probe writes under `census/round-13/` or mktemp), Q17 (claimed fixture must resolve to a regular file), Q18 (integrity ≠ deletion authority). Q17 and Q18 were added to `corpus/QUALITY.md` during this round and cite `corpus/lessons/round-13.md`, which does not exist yet.

## 2. Source check against the installed pages (2026-10-20, git 2.55.0)

| row | claim | installed location | result |
|---|---|---|---|
| S005 anchor | § DESCRIPTION EXPERIMENTAL | git-repo.1.gz :44 `THIS COMMAND IS EXPERIMENTAL. THE BEHAVIOR MAY CHANGE.` | agrees |
| S005 teaches | five report kinds | :103-160 (reference counts, reachable counts, inflated size, disk size, largest objects) | agrees |
| S005 teaches | "not for machine parsing" | :166 `This format may change and is not intended for machine parsing.` (table only, the default) | agrees, but scope is the table only |
| S005 teaches | "lines and nul (-z) are" | :168-189 describe key-value output and NUL delimiting; no stability promise | **truncated; cannot be completed from source** |
| S006 anchor | § ENVIRONMENT GIT_OPTIONAL_LOCKS | `.SH "ENVIRONMENT VARIABLES"` at git.1.gz :1508; entry at :2195-2200 | **heading name wrong** (`ENVIRONMENT`, not `ENVIRONMENT VARIABLES`) |
| S006 anchor | § OPTIONS --no-optional-locks | `.SH "OPTIONS"` :52; flag at :285-288 "equivalent to setting GIT_OPTIONAL_LOCKS to 0" | agrees |
| S006 teaches | skips optional lock-taking work, e.g. index refresh | :2197-2200 `…without performing any optional sub-operations that require taking a lock. For example, this will prevent git status from refreshing the index as a side effect.` | agrees (quote ≤25 words: "without performing any optional sub-operations that require taking a lock") |
| S006 teaches | "doc basis for a read-only census" | no "read-only" or write statement in :2195-2202; git-status.1.gz BACKGROUND REFRESH :1113-1115 (`read-only` count 0) only advises `--no-optional-locks status` for background scripts | **overstated; not in source** |

Counter-evidence from the lane (measured, not doc):
- `census/round-10/S14-cluster-G.md:69-72`: `git diff --quiet <ref> -- <path>` creates `.git/index.lock` and rewrites `.git/index`; `GIT_OPTIONAL_LOCKS=0` does not suppress it.
- `census/round-10/seat-15.json:65`: four variants (plain, env `GIT_OPTIONAL_LOCKS=0`, `--no-optional-locks`, `--exit-code`) all WRITE.
- `census/round-12/postreview.md:18`: the `git repo structure` scratch run left `.git` unchanged in names, sizes and mtimes, with and without the variable. Lock-taking was not sampled.

Conclusion: no row, including a corrected S006, can ground "`git repo structure` is read-only". Under contract rule 5 a negative claim carries its own sweep. The only admissible basis is the isolated before/after manifest fixture (round-12 ART C3 flip condition, `corpus/lessons/round-12.md:133`).

## 3. Allowed in-place cells for S005 and S006

| cell | HEAD (`31984f4`) | working tree now | allowed in place? | recommended action |
|---|---|---|---|---|
| status | queued | mined | yes, only if `used-by` names an existing admitted entry that cites the row | revert to `queued` until admission; set `mined` only if the entry cites S005/S006 directly (see §5) |
| used-by | — | `corpus/knowledge/git-repo-structure-readonly.md` | yes | `—` if the entry cites S035/S036 instead; otherwise the admitted path |
| recheck | on-release | on-release | yes | keep |
| opened | 2026-10-19 | 2026-10-19 | **no** (draft row "opened → 2026-10-20" is not allowed) | keep 2026-10-19; record today's re-open in the round Gate |
| anchor | as above | as above | **no** | leave; S006 heading error goes into S036 |
| teaches | as above | as above | **no** (draft "PENDING proposed narrowing" in place is not allowed) | leave; correct via supersedes rows |
| tier, kind, scope, source | — | — | no | — |

Each in-place change must be logged old→new in `corpus/lessons/round-13.md` `## Gate`. That file does not exist; the 02:12 flip is unlogged.

## 4. Source row corrections (new rows; the integrator assigns ids)

Proposed rows, each with the same URL and scope as the row it supersedes, so E04 is exempt through `supersedes`. Tier A and kind `docs` as for the originals. Use no `|` inside cells. `opened` is the date the writer opens the source in round 13; this reviewer's re-read was 2026-10-20.

```
| S035 | git-repo(1) — https://git-scm.com/docs/git-repo | docs | A | git 2.55.0 git repo structure output and format stability | § DESCRIPTION (THIS COMMAND IS EXPERIMENTAL, :44); § COMMANDS structure, table format (:166); installed man page git 2.55.0-1 /usr/share/man/man1/git-repo.1.gz | supersedes S005 — EXPERIMENTAL command; structure reports reference and reachable-object counts, inflated and disk sizes, and largest objects by type; the default table is not intended for machine parsing; lines and nul are documented as key-value output with no stability statement | mined | 2026-10-20 | on-release | corpus/knowledge/<F2 entry>.md
| S036 | git(1) — https://git-scm.com/docs/git | docs | A | git 2.55.0 GIT_OPTIONAL_LOCKS scope | § OPTIONS --no-optional-locks (:285-288); § ENVIRONMENT VARIABLES › GIT_OPTIONAL_LOCKS (:2195-2200); installed man page git 2.55.0-1 /usr/share/man/man1/git.1.gz | supersedes S006 — GIT_OPTIONAL_LOCKS=0 or --no-optional-locks makes git skip optional sub-operations that take a lock, e.g. git status refreshing the index; the page makes no read-only claim for any command, so this row grounds lock scope only | mined | 2026-10-20 | on-release | corpus/knowledge/<F2 entry>.md
```

Quotes for the round Gate (rule 1): S035 `This format may change and is not intended for machine parsing.` (git-repo.1 :166); S036 `without performing any optional sub-operations that require taking a lock` (git.1 :2197-2198).

`<F2 entry>` is the admitted path. Both rows become `mined` only after that file exists (E11 and the census gate order).

The S034 timeout row is not reviewed here. If SourceTimeout's S034 is admitted, S035 and S036 shift only if another seat writes first. The integrator must serialize allocation.

## 5. Census accounting (before33 → after)

Baseline is HEAD, read with `git --no-optional-locks -C … show HEAD:corpus/SOURCES.md`: 33 rows, 0 malformed, A=29 B=3 C=1, mined=16 queued=15 rejected=2. This matches `corpus/lessons/round-12.md:375`. The stored `census/round-12/sources-census.txt` (mined=18 queued=13) is stale. Its input `census/round-12/sources-exec2.md:16` lists S024/S025 as mined, and HEAD has them queued after the postreview downgrade (`census/round-12/postreview.md` row 3).

| scenario | rows | A/B/C | mined | queued | rejected | status |
|---|---|---|---|---|---|---|
| HEAD baseline | 33 | 29/3/1 | 16 | 15 | 2 | verified (read-only) |
| working tree now | 33 | 29/3/1 | 18 | 13 | 2 | **non-compliant**: pre-admission, unlogged flip |
| recommended, S034 admitted and cited | 36 | 32/3/1 | 19 | 15 | 2 | S005/S006 back to queued; S035/S036 mined |
| recommended, S034 not admitted | 35 | 31/3/1 | 18 | 15 | 2 | |
| alternative: entry also cites S005/S006 | 36 | 32/3/1 | 21 | 13 | 2 | keeps superseded teaches reachable from the entry |
| draft as written (in-place teaches edits, no supersedes) | 34 | 30/3/1 | 18 | 14 | 2 | **not permitted** (rule 2) |

Limitation: the contract has no `superseded` status, so superseded rows still count as `queued` or `mined`. A contract change to add one is a kaika/operator decision and is not made here.

## 6. Findings on the new F2 entry (`corpus/knowledge/git-repo-structure-readonly.md`)

1. **Cites rows with defective teaches.** Its `source:` line cites S005/S006. After admission it should cite S035/S036.
2. **Q1 fails.** `verified-at: 2026-10-20` names no git version. The K2 precedent names one (`corpus/knowledge/git-grace-periods-and-expire-to.md:2`: "installed Git man pages 2.55.0; host git 2.55.0").
3. **Q17 fails.** The entry's recheck and body cite artifacts that are absent at review time (`test -e`): `tests/fixtures/r13-repo-structure.sh`, `tools/souji-repo-structure.sh`, `census/round-13/verification.json`. The entry cannot be admitted until they exist as regular, committed files.
4. **Line 9 "use `lines` or NUL format" for machine reading.** S005 does not say that. Mark it [INFERENCE] or ground it in the fixture's parse run. The "not intended for machine parsing" statement for the table is correct (:166).
5. **Line 11** ("`GIT_OPTIONAL_LOCKS=0` skips optional lock-taking operations; it is not a universal prohibition on filesystem writes") is correct and matches the page. Keep it.
6. **Line 25** ("deleting a worktree does not necessarily free corresponding object storage") has no citation. Ground it or mark [INFERENCE].
7. **File name `git-repo-structure-readonly.md`** asserts the property the entry bounds to one fixture and one host version. Rename before admission (candidate: `size-census-git-repo-structure.md`, the scribe's slug). Renaming updates S005/S006 `used-by` in place, which is allowed and must be logged.
8. **Fixture requirements (Q2, Q4, Q13).** `mktemp -d` under `/var/tmp` with a trap; `TMPDIR:-/tmp` absent; compare a content hash manifest of `.git` before and after (index, packed-refs, config, refs, objects dir listing), not names, sizes and mtimes only (the scratch run's method, `postreview.md:18`). State the bound: one host, git 2.55.0, no concurrent writer.
9. **Q3** applies to deletion mechanisms. The entry authorizes no deletion, so state Q3 as not applicable rather than leaving the failure-case section unscored.

## 7. Proposed checks for L1 (run after integration; not run here)

1. `git --no-optional-locks -C /home/vgpnk/Projects/shokunin/souji-shokunin show HEAD:corpus/SOURCES.md | <status histogram>` → `mined=16 queued=15 rejected=2`, 33 rows (baseline).
2. `bash census/round-12/sources-census.sh` from the lane root → row count, `0` malformed, tier and status lines per §5, empty duplicate and enum lines, no `missing:` lines.
3. `scripts/sources-census.sh validate --today 2026-10-20 --root /home/vgpnk/Projects/shokunin souji` → no E01-E11; W04 only if a scope differs; no W03.
4. `grep -oE '^\| S[0-9]+' corpus/SOURCES.md | sort | uniq -d` → empty.
5. Diff check: for S005 and S006, cells 2-7 and 9-11 unchanged from HEAD; only status and used-by differ.
6. Verbatim re-check of quotes: `zcat /usr/share/man/man1/git-repo.1.gz | grep -n 'not intended for machine parsing'` → line 166; `zcat /usr/share/man/man1/git.1.gz | grep -n 'optional sub'` → line 2197.
7. Entry: `test -f tests/fixtures/r13-repo-structure.sh` and `test -f tools/souji-repo-structure.sh`; `grep -c 'TMPDIR:-/tmp' <fixture>` → 0; `grep -c '/var/tmp' <fixture>` ≥ 1 (Q4); `shellcheck -S warning` on both (Q9).
8. Q1: `grep -n 'git 2\.55' corpus/knowledge/git-repo-structure-readonly.md` (or the renamed entry) returns the verified-at line.
9. Round log: `corpus/lessons/round-13.md` `## Gate` records the old→new cells (§3) and the quotes (§4).

## 8. Limitations

- No command was executed in the lane, so no fixture, validator or census output is observed here. Counts come from read-only `awk` over HEAD and the working tree, and from reading the validator source.
- The working tree is mid-edit by sibling seats (`M PROVINCE.md`, `SHONEN.md`, `corpus/QUALITY.md`, `corpus/SOURCES.md`; untracked `.ufo/`, `census/round-13/`, the entry file). Results describe both HEAD and the state at review time.
- Quotes come from the installed man pages (git 2.55.0-1). Live web pages were not re-fetched; the S005/S006 anchors name the installed page, so the revision is pinned.
- The S034 timeout row was not reviewed.
- The contract's lack of a `superseded` status is a standing gap (§5).
- The draft's claim that `census/round-12/sources-exec2.md:16` drives the stale census is verified in §5.
