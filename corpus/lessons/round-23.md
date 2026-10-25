# Round 23 — record agreement, blob-bound receipts, F2 read side

Author: SoujiR23 (lane identity `souji-shokunin <souji@shokunin.local>`). Lane base
`1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`. Preregistration
`.ufo/waves/round-23/preregistration.txt`. Inbound: the non-author spot-check of round 22,
`corpus/lessons/round-22-verifier-spotcheck.md` §5–§7 (routed defects D1–D8).

## Claim and boundary

Three claims, each on a distinct axis, each with one concrete after-value re-derivable by one
command over committed bytes.

**C1 — calibration (7, the lowest non-retired axis).** `tools/souji-record-agreement.py` re-derives
four declared-vs-observed keys: K1 the r22 C1 after-state is bound to the revision SCORECARD names,
with each counts tuple bound to its own nearest preceding revision token; K2 every superseded
scalar in `LOG.md`'s round-22 section is named by a later `superseded by` line while the filed
occurrence survives; K3 the register-slice tally in `corpus/README.md` and `lessons/round-22.md`
equals `census/round-22/attempt2/slice-verdicts.tsv`; K4 no uncommitted round work outside an
exact, frozen exemption allowlist. Control (do nothing) = the same bytes at the base revision:
`keys=4 records=3 occurrences=13 mismatches=6` revision-scoped (`mismatches=29` with the live
worktree arm), receipt `census/round-23/records/agreement-control-base.txt`. After: `0`
(`census/round-23/records/agreement-after.tsv`). Fixture `tests/fixtures/r23-record-agreement.py`
11/11 with `control=FALSE-GREEN-REJECTED`: ten cases require a nonzero mismatch, so an
always-zero emitter fails them; the eleventh is the green-on-clean target.

**C2 — operability (8).** `tools/souji-receipt-run.py` re-derives a counter at a full durable
revision in a private `--no-local` clone and emits a receipt binding rev, tool path, the sha256 of
the bytes the command ran against, argv, exit code and redacted output; `verify` re-reads the tree
at the receipt's revision and refuses a digest that is not the committed blob. Counter:
`grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l` 0 → 5, every receipt `verify=ok`; the
stale r22 digest `5b8025a8…` is refused with `RECEIPT-TOOL-DIGEST-MISMATCH`. Fixture
`tests/fixtures/r23-receipt-run.py` 8/8, and 12/12 mutants of a compliant reference runner are
caught, so the green is not vacuous.

**C3 — coverage (8).** One assimilation theme on F2's read side: `repo-size-census-readonly.md`
(S115–S117) and `count-objects-garbage-readings-r25.md` (S118–S119), re-grounded from sources
opened this round. Registry 114 → 119 rows, 0 malformed, 0 duplicate ids, census exit 0; gate
`entries=2 ok=2 fail=0`.

**Boundary.** Receipts bind bytes, not execution — a typed receipt passes `verify`, and that is
why Q55 exists. K4 is a live-worktree observation, not a revision snapshot. C3's gate slice arm is
inert this round (no register rows were quarantined), so the entry arm carries the verdict, and
the coverage delta is stated as F2 entries 1 → 3, never as newly-uncovered ground: `corpus/README.md`
already held `git-repo-structure-readonly.md` on F2. No fleet size figure is claimed anywhere. No
deletion authority, no history rewrite, no credentials, no live `/proc` census, no operator-sweep
contents. Certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged.

**Process deviation, disclosed.** The counters were repaired *after* wave-1 seats had reviewed
them: K1's tuple-to-revision binding, K2's filed-occurrence list, K3's per-record class presence,
K4's exact allowlist, and the runner's clone-derived digest, argv refusals, redaction and
newline-preserving capture all changed in response to CritC1Gameable, CritPrereg, CritC2Value and
ExecFixtureReceiptRun. No after-data existed at any of those edits, and every number above comes
from the final bytes, which are pinned by digest in SCORECARD. `MutCounter`'s and
`ExecGateReproduce`'s scoring against earlier bytes is therefore historical, and the residual call
re-derives the mutant inventory against the final bytes. This is reported as a deviation from §9's
"a rule changed after any seat has scored is not the claim's rule", not as compliance.

## Mistakes

