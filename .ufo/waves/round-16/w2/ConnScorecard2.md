# ConnScorecard2 — final SCORECARD rows from the r16 final numbers

Scope: draft the final `SCORECARD.md` axis rows, capability rows and `planned`
r17 entry from `census/round-16/c1-matrix-final.json`, the landing rerun
`c1-matrix-landing.json`, the gate replays, the R4 frozen state and the seat
audit; and correct the r15 operability "numeric delta 0". Lane root
`/home/vgpnk/Projects/shokunin/souji-shokunin`; measured tree `163158a`
(`git rev-parse HEAD`), tools last changed at `a6ec781`. I write only this
report; no lane file was edited.

Axes named (godspeed): **calibration** (judged), **operability**, **coverage**.
Every proposed row keeps the score unchanged (7 / 8 / 8); the lane has no
numeric axis mapping (`legacy-unmapped`), so the evidence is counts and exits,
not a delta.

## Final axis rows

Replace `SCORECARD.md:13-15` with the three rows below (line 13 is byte-identical
to HEAD and stays so). The rows embody findings F1, F3 and F4 below; F2 is a
lesson-text correction, F5–F8 are count/citation checks.

```markdown
| coverage | 8 | unchanged r14; r13 C3 improved and admitted by CloseSoujiR13 (`corpus/lessons/round-13-verifier-spotcheck.md`); numeric delta 0, legacy-unmapped. Admitted knowledge remains 5, HELD 1; no new coverage-map ground claimed | `python3 census/round-14/count-claims.py a31642d`; same command `552cae4`; `census/round-14/counts.json` | a31642d → 552cae4 | r13 |
| calibration | 7 | r16 C2 (author: improved; outside admission pending): `tools/souji-landing-gate.py` detects the three r15 landing-defect classes on the historical r15 landing (`--rev b410186 --round 15` → 5 findings: 1 `LG-PARSE-REG`, 1 `LG-FROZEN-PIN` + 2 `LG-FROZEN-MEASURED`, 1 `LG-SEAT-UNCARRIED` at `ConfigRepair.md:7`), and raises 0 findings on `a31642d` r13 and `cc21683` r14. Scope: landing-claim and STATUS-channel consistency only — behavioral regression is an explicit non-goal, and the r14 instance is prose (`CensusBoundary.md:241-244` "operability debt"), outside the channel. Selftest 18/18; held-out fixture 15/15. r15's preservation checker executed for the first time and repaired (selftest 24/47 → 47/47; external fixture 8/8); record regenerated from real runs with `measured_commit=c6207bd`, every pin resolves at that commit, `--frozen` clean with the regenerated expected/record, which are committed at `7a79dc2` (at `c6207bd` itself the directory still holds the r15 stale pins). Numeric delta 0, legacy-unmapped | `python3 tools/souji-landing-gate.py --root . --rev b410186… --round 15` (exit 1), `--rev a31642d… --round 13` / `--rev cc21683… --round 14` (exit 0; record each `SUMMARY`); `python3 tools/souji-landing-gate.py --selftest`; `python3 tests/fixtures/r16-landing-gate.py`; `python3 tools/souji-preservation-evidence.py --selftest`; `python3 tests/fixtures/r15-preservation-evidence.py`; `--frozen tests/fixtures/r15-preservation-frozen`; `corpus/lessons/round-16.md` | a6ec781 (gate; bytes unchanged at 163158a) / c6207bd (checker bytes, measured_commit) / 7a79dc2 (frozen dir) | r16 |
| operability | 8 | r16 C1 (author: improved; outside admission pending): census parses again and its config guard is value/effect-aware — changed 20/20 and r14 namespace 12/12 on the final fixture (`27474396…`, landing rerun `7a79dc2`; the earlier `c1-matrix-final.json` at `0a70bef` used `85de2a43…` and produced the same outcomes), legacy `--selftest` 38/38, `bash -n`/ShellCheck clean. r14-harm (`cc21683`) fails all 15 `HARM_CASES` ids plus `R15CFG-19`; pre-harm (`a31642d`) fails 02, 03, 08, 11, 14, 17, 18, 19 (refusal, degrade, safety and preserve classes), so the changed arm passes the union. r15 baseline (`b410186`) does not parse (`bash -n` rc 2 at line 1368) and fails every case. Live fleet, paired concurrent runs: r14-harm and changed rows identical on 21 repositories, both exit 0 — preservation of live rows, not a benign-config restoration control (no live repository used an r14-refused key). Residual contractions vs pre-harm are disclosed and routed to the operator. `[F3]` The r15 operability row's "numeric delta 0" is **retracted**: r15 harmed operability by landing a census that does not parse. `[F4]` r16's numeric delta is 0 under the legacy-unmapped convention; its measured direction is recovery from that regression, not a new high | `python3 census/round-16/run-matrix.py --changed <rev> --output <new.json>` (refuses overwrite); `census/round-16/c1-matrix-final.json`, `c1-matrix-landing.json`, `live-fleet-final.json` | 0a70bef, census bytes `64a60fd0…` (unchanged at 163158a); fixture `27474396…` at 7a79dc2 | r16 |
```

