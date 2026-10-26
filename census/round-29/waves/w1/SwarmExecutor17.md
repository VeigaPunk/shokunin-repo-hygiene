# SwarmExecutor17 — round-end landing checklist (executed at base)

STATUS: PARTIAL — the deliverable is complete and every command shape in it was executed and
verified at base `b8cb4b31ce80e2e3314b88e85d40ea9873180804`, but I breached the read-only bound
once (Finding 1: a scratch-clone `push` landed on the lane's `refs/heads/master`); I restored the
ref byte-exactly and re-verified `ahead=0 behind=0`, no ref on the stray object, and reported it
here rather than hiding it.

## Evidence

All lane paths below are under `/home/vgpnk/Projects/shokunin/souji-shokunin`. Scratch was
`/var/tmp/souji-r29-PreReportGateReadiness/` (clone `c`, toplevel printed
`/var/tmp/souji-r29-PreReportGateReadiness/c`), removed at the end. Lane readings are read-only.

1. Lane state at base and after repair:

```
$ /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/souji-shokunin
state branch=master local=b8cb4b31ce80e2e3314b88e85d40ea9873180804 remote=b8cb4b31ce80e2e3314b88e85d40ea9873180804 ahead=0 behind=0 head=detached tracked=1 untracked=0      (rc 0)
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-remote origin refs/heads/master
b8cb4b31ce80e2e3314b88e85d40ea9873180804	refs/heads/master      (rc 0)
```

2. Pre-report gate cases, scratch clone at base (gate =
`tools/souji-pre-report-gate.sh`, `--prereg census/round-29/records/preregistration.txt`):

| case | rc | output |
|---|---|---|
| report absent | 1 | `check-report=FAIL`, `check-shonen=FAIL`, `detail-shonen: found 0 headings, expected 1`; tip/clean/prereg PASS |
| one `^## SHONEN`, clean tree | 0 | five `check-*=PASS` |
| two `^## SHONEN` | 1 | `detail-shonen: found 2 headings, expected 1` |
| untracked `stray.txt` | 1 | `detail-clean: ?? stray.txt` |
| local commit unpushed | 1 | `check-tip=FAIL`, `detail-tip: local=6ff002aa… remote=b8cb4b31…` |
| same commit pushed | 0 | five PASS |
| `origin` unreachable | 1 | `check-tip=FAIL`, `detail-tip: local=… remote=<none>` |
| missing `--prereg` | 2 | `Usage: bash tools/souji-pre-report-gate.sh --lane ABS --branch NAME --report ABS --prereg ABS` |

`ls-remote` form used by the gate: first line, field 1, checked against `refs/heads/<branch>` as
40–64 hex.

3. Landing gate at base (`python3 -B tools/souji-landing-gate.py`):

```
--root <lane> --rev b8cb4b31ce80e2e3314b88e85d40ea9873180804 --round 29
rc=2  SUMMARY findings=3 … checked_reports=0
stderr: COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-29/ at b8cb4b31ce80e2e3314b88e85d40ea9873180804
same with --fleet-root /home/vgpnk/Projects/shokunin: rc=2, SUMMARY findings=0 …, same COULD-NOT-EVALUATE line
--round 28 at base: rc=2, findings=6, no .md reports under .ufo/waves/round-28/
--round 26 at base: rc=1, findings=21, checked_reports=466, carry_heading=0
--rev 000…0: rc=2, SUMMARY findings=0 all counters 0, COULD-NOT-EVALUATE cannot resolve revision …
--selftest: rc=0, SELFTEST pass=65 fail=0
scratch commit of one benign .ufo/waves/round-29/w1/Seat.md + corpus/lessons/round-29.md:
  without --fleet-root rc=1 findings=3, SUMMARY … checked_reports=1 carry_heading=1 status_lines=1
  with    --fleet-root rc=0 SUMMARY findings=0 … checked_reports=1 carry_heading=1
```

4. Census at base: `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin souji` rc 0, 36 lines, last two:
`souji	W04	S210 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c across scopes`
then `souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`. The committed
record `census/round-29/records/census-start.txt` is the same 36 lines plus `exit=0` (37 lines).
Census mode: rc 0, `souji	rows	139`.

5. SHONEN: the filed round-28 report has one `^## SHONEN` (rc 0); `SHONEN.md` has 4 `- [~]` boxes.

6. Misroot sweep at base: `git -C /home/vgpnk/Projects/shokunin status --porcelain` → 22 lines =
18 ` M` + 4 `??`. Untracked: `.tower/`, `.ufo/reports/round-41/mado.md`, `.ufo/waves/round-30/`,
`demo-cwd.txt` (30 bytes, content `/home/vgpnk/Projects/shokunin`).

No lane write other than the delivery and this report; no tool installed.

## Findings

1. **Write-bound breach, repaired (mine).** `git -C /home/vgpnk/Projects/shokunin/souji-shokunin
   status --porcelain` and `jj-lane.sh state` showed `tracked=1`, and the lane branch read
   `local=6ff002aa63a8d79a9ec34afd673f62e5ac8d8447 ahead=1`. Cause: my scratch repo was created
   with `git clone --no-local <lane>`, which sets `origin` to the lane itself; a `push` case in
   the scratch pre-report tests therefore pushed a one-file scratch commit (`base-marker.txt`,
   message `unpushed`) into the lane. The lane's HEAD is detached (jj-colocated), so git did not
   refuse it. Repair: `git -C <lane> update-ref refs/heads/master
   b8cb4b31ce80e2e3314b88e85d40ea9873180804 6ff002aa…` (compare-and-swap, current value checked
   first), reflog confirmed the prior entry was my `push` and the one before it jj's `export`
   (`b8cb4b3`). Re-verified: `state … local=b8cb4b31… remote=b8cb4b31… ahead=0 behind=0
   tracked=1 untracked=0`, `ls-remote origin refs/heads/master` unchanged, `for-each-ref` has no
   ref on `6ff002aa` (the object is dangling in the lane odb; I ran no `gc`/prune). Lane worktree
   and index were untouched throughout. The checklist carries this as an explicit trap warning
   (step 6). Location: lane `.git` refs, `/home/vgpnk/Projects/shokunin/souji-shokunin`.

2. **The lane is not clean, so `check-clean` will FAIL until resolved.** `git -C <lane> status
   --porcelain=v1 --untracked-files=all` at base prints exactly one line: ` M
   .ufo/waves/round-26/w1/ScribeGateDraft.md` (a 3-line addition naming an inbound round-31
   coordination message). Location: `.ufo/waves/round-26/w1/ScribeGateDraft.md`. Checklist step 0
   routes it to prompt §6.5 (commit through the helper or restore from `master:`); a seat cannot
   clear it.

3. **Landing gate terminal rc at round end is 2, not 0 — and that is the routed r28 defect, not a
   finding.** `.ufo/waves/` is gitignored (`.gitignore:1`), so `check_carry` enumerates no
   committed `.ufo/waves/round-29/*.md` and raises could-not-evaluate; the error wins the exit
   code and `checked_reports=0` while independent `LG-*` findings are still printed. Distinction
   verified: rc 2 always carries `COULD-NOT-EVALUATE<TAB><reason>` on stderr and `checked_reports=0`;
   rc 1 carries `LG-<ID>` TSV lines and no could-not-evaluate line. `--round 26` at base proves the
   evaluated shape (`checked_reports=466`, rc 1). Location:
   `tools/souji-landing-gate.py:469-474` (`check_carry`), `:1137-1141` (exit selection),
   `:1166-1167` (`COULD-NOT-EVALUATE` on stderr).

4. **`--fleet-root` is required to read the gate's findings.** Without it the base tip reports
   three `LG-DANGLING-PTR`: `corpus/README.md:217` citing `../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md`
   and `…/JjTrialSouji.md`, and `corpus/knowledge/jj-colocation-receipts.md:148` citing
   `.ufo/waves/hyaku/jj-w1/reports/`. With `--fleet-root /home/vgpnk/Projects/shokunin` all three
   classify as `fleet` and are not findings (`findings=0`, verified). Those fleet paths exist.

5. **Pre-report gate rc semantics: rc 2 is usage only.** Every substantive miss is rc 1 with a
   named `check-*` line, including an unreachable `origin` — which surfaces as `check-tip=FAIL`
   plus `detail-tip: … remote=<none>` because the gate discards `ls-remote` stderr
   (`tools/souji-pre-report-gate.sh:33-36`). So a tip failure is not evidence of a wrong hash;
   rerun `ls-remote` standalone. `--lane`/`--report`/`--prereg` must be absolute or the gate exits
   2 (`:22`). The report input must exist *before* the gate runs and belongs outside the lane, or
   `check-clean` fails.

6. **Misroot sweep at base yields no souji misroot.** 22 entries, 4 untracked
   (`.tower/`, `.ufo/reports/round-41/mado.md`, `.ufo/waves/round-30/`, `demo-cwd.txt`); none
   names souji round 29 (`demo-cwd.txt` holds only the fleet path), so nothing was copied or
   deleted. The 18 ` M` entries are driver files (`.ufo/state/*.report-baseline`, `.ufo/watchdog.log`,
   `.scratch/goal-20261025-hyaku-run7.md`) and must not be touched.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-landing-checklist.md` — ordered 0–8 checklist with each
  command's expected output shape as measured here at base, both gates' input lists and exit-code
  tables, the rc 2-vs-finding tell, and the scratch force-add recipe for evaluating the carry check.
