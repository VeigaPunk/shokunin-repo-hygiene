# Deliver — r32 lesson sections (seat SwarmScribe32, a2w1)

Draft for `corpus/lessons/round-32.md` (absent at lane tip `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`), read from
committed bytes only: frozen contract `census/round-32/records/preregistration.txt` (prereg `3ec84fc8…`), landed
commits `98e5203d45b4e419a9e72801733d93303acc7ebd` (C2), `a92e1aae91dbf46c2d7eff713932cfc820186970` (C3 + A1 +
routed defect 2), `9e8982b7a6ac57dffa415f9db43cf7cd6e829c93` (C1 rows), amendments at
`census/round-32/records/amendments.txt`, and the wave-1 reports under `.ufo/waves/round-32/w1/`.

Nothing here is a claim change: no predicate, target, counter or item set is touched. No counter was run for these
sections. The only execution performed by this seat is the M1 green arm (`tools/souji-record-contract.py`, output in
§Observed); the red arm is the committed receipt, cited as such. Attempt-1's salvaged after-records
(`census/round-32/records/c*-after-v*.txt`, commit `4e56c48`) were **not** used as evidence.

Both blocks are append-ready: the `## Mistakes` rows continue the table whose header is
`| class | evidence pointer | captured-by | fix |`, and the `## Seat-reported failures` bullets follow the round-31
lesson's shape (path + STATUS line, disposition, then the STATUS paragraph). Report statuses were swept with
`grep -m1 '^STATUS:' .ufo/waves/round-32/w1/Swarm*.md`; 41 reports carry one (34 PASS, 7 non-PASS), and all seven
non-PASS reports are carried below.

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| contract | `census/round-32/records/m1-red-before.txt` — `lines=17 bad=4`, `exit=1`, `BAD 16` to `BAD 19` for `arm=reflog-only` outside the frozen `solo`/`descendant` set, over `census/round-31/records/jj-object-clock-run.txt` against the reconstructed r31 grammar `census/round-32/m1-r31-contract.txt`; the frozen sentence is `census/round-31/records/preregistration.txt:20` | none — no r31 instrument read a record against the contract it printed under, and the deviation was disclosed only after landing (routed defect 3, `census/round-32/records/preregistration.txt` line 3) | `tools/souji-record-contract.py` plus C3 leg L14, shown able to fail: red arm exits 1 on the r31 record, green arm exits 0 with `lines=22 bad=0` on `census/round-32/records/jj-mtime-clock-run.txt` under `census/round-32/c3-contract.txt` (§Observed). Its own escape survives: both parsers require `RESULT` plus one space (`tools/souji-record-contract.py:44`, `census/round-32/c3-counter-v2.py:93`), so a tab-separated line still passes (wave-1 `SwarmCritic36.md`, open below) |
| enumeration | `census/round-32/c1-enumerate.py:6` makes every maximal digit run in a cell one item; `:84` mints a unit from any `name=` key, digits included, so `census/round-32/c1-items.tsv:26,27,43` carry units `k1` and `r26`; `census/round-32/c1-counter.py:39,207,272` allows one item per `(path, line)`; honest-binding receipts `SwarmExecutor04.md`, `SwarmExecutor05.md`, `deliver-c1-bind-N35-N43-L29.md` | none at freeze — the frozen controls measured adversarial cheapness only (do-nothing, withdraw-all, mechanical binder: `census/round-32/records/controls.tsv`, `controls-a0.tsv`); no control attempted one honest binding per unit class, and the freeze ran before any binding row existed. The C1 target caught it after landing: 17 withdrawals against a cap of 8, and six items with no row (`SCORECARD.md:434-471`) | reject digit-bearing key names as units at `c1-enumerate.py:84`, and add a pre-freeze feasibility leg that binds one item per unit class under the frozen literal rule and must read MATCH under both counters; it fails on N25 (`k1=13`), N26 (`k1=0`) and N42 (`r26=495`) today |
| anchor-selection | `census/round-32/c2-items.tsv:29` freezes T18 on `--baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812`; its last digit-bearing line is the `SUMMARY` carrying `baseline_mismatches` (`tests/fixtures/r20-input-binding.py:105`, incremented at `:88`), a count of closure files differing from the pinned 2026-10-21 revision, which any edit to those files moves — 26 to 31 at the integration commit (`census/round-32/records/amendments.txt:26-29`) | none at freeze — the pre-freeze trial ran every candidate once at base (`census/round-32/records/preregistration.txt:5`), so a revision-sensitive anchor is indistinguishable from a stable one; first observed by wave-1 `SwarmExecutor14.md` (T18 FAIL 48/52) and by the L1's integration reading | a pre-freeze anchor-sensitivity control: in a scratch clone, append one byte to a lane file outside the item's own file set and require the anchor's last digit-bearing line unchanged; T18's line moves, so the item is rejected before it is frozen |
| instrument | `census/round-32/c2-counter.py:174-176` compares one string and one gross creation count, and scored cheat commits `dc318437ce0bfc196818e9ad02ddd8e762af49b8` (scratch inside the clone, caller `TMPDIR` unread) and `e36b78f4bd5fdfa4a970878171ed6efbe4f66ac6` (11 cases skipped, 60 dummy files) as `ITEM T06 PASS` (`SwarmCritic34.md`); `census/round-32/c3-counter.py:262,270` scored a fixture that discards every call status, `fade71abef74fc25edf66515407166c4de9edde0`, at `legs=14 fail=0 f1_entries=5` (`SwarmCritic35.md`) | none before wave 1 — the frozen controls are one-sided (`census/round-32/records/controls.tsv:7,8`: stub selftests `fail=2`, a sourceless C3 entry `fail=6`), i.e. they test stubs that fail, not fixtures that print the expected surface while measuring nothing; the wave-1 attack seats were the first criterion | C3 v2 legs L15-L17 (landed with amendment A1 at `a92e1aae91dbf46c2d7eff713932cfc820186970`) have to flip `fade71ab` and `40d5f590` to FAIL; no committed receipt shows that flip, only the green first reading in `amendments.txt`. For C2, critic34's corrections (count creations under the run's own `TMPDIR`, compare the normalized multiset of stdout lines, bind the clone and `$HOME` read-only) are unlanded and the predicate is byte-unchanged since the preregistration (`git diff 3ec84fc..master` over `census/round-32/c2-counter.py` is empty), so re-applying the two cheat patches is the outstanding falsification |

