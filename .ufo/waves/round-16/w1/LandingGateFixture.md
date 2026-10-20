# LandingGateFixture — round 16 w1 report

Seat: SoujiR16.LandingGateFixture (executor, leaf).
Owned file: `tests/fixtures/r16-landing-gate.py` (new, 23 KB, executable,
python3 stdlib only). No other lane file touched.

STATUS: all 15 cases PASS (exit 0) against the live gate at work-tree HEAD;
no known fixture defect.

## What the fixture does

`python3 tests/fixtures/r16-landing-gate.py [--tool PATH]` runs
`python3 tools/souji-landing-gate.py --root R --rev REV --round N [--base B]`
against (a) the lane's committed history and (b) throwaway git repositories it
builds under a private `/var/tmp/souji-r16-lgfixture-*` dir (removed in
`finally`; verified absent after the run). Output is `CASE\tid\tPASS|FAIL\tdetail`
then `SUMMARY\ttotal=N\tfailed=M`; exit 0 iff all pass, 2 on missing
prerequisite (tool absent, no git, lane root not a worktree).

Held-out cases were written against the pinned contract plus both L1 steers
(blob reads, snapshot-root-only pin resolution, STATUS first-word allowlist,
phrase markers outside fences/tables, `## Seat-reported failures` carry with
`open`/`resolved@<hex>`, HTML-comment stripping, LG-OPEN-ADMITTED,
LG-FROZEN-MEASURED, exit 2 on missing wave dir, `compile()` for .py,
`bash -n` stderr as a finding). None is copied from the gate's selftest list.

## Measured output (verbatim)

```text
CASE	replay-b410186	PASS	exit=1 lg_rows=36
CASE	unterminated-case	PASS	exit=1 lg_rows=1
CASE	py-compile-defects	PASS	exit=1 lg_rows=2
CASE	truncated-heredoc	PASS	exit=1 lg_rows=1
CASE	missing-reg-and-changed	PASS	exit=1 lg_rows=2
CASE	uncited-nobase-invisible	PASS	exit=1 lg_rows=1
CASE	pin-only-inside-frozen-dir	PASS	exit=1 lg_rows=2
CASE	pin-vs-measured-commit	PASS	exit=1 lg_rows=1
CASE	marker-one-char-off	PASS	exit=1 lg_rows=1
CASE	marker-rewordings	PASS	exit=1 lg_rows=5
CASE	carry-inside-html-comment	PASS	exit=1 lg_rows=1
CASE	open-marker-admitted-true	PASS	exit=1 lg_rows=1
CASE	missing-wave-dir	PASS	exit=2 lg_rows=0
CASE	clean-all-green	PASS	exit=0 lg_rows=0
CASE	vacuity-stub	PASS	stub rc=0 stdout_bytes=0; replay assertions failed as required: yes
SUMMARY	total=15	failed=0
```

Exit code of the fixture run: 0.

## Case inventory and what each pins

| case | held-out input | expected → observed |
|---|---|---|
| replay-b410186 | real lane, `--rev b410186 --round 15` | exit 1 with LG-PARSE-REG (`tools/souji-census.sh`), LG-FROZEN-PIN (`r15-preservation-frozen` census pin), LG-SEAT-UNCARRIED (`ConfigRepair.md`), `checked_reports=` in SUMMARY. All present; 36 LG rows total (real r15 wave reports contain many uncarried marker lines — replay asserts inclusion, not exact count). |
| unterminated-case | cited `tools/registry.sh` ends inside `case … in` with no `esac`; two clean cited scripts as controls | exactly 1 LG-PARSE-REG for the broken path only. |
| py-compile-defects | cited `tools/indented.py` (tab/space `TabError`) and `tools/returns.py` (module-level `return`, which `ast.parse` accepts — verified) | 2 LG-PARSE-REG rows; gate uses `compile()`. |
| truncated-heredoc | cited `tools/hd.sh` ends inside `cat <<EOF` with no terminator; `bash -n` exits 0 with a stderr warning (verified: rc 0, `warning: here-document … wanted 'EOF'`) | LG-PARSE-REG — confirms stderr-as-finding. |
| missing-reg-and-changed | SKILL cites absent `tools/ghost.sh`; uncited `tools/uncited.sh` parse-clean at base, broken at REV | exit 1 with LG-MISSING-REG + LG-PARSE-CHANGED; no LG-PARSE-REG for the uncited path. |
| uncited-nobase-invisible | same REV, no `--base` | only LG-MISSING-REG; changed/parse checks correctly absent. |
| pin-only-inside-frozen-dir | `expected.json` pins `tools/pinned.sh` absent at snapshot root but present inside the frozen dir; `notes.txt` pinned dir-local and satisfied | LG-FROZEN-PIN for `tools/pinned.sh` (2 rows total: the second is LG-FROZEN-MEASURED for the same pin, since measured_commit lacks the file — tolerated); no finding for `notes.txt`. |
| pin-vs-measured-commit | pin matches REV bytes but `record.json` `measured_commit` has different bytes | LG-FROZEN-MEASURED only; no LG-FROZEN-PIN. |
| marker-one-char-off | SeatA `STATUS: INCOMPLETE — frobnicate the journal` vs lesson `… jouxrnal — open` (one char); SeatB carried verbatim with `resolved@<ancestor hex>` | SeatA flagged, SeatB not. |
| marker-rewordings | `**STATUS:** INCOMPLETE`, `STATUS: fails selftest 11/13`, `doesn't parse`, `do not ship this`, colonless `STATUS — INCOMPLETE`; fenced `STATUS: ok`/`does not parse` and a `syntax error` table row as negative controls | 5 rows (SeatA–E flagged), SeatF exempt. |
| carry-inside-html-comment | marker line carried only inside `<!-- … -->` under the heading | still LG-SEAT-UNCARRIED. |
| open-marker-admitted-true | marker carried with `— open` while lesson says `admitted: true` | LG-OPEN-ADMITTED. |
| missing-wave-dir | repo with no `.ufo/waves/round-77/` at REV | exit 2. |
| clean-all-green | cited .sh+.py clean, one marker carried `resolved@<hex>`, one benign `STATUS: none`, two satisfied frozen pins + matching `record_sha256`/`measured_commit`, `--base` exercised | exit 0, `findings=0`, zero LG rows — every check exercised on ≥1 passing item (C2 measured on inputs the C1 census repair cannot change). |
| vacuity-stub | in-fixture stub tool exiting 0 printing nothing | stub produces 0 findings → replay assertions all fail → fixture would report FAIL under `--tool <stub>`; case asserts the assertions failed as required. |

