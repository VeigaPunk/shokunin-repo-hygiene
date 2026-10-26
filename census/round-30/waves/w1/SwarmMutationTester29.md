# SwarmMutationTester29 — C2 counter mutation probe (r30 wave 1)

## Status
STATUS: PASS — all 8 assigned mutants executed in scratch; 7 killed (2 by the committed do-nothing receipt, 1 by the junk-state receipt, 4 by constructed states, incl. 2 full false-green PASSes), 1 survivor (m7, equivalent mutant). Pristine counter reproduced the committed do-nothing receipt byte-exactly; lane bytes untouched (sha256 before == after).

## Evidence
Rig: private `git clone --no-local` of the lane (origin removed), worktree verified `rev-parse --show-toplevel` == clone; all scratch under `/fast/scratch/hyaku/souji-r30/MutateC2Counter/` with `TMPDIR` exported there; mutants are exact-replacement patches of a scratch copy of `census/round-30/c2-counter.py` (each replacement asserted count==1); lane file never modified.

Baseline (pristine counter, `--root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --fleet-root /home/vgpnk/Projects/shokunin`):
```
SUMMARY reports=0 cne=1 dangling=3 other=0 fixture=fail redarm=fail regress=same rev=9420341d9a814cb6089c25fb03a4cc9b23dc0d1b   (rc=1)
```
Byte-equal to the committed `C2-do-nothing(base)` receipt in census/round-30/records/controls.tsv:3. Baseline PASS → mutant verdicts are conclusive.

Junk-state reconstruction: the committed `C2-junk` rev `2adeb3c115675126e034fe919546f87e67c3f382` is NOT an object in the lane repo (`git cat-file -t` → exit 128), so the junk state was rebuilt in scratch (stub gate printing `checked_reports=86`, fake fixture printing `CASE D1..D7 PASS` + `cases=7 pass=7 control=FALSE-GREEN-REJECTED`, committed as db156ef836bdf1f9b280ac6c976ae3fbfcb93497 in the scratch clone; counter run with `--root <scratch clone>`). Pristine counter on it:
```
SUMMARY reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=fail regress=differs rev=db156ef836bdf1f9b280ac6c976ae3fbfcb93497   (rc=1)
```
Field-for-field equal to the committed `C2-junk` receipt (controls.tsv:8) modulo rev. Sharper states built for probes the committed controls cannot reach:
- junk2 `1f3e07ab34231cb3336cb323bfacb76ab870b915` — real base gate with a round-29-only override (findings=[], checked_reports=86, error=None); `--selftest` and r16 fixture untouched → pristine prints `... fixture=ok redarm=fail regress=same` rc=1: REDARM is the only failing leg.
- k5b `51261c8c23a470359d03c3d3db4b37ac87b87378` — junk2 + selftest digit patch (`passed + 100`, rc unchanged) + fixture that discriminates base vs rev tool → pristine prints `... fixture=ok redarm=ok regress=differs` rc=1: REGRESS is the only failing leg.
- k2-nocase `efd53802a09f3e4a5ace5532a239999d046bca48` — fixture without the `CASE D*` lines → pristine `fixture=fail`.
- k3-accepted `ea930d20d1b6cd93ec9ddc13cbdb51568ca0a560` — fixture with `control=FALSE-GREEN-ACCEPTED` → pristine `fixture=fail`.

Constructed full false greens (mutated counter exits 0 on a must-fail state):
```
[m4-skip-redarm / junk2]      rc=0 SUMMARY reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=ok regress=same
[m5-regress-rc-only / k5b]    rc=0 SUMMARY reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=ok regress=same
```
Restoration: lane `census/round-30/c2-counter.py` sha256 `6cd15db9ce0f55552c5cde4e1aa93c48105a4836c3eb1b87ab72b81614d88b41` before and after all runs; scratch dir removed at the end of this seat (no tree left).

