# Round 71 — filter-driver and core.fileMode witness hardening in the receipt writer (C1 operability), counter self-check of the r70 survivors (C2 calibration)

Attempt 1. Lane base `8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0` (r70 admitted). Freeze
`aa91d1cad89200ec733edd3475461010a372923d` (`census/round-71/preregistration.txt`, controls and
probe committed in the same commit, all executed before it). Candidate writer
`a1db6c8514771c0a0321c29741831606d09cc2a5`. After-arms `52e8c3faf678b0f3d2f18cc6d41a365dc91123f7`.
Frozen claims, counters and predicates are in the preregistration and are not restated here.

## Measured

- C1: `census/round-71/records/c1-after.txt` — `SUMMARY matrix=70 base_forgeries=7 base_honest=19
  new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS`, `EXIT=0`
  (before, `controls/c1-do-nothing.txt`: `new_forgeries=7 new_honest=19 class_mismatches=7`,
  `EXIT=1`). Forgery controls stay red: F1 blanket refusal `new_honest=16`, F2 attr-source scrub only
  `new_forgeries=5`, F3 fileMode pin only `new_forgeries=5`, all `EXIT=1`.
- C2: `census/round-71/records/c2-after.txt` — `SUMMARY label=c2-after-r71 positive_selftest=PASS
  x_mutants=5 x_killed=5 x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0`, `EXIT=0`
  (before, `controls/c2-before-r70.txt`: the frozen r70 counter, X6-X10 all survived, `score=5`,
  `EXIT=1`). The always-failing counter CF1 is refused as invalid (`EXIT=2`).
- Selftests: writer `records/writer-selftest.txt` `SELFTEST cases=40 pass=40 fail=0` at `a1db6c85`;
  counter `records/counter-selftest.txt` `SELFTEST cases=39 pass=39 fail=0` (rev `aa91d1ca`).
- Probe durability: the size-changing first form of the pre-freeze probe was re-run after the freeze
  and committed (`probes/attr-filemode-probe-sizechange.txt`): with `counter FORGED` every filter
  route is refused by the base writer (stat size check) while the core.fileMode routes P6/P7 still
  forge; the size-preserving form is `probes/attr-filemode-probe-base.txt`.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | false closure in a knowledge entry (mined from r67): an unmeasured scope was written as closed by a mechanism that cannot reach it — `corpus/knowledge/common-dir-route-receipt-writer.md:41` says a repository-local `core.fileMode` is "pinned away by `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM` on every call"; those pins reach only the global and system scopes | `census/round-71/controls/c1-do-nothing.txt` rows FM1/FM2 `base=accept` (receipt written over a pre-run and an in-run mode flip at the round base); probe P6/P7 in `probes/attr-filemode-probe-base.txt` | none (the r68 PK4/PK7 rows inject only global/system config files; no row set a repository-local key) | rows FM1/FM2/FMh in the frozen r71 matrix and the writer's `-c core.fileMode=true` pin; shown able to fail: the do-nothing control and control F2 (no pin) both forge FM1/FM2 (`EXIT=1`); correction appended to the entry (the original line is not edited) |
| M2 | self-assessment copied from a superseded receipt (r70 routed D1): `SCORECARD.md:181` says `pointer-check-r69.txt (5 missing, EXIT=1)`; the committed receipt reads `missing=8` | `census/round-70/records/pointer-check-r69.txt` at `3b7cce81` (`SUMMARY files=2 checked=59 missing=8`); r70 spot-check D1 | none (the pointer check resolves paths, not the numbers quoted beside them) | correction appended to SCORECARD (r71 section); not a check — no fix shown able to fail for this class this round, so the class stays open |
| M3 | evidence durability (this round): the pre-freeze probe's decisive first run (size-changing bytes, every filter row visible) was overwritten by the second run, so the preregistration's "a size change is caught by the stat check" rested on prose | `census/round-71/preregistration.txt` probe paragraph (freeze `aa91d1ca`) | none at freeze | the first form re-run and committed post-freeze as `probes/attr-filemode-probe-sizechange.txt`, labelled post-freeze; rule kept for next round: a probe whose run changes design is committed per run, never overwritten |
| M4 | claim prose wider than its counter (this round): the preregistration's C1 sentence "the clean-tree witness is not forgeable through a clean filter driver" covered routes the frozen 70-row matrix never exercised; the wave forged the frozen candidate three ways in that class (a driver named `set`, S71Reviewer F1; an in-run filter that deletes its own attribute while the post-run status read runs it, S71Sentinel HIGH-1; `ident`, S71CriticClaims HIGH) plus a stat route (core.checkStat/trustctime, S71Sentinel HIGH-2) | `census/round-71/records/wave-w1/seats/S71Reviewer.md`, `S71Sentinel.md`, `S71CriticClaims.md`; candidate `a1db6c85` | none (prereg named limits listed attr.tree, core.attributesFile, process drivers and in-run creation, not these) | writer repairs `45a94c83`, `f13d575e` with selftest cases 41-42; shown able to fail: each repair reverted alone fails its case (`census/round-71/records/repair-canfail.txt`: R1, R2, R3a, R3b, R4 each `fail=1`; repaired `cases=42 pass=42`); the frozen counter at the repaired tip still prints the frozen SUMMARY (`records/c1-at-repair.txt`, EXIT=0). Rule kept: a claim sentence names exactly the matrix routes; anything wider is a named limit |

