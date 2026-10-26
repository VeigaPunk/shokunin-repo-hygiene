# deliver-sibling-overlap — Souji r33 w1 sibling-overlap scan (seat SwarmConnector43)

Scan of sibling lane repos for overlap with this round's two surfaces:
- **C1-CURRENCY**: SCORECARD.md capability rows re-run against their stated outputs (capability-table currency).
- **C2-SCRATCH**: scratch-root discipline (TMPDIR honouring, trailing-slash TMPDIR, bwrap read-only /tmp).

Scope read (read-only, this run): every `*-shokunin/` repo except `souji-shokunin/`, files
`PROVINCE.md`, `SKILL.md`, `SCORECARD.md`, `corpus/QUALITY.md`, `corpus/knowledge/**/*.md`.
Patterns: TMPDIR, trailing slash, mkdtemp, gettempdir/tempfile, scratch root, bwrap/bubblewrap,
capability currency / stale capability / capability row / re-run capability.

Verdict up front: **no contested scope.** Every hit is a closed historical landing in the sibling's
own repo, outside souji's write scope. Two are close doctrine neighbours worth citing as prior art
(tameshi executable-self-assessment for C1; game-dev-3d TMPDIR-honouring gate for C2). Nothing is
absorbed; everything is reported.

## 1. C1-CURRENCY surface (capability rows re-run against stated outputs)

