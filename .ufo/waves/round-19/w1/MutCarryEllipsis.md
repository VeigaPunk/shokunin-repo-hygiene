STATUS: DONE — M1 was killed by TC1 on a private reconstruction: the pristine and restored predicate rejected the unmarked cut; M1 accepted it and failed the unchanged detector. Exact bytes were restored before scratch cleanup; no lane gate ran.

# Findings

- Seat: `SoujiR19.MutCarryEllipsis-2`; item `MutCarryEllipsis`; axis **calibration**, C1 only. Probe date: 2026-10-21.
- **Mutant M1:** in the reconstructed `carries` function, replace `if ELLIPSIS_RE.match(entry, m.end()):` with `if m:`. A `re.finditer` match object is truthy, so this single-predicate defect accepts any occurrence of a source-line-boundary prefix without requiring an ellipsis. The complete-paragraph branch and all detector bytes remained unchanged.
- **Expected detector:** TC1 `wrap-unmarked` must be rejected: `carried == false`, synthetic finding `LG-SEAT-UNCARRIED`, synthetic gate exit 1. The detector itself exits 0 when that rejection is observed, and 1 if the truncation is accepted.
- **Observed:** pristine detector PASS/exit 0; M1 detector FAIL/exit 1; restored detector PASS/exit 0. Under M1, TC1 **no longer fails the carry rule**: its synthetic gate exit becomes 0 and the finding disappears. Therefore **KILLED**, not survived or inconclusive.
- This is a bounded, single-stimulus **predicate-level reconstruction**, not execution of the installed gate or its fixture/selftest. The source paragraph is selected directly from TC1's known lines, and its lesson bullet already has an `open` carry token. Paragraph discovery, carry-token parsing, joining, replay gating, counters and integrated gate diagnostics were not exercised or claimed.

# Evidence

## Source and reconstruction boundary

Read the worktree bytes of `.ufo/waves/round-18/w1/ScoutCarryWrap.md`, not the installed round-19 gate:

- `:15` specifies the supporting normalizer: NFC, remove `*` and backticks, collapse whitespace and strip.
- `:40-43` defines the strict-round constant and ellipsis expression; `:74-83` defines the exact carry predicate reconstructed here.
- `:86-92` specifies whole-paragraph or boundary-ellipsis matching and the unmarked-cut finding.
- `:120-143` supplies the exact two-line report and unmarked lesson bullet used by TC1.
- `.ufo/waves/round-19/preregistration.txt:18-22` identifies the C1 boundary this mutation challenges. Integrated worktree claims were not accepted as verification.

The private reconstruction at `/var/tmp/souji-r19-MutCarryEllipsis/carry_rule.py` was exactly the following before mutation and after restoration. Its `carries` body and `ELLIPSIS_RE` reproduce the proposal; `norm_line` implements the report's stated supporting normalization.

```python
import re
import unicodedata

# Reconstruction from ScoutCarryWrap.md:15 and :74-83; never imports the lane gate.
ELLIPSIS_RE = re.compile(r'\s*["”]?\s*(?:…|\.\.\.)')


def norm_line(text):
    text = unicodedata.normalize("NFC", text)
    return " ".join(text.replace("*", "").replace("`", "").split())


def carries(block, entry):
    full = norm_line(" ".join(block))
    if full and full in entry:                 # (a) complete paragraph
        return True
    for k in range(1, len(block)):             # (b) cut at a source line end
        prefix = norm_line(" ".join(block[:k]))
        for m in re.finditer(re.escape(prefix), entry):
            if ELLIPSIS_RE.match(entry, m.end()):
                return True
    return False
```

The sole mutation was private `carry_rule.py:20`: `if ELLIPSIS_RE.match(entry, m.end()):` → `if m:`. That line was restored immediately after the mutant detector returned exit 1.

## Unchanged bounded detector

`/var/tmp/souji-r19-MutCarryEllipsis/tc1_detector.py` contained exactly:

```python
import hashlib
import json
from pathlib import Path
import sys