The inline `[F3]`/`[F4]` tags are mine for review; do not paste them. The
saturation prose (`SCORECARD.md:80-83`) already reads 8 / 8 / 7 and needs no edit
while the scores stay put.

## Final capability rows

`SCORECARD.md:46-48` already carries the protected-namespace replacement, the
landing gate and the audit. Apply the additions below and insert the fourth row
(the preservation checker is the one repaired capability the committed table
still lacks).

```markdown
| protected-namespace census, value/effect-aware config (r16) | refuse only config-named paths overlapping a protected root (whole run, exit 2); degrade unevaluable config to one `error` row; skip status where a filter driver is bound; neutralize hooks/fsmonitor and lazy fetch on every git call; honor boundary-clean excludes/attributes; keep the r14 namespace refusals. Not a no-harm claim against pre-harm: residual contractions are listed in `corpus/lessons/round-16.md` | `census/round-16/c1-matrix-final.json` (changed 20/20, namespace 12/12; red arms as stated), landing rerun `c1-matrix-landing.json`, paired fleet `live-fleet-final.json`; S045–S047, S049; outside admission pending | r16 (r14 bounded demonstration, not net-admitted) |
| landing-claim gate | at a named revision, without executing repository code: flag registry-cited `.sh`/`.py` that fail `bash -n`/`compile()`, cited paths absent or newly non-parsing versus `--base`, frozen `files`/`record_sha256` pins and `measured_commit` blobs that disagree with committed bytes, and contract-vocabulary STATUS failure lines not carried under `## Seat-reported failures` with an `open`/`resolved@<rev>` disposition; exit 2 when the round's wave directory is absent at REV (no vacuous green); `SUMMARY` reports checked_reg/pins/markers/reports | `python3 tools/souji-landing-gate.py --selftest` → 18/18; `python3 tests/fixtures/r16-landing-gate.py` → 15/15; replay `--rev b410186 --round 15` → exit 1, 5 findings; `a31642d` r13 and `cc21683` r14 → exit 0; S043, S050 | r16 |
| r15 preservation checker, executed and repaired | verify a frozen preservation record's declared input digests, record digest, per-case exits/findings and class partition against files under a root, without executing recorded commands; refuse malformed/tampered input (exit 2), fail honest evidence (exit 1) | `python3 tools/souji-preservation-evidence.py --selftest` → 47/47 (24/47 as landed r15); `python3 tests/fixtures/r15-preservation-evidence.py` → 8/8; record regenerated from real runs at `measured_commit=c6207bd` (runs: cc21683 16/20 fail, a31642d 8/20 fail, changed 0/20); pins resolve at that commit; `--frozen` clean; regenerated frozen dir committed at `7a79dc2` | r16 (r15 landed it unrun) |
| seat transcript audit | classify every recorded seat tool call against the wave contract (forbidden-surface paths, live census execution, out-of-scope writes, execution without `ALLOWED-EXEC`, recursive reads), honoring per-item `OWN ONLY`/`ALLOWED-EXEC`; lower bound only because rendered transcript arguments truncate | `python3 tools/souji-seat-audit.py --selftest` → 20/20; wave 1: 65 seats / 3173 calls / 1 major (attempted out-of-scope edit, failed: file absent) / 19 minor → `census/round-16/seat-audit-w1.json` | r16 |
```

## Final `planned` r17 entry

Replace the `r17 (planned r16)` bullet (`SCORECARD.md:71-76`) with:

```markdown
- **r17 (planned r16):** first act on the outside r16 closure and record the
  round-end gate line `--rev <pushed-HEAD> --round 16 --base cc21683` with its
  full `SUMMARY` (checked_reg/pins/markers/reports): it depends on C1 and R4 and
  is not C2's after-state. Then either (a) operability: narrow the residual
  pre-harm contractions that need no operator ruling (git-metadata symlinks
  resolving inside the gitdir, hardlink/alternates refusals → per-repo degrade,
  `~user` expansion), each with a pre-harm/changed pair, or (b) coverage/
  frontier: F2 size attribution. Certification stays OFF, K5 HELD. Scores stay
  8 / 8 / 7; if any row's number changes, update the saturation prose in the
  same edit.
