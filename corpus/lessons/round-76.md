# Round 76 — which file decides an ignore match (C1 operability), a kill tally that binds each receipt to its mutant (C2 calibration)

Attempt 1 (`SoujiR76`). Lane base `ee59aa4da358d38850ccace194f7cd558ee45ce9` (r75 admitted, spot-check committed).
Staged commits in the order the preregistration binds: P `6c9c2a8eaad2ee570e4f43517d1f437567bb9873` (counters,
populations, forged C2 cases, every control receipt, S320 capture, census-before); F
`2ed6b179ef4aeb106488806b9f3dcacca29e2e60` (preregistration, Q99 grammar; freeze-check `--substance --chronology`
`SUMMARY claims=2 findings=0`); I `2c7c1ce6f91062f497ffbbc7fcc9e9c19e2511ce` (C2 candidate tally); W
`e827d2bf53f71470bfc1fce6aa4633549b018270` (C1 candidate gate and `.gitignore`); A
`113b007202d79275ca2debaaaa719551eaa35198` (after-arms); lesson fixes `eef6f30c7be607d7590898da53496408f5fa9545`; wave
repair R `9cbfd29630f04799cb72b17a53df860c1f503275` and its receipts `1a6eaea8acc14c23e13269429ab2699dde8e112f`. Frozen
claims, counters and predicates are in `census/round-76/preregistration.txt` and are not restated here.

## Inherited

The r75 spot-check routed five defects (`corpus/lessons/round-75-verifier-spotcheck.md`, Routed defects):

- 1 (a probe that cannot fail) → `census/round-76/probes/repro-coreworktree.sh` computes `VERDICT=FORGERY` (exit 1) or
  `REFUSED` (exit 0): `records/probe-coreworktree-at-r75W.txt` FORGERY EXIT=1 on the r75 W gate (blob `620ed97e…`),
  `-at-r76W.txt` REFUSED EXIT=0; blob digests in `records/probe-coreworktree-gates.sha256` (S76CriticDiscern F4).
- 2 (core.excludesFile arm undiscriminated) → open; no r76 row separates the writer's pinned status from the gate's
  own rule (S76CriticDiscern, S76MutGate LOW-4). Routed r77.
- 3 (domain-trial revision) → the prereg binds the C1 candidate's gate blob and requires an amendment line for a later
  blob; the trial receipt names both (`records/c1-domain-trial.txt`).
- 4 (routed (a)-(d)) → (b) taken as C2 (binding and committed UNREAD receipts `c2-cases/exit2-fail1-X09.txt`,
  `fail0-exit1-X15.txt`); (c) the r27/r36 regressions are a frozen conjunct of C1 (21/21, 4/4 at W and at R); the
  ls-files failure branch and refusal class stay unmeasured; (a) Y4/Y5 and (d) stay routed.
- 5 (stated limit: self-ignoring untracked `.gitignore`) → C1; QUALITY Q137 supersedes Q136's limit clause. A broad
  committed rule still hides content (declared policy).

No inherited lane leftovers (`jj-lane.sh state` at start: `local=remote=ee59aa4d… ahead=0 tracked=0 untracked=0`;
`.ufo/watchdog.log` has no `lane-dead-no-report souji round=76`). No `considerthese/` directory exists in this lane; no
shokuknow theme taken (Assimilation: none).

## Measured

- C1: `controls/c1-K-a-do-nothing.txt` mismatches=4 [f7 f9 f10 f14] EXIT=1 → `records/c1-after.txt` mismatches=0
  EXIT=0; K-b 4 and K-c 1 stay red; `records/c1-regress-r36.txt` 21/21, `c1-regress-r27.txt` 4/4; at the repair
  `records/wave-repair/c1-at-repair.txt` 0, r36 21/21, r27 4/4.
- C2: `controls/c2-K-do-nothing-r75.txt` mismatches=5 EXIT=1 → `records/c2-after.txt` mismatches=0 EXIT=0, h-honest
  `killed=6`; blanket 2 stays red; at the repair `records/wave-repair/c2-at-repair.txt` 0.
