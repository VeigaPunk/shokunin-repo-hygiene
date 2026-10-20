# round-13 SOURCES draft — S005/S006 cells, S034 candidate, census before/after

Status: DRAFT, not applied. Author seat: SoujiR13.SourceBookkeeping (scribe).
Scope: proposed cells only. `corpus/SOURCES.md` is NOT edited by this draft; integration is L1's.
Sources opened by this seat: none. Every quote below is a round-12 observation copied from
`census/round-12/sources-gate.md`, labelled as such. Round-13 opener reports (SourceRepo,
SourceLocks, SourceTimeout) are PENDING and must supply any new quote, access date and revision.

## 1. Baseline (before33)

Row count and tiers were counted by hand from `corpus/SOURCES.md` rows at lines 9-41 (ids S001-S033,
contiguous, no duplicates). These are NOT command output. L1 must confirm them with the census script.

| measure | value | basis |
|---|---|---|
| rows | 33 | S001-S033 at `corpus/SOURCES.md:9-41` |
| tiers | A=29 B=3 C=1 | B: S014, S017, S029; C: S030 |
| status | mined=16 queued=15 rejected=2 | manual count of status column: queued S005 S006 S007 S008 S011 S012 S013 S014 S015 S024 S025 S026 S027 S028 S033; rejected S030 S032 |

