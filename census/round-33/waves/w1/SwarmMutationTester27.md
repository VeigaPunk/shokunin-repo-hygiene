# SwarmMutationTester27 — C1 counter mutation test (round 33 w1)

## Status

STATUS: PASS — all 8 assigned mutants of the frozen C1 counter were built and run against all three controls; 7 killed, 1 survivor (M7, RESULTS-count check: unkillable and unexploitable under the frozen rules, missing control named). One attack on the pristine counter itself was reproduced (M6b: argv-correction restatement backed by an unrelated command's output). Lane counter bytes unchanged: sha256 `a180c3fdbfb4e0a4becf7cfbbf1c9e270e5085e3a3cb9bf2cc4936a536c5bc38` before and after. No tool installs were performed (none needed).

## Evidence

Environment: git 2.56.0, jj 0.45.1 (matches the records, so K24/K25 reproduce; P-a0 below equals the preregistered do-nothing reading exactly).

Scratch (removed at end of run): `/fast/scratch/hyaku/souji-r33/MutateC1Counter/` — clone `c` of the lane (`git clone -q --no-local`, origin removed, `rev-parse --show-toplevel` = the clone, verified before any commit), detached at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`; pristine counter copy `c1-counter.orig.py` (sha256 equal to the lane file); mutants `m1.py`–`m8.py`; control/cheat commits on detached branches `refs/heads/mut-*` (refs added after the first batch showed the counter's per-item `git clone` only fetches ref-reachable commits; see Finding 5).

Counter invocation shape (all runs):
`python3 -B <counter> --root <scratch-clone> --rev <rev> --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch <dir> [--only <ids>]`

Control revs (all built in the scratch clone on top of `2d9bca55`, throwaway identity `scratch <scratch@invalid>`):

| rev | purpose | sha (full40) |
|---|---|---|
| base do-nothing | control (a) | `2d9bca55a9f042a2c9ed60a797a8069e74c41f46` |
| J junk control | control (b): the four L1 rows of `census/round-33/records/feasibility.txt` "C1 junk control" rebuilt verbatim (K04 substring `ids=7/7`, K16 true line `selftest=15/15`, both cause `98e5203d45b4e419a9e72801733d93303acc7ebd`; K05 valid cause `ddb73474433977ff54b015ac3e77669ff2537353`; K18 valid argv-correction cause `07f83e69979b1032f9de4fe876739a8dccc7242b`) | `da09f10f6ea7b1aa8c189175ad2a773be5f89cec` |
| M1 cheat | original SCORECARD bytes edited (line 155 `→ 5/5;` → `→ 7/7;`) | `8bddc853b7edd1a8cbdf42b3beed544f394fdb39` |
| M2 cheat | 5 rows, true complete digit-bearing output lines, junk cause `98e5203…` | `0f03407673d4e32712bf56703b651e5c095e7b3e` |
| M3 cheat | K18 row, run = corrected argv, statement `pass=9` (substring), valid cause `07f83e69…` | `f1bf9bb3404661fcd877a1caf182453fb79dc1bf` |
| M4 cheat | K05 row, valid cause `ddb7347…`, exit cell `3` (actual rc 0) | `0eb625bb4861dbe349be80a5f8deedaf0557918c` |
| M5 cheat | K05 valid row + duplicate junk K05 row | `2f26e0e637b7a3a56e2ef742631b9b2e96e255b6` |
| M6a cheat | K18 row, run = `python3 tools/souji-rev-pin.py --selftest` (unrelated command), digit-free statement `CASE pass durable-clean-accept` | `c52851af96ff2ec656e8dd7b4afe644cb46ed853` |
| M6b attack | same but digit-bearing statement `SUMMARY total=11 failed=0` (rev-pin's own output) | `12063c0788140891c873657813dca46c9bcf5f18` |
| M7 cheat | K24 row, run = K24 fixture, statement `RESULTS:census/round-31/records/jj-object-clock-run.txt:16` (record has 17), cause = line-424 writer `f950267893340096964ae8ceb7116f6789d7c87b` | `46ea2dc13be83c43815ebee3e341b3dc2259689e` |
| M7b probe | same shape for K25 (count 21 vs record 22), cause = line-488 writer `9da5e9a559f76ecbd275a9685226883d334dc8f9` | `c762221dc72569e8cf11d0f8f02f9ca064d610ce` |
| M8 cheat | K05 row, valid cause, line cell `SCORECARD.md:999` | `56f89a06395edcd3accaea8c25ae52bf9346515d` |

Pristine anchors (all executed this run):

- (a) do-nothing, full 24 items, rev = list-rev = `2d9bca55…`: `SUMMARY items=24 agree=19 mismatches=5 restated=0` — MISMATCH exactly K04 K05 K16 K17 K18, matching the preregistration and `feasibility.txt` v2 control line for line (rc 1).
- (b) junk rev J, `--only K04,K05,K16,K18`: `SUMMARY items=4 agree=2 mismatches=2 restated=4` — K04 and K16 `MISMATCH BAD-CAUSE(original at parent=False at cause=False; need True/False)`, K05 and K18 AGREE; reproduces the L1 junk-control receipt semantics (rc 1).
- Cheat revs under the pristine counter: M1 → `COULD-NOT-EVALUATE SCORECARD.md at --rev does not start with its --list-rev bytes (not append-only)` (rc 2); M2 → 5× `BAD-CAUSE(…)` (rc 1); M3 → `MISMATCH … statement is not a digit-bearing output line` (cause checks passed; rc 1); M4 → `MISMATCH rc=0 expect_exit=3 statement is an output line` (rc 1); M5 → `MISMATCH BAD-ROW(duplicate restatement)` (rc 1); M6a → `MISMATCH … statement is not a digit-bearing output line` (rc 1); M6b → `ITEM K18 AGREE restated rc=0 … statement is an output line last=SUMMARY total=11 failed=0`, `SUMMARY items=1 agree=1 mismatches=0` (rc 0 — see Finding 2); M7 → `MISMATCH BAD-CAUSE(the row's own argv held at the cause)` (rc 1); M7b → same BAD-CAUSE for K25 (rc 1); M8 → `MISMATCH BAD-ROW(line or kind)` (rc 1).

Mutant hashes (before/after pairs; the "before" is `c1-counter.orig.py` = lane bytes `a180c3fd…`, restored/untouched throughout — mutants are separate files):

| file | sha256 |
|---|---|
| m1.py | `a51d0b18ec5c3cbdf6a1acad9df0990ba3f6280fd2f18768867934677fbb2834` |
| m2.py | `0f734867c1aba60641bd4c09c27ee210c680cdedacc30d0e0e10f55ca0841b36` |
| m3.py | `4046ed212c5978eb06d78b3dc835463683aef94b2317ba33806ec47532c92fce` |
| m4.py | `0a6febc686a9fef234628c349ba91c87b9d0971e1d6a9755e72917ba6e8d64af` |
| m5.py | `ed77eb677bdfc4b9e020054366645cfb98e58c09fbf4e8027e41a3b41c8d0989` |
| m6.py | `861171f0ee5226ea1e20c2c22b754c8a6156f40e914296ecc1545b29a89a4c58` |
| m7.py | `8ff4b1619b257fb842d10fa90ab6e74bd051e835a6b6a082befa47508b923678` |
| m8.py | `da783d18918a70cfc1c722858bf27a4852133b41e7dbeea2bf384fe6ea890f61` |

## Findings

1. **M7 SURVIVOR — the RESULTS-count check is unreachable by any admissible control and unexploitable for a false PASS.** Location: `census/round-33/c1-counter.py`, `results_pred`, `if len(want) != n: return False, f"record has {len(want)} RESULT lines, stated {n}"`. No control kills it: (a) and (b) behave identically to pristine (the count check only fires for a *restated* row whose statement is `RESULTS:<path>:<n>` with a *valid* cause, and both controls' rows die earlier), and the crafted cheats (c) die at the cause machinery before the count check matters: `P-c-M7`/`c-m7` and `P-c-M7b`/`c-m7b` all print `MISMATCH BAD-CAUSE(the row's own argv held at the cause)`. The missing control is "a valid-cause restatement row with a wrong `RESULTS:<path>:<n>` count". It is not constructible under the frozen list-rev: K24's record+fixture landed in one lockstep commit (`1baf4da02b71b012ee2426ea7c309496c0c3aca0`) and K25's in `a92e1aae91dbf46c2d7eff713932cfc820186970`, neither touched again (`git log` over both paths shows exactly one commit each), so no value-drift cause exists (the frozen predicate holds at every commit where the record exists and fails only before it, when the record is unreadable); and the SCORECARD row-writer commits (`f950267…` for line 424, `9da5e9a…` for line 488) postdate their records, where the frozen argv already held — measured, not inferred. Cheapest kill: none exists as a row/commit under the frozen rules; a future preregistration would have to enumerate an item whose record and fixture histories diverge (a fixture-change commit predating its record-update commit) so a valid-cause wrong-count junk row becomes admissible at freeze time. Until then the check is redundant defense-in-depth — it cannot be hit, but it also cannot be exploited (every wrong-count row is rejected by the cause machinery first, mutant or not).
2. **ATTACK on the pristine counter (reproduced, not a mutant): the argv-correction run cell is not tied to the item's command.** Location: `census/round-33/c1-counter.py`, `judge()` argv-correction branch (it validates only that the cause wrote the SCORECARD line and that the *frozen* argv failed at the cause) plus the final statement match. Reproduced state: rev `12063c0788140891c873657813dca46c9bcf5f18` restates K18 with run `` `python3 tools/souji-rev-pin.py --selftest` `` (souji-rev-pin's selftest — unrelated to K18's fixture), statement `` `SUMMARY total=11 failed=0` `` (rev-pin's own output line), cause `07f83e69…`; the pristine counter prints `ITEM K18 AGREE restated … statement is an output line last=SUMMARY total=11 failed=0`, `SUMMARY items=1 agree=1 mismatches=0`, exit 0. So any argv-broken item can be restated green on any green command's output; the digit rule does not block this (the statement is digit-bearing). Reported as an attack with reproduced state; the frozen counter was not changed and no change is proposed here.
3. **M1 residual: dropping the append-only check yields no false PASS.** `c-m1` (rev `8bddc85…`, edited original bytes): the mutant proceeds where pristine says `COULD-NOT-EVALUATE … (not append-only)` (rc 2 → rc 1), but still reports `mismatches=1` — the cause and statement machinery are intact, and SCORECARD.md at the list-rev contains no `| Kxx |`-shaped rows that an early-inserted section heading could capture (grep over the list-rev blob: none). The check's protective value is the protocol refusal itself; killed by cheat (c) as a strictness divergence, with no verdict-level exploit found.
4. **Check-order note: `BAD-CAUSE` fires before statement matching, so the junk control's K04 row is double-protected.** `b-m3` (substring mutant) still rejects K04's junk row via `BAD-CAUSE` — the junk control alone would NOT kill M3; the kill required the valid-cause substring cheat (`c-m3`). The junk K04 leg is redundant with the K16 leg for killing M2 (K16 flips on `b-m2`, K04 stays MISMATCH on its statement).
5. **Counter operational note: `run_item`'s per-item `git clone` only sees ref-reachable commits of `--root`.** A `--rev` reachable only as a detached commit in the root's object store yields `RUN-FAILED(git failure)` / `COULD-NOT-EVALUATE … unable to read tree` (hit and fixed during this test by adding `refs/heads/mut-*`). Landing commits on master are unaffected; noted because a future seat running the counter at an unadvertised rev will misread RUN-FAILED as item failures.

## Attack log

Mutant × control matrix (a = do-nothing rev `2d9bca55…`, `--only K04,K05,K16,K17,K18`; b = junk rev `da09f10…`, `--only K04,K05,K16,K18`; c = the mutant's cheat rev). "same as pristine" = byte-identical verdict lines to the pristine run on that control.

| mutant | (a) base do-nothing | (b) L1 junk rows | (c) crafted cheat | verdict |
|---|---|---|---|---|
| M1 drop append-only check | 5 mismatches, same as pristine | 2 mismatches, same as pristine | rev `8bddc85…`: pristine `COULD-NOT-EVALUATE (not append-only)` rc 2 vs mutant proceeds rc 1 (`mismatches=1`) | KILLED (no false PASS reachable — Finding 3) |
| M2 drop cause execution | same as pristine | K16 flips to AGREE (`mismatches=1`) — junk true-line/wrong-cause row accepted | rev `0f03407…`: FALSE PASS, `mismatches=0` rc 0 (all 5 AGREE; K18 via exit cell `2` + error-line statement) | KILLED |
| M3 accept substrings | same as pristine | same as pristine (BAD-CAUSE masks the statement check) | rev `f1bf9bb…`: FALSE PASS rc 0 (K18 `pass=9` substring of `cases=9 pass=9 …`, valid cause `07f83e69…`) | KILLED |
| M4 skip exit comparison | same as pristine | same as pristine | rev `0eb625b…`: FALSE PASS rc 0 (K05 exit cell `3`, actual rc 0, valid cause `ddb7347…`) | KILLED |
| M5 ignore duplicates | same as pristine | same as pristine | rev `2f26e0e…`: FALSE PASS rc 0 (valid K05 row + junk duplicate; mutant judges `rows[0]`) | KILLED |
| M6 drop digit requirement | same as pristine | same as pristine | rev `c52851a…`: FALSE PASS rc 0 (K18 digit-free statement `CASE pass durable-clean-accept` from an unrelated rev-pin run) | KILLED |
| M7 RESULTS count loose | same as pristine | same as pristine | revs `46ea2dc…` (K24/W424) and `c762221…` (K25/W488): both pristine and mutant print `BAD-CAUSE(the row's own argv held at the cause)` — no divergence reachable | SURVIVED (Finding 1) |
| M8 skip line-number match | same as pristine | same as pristine | rev `56f89a0…`: FALSE PASS rc 0 (K05 row with line cell `SCORECARD.md:999`, valid cause) | KILLED |

Pristine-counter attack (not a mutant): rev `12063c07…` — K18 restated on `python3 tools/souji-rev-pin.py --selftest` output `SUMMARY total=11 failed=0` → pristine `AGREE`, rc 0 (Finding 2).

Per-mutant (a) runs all printed the pristine 5-mismatch column (`SUMMARY items=5 agree=0 mismatches=5` for every m1–m8); per-mutant (b) runs matched pristine except `b-m2` (K16 flip, the kill).

## Deliveries

- `.ufo/waves/round-33/w1/SwarmMutationTester27.md` — this report (the only file written in the lane).

Restoration evidence: lane counter sha256 `a180c3fdbfb4e0a4becf7cfbbf1c9e270e5085e3a3cb9bf2cc4936a536c5bc38` identical before and after the run; mutants live only in scratch copies; the scratch clone's commits are throwaway (`scratch <scratch@invalid>`) and never pushed; scratch dir removed at end of run.