## Seat-reported failures

Every wave-1 report whose STATUS is FAIL or PARTIAL, from
`grep -m1 '^STATUS:' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/Swarm*.md` (41 reports
carry a STATUS line; 34 PASS, 7 non-PASS, all listed). `resolved@<commit>` names the lane commit that answered the
report; `open` means the defect stands at tip `4e56c48`. Paragraphs are reflowed onto one line; wording is verbatim.

- `.ufo/waves/round-32/w1/SwarmCritic34.md` line 4 — open: STATUS: FAIL — claim C2's frozen pass predicate is satisfiable without the property it claims: two cheat commits score `pass=1` under the real counter (`--only T06`), one of them running zero selftest cases, and one rule-matched item that is absent from the frozen set fails under the same counter.
- `.ufo/waves/round-32/w1/SwarmCritic36.md` line 3 — open: STATUS: PARTIAL — the M1 receipt is honest and reproducible, the reconstructed r31 contract is faithful to its frozen line, and the named dodge "contract edited at REV" is blocked; but the guard pair (tool + C3 L14) is narrower than the frozen catalog it enforces, and one reproduced record shape carries out-of-contract values past all fourteen legs.
- `.ufo/waves/round-32/w1/SwarmExecutor04.md` line 4 — open: STATUS: PARTIAL — all seven items are honestly bound as WITHDRAWN and the frozen target arithmetic holds for them (`unbound=0 mismatches=0 withdrawn=7`, identical under v1 and v2, deterministic, rc=0), but no MATCH binding exists: five cells name no record that holds their integer (A0(a) refuses the only blobs that do) and two carry a digit-bearing unit word (`k1`) that makes any honest literal inadmissible. This consumes 7 of the round's 8 withdrawals, leaving 1 for the other 37 items.
- `.ufo/waves/round-32/w1/SwarmExecutor05.md` line 5 — open: STATUS: PARTIAL — 2 of 8 assigned items (N27, N32) bind MATCH under both `c1-counter.py` and `c1-counter-v2.py`; the other 6 have no admissible observable under the frozen rules (receipts in §Findings 1–3), so I wrote no row for them rather than a `withdrawn:` row whose definition they contradict.
- `.ufo/waves/round-32/w1/SwarmExecutor14.md` line 4 — open: STATUS: PARTIAL — **T17 PASS** (needs one file beyond the named set: `tools/souji-seat-audit.py`); **T18 FAIL 48/52**, and the remaining four failures are structural: its `--baseline` red-before arms execute entrypoint bytes pinned at `12516f7…`, which create scratch under a literal `/var/tmp` before the stub producer, so no revision of live files can satisfy the frozen predicate. Both named fixtures are patched, host-behaviour-identical, and delivered.
- `.ufo/waves/round-32/w1/SwarmScribe26.md` line 5 — open: STATUS: PARTIAL — the `## Gate` draft (24 rows: 3 source ADMIT, 1 entry placeholder, 20 per-entry REJECT), the `### SOURCES touched-row log (old -> new)` skeleton, the `Assimilation:` and `considerthese/` lines and the M1 `## Mistakes` row are delivered, and every source quote was re-fetched from its tag and verified byte-present this run. The entry ADMIT row and its numbers stay placeholders by construction: at read time the C3 entry, its record and its fixture had not landed, and `.ufo/waves/round-32/w1/deliver-sources-rows.md` did not exist, so `S223`/`S224` remain provisional ids.
- `.ufo/waves/round-32/w1/SwarmSimplifier44.md` line 6 — open: STATUS: PARTIAL — the eight structural predicates hold (44 seats; 44 distinct item ids and 44 distinct prompts; roles only from the 10 allowed names; flash 34/44 = 77.3 %; attack 11/44 = 25.0 %; 34/34 scratch tokens under `/fast/scratch/hyaku/souji-r32/`, each inside its own item dir; 44/44 report paths distinct and under `w1/`; zero deliverable-name collisions and zero overlaps among the declared C2 file sets, though D8 shows the realized run has already departed from those sets; every rendered prompt is byte-identical to its `w1-spec.json` item after stripping the three dispatcher-added lines). The "every path absolute" predicate fails on 23/44 prompts, and seven further defects (D2-D8: two shared integration targets, one realized cross-seat edit of a file another item owns, one contradiction with the frozen context, one acceptance command that cannot pass as written, one with unfilled deterministic placeholders, one triplicated attack set, one C2 file list not closed under runtime dependency) need the L1's ruling; the wave is already dispatched (`w1.ready.dispatched` 2026-10-26T05:28:15), so these are wave-2 / integration findings, not pre-dispatch gate failures. No claim predicate, target or counter is contested here.