## Findings
1. **C2-junk control is not re-executable from committed bytes.** Location: census/round-30/records/controls.tsv:8, quote: `C2-junk(stub gate + fake fixture)`; `git -C <lane> cat-file -t 2adeb3c115675126e034fe919546f87e67c3f382` exits 128 (object absent). The receipt was validated here only by state-class reconstruction (db156ef). The do-nothing row IS byte-exactly reproducible. Not gameable by itself, but a future seat cannot re-run that control against committed bytes — L1 may want the junk state's tree bundle stored alongside the receipt.
2. **REDARM is load-bearing and is the last line of defense for fixture discrimination** (m4, killed by constructed junk2). Counter location: census/round-30/c2-counter.py:102, quote: `rok = bool(bm) and int(bm.group(2)) < int(bm.group(1))`. With redarm skipped, a regress-clean stub + non-discriminating fixture turns the counter fully green (rc=0). The committed C2-junk row kills m4 only as a receipt-field mismatch (`redarm=ok` vs recorded `fail`); its verdict stays fail via `regress=differs`.
3. **The regress leg's digit-line comparison is load-bearing** (m5, killed by constructed k5b). Counter location: census/round-30/c2-counter.py:115, quote: `same = same and s1 == s2`; compared tuple at :114 is `(rc, lastnum(...))`. Comparing rc only lets a gate whose `--selftest` prints changed digits at the same rc pass regress (k5b: full rc=0 false green). The committed controls do not kill m5 (junk-v1 output unchanged under m5).
4. **m7 survived — equivalent mutant (coverage finding, not a counter defect).** Counter location: census/round-30/c2-counter.py:89, quote: `dangling = sum(1 for l in out.splitlines() if l.startswith("LG-DANGLING-PTR"))`; the gate prints finding lines on stdout — tools/souji-landing-gate.py:1151, quote: `print("%s\t%s\t%s" % (f["id"], f["path"], detail))` — so a stdout-only dangling count is behavior-identical on every state constructible from this gate (verified unchanged on do-nothing, junk, junk2). The load-bearing stream case is the opposite one: `COULD-NOT-EVALUATE` goes to stderr — tools/souji-landing-gate.py:1167, quote: `print("COULD-NOT-EVALUATE\t%s" % result["error"], file=sys.stderr)` — and is only counted because run() merges streams at c2-counter.py:49, quote: `return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")`. If a future gate moved LG-DANGLING-PTR lines to stderr, a stdout-only counter would silently report dangling=0; the frozen counter is safe today, the merge is what makes it safe.
5. **m8 killed by the junk state; hazard demonstrated.** Counter location: census/round-30/c2-counter.py:84, quote: `rc, out = run([sys.executable, "-B", os.path.join(tr, "tools/souji-landing-gate.py")` (GATE leg executes tool@REV from the rev export). Mutated to execute the worktree tool at `--root`, the GATE leg measured non-REV bytes: on the junk state (root = clone holding junk rev, worktree at BASE) it printed `GATE ... reports=0 cne=1 dangling=3` (the base gate's numbers) instead of the stub's `86/0/0` → receipt mismatch. The do-nothing row does not kill it only because the lane worktree happens to equal base bytes right now (gate unchanged base→HEAD; `git status --porcelain tools/` empty) — i.e. the mutant's receipts are non-reproducible whenever the worktree drifts, violating the counter's own committed-bytes contract. Rig note: the first m8/junk cell (p2 receipt) was a rig artifact — with `--root` = the scratch clone the mutant path resolved to that clone's stub worktree and matched the junk receipt; superseded by the p3 redo with a worktree-at-BASE clone.
6. **m1 and m6 are killed by the do-nothing receipt alone** — the do-nothing control's `fixture=fail redarm=fail` and `cne=1` fields are each load-bearing for the fixture-absent and stderr-cne cases (m1: `fixture=ok redarm=ok` at base; m6: `cne=0` at base, both receipt mismatches). No constructed state needed.

## Attack log
Verdict rule: killed = on some state the mutated counter no longer reproduces the frozen control receipt for that state, or exits 0 (target-shaped) on a state that must fail; survivor = no available or constructible state distinguishes it. States: do-nothing = lane base rev as `--rev`; junk = reconstructed stub state db156ef (committed control rev absent, see Finding 1); junk2/k5b/k2/k3 = constructed states above.

| # | mutant (patch site) | do-nothing row | C2-junk row | constructed state | verdict |
|---|---|---|---|---|---|
| m1 | fixture absent → `fok = rok = True` (:106) | KILLED (`fixture=ok redarm=ok` ≠ receipt `fail fail`) | n/a (fixture present) | — | killed |
| m2 | drop `and cases_ok` from fixture predicate (:98) | no (receipt match) | no (junk-v1 identical) | k2-nocase: `fixture=fail` → `fixture=ok` | killed (constructed) |
| m3 | accept `FALSE-GREEN-ACCEPTED` (:98) | no | no | k3-accepted: `fixture=fail` → `fixture=ok` | killed (constructed) |
| m4 | `rok = True` (:102) | no | field flip (`redarm=ok` ≠ recorded `fail`) | junk2: **full PASS rc=0** | killed (constructed) |
| m5 | `same = same and s1[0] == s2[0]` (:115) | no | no (junk-v1 identical) | k5b: **full PASS rc=0** | killed (constructed) |
| m6 | cne counted on stdout only (:88) | KILLED (`cne=0` ≠ receipt `cne=1`) | — | — | killed |
| m7 | dangling counted on stdout only (:89) | no (receipt match) | no (junk, junk2 identical) | none possible — gate emits LG-DANGLING-PTR on stdout only (gate:1151) | **SURVIVOR** (equivalent mutant) |
| m8 | GATE tool path `tr` → `root` (:84) | no (worktree gate == base bytes at probe time) | KILLED (root=D: `reports=0 cne=1 dangling=3` ≠ `86/0/0`) | — | killed (junk state) |

Survivors: m7 only. It is an equivalent mutant for this gate's emission streams — a coverage observation (Finding 4), not a counter defect; no contract change proposed.

## Deliveries
- Report: .ufo/waves/round-30/w1/SwarmMutationTester29.md (this file)
- Receipts (42 files): .ufo/waves/round-30/w1/SwarmMutationTester29-receipts/ — every matrix cell's full counter output (`<phase>-<mutant>__<state>.txt`), plus the three rig drivers (`driver.py`, `driver2.py`, `driver3.py`) containing the exact mutant patches and state builders.
- Tooling record: no tools installed or upgraded (pacman guard respected; nothing needed beyond python3/git already present).
- Scratch: `/fast/scratch/hyaku/souji-r30/MutateC2Counter/` removed after receipt copy; lane repo bytes and index untouched throughout (read-only git against the lane only).
- Point-in-time note (post-run): `git status --porcelain census/round-30/c2-counter.py tools/` now shows ` M tools/souji-capability-agreement.py` — an in-flight edit by another seat/the L1, not made by this seat; this seat's files (`census/round-30/c2-counter.py` sha256 `6cd15db9ce0f55552c5cde4e1aa93c48105a4836c3eb1b87ab72b81614d88b41`, `tools/souji-landing-gate.py`) remain clean.