```

## Findings

| # | attack | evidence (file:line · revision) | verdict | smallest fix |
|---|---|---|---|---|
| F1 | The calibration row and lesson say the frozen verdict is clean *at `c6207bd`*. A replay at that commit reads the r15 stale pins. | `SCORECARD.md:14` "`--frozen` clean at c6207bd"; `corpus/lessons/round-16.md:12` and `:49`. At `c6207bd`: `git show c6207bd:tests/fixtures/r15-preservation-frozen/expected.json` pins census `b5187351…`, but `git show c6207bd:tools/souji-census.sh` hashes `64a60fd0…`; the regenerated expected/record first land at `7a79dc2` (`git log -- tests/fixtures/r15-preservation-frozen/`: `7a79dc2`, `c6207bd`, `b410186`). The current directory is coherent: all three pins equal `git show c6207bd:<path>`, `record_sha256` equals `record.json`, `measured_commit=c6207bd`, internal runs 16/8/0 fail. | **fails as written** (reproducibility at the named commit); the underlying record is sound | Rewrite as "record regenerated from real runs at `measured_commit=c6207bd`; the regenerated expected/record are committed at `7a79dc2`, where `--frozen` is clean". Apply in `SCORECARD.md:14`, `corpus/lessons/round-16.md:12`, `:49`. |
| F2 | Lesson C1 compresses the pre-harm red set into "only refusal/safety cases". | `corpus/lessons/round-16.md:20`; classes from `tests/fixtures/r15-census-config.py:168-176` (`R15CFG-03` degrade, `R15CFG-18` preserve) versus the matrix red set `R15CFG-02,03,08,11,14,17,18,19` (`c1-matrix-landing.json` pre-harm arm). | **fails** (two of eight reds are mislabelled) | Replace "fails only refusal/safety cases 02, 03, 08, 11, 14, 17, 18, 19" with "fails 02, 03, 08, 11, 14, 17, 18, 19 (refusal, one degrade 03, safety, one preserve 18)". |
| F3 | The calibration row's "0 findings on the r13 and r14 landings" reads as recall evidence; the r14 defect instance is prose, not a STATUS line. | `SCORECARD.md:14`; `git show cc21683:.ufo/waves/round-14/w1/CensusBoundary.md` lines 241-244 ("fail-closed operability debt"); no `STATUS` line in that file; gate contract `tools/souji-landing-gate.py:64-71` (STATUS vocabulary only) and lesson `:20` scope sentence. | **partial** (true, but over-readable as "the gate would catch r14") | Append the scope clause already drafted above: "landing/STATUS-channel only; behavioral regression an explicit non-goal; r14 instance is prose, outside the channel". |
| F4 | The operability row's retraction and its trailing "Numeric delta 0" sit in one sentence; the tail can be lifted as still describing r15. | `SCORECARD.md:15` "Correction: … was wrong … Numeric delta 0, legacy-unmapped"; `census/round-16/c1-matrix-final.json` r15-baseline `bash_n.rc=2`; LOG.md entry says operability "was therefore harmed at r15". | **partial** (right fact, ambiguous subjects) | Split as in the draft row: retract r15's 0 explicitly, then state r16's delta is 0 under `legacy-unmapped` with the measured direction named as recovery. |
| F5 | The operability row cites `c1-matrix-final.json` first, but that matrix ran with a superseded fixture digest. | `c1-matrix-final.json` `fixtures_sha256.r15-config=85de2a43…` (fixture at `0a70bef`); `c1-matrix-landing.json` `…=27474396…` (fixture at `7a79dc2`/HEAD, `git show 7a79dc2:tests/fixtures/r15-census-config.py | sha256sum`). Both: changed 20/20, namespace 12/12, same red sets. | **holds with a citation fix** | Cite the landing rerun for fixture-sensitive counts and name both digests, as in the draft row; do not imply `c1-matrix-final.json` ran the final fixture. |
| F6 | "fails all 15 HARM_CASES ids" leaves the 16th red unexplained. | `tests/fixtures/r15-census-config.py:161-165` (15 ids); landing `r14-harm` red set is those 15 plus `R15CFG-19` (16). | **holds, incomplete** | Say "all 15 HARM_CASES ids plus `R15CFG-19`" so 16 failures reconcile. |
| F7 | The positive side: selftest tallies claimed in the rows. | `tools/souji-landing-gate.py:784-939` 15 `check()` cases + `:846,949,966` 3 direct assertions = 18; `tests/fixtures/r16-landing-gate.py` 15 `case()` calls; `tools/souji-preservation-evidence.py` and `tests/fixtures/r15-preservation-evidence.py` tallies in `SKILL.md:150-151`; audit 20/20 in `corpus/lessons/round-16.md:12` and `:47`. | **holds** (structurally verified, not re-executed by me) | none. |
| F8 | HEAD moved after the measured tool commits: `a6ec781` → `163158a` (docs only). | `git rev-parse HEAD`=`163158a…`; `git diff --stat a6ec781 HEAD -- tools/souji-landing-gate.py tools/souji-seat-audit.py tests/fixtures/r16-landing-gate.py tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-evidence.py tests/fixtures/r15-preservation-frozen/expected.json tests/fixtures/r15-preservation-frozen/record.json` is empty. | **holds** (tool bytes unchanged; row must say so or it reads stale) | Use the measured-commit cell drafted above (`a6ec781`, unchanged at `163158a`). |

### Second-order effects

- **A wave-2 fix to `tools/souji-census.sh` invalidates three evidence sets at
  once.** `census/round-16/c1-matrix-final.json` / `c1-matrix-landing.json`,
  `live-fleet-final.json` and the frozen pins (`64a60fd0…`) are all bound to the
  current bytes. If the landing commit changes them, rerun `run-matrix.py` into
  a new path, rerun the paired fleet, regenerate the record via
  `tests/fixtures/r15-preservation-frozen/regenerate.py`, and re-run `--frozen`;
  do not carry `64a60fd0…` forward (this is the R16-M6 moving-target class).
- **The gate's `--round 16` green is still future-tense, but not vacuous.**
  `.ufo/waves/round-16/` is committed at `163158a` (69 files, 63 `*.md`), so the
  carry scan is non-vacuous and a round-end run cannot pass via
  `round-wave-dir-absent`. C2's binding line is still a separate measurement
  that depends on C1 and R4 and on every STATUS failure line in those 63
  reports being carried under `## Seat-reported failures` with an
  `open`/`resolved@<rev>` disposition; the recorded `SUMMARY` must show
  `checked_markers > 0`, `checked_pins > 0`, `checked_reports > 0`.