## Gate

Sources opened this round (`census/round-71/srcs/`, fetched 2026-11-06, HTTP 200; quotes located in
the tag-stripped whitespace-normalized text `*.txt` at the offsets cited in the rows):

- **S306 admit (A, mined)** — https://git-scm.com/docs/gitattributes, sha256 `0a1e8015…6aee`,
  131046 bytes, offset 17513: "Similarly, the clean command is used to convert the contents of
  worktree file upon checkin." (15 words). Grounds the clean-filter route.
- **S307 admit (A, mined)** — https://git-scm.com/docs/git OPTIONS `--attr-source`, sha256
  `534c674f…f9d1` (byte-identical to the r70 S304 capture), offset 13322: "Read gitattributes from
  <tree-ish> instead of the worktree. See gitattributes[5] . This is equivalent to setting the
  GIT_ATTR_SOURCE environment variable." (20 words).
- **S308 admit (A, mined)** — https://git-scm.com/docs/git-config, sha256 `37aa8407…9226`, 830605
  bytes, offset 82016: "core.fileMode Tells Git if the executable bit of files in the working tree
  is to be honored." (17 words).
- **S309 reject (row kept)** — git(1) ENVIRONMENT `GIT_ATTR_SOURCE`, offset 40119: "GIT_ATTR_SOURCE
  Sets the treeish that gitattributes will be read from." It names the tree but not that it replaces
  the worktree attributes; S307 is the located ground. Flip: a release adds that sentence.
- **S310 queued** — git-config(1) `attr.tree`, offset 53875: "attr.tree A reference to a tree in the
  repository from which to read attributes, instead of the .gitattributes file in the working tree."
  (23 words). A third attribute route; no row measures it, so it is not mined.
- Considered, not appended: gitattributes(5) `text`/`eol` conversion as a forgery ground — the probe
  (P1) shows a CRLF rewrite changes size and is reported, so it grounds no claim.