CONFLICT (must be resolved by L1 before any after-count is trusted):
`census/round-12/sources-census.txt:4` records `mined=18 queued=13 rejected=2`. Its input lists
S024 and S025 as mined (`census/round-12/sources-exec2.md:16` lists "S016–S025" under mined;
`:17` lists queued without S024/S025). The current registry rows `corpus/SOURCES.md:32-33` read
`queued`. The round-12 census file therefore predates the post-review status edits
(`census/round-12/postreview.md` row 3 says S025's quote is unverified). Treat `sources-census.txt`
as stale. `census/round-12/sources-census.sh:10` is the status histogram that must be re-run.

## 2. Permitted in-place cell changes for S005 and S006 (conditional on F2 admission)

Gate order is fixed: (a) write the F2 entry file, (b) confirm its path exists, (c) flip the cells.
Reversing the order makes the mined-path check fail: `census/round-12/sources-census.sh:16` prints
`missing: <path>` for any mined row whose used-by path does not exist.

| row | cell | old (current) | new if F2 entry admitted | gate |
|---|---|---|---|---|
| S005 (`corpus/SOURCES.md:13`) | status | queued | mined | F2 entry exists and cites S005 |
| S005 | used-by | `—` | `corpus/knowledge/size-census-git-repo-structure.md` (slug taken from ART C3 id `size-census-git-repo-structure`, cited at `corpus/lessons/round-12.md:133`; PROPOSED, to-verify against the entry L1 admits) | file exists |
| S005 | opened | 2026-10-19 | 2026-10-20 only if SourceRepo records a fresh access; otherwise unchanged | SourceRepo report |
| S005 | recheck | on-release | unchanged | — |
| S005 | anchor, teaches | see `corpus/SOURCES.md:13` | unchanged unless SourceRepo shows an anchor or teaches error; any correction must name the line it replaces | SourceRepo report |
| S006 (`corpus/SOURCES.md:14`) | status | queued | mined | same as S005 |
| S006 | used-by | `—` | same path as S005 | same as S005 |
| S006 | opened | 2026-10-19 | 2026-10-20 only if SourceLocks records a fresh access | SourceLocks report |
| S006 | teaches | "…the doc basis for a read-only census (cf. git-status § BACKGROUND REFRESH)" | PENDING. Proposed narrowing: the docs describe skipping optional lock-taking; "read-only" is not a documented claim. Round-12 quote supports only index refresh: "this will prevent git status from refreshing the index as a side effect" (`census/round-12/sources-gate.md:41`, S006 roff :2195-2200). [INFERENCE that the "read-only" wording overstates; SourceLocks must confirm] | SourceLocks report |

Old→new accounting for the census: mined +2, queued -2. The F2 entry requires a `used-by` path, so
it cannot add a row by itself; it only grows the used-by count.

If F2 is NOT admitted (held or rejected): S005 and S006 stay queued, used-by stays `—`, and no
cell changes. The draft then yields no change for S005/S006.

## 3. S034 candidate row (timeout only; PENDING SourceTimeout opener report)

SourceTimeout was asked to recommend S034 for GNU `timeout` only (`.ufo/waves/round-13/w1-dispatch.json`,
task SourceTimeout). S034 is the next unused id; S033 is the registry maximum (`corpus/SOURCES.md:41`).
Q8 requires `timeout` wrapping of per-target mv/digest steps (`corpus/QUALITY.md:32`), so S034 would
ground Q8 rather than the F2 entry.

Proposed row. Every PENDING cell must be filled from the opener report before the census is run.
The census rejects a non-letter tier (`census/round-12/sources-census.sh:14`), so an unfilled cell fails closed.

```
| S034 | GNU coreutils manual, timeout invocation — https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html | docs | A | PENDING | PENDING | PENDING | queued | 2026-10-20 | on-release | — |
```

Notes:
- Tier A is PROPOSED on the same basis as the other coreutils docs rows S024/S025 (`corpus/SOURCES.md:32-33`).
- Status `queued` is proposed because no entry uses S034 yet. Flipping to `mined` requires a used-by
  path that exists (the Q8-fixing tool or a knowledge entry), per the census mined-path check.
- S025 (GNU mv manual) was not fetched in r12 (`census/round-12/postreview.md` row 3, gnu.org unreachable).
  S034 may hit the same host. The opener report must record the fetch outcome; if the page is
  unreachable, S034 must not be admitted with a quote. It stays out of the registry.

## 4. Expected census after the wave (after34)

Computed by arithmetic from section 1 and 2. Not run.

| scenario | rows | malformed | tiers | mined | queued | rejected | sum check |
|---|---|---|---|---|---|---|---|
| registry baseline (manual count), F2 admitted, S034 admitted as A/queued | 34 | 0 | A=30 B=3 C=1 | 18 | 14 | 2 | 34 |
| registry baseline, F2 admitted, S034 NOT admitted | 33 | 0 | A=29 B=3 C=1 | 18 | 13 | 2 | 33 |
| registry baseline, F2 NOT admitted, S034 admitted | 34 | 0 | A=30 B=3 C=1 | 16 | 16 | 2 | 34 |
| stale r12 census baseline (`census/round-12/sources-census.txt`), F2 + S034 admitted | 34 | 0 | A=30 B=3 C=1 | 20 | 12 | 2 | 34 |

The first row is the target expectation (before33 → after34). It holds only if the registry baseline
in section 1 is confirmed. The stale-baseline row is shown only to make the S024/S025 conflict visible.

Tier note: S034 is counted as A. If the opener gives a different tier, the tier column changes and
the rejected/queued columns do not.

## 5. Search log (draft; counts PENDING opener reports)

- Question: does any opened source ground an F2 entry (size census of `git repo structure`) that the
  round-12 reject (ART C3, `corpus/lessons/round-12.md:133`) left open? The round-12 flip condition is
  "a /var/tmp fixture diffing `find .git -newer` around a `GIT_OPTIONAL_LOCKS=0 git repo structure` run".
  The source question is whether S005 (format and EXPERIMENTAL status) and S006 (GIT_OPTIONAL_LOCKS scope)
  support that claim.
- Bounded sources: S005 = git-repo(1), S006 = git(1), both installed man pages at git 2.55.0 (scope
  column, `corpus/SOURCES.md:13-14`). S034 candidate = GNU coreutils timeout docs, one page.
  Installed-man-page route only; no other site was searched in this draft.
- Identified: PENDING. Screened: PENDING. Included: PENDING. Excluded: PENDING.
  The count and its command must be recorded with the opener report (fleet floor: "a count carries its
  command", `corpus/QUALITY.md:9`).
- Inclusion rule: a row is admitted only with a located quote from an opened report in this round.
  Quotes are not added in this draft. Round-12 quotes in `census/round-12/sources-gate.md:34-42` may be
  cited only as round-12 observations.
- Negative claims: any "no source documents write behaviour" claim needs its own bounded sweep. None is made here.

## 6. Final checks for L1 (run after integration, not by this seat)

Run from the lane root, `cwd` = `/home/vgpnk/Projects/shokunin/souji-shokunin`:

1. `bash census/round-12/sources-census.sh` → expect lines: `34`, `0`, tier line with `A=30 B=3 C=1`,
   status line `mined=18 queued=14 rejected=2` (target scenario). Empty output lines 5-7 required.
   Any `missing:` line blocks admission.
2. `grep -nE '^\| S0(05|06|34) ' corpus/SOURCES.md` → confirm S005/S006 used-by equals the admitted entry path,
   and S034 row has no `PENDING` (`grep -c PENDING corpus/SOURCES.md` → 0).
3. `test -e corpus/knowledge/size-census-git-repo-structure.md` (or the slug actually admitted) → exit 0
   before flipping S005/S006 to mined.
4. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat -- corpus/SOURCES.md` → only rows S005, S006, S034
   (plus the Paths/Search-log bookkeeping L1 chooses to add) change.
5. Reconcile the stale `census/round-12/sources-census.txt` against a fresh run. Do NOT overwrite
   round-12 evidence; write any new census output under `census/round-13/`.

## 7. Limitations

- No source was opened by this seat. Every quote is a round-12 observation.
- Baseline counts are by hand; section 1 conflicts with the stored census file and is unresolved.
- The F2 slug is proposed, not admitted. The `used-by` path depends on what L1 and the entry author choose.
- No registry (`.ufo/waves/round-13/w1/swarm-registry.json`) or shared bookkeeping was written.
- Git HEAD assumed to be 31984f4 per the lane context; not checked by this seat.