| id | class | evidence | captured-by | fix / failure witness |
|---|---|---|---|---|
| R23-M1 | calibration, uncommitted round work (D1) | seven round-22 wave files left uncommitted while the filed report said "none uncommitted"; reproduced at base by K4 | Q10 named the bookkeeping state but had no command for an uncommitted round-authored path | committed here; `ScoutInherited` re-derived both evidence digests and every moved number; K4 keeps it closed, and its failure witness is the base control's 23 K4 rows. |
| R23-M2 | calibration, unbound after-state (D2) | no committed byte under `census/` bound `9301d98` to the r22 after-tuple | Q6/Q37 bound digests and revisions for tools, not for a quoted count in a record | `census/round-23/records/declared-evidence-after.tsv` (rev `9301d98c…`, tool `65817d0d…`, `assertions=63 resolved=63 skipped=40 mismatches=0`); K1 fails if the receipt is absent or the bound tuple disagrees. |
| R23-M3 | calibration, stale digest (D3) | the r22 report cited `5b8025a8…` at a tip whose tool blob hashes `d5ed0805…`; the `fail=10` before-state exists in no commit | Q55 did not exist; `instrument-digests.txt` was written out of band and read by no code | digest chain recorded with two bound receipts; the before-state is reported unrecoverable rather than reconstructed (`ExecGateReproduce`, `RevD3`, `RevGateHistory` agree). |
| R23-M4 | calibration, single-site sweep (D4) | `corpus/README.md` carried the wrong slice tally while `slice-verdicts.tsv` held the right one | the CORPUS "corrections sweep every mention" rule was applied by hand, with no counter | README corrected in place; K3 fails on any `<n> <class>` occurrence that disagrees, and on a missing class in either record. |
| R23-M5 | calibration, superseded numbers kept (D5) | `LOG.md` kept `assertions=56 resolved=53` and the wrong tally pair with no correction | Q41 required an append-only replacement index, but nothing detected its absence | `LOG.md` `Round22 attempt2 corrections` names both cells under `superseded by`; K2 fails when a stale scalar has no later correction, and also when the filed occurrence is deleted. |
| R23-M6 | discernment, overbroad reject reason (D6) | the r22 lesson rejected a candidate on "no new refusal semantics or field" while the candidate added `RENAME_EXCHANGE`/`RENAME_WHITEOUT` and named its own consequence | Q1/Q2 required a located quote, not that a reject reason be true of the bytes it describes | append-only correction in `corpus/lessons/round-22.md`: entry-level reason (budget + `mv --no-copy` fallback) plus the named delta and a flip not already met. |
| R23-M7 | discernment, `captured-by: none` with no criterion (D7) | M17 (and M19/M21, not routed) record `captured-by: none`; `corpus/QUALITY.md` was unchanged base→tip | LEARNING step 3 asks for a criterion when no rule caught the mistake; nothing enforced it | Q54: a Gate's `§ <NAME>` locator must appear in one of the Gate's own snapshots; witness `tests/fixtures/r23-locator-heading.py` (real entries 0 bad, mutant 6 bad, `selftest=2/2`). The spot-check's M22 half is overstated — that row names Q1/Q2. |
| R23-M8 | scope, wave-1 seat writes | `SimplTouched` created `tools/__pycache__/` by importing a lane tool without `-B`; the directory is a K4 mismatch and the lane has no `.gitignore` | Q26's write audit covers declared paths, not interpreter side effects | removed before landing; every later run uses `python3 -B`; the K4 base control's `__pycache__` row is the witness that the counter sees it. |

## Gate

### Opened sources (2026-10-25)

Every row below was opened by this lane this round; the man-page snapshots are committed under
`census/round-23/sources/` with their sha256, and the two community pages as bounded extracts of
the bytes fetched.