# A single synthetic TC1 stimulus from ScoutCarryWrap.md:120-143.
# This tests only the reconstructed carry predicate, not the lane gate.
rule_path = Path(__file__).with_name("carry_rule.py")
rule_bytes = rule_path.read_bytes()
namespace = {"__name__": "private_carry_rule"}
exec(compile(rule_bytes, str(rule_path), "exec"), namespace)
report = (
    "# SeatWrap\n\n"
    "STATUS: PARTIAL — guarded repos measured and the\n"
    "remaining arm never runs under a bound.\n"
)
lesson = (
    "# Round 18\n\n## Seat-reported failures\n\n"
    "- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "
    "\"STATUS: PARTIAL — guarded repos measured and the\" — open\n"
)
block = report.splitlines()[2:4]
entry = namespace["norm_line"](lesson.splitlines()[4])
carried = namespace["carries"](block, entry)
findings = [] if carried else ["LG-SEAT-UNCARRIED"]
synthetic_gate_exit = 0 if carried else 1
ok = carried is False and findings == ["LG-SEAT-UNCARRIED"] and synthetic_gate_exit == 1
print(json.dumps({
    "case": "TC1 wrap-unmarked",
    "round_no": 18,
    "rule_sha256": hashlib.sha256(rule_bytes).hexdigest(),
    "report": report,
    "lesson": lesson,
    "block": block,
    "normalized_entry": entry,
    "carried": carried,
    "synthetic_findings": findings,
    "synthetic_gate_exit": synthetic_gate_exit,
    "detector": "PASS" if ok else "FAIL",
}, ensure_ascii=False, sort_keys=True))
sys.exit(0 if ok else 1)
```

The synthetic finding and synthetic exit are detector projections of the observed boolean, not outputs attributed to an unrun gate. The executable assertion is that the reconstructed predicate returns `False` on TC1.

## Exact stimulus outputs

Each invocation used the same command, `python3 -B tc1_detector.py`, in the private scratch directory. No detector edits occurred between invocations.

### Pristine — detector exit 0

```json
{"block": ["STATUS: PARTIAL — guarded repos measured and the", "remaining arm never runs under a bound."], "carried": false, "case": "TC1 wrap-unmarked", "detector": "PASS", "lesson": "# Round 18\n\n## Seat-reported failures\n\n- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` \"STATUS: PARTIAL — guarded repos measured and the\" — open\n", "normalized_entry": "- SeatWrap .ufo/waves/round-18/w1/SeatWrap.md:3 \"STATUS: PARTIAL — guarded repos measured and the\" — open", "report": "# SeatWrap\n\nSTATUS: PARTIAL — guarded repos measured and the\nremaining arm never runs under a bound.\n", "round_no": 18, "rule_sha256": "342085992da876a75418ca00471d4e70d0c13adc14a3ac475f5280a42c973674", "synthetic_findings": ["LG-SEAT-UNCARRIED"], "synthetic_gate_exit": 1}
```

### M1 — detector exit 1

```json
{"block": ["STATUS: PARTIAL — guarded repos measured and the", "remaining arm never runs under a bound."], "carried": true, "case": "TC1 wrap-unmarked", "detector": "FAIL", "lesson": "# Round 18\n\n## Seat-reported failures\n\n- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` \"STATUS: PARTIAL — guarded repos measured and the\" — open\n", "normalized_entry": "- SeatWrap .ufo/waves/round-18/w1/SeatWrap.md:3 \"STATUS: PARTIAL — guarded repos measured and the\" — open", "report": "# SeatWrap\n\nSTATUS: PARTIAL — guarded repos measured and the\nremaining arm never runs under a bound.\n", "round_no": 18, "rule_sha256": "37f8206366189f7ab67904d13c85f9634262b54387feab5c5418a6544ba08f6c", "synthetic_findings": [], "synthetic_gate_exit": 0}
```

The command runner additionally reported `Command exited with code 1`.

### Restored — detector exit 0

```json
{"block": ["STATUS: PARTIAL — guarded repos measured and the", "remaining arm never runs under a bound."], "carried": false, "case": "TC1 wrap-unmarked", "detector": "PASS", "lesson": "# Round 18\n\n## Seat-reported failures\n\n- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` \"STATUS: PARTIAL — guarded repos measured and the\" — open\n", "normalized_entry": "- SeatWrap .ufo/waves/round-18/w1/SeatWrap.md:3 \"STATUS: PARTIAL — guarded repos measured and the\" — open", "report": "# SeatWrap\n\nSTATUS: PARTIAL — guarded repos measured and the\nremaining arm never runs under a bound.\n", "round_no": 18, "rule_sha256": "342085992da876a75418ca00471d4e70d0c13adc14a3ac475f5280a42c973674", "synthetic_findings": ["LG-SEAT-UNCARRIED"], "synthetic_gate_exit": 1}
```

## Hashes and restoration

SHA-256 values were obtained with `sha256sum` immediately before each behavioral run:

| Bytes | Pristine | M1 | Restored |
|---|---|---|---|
| Private `carry_rule.py` | `342085992da876a75418ca00471d4e70d0c13adc14a3ac475f5280a42c973674` | `37f8206366189f7ab67904d13c85f9634262b54387feab5c5418a6544ba08f6c` | `342085992da876a75418ca00471d4e70d0c13adc14a3ac475f5280a42c973674` |
| Private `tc1_detector.py` | `edc7c6f6f01d9cdca3bb5b9a10e74da00e5c4fe424ca4f6462914e6127cf8c20` | `edc7c6f6f01d9cdca3bb5b9a10e74da00e5c4fe424ca4f6462914e6127cf8c20` | `edc7c6f6f01d9cdca3bb5b9a10e74da00e5c4fe424ca4f6462914e6127cf8c20` |

The source report's hash before and after the probe was identical: `9d1e95b3f51109eb4be7c159ff90d7c59a3c8f92e06509583197246c952316b8` for `.ufo/waves/round-18/w1/ScoutCarryWrap.md`. The exact restored rule hash and restored PASS establish restoration before cleanup. Both private files and the otherwise-empty private directory were then removed successfully.

# Commands run

File reads used `read`/`grep` for the assigned proposal, preregistration and its prerequisite sections, agent rules, applicable skills/protocol, the private mutation anchor, and untruncated captured output. New private files and this report used `write`; mutation and restoration used `edit`. No git or jj commands ran.

The three behavioral invocations below all ran with cwd `/var/tmp/souji-r19-MutCarryEllipsis`; the only executed probe was the synthetic detector and its private rule. Runtime output: `Python 3.14.8`.

1. Pristine:
   ```sh
   python3 --version && sha256sum -- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-18/w1/ScoutCarryWrap.md carry_rule.py tc1_detector.py && python3 -B tc1_detector.py
   ```
2. After applying M1:
   ```sh
   sha256sum -- carry_rule.py tc1_detector.py && python3 -B tc1_detector.py
   ```
3. After restoring the original predicate:
   ```sh
   sha256sum -- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-18/w1/ScoutCarryWrap.md carry_rule.py tc1_detector.py && python3 -B tc1_detector.py
   ```
4. Cleanup, cwd `/var/tmp`:
   ```sh
   rm -- /var/tmp/souji-r19-MutCarryEllipsis/carry_rule.py /var/tmp/souji-r19-MutCarryEllipsis/tc1_detector.py && rmdir -- /var/tmp/souji-r19-MutCarryEllipsis && printf 'CLEANUP: removed both private probe files and the private scratch directory\n'
   ```
   Exact output: `CLEANUP: removed both private probe files and the private scratch directory`.

# Contract compliance

- Only the assigned lane report was written in the lane. All probe creation, mutation and restoration occurred under `/var/tmp/souji-r19-MutCarryEllipsis/`, which has been removed. No sibling source was touched and no extra artifact was delivered.
- No installed lane gate, selftest, fixture, census, proc census, verification runner or fleet-reading probe ran. No live process data was read; no process was signalled. No `/proc/*/environ`, secrets, driver state, watchdog log, operator-sweep tree, fleet ledger or fleet repository was opened or changed.
- No subagents, peer messages, other runtime, network access, git/jj mutations, tool installs/updates or pacman transaction occurred. Tool installs/updates: **none**.
- The verdict concerns this one mutation and this one synthetic TC1 detector only. It is not a round admission, integration, shipment or claim that installed-gate acceptance checks passed.
