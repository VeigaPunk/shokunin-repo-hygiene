# Round 23 — ScribeLog: two append-only LOG.md blocks

seat: `L1Souji23.ScribeLog` (scribe, leaf member — no subagent dispatch)
date: 2026-10-25
lane base: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (branch `master`, ahead=0 behind=0, measured)
delivery target: append the two blocks below to
`/home/vgpnk/Projects/shokunin/souji-shokunin/LOG.md` (append only; no existing line is edited)
contract: `.ufo/waves/round-23/preregistration.txt` (frozen before data)

## Status

STATUS: PASS — both blocks drafted from bytes read this run; every value the round has not
measured yet is a named placeholder (§ Placeholders), and one pre-data contradiction between the
assignment's file attribution and the receipt bytes is reported instead of silently resolved
(§ Findings 1). Only this report was written; no other lane file was touched.

Touched: `.ufo/waves/round-23/w1/ScribeLog.md` (this file) only. Not touched: `LOG.md` (the two
blocks are drafted here, not appended), `corpus/README.md`, `corpus/lessons/round-22.md`,
`corpus/QUALITY.md`, `census/**`, `tools/**`, the git index, the lane's jj state, the fleet root.
Gates: no round counter was executed by this seat — C1/C2/C3 values are placeholders, and the one
mechanical check I did run is a read-only simulation of the frozen K2 predicate over
`LOG.md` + both blocks (0 mismatches under either ground receipt; § Evidence E18). No commit, push,
delete, move or signal. Out of scope by assignment: the D1-D8 repairs themselves (other seats),
and the F2 premise defect, which is reported rather than fixed because the contract is frozen.

## Block 1 — correction entry (append after the filed `Round22 attempt2` block)

```
Round22 attempt2 — append-only correction entry (written by round 23)
=====================================================================
This block corrects the Round22 attempt2 entry above without rewriting it:
the filed bytes stay as landed (PROTOCOL: filed bytes are append-only), and
each superseded value is named here verbatim so the correction is traceable
to the exact token it replaces. Ground: corpus/lessons/round-22-verifier-
spotcheck.md §6 D3/D4/D5 (lines 193-199) plus the receipts named per item.

1. Declared-evidence base counts (D5). The entry above records the base
measurement as assertions=56 resolved=53 skipped=33 mismatches=3, citing
census/round-22/attempt2/declared-evidence-before.tsv. That tuple is
superseded by assertions=55 resolved=52 skipped=33 mismatches=3 — the counts
line of the pinned-instrument receipt
census/round-22/attempt2/declared-evidence-before-final.tsv (commit dd8a6b7;
instrument sha256 65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4,
recorded in census/round-22/attempt2/instrument-digests.txt). Reason: the
56/53 reading came from the pre-split scanner; the escaped-pipe split fix left
one class-B token inside a revision-named cell, so the same base revision
re-measured with the pinned instrument yields one assertion and one resolved
token fewer (.ufo/waves/round-22/attempt2/w1/DraftScorecard.md records both
readings side by side). Direction and endpoint are unaffected: mismatches=3 at
the base, 0 at the repaired tip, so this is a receipt-arithmetic correction,
not a re-scoring. SCORECARD.md:14 already quotes 55/52; the correction makes
LOG agree with SCORECARD and with the `-final` receipt, not the reverse.
Attribution note, because the two receipts disagree: the superseded 56/53
tuple is itself the counts line of declared-evidence-before.tsv, the receipt
the entry above cites; the corrected value comes from the later `-final`
receipt at the same base revision.

2. Slice tally (D4). The entry above says the 8-row register slice carries
"5 accepted with corrected quotes, 1 present, 1 refused (S123 wrong-source
citation), 1 unverifiable (S118 DOI 202 empty body)". Those two tallies are
superseded by the verdict column of
census/round-22/attempt2/slice-verdicts.tsv:
`1 present` and `1 refused` are superseded by 2 present and 0 refused.
The receipt reads 5 accepted, 2 present, 1 unverifiable, 0 refused. S123 is
accepted — its quote is verbatim in git-worktree(1) SYNOPSIS and only the
citation target was wrong — and S126 and S138 are the two present rows; no
row in the slice is refused. corpus/README.md carried the same pair and is
corrected by the same round-23 sweep (D4), because a correction sweeps every
mention.

3. C2 gate-counter digest (D3). The round-22 fleet report
/home/vgpnk/Projects/shokunin/.ufo/reports/round-22/souji.md:65 cites the gate
counter's digest as 5b8025a8… . That is the pre-9fcc4f7 sha256: at both
revisions the round measured (9301d98, 77d6595) and at this lane base
(1208bfb) tools/souji-gate-check.py is blob 63ac63b8 with sha256
d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d. The cited
5b8025a8… is superseded by <R23-GATE-DIGEST>, the digest the round-23 re-run
records for the tool at its measured revision, bound in a receipt that
tools/souji-receipt-run.py verify accepts. No re-run is claimed in this block.

4. Not corrected here, routed instead: D1 (uncommitted round-22 wave work),
D2 (no after-state receipt at the named revision), D6 (lesson Gate reject
reason), D7 (QUALITY criterion for M17/M22), D8 (stray backtick in the S118
slice row). Dispositions are in the Round23 entry below.
```