Disposition evidence, one clause per bullet:

1. `census/round-32/c2-counter.py` is unchanged from `3ec84fc` to `master`, and `census/round-32/records/amendments.txt:29-30` records the cheat as "disclosed, not amended".
2. `tools/souji-record-contract.py` is unchanged from `3ec84fc` to `master` and line 44 still requires `prefix + " "`; `census/round-32/c3-counter-v2.py:93` repeats the same in-scope test.
3. The seven rows landed as withdrawals at `SCORECARD.md:454-460`, but the round's C1 target is missed: the landed block carries 17 `withdrawn:` rows against a frozen cap of 8, and N28-N31, N33, N34 have no row at all (`SCORECARD.md:434-471`).
4. Its two MATCH rows landed (`SCORECARD.md:461-462`); the same sweep shows the remaining six of its eight ids with no row.
5. T18's anchor is revision-sensitive by construction (`tests/fixtures/r20-input-binding.py:105`), and `census/round-32/records/amendments.txt:26-29` records T18 as still failing at the integration commit with no C2 amendment.
6. Scoring narrowed but not closed: `corpus/SOURCES.md:168` now carries S223, `grep -c 'S224' corpus/SOURCES.md` is 0, and the Gate block itself is not landed (`corpus/lessons/round-32.md` absent at `master`); this delivery supplies the `## Mistakes` and seat-carry sections, not the Gate.
7. The audited plan is untracked (`.gitignore:1` ignores `.ufo/waves/`), no landed commit touches a wave spec, and the a2w1 spec is a new file outside those commits' scope.

## Observed

M1 green arm, this seat, read-only, `python3 -B`:

```
$ python3 -B tools/souji-record-contract.py --record census/round-32/records/jj-mtime-clock-run.txt \
    --contract census/round-32/c3-contract.txt
lines=22 bad=0
exit=0
```

Together with the committed red receipt (`lines=17 bad=4`, exit 1) the instrument discriminates on both sides.

## Not drafted here

The `## Gate`, `## Scores`, QUALITY rows, SCORECARD measurements, LOG entry and final-tip receipt belong to the L1's
integration; the C3 Gate draft exists in `.ufo/waves/round-32/w1/deliver-lesson-gate.md` and needs its placeholders
re-pointed at the landed S223 row and the landed entry.
