# souji-shokunin — SCORECARD

Axes (fleet `AXES.md`): the lane owns **calibration, operability,
coverage**. Following the kotodama precedent, rows carry per-axis verdicts
and checkable observations plus a 0–10 score only where a reproducible
mapping from evidence to number exists. Every observation carries its
counting command and the commit it was measured against.

## Axes

| axis | score | verdict / observation | counting command | measured commit | last change |
|---|---|---|---|---|---|
| coverage | 8 | improved (r12 C2, self-verdict pending non-author; score delta 0 — legacy-unmapped since r9): knowledge entries with source/verified-at/recheck headers 0→5 on frontier rows F1, F3, F4 (0→3 rows holding an entry); SOURCES registry 0→33 rows, contract census clean. Prior: r3 C1, 21/21 metadata prunes with receipts | `bash -c 'for f in corpus/knowledge/*.md; do head -3 "$f" \| grep -cE "^(source\|verified-at\|recheck):"; done' \| grep -c '^3$'` → 5; `grep -cE '^\| F[0-9] .*\| frontier, entr' corpus/README.md` → 3; `bash census/round-12/sources-census.sh` | d7266c5 (`census/round-12/after.txt`) | r12 |
| calibration | 7 | improved (r12 C1, self-verdict pending non-author; score delta 0): own-mistake classes with a mapped captured-by rule 28/52 → 51/53 (mapped criteria, not demonstrated catches; M27/M39 external). Prior: r5 V1, 3 material defects corrected in-round | `sed 's/\\|/%7C/g' <file> \| awk -F'\|' '/^\| M[0-9]+ \| (defect\|process\|honest-stop\|caught) \|/{n++; if ($6 !~ /^[[:space:]]*none/) c++} END{print c"/"n}'` on `census/round-12/mistakes.md` (before) and `corpus/lessons/round-12.md` (after) | d7266c5 (`census/round-12/after.txt`) | r12 |
| operability | 8 | improved (r12 C3, self-verdict pending non-author; score delta 0): registered gates 0→1 (`r12-maintenance-guard`, exit 0/1/2, `--selftest` asserts pinned ids); executable Pre-quarantine guard rows 0→3. Prior: r4 O1', souji-vault-verify live | `bash tests/fixtures/r12-maintenance-guard.sh --selftest; echo $?` → 0; `grep -cE 'maintenance\.auto=false\|rev-parse --show-toplevel\|worktree lock --reason' SKILL.md` → 3 (0 at dcc8b9e) | d7266c5 (`census/round-12/after.txt`) | r12 |

Correction (r12 post-review, 2026-10-19): coverage C2 reads 0→4 admitted entries (+1 held,
K5) on F1/F3/F4, SOURCES census mined=16 queued=15; calibration C1's 28/52 → 51/53 is a
rule-coverage count, not calibration proof. Details: `corpus/lessons/round-12.md`
`## Post-review fixes`.

## Capabilities

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| fleet census (receipt taxonomy) | classify every fleet artifact into pushed / moved-to-obsidian / stale / none with per-row command evidence, at 64-seat parallelism, dry-run | `census/round-1/census-summary.json`, `census/round-1/census.tsv` (246 rows) | r1 |
| souji-verify | per-artifact SAFE/NOT-SAFE verdict from receipts, read-only, secrets-refusal; advisory while certification is OFF | `tools/souji-verify.sh`, current installed digest in `census/round-13/verification.json`; historical evidence `tests/results/INSTALL.json`, `tests/results/parent-harness-live.json` | r2 |
| worktree metadata prune | selective prune with lock-preserve of pinned registrations; receipts re-verified at act time | `census/round-3/seat-61.json` (plan), `census/round-3/seat-62.json` (lore assertions), LOG r3 | r3 |
| ledger-verify (moved-to-obsidian receipt) | verify a ledger row's source + vault sha256 pairs read-only; refuses self-referential rows; --ledger override; Obsidian integration remains operator-waived | `tools/souji-vault-verify.sh`, current installed digest in `census/round-13/verification.json`; historical evidence `tests/results/parent-vault-battery.json`, LOG r4 | r4 |
| sources registry | curate opened, scoped sources and retained rejections; counts re-derived at r13, not copied from stale r12 output | `corpus/SOURCES.md`; `census/round-13/verification.json` source census and histograms; baseline 33 rows, mined=16 queued=15 rejected=2 at 31984f4 | r12 |
| maintenance-guard gate | prove on the host git that a plain commit can prune expired unlocked worktree metadata and that `-c maintenance.auto=false`, `worktree lock` and a fresh index prevent it | `bash tests/fixtures/r12-maintenance-guard.sh --selftest` → 6/6 PASS, exit 0; `tests/results/r12-maintenance-guard.txt` | r12 |

## Planned

- **r4 — AMENDED by operator mid-round:** the Obsidian-CLI integration
  claim was withdrawn ("forget the obsidian integration for now"); closed
  instead on the standalone ledger-verify capability
  (`tools/souji-vault-verify.sh`, installed r4). Finding: no usable CLI
  entry point on this host — banked in
  `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` for the operator.
  Completion-criterion obsidian-row requirement waived by the operator.
- **r5 (verification round, all axes):** audit rounds 1–4 verdicts and
  outputs for correctness and missed items, folded into the round's own
  claims (scheduled model: gpt-6-luna-max). Carry-overs: the 96-row
  approval list awaits operator sign-off; the 3 pinned gd2d registrations
  await that lane's push; `/tmp` fixture residue routed to
  tsukuroi/operator.
- **r6–r11 (appended r12):** this section was not updated for rounds 6–11
  (STATE dossier §5.4; lesson row M52). Their claims and verdicts are in
  LOG.md and `corpus/lessons/round-{6..11}.md`.
- **r14 (planned r13):** comprehensive class-suite re-certification under
  Q6/Q18 remains separate from declared-fragment integrity and from the
  built-in smoke suites; certification stays OFF. Revisit the kotodama
  `.scratch` age/receipt census only as a read-only, metadata-bounded sweep
  with no content inspection or automatic removal. F2 wider size attribution,
  unreachable-object accounting and linked common-store aggregation remain
  frontier. Cross-device quarantine/K5 remains HELD under Q4/Q16.

## Saturation / stagnation

Saturation line: 8 per axis; stagnation window 3 rounds. Scores per the
rows above: coverage 8, operability 8, calibration 7 (this prose formerly
said 6/7 — corrected r9 after the judges caught the drift).

## Tool certification (r9)

The verdict tools are PATCHED (r9 S17: 40/51/91 selftest checks) but NOT
certified for deletion authorization: r9 red-team replays still reproduce
unsafe deletions (>=16 open defect classes; see corpus/lessons/round-9.md).
Receipts are advisory until the r10 hardening closes the classes.

Correction (r13): r10 and r11 ran; r11's certification evidence was
compromised (shared relay, verdicts on non-installed bytes). The historical
`census/round-10/cert-16.json` still carries a candidate CERTIFIED claim;
the appended r13 lesson and LOG explicitly supersede its authority for
installed tools without rewriting those bytes. The r13 integrity gate
checks declared evidence only. It cannot prove author identity, command
execution, or full defect-class coverage. Deletion authorization stays OFF.

## Retired

None.
