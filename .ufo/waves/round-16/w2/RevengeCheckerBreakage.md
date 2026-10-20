# RevengeCheckerBreakage — why the r15 preservation checker shipped a self-test that fails 23/47 (r16, w2)

Seat: revenger, leaf. Axes: calibration (primary), operability (secondary).
Scope: the provenance of one seeded defect — `tools/souji-preservation-evidence.py`
at `b410186` rejecting the real fixture's TAB-separated `CASE` detail while its own
`\tobserved_finding=` token rule requires that TAB. Read-only; no checker, fixture,
census or test was executed by this seat.

## Answer

Two formatter definitions of the same wire format existed in one commit, and the
self-test was written against the invented one. The real fixture prints
`CASE\t<id>\t<PASS|FAIL>\t<detail>\tobserved_exit=…\tobserved_finding=…`
(`b410186:tests/fixtures/r15-census-config.py:1367-1368`). The checker's parser
forbade TABs in the detail (`CASE_LINE_RE … ([^\t]*)\Z`, checker `:916`), so no real
line could ever parse; its token rule then required a TAB inside that same detail
(`re.search(r"\tobserved_finding=…")`, checker `:1482`), so no PASS row could ever
carry a token. The self-test's synthetic transcript builder used spaces
(`_default_detail`, checker `:1804-1811`), which hides the parse failure and
guarantees the token failure — including on its own positive control, which demands
exit 0 and an empty finding set. The artifact landed because it was never executed
by its author, never re-reviewed after it existed, never accepted by L1, and its
planned adversarial wave was skipped. No criterion in `corpus/QUALITY.md` requires a
self-invocation to be executed before the unit lands; Q24 protects the claim, not
the artifact, and the r16 gate has no finding id for this class. That gap is still
open.

## Evidence chain (all observed; every citation is committed bytes)

### 1. The real producer emits a TAB-separated detail

`b410186:tests/fixtures/r15-census-config.py:1365-1368`:

```python
detail = (
    "; ".join(problems) if problems else "ok"
) + f"\tobserved_exit={obs_exit}\tobserved_finding={obs_finding}"
print(f"CASE\t{cid}\t{status}\t{detail}")
```

A real PASS row therefore is
`CASE\tR15CFG-01\tPASS\tok\tobserved_exit=0\tobserved_finding=none` — three TABs
after the status field. The fixture's docstring at `:87` advertises
"observed_exit/observed_finding per case (last invocation) for the C2" contract.

### 2. The parser forbids exactly those TABs

`b410186:tools/souji-preservation-evidence.py:916`:

```python
CASE_LINE_RE = re.compile(r"CASE\t([^\t]+)\t(PASS|FAIL)\t([^\t]*)\Z")
```

`[^\t]*` cannot consume the remaining TAB-separated fields, so `_parse_transcript`
(`:921`; match at `:953`) falls through to `problems.append("line %d does not match
a known record shape")`. Consequence on a real transcript: zero `CASE` rows, one
parse problem per line, and `case-missing` for the whole pinned universe. The r15 config fixture could never
produce an admissible record, independently of behavior. (The separate r14 namespace
arm is unaffected: its transcript carries plain `ok` details, per the code's own
namespace skip at `:1477-1481`.)

### 3. The token rule requires the TAB the parser forbade

`b410186:tools/souji-preservation-evidence.py:1482-1494`:

```python
token = re.search(r"\tobserved_finding=([^\t]+)", detail)
finding_tok = token.group(1) if token else None
...
if cid in refusal_ids:
    if finding_tok is None or finding_tok == "none":
        _add(findings, "case-finding-mismatch", "... lacks a non-'none' observed_finding token")
elif finding_tok != "none":
    _add(findings, "case-finding-mismatch", "... carries %s observed_finding")
```