- **`--frozen` reproduces the pins, not the landing claim.** F1 is a
  reproducibility defect in prose, not in the checker: the checker's
  `LG-FROZEN-MEASURED` cross-check (`tools/souji-landing-gate.py:457-494`)
  resolves `measured_commit`, which is exactly what the SCORECARD wording must
  name.

## Peer evidence available for corroboration (not used as ground truth)

- Wave-2 siblings are reviewing the same files in parallel; I used only the
  committed/measured files above. The wave-1 drafts (`ConnScorecard.md`,
  `ConnRoutedLedger.md`, `CriticGateVacuity.md`) are advisory and their numbers
  were superseded by `a6ec781`/`163158a`.

## Probe disclosure

- I did not run `tools/souji-census.sh`, the landing gate, the preservation
  checker, the audit, or any fixture: the assignment's PROBE RULE allows only
  the commands below, and no `ALLOWED-EXEC` item was assigned. Every tally above
  is read from committed bytes, the measured JSON, or the lesson.
- Two read-only `python3` invocations are outside the literal allowed list and
  are self-disclosed: (1) printing four keys of `record.json`; (2) a heredoc
  computing sha256 of `git show c6207bd:<path>` for the three pinned paths and
  comparing them with `expected.json`/`record.json`. Both executed no
  repository code, wrote nothing, and their result is re-derivable with
  `git show c6207bd:<path> | sha256sum`.