### Structural note for the L1 (load-bearing, not decoration)

The `=====` underline on the second line of Block 1 is what terminates the
`Round22 attempt2` section for the frozen C1/K2 predicate
(`tools/souji-record-agreement.py:47`, section end `^=====`). Keep it, and keep
Block 1 ahead of Block 2. Without it the correction's own `1 present` / `1 refused`
literals fall inside the scanned section, and K2's `later` rule (a strictly later
line must carry both `superseded by` and the stale token) can never be satisfied by
the line that carries the marker itself — the block would score uncorrectable
mismatches. See § Attack log A2.

## Block 2 — `Round23` entry (append after Block 1)

```
Round23 (fleet repository & workspace hygiene, 掃除)
=====================================================
Lane base 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd (branch master, ahead=0
behind=0); round tip <R23-TIP>. Contract frozen before data in
.ufo/waves/round-23/preregistration.txt. Axes: calibration (7, the lane's
lowest non-retired), operability (8), coverage (8); no axis may be harmed.
Inbound: corpus/lessons/round-22-verifier-spotcheck.md §6 (D1-D8) and §7.

Claims (frozen; the key set is code, not data).
C1 calibration — record agreement. One instrument,
tools/souji-record-agreement.py, re-derives the four routed bookkeeping
defects from receipts instead of declarations: K1 after-receipt binding (D2),
K2 superseded-number correction (D5), K3 slice tally (D4), K4 uncommitted
round work (D1). Target M_after = 0 while the do-nothing control at the base
reports M >= 1 (receipt census/round-23/records/agreement-control-base.tsv);
the fixture's cases 2-6 each demand a mismatch, so an always-zero emitter is
rejected (control FALSE-GREEN-REJECTED).
  before→after: <C1-BEFORE> → <C1-AFTER>
C2 operability — blob-bound receipts. tools/souji-receipt-run.py re-derives a
counter at a full durable revision and emits (rev, tool path, tool sha256 at
rev, command, rc, stdout); its verify refuses a receipt whose recorded tool
digest is not the committed blob at the named revision. This is D3's repair.
  before→after: <C2-BEFORE> → <C2-AFTER> bound receipts (target >= 4:
  declared-evidence before/after, gate-check before/after)
  refusal demonstration: verify on a receipt carrying the stale r22
  5b8025a8… digest exits nonzero with RECEIPT-TOOL-DIGEST-MISMATCH.
C3 coverage — one assimilation theme (F2 repository size census, read side),
2 entries, 3 registry rows: corpus/knowledge/repo-size-census-readonly.md and
corpus/knowledge/count-objects-garbage-semantics-r24.md. Every cited source
was re-opened by this lane on 2026-10-25 with a <=25-word located quote in the
entry's ## Gate (CORPUS rule 1; staged opened-dates prove nothing). Id
collision: the registry held 114 rows (max S114) and the staged package cites
S112-S114, which this lane's registry already spends, so adopted ids continue
at S115 with citations re-pointed by document.
  registry 114 → <C3-REGISTRY-AFTER> rows (target >= 117, 0 malformed,
  0 duplicate ids); gate-check entries=2 ok=2 fail=0 → <C3-GATE-RESULT>;
  /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
  /home/vgpnk/Projects/shokunin souji → exit <C3-CENSUS-RC>.
  Control committed before append: the staged rows appended as-is (staged ids
  S112-S114) must fail on duplicate id.
Premise note, pre-data and from committed bytes: corpus/README.md:40 still
reads "frontier, no entry" for F2, but README.md:64-68 supersedes that r12 row
and F2 already holds knowledge/git-repo-structure-readonly.md (S035-S037) plus
tools/souji-repo-structure.sh. The adopted entries' delta is therefore the
size read side (count-objects / gc garbage semantics), not F2's first entry;
the frozen claim is unchanged and this note is recorded so the LOG does not
restate a superseded README row as current.

Wave shape. One v1 wave under scripts/hyaku/ufo-wave-policy.json, dispatched
from .ufo/waves/round-23/w1-spec.json: 41 seats at spec time — 9 scout,
9 scribe, 9 reviewer, 4 critic, 3 executor, 2 revenger, 2 mutation-tester,
1 connector, 1 sentinel, 1 simplifier; dispatched tally
<R23-DISPATCHED-TALLY>. L1 holds the planner seat and is the only landing path
(scripts/hyaku/jj-lane.sh); leaf seats hold no subagent dispatch. No new
cleanup authority.

Routed-defect dispositions (corpus/lessons/round-22-verifier-spotcheck.md §6,
lines 189-205). Block 1 above carries the D3/D4/D5 corrections themselves.

- D1 — uncommitted round-22 wave work. The five modified seat reports and the
  two untracked evidence/impl-a/head-c9f1fe3.* files are committed (or
  reverted) by this round, and the "none uncommitted" claim is dropped.
  Artifact: .ufo/waves/round-22/attempt2/w1/** as listed by git status at
  <R23-TIP>; re-derived by RevD1 and by K4.
- D2 — no receipt binds the named revision. A run receipt for the C1
  after-state is committed at the revision SCORECARD names, and the report tip
  and SCORECARD's measured commit agree. Artifact:
  census/round-23/records/declared-evidence-after.tsv; re-derived by K1.
- D3 — stale gate digest and missing before receipt. The gate counter is
  re-run with the blob the tip holds, before and after receipts are committed,
  and the cited 5b8025a8… digest is replaced. Artifact:
  census/round-23/records/gate-check-before.tsv and -after.tsv, each carrying
  tool_sha256; re-derived by tools/souji-receipt-run.py verify.
- D4 — README slice tally. Every mention is swept to the receipt's 5 accepted,
  2 present, 0 refused, 1 unverifiable. Artifact: corpus/README.md; re-derived
  by K3 over corpus/README.md and corpus/lessons/round-22.md.
- D5 — superseded LOG numbers. Block 1 of this delivery is the append-only
  named correction; the filed occurrence stays. Artifact: LOG.md; re-derived
  by K2.
- D6 — lesson Gate reject reason. The overbroad "no new refusal semantics or
  field" reason for quarantine-staging-no-copy-r24 is replaced by the
  entry-level wording (entry budget plus the mv --no-copy fallback), naming
  the RENAME_EXCHANGE/RENAME_WHITEOUT delta the candidate does add. Artifact:
  corpus/lessons/round-22.md:337-340; checked by RevD6.
- D7 — no QUALITY criterion for M17/M22. A criterion row citing the lesson is
  appended after the current last row Q53, so the locator-heading defect and
  the overstated-novelty defect each have a captured-by. Artifact:
  corpus/QUALITY.md; checked by RevD7.
- D8 — stray backtick in the S118 slice row. The id cell loses the backtick
  copied from the register text; the count is unaffected. Artifact:
  census/round-22/attempt2/quarantine-slice:8; checked by RevD8.

Bounds (unchanged, carried). Certification OFF, K5 HELD, F5 reap and the
NAMESPACE_SHA256 holds unchanged. Write scope is this repo only: no deletion,
move, quarantine or classify-for-cleanup outside souji-shokunin/; .ufo/state/,
.ufo/watchdog.log, MANIFEST.json, the fleet scripts/ and templates/, sibling
lanes and the lane's jj state are never written. No history rewrite, no
credentials, no live /proc census, no operator-sweep contents read or staged.
Receipt runners stay read-only and materialize git archive under /var/tmp.
Landing goes only through scripts/hyaku/jj-lane.sh (lane) and fleet-commit.sh
(fleet report).
```

