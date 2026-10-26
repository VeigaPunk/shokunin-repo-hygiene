# Round 33 w1 — mistake-class recurrence scan (seat SwarmConnector45)

Scope: `## Mistakes` tables and Step-1 / `## Routed defects` lists in
`corpus/lessons/round-28.md` … `round-32.md` and the five `round-*-verifier-spotcheck.md`
files, mapped against the frozen round-33 design (`census/round-33/preregistration.txt`,
`c1-counter.py`, `c2-counter.py`, `c1-items.tsv`, `c2-legs.tsv`, `records/feasibility.txt`,
`corpus/QUALITY.md` Q70–Q74). All design artifacts read at lane commit
2d9bca55a9f042a2c9ed60a797a8069e74c41f46 (frozen preregistration); lane tip observed read-only
at a416d0b26495ce78b76ea82316533bd8a9ef368c. Analysis only: no counter was executed, no
lane bytes were written.

## Part 1 — mistake-class inventory (rounds 28–32)

Classes are named as in the lessons' Mistakes tables where a table row exists; spot-check-only
classes are marked (sc).

| # | class | rounds | what it was (location) |
|---|---|---|---|
| C1 | stale-premise | r28, r30 | pointer/instrument premise disagrees with the measured object's real shape: r28 base `c1-before.tsv` `findings=2` vs Q57 `q57=PASS` (`round-28.md` Mistakes); r30 A1 regex `\terr=` vs emitted ` err=` made `regress_full=same` unprintable (`round-30.md` Mistakes) |
| C2 | contract | r31, r32 | frozen sentence/prose disagrees with enumeration or record: r31 "23 literals" vs `unbound=22` (`round-31.md` Mistakes); r32 record printed `arm=reflog-only` outside the frozen `solo`/`descendant` set, disclosed only after landing (`round-32.md` Mistakes; r32 spot-check Step-1 D1; r31 routed 3) |
| C3 | enumeration | r32 | derived enumeration minted items from maximal digit runs and `name=` keys; one item per `(path,line)` (`round-32.md` Mistakes; r32 routed 1) |
| C4 | anchor-selection | r32 | T18 frozen on `--baseline 12516f7…` whose last digit-bearing line is a `baseline_mismatches` count of closure files — any edit to those files moves it (26→31 at integration) (`round-32.md` Mistakes; r32 routed 2) |
| C5 | flaky anchor | r32 | T12 base readings disagreed run to run under strace wall-time budgets on `/fast` (`round-32.md` Mistakes) |
| C6 | instrument / vacuous | r29, r30, r31, r32 | target met without honest work: r29 composite no-work state + K2 empty marker (`round-29.md` Mistakes); r30 combined stdout+stderr observation was a usage banner; C2/C3 met by stub gate + byte-recognising fixture (`round-30.md` Mistakes); r31 C1 non-count record text, C3 fixture that cats a typed record, C2 v1 "gates that read nothing", v2 base fingerprint + copied 21-token table, v3 envelope echo (`round-31.md` Mistakes); r32 counters scored cheat commits as PASS; C3 beatable by a constants fixture, C2 predicate accepted a fabricated anchor (`round-32.md` Mistakes; r32 routed 5) |
| C7 | harm (digest-pinned consumer) | r32 | r32 C2 edits turned `r22-result-oracle`, `mutation-adequacy.py` (sha256 pin at `run-acceptance.py:503`) and the r15 frozen pin red at the tip; the preregistration's no-harm watch was a wave-2 sweep that never ran (`round-32.md` Mistakes; r32 routed 2 bullet 2) |
| C8 | harm (write-scope widening) + misroot | r32 | `--out` guard moved from fixed `/var/tmp/` to caller `TMPDIR`; the L1 then reproduced the attack against the real fleet root and wrote a receipt there (`round-32.md` Mistakes) |
| C9 | number-drift | r29 | prose said "two malformed newline-path records"; committed bytes said 152 absent records (`round-29.md` Mistakes; r28 routed 2) |
| C10 | reference-drift | r29, r30 | S215 `used-by` names a non-citing entry (+5 one-directional pairs); r29 report cited `final-tip-measure*` before it landed (r29 spot-check Step-1 D1); r30 `SCORECARD.md:322` cited a wave path absent at C2 landing (`round-29.md`, `round-30.md` Mistakes; r29 routed 1; r30 routed 5) |
| C11 | attribution | r29 | lane self-ruled the r28 C2 target missed at 139 although the frozen clause excluded S215 (`round-29.md` Mistakes; r28 routed 6) |
| C12 | landing | r30, r31 | committed seat STATUS failures went uncarried: the gate read only the gitignored `.ufo/waves/` tree (`round-30.md`, `round-31.md` Mistakes; r28 routed 3) |
| C13 | record | r31 | unquoted heredoc executed four backticked spans and dropped them from A1/A3 text (`round-31.md` Mistakes) |
| C14 | disposition | r31 | carries not honest per entry: 7 wrong `resolved@` + 3 should-be-resolved of 26 (r26), 3 wrong of 29 (r27), 3 wrong + 2 should-be-resolved of 19 (r28) (`round-31.md` Mistakes) |
| C15 | scope | r29, r30 | r29 scratch `push` into lane `master` via `--no-local` origin (restored, disclosed); parked r26 seat woke on a mis-addressed message and edited its tracked report; r30 admitted entry carried sentences stronger than its record (`round-29.md`, `round-30.md` Mistakes; r29 routed 7) |
| C16 | recording (sc) | r28–r32 spot-checks | green fixture runs not committed (r29 routed 2/D3), imprecise reject reason (r29 D4), missing cross-domain line (r29 D2), report said `findings=0` with no committed tip run (r32 Step-1 D2 / routed 3), "26 files" vs 27 (r32 Step-1 D3), placeholder-id `source:` line (r32 Step-1 D4 / routed 4) |

