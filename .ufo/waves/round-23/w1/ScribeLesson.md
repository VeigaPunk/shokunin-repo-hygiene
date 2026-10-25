## Status

STATUS: PARTIAL — draft only. The lesson body is written from committed bytes at lane base
`1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` and three sources opened live this run. No C1, C2 or C3
counter has been run by this seat, so every measured number is a named placeholder (listed below);
`corpus/lessons/` was not edited. Seven findings and two C3 attacks are recorded; the C3 premise and
the C3 counter command are the two the L1 must rule on before that claim can land.

## Evidence

Read-only, absolute paths, no writes outside this report.

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`
  (matches the prereg's lane base).
- `git status --porcelain` (lane, this run) → `M` on five r22 wave files
  (`.ufo/waves/round-22/attempt2/w1/{CritC1Axis,DraftScorecard,ImplDeclaredA}.md`,
  `…/w1/evidence/{CritC1Axis,DraftScorecard}.md`) and `??` on
  `…/w1/evidence/impl-a/head-c9f1fe3.{counts,tsv}`, plus `?? .ufo/waves/round-23/`,
  `?? census/operator-sweep-20261019/`, `?? tools/souji-record-agreement.py`. The D1 leftovers are
  still uncommitted at this round's base.
- `git grep -n 'resolved=63' 77d659524c777276bcef33568be3c4cbcb9d1052` → exactly one hit,
  `SCORECARD.md:14`; that line names tip `9301d98c1c689c79741f0f1ba1f171138d20af07` with
  `assertions=63 resolved=63 skipped=40 mismatches=0`.
- `git rev-parse <rev>:tools/souji-gate-check.py` → `c9f1fe3` and `8680755` both `f26aa72855e3…`;
  `9fcc4f7` and `77d6595` both `63ac63b8e481…`. The r22 after-run's tool blob is not the tip's.
- `cat census/round-22/attempt2/slice-verdicts.tsv` → 8 rows: 5 `accepted`, 2 `present`
  (S126, S138), 1 `unverifiable` (S118), 0 `refused`.
- `sed -n '440,441p' corpus/README.md` → "5 accepted with corrected quotes, 1 present, 1 refused
  (wrong-source citation), 1 unverifiable (unreachable DOI)".
- `grep -n 'assertions=56' LOG.md` → `1484`; `grep -n 'superseded by' LOG.md` → no match;
  `grep -n '1 present, 1 refused' LOG.md` → `1509`.
- `grep -n 'RENAME_EXCHANGE' /home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r24.md`
  → lines 24–25 (`RENAME_EXCHANGE` atomic two-path swap, `RENAME_WHITEOUT`).
- `grep -n 'F2' corpus/README.md` → line 40 `| F2 repository size census | frontier, no entry …`,
  but line 64 heads `## Round 13 current coverage (supersedes the r12 F2 row)` and line 68 already
  lists `knowledge/git-repo-structure-readonly.md` (S035/S036/S037) as F2's entry.
