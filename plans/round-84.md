# Round 84 — amendments to the frozen claims (pre-file falsification)

Written before the round report was filed. The frozen wording lives in `census/round-84/preregistration.txt`
(commit `35d87842efd966bfc326eff92fb534ab3e56b79e`, F) and is not edited here: each amendment records what the
round's own artifacts falsified in that wording, and the narrower sentence the round now puts its name to. Numbers
are re-derived on committed bytes by non-author seats and by the L1; records under `census/round-84/records/` and the
wave's reports under `.ufo/waves/round-84/w1/`.

Wave evidence root: `.ufo/waves/round-84/w1/`.

## A0 — instrument corrections, before any claim score (not amendments to a claim)

- **A0.1 — the `latefork` stub deferred its own trap.** The first stub ran `while :; do sleep 1; done`; a foreground
  child defers bash's trap until that child returns, so the tool's 0.1 s KILL sweep killed the CLI before the trap
  ran and the row measured the stub, not the tool (`census/round-84/controls/c2-before-r83-tool.txt` first run read
  `survivors=0` on both late rows for the r83 tool, a false green). Correction: the stub busy-loops on the `:`
  builtin, so the trap runs the moment the signal lands; the control then read `mismatches=2 orphans=2` with one
  survivor per late row, which is the frozen before. No candidate had been scored when the stub changed.
- **A0.2 — the first repair idea (a second TERM pass) is not deterministic.** The reference implementation at
  `.ufo/waves/round-84/w1/RefC2/souji-vault-verify.sh` was first built as "TERM pass, 0.1 s, second map, TERM the
  newcomers, KILL sweep". Measured: `l1` green but `l2-late-setsid-group` left 1 survivor
  (`census/round-84/records/c2-reference-prefreeze.txt`, first and second runs), because `setsid sleep 600 &` forks
  (setsid's own fork when its caller is a group leader) and the `sleep` is reparented before the second map is read —
  it is no longer a descendant. Diagnosis: one walk discovered only the CLI pid twice, never the child. Correction
  before any claim score: the repair is FREEZE-then-kill (SIGSTOP each discovered descendant before any trappable
  signal, second map pass for a child forked in the read->stop window, then SIGKILL), which removes the trap from
  the path instead of racing it. The prereg was amended to this wording before F. The reference run then read
  `rows=22 mismatches=0 errors=0 orphans=0`, late rows 0 survivors, deep rows 0.8-0.9 s.
  **Disclosure:** both pre-freeze reference runs are instrument validation, not the claim's after evidence; the after
  arm is re-run on the filed bytes after F and that receipt is the claim's.
- **A0.3 — m9 (the basename rule) as first written was already killed by the r83 population.** The first
  `m9-basename-only` edit was `return bool(m) and got[-1:] == want[-1:]` (no length constraint); the r83 population
  killed it (`mismatches=1`, `NF-J`), so it was not one of the unbound clauses. Correction before F: m9 is the r83
  critic's A2 rule, `len(got) == 2 and got[1] == want[-1]`, which the r83 population leaves green (measured
  `killed_r83=0` on the corrected set, `census/round-84/controls/c1-before-r83-population.txt`) and the r84 population
  kills on TF8 and NF-P.

## A1 — C2: the second map pass carries no row (the freeze and the KILL sweep do)

- **Artifact:** `census/round-84/records/c2-mutants-on-filed.txt` — M2 (`for pass in 1 1`) scores
  `rows=22 mismatches=0 errors=0 orphans=0`; S84Connector F-03 says the same from the other side.
- **Frozen wording falsified:** "a second map pass catches a child forked in the read->stop window, and the frozen
  set is then SIGKILLed" presents the second pass as the mechanism the population certifies. It does not: the CLI is
  SIGSTOPped in pass 1 and never runs its trap, so nothing is forked in that window on any frozen row.
- **Amended sentence:** *the repair FREEZES before it signals — every descendant discovered by a fork-free /proc pass
  is SIGSTOPped before any trappable signal reaches it, and the frozen set is SIGKILLed. Replacing SIGSTOP with TERM
  (the r83 order) leaves both late rows red and dropping the KILL sweep leaves two red, so those two clauses are the
  measured ones; the second map pass is a belt for the read->stop window and no frozen row exercises it (a single-pass
  mutant scores 22/22 green).*

## A2 — C2: the whole-file re-check (the r83 D5 fix) carries no row

- **Artifact:** M4 (`{ read -r now < ... }` in the STOP re-check) scores `rows=22 mismatches=0 ...`; no frozen row
  carries a comm with a newline, so the re-check's whole-file read is unexercised.
- **Amended sentence:** *every stat read in `cli_kill_tree` — the map pass and both re-checks — is whole-file with
  the last `)` strip, which closes the r83 spot-check's D5 hazard on the re-check path; the frozen population has no
  comm-with-newline row, so the re-check's read shape is a stated repair with a routed row, not a measured clause.*

## A3 — C2: the `latefork` stub forks once, and a daemonizing CLI is not a row

- **Artifact:** `S84ExecEvade.md` shapes (a2) and (b): a CLI that forks on every signal, and a CLI that double-forks a
  daemon and exits before the caller's signal.
- **Amended sentence:** *the late-fork rows cover a CLI that traps the caller's signal and forks one child from it;
  a CLI that forks on every signal, and a CLI that daemonizes and exits before any signal arrives (the tool then
  returns a verdict with no SIG line, which is correct) are stated limits, not rows.*

## A4 — C1: m9's kill set is four rows, three of them true-row refusals

- **Artifact:** `census/round-84/records/c1-m9-rows.txt` — m9 (the r83 critic's A2 basename rule) refuses TF8, TF9 and
  TF10 (`refused_true=3`) and accepts NF-P (`accepted=1`); `SUMMARY rows=44 mismatches=4`.
- **Amended sentence:** *m9 is killed by three true rows it refuses (the deep token and the two shape true rows) and
  one false row it accepts (the flattened copy); the kill is therefore a suffix-depth proof, not only a shape proof.*
  (The preregistration says "the rows that would exercise it"; this is the exact set.)

## A5 — Substrate: two seats scored a reference copy the L1 was still rewriting

- **Artifact:** `S84ExecEvade.md` §"Bytes under test" (`a810acaf…`), `S84MutTool.md` §"Candidate provenance",
  `S84Reviewer.md` F1/F4, `plans/round-84.md` A0.2.
- **What happened:** the reference implementation at `.ufo/waves/round-84/w1/RefC2/` was rewritten twice while the
  wave was running; both seats copied `a810acaf…`, which carries the M2 `|| continue` defect, so their survivor
  tables describe bytes that were never filed.
- **Disposition:** the filed tool is `030fa10d…` (S84ExecC2's `a33038e9…` plus the whole-file re-checks). The L1
  re-scored the filed bytes (`census/round-84/records/c2-after.txt`, 22/0/0/0) and re-mutated them
  (`census/round-84/records/c2-mutants-on-filed.txt`). The seats' findings stand as findings about `a810acaf…` and
  are recorded as such; M5 in the lesson routes the practice (a reference belongs in a seat-owned path with a frozen
  hash).

## A6 — C1: the counter is unchanged, so the claim is about the instrument

- **Artifact:** `census/round-84/c1-pointer-counter.py` sha256 `052c4f3f…` = `census/round-83/c1-pointer-counter.py`.
- **Amended sentence:** *no counter byte changed this round; the population changed. The claim is that the lane's
  self-assessment instrument now discriminates five clauses it previously certified blind, measured as a kill rate
  over two pinned populations (0/5 -> 5/5) with both pristine arms green.*