## Evidence

All commands read-only, run from `/home/vgpnk/Projects/shokunin/souji-shokunin` unless absolute.

| # | command | observed |
|---|---|---|
| E1 | `tail -1 census/round-22/attempt2/declared-evidence-before.tsv` | `assertions=56 resolved=53 skipped=33 mismatches=3` |
| E2 | `tail -1 census/round-22/attempt2/declared-evidence-before-final.tsv` | `assertions=55 resolved=52 skipped=33 mismatches=3` |
| E3 | `git log --format='%h %ad %s' -- census/round-22/attempt2/declared-evidence-before{,-final}.tsv` | `dd8a6b7` (…-final), `a211e4d` (plain) |
| E4 | `awk -F'\t' '!/^#/&&NF{print $2}' census/round-22/attempt2/slice-verdicts.tsv \| sort \| uniq -c` | 5 accepted, 2 present, 1 unverifiable, 0 refused |
| E5 | `grep -n "assertions=56" LOG.md` | only `LOG.md:1484`, and the tuple is wrapped: `1484 … -> assertions=56 resolved=53` / `1485 skipped=33 mismatches=3` |
| E6 | regex sweep of `LOG.md` lines 1471-1522 with `tools/souji-record-agreement.py:57` `COUNTS_RE` / `TALLY_RE` | 0 four-tuple matches, 4 tally matches: `5 accepted` (1508), `1 present` + `1 refused` (1509), `1 unverifiable` (1510) |
| E7 | `for r in 77d6595 9301d98 1208bfb; do git show $r:tools/souji-gate-check.py \| sha256sum; done` | all three `d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d`; `git ls-tree` → blob `63ac63b8` |
| E8 | `grep -n "5b8025a8\|d5ed0805" /home/vgpnk/Projects/shokunin/.ufo/reports/round-22/souji.md` | `65:  \`5b8025a8…\`: six frozen per-entry checks + slice-verdict completeness,` |
| E9 | `git status --porcelain \| wc -l` at `1208bfb` | 13 paths: 5 `M` + 2 `??` under `.ufo/waves/round-22/attempt2/w1/`, plus `?? .ufo/waves/round-23/`, `?? census/operator-sweep-20261019/`, `?? tools/__pycache__/`, `?? tools/souji-record-agreement.py` |
| E10 | `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ \| wc -l` | `0`; `ls census/round-23` → does not exist |
| E11 | `grep -cE '^\|S[0-9]{3,}' corpus/SOURCES.md` and max id | 114 rows, max `S114`; `ls corpus/knowledge` → 11 files, neither C3 entry present |
| E12 | `sed -n '8p' census/round-22/attempt2/quarantine-slice \| cat -A` | ` S118\`   the cited source could not be fetched, so no quote was checked $` |
| E13 | `sed -n '440,442p' corpus/README.md` | `5 accepted with corrected quotes, 1 present, 1 refused (wrong-source` / `citation), 1 unverifiable (unreachable DOI).` |
| E14 | `grep -nE "[0-9]+ (accepted\|present\|unverifiable\|refused)" corpus/lessons/round-22.md` | `355: … **0 refused**.` (lesson already correct) |
| E15 | `grep -nE '^\| Q[0-9]+' corpus/QUALITY.md \| tail -1` | `Q53` is the last criterion row |
| E16 | `python3 -c 'json.load(.ufo/waves/round-23/w1-spec.json)'` and `swarm-registry.json` | 41 items, 41 members; roles 9/9/9/4/3/2/2/1/1/1 |
| E17 | `git rev-list --left-right --count origin/master...HEAD`; `git rev-parse 1208bfb…` | `0 0`; base resolves to `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` |
| E18 | read-only simulation of `tools/souji-record-agreement.py` K2 (`START`/`END`/`COUNTS_RE`/`TALLY_RE`, `later` rule) over `LOG.md` + both drafted blocks, in memory, nothing written | scanned section = lines 1471-1523, occurrences = 4, mismatches = **0** under ground `before.tsv` (56/53) **and** under ground `before-final.tsv` (55/52); no `filed-occurrence-missing` |