- `git log --oneline 4edb25dfe262515d0da63224bbba71e02e36cba5..77d659524c777276bcef33568be3c4cbcb9d1052 -- corpus/QUALITY.md`
  → no output (QUALITY.md unchanged base→tip, so r22's `captured-by: none` rows added no criterion).
- `python3 -B tools/souji-gate-check.py --help` → usage lists `--root --round-date --entries
  --snapshot-dir --slice --slice-verdicts --selftest`; no `--expect-slice`.
- Opened live 2026-10-25: `https://git-scm.com/docs/git-count-objects`,
  `https://git-scm.com/docs/git-fsck`, `https://git-scm.com/docs/git-prune` (host `git version 2.56.0`).
- Read: `.ufo/waves/round-23/preregistration.txt`, `corpus/lessons/round-22.md`,
  `corpus/lessons/round-22-verifier-spotcheck.md` §1–§7, `SCORECARD.md`, `LOG.md:1469-1522`,
  `corpus/README.md:422-446`, `corpus/QUALITY.md`, `/home/vgpnk/Projects/shokunin/LEARNING.md`,
  `corpus/pointer-exemptions.tsv`, `.ufo/waves/round-23/w1-spec.json`.

---

<!-- BEGIN LESSON DRAFT — corpus/lessons/round-23.md (L1 replaces every <…> placeholder before commit) -->

# Round23 — receipts that bind their bytes, records that agree with them

Author: SoujiR23 (hyaku in-session L1). Lane: fleet repository and workspace hygiene. Claims were
frozen before data in `.ufo/waves/round-23/preregistration.txt` at lane base
`1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (branch master, ahead=0 behind=0). Inbound work is the
non-author r22 spot-check's routed defects D1–D8 (`corpus/lessons/round-22-verifier-spotcheck.md`
§6). Axes: calibration 7 (the lane's lowest), operability 8, coverage 8. This is a bookkeeping and
instrument round: no axis is claimed to move unless its SCORECARD row's counting command re-derives
at the round tip.

## Claim and boundary

**C1 — calibration, record agreement.** The four routed bookkeeping defects D2, D5, D4 and D1 are
repaired *and* the lane holds an instrument that re-derives them. One command, frozen before data:
`python3 tools/souji-record-agreement.py --rev <full40> --root /home/vgpnk/Projects/shokunin/souji-shokunin`,
counts line `keys=K records=R occurrences=O mismatches=M`, exit 0 iff `M==0`. The key set is frozen
and every value is derived from a receipt, never declared in the key table: K1 after-receipt binding
(D2), K2 superseded-number correction (D5), K3 slice tally (D4), K4 uncommitted round work (D1).
Target `M_after=0`. The cheap control is the same instrument at the base revision, which must report
`M>=1` (receipt `census/round-23/records/agreement-control-base.tsv`); a second control is the
fixture's cases 2–6, each of which requires at least one mismatch, so an always-zero emitter is
rejected by the same harness (`control=FALSE-GREEN-REJECTED`). Observed: base `<C1-BEFORE>`, tip
`<C1-AFTER>`, fixture `<C1-FIXTURE>`. Kill rule: a mismatch class with no covering repair keeps C1
unverified, and the residual is reported — the key set is never narrowed after data.

**C2 — operability, blob-bound receipts.** The lane gains a runner that re-derives a counter at a
full durable revision and emits a receipt binding `(rev, tool path, tool sha256 at rev, command, rc,
stdout)`, plus a verifier that refuses a receipt whose recorded digest is not the committed blob at
the named revision. Counter, frozen: `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l` — 0 at
base, target `>=4` (declared-evidence before and after, gate-check before and after), each checkable
with `python3 tools/souji-receipt-run.py verify <receipt>`. Refusal demonstration: verify on a
receipt carrying the stale r22 `5b8025a8…` digest must exit nonzero with
`RECEIPT-TOOL-DIGEST-MISMATCH`; observed `<C2-REFUSAL>`. Observed after: `<C2-AFTER>` bound receipts.
Kill rule: a receipt whose verify exits 0 while its tool bytes at that revision differ from the
recorded digest kills the claim. The runner is read-only with respect to the lane: it materializes
`git archive <rev>` under `/var/tmp`, never writes the lane tree and never fetches.

**C3 — coverage, one assimilation theme on F2.** F2's r12 row reads "frontier, no entry"
(`corpus/README.md:40`), but that row is explicitly superseded at `corpus/README.md:64` by the r13
coverage table, whose F2 row already holds `knowledge/git-repo-structure-readonly.md` (S035–S037)
with the wider size attribution still frontier. This round therefore deepens F2's read side rather
than entering an entryless row, and the lesson says so instead of repeating the stale cell. One
theme, two entries:
`corpus/knowledge/repo-size-census-readonly.md` and
`corpus/knowledge/count-objects-garbage-readings-r25.md`. Counter, frozen:
`python3 tools/souji-gate-check.py --entries … --snapshot-dir <dir> --expect-slice 0`, plus
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`.
Targets: gate-check `entries=2 ok=2 fail=0`; registry 114 → `>=117` rows with 0 malformed and 0
duplicate ids; census exit 0. Observed: `<C3-GATE>`, `<C3-REGISTRY>`, `<C3-CENSUS>`. Control: the
staged rows appended as-is carry staged ids S112–S114, which this lane's registry already binds to
different documents, so the cheap append fails the census on duplicate ids; that receipt is committed
before any append. Kill rule: an entry that fails its own gate, or a row whose id collides, lands
nothing and the round reports the refusal.

**Boundary — what none of the three claims establishes.** A receipt re-derives; it does not
authenticate execution, authorship or independence, and a byte-matching receipt is not proof that a
command ran. K4 reads one working-tree `git status --porcelain` query, so it is a tree observation,
not a hermetic snapshot; K1–K3 read committed bytes at `--rev` only. The instrument is read-only and
creates no deletion, move or quarantine authority. Certification OFF, K5 HELD, F5 reap and NAMESPACE
holds unchanged. Filed history is not rewritten: D5 is repaired by an appended LOG correction, D2 and
D3 by new receipts, and the r22 report — which lives in the fleet root, not in this lane — is
corrected append-only in LOG.md and here, never edited. The lane's write scope is its own repo: the
fleet `.scratch/`, `.ufo/state/`, `watchdog.log`, `MANIFEST.json`, fleet `scripts/` and `templates/`,
sibling lanes and jj state are untouched. The fleet garbage figure remains unmeasured in this lane,
and the staged S134 own-work row is not adoptable because its evidence lives outside this repo.

## Mistakes

Every row below is one routed spot-check defect, with the criterion that should have caught it and
the repair that lands this round. `K<n>` names a frozen C1 key; `C2` names the receipt verifier.
K1–K4 cover D1, D2, D4 and D5; D3 is covered by the C2 verifier's refusal; D6 and D7 are
record-and-criterion repairs with no counter, and each row states its own witness.

| id | class | evidence | captured-by | fix / failure witness |
|---|---|---|---|---|
| R23-M1 | calibration, record accuracy (D1) | the r22 report claims "Received but not integrated — inherited attempt-1 leftovers: none uncommitted" while `git status --porcelain` at the r22 tip lists five modified seat reports and two untracked `evidence/impl-a/head-c9f1fe3.*` files; the same seven paths are still uncommitted at this round's base `1208bfb` | Q10 ("bookkeeping matches the repo at the closing commit") — stated as prose, and its listed test never ran `git status`; no lane criterion covered working-tree cleanliness | K4 counts each `git status --porcelain` path that no committed `uncommitted:` exemption names as one mismatch; the seven r22 paths land in this round's lane commit, and the r22 report's sentence is corrected append-only in LOG.md. Witness: fixture case 8 (unexempted dirty path → mismatch) and case 9 (exempted operator path → not a mismatch), then `<C1-AFTER>`. Q54 states the one-command check |
| R23-M2 | calibration, receipt binding (D2) | `SCORECARD.md:14` names tip `9301d98` with `assertions=63 resolved=63 skipped=40 mismatches=0`, the r22 report names `77d6595`, `git grep -n 'resolved=63' 77d6595` returns only `SCORECARD.md:14`, and the lane's own residual seat recorded `63/61/39/2 rc=1` (`.ufo/waves/round-22/attempt2/residual/ResClaims.md:24`) | Q37 (a stamped revision binds the measured bytes) — scoped to evidence runners, never to a record that quotes a count; nothing required the quoted 4-tuple to equal a receipt's counts line | K1: the r22 after 4-tuple in `SCORECARD.md` must equal the counts line of `census/round-23/records/declared-evidence-after.tsv`, the revision token on that same line must equal the receipt's `rev=` header, and the receipt must exist in the tree at `--rev`; classes `receipt-absent`, `value-disagree`, `rev-disagree`. Witness: fixture cases 2, 3, 4. Q55 states the criterion |
| R23-M3 | operability, digest binding (D3) | the r22 C2 after-run was measured with tool blob `f26aa728` (blob at `c9f1fe3` and `8680755`), the tool changed at `9fcc4f7` to blob `63ac63b8` (sha256 `d5ed0805…`), and the report cites `5b8025a8…`, the pre-`9fcc4f7` digest; no committed re-run and no before (`fail=10`) receipt exist | Q6 (a verdict names the sha256 of the bytes it measured, equal to the installed file) — scoped to certification fragments, never to a report sentence about a counter run | C2's runner emits `rev`, tool path, tool sha256 at rev, command, rc and stdout; `verify` refuses a receipt whose recorded digest is not the committed blob at that revision. Witness: verify on the stale `5b8025a8…` receipt exits nonzero with `RECEIPT-TOOL-DIGEST-MISMATCH` (`<C2-REFUSAL>`), and `<C2-AFTER>` bound receipts each pass verify. Q55 states the criterion |
| R23-M4 | calibration, sweep completeness (D4) | `corpus/README.md:440-441` says "5 accepted with corrected quotes, 1 present, 1 refused (wrong-source citation), 1 unverifiable", while `census/round-22/attempt2/slice-verdicts.tsv` holds 5 accepted, 2 present (S126, S138), 1 unverifiable (S118), 0 refused — and the lesson already said 2 present, 0 refused | the CORPUS rule that a correction sweeps every mention, plus Q10 — both prose; no counter compared every occurrence to the receipt it should derive from | K3: every "<n> <class>" occurrence in `corpus/README.md` and `corpus/lessons/round-22.md` must equal the tally derived from `census/round-22/attempt2/slice-verdicts.tsv`, and each record must carry at least one occurrence of each class. Witness: fixture case 7; the README corrections block lists every mention with its line number, so a missed mention is a visible omission rather than a silent one |
| R23-M5 | calibration, append-only history (D5) | `LOG.md:1484` keeps `assertions=56 resolved=53` while the committed receipt `census/round-22/attempt2/declared-evidence-before.tsv` holds `55/52/33/3`; `LOG.md:1509` keeps "1 present, 1 refused (S123 wrong-source"; `grep -n 'superseded by' LOG.md` returns no match | Q41 (an obsolete immutable LOG command receives a named append-only replacement index) — applied to counter commands only, never to superseded numbers | K2: every 4-tuple inside LOG.md's "Round22 attempt2" section that disagrees with the receipt must be named by a LATER LOG.md line carrying `superseded by` and the same 4-tuple, and the filed occurrence must still exist (deleting filed bytes is itself a mismatch). Witness: fixture cases 5 and 6; the LOG correction block names the superseded tuple and the correct one |
| R23-M6 | discernment, reject reason scope (D6) | `corpus/lessons/round-22.md:337-341` refuses `quarantine-staging-no-copy-r24.md` because it adds "no new refusal semantics or field, so no new consequence"; the staged candidate's lines 24-25 add `RENAME_EXCHANGE` and `RENAME_WHITEOUT`, and its line 44 claims the primitive verified across the whole writable set. The refusal survives on the entry budget and r23's `mv --no-copy` fallback, not on "no new consequence" | Q1 and Q2 (a tool-behaviour claim names its version and cites a fixture) plus the M22 coverage-delta rule — neither checks a refusal's *reason* against the refused candidate's own bytes | the Gate below states the narrow reason and names the delta the candidate does add; the same candidate is refused again under that reason. Witness: a reason that names a delta the bytes do not carry is the same defect again, so the reason must be checkable against two named lines of the candidate |
| R23-M7 | discernment, criterion production (D7) | r22 rows M17 and M22 record `captured-by: none`, and `corpus/QUALITY.md` is unchanged base→tip (its last row is Q53) | LEARNING step 3 (when no criterion caught a mistake, a `QUALITY.md` criterion citing the lesson is written) — stated, and nothing fails when it is skipped | Q54 (uncommitted round work and a "none uncommitted" claim are caught by one runnable command) and Q55 (a quoted count needs a receipt binding revision and tool digest) are added with lesson pointers to R22-M17, R22-M22 and R23-M1 to R23-M3. Witness: each new criterion's check is a command that can exit nonzero — K4 for Q54, C2 `verify` for Q55; a criterion whose check cannot fail is not a criterion |

D8 (a stray backtick on the derived S118 slice row, count unaffected) is routed and cosmetic; it is
repaired wherever the derived slice rows are regenerated, not by this lesson, and it is not counted
as an eighth mistake class.

## Gate

### Opened sources (2026-10-25)

All three were opened live this run from this host (`git version 2.56.0`); the staged entries'
`opened` dates and quotes prove nothing for this lane, so each row below is re-grounded here.

- S115 mined: https://git-scm.com/docs/git-count-objects, git-count-objects manual (last updated in
  2.51.1), § OPTIONS, `-v` field list, `garbage` field. Located quote: "garbage: the number of files
  in the object database that are neither valid loose objects nor valid packs". Grounds the read-side
  distinction the F2 entry needs: loose-object count, loose size and garbage-file count are separate
  fields, so no single "size" number is a census.
