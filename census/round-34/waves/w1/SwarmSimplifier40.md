# SwarmSimplifier40 — w1 spec hygiene (souji round 34)

## Status
STATUS: PARTIAL — every mechanical gate passes (40 distinct ids/prompts, exactly the policy's 10 proposal roles, attack share 10/40 = 25.0 %, 89 unique `deliver-*` paths all under w1/, all scratch roots equal the item id, no item asks a seat to edit the lane, context carries the pacman guard and tooling authorization), but 4 executor items are dispatched with a `--only` flag the C2 counter does not implement (exit 2), 5 items carry relative paths that do not resolve from the mandated fleet-root cwd, and 2 items write a host `/var/tmp` canary outside the wave's declared write scope.

## Evidence
All analysis read-only over the lane at working-tree tip; lane Python run with `python3 -B`; probe scratch `/fast/scratch/hyaku/souji-r34/SpecHygieneW1/` (removed after receipts).

1. Dispatch scan (`python3 -B` over `w1-dispatch.json`):
   - `taskCall.tasks`=40, distinct `name`=40, distinct `task`=40; registry members=40, names equal, role/item maps consistent, `counts.spawn`=40.
   - roles: `{'executor': 17, 'critic': 4, 'reviewer': 4, 'scribe': 4, 'scout': 3, 'connector': 3, 'mutation-tester': 2, 'sentinel': 1, 'revenger': 1, 'simplifier': 1}`; attack roles = 10/40 = **0.25**; no `planner`.
   - Allowed set check: `scripts/hyaku/ufo-wave-policy.json:104-115` `proposalRoles` = scout, reviewer, critic, connector, sentinel, executor, mutation-tester, revenger, simplifier, scribe — identical to the 10 used.
   - delivery paths: 89 distinct `/.../.ufo/waves/round-34/w1/deliver-*`, 0 duplicates; 38 items name ≥1; `SwarmSentinel37`/`SwarmSimplifier40` say "Deliver findings in your report".
   - scratch roots: 40/40 items with scratch references resolve to `/fast/scratch/hyaku/souji-r34/<item>/`; 10 items reference none (read-only review/draft items).
   - context contains `pacman guard`, `Tooling is authorized (operator 2026-10-19)`, `uv tool`, `~/.local/bin`, `RULES.md`.
   - dispatch task text = spec prompt + fixed footer for all 40 (0 mismatches).
2. C2 flag probe (load recorded, Q77):
   ```
   $ cat /proc/loadavg ; python3 -B .../census/round-34/c2-counter.py --root .../souji-shokunin \
       --rev 9c76c7222a8abff027af42e37f0d160d52526bba --base 9c76c7222a8abff027af42e37f0d160d52526bba \
       --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch .../SpecHygieneW1/cnt --only W1,W2
   54.74 32.60 15.91 45/8869 39299
   c2-counter.py: error: unrecognized arguments: --only W1,W2
   rc=2
   54.74 32.60 15.91 54/8892 40021
   ```
   `--help` options: `--root --rev --base --list-rev --scratch --timeout --selftest` (no `--only`).
3. Relative-path probe at the mandated cwd `/home/vgpnk/Projects/shokunin`:
   ```
   $ ls tools/souji-evidence-cache.py tests/fixtures/r34-sandbox-junk.py
   ls: cannot access 'tools/souji-evidence-cache.py': No such file or directory
   ls: cannot access 'tests/fixtures/r34-sandbox-junk.py': No such file or directory
   ```
4. Unscoped `git show` probe: fleet root is itself a repository and does not carry the lane commit:
   ```
   $ git -C /home/vgpnk/Projects/shokunin rev-parse --show-toplevel
   /home/vgpnk/Projects/shokunin
   $ git -C /home/vgpnk/Projects/shokunin show 9c76c722...:tests/fixtures/r14-census-boundary.py
   fatal: path 'tests/fixtures/r14-census-boundary.py' does not exist in '9c76c7222a8abff027af42e37f0d160d52526bba'
   ```
5. `census/round-34/preregistration.txt:135-172` contains amendments A1–A6 (A5 at :165, A6 at :169).

## Findings

1. **HIGH — 4 C2 executor items dispatch an unimplemented flag.** `SwarmExecutor14` (`--only W1,W2`), `SwarmExecutor15` (`--only W3,W4`), `SwarmExecutor16` (`--only N3,N4`), `SwarmExecutor17` (`--only J1,G1,G2,G3,G4,G5,G6`) all pass `--only`; `census/round-34/c2-counter.py:260-266` defines no `--only`, so each primary command dies at argparse with rc 2 (evidence 2). As written those four seats either report a phantom failure or silently fall back to a 13-leg run, quadruplicating the bwrap+strace battery. Location: `.ufo/waves/round-34/make-spec-w1.py:74-77`; rendered `.ufo/waves/round-34/w1-dispatch.json:347,352,357,362`.
2. **MEDIUM — `SwarmExecutor16` digest command has no repository selector.** It is told `` `git show 9c76c722...:tests/fixtures/r14-census-boundary.py | sha256sum` ``; from the mandated fleet-root cwd this reads the fleet repo and fails (evidence 4). Every other item names `-C`; the wave's own contract requires it. Location: `make-spec-w1.py:76`; dispatch `:357`.
3. **MEDIUM — relative paths in executable instructions.** Commands that only resolve if the seat happens to `cd` into the lane: `SwarmExecutor14` ``run `python3 -B tools/souji-evidence-cache.py --selftest` ``; `SwarmExecutor15` `` `bash tools/souji-census.sh --selftest` `` and `tools/souji-verify.sh --selftest`; `SwarmExecutor17` `` `python3 -B tests/fixtures/r34-sandbox-junk.py --counter …` ``; `SwarmConnector30` (`tools/souji-census.sh`, `tools/souji-evidence-cache.py`, `tools/souji-verify.sh`); `SwarmReviewer26` (`census/round-34/`, `tests/fixtures/r34-*`); plus the context's `tests/fixtures/r34-c1-junk.py`, `tests/fixtures/r34-sandbox-junk.py`, `corpus/lessons/round-34.md`, `census/round-34/records/census-start.txt`. Evidence 3. Locations: `make-spec-w1.py:18-40,74,75,77,89,95`; dispatch `:277,347,352,362,407,417`.
4. **MEDIUM — two items write a host `/var/tmp` canary outside the declared write scope.** `SwarmExecutor16` ("place a canary in the REAL /var/tmp before the run and show it byte-identical after") and `SwarmScout28` ("place a canary under the real /var/tmp and show it invisible inside, reappears after") are the only writes the contract does not route to w1/ or `/fast/scratch/…/<item>/`. Both lanes run concurrently in this wave and neither is told a per-seat canary name, so N3's before/after byte-identity reading can race ReconSandbox's bind probe. Locations: `make-spec-w1.py:76,93`.
5. **MEDIUM — `SwarmScribe33` download target contradicts the Contract.** The item says "save the bytes under `/home/…/w1/src-S230.html` — not committed by you", while the Contract says "every clone, work tree, fixture repo and download lives ONLY under `/fast/scratch/hyaku/souji-r34/<YourItemId>/`" (`make-spec-w1.py:30`). It is also the only non-`deliver-*` write into w1/. Location: `make-spec-w1.py:102`; dispatch `:442`.
6. **MEDIUM — amendment-scope inconsistency leaves A5/A6 unreviewed.** Context Goal says "amendments A1-A6"; Contract says "amendments A1-A4 in … are this round's"; `SwarmReviewer26` is told "the amendments A1-A4 are stricter-only". A5 (`preregistration.txt:165`) and A6 (`:169`) are in the freeze but outside the named reviewer's brief and outside the freeze review's stated scope. Locations: `make-spec-w1.py:18,28,89`; dispatch `:277,407`.
7. **LOW — unexpanded `{REV}` tokens.** 65 literal `{REV}` occurrences across `SwarmExecutor01-12` (`at={REV}` from the frozen items file plus argv templates). The counter substitutes at run time (`c1-counter.py:171-178`); the prompt does not, so the history-walk step opens with an unresolved placeholder and never states that `{REV}` means `--rev`. Location: `make-spec-w1.py:69`; dispatch `:282-337`.
8. **LOW — undefined `$D` in the clone recipe.** "Clone with `` `git clone -q --no-local {L} "$D/c" && git -C "$D/c" remote remove origin` ``" never assigns `D`; unset expansion targets `/c`. Applies to all 40 seats. Location: `make-spec-w1.py:30`.
9. **LOW — jj symlink instruction is ambiguous against the host guard.** `SwarmExecutor01-12` say "PATH=/usr/bin:/bin plus a jj symlink if present" without saying the symlink lives in a scratch `bin/`; the inherited host guard forbids creating anything in `~/.local/bin` or any other PATH directory, so a literal reading violates it. Location: `make-spec-w1.py:69`.
10. **LOW — G5 wording is broader than the code.** `SwarmExecutor17` is told to "show none touches both namespaces"; `c2-counter.py:220-229` only intersects `{SCORECARD.md, SKILL.md}` with `{c2-legs.tsv, c2-counter.py}`, so a commit touching `census/round-34/c1-counter.py` and `SCORECARD.md` passes — the freeze commit itself touches both counters and passes. Location: `make-spec-w1.py:77`.
11. **LOW — frozen prose vs junk-fixture CLI.** `c2-legs.tsv:23` describes J1 as `r34-sandbox-junk.py --tool <path> --counter …`; `tests/fixtures/r34-sandbox-junk.py:58-59` accepts only `--counter` and `--scratch` (no `--tool`). The wave's command follows the legs *argv* (valid) but the frozen kind text names a flag that does not exist, which will mislead `SwarmExecutor17` and `SwarmReviewer24` when they reconcile prose with code.
12. **Observation, not a defect.** Attack share is exactly 25.0 % (10/40): the gate is met with zero margin, so any single reseat to a non-attack role drops the wave below 25 %. `SwarmSentinel37`/`SwarmSimplifier40` name no build/attack deliverable — consistent with their sentinel/simplifier cards and with "deliver findings in your report".

## Deliveries
None — this item's delivery is the report itself (`.ufo/waves/round-34/w1/SwarmSimplifier40.md`). Probe scratch `/fast/scratch/hyaku/souji-r34/SpecHygieneW1/` created and removed; no lane, fleet-root or PATH path was written.