## Findings

1. **The assignment's receipt attribution contradicts the bytes.** The assignment names
   `census/round-22/attempt2/declared-evidence-before.tsv` as the receipt holding the correct
   tuple; that file's counts line *is* the superseded one (E1). The corrected
   `assertions=55 resolved=52 skipped=33 mismatches=3` lives in
   `census/round-22/attempt2/declared-evidence-before-final.tsv` (E2, commit `dd8a6b7`, E3) and is
   already the value `SCORECARD.md:14` quotes. Block 1 cites the `-final` receipt and states the
   attribution conflict in-item rather than writing a self-contradictory correction
   (`56/53 … superseded by 56/53`). Location: `.ufo/waves/round-23/preregistration.txt` C1/K2 vs
   `census/round-22/attempt2/*.tsv`.
2. **K2's frozen ground receipt is the superseded receipt.**
   `tools/souji-record-agreement.py:48` pins `K2_RECEIPT = declared-evidence-before.tsv`, so the
   predicate treats `56/53` as correct and can never detect the `56/53 → 55/52` correction it was
   written for. Under K2 as frozen the correction is invisible; if the ground is re-pointed to the
   `-final` receipt pre-commit, Block 1's later line still satisfies it (it carries the marker and
   the exact stale tuple). Recorded as an ATTACK, not edited.