- S116 mined: https://git-scm.com/docs/git-fsck, git-fsck manual (last updated in 2.53.0),
  § DESCRIPTION. Located quote: "Verifies the connectivity and validity of the objects in the
  database." Grounds fsck as a reachability and validity instrument, not a size measurement, which is
  why the F2 entry keeps it in a separate role.
- S117 mined: https://git-scm.com/docs/git-prune, git-prune manual (last updated in 2.43.0),
  § DESCRIPTION. Located quote: "Note that unreachable, packed objects will remain." Grounds why
  pruning loose objects cannot be read as a size bound. Same document, § OPTIONS `-n, --dry-run`:
  "Do not remove anything; just report what it would remove." Grounds the read-only reading of prune
  that the C2 receipts depend on.

The three ids are the lane's re-pointing of the staged S112–S114 (the staged ids already belong to
this lane's quarantine rows). The entry-level Gate quotes are the two entries' own and are drafted by
their scribes from the same pages; this section is the lesson-level re-grounding, not a substitute.

### Assimilation decisions

- `corpus/knowledge/repo-size-census-readonly.md` (ground F2) → **ADMIT**. The delta over the held
  `knowledge/git-repo-structure-readonly.md` is named rather than assumed: that entry holds the
  structure-census metrics, while this one holds the three-instrument read side (count-objects field
  set, fsck as connectivity not size, prune's packed-object residual) and the `git fsck --lost-found`
  write trap. It grounds that read side on three re-opened pages re-pointed to S115–S117 and cites
  the lane's own `tools/souji-repo-structure.sh` and `census/round-13/verification.json` instead of
  claiming a fleet measurement. Flip: an entry that asserts a fleet size or garbage figure without a
  lane-measured receipt is refused, and an entry whose delta over the held F2 entry is not stated is
  refused for novelty overstatement (the r22 M22 class).
- `corpus/knowledge/count-objects-garbage-readings-r25.md` (ground F2) → **ADMIT**, conditional on
  the two community pages resolving (tier B, S118/S119). The entry must state that the fleet figure
  is unmeasured here and that the staged S134 own-work row is not adoptable, because its evidence
  lives outside this repo. Flip: if either page is unreachable, that row is refused and the refusal
  reason plus flip are recorded in place of the row.
- staged rows appended with their campaign ids S112–S114 → **REJECT**. Reason: those numbers already
  resolve to different documents in this lane's registry, so an as-is append is a duplicate id and
  fails the census. Flip: a lane id space that does not collide with rows already holding those
  numbers. This refusal is the prereg's cheap control and its receipt is committed before any append.
- staged `S134` own-work row → **REJECT**. Reason: the row's evidence is a campaign-repo payload, so
  the lane would cite bytes it cannot re-derive at its own revision. Flip: a committed in-repo
  receipt of that measurement.

Registry and gate effect: 114 → `<C3-REGISTRY>` rows, gate-check `<C3-GATE>`, census `<C3-CENSUS>`.
A row no admitted entry cites is not appended (CORPUS rule 4).

### Independent expectations and rejected scope

The C1 key table is frozen in the preregistration, and every key's value is derived from a receipt:
K1 from `census/round-23/records/declared-evidence-after.tsv`, K2 from
`census/round-22/attempt2/declared-evidence-before.tsv` plus LOG.md's filed section, K3 from
`census/round-22/attempt2/slice-verdicts.tsv`, K4 from one working-tree status query minus committed
exemptions. The fixture that judges the instrument is authored by a seat that does not write the
instrument, and the mutant list is designed from the predicate text rather than from the
implementation, so "the fixture agrees with the tool" is not the only evidence. The instrument's own
fixtures reject the always-zero emitter (`control=FALSE-GREEN-REJECTED`), so the target cannot be met
by asserting it.

Rejected scope, explicitly: certifying that a command executed, that a seat authored its report, or
that a review was independent; treating K4's single status query as a hermetic tree snapshot;
comparing transient paths or timestamps; rewriting any filed LOG or receipt byte; reusing evidence
from a Q26-void seat; asserting a fleet garbage census from outside this repo; creating deletion,
move or quarantine authority; moving an axis score on bookkeeping alone; and re-pointing a source id
by arithmetic instead of by document. The outside spot-check for this round is owed — at least one
admit and one reject judged by a non-author with a reason on record — and a lane-dispatched seat is
still the lane, so no outside agreement is claimed here.

## Seat-reported failures

Append-only. Empty at draft time: no wave output exists yet, and a source-only draft's own lack of
integration is not runtime failure evidence. Every contract `STATUS:` failure paragraph will be
carried here verbatim with `open` or `resolved@<rev>`, per Q25(c); a Q26-void seat's findings are
recorded as VOID and never used for admission.

## Trend verdicts

Verdicts use the protocol vocabulary and are written from measured bytes, so each line below states
the observation that would settle it. No trend is claimed on the lane's own say-so.

- **expansion — `unprovable-but-better`, pending a named non-author.** The LEARNING `improved` test is
  "net new admitted entries on ground the coverage map did not hold". That test is not met on the
  map's own bytes: F2's r12 "no entry" cell (`corpus/README.md:40`) is superseded at
  `corpus/README.md:64`, and the r13 table already lists `knowledge/git-repo-structure-readonly.md`
  as F2's entry, so this round deepens a held area instead of opening one. It is still better — two
  entries whose every claim resolves, three mined rows with live-opened quotes, and a read side the
  held entry does not carry — but a verdict of `improved` would repeat r22's M22 novelty
  overstatement. `unprovable-but-better` requires a named non-author judging the change better with
  reasons on record, so this line stays conditional until that reviewer exists; if either entry fails
  its gate the verdict is `unchanged` and the refusal is recorded, not traded.
- **quality — `improved` (bounded) if `<C1-AFTER>` reports `mismatches=0` at `<R23-C1-REV>` and
  `<C2-AFTER>` bound receipts each verify, otherwise `unprovable-but-better`.** The bounded part is
  named: a receipt re-derives a counter, it does not authenticate execution, and the r22 after-state
  is repaired by adding a receipt at a named revision rather than by rewriting the old record. No
  admitted entry is superseded this round, so the weaker half of the `improved` test (a stale entry
  re-verified) is not exercised.
- **discernment — `unchanged` at draft time.** The round's own disagreement with the spot-check is
  learned rather than left unlearned: D6's overbroad reason is restated narrowly here, and D7's
  missing criterion becomes Q54 and Q55 with lesson pointers. That is the `improved` condition's
  second half, but the first half — the spot-check agreeing with this round's admits and rejects — is
  not available until a non-author records it, so the verdict does not move on this lesson's word.

<!-- END LESSON DRAFT -->

## Placeholders

Every one must be replaced by the L1 from a committed receipt or command output before the lesson is
committed; none may be filled by inference.

- `<C1-BEFORE>` — counts line `keys=… records=… occurrences=… mismatches=…` of the C1 instrument at
  base `1208bfb`, from `census/round-23/records/agreement-control-base.tsv`.
- `<C1-AFTER>` — the same counts line at the round tip.
- `<C1-FIXTURE>` — the fixture's terminal `selftest=<pass>/<total>` line and its
  `control=FALSE-GREEN-REJECTED` marker.
- `<C2-REFUSAL>` — exit code and message of `verify` on the stale `5b8025a8…` receipt.
- `<C2-AFTER>` — the `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l` value at the tip.
- `<C3-GATE>` — gate-check counts line for the two entries.
- `<C3-REGISTRY>` — `corpus/SOURCES.md` row count after the append, with malformed and duplicate-id
  counts.
- `<C3-CENSUS>` — exit code of `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`.
- `<R23-C1-REV>` — the `rev=` value the after receipt carries, which K1 requires to equal the
  revision token on the SCORECARD line.

Angle-bracket tokens inside command syntax — `<full40>`, `<rev>`, `<dir>`, `<receipt>`, `<n>`,
`<class>`, `<pass>/<total>` — are placeholders of the frozen counters and of the fixture contract,
not lesson placeholders, and stay as written.

## Findings

1. **C3's justification quotes a row the README itself supersedes.** The prereg's C3 says F2 is "the
   lane's only frontier row with NO entry (corpus/README.md F2: 'frontier, no entry')". That cell is
   `corpus/README.md:40`, and line 64 heads `## Round 13 current coverage (supersedes the r12 F2 row)`,
   whose F2 row already lists `knowledge/git-repo-structure-readonly.md` (S035/S036/S037). The counter
   is unaffected (it checks entries and registry rows, not novelty), but the expansion verdict cannot
   rest on "uncovered ground", and the lesson's C3 paragraph and expansion line now say
   `unprovable-but-better` on the corrected basis. Location: `corpus/README.md:40` versus
   `corpus/README.md:64-68`; prereg C3.
2. **C3's frozen counter names a flag the committed tool does not have.** The prereg's C3 command is
   `tools/souji-gate-check.py … --expect-slice 0`, but `--help` at lane base lists only `--root
   --round-date --entries --snapshot-dir --slice --slice-verdicts --selftest`
   (`tools/souji-gate-check.py:296-302`). The defaults `--slice`/`--slice-verdicts` still point at
   the r22 quarantine slice, which holds 8 verdict rows, so without the flag the command cannot
   express this round's target. Location: `.ufo/waves/round-23/preregistration.txt` C3 versus
   `tools/souji-gate-check.py:296-302`.
3. **C3's landed path disagrees between the frozen contract and the wave item.** The prereg names the
   second entry `corpus/knowledge/count-objects-garbage-semantics-r24.md` (and its gate-check command
   uses that path); the `ScribeEntryGarbage` item names
   `corpus/knowledge/count-objects-garbage-readings-r25.md`. The row set also differs: the prereg
   lists staged S134/S138/S139, the item allows only S118/S119 with S134 refused. One of the two must
   be corrected explicitly before the C3 counter runs, and a silent rename would make the frozen
   command unrunnable. Location: `.ufo/waves/round-23/preregistration.txt` C3 versus
   `.ufo/waves/round-23/w1-spec.json` item `ScribeEntryGarbage`.
4. **K4 will count the operator-owned untracked sweep unless an exemption row is added.**
   `corpus/pointer-exemptions.tsv` carries four rows and none is prefixed `uncommitted:`, while
   `git status --porcelain` shows `?? census/operator-sweep-20261019/`. K4's declared mechanism
   (committed `uncommitted:` rows for operator-owned paths) therefore needs that row for the tip to
   reach `M=0` without touching the sweep. Location: `corpus/pointer-exemptions.tsv` and
   `git status --porcelain` at `1208bfb`.
5. **The r22 report cannot be corrected in place from this lane.** Its "none uncommitted" sentence
   lives in `/home/vgpnk/Projects/shokunin/.ufo/reports/round-22/souji.md`, outside the lane's write
   scope, so D1's record repair is the appended LOG correction plus this lesson — the report file
   stays as filed. Location: spot-check §1 versus the lane bound in the preregistration.
6. **D2's two revisions must be reconciled by the receipt, not by choosing one.** `SCORECARD.md:14`
   names `9301d98` while the r22 tip is `77d6595`; K1 binds the SCORECARD token to the receipt's
   `rev=` header, so the receipt decides which revision the after-state is measured at and the
   SCORECARD line must then agree. Location: `SCORECARD.md:14`.
7. **The three C3 source rows should carry the manual version they were quoted from**, not only the
   access date: the live pages report "last updated in 2.51.1" (count-objects), "2.53.0" (fsck) and
   "2.43.0" (prune), while the host runs git 2.56.0. Q1 asks a tool-behaviour claim to name the
   version it was verified on; a date alone does not. Location: `corpus/SOURCES.md` rows S115–S117 as
   drafted by `ScribeSourcesRows`.

## Attack log

- **ATTACK on C3's counter as written (not on its predicate).** The frozen command cannot run against
  the committed tool: `--expect-slice` is absent from `tools/souji-gate-check.py`'s parser
  (`--help` at `1208bfb`), so the command exits on an argparse error before any entry is checked.
  The predicate ("two entries pass their own gate, no register slice is expected this round") is
  sound and stays frozen; what is missing is a tool capability the counter already assumes. The
  honest resolutions are to extend the tool with `--expect-slice` and re-run the frozen command, or
  to record the counter as unrunnable and report C3 unverified. I did not edit the counter, the tool
  or the prereg.

- **ATTACK on C3's stated ground, not on its predicate.** C3 justifies the theme with "the lane's
  only frontier row with NO entry", quoting `corpus/README.md:40`. That row is superseded four lines
  later in the same file (`corpus/README.md:64`, "supersedes the r12 F2 row"), and the superseding
  table already gives F2 an entry. The frozen predicate (two entries pass, registry rows append
  without a duplicate id) still measures something real — a better F2 read side — but it does not
  measure entry into uncovered ground, so an `expansion: improved` verdict drawn from it would be
  unearned. I did not edit the claim; the lesson's C3 paragraph and expansion verdict record the
  corrected basis, and the novelty wording is left to the L1's ruling.