## Part 2 — exposure of the round-33 frozen design

Verdicts: CLOSED (a named design element closes the class), PARTIAL (closed for one claim or
mechanism, open for another), OPEN (no design element addresses it), N/A (class is lane-process,
outside the two claims).

| class | verdict | closing design element / failure to close |
|---|---|---|
| C1 stale-premise | CLOSED | Q70(a) (`corpus/QUALITY.md:175`): a feasibility leg must reach the item-level target under the frozen counters before freeze — both claims have one (`records/feasibility.txt`: C1 leg at 190b4b1, both restatement kinds AGREE; C2 leg at 6a409e1, O2/O4 PASS). Controls re-ran at the preregistration commit into `records/controls.txt` (lane commit 3aec290). The predicate sentence is identical in plan, code and receipt label (`preregistration.txt`, both claims), and predicates match the live run's whitespace-collapsed output, not a derived shape. |
| C2 contract | CLOSED | Same sentence in plan/code/receipt for both predicates; items and legs are frozen TSVs read at `--list-rev`, never at `--rev` (`c1-counter.py` `load_items`; `c2-counter.py` `blob(root, a.list_rev, LEGS_PATH)`), so prose cannot drift from the measured set. The preregistration's before-state numbers are quoted verbatim from the committed `feasibility.txt` (e.g. `SUMMARY items=24 agree=19 mismatches=5 restated=0 rev=b900260…`), a seat can diff them byte-for-byte. Amendments are stricter-only, logged, and only before the first wave seat scores (`preregistration.txt` `== Amendments`). Q72 (`QUALITY.md:178`) is the r31-routed-3 guard, carried forward. |
| C3 enumeration | CLOSED | The r32 derived digit-run enumeration is replaced by a hand-frozen 24-row TSV with an explicit inclusion/exclusion rule in its header and documented unused ids (`c1-items.tsv` header: "Ids K09 and K10 are unused"). C2 legs are likewise a frozen 4-kind TSV (`c2-legs.tsv`). The counters refuse malformed leg lines (`c2-counter.py` `cne(f"malformed leg line: …")`). |
| C4 anchor-selection | CLOSED for C1 / PARTIAL for C2 | C1: Q70(c) (`preregistration.txt`: "no item's anchor counts lane files; K22 reads fixed historical revisions only") plus executed restatement causes. C2: the O legs measure behaviour (exit + normalized last digit-bearing line + creation counts), not counts of lane files — but the six G guards pass iff rev output equals a live re-run of the base output. Later lane traffic that legitimately moves a guarded count (e.g. `G2` `"survived": 7` over a growing corpus, `G6` `total=29` if census checks change) produces `harm>0` at the tip and C2 MISSES without any C2 fault. The preregistration accepts this deliberately (`== Separability`: coupling "shows up in the readings"), so the class re-enters inverted — as a false-positive anchor, not a game. |
| C5 flaky anchor | CLOSED | Q70(b): three base runs must print identical exit + last digit-bearing line before freeze — recorded for both counters (`feasibility.txt`: C1 v1 runs 1–3 identical verdict columns; C2 v1 three runs identical LEG lines; v2 do-nothing agrees). Residual, bounded: the counters re-run base legs live at measure time (`run("base", …)` in `c2-counter.py`; `holds(… parent/cause)` in `c1-counter.py`), and normalization maps `<TMP>`/`<HEX>`/`<DUR>` only; wall-time-sensitive tools could disagree between freeze-time and landing-time base. Q70b plus the normalization is the design's whole defence. |
| C6 instrument / vacuous | PARTIAL | C1: every item executes in a private clone at the measured rev; a restatement's statement must be one complete digit-bearing line of that run's own output; the cause is executed (value drift: True at parent, False at cause, cause touches an item file; argv correction: cause wrote the row and the row's argv already failed there) (`c1-counter.py` docstring + `judge`). Junk controls recorded pre-freeze: substring statement and true-line/non-causal commit both `BAD-CAUSE` at 65812db. C2: legs execute the real tools under bwrap/strace; O1 has the creation-count condition (`w1 * 2 >= w0`) aimed at a tool that "stops its work to dodge the sandbox"; do-nothing at base fails all five O legs (recorded 3×). NOT closed: `sandbox-nt` legs O2/O3 carry "no strace wrapper and no creation-count condition" (`c2-legs.tsv` header); their work proof is the last line itself, so a tool edited to print the base `SUMMARY total=20 failed=0` without doing the work satisfies O2's predicate. What stands against it: O3 is itself the Q73 re-pin instrument; G4/G5 bind the r15 frozen-pin digests of `tools/souji-census.sh` and `tests/fixtures/r15-census-config.py`, so any byte change to those tools forces the declared re-pin act (its own commit, G4-red reading of the repair commit recorded, not hidden). The trade is disclosed (nested ptrace defeats the fixture's own strace probe; `feasibility.txt` "L1 feasibility"), but it is exactly the seam r32 routed defect 5 pointed at, narrowed rather than sealed. |
| C7 harm (digest-pinned) | CLOSED | This is C2's subject. G1/G2 pin `souji-evidence-cache.py` (via `run-acceptance.py:503`), G4/G5 the r15 frozen pin over `tools/souji-census.sh` / `r15-census-config.py`, G3 the cache's own fixture, G6 the census-hygiene consumer. Q73 (`QUALITY.md:178`): a digest pin of a live tool is regenerated only by its own committed script at the candidate; the C2 landing commit is defined as the re-pin commit; the r32 routed-6 hygiene point (re-pin as its own committed act) is answered by that landing-commit definition. |
| C8 write-scope widening / misroot | CLOSED | O1/O2/O3 are precisely the misroot class executed: `/tmp`, `/var/tmp`, `/dev/shm` read-only-empty inside bwrap, `TMPDIR` a scratch dir. Q74 (`QUALITY.md:179`) keeps every base refusal and confines attack reproduction to a fake fleet root inside scratch. Q71 keeps the fix to the scratch root ("the fix is the scratch root, not a widened skip"), the r32 lesson's exact failure. |
| C9 number-drift | CLOSED | All counts in the preregistration are machine-printed counter lines quoted from committed `feasibility.txt` bytes (24/19/5; `O4 … 10 failed`; `O5 … 2 failed`; `legs=11 pass=0 fail=5 harm=1`), re-verifiable by any seat. Nothing is hand-counted into the contract. |
| C10 reference-drift | CLOSED at claim level | Restatement statements must be output lines of the executed run; items/legs name only lane-committed paths read at `--list-rev`; causes are executed commits. No frozen artifact cites a wave path. Lane-process residue (seat reports citing uncommitted captures) is governed by Q65-class discipline, not by these claims. |
| C11 attribution | CLOSED at claim level | Predicate, target, items, legs, controls and kill rules are all frozen at the preregistration commit before any wave seat scores; the do-nothing, junk and feasibility controls are committed pre-freeze (`records/feasibility.txt`, lane commit 3aec290). A stricter-only amendment is the L1's alone and logged with time and reason. Report-level readings remain the non-author spot-check's to police. |
| C12 landing | N/A (not claimed) | r33 claims C1 currency + C2 scratch only. The committed-report discovery (r28 routed 3, r30 C2) is out of scope; this round does not close it. |
| C13 record (heredoc) | N/A | Lane-process mistake; no design element, none needed for the claims. |
| C14 disposition | N/A | Human-audit class by r31's own finding; no instrument closes it, this round adds none. |
| C15 scope (origin push / stray edit) | CLOSED at seat level | The wave contract itself: clone with `--no-local`, `remote remove origin` at once, throwaway identity only, write scope confined to `.ufo/waves/round-33/w1/` — the r29 routed-7 fix embedded in every seat's instructions. Not a claim element. |
| C16 recording | PARTIAL (process) | The wave contract requires committed receipts before citation and verbatim quotes; the C2 landing-commit rule requires the repair commit's G4-red reading be recorded, not hidden. The final-tip receipt commitment (r32 routed 3) still depends on the L1 landing it — see Part 3. |

## Part 3 — residual exposures the frozen design does not close

1. **Receipt commitment is process, not claim (class C16/r32 routed 3).** The predicate is a
   printed counter line re-runnable by any seat, so a falsely claimed reading is falsifiable —
   but the design cannot force the landing/tip receipts to be committed before the closure report
   cites them. Exposure sits with the L1 + spot-check, unchanged from r32.
2. **C2 guard anchors can false-positive on later lane traffic (class C4 inverted).** Six guards
   compare rev output to a live base re-run; any post-landing commit that legitimately changes a
   guarded count kills C2 at the tip. Accepted by the Separability clause, but it means C2's
   "harm=0" is hostage to lane traffic after its landing commit, not only to C2's own diff.
3. **sandbox-nt seam (class C6).** O2/O3 predicates are satisfiable by a base-output mimic; the
   closing elements are the G4/G5 digest pins + Q73 re-pin sequencing, which bind the tools the
   fixtures execute, not the fixture output itself. A constants-cheat confined to
   `tests/fixtures/r15-census-config.py`'s printed line would have to re-pin to land — the act
   the design forces into the open — but the O2 leg alone does not catch it.
4. **Environment flake is lethal by design.** Both kill rules have no exclusion clause; a CNE
   (exit 2) at either point is MISSED (`preregistration.txt`). Q70(b) is the only defence
   against host/tooling drift between freeze and scoring; K24/K25 depend on `jj 0.45.1` /
   `git 2.56.0` being present.

## Verification

- All quoted classes traced to bytes opened this run at
  `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-{28,29,30,31,32}{,-verifier-spotcheck}.md`
  (Mistakes tables at lines 31/75/61/93/73; routed-defect lists at 110/121/129/126/128).
- Design elements traced to `census/round-33/{preregistration.txt,c1-counter.py,c2-counter.py,c1-items.tsv,c2-legs.tsv}`,
  `census/round-33/records/feasibility.txt`, `corpus/QUALITY.md:175-179`.
- Read-only git only; lane tip observed at a416d0b (C1 restatement rows landed), worktree clean.
- No counter executed (analysis seat); no `[INFERENCE]` items except: exact behaviour of
  post-landing lane traffic under C2 guards (item 2 of Part 3) is a risk statement, not an
  observed failure.