3. **K2 cannot see the D5 tuple at all in current bytes.** `LOG.md` hard-wraps at ~72 columns, so
   the four-tuple is split across lines 1484-1485 (E5) and `COUNTS_RE` (line 57, which requires one
   line) matches zero four-tuples in the section (E6). The only K2-visible defect today is the
   slice tally. A K2 result of `mismatches=0` therefore proves less than the claim's wording
   implies.
4. **The `=====` terminator in Block 1 is load-bearing.** See the structural note; without it the
   correction's own stale literals are scanned and the `later` rule is unsatisfiable for the last
   line carrying a marker (A2).
5. **The C3 premise cites a superseded README row.** `corpus/README.md:40` says F2 is "frontier, no
   entry"; `corpus/README.md:64-68` explicitly supersedes that row and F2 already holds
   `knowledge/git-repo-structure-readonly.md` (S035-S037). The frozen claim is not changed; Block 2
   carries a premise note so the permanent LOG does not restate a stale row. Location:
   `.ufo/waves/round-23/preregistration.txt` C3 vs `corpus/README.md:40,64-68`.
6. **D4 is still open at draft time.** `corpus/README.md:440-441` holds the stale
   `1 present` / `1 refused` pair (E13); the lesson is already correct (`corpus/lessons/round-22.md:355`,
   E14). K3 scans both records, so the README mention alone keeps C1 at `M >= 1`. Final check of
   this run: `git status` now lists `M corpus/README.md`, `?? census/round-23/` and
   `?? tools/souji-receipt-run.py`, so the D4/C1/C2 repairs are in flight in sibling seats; the
   finding describes the base bytes, and none of those paths was written by this seat.
7. **K4 will count the operator-owned untracked directory.** `corpus/pointer-exemptions.tsv` has no
   `uncommitted:`-prefixed row today, and `K4_EXEMPT_PREFIX` is `uncommitted:`
   (`tools/souji-record-agreement.py:51`), so `census/operator-sweep-20261019/` — which the same
   file already describes as operator-owned and never committed — is scored as uncommitted round
   work. Either an `uncommitted:` row is added for it or C1 cannot reach `M = 0` without touching an
   operator-owned path (forbidden). Same trap for `tools/__pycache__/`, created by running the
   round's own Python tools (E9).
