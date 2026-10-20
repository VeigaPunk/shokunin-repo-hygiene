# LandingGate — round 16 w1 (executor, leaf)

Claim covered: **C2 calibration**. Honest name for what this gate detects:
**landing-claim consistency + failure-channel carry** — it mechanically
re-derives the three r15 landing defects the non-author closure found by hand
(a registry-cited script that does not parse; frozen pins matching no
committed bytes; seat-reported known failures not carried into the lesson).
Behavioral regressions of lane tools are a non-goal: the gate never executes
repository code (only `bash -n FILE` and Python `compile()`).

OWNED file: `tools/souji-landing-gate.py` (new, executable, python3 stdlib only).

## 1. Design (final, after both L1 steers)

Byte provenance: `git -C LANE ls-tree -r -z --full-tree REV` +
`git cat-file blob <oid>` (no `git archive` — export-ignore/export-subst can
alter bytes). Only files needing a real path (`bash -n` targets) are written
under `tempfile.mkdtemp(dir='/var/tmp')`, removed in `finally`.

Checks (pinned ids):
- **LG-PARSE-REG** — every `tools|tests/fixtures|census/round-\d+/NAME.(sh|py)`
  path cited in SKILL.md at REV: `.sh` → `bash -n` (rc!=0 **or any stderr** is
  a finding), `.py` → `compile(src, path, 'exec')`.
- **LG-MISSING-REG** — a cited path absent at REV.
- **LG-PARSE-CHANGED** — `.sh`/`.py` added/modified in BASE..REV (with `--base`).
- **LG-FROZEN-PIN** — every `tests/fixtures/*-frozen/expected.json`: each
  `files` key resolves at snapshot root iff it starts with `tools/`, `tests/`,
  `census/` or `corpus/`, else inside the frozen dir (no fallback); the file
  must exist and match its sha256; `record_sha256` (if present) must match the
  `record` file resolved by the same rule.
- **LG-FROZEN-MEASURED** — if the record carries a resolvable `measured_commit`,
  each pinned digest must equal `git cat-file blob <measured_commit>:<path>`
  digest. A non-hex or unresolvable `measured_commit` contributes no checks.
- **LG-SEAT-UNCARRIED** — every `.md` under `.ufo/waves/round-N/` at REV:
  failure channel = lines starting `STATUS:`/`**STATUS:**`/`## STATUS:`
  (also `STATUS —`) whose first word (after stripping `*`/`:`/`—`) is not in
  {ok, none, complete, completed, pass, passed, clean, done, draft}, plus the
  pinned phrase markers (do not ship / does|doesn't parse / fails to parse /
  parse error / syntax error / SyntaxError / IndentationError /
  snapshot_tampered / currently fails?) — phrase markers ignored inside
  ``` fenced blocks and table rows. Each failure line must appear (NFC,
  `*`/backticks dropped, whitespace collapsed) inside the lesson's
  `## Seat-reported failures` section on a line containing `open` or
  `resolved@<7+ hex>`; HTML comments stripped first. Missing lesson → every
  marker uncarried. Missing `.ufo/waves/round-N/` → exit 2.
- **LG-OPEN-ADMITTED** — a failure carried with `open` while the lesson
  declares `admitted: true`.

CLI: `--root LANE --rev REV --round N [--base REV] [--json OUT]`, `--selftest`.
TSV findings sorted + `SUMMARY findings/reg/pins/markers/reports`. Exit
0/1/2. `--json` refuses overwrite.

## 2. Measured runs (advisory; L1 reruns)

- `python3 tools/souji-landing-gate.py --selftest` →
  `SELFTEST pass=18 fail=0`, RC=0. Cases: clean-pass, nonparsing-cited-sh,
  nonparsing-cited-py, missing-cited-path, changed-nonparsing-with-base,
  uncited-nonparsing-not-flagged, pin-mismatch, pin-missing-file,
  record-sha256-mismatch, frozen-measured, uncarried-marker, carried-open,
  carried-resolved, open-admitted, no-wave-dir-exit2,
  fenced-and-table-ignored, bad-rev-exit2, no-skill-exit2.
- `--rev b410186 --round 15` → **RC=1**, `findings=34 checked_reg=18
  checked_pins=16 checked_markers=30 checked_reports=64`. All three r15
  defects detected: `LG-PARSE-REG tools/souji-census.sh bash -n rc=2 … line
  1368: syntax error near unexpected token '}'` (matches spotcheck `:49`);
  `LG-FROZEN-PIN files[tools/souji-census.sh] pinned b51873514d1f6d34 but …
  hashes dab4122c997db9b9` plus `LG-FROZEN-MEASURED` rows showing the pin
  matches neither the measured commit `fc3a8d49` (`fcff8b05…`) nor HEAD;
  `LG-SEAT-UNCARRIED` including `ConfigRepair.md:7` (`## STATUS: INCOMPLETE —
  file has an unresolved syntax error`), `:11` (does NOT parse / do not ship),
  `:9`, `:124` (currently FAILS) and `AdmissionChecker.md:74`
  (snapshot_tampered exit-2 prediction).
