# MutC1Count — mutation test of the C1 landing-gate counter invocation (round 27, attempt 2)

Seat: MutC1Count (mutation-tester, leaf — no subagents). Read-only seat honored: no lane bytes written, no git mutations, no signals. No tooling installed (operator 2026-10-19 authorization unused). Mutants are invocation mutations only; detector = the frozen counter itself.

## Status

STATUS: PASS — all four mutation arms plus baseline and repeat executed at pinned rev e78ac7c4837b81b634db4a927605a751a7f006ba (HEAD of lane at probe time); `SUMMARY findings=N` line byte-stable across repeats; JSON receipt `exit` equals shell rc in all 5 runs; two tasking expectations refuted and recorded as survived-mutant coverage findings F3/F4.

## Evidence

- Revision: lane HEAD = `e78ac7c4837b81b634db4a927605a751a7f006ba` (verified via `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` this run); probe pinned `--rev` to the full 40 hex except arm C.
- Detector (frozen, preregistration.txt C1): `python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40> --round 27 --fleet-root /home/vgpnk/Projects/shokunin` → `SUMMARY findings=N`; frozen before=2.
- Baseline B1 (full40, round 27, fleet-root) stdout:
  ```
  LG-DANGLING-PTR	corpus/knowledge/registry	corpus/QUALITY.md:143 cites path absent at e78ac7c4837b
  LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:141 cites path absent at e78ac7c4837b
  SUMMARY	findings=2	checked_reg=50	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
  ```
  rc=2, stderr: `COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-27/ at e78ac7c4837b81b634db4a927605a751a7f006ba`. Grounding: `git ls-tree e78ac7c…:.ufo/waves/round-27/` → `fatal: Not a valid object name` (round-27 dir is worktree-only at base).
- Repeat D: stdout byte-identical to B1 (compared as raw bytes: True). Short-rev C: stdout byte-identical to B1 (True).
- Receipt: every arm's JSON (`--json` under `/var/tmp/souji-r27-MutC1Count/`, since removed) carried `"exit"` equal to the observed shell rc in all 5 runs (5/5 True). Tool doc, tools/souji-landing-gate.py:32: "Exit: 0 no findings, 1 findings, 2 could-not-evaluate (usage, unknown rev,". Receipt writes are refusal-safe (tools/souji-landing-gate.py:1169-1171: "--json output %s exists; refusing to overwrite").
- Before/after hashes (tool blob and worktree identical; exemptions blob unchanged):
  - `tools/souji-landing-gate.py` blob@e78ac7c sha256 before = after = `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd`
  - `corpus/pointer-exemptions.tsv` blob@e78ac7c sha256 before = after = `9d6a0352186076e9a027facd581d869195b663e305fe92fddf224cb073bb68cf`
- Read-only safety of the detector: it reads committed bytes via git plumbing and stages `bash -n` snapshots under "private tempfile.mkdtemp(dir='/var/tmp') snapshot removed in `finally`" (tools/souji-landing-gate.py:24-25). No lane write path exists for these invocations.

## Findings

1. **F1 — counter value stable (baseline holds).** `findings=2` at e78ac7c with exactly the two frozen LG-DANGLING-PTR sites (`corpus/knowledge/registry`, `corpus/lessons/round-24.md:232:S118`); repeat run byte-identical. Location: B1/D SUMMARY lines; output contract tools/souji-landing-gate.py:36-37.
2. **F2 — at base the gate's rc is 2, not 1, despite findings=2.** Error precedence: `result["exit"] = 2 if result["error"] else (1 if findings else 0)` (tools/souji-landing-gate.py:1138); the error is the absent committed `.ufo/waves/round-27/` (worktree-only at base, ls-tree fatal). Consequence: the frozen counter is correctly defined on the `SUMMARY findings=N` line, not on rc; any receipt that records rc alone at base reads 2. The JSON receipt captures both (`exit`=2 and the findings list), so nothing is lost.
3. **F3 — SURVIVED mutant (coverage finding): short `--rev` is accepted, not refused.** `--rev e78ac7c` resolved to the full hash (JSON `resolved_rev: e78ac7c4837b81b634db4a927605a751a7f006ba`) and produced byte-identical output to baseline. Location: resolve_commit via `rev-parse --verify --quiet` (tools/souji-landing-gate.py:253-258); no full-40 length enforcement anywhere in main() (tools/souji-landing-gate.py:2278-2326). Unresolvable/ambiguous revs still land in exit-2 ("cannot resolve revision"), so the failure mode is safe; the receipt's `resolved_rev` keeps post-hoc full-hash binding. Recorded per role: coverage finding, not a contract-change proposal.
4. **F4 — SURVIVED mutant (coverage finding): `--round` is load-bearing.** `--round 26` at the same rev returns `findings=20` (the 2 LG-DANGLING-PTR plus 18 `LG-SEAT-UNCARRIED` from `.ufo/waves/round-26/w1/*.md`; checked_reports=84, checked_markers=18), rc=1. The counted population is round-scoped, so a receipt must pin the round it claims; the frozen counter pins `--round 27`. Tasking hedge "must NOT change findings count semantics?" is refuted by observation.
5. **F5 — KILLED mutant: omitting `--fleet-root` yields exactly 5 findings as tasked.** The 3 additional LG-DANGLING-PTR are fleet-only citation paths (`corpus/README.md:217` → `.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md`, `…JjTrialSouji.md`; `corpus/knowledge/jj-colocation-receipts.md:148` → the reports dir). With `--fleet-root` they are classified fleet-only and are not findings, matching the doc: "For round 18 and later, `--json` also carries a `fleet` list" (tools/souji-landing-gate.py:38-39).
6. **F6 — exemptions state at base consistent with before=2.** `corpus/pointer-exemptions.tsv` at e78ac7c has 4 rows (census/operator-sweep-20261019, two r17 quarantine/vault rows, r14 placeholder record); none covers the two dangling-pointer sites.

## Attack log

| # | Mutant (invocation at e78ac7c) | Expected (tasking) | Observed (rc / findings / excerpt) | Verdict |
|---|---|---|---|---|
| A0 | none — baseline full40, `--round 27`, `--fleet-root` | findings=2 (frozen before) | rc 2, findings=2, stderr "no .md reports under .ufo/waves/round-27/" | baseline confirmed (see F2 for rc) |
| A1 | `--round 26` | count semantics unchanged? record | rc 1, findings=20 (2 ptr + 18 LG-SEAT-UNCARRIED, checked_reports=84) | survived — round-scoped population (F4) |
| A2 | drop `--fleet-root` | must show 5 findings | rc 2, findings=5 (3 fleet-only citations become findings) | killed (F5) |
| A3 | `--rev e78ac7c` (short) | must refuse or fail | rc 2, findings=2, resolved_rev=full40, stdout byte-identical to A0 | survived — no full-40 enforcement (F3) |
| A4 | repeat A0 | two runs identical | stdout byte-identical (True); SUMMARY findings=2 both | reproducibility confirmed (F1) |
| R  | receipt format | captures rc | JSON `"exit"` == shell rc in 5/5 runs; refuses overwrite | confirmed |

Restoration evidence: no bytes were mutated anywhere (mutants were CLI-argument mutations); tool and exemptions sha256 identical before/after (values above); scratch `/var/tmp/souji-r27-MutC1Count/` (receipts only) deleted at close; lane untouched.