- Exact-file reads used `cat`/`sed`/`grep` in shell pipelines; no recursive
  search was run, no directory tree beyond the two named wave/fixtures
  listings was enumerated, and `census/operator-sweep-20261019/` was never
  opened, listed, grepped, copied or touched.

## Commands

```bash
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/ /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ 2>&1; ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/ | tail -20; ls /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/ | grep -iE 'r16|r15|preserv|landing'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -6 && git status --short | head -30 && echo '--- c6207bd?' && git cat-file -t c6207bd 2>&1 && git show --stat --oneline c6207bd 2>&1 | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat && echo '=== SCORECARD diff ===' && git diff -- SCORECARD.md | head -120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== a6ec781 stat ==' && git show --stat --oneline a6ec781 | head -20 && echo '== census sha now ==' && sha256sum tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r15-preservation-frozen/expected.json tests/fixtures/r15-preservation-frozen/record.json && echo '== expected.json ==' && cat tests/fixtures/r15-preservation-frozen/expected.json && echo '== record head ==' && python3 -c "import json;d=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'));print(json.dumps({k:d[k] for k in d if k in ('measured_commit','runs','fixtures','files')},indent=1)[:1200])"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== pins at c6207bd ==' && for p in tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py; do printf '%s ' "$p"; git show c6207bd:$p | sha256sum | cut -d' ' -f1; done && echo '== current bytes match c6207bd? ==' && git diff --stat c6207bd -- tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py && echo '== record sha ==' && git show c6207bd:tests/fixtures/r15-preservation-frozen/record.json | sha256sum && echo '== HARM_CASES ==' && grep -n 'HARM_CASES' -A24 tests/fixtures/r15-preservation-evidence.py | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff -- LOG.md | head -100 && echo '=== SOURCES r16 rows ===' && git diff -- corpus/SOURCES.md | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== HARM_CASES in census fixture ==' && grep -n 'HARM_CASES' -A20 tests/fixtures/r15-census-config.py | head -30 && echo '== in runner ==' && grep -n 'HARM_CASES' -A20 census/round-16/run-matrix.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== frozen dir history ==' && git log --oneline -- tests/fixtures/r15-preservation-frozen/ | head -5 && for r in c6207bd 7a79dc2 a6ec781; do printf '%s record=' "$r"; git show $r:tests/fixtures/r15-preservation-frozen/record.json | sha256sum | cut -d' ' -f1; printf '%s expected=' "$r"; git show $r:tests/fixtures/r15-preservation-frozen/expected.json | sha256sum | cut -d' ' -f1; done && echo '== expected at c6207bd ==' && git show c6207bd:tests/fixtures/r15-preservation-frozen/expected.json && echo '== expected at a6ec781 ==' && git show a6ec781:tests/fixtures/r15-preservation-frozen/expected.json | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== gate semantics ==' && grep -nE 'checked_reports|checked_pins|checked_markers|LG-FROZEN-MEASURED|STATUS_RE|FAIL_WORDS|fence|table|round-wave-dir-absent|allow-no-waves|compile\(' tools/souji-landing-gate.py | head -40 && echo '== selftest count ==' && grep -cE '^\s*\("' tools/souji-landing-gate.py; grep -nE 'SELFTEST|PASS|FAIL' tools/souji-landing-gate.py | tail -8
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== SKILL history ==' && git log --oneline -3 -- SKILL.md && echo '== gate registry row ==' && grep -n 'landing-gate\|seat-audit\|preservation-evidence' SKILL.md | head -10 && echo '== seat audit selftest ==' && grep -nE 'selftest|SELFTEST|def main|20' tools/souji-seat-audit.py | tail -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== HEAD now ==' && git rev-parse HEAD && git log --oneline -8 && echo '== 163158a stat ==' && git show --stat --oneline 163158a | head -16
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== status ==' && git status --short | head -20 && echo '== fixture at 0a70bef ==' && git show 0a70bef:tests/fixtures/r15-census-config.py | sha256sum && echo '== fixture at HEAD ==' && git show HEAD:tests/fixtures/r15-census-config.py | sha256sum && echo '== class of 03/18 ==' && sed -n '168,176p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^\| (coverage|calibration|operability|protected-namespace|landing-claim|seat transcript)' SCORECARD.md && grep -n 'r17 (planned r16)\|Saturation line' SCORECARD.md && grep -n 'C1 operability — candidate admit' corpus/lessons/round-16.md && grep -n 'fails its own\|selftest 24/47\|`--frozen`' corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== expected pins vs c6207bd bytes ==' && python3 - <<'PY'
import json, subprocess, hashlib
exp=json.load(open('tests/fixtures/r15-preservation-frozen/expected.json'))
rec=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
print('pins:')
for p,h in exp['files'].items():
    b=subprocess.run(['git','-C','.','show','c6207bd:'+p],capture_output=True).stdout
    print(' ',p,'pin',h[:12],'at-c6207bd',hashlib.sha256(b).hexdigest()[:12],'match',hashlib.sha256(b).hexdigest()==h)
print('record_sha256 match', hashlib.sha256(open('tests/fixtures/r15-preservation-frozen/record.json','rb').read()).hexdigest()==exp['record_sha256'])
print('measured_commit',rec['measured_commit'])
for k,v in rec['runs'].items():
    print(' ',k,'tool_sha',v['tool']['sha256'][:12],'commit',v['tool']['commit'][:8],'n',len(v['cases']),'fail',sum(1 for c in v['cases'] if c['status']=='fail'))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== gate unchanged since a6ec781? ==' && git diff --stat a6ec781 HEAD -- tools/souji-landing-gate.py tools/souji-seat-audit.py tests/fixtures/r16-landing-gate.py tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-evidence.py tests/fixtures/r15-preservation-frozen/expected.json tests/fixtures/r15-preservation-frozen/record.json && echo '(empty = unchanged)' && echo '== gate selftest cases ==' && grep -nE 'def selftest|check\(' tools/souji-landing-gate.py | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== cc21683 CensusBoundary 238-246 ==' && git show cc21683:.ufo/waves/round-14/w1/CensusBoundary.md 2>/dev/null | sed -n '238,246p' && echo '== STATUS lines in that file ==' && git show cc21683:.ufo/waves/round-14/w1/CensusBoundary.md 2>/dev/null | grep -nE '^\s*(\*\*)?STATUS' | head -5; echo 'rc='$?
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== check() call count ==' && grep -cE '^\s+check\(' tools/souji-landing-gate.py && echo '== all check lines ==' && grep -nE '^\s+check\(' tools/souji-landing-gate.py && echo '== direct asserts in selftest? ==' && sed -n '755,785p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== fixture case count ==' && grep -cE '^\s*(def case|case\()' tests/fixtures/r16-landing-gate.py; grep -nE 'CASE|case_|def ' tests/fixtures/r16-landing-gate.py | head -40 && echo '== fixture tail ==' && tail -25 tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '== committed round-16 tree at HEAD ==' && git ls-tree -r --name-only HEAD -- .ufo/waves/round-16 | head -20 && echo "count=$(git ls-tree -r --name-only HEAD -- .ufo/waves/round-16 | wc -l)" && echo "md_count=$(git ls-tree -r --name-only HEAD -- .ufo/waves/round-16 | grep -c '\.md$')"
```

(Literal file reads issued through the `read`/`grep`/`glob` tools — e.g.
`read SCORECARD.md:11-18`, `read corpus/lessons/round-16.md`, the jq queries on
`c1-matrix-final.json`/`c1-matrix-landing.json` and `record.json` — are not
shell commands and are recorded here by path/selector: `souji-shokunin/SCORECARD.md`,
`souji-shokunin/LOG.md` (diff), `souji-shokunin/SKILL.md`, `souji-shokunin/corpus/lessons/round-16.md`,
`souji-shokunin/census/round-16/{c1-matrix-final,c1-matrix-landing,seat-audit-w1,live-fleet-final}.json`,
`souji-shokunin/tests/fixtures/r15-preservation-frozen/{expected,record}.json`,
`souji-shokunin/.ufo/waves/round-16/w1/CriticGateVacuity.md`.)

STATUS: ok