8. **C2 started from zero and no round-23 receipt tree existed at base** (E10): `census/round-23/`
   was absent at `1208bfb`, so the K1 receipt `census/round-23/records/declared-evidence-after.tsv`
   and the control receipt `census/round-23/records/agreement-control-base.tsv` must be created by
   this round before any C1 after-data can be taken. Final check: `?? census/round-23/` now appears
   (sibling seats, in flight; not read by this seat after it appeared).
9. **The stale digest is stale at every revision the round can measure.** `5b8025a8…` is not the
   blob at `77d6595`, `9301d98`, or the r23 base `1208bfb` (E7); the committed digest file
   `census/round-22/attempt2/instrument-digests.txt` already records `d5ed0805…`, so the defect is
   confined to the fleet report text (E8).
10. **D1 is unchanged at draft time** (E9): the five modified and two untracked round-22 paths are
    still in the working tree at the lane base.

## Attack log

- **A1 — K2's ground receipt is the value it declares wrong.** Pinning `K2_RECEIPT` to
  `declared-evidence-before.tsv` (56/53) makes the D5 correction unfalsifiable in the direction that
  matters: an author who corrects LOG to the `-final` receipt still scores 0 mismatches only because
  the corrected value is never compared, while an author who leaves `56/53` also scores 0. The key
  is satisfiable by doing nothing about the tuple. Not edited (frozen after data); re-pointing
  `K2_RECEIPT` to `declared-evidence-before-final.tsv` would make the key bite, and Block 1 is
  written to satisfy either ground.
- **A2 — K2's `later` rule has no self-exemption, so the correction must live outside the scanned
  section.** `tools/souji-record-agreement.py:199-205` searches `range(i+1, len(lines))` for a line
  containing both the marker and the stale token. A line carrying the marker *and* the token it
  supersedes is itself a scanned occurrence needing a still-later line, so any correction block that
  sits inside the section and names a stale tally regresses. Consequence: the key is satisfied by
  block *placement*, not by block *content* — a block after a `=====` line scores the same whether
  it names the right tuple or invents one. The `filed-occurrence-missing` guard (lines 208-209) is
  the only content check left, and it is satisfied by the pre-existing section.
- **A3 — the K2 section-end rule makes the file's own wrapping load-bearing.** Because the section
  ends at the first `^=====` after the header underline, appending any block whose first `=====` line
  is its header underline silently truncates the scanned region. A future author can therefore
  shrink the scanned region (and any future mismatch with it) by choosing a heading style, with no
  mismatch raised. Not exploitable today (the scanned region already ends at EOF), but it is a
  placement lever, not a content predicate.

## Placeholders (L1 replaces every one before commit)

| token | where | what to substitute |
|---|---|---|
| `<R23-TIP>` | Block 2 header, D1 disposition, bounds | the round's full 40-hex tip revision |
| `<C1-BEFORE>` | Block 2 C1 | counts line `keys=K records=R occurrences=O mismatches=M` of `tools/souji-record-agreement.py --rev 1208bfb…` (the do-nothing control; expect `M >= 1`) |
| `<C1-AFTER>` | Block 2 C1 | the same counts line at `<R23-TIP>` (target `M = 0`) |
| `<C2-BEFORE>` | Block 2 C2 | bound-receipt count at the base — measured `0` this run (E10); confirm |
| `<C2-AFTER>` | Block 2 C2 | bound-receipt count at the tip (target `>= 4`) |
| `<R23-GATE-DIGEST>` | Block 1 item 3 | the `tool_sha256` the round-23 gate-check re-run records at its measured revision (r22 measured `d5ed0805…`) |
| `<C3-REGISTRY-AFTER>` | Block 2 C3 | `corpus/SOURCES.md` row count after the append (target `>= 117`) |
| `<C3-GATE-RESULT>` | Block 2 C3 | the gate-check counts line for the two entries (target `entries=2 ok=2 fail=0`) |
| `<C3-CENSUS-RC>` | Block 2 C3 | exit code of `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` (target `0`) |
| `<R23-DISPATCHED-TALLY>` | Block 2 wave shape | dispatched seat count from `.ufo/waves/round-23/w1/swarm-registry.json` at landing (41 members at draft time) |

## Tooling

No tool installed or upgraded; no `pacman` transaction attempted. Only `python3` (stdlib) and
`git` plumbing were used, both already present.