- Wave-repair probes (computed verdicts, exit 1 on any unexpected arm): `records/wave-repair/repair-probes.txt`
  `SUMMARY arms=8 as_expected=8`; `records/wave-repair/tally-probes.txt` `SUMMARY arms=8 as_expected=8`.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | a receipt helper that writes a header for a bind path that does not exist (this round): the first census-before receipt bound `scripts-none` and printed an empty `instrument_sha256=` with rc 0 | L1 session ~22:20 -03, census-before re-recorded without rec.sh before P | none: `census/round-75/rec.sh` swallowed the `sha256sum` error | `census/round-76/rec.sh` refuses a missing or non-file BIND before writing; shown able to fail in `census/round-76/records/rec-missing-bind-control.txt` (old helper `old-rc=0` with `instrument_sha256=` empty, new helper `new-rc=2`, no output file) |
| M2 | a frozen population whose forging rows all share one count (this round): f7 f9 f10 f14 each carry exactly two undeclared paths, so a gate that refuses only above one passes the frozen counter, r27 and r36 | `.ufo/waves/round-76/w1/S76MutGate.md` M09; mirrored in `census/round-76/records/wave-w1/seats/` | Q132 (a row is evidence for a shape only if it refutes a mutant that depends on it) — not applied to the count dimension at freeze | one-path arm in `census/round-76/records/wave-repair/probes/repair-probes.sh`: M09 mutant `got=PASS`, repaired gate `got=FAIL` (`repair-probes.txt`, arm single); a frozen successor row is routed r77 |
| M3 | the L1 took a seat's description of a forgery without reading its bytes (this round): the first tally-probe draft expected the repaired tally to refuse S76ExecC2's F3 receipt, but that receipt still carries a whole `--selftest` token (moved after the `--work` path); the draft read `SUMMARY arms=6 as_expected=5`, exit 1 | L1 session; `census/round-76/records/wave-repair/cases/reX09-selftest-in-path.txt` command= line | the probe's own computed verdict (exit 1) — the r75 routed-defect-1 rule working | arm renamed `selftest-moved` (both tallies accept: rec.sh's command= line loses quoting, a stated limit) and a distinguishing arm `selftest-off` added (I accepts, R refuses); final `tally-probes.txt` 8/8 |
| M4 | a new git call added without the pins its sibling calls carry (this round): the W block's `ls-files --cached` lacked `-c core.fsmonitor=false`; a repository fsmonitor hook ran after the byte-truth check, appended a rule to the tracked `.gitignore`, and the gate passed | `.ufo/waves/round-76/w1/S76Sentinel.md` HIGH-1 | none in the frozen 30 rows (r74 `d-fsmonitor-empty` fires before the truth check) | tracked set read from HEAD's tree (`git ls-tree -r -z --name-only --full-tree HEAD`, no hook, no staged-only file); `repair-probes.txt` arm fsmonitor: W `got=PASS`, R `got=FAIL` |

## Gate

- **S320 admit (A, mined)** — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-check-ignore.adoc,
  sha256 `940177c7385eb3cf0ffb1f22ffba35661d16800f8ce787ac676e9a8c89d68208`, 4159 bytes, HTTP 200, accessed 2026-11-06 by
  the L1 (capture `census/round-76/srcs/git-check-ignore.adoc`), re-fetched by S76Scribe (HTTP 200, 4159 bytes, `cmp`
  identical). Offset 2355 of the whitespace-normalized capture (raw lines 81-82): "<source> is the pattern's source
  file, and <linenum> is the line number of the pattern within that source." (18 words). Cited by
  `corpus/knowledge/filter-filemode-witness.md` r76; grounds the sourced claim C1 (the gate reads the source field to
  decide declared versus undeclared). S76CriticClaims: the code parses the four NUL fields exactly as the OUTPUT
  section states (`-z` form, raw line 92) — used, not only cited.