- **S115 mined** — https://git-scm.com/docs/git-count-objects, § OPTIONS `-v/--verbose`, page last updated 2.51.1 (2.51.2 → 2.56.0 no changes), installed `man git-count-objects` git 2.56.0-1 agrees. Located quote: "garbage: the number of files in the object database that are neither valid loose objects nor valid packs". The page documents no write side effect; that is documentation-absence, not an empirical read-only proof.
- **S116 mined** — https://git-scm.com/docs/git-fsck, § OPTIONS, page last updated 2.53.0. Located quote: "Write dangling objects into .git/lost-found/commit/ or .git/lost-found/other/, depending on type." This is the one option that writes, and for a blob it writes the blob's *contents*.
- **S117 mined** — https://git-scm.com/docs/git-prune, § DESCRIPTION and § OPTIONS, page last updated 2.43.0. Located quote: "Do not remove anything; just report what it would remove." ScoutPrune measured four counter-examples showing `prune -n` is not the `fsck --unreachable` set.
- **S118 mined** — https://qiita.com/koseki/items/f1af58f1ec1693f0536a (tier B, community, JA). Located quote: "The default value is 6700. Setting this to 0 disables it." The page never glosses the `garbage` field: `count-objects` occurs zero times in its bytes.
- **S119 mined** — https://bbs.csdn.net/weixin_33940469/article/details/100327798 (tier B, community, ZH), § 2.1 heading `先看总量：count-objects 与 du`. Located quote: "无法被 Git 识别的垃圾文件大小". The gloss matches the referent and mislabels the unit: `garbage` is a count, `size-garbage` the space.

Registry `114 → 119` rows (`grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`),
`validate` exit 0 with the retained 30 `W04` duplicate-URL warnings and no `E` finding.

### Assimilation decisions

ADMIT — `repo-size-census-readonly.md` (S115–S117). Reason: it supplies the two halves
`git-repo-structure-readonly.md` names as missing (the unreachable census and the size census
including `garbage`/`size-garbage`/`alternate`), and it names the write-safety trap the F2 fixture
must fence. The staged entry's own source ids collided with this lane's S112–S114, which resolve to
different documents; re-pointing was done **by document**, with this lane's access date and quotes.

ADMIT — `count-objects-garbage-readings-r25.md` (S118–S119). Reason: the target-language reading is
not uniform, and the difference is actionable (one page glosses the field and gets the unit wrong,
the other means the collection). Renamed from the staged `-semantics-r24.md` because the staged
title's "both target languages read `garbage` the same way" is false on the pages themselves.

REJECT — the staged own-work row (staged `S134`, the round-3 fleet `garbage` census). Reason: its
evidence lives outside this repository, so no lane path resolves it and it cannot be re-derived from
lane bytes. Flip: that `.out` is committed under `census/` with a receipt and a read-only re-run
bound at a named revision.

REJECT — the staged claim that both target languages read `garbage` the same way. Reason: the JA
page holds no `count-objects` or `size-garbage` bytes and uses ガベージ for the collection. Flip: a
JA source that glosses the field itself and states its unit.

REJECT (in the entry Gate) — `git fsck --lost-found` as a census instrument. Flip: admit it only for
a census on a disposable copy under `/var/tmp` whose writes are discarded, with that copy named in
the receipt.

### Independent expectations and rejected scope

The counters' expected values are literals in the fixtures, never read from the tool under test; the
fixtures reject an always-zero emitter by construction. Rejected scope: no claim that a receipt
authenticates execution; no claim that K4 is revision-reproducible; no fleet size or debris figure;
no statement that the r22 `fail=10` before-state was reproduced; no promotion of F2 to core (it
still lands no SKILL rule and no tool).

## Seat-reported failures

Wave 1 carried 41 seats: 30 reported `PASS`, nine reported `PARTIAL` or `FAIL`, and two (`ScribeEntryRepoSize`, `ScribeReport`) carried no `STATUS:` line — so "nine failed" must not be read as "the other 32 passed". Every failure paragraph is carried
verbatim below with its disposition; none is silently dropped and none is used as evidence for a
claim without the L1 re-derivation named in the disposition.