**Status changes (old → new).** Rows 228 → 234 (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`). No pre-r71 row changed. Within the round, after the wave: S306 `teaches` narrowed to the check-in sentence (the status consequence is the probe's, S71CriticDiscern/S71ScoutSources); S307 `teaches` qualified (`info/attributes` survives GIT_ATTR_SOURCE); S309 reject reason old "names the tree but not that it replaces …; flip: a release adds that sentence" → new "duplicate anchor of S307 on the same page; flip: the OPTIONS entry loses that sentence" (S71ScoutSources); S310 `status` queued → mined, `recheck` 90d → 180d, `used-by` `corpus/lessons/round-71.md` → `corpus/knowledge/filter-filemode-witness.md`, anchor re-quoted to the precedence sentence at offset 54097 (S71CriticDiscern, S71ScoutSources: attr.tree measured — the round-start writer forges over it, the candidate refuses); S311 (gitattributes(5) `ident`, offset 17004, 21 words) added, mined. Offsets in S306-S311 are character offsets into the committed `srcs/*.txt` (S71ScoutSources LOW).

**Assimilation: none.** `considerthese/` is absent in this lane; `grep -ril
'gitattributes\|fileMode\|clean filter' /home/vgpnk/Projects/shokuknow/merge/souji/` → 0 files, so no
theme fits this round's claims.

## Routed (r70 spot-check D1-D5 and lesson round-70.md:78)

- D1 → M2 correction (SCORECARD r71 section). D2 → erratum appended to `corpus/lessons/round-70.md`.
- D3 → closed: `tools/souji-pointer-check.py --selftest` (see Wave); SKILL.md gate row added.
- D4 (a) F1 filter attribute / GIT_ATTR_SOURCE → C1. (b) F2 core.fileMode → C1. (c) F3/F4/F5 →
  counter `verify_members` name/symlink checks and harness label check (selftest (8e); harness
  `LABEL_RE`). (d) X7/X8 → C2 (selftest kills both); the counter's rc still does not bind
  `base_forgeries`/`base_honest` (named limit, unchanged). NOGLOB scrub row: not built (open).
- D5 → the wave context carries an explicit empty-variable / toplevel guard for fixture repos.

## Wave

One v1 wave `w1`, 12 seats (connector 1, scout 1, executor 3, mutation-tester 2, reviewer 1, critic 2, sentinel 1, scribe 1; attack seats reviewer+critic×2+mutation-tester×2 = 5 of 12). All 12 settled with output; dead seats 0 (`census/round-71/records/wave-w1/w1-results.json`). Seat evidence is mirrored byte-for-byte to `census/round-71/records/wave-w1/seats/` (the scout's final output, which it did not write to its report path, is `S71ScoutSources-final-output.txt`).

- Reproduced byte-for-byte: C1 (S71ExecC1 5/5 runs, S71Connector, S71Reviewer, S71CriticClaims, S71ScoutSources) and C2 (S71ExecC2, S71Connector, S71Reviewer, S71ScoutSources); X6-X10 edits reproduce the r70 seat mutants 5/5 (S71ExecC2, S71MutCounter).
- Verdicts: S71CriticClaims C1 STANDS on the predicate, QUALIFIED as a claim (ident route; the predicate accepts any design that emits the frozen class; honest repos with a configured driver are over-refused); C2 STANDS, QUALIFIED (mutant-set-specific; calibration by r70 precedent).
- Repaired this round (outside the frozen claims; M4): driver named `set`/`unset`/`unspecified` (S71Reviewer F1), post-run order (S71Sentinel HIGH-1), stat pins (S71Sentinel HIGH-2), ident/working-tree-encoding (S71CriticClaims HIGH). Measured residual: same-second in-place edit (`probes/stat-granularity-probe.txt`).
- D3 closed: S71ExecPointer's `--selftest` adopted into `tools/souji-pointer-check.py` (`records/pointer-check-selftest.txt`: 4/4; mutants M1 `fail=2`, M2 `fail=1`).

**Routed to round 72 (not repaired; the counter and harness are frozen).** (a) HIGH S71MutCounter F1/S71Scribe: `claim_upheld` still ignores the base slot — mutants Y6/Y10 (size-changing forgery, non-reversing filter) drop `base_forgeries` 7 → 2 with EXIT=0. (b) HIGH S71MutCounter F2: AS1/AS2 cannot tell a GIT_ATTR_SOURCE scrub from an unfiltered dirty tree (Y4 survives). (c) MEDIUM S71MutCounter F3/F4: no selftest pins FORGED_SAMESIZE/FILTER_CLEAN/chmod_notes; Y1/Y9 (half of the member-name check) survive. (d) HIGH S71MutWriter W8: no row pins that check-attr reads worktree attributes (`--cached` mutant survives); W3/W4/W5/W6/W7 survive the matrix (in-run, process and failure paths are selftest-only or unmeasured). (e) MEDIUM S71CriticClaims: over-refusal of an honest repo with a configured driver on a tracked path — needs a row and an operator view on LFS-like repos. (f) LOW harness: no TMPDIR check, uncaught timeout, symlinked label dir (S71Reviewer F2/F3); dead `CLASS_*` constants (S71MutCounter F5); receipts' `rev=` has three referents (S71Scribe). (g) open from r70: NOGLOB row, battery regeneration, case 38 independence, r69 D5 items (S71Scribe table). (h) Cross-lane, documented only: S71Connector lists 13 sibling clean-tree gates (kaidoku, kama, mori, tameshi, audio) that neither scrub GIT_ATTR_SOURCE, pin core.fileMode nor check filter drivers.
