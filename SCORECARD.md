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

## Capabilities

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| fleet census (receipt taxonomy) | classify every fleet artifact into pushed / moved-to-obsidian / stale / none with per-row command evidence, at 64-seat parallelism, dry-run | `census/round-1/census-summary.json`, `census/round-1/census.tsv` (246 rows) | r1 |
| souji-verify | per-artifact SAFE/NOT-SAFE verdict from receipts, D1–D3 fixed, --selftest over F1–F10 fixtures, read-only, secrets-refusal | `tools/souji-verify.sh` (sha256 7efda63bd760…), `tests/results/INSTALL.json`, `tests/results/parent-harness-live.json` | r2 |
| worktree metadata prune | selective prune with lock-preserve of pinned registrations; receipts re-verified at act time | `census/round-3/seat-61.json` (plan), `census/round-3/seat-62.json` (lore assertions), LOG r3 | r3 |
| ledger-verify (moved-to-obsidian receipt) | verify a ledger row's source + vault sha256 pairs read-only; refuses self-referential rows; --ledger override; obsidian-CLI probe path reserved (no usable CLI entry point on this host — banked for operator) | `tools/souji-vault-verify.sh` (sha256 d312263a…), `tests/results/parent-vault-battery.json`, LOG r4 | r4 |
| sources registry | curate where souji learns: 33 opened, tiered rows (2 rejected with flips), study paths, search log; contract v1 census runs clean | `corpus/SOURCES.md`, `bash census/round-12/sources-census.sh` → 33 / 0 / A=29 B=3 C=1 / mined=18 queued=13 rejected=2, last three checks silent | r12 |
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
- **r13 (planned r12):** (1) the r11 carry — re-run the certifier suites
  under a no-relay protocol (QUALITY Q6) before certification can flip;
  (2) operability: bounded per-target staging in
  `tools/souji-quarantine.sh` (QUALITY Q8, M43); (3) gate-registry rows in
  SKILL.md for the four installed tools; (4) F2 frontier: the /var/tmp
  write-safety fixture for `git repo structure`; (5) the kotodama
  `.scratch` re-sweep once the tree ages past 24 h (M47).

## Saturation / stagnation

Saturation line: 8 per axis; stagnation window 3 rounds. Scores per the
rows above: coverage 8, operability 8, calibration 7 (this prose formerly
said 6/7 — corrected r9 after the judges caught the drift).

## Tool certification (r9)

The verdict tools are PATCHED (r9 S17: 40/51/91 selftest checks) but NOT
certified for deletion authorization: r9 red-team replays still reproduce
unsafe deletions (>=16 open defect classes; see corpus/lessons/round-9.md).
Receipts are advisory until the r10 hardening closes the classes.

Correction (r12): the note above is stale. r10 and r11 ran; r11 closed the
last r9 class in the tools (census selftest 36/36) but certification was
NOT granted — the certifier evidence was compromised (shared relay,
verdicts on non-installed bytes; `corpus/lessons/round-11.md:13-17`).
Deletion authorization stays OFF; receipts stay advisory until a no-relay
re-certification passes (Planned r13).

## Retired

None.