- **Rejected anchor (L1, over the bar)** — "If `-n` or `--non-matching` are specified, non-matching pathnames will also be
  output, in which case all fields in each output record except for <pathname> will be empty." (27 words, normalized
  offset 3013). The gate relies on it (a path only `core.excludesFile` hides reads unmatched under `/dev/null`), so it
  is paraphrased in the knowledge entry, not quoted.
- **Rejected anchor (L1, over the bar)** — "<source> will be an absolute path when referring to the file configured by
  `core.excludesFile`, or relative to the repository root when referring to `.git/info/exclude` or a per-directory
  exclude file." (30 words); paraphrased only.
- No existing row's status, recheck or used-by cell changed. `grep -n 'check-ignore' corpus/SOURCES.md` before the
  append: no row (S320 is not a within-scope duplicate).

## Wave

One v1 wave, 12 seats (connector 1, scout 1, executor 3, mutation-tester 2, reviewer 1, critic 2, sentinel 1, scribe 1;
attack seats 5 of 12). Seat reports are mirrored byte-exact under `census/round-76/records/wave-w1/seats/`.

- Reproduced from committed bytes: every frozen number (S76ExecC1, S76ExecC2, S76Reviewer, S76Connector,
  S76CriticClaims, S76CriticDiscern, S76Scribe). Causal separation SEPARABLE (S76Connector strace: no cross reads).
- Repaired after measurement (`9cbfd296`, receipts `1a6eaea8`): S76Sentinel HIGH-1 (fsmonitor, M4), MEDIUM-1 (caller
  `GIT_EXEC_PATH` ran a planted remote helper through `ls-remote`), LOW-1 (index membership admitted a staged
  `.gitignore`); S76CriticClaims MEDIUM (unanchored `.jj/` declared any nested `sub/.jj/`); S76Reviewer LOW (substring
  `--selftest`).
- Recorded, not repaired (kill power of frozen instruments; predicates unchanged): S76MutGate M09 (M2) and LOW
  survivors M02-M08, M11, M13, M15 (equivalent or unreachable on constructible inputs, per the seat); S76MutTally K03/K04
  HIGH (the binding counter compares exit codes only; a counter accepting every rejection reads the r75 control as 0)
  and T02/T04/T10 survivors with killing cases; S76CriticClaims MEDIUM (a tally matching six file names scores 0 on the
  frozen C2 population; the real tally binds bytes, `tally-probes.txt` arm by-name).
- Disagreed: S76ExecEvade b-neg "FORGERY HIGH" (tracked root rule `hidden/`, untracked `hidden/.gitignore` with
  `!payload`, gate PASS). The deciding pattern is the tracked root rule naming the directory — the f11 shape and the
  stated broad-committed-rule limit; the untracked negation never applies because git does not descend into an excluded
  directory. Not a forgery of the r76 rule; the limit stays stated in Q137.
- Open, pre-existing: S76Sentinel MEDIUM-2 (no timeout; a FIFO `.gitignore` or `core.excludesFile` hangs the gate; the
  lane-base gate hangs too).
- Sibling note (report only): every sibling lane S76Sentinel sampled carries an untracked `.jj/.gitignore`; the r76 gate
  would refuse them until they declare `/.jj/` (S76Sentinel LOW-2). Sibling gates and tallies listed by S76Connector,
  not edited.

## Routed to round 77

- (a) gate: timeout and non-regular exclude sources (S76Sentinel MEDIUM-2); a frozen successor population with
  one-path forgery rows (M2) and the refusal class per row; the core.excludesFile arm (r75 routed defect 2).
- (b) binding counter: compare SUMMARY counts and rows executed, not exit codes only (S76MutTally K03/K04); add
  name-swapped cases (S76CriticClaims) and the T02/T04/T10 killing cases.
- (c) carried: new-slot post-only and aliased witnesses (S75ExecC2 Y4/Y5); witness set from the builders (r74 M3);
  status-trusting lane tools `tools/souji-verify.sh:550,594`, `souji-census.sh` (S76Connector); writer survivor M03;
  caller `PATH`/`BASH_ENV` trust.