## Findings about the gate (advisory)

1. **Replay red is real but fat.** `--rev b410186 --round 15` emits 36 LG
   rows, not 3: the marker channel flags every uncarried STATUS/phrase line
   across all r15 seat reports (many are echoes of the r15 fault or non-
   failure statuses reworded). Inclusion assertions hold; the row volume is a
   signal-to-noise property of the real wave corpus, worth L1 attention when
   reading the green-at-round-end run (many r16 reports quote r15 vocabulary;
   check whether marker hits land under the lesson heading or stay uncarried).
2. **`pin-only-inside-frozen-dir` emits two findings for one pin** —
   LG-FROZEN-PIN (not at snapshot root) and LG-FROZEN-MEASURED (not at
   measured_commit). Semantically consistent (the file is missing at both
   resolutions); noted only so row counts are not read as pin counts.
3. **Fixture attribution limit:** `marker-one-char-off` relies on per-file
   seat reports rather than detail-text matching; if the gate later stops
   naming the seat file in findings, the absent-side of that case becomes
   unverifiable. Current gate names it (`lg_rows=1`, SeatB unflagged).
4. Contract ambiguity observed: the colonless `STATUS —` form IS flagged
   (SeatE in marker-rewordings fired); treat it as a marker variant.

## Risks / blockers

None blocking. The gate file arrived mid-wave; the fixture run above is the
single allowed invocation and it is green end-to-end. If the gate is edited
again, rerun `python3 tests/fixtures/r16-landing-gate.py`.

Tooling installs/updates: none. pacman untouched (paused host-wide).

## Commands

```sh
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/tools/ /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/ | head -60
ls /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-* /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-preservation-frozen/ ; ls /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-*
ls /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-15/w1/ /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/ | head -50
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/ ; ls /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ | head -40
mkdir -p /var/tmp/souji-r16-LandingGateFixture-probe && cd /var/tmp/souji-r16-LandingGateFixture-probe && printf '#!/bin/sh\ncase "$1" in\n  a) echo a;;\n' > uc.sh && printf '#!/bin/sh\ncat <<EOF\nline one\nline two\n' > hd.sh && printf 'def f():\n    a = 1\n\tb = 2\n' > ind.py && printf 'x = 1\nreturn 0\n' > ret.py && bash -n uc.sh; bash -n hd.sh; python3 -c "compile(open('ind.py').read(),'ind.py','exec')"; python3 -c "compile(open('ret.py').read(),'ret.py','exec')"; python3 -c "import ast; ast.parse(open('ret.py').read())"
rm -rf /var/tmp/souji-r16-LandingGateFixture-probe
python3 -m py_compile /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py && ls /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py
ls -d /var/tmp/souji-r16-lgfixture-* ; ls /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/__pycache__/
rm -rf /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/__pycache__ && cat /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/.gitignore
```

Non-shell (read tool): `skill://godspeed`,
`tests/fixtures/r15-preservation-frozen/{README.md,record.json,expected.json}`,
`.ufo/waves/round-15/w1/ConfigRepair.md`,
`corpus/lessons/round-15-verifier-spotcheck.md`, `SKILL.md:120-178`,
`.ufo/waves/round-16/w1/RevGateSpec.md`,
`.ufo/waves/round-16/w1/CriticGateVacuity.md`,
`.ufo/waves/round-16/w1-spec.json` (jq query on items LandingGate /
LandingGateFixture).