- `--rev cbf688ab…423 --round 15` → **RC=1**, `findings=34`. PARSE-REG clean
  (census parses again), but the two `LG-FROZEN-PIN` rows now measure the
  pinned-vs-committed drift ConnScorecard reported (`6314d45d…` vs
  `9151cde8…`, `b5187351…` vs `fed43c71…`) and all 30 r15 marker lines remain
  uncarried — the lesson still lacks `## Seat-reported failures`.
- `--rev cbf688ab…423 --round 16` → **RC=2** (`no .md reports under
  .ufo/waves/round-16/` at that revision — the wave dir is worktree-only).
  Non-vacuous: it cannot pass green while the round is uncommitted.
- `--rev cc21683 --round 14` → RC=1, `findings=10`, all LG-SEAT-UNCARRIED —
  r14 seat prose (`snapshot_tampered`, `syntax error`, `Status: design-only`)
  never carried into `corpus/lessons/round-14.md`. See risks.
- `--rev b410186 --round 15 --base fc3a8d4` → `findings=35` (one
  LG-PARSE-CHANGED for the landing commit's new census bytes); `--json`
  writes the payload and a second invocation over the same path exits 2
  (overwrite refusal verified).

## 3. Risks / blockers

1. **Channel over-inclusiveness is spec-pinned, not a bug to fix here.** The
   benign allowlist does not contain `design-only`, `advisory`,
   `no known failure`, or `Status:` spelled with a lowercase `s` first word —
   so legitimate status lines (e.g. `Status: design-only`, `STATUS: no known
   failure`) are failures by the pinned rule and must be carried or the
   lesson goes red. This is the enforcement pressure the spec intends
   (CriticDisclosureR3 V1: "over-inclusive on purpose"), but L1 should know
   r14 also fails its own lesson. Seats should adopt a benign first word.
2. Carry requires the full normalized line verbatim on one lesson line —
   paraphrase is red (pinned). Lesson authors should quote the line.
3. `checked_reg` counts each parse check individually (cited ∪ changed);
   `checked_pins` counts pin comparisons (files entries + record_sha256 +
   measured comparisons).
4. No known failure in this seat's own deliverable beyond the above; the
   tool itself passes `py_compile` and selftest 18/18.

## Commands

1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 | head -200`
2. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:SKILL.md | head -120`
3. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:SKILL.md | grep -nE '(tools|tests/fixtures|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.(sh|py)'`
4. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tests tools corpus | grep -vE 'corpus/knowledge|corpus/lessons' ; echo '---LESSONS---'; git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- corpus/lessons`
5. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-preservation-frozen/expected.json; …:r14-cache-frozen/expected.json; …:r13-cert-frozen/expected.json`
6. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:corpus/lessons/round-15-verifier-spotcheck.md`
7. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -nIE '\bSTATUS:\s*(INCOMPLETE|FAIL(ED)?|BLOCKED|BROKEN)\b|does NOT parse|\bsyntax error\b' b410186 -- '.ufo/waves/round-15/' | head -60`
8. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:corpus/lessons/round-15.md | grep -nIE 'STATUS:|does NOT parse|syntax error|ConfigRepair|parse' | head -40; git -C … show b410186:corpus/lessons/round-15-verifier-spotcheck.md` (rc 128 — file not at that rev)
9. `cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain | head -20 && git log --oneline -8`
10. `git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-preservation-frozen/record.json | head -40; git ls-tree --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 .ufo/waves/; git ls-tree --name-only cc21683 .ufo/waves/`
11. `python3 -m py_compile /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py` → PARSE-OK
12. `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --selftest` → `SELFTEST pass=18 fail=0`, RC=0
13. `python3 …/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev b410186 --round 15` → RC=1, `SUMMARY findings=34 checked_reg=18 checked_pins=16 checked_markers=30 checked_reports=64`
14. `python3 …/souji-landing-gate.py --root … --rev cbf688ab2ab28e38103e5a9417ca525b5f2ed423 --round 15` → RC=1, `findings=34`
15. `python3 …/souji-landing-gate.py --root … --rev cbf688ab2ab28e38103e5a9417ca525b5f2ed423 --round 16` → RC=2 (`no .md reports under .ufo/waves/round-16/`)
16. `python3 …/souji-landing-gate.py --root … --rev cc21683 --round 14` → RC=1, `findings=10 checked_reg=15 checked_pins=9 checked_markers=10 checked_reports=32`
17. `python3 …/souji-landing-gate.py --root … --rev b410186 --round 15 --base fc3a8d4 --json /var/tmp/lg-b410186.json` → findings=35; repeat `--json` → RC=2 (overwrite refused); `rm /var/tmp/lg-b410186.json`

Tool installs/updates: none. No `git archive`, no commits, no operator-sweep
or ~/.omp access. Selftest scratch under `/var/tmp/souji-landing-gate-*`
removed by the tool itself.