| # | Lane | file:line | Overlap? | Located quote (verbatim, ≤25 words) | Contested scope |
|---|------|-----------|----------|--------------------------------------|-----------------|
| 1 | tameshi | `corpus/knowledge/executable-self-assessment.md:7` | YES — same method | "A standing capability row says what a tool can do and quotes what its command printed." | none (closed r31 entry; tameshi's own table) |
| 2 | tameshi | `corpus/knowledge/executable-self-assessment.md:66` | YES — same append-only restatement rule | "Correct a stale row by appending a new statement; never edit or delete the old row." | none (doctrine prior art) |
| 3 | tameshi | `SCORECARD.md:2172` | YES — restatement sections whose counter re-runs row commands | "Each capability row restates the line its frozen command prints at the round-46 revision" | none (closed r46/47) |
| 4 | mado | `SCORECARD.md:1625` | YES — same measurement shape (re-run rows, count mismatches) | "capability table vs frozen re-demonstration" → "1/12 mismatches → 0/12" | none (closed r24) |
| 5 | tsukuroi | `SCORECARD.md:1312` | adjacent — self-assessment re-run counter | "Re-run `python3 tools/check-self-assessment.py --revision <REV>` before treating any count here as current." | none (closed) |
| 6 | kotodama | `SCORECARD.md:426` | YES — currency sweep of recorded capability commands | "50/50 capability rows exit 0" … "all 50 recorded commands re-executed green" | none (closed r31) |
| 7 | chousa | `corpus/QUALITY.md:881`, `:915` | adjacent — capability-row pointer integrity counter | "SCORECARD.md capability rows and SHONEN.md evidence lines name paths the tree does not hold" | none (closed) |
| 8 | kaidoku | `SCORECARD.md:3119-3136` | adjacent — capability-row audit hygiene | four capability tables (:617, :2133, :2205, :2372), "capability rows 6→7" count audit | none (closed) |

## 2. C2-SCRATCH surface (TMPDIR / scratch root / trailing slash / bwrap /tmp)

| # | Lane | file:line | Overlap? | Located quote (verbatim, ≤25 words) | Contested scope |
|---|------|-----------|----------|--------------------------------------|-----------------|
| 9 | game-dev-3d | `corpus/knowledge/unreal-mcp/gate/run_gate.sh:59` | YES — Q71-identical repair (scratch root from TMPDIR) | "WORK_ROOT=${GATE_WORKDIR:-${TMPDIR:-/tmp}}" | none (closed r104) |
| 10 | game-dev-3d | `corpus/knowledge/unreal-mcp/gate/README.md:98`, `:379` | YES — TMPDIR honoured + W2 control | "TMPDIR is honoured too (this is the POSIX convention most tools already follow)"; W2 "WORK_ROOT=… (from TMPDIR)" … "the POSIX convention is honoured" | none (closed r104; corroborates C2 mechanism) |
| 11 | game-dev-3d | `SKILL.md:76`, `corpus/QUALITY.md:25` (Q14) | adjacent — error pattern "temp-dir-dependent gate" | "redirect the scratch root — `GATE_WORKDIR=<roomy dir>` (or `TMPDIR=`)" | none (closed) |
| 12 | mori | `SKILL.md:604` | INVERSE rule — selftests require private repo-local TMPDIR, refuse /tmp fallback | "Use an existing private scratch root for selftests; do not let an invalid TMPDIR fall back to /tmp." | none (closed; opposite direction from souji O1-O5) |
| 13 | mori | `corpus/knowledge/evidence-minimization-r18.md:3`, `freeze-order-r18.md:3`, `dispatch-ledger-r18.md:3`, `retention-reconciliation-r22.md:3` | adjacent — selftests require `TMPDIR=$PWD/.scratch` | "the selftest requires TMPDIR to be `<repo>/.scratch`" | none (closed) |
| 14 | kama | `corpus/QUALITY.md:353` (KQ51) | YES — private-TMPDIR hygiene leg | "A lane counter removes every temporary directory it creates" | none (closed r42) |
| 15 | tameshi | `corpus/knowledge/guard-kill-closure.md:129` | adjacent — bwrap envelope with private /tmp | "The probes run in the bwrap envelope … with `env -i`, a private /tmp" | none (closed) |
| 16 | tameshi | `corpus/knowledge/hermetic-env-differential.md:34` | adjacent — private HOME/TMPDIR profiles | "empty environment plus PATH, private HOME/TMPDIR, LANG=C, LC_ALL=C, TZ=UTC" | none (closed) |
| 17 | tameshi | `corpus/knowledge/mutation-case-kumitate-round-gate.md:24` | adjacent — TMPDIR placement inside a work tree breaks checks | "a `TMPDIR` inside a work tree makes 3 checks fail" | none (closed) |
| 18 | kumitate | `corpus/knowledge/mount-order-and-bind-scope.md:9`, `SKILL.md:618` | adjacent — bwrap fresh-/tmp tmpfs, refuse whole-/tmp binds | "mounts fresh `/tmp` and `/run` tmpfs roots" | none (closed r49/50) |
| 19 | chousa | `SKILL.md:162`, `corpus/knowledge/verification-r16.md:67` | mechanism overlap — strips ALL trailing slashes | "strips all trailing slashes for the prefix test only"; "`in_root` now strips all trailing slashes" | none (closed r15/16; root prefix test, not TMPDIR) |
| 20 | tsukuroi | `corpus/knowledge/update-safety-note.md:489` | adjacent — tool consuming TMPDIR | "defaults `CHECKUPDATES_DB` under `${TMPDIR:-/tmp}`" | none (closed) |
| 21 | kotodama | `PROVINCE.md:331` | adjacent — bwrap replay with TMPDIR inside sandbox | "Tier A bwrap mount-namespace replay … TMPDIR inside the sandbox" | none (closed r39 protocol) |
| 22 | audio | `SCORECARD.md:873`, `:892` | NO for C2 — TMPDIR-lock co-tenancy (lock folding), not scratch root | "TMPDIR-lock co-tenancy defect" | none (closed) |
| 23 | kagi | `corpus/knowledge/handler-on-disk-state.md:233-246` | NO — TMUX_TMPDIR server isolation | "use the isolated TMUX_TMPDIR form below for bare-start probes" | none (closed) |
| 24 | kaidoku | `SKILL.md:559`, `corpus/knowledge/2026-10-19-arc3-*.md` passim | adjacent — disk-backed TMPDIR for REA (host /tmp quota) | "a disk-backed `TMPDIR` is required, not optional" | none (closed; same host /tmp condition that motivates O1, different repair) |

## 3. Contested-scope determination

- No sibling lane holds an open (current-round) claim on either surface. All 24 rows above are
  closed historical landings in the siblings' own repositories — outside souji's write scope and
  outside this round's frozen predicates. Nothing contests souji r33's scope over its own
  SCORECARD.md / tools / fixtures.
- Not an overlap but flagged for the L1: tsukuroi's `child-env-allowlist-r33` probe
  (`tsukuroi-shokunin/SKILL.md:2870`, `:2940`, `:3001`, `:3106`) is **tsukuroi's own round 33**
  and names TMPDIR as one of its value-channel leak names. That is the child-environment
  allow-list surface (a different surface from scratch-root discipline); no routing conflict,
  but the shared "r33" number and shared TMPDIR vocabulary are a confusion risk in fleet reports.

## 4. Prior-art recommendations for the L1 (report, never absorb)

1. **C1 lesson Gate / SKILL bullet**: tameshi `executable-self-assessment.md` (:7, :66) already
   encodes the append-only capability-restatement rule souji r33 C1 rediscovers. Cite it as
   sibling doctrine; do not re-mine it as a new mistake class.
2. **C2 lesson Gate / SKILL error-pattern bullet**: game-dev-3d gate r104
   (`run_gate.sh:59`, README W0-W2) is a landed, control-verified instance of the Q71 repair
   (scratch root from `TMPDIR`, default `/tmp` preserved, named up-front failure on nonexistent
   root). It corroborates the mechanism but is **not a substitute** for the SOURCES rows the
   preregistration requires souji to open itself (POSIX repeated slashes; proc_pid_fd(5);
   Python tempfile.gettempdir/mkdtemp TMPDIR search).
3. No scope handoff to any sibling is required this round.