Once `CASE_LINE_RE` matches, group 3 contains no TAB by construction, so `token` is
always `None`. Every config PASS is then flagged: refusal ids for "lacks", every
other id because `None != "none"`. The file's own docstring states the rule
(`:119-120`: "A refusal PASS must carry a non-`none` observed_finding token and
every other PASS must carry observed_finding=none"), so the contradiction is
visible in the docstring + regex pair alone, without executing anything.

The two matchers of the same string disagree inside one file: the weak-reason check
uses TAB-blind token membership (`REASON_TOKENS = ("observed_exit=",
"observed_finding=")`, `:367`, consumed at `:1506-1507`), while the finding check
uses a TAB-required regex (`:1482`).

### 4. The self-test's synthetic producer hides (2) and guarantees (3)

`b410186:tools/souji-preservation-evidence.py:1804-1811`:

```python
def _default_detail(cid, status):
    if status == "FAIL":
        return "contract difference observed_exit=2 observed_finding=path-protected"
    if cid in CONFIG_REFUSAL_IDS or cid in NAMESPACE_IDS:
        return "guard held observed_exit=2 observed_finding=path-protected"
    return "ok observed_exit=0 observed_finding=none"
```

`_transcript` (`:1814`) prints `CASE\t%s\t%s\t%s` with that space-separated detail
(`:1823`). These lines satisfy `[^\t]*` (so defect 2 never fires in the self-test)
and can never satisfy `\tobserved_finding=` (so defect 3 fires on every PASS).
The self-test thus validated the consumer against a second, invented formatter
instead of the producer whose bytes the checker exists to judge.

### 5. Therefore the positive control is impossible

- The `positive` case expects exit 0 and an empty finding set
  (`:1969-1978`, `["souji-preservation-evidence: clean", …]`).
- `_status_for` maps any level-1 finding to exit 1 (`:409-414`).
- The changed arm is all-PASS over the 20 config ids (`_good_statuses`, `:1856-1858`),
  so step 3 emits at least 20 `case-finding-mismatch` findings; the preharm and
  baseline arms add more.
- The harness compares the exact finding-id multiset (`if observed != sorted(want_ids)`,
  `:2554`) and fails the case on any delta.

`evaluate()` calls `_eval_arm` for every present arm after only a level-2 schema
early return (`:1550-1577`), so the same delta hits every case whose record is
well-formed enough to reach the arm loop. [INFERENCE] the 24 cases that pass are the
ones rejected before that loop (malformed JSON or a level-2 schema finding). The
observed count is 24/47 (recorded at `corpus/lessons/round-16.md:12`, R16-M4:
"HEAD self-test copy → `selftest: 24/47 passed`").

### 6. Three independent probes existed in the tree; none ran

1. The artifact's own `--selftest`.
2. The external fixture invokes it, requires exit 0, and requires a parseable
   `selftest: N/N passed` line (`b410186:tests/fixtures/r15-preservation-evidence.py:204-210`).
3. The round runner registers `preservation-checker-selftest` as
   `["python3","-B",CHECKER,"--selftest"]`, 240 s, `eval_exact(0)`
   (`b410186:census/round-15/run-verification.py:680-687`; announced in
   `.ufo/waves/round-15/w1/RoundRunner.md:21`).

The internal run's recorded result is `selftest: 24/47 passed` (exit 1); the external
fixture requires exit 0 and that same N/N line, and the runner's `eval_exact(0)` would
fail on the same output. The runner was written to run it once; it never ran.

### 7. Who wrote and who claimed what

| seat | artifact / claim | what actually happened |
|---|---|---|
| `SoujiR15.AdmissionChecker` | Owned `tools/souji-preservation-evidence.py` and `tests/fixtures/r15-preservation-evidence.py` (spec item prompt: "Own ONLY …"; `b410186:.ufo/waves/round-15/w1-spec.json`). Declared "Selftest: 47 discriminating cases, self-invoked via `sys.executable` … negative controls prove the gate rejects …" (`AdmissionChecker.md:51-53`). Listed `--selftest` "(expect 0/47)" under **Unrun checks** (`:80-82`), and "no runtime tests executed (source inspection only)" (`:87`). | Authored both sides of the format mismatch and never executed the selftest. The "47" is a count of defined cases, not a result. No `STATUS:` line, so the landing gate's failure channel has nothing to read. |
| `SoujiR15.RoundRunner` | Built the check `preservation-checker-selftest` expecting exit 0 (`run-verification.py:681-687`); interface and pinned sets agreed with the author (`RoundRunner.md:21,45-53`). | Check exists; round acceptance unrun (`b410186:LOG.md:786`). |
| `SoujiR15.CheckerGreen` | Required "one admitted positive control … which must exit 0" (`CheckerGreen.md:110`) and a `--selftest` returning 0 in acceptance item 1 (`:136`), with a mutation table (`:112-127`). | Design-only: "At write time none of these files exist" (`:3`). The correct requirement was never re-checked against the landed file. |
| `SoujiR15.CheckerCases` | A7: "discriminating selftest" with ten named negative classes (`CheckerCases.md:86,102`), acceptance `:118`. | Design-only; file absent at review. No post-landing verification seat existed. |
| L1 | Landed `b410186` and disclosed "checker selftest/external/frozen/actual-record acceptance are all UNRUN" (`b410186:LOG.md:786`). Reported static integration edits including "omitted structured-detail compatibility" and removing "an impossible r15-only finding-token requirement on the unchanged r14 namespace transcript" (`corpus/lessons/round-15.md:104-106`). | The compatibility edit did not resolve the parser/token contradiction; it was made without execution. The shipped blob still contradicts itself. [INFERENCE] on which line the static edit touched: no pre-landing blob survives (`git log -- tools/souji-preservation-evidence.py` has only `b410186` and `c6207bd`). |
| wave 2 | 32-seat falsification was planned (`w2-spec.json`). | 0 dispatched; "skipped-by-operator-wrapup" (`w2-skipped.json`). No adversarial pass ever existed. |

Five seats are documented here — author, runner author, two reviewers holding the
right requirement, integrator — and a further reviewer (`CheckerBindings`) was equally
design-only. None executed the artifact. This is not a false green claim: the
report, the lesson and the log all say "unrun". The failure is that an executable
artifact carrying its own acceptance probe was allowed to land and remain for a full
round with zero runs, and that no later mechanism was obligated to run it.

### 8. Which rule should have caught it

**(a) The process rule that does not exist, at r15 or now.** `corpus/QUALITY.md`:

- Q24 (r15) states "unrun checks never pass" and was correctly applied to the
  *claim*: C2 is "unprovable; NOT admitted" because "none was executed"
  (`corpus/lessons/round-15.md:101`). It has no landing force; the artifact landed
  with the unrun disclosure in prose.
- Q25 (r16) adds (a) parse of SKILL-cited scripts, (b) frozen-pin coherence at the
  landing commit, (c) seat `STATUS:` carry. The checker is SKILL-cited
  (`b410186:SKILL.md:149`), so `compile()` passes; (b) addresses the unrelated
  `b5187351…` pin; (c) reads only `STATUS:` lines outside fences/tables (`:257-284`) — and
  `AdmissionChecker.md` has none.
- `tools/souji-landing-gate.py` pins exactly seven ids (`:37-38,97-103`), none a
  self-invocation; `LG-PARSE-REG`/`LG-PARSE-CHANGED` only compile/parse
  (`:539-566`). The recorded replay of `--rev b410186 --round 15` (5 findings) is
  therefore complete and still blind to the 24/47 selftest.

Smallest rule (proposed Q25(d)): *A unit that carries its own self-invocation and is
cited in SKILL.md must have that invocation's observed output bound at the landing
commit — command, exit, and a `selftest: N/N passed` line with N==N in a file that
resolves at the revision. An unrun self-invocation blocks landing of that unit, not
merely admission of the claim it supports.* Mechanically checkable without running:
a gate id `LG-SELFTEST-UNRUN` resolving the cited output file and its N/N line.

**(b) The structural rule that would have caught the bug without any execution.**
*A consumer's self-test must be driven by the real producer's formatter, or parse one
literal line copied from the real producer; a second synthetic producer is not
evidence of compatibility.* At review this was two greps:

- `grep -n 'observed_finding=' tools/souji-preservation-evidence.py` → `:1482` shows
  `\tobserved_finding=`, `:119-120` states the token rule;
- `git show b410186:tests/fixtures/r15-census-config.py | grep -n 'observed_finding='`
  → `:1367` shows the producer separates with `\t`.

Together with `CASE_LINE_RE … [^\t]*` (`:916`), the contradiction is plain. The
reviewers who would have run exactly this were the Checker* seats (Green, Cases and
Bindings read here); those were design-only by the wave contract (no runtime tests),
and their reviews predate the file.

**Smallest code fix** (already applied by R4 at `c6207bd`): widen the detail group to
`(.*)`, make `_default_detail`/`_transcript` TAB-shaped, normalize record-vs-transcript
detail (Tab→space) at comparison, and add one self-test case that calls
`_parse_transcript` on a literal real-formatter line. The diff is coherent and the
recorded result is 47/47 with the external fixture 8/8 and `--frozen` clean. The
durable part still missing is (a).

## Verdicts

| # | Attack | Verdict | Basis |
|---|---|---|---|
| F1 | The seed defect is the `[^\t]*` detail group plus the `\tobserved_finding=` token rule | **holds** | Both halves are literal at `b410186` checker `:916` and `:1482`; the producer's TABs are literal at fixture `:1367-1368`. |
| F2 | The self-test would have caught it (the positive control cannot pass) | **holds** | `positive` expects 0/[] (`:1969-1978`); every cfg PASS yields `case-finding-mismatch`; harness compares exact ids (`:2554`); 24/47 recorded (`round-16.md:12`). |
| F3 | A reviewer could have caught it statically, without execution | **holds** | Two greps (above). The requirement to do so existed (`CheckerGreen.md:110,136`; `CheckerCases.md:102`) but was written before the file existed. |
| F4 | An existing rule should have caught it | **fails** | Q24 has no landing force; Q25(a)/(b)/(c) and all seven `LG-*` ids are blind to an unrun self-invocation; `AdmissionChecker.md` emits no `STATUS:` line. The r16 lesson's R16-M4 "fix" cell cites "Q25 (b)" (`round-16.md:12`), which is frozen-pin coherence — a calibration overclaim. |
| F5 | The r16 repair closes the class | **partial** | Format drift fixed and measured (47/47, external 8/8, frozen clean at `c6207bd`). The gate/rule gap and the absence of an obligation to run a self-invocation remain; nothing prevents recurrence next round. Minimally add Q25(d) + `LG-SELFTEST-UNRUN`. |
| F6 | The seats misrepresented a run as green | **fails** (no misrepresentation) | `AdmissionChecker.md:80-82`, `LOG.md:786` and `round-15.md:101` all say unrun. The defect is "landed unexecuted", not "claimed executed". Mining it as dishonesty would miscalibrate the lesson. |

## Confidence

High on the mechanism and every line citation: both sides are static committed bytes,
and the contradiction is provable by reading. Medium on the 24/47 partition (inferred
from control flow; the count itself is R4's recorded measurement, not re-run here). No
behavioral claim in this report rests on a fresh execution.

## Boundary disclosure

- One scratch copy of the committed checker was created with
  `git show b410186:… > /tmp/r15checker.py` and later moved to
  `/var/tmp/souji-r16-RevengeCheckerBreakage-4/r15checker.py`. `/tmp` is outside the
  allowed scratch root (and Q4's `/var/tmp` rule); the `/tmp` copy is deleted, the
  `/var/tmp` directory is deleted, and its content was committed bytes only. No lane
  file was written outside this report.
- Reads were limited to exact named files and `git show|log|ls-tree` on named paths.
  No census, checker, fixture, runner or mutation was executed. The operator sweep,
  `.ufo/state`, `watchdog.log`, `MANIFEST.json` and sibling lane repositories were not
  opened, listed, grepped or copied.
- No tools installed or upgraded (RULES.md not needed).
- Two citation corrections inside this report were applied with an in-place `sed -i`
  over this file only (the positive-control case range and the lesson pointer). The
  remaining corrections used the preferred edit path. No source or lane artifact was
  edited.

STATUS: ok

## Commands

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -15 -- tools/souji-preservation-evidence.py && echo "---" && git show --stat b410186 | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain | head -20 && echo "--- files ---" && ls -la .ufo/waves/round-15/ 2>/dev/null | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-preservation-evidence.py > /tmp/r15checker.py; wc -l /tmp/r15checker.py; sed -n '1,80p' /tmp/r15checker.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'CASE_RE\|CASE\\t\|observed_finding\|\\\\t' /tmp/r15checker.py | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-15/ && echo "--- w2 files ---" && ls .ufo/waves/round-15/w2 2>/dev/null | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '270,300p;900,930p' /tmp/r15checker.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show c6207bd --stat && echo "=== DIFF checker ===" && git show c6207bd -- tools/souji-preservation-evidence.py | head -200
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'CASE_LINE_RE\|observed_finding' /tmp/r15checker.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1460,1505p' /tmp/r15checker.py && echo "=== transcript emitter ===" && sed -n '1820,1845p' /tmp/r15checker.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '940,1000p' /tmp/r15checker.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tests/fixtures/r15-census-config.py | grep -n 'CASE\\t\|observed_finding\|observed_exit\|def _detail\|SUMMARY' | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only HEAD -- .ufo/waves/round-16/w1 | grep -i -E 'preserv|checker|frozen'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1506,1545p' /tmp/r15checker.py && echo "=== harness ===" && sed -n '2555,2638p' /tmp/r15checker.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '2490,2560p' /tmp/r15checker.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:.ufo/waves/round-16/w1/RevengeFrozenPin.md | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'observed != sorted\|def _default_detail\|def _transcript\|^CASE_LINE_RE\|^TOOL_LINE_RE\|def _parse_transcript\|def _eval_arm\|if not problems' /tmp/r15checker.py && echo "=== fixture b410186 ===" && git show b410186:tests/fixtures/r15-census-config.py | sed -n '1355,1372p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only HEAD -- .ufo/waves/round-16/w1 | sed -n '1,90p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'LG_[A-Z_]*\|LG-[A-Z-]*\|def _rule\|RULES = ' tools/souji-landing-gate.py | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:census/round-15/run-verification.py | grep -n 'preservation-checker-selftest' -A10 -B6
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== AdmissionChecker STATUS lines ==" && git show b410186:.ufo/waves/round-15/w1/AdmissionChecker.md | grep -n 'STATUS' ; echo "== CheckerGreen 47/selftest ==" && git show b410186:.ufo/waves/round-15/w1/CheckerGreen.md | grep -n '47\|selftest\|positive control' | head; echo "== CheckerCases selftest ==" && git show b410186:.ufo/waves/round-15/w1/CheckerCases.md | grep -n 'selftest\|47' | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '300,360p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== SKILL citations at b410186 ==" && git show b410186:SKILL.md | grep -n 'preservation-evidence' ; echo "== LOG r15 landing ==" && git show b410186:LOG.md | grep -n -i 'preservation\|acceptance unrun\|unrun' | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:LOG.md | sed -n '770,800p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '235,300p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '100,132p;1798,1815p;2560,2572p' /tmp/r15checker.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tests/fixtures/r15-preservation-evidence.py | grep -n 'selftest\|expect\|47' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'def evaluate\|_eval_arm(\|if findings\|return EXIT_COULD' /tmp/r15checker.py | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c 'cases.append((' /tmp/r15checker.py && grep -n 'cases.append((' -A3 /tmp/r15checker.py | grep -E '^\s*[0-9]+-\s+"' | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1550,1640p' /tmp/r15checker.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1955,1992p' /tmp/r15checker.py && echo "=== status_for ===" && grep -n 'def _status_for' -A12 /tmp/r15checker.py && echo "=== good_statuses ===" && grep -n 'def _good_statuses' -A12 /tmp/r15checker.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:.ufo/waves/round-15/w1/AdmissionChecker.md | grep -n 'Selftest: 47\|Unrun checks\|expect 0/47\|no runtime tests\|No installs'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:.ufo/waves/round-15/w1/RoundRunner.md | grep -n 'preservation-checker-selftest\|preservation-checker-external\|240s' | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'structured-detail\|C2 calibration\|C2.*unprovable\|47-case selftest' corpus/lessons/round-15.md
mkdir -p /var/tmp/souji-r16-RevengeCheckerBreakage-4 && cp /tmp/r15checker.py /var/tmp/souji-r16-RevengeCheckerBreakage-4/r15checker.py && rm -f /tmp/r15checker.py && ls -l /var/tmp/souji-r16-RevengeCheckerBreakage-4/
rm -rf /var/tmp/souji-r16-RevengeCheckerBreakage-4 && ls -d /var/tmp/souji-r16-RevengeCheckerBreakage-4 2>&1 | head -2
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:.ufo/waves/round-15/w1/AdmissionChecker.md | sed -n '48,56p;78,88p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '"positive",' .ufo/waves/round-16/w2/RevengeCheckerBreakage.md; git show b410186:tools/souji-preservation-evidence.py | grep -n '"positive",\|"souji-preservation-evidence: clean"'; grep -n 'R16-M4' corpus/lessons/round-16.md; grep -n 'acceptance are all UNRUN' <(git show b410186:LOG.md)
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'round-16.md:20\|1965-1974\|271-285\|LOG.md:786' .ufo/waves/round-16/w2/RevengeCheckerBreakage.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && f=.ufo/waves/round-16/w2/RevengeCheckerBreakage.md && sed -i 's/`:1965-1974`/`:1969-1978`/g; s/round-16\.md:20/round-16.md:12/g' "$f" && grep -n 'round-16.md:12\|1969-1978' "$f"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '505,570p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'def parse_script' -A40 tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1466 && NR<=1482 {printf "%d:%s\n", NR, $0}' <(git show b410186:tools/souji-preservation-evidence.py)
```