- `.ufo/waves/round-23/w1/CritC2Value.md` "STATUS: FAIL — the claim's own kill rule fires under an executed counterexample against the" — open — accepted in part: the runner now takes the digest from the tree the command ran in, sets GIT_NO_REPLACE_OBJECTS/GIT_NO_LAZY_FETCH, and refuses `git -C`/mutating subcommands; the "typed receipt passes verify" limit is retained and disclosed (C2 kill rule unchanged).
- `.ufo/waves/round-23/w1/CritC3Ground.md` "STATUS: PARTIAL — entry 1 (repo-size census instruments) is honest and does add ground the lane did" — open — accepted: C3 is restated as F2 entries 1→3 on the read side, not as uncovered ground; the prereg premise was amended pre-data and the report says so.
- `.ufo/waves/round-23/w1/CritPrereg.md` "STATUS: FAIL — not admissible as frozen: C1's `mismatches=0` is unreachable on the real" — open — accepted in part: K1 now binds each tuple to its nearest preceding revision token (the before-tuple is no longer erased), the C2 coupling (receipt-unbound) was removed for separability, and the counter repairs are disclosed with the final bytes pinned. The "rule changed after scoring" finding is recorded as a real deviation of process, not repaired.
- `.ufo/waves/round-23/w1/MutCounter.md` "STATUS: PARTIAL — 51 clause mutants designed for `tools/souji-record-agreement.py` (sha256" — open — accepted: 54 clause mutants over 32 clauses were designed against the final counter bytes (sha256 617f4c96…); 28 are uncovered by the fixture's 9 cases and are named in the seat report, which is the honest adequacy statement for a counter this size — `selftest=9/9` is not claimed as clause adequacy.
- `.ufo/waves/round-23/w1/MutReceipt.md` "STATUS: PARTIAL — 26 mutants over 20 clauses; 9 killed, **uncovered=17**. The fixture is now a" — open — accepted in part: 26 mutants over 21 clauses, 9 killed, 17 uncovered. The 'digest from the tree at rev' clause is NOT killed by fixture case 3 and cannot be — case 3 moves HEAD forward after the receipt exists, so the working-tree and rev-blob digests are identical at run time; the seat's direct probe (working tree holding C2's bytes with `--rev C1`) is the only separating case and no fixture case runs it. Disclosed as a fixture coverage limit, not repaired.
- `.ufo/waves/round-23/w1/RevD6.md` "STATUS: PARTIAL — D6 is **real and open** at the lane base (`1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`): the" — open — accepted: D6 repaired append-only in corpus/lessons/round-22.md with the entry-level reason and a flip not already met.
- `.ufo/waves/round-23/w1/RevD7.md` "STATUS: FAIL — D7 is real for M17 and reproducible, but the spot-check overstates it for M22, and" — open — accepted: D7 repaired as Q54 (locator-heading), not as the D1-class criterion the wave item proposed; Q55 covers the receipt binding.
- `.ufo/waves/round-23/w1/ScribeLesson.md` "STATUS: PARTIAL — draft only. The lesson body is written from committed bytes at lane base" — open — accepted: this lesson is its own draft, corrected where the wave-1 findings changed a number or a path.
- `.ufo/waves/round-23/w1/SentinelScope.md` "STATUS: PARTIAL — 1 HIGH, 4 MEDIUM, 1 LOW; item 4's claim is accurate and confirmed from both the opened page and the installed manual. No credential was read or printed this run; `.scratch/` and operator-sweep contents were not opened." — open — accepted: argv refusal list, redaction ported from tools/souji-proc-census.sh, GIT_OPTIONAL_LOCKS=0, newline-preserving capture and the out-path guards landed in the runner; the "grep counter counts files, not verified receipts" attack is disclosed and paired with a verify-per-receipt command.

## Trend verdicts

- **expansion — `improved` (bounded).** Two admitted entries on F2's read side move F2 from one
  entry to three, with five new tier-A/B rows and committed snapshots; the bound is that no SKILL
  rule or tool lands, so the row stays frontier. A non-author closure may re-grade this as
  `unprovable-but-better`; the lane's own reading is that the entries add actable consequences
  (`--lost-found` writes, `prune -n` ≠ `fsck --unreachable`, `alternate` must be read).
- **quality — `improved` (bounded).** Every receipt in the round verifies against its own revision;
  the two instruments carry fixtures that reject a false green (9/9 and 8/8, plus 12/12 mutants of a
  reference runner); the record defects the spot-check routed are closed by counters rather than
  prose. Bounds: K4 is not revision-reproducible, a receipt binds bytes not execution, and the
  counter repairs happened after wave-1 scoring.
- **discernment — `improved` (bounded).** Two routed defects (D6, D7) turned into a corrected reject
  reason and a new criterion; three wave-1 attacks that falsified parts of the plan were accepted in
  the round's own text (C2's `refs/replace` hole, C1's tuple-binding hole, C3's ground already held).
  Bounds: the spot-check's D3 premise is partly false (blob sha1 vs sha256 of the same bytes) and
  D7's M22 half is overstated; both are reported rather than repaired.
