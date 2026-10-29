#!/usr/bin/env python3
"""Generate .ufo/waves/round-42/w2/R42w2mutationtester07.md from the recorded receipts (no re-measurement)."""
import json
import os
import re

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester07"
OUT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester07.md"
LANDED = "tools/souji-freeze-check.py"
CONTROL = "census/round-42/controls/c2-stub-tool.py"
BL = ("cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red "
      "retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb")
BC = ("cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok retro=red "
      "retro_clean=ok selftest=ok patches=0/3 tool_sha=6e1c564a94b5")
FIELDS = ["cases", "pass", "fail", "control_clean", "control_findings", "real", "retro",
          "retro_clean", "selftest", "patches", "tool_sha"]

man, res = {}, []
for t in ("results.json", "results-g.json", "results-h.json"):
    R = json.load(open(os.path.join(SEAT, "receipts", t)))
    for m in R["manifest"]:
        man[m["id"]] = m
    res += R["results"]
by = {}
for r in res:
    by.setdefault(r["id"], {})[r["tool"]] = r


def fields(s):
    return dict(re.findall(r"(\w+)=([^\s]+)", s or ""))


def diff(s, base):
    if s is None:
        return "NO SUMMARY"
    f, b = fields(s), fields(base)
    out = ["%s=%s" % (k, f[k]) for k in FIELDS if k in f and f[k] != b.get(k)]
    return "unchanged" if not out else " ".join(out)


# Per-mutant verdict notes (hand-classified from the receipts).
NOTE = {
 "A08": "VACUITY on the r41 tool: control SUMMARY reads cases=37 pass=37 (case set no longer checked); exit stays 1 only because the patches leg still reads 0/3",
 "C08": "VACUITY on the r41 tool: control SUMMARY reads patches=3/3 (an always-green selftest is credited with three patches); exit stays 1 only because pass=24",
 "G13": "SUMMARY-only: tool_sha field changes, met() ignores it, so the provenance field is unpinned; verdict unchanged",
 "C04": "SURVIVOR, equivalent under the exit rule (exit 0 already implies findings=0)",
 "E06": "SURVIVOR, equivalent on this host: no sitecustomize is injected when no patch id is set; the default branch is unreached",
 "G02": "SURVIVOR, equivalent: the +1 count is used only on the PRISTINE FAIL path, unreached while the tool is present",
 "G07": "SURVIVOR, equivalent: fixture heading text only; `## C1 claim 1` is still a valid claim heading to the grammar",
 "G09": "SURVIVOR, equivalent: redundant with the class-multiset comparison in case_ok",
 "G11": "SURVIVOR, equivalent under the table: dup-base-differs still duplicates Base with a differing value; same expected class",
 "G15": "SURVIVOR, equivalent on this host: no case stderr differs between the two crash strings",
 "H07": "SURVIVOR, equivalent by construction: len(results) is always len(CASES)+2",
 "C01": "SURVIVOR, blind spot: real leg no longer requires claims=3; a tool under-counting claims on the real prereg passes",
 "C02": "SURVIVOR, blind spot: retro leg accepts one finding where the leg requires >=3 of the 19 pre-grammar findings",
 "C05": "SURVIVOR, blind spot: self-test floor of 1 case instead of 12; a 5-case self-test passes",
 "C06": "SURVIVOR, blind spot: a self-test that prints pass != cases with fail=0 passes",
 "C09": "SURVIVOR alone, blind spot: the clean-stub REJECTED requirement is only observable when a stub is accepted (see W1/W2)",
 "C10": "SURVIVOR alone, blind spot: patches==3 is observable only in combination with A08 (S3, V3)",
 "D01": "SURVIVOR, blind spot: the stub's claims= count is never compared by case_ok",
 "D02": "SURVIVOR, blind spot: the stub's finding class is never compared; a stub only has to fail",
 "D03": "SURVIVOR alone, blind spot: the stub gate `sp <= sn` is invisible while both stubs fail cases; it flips the landed exit only with A08 and both refusal rows forced (probe W2)",
 "F02": "SURVIVOR, blind spot: SUMMARY regex unanchored; a second SUMMARY line is not seen",
 "F03": "SURVIVOR, blind spot: refusal row without the no-crash requirement",
 "F04": "SURVIVOR, blind spot: refusal row without the no-crash requirement",
 "G10": "SURVIVOR, blind spot: multiset compared as set; no case expects a duplicated identical finding",
 "G14": "SURVIVOR alone, blind spot: the 37-case pin is only in met(); with G01 it gives a green landed tool (S4)",
 "H01": "SURVIVOR, blind spot: unresolved-rev refusal forced true; the landed tool refuses, so a non-refusing tool passes this row",
 "H02": "SURVIVOR, blind spot: 1 s run_tool timeout never reached on this host; run_tool has no timeout handler",
 "H03": "SURVIVOR, blind spot on a healthy host: failed git no longer raises; no fixture fails",
 "H04": "SURVIVOR, blind spot on a healthy host: fixture-root assertion never fires",
 "H06": "SURVIVOR, blind spot: crash check dropped from case_ok; no case crashes at BASE",
 "H08": "SURVIVOR alone, blind spot: control_findings REJECTED requirement only observable with an accepted stub",
 "B06": "CRASH: no-op rewrite makes git commit fail in the fixture builder; no SUMMARY, exit 1 on both artifacts (a false red)",
 "F01": "CRASH: IndexError in run_tool (group 2 removed); no SUMMARY, exit 1 on both artifacts (a false red)",
 "G12": "CRASH: git identity removed; fixture commit fails; no SUMMARY, exit 1 on both artifacts (a false red)",
 "H05": "CRASH: only census/ staged, prereg.txt is not committed; fixture commit fails; no SUMMARY, exit 1 on both artifacts (a false red)",
 "G01": "CAUGHT: landed reads cases=36; met() requires n==37 and the tool is red",
 "S1": "WRONG GREEN on the r41 tool: control rc=0 with cases=37 pass=37 patches=3/3",
 "S2": "WRONG GREEN on the r41 tool: control rc=0 with cases=37 pass=37 patches=3/3",
 "S3": "WRONG GREEN on the r41 tool: control rc=0 with cases=37 pass=37 patches=0/3 (patches not required)",
 "S4": "WRONG GREEN on the landed tool: rc=0 with cases=36 pass=36 (the 37 pin is not in the gate)",
}


def verdict(mid):
    L, C = by[mid][LANDED], by[mid][CONTROL]
    if mid in NOTE:
        return NOTE[mid]
    if L["summary"] is None or C["summary"] is None:
        return "CRASH (no SUMMARY)"
    if L["rc"] == 1:
        return "CAUGHT: false red on the landed tool"
    if C["rc"] == 0:
        return "WRONG GREEN on the r41 tool"
    return "unchanged"


singles = sorted([i for i in man if not i.startswith("S")], key=lambda k: (k[0], int(k[1:])))
stacks = sorted([i for i in man if i.startswith("S")])
region = lambda i: man[i]["region"]
desc = lambda i: man[i]["desc"]

nochange = [i for i in singles if diff(by[i][LANDED]["summary"], BL) == "unchanged"
             and diff(by[i][CONTROL]["summary"], BC) == "unchanged"]
vacu_ctrl = [i for i in man if fields(by[i][CONTROL]["summary"]).get("cases") == "37"
             and fields(by[i][CONTROL]["summary"]).get("pass") == "37"]
false_red = sum(1 for i in singles if by[i][LANDED]["rc"] == 1)
ctrl_green_single = [i for i in singles if by[i][CONTROL]["rc"] == 0]

rows = []
for i in singles + stacks:
    L, C = by[i][LANDED], by[i][CONTROL]
    rows.append("| `%s` | %s | %s | `%s` / `%s` | %s |" % (
        i, region(i).replace("|", "/"), desc(i).replace("|", "/"),
        diff(L["summary"], BL) + " (rc=%s)" % L["rc"],
        diff(C["summary"], BC) + " (rc=%s)" % C["rc"],
        verdict(i)))

head = """# R42w2mutationtester07 — mutation test of the r42 C2 counter (`census/round-42/c2-counter.py`)

Seat: R42w2mutationtester07 (role mutation-tester, wave 2, falsify). Judged on operability. Leaf seat; no subagent dispatch.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Tip under attack: `3105a63b23481fccf7df58e74d14a6681e0ea0c8`.
Frozen counter: `census/round-42/c2-counter.py` sha256 `fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1` (the preregistration pin; unchanged at the end of this seat).
Landed tool: `tools/souji-freeze-check.py` at the tip, `tool_sha=9ddd596b98fb` (first 12 hex of its sha256).
Control: `census/round-42/controls/c2-stub-tool.py` (the r41 tool plus an always-green `--selftest`; `tool_sha=6e1c564a94b5`).

## Verdict

**Falsified at the counter level.** The landed tool was not mutated; every finding below is about the frozen counter that scores it.

- Of 60 single-point counter mutants, 28 change no SUMMARY field for either artifact. Of those 28, 8 are behaviour-identical to the frozen counter and 20 are blind spots.
- Two single-point mutants (`A08`, `C08`) and three stacks (`S1`–`S3`) read the r41 control as `cases=37 pass=37` or `patches=3/3`, the vacuity pattern the brief names.
  `S1`–`S3` also flip the control's exit to 0, so the counter reports the r41 tool target-met.
- The built-in stub gate (`stubs[label] = "REJECTED" if sp < sn`) is carried by the case table and the refusal rows. With `A08` (case expectations unchecked) and both refusal
  rows forced true, both stubs score 37/37 and the counter prints `control_clean=ACCEPTED` (W1, exit 1). Flipping the one comparison to `sp <= sn` (`D03`, W2) prints
  `control_clean=REJECTED` for two stubs that pass every row, and exits 0 on the landed tool.
- `G14` moves the 37-case pin into `met()` alone; `G14`+`G01` (`S4`) is a green landed tool with 36 cases.
- The frozen counter is not edited (preregistration rule 1); these are named limits for the L1.

## What was tested

- The frozen counter was read, and each mutant written as a unique-anchor replacement of it (anchor count checked to be exactly 1 before writing) under `mutants/<id>.py`.
  The mutants cover the CASES expectation table (A), the `build()` fixture helpers (B), the five legs and the verdict gate (C), the built-in stubs (D), the `SITECUSTOMIZE`
  text and patch injection (E), and `run_tool`, the refusal checks and the harness (F, G, H). `mutants/` holds 65 counter files (BASE, 60 singles, 4 stacks) plus 5 probe files (V1–V3, W1, W2).
- Four stacks (`S1`–`S4`) combine two or three singles and are reported apart from the single-point count. Probes `V1`–`V3`, `W1`, `W2` are reported in the findings.
- Each mutant (and the pristine BASE, through the same harness) was run as `python3 -B mutants/<id>.py --root <clone at 3105a63…> --rev 3105a63… --tool <artifact> --scratch <dir>`
  against both artifacts: the landed tool `tools/souji-freeze-check.py` and the control `census/round-42/controls/c2-stub-tool.py`.
- Each SUMMARY is compared verbatim to the pristine SUMMARY for that artifact, `tool_sha` included. A change of any field is a change.
- For every mutant that changes no SUMMARY field, the per-case FAIL set was also compared with pristine; all 28 match.

## Pristine baseline (the same harness)

```
landed  (rc=0): SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb
control (rc=1): SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=0/3 tool_sha=6e1c564a94b5
```

The landed line matches the tool digest recorded in `census/round-42/records/c2-after.txt` (`tool_sha=9ddd596b98fb`). The control line matches control B in
`census/round-42/controls/c2-control.txt` (`pass=24 … patches=0/3`, `tool_sha=6e1c564a94b5`). The 13 control failures are the 13 cases the r41 tool cannot pass.

## Table — counter mutants

Columns: mutant | region | change | SUMMARY diff vs pristine for landed / control (exit code in parentheses) | verdict.
`unchanged` means the SUMMARY line is byte-identical to the pristine one. Full SUMMARY lines per mutant are in `receipts/<id>.landed.txt` and `receipts/<id>.control.txt`
(stacks `S1`–`S4` in `receipts/S*.txt`; the W and V probes in `receipts/W*.landed.txt`, `receipts/V*_*.txt`).

| mutant | region | change | landed / control SUMMARY diff | verdict |
|---|---|---|---|---|
"""

body = "\n".join(rows)

counts = """

## Counts

- Single-point mutants: %d (A 8, B 6, C 10, D 3, E 6, F 4, G 15, H 8). Stacks: %d.
- Mutants that change no SUMMARY field for either artifact (single-point): %d — `%s`.
  Of these, 8 are equivalent to the frozen counter and 20 are blind spots (see the verdict column).
- Single-point mutants that flip the landed tool red: %d. Of these, four crash the harness with no SUMMARY (`B06`, `F01`, `G12`, `H05`).
- Single-point mutants that flip the control to exit 0: %d.
- Mutants whose control SUMMARY reads `cases=37 pass=37` (the vacuity criterion as stated): %s.
""" % (
    len(singles), len(stacks), len(nochange), "`, `".join(nochange),
    false_red, len(ctrl_green_single),
    ", ".join("`%s`" % i for i in sorted(vacu_ctrl)),
)

findings = """

## Findings

### F1 — vacuity: the case set is not what the stub gate measures (A08, C08, S1–S3)

- **Attacks:** the stub-rejection gate (`stubs[label] = "REJECTED" if sp < sn`) and the `case_ok` expectation check.
- **A08** (`case_ok` keeps only `not crash and summ is not None`): the control reads `cases=37 pass=37 fail=0 … patches=0/3`. The verdict stays red only because the patches
  leg reads 0/3. Receipt `receipts/A08.control.txt`. This is the brief's example: a counter that reads `cases=37 pass=37` on the r41 tool.
- **S2** (`A08`+`C08`): control `cases=37 pass=37 … patches=3/3`, exit **0** on the r41 tool; the counter declares the r41 tool target-met. `S1` (`A08`+`C08`+`C10`) and
  `S3` (`A08`+`C10`) also give control exit 0. Receipts `receipts/S1.control.txt`, `S2.control.txt`, `S3.control.txt`.
- **C08** (any non-timeout patch exit counts as detected): the control reads `patches=3/3` with `pass=24`, exit 1. The always-green selftest is credited with three patches.
  Receipt `receipts/C08.control.txt`.
- **Stub gate under A08.** Probe `scripts/probe_stub.py` (receipt `receipts/stub-probe.txt`): at BASE the stubs score sp=4/37 (`control_clean`) and sp=0/37
  (`control_findings`). Under A08 they score sp=35/37 each; the two failing rows are the refusal rows. The stub's REJECTED label is carried by the refusal rows, not by the case table.
- **Probe W1/W2** (`scripts/probe_d03.py`; receipts `receipts/W1.landed.txt`, `W2.landed.txt`). Both are A08 with both refusal rows forced true, so both stubs score 37/37.
  W1 keeps the frozen stub rule `sp < sn`: `control_clean=ACCEPTED control_findings=ACCEPTED`, exit 1. W2 adds `D03` (`sp <= sn`): `control_clean=REJECTED control_findings=REJECTED`,
  exit **0** on the landed tool. A stub that passes every row is labelled REJECTED. W2 is four edits (A08, two refusal rows, D03): a stacked finding. Within it, A08 is visible
  in the control SUMMARY, the two refusal rows (`H01`, `F04`) and `D03` are single-point survivors.
- **Probe V3** (`A08`+`H01`+`F04`, `scripts/probe_vacuity.py`): control `cases=37 pass=37`, exit 1 (patches still 0/3). `V1` is `A08` again and `V2` is `S2`; their receipts are `receipts/V*_*.txt`.

### F2 — the case-count pin lives only in met() (G14, S4)

- `G01` (one case deleted) is caught by `n == 37` in `met()`. `G14` (`n >= 30`) alone survives, since n is always 37. `S4` (`G01`+`G14`) gives the landed tool
  `cases=36 pass=36` and exit **0**. The pin is not in `case_ok` or the table, so loosening the gate makes a dropped case green. Receipts `receipts/S4.landed.txt`, `G01.landed.txt`.

### F3 — tool_sha is outside the verdict (G13)

- `G13` (tool digest printed as `000000000000`) changes the SUMMARY on both artifacts and leaves the verdict unchanged. `tool_sha` is the only provenance field in the
  SUMMARY and `met()` does not read it, so a SUMMARY can name the wrong tool bytes and still meet the target. Receipts `receipts/G13.*.txt`.

### F4 — survivors: defects the case table does not detect

The 28 no-change mutants split into 8 equivalents (`C04`, `E06`, `G02`, `G07`, `G09`, `G11`, `G15`, `H07`) and 20 blind spots. The ones that matter for the wave:

- `H01`, `F03`, `F04`: refusal rows never observed failing; a tool that stops refusing an unresolved revision or an absent prereg is not distinguished from the landed one.
- `H02`: no case runs long enough to reach a 1-second timeout on this host; `run_tool` has no timeout handler, so a hung child is covered by no row.
- `C01`, `C02`, `C05`: the real, retro and selftest floors are one-sided; a tool that under-reports claims, under-finds on the pre-grammar prereg, or self-tests 5 cases passes.
- `G10`: the multiset is compared as a set; no case expects a duplicated identical finding, so a tool that double-reports a class is not seen.
- `D01`, `D02`: the stubs' claim count and finding class are never compared; a stub only has to fail, so its SUMMARY text is outside the stub gate.
- `H06`: the crash check is dropped from `case_ok`; no case crashes at BASE, so a crashing child with a matching exit code is not separated from a clean one.

### F5 — crashes read as red on both artifacts (B06, F01, G12, H05)

Four harness mutants crash `score_tool` (no SUMMARY, exit 1 on both artifacts). They are caught, but as a red verdict with no counter line to explain it; a counter crash
is indistinguishable from a target miss to the caller.

## Named limits for the L1 (proposed additions to the wave-2 list; nothing edited)

- **N-C2d** (F1) the case-set check and the patches leg do not carry the stub gate: under A08 the control's `cases=37 pass=37` is printed; under A08+C08 the r41 tool exits 0.
  The stub's REJECTED label rests on refusal rows and on `sp < sn`; W2 shows that `sp <= sn` turns two passing stubs into REJECTED.
- **N-C2e** (F2) the 37-case pin lives only in `met()`; a loosened gate plus one dropped case is green (S4).
- **N-C2f** (F3) `tool_sha` is printed but not part of the verdict.
- **N-C2g** (F4) twenty single-point survivors (table): refusal rows, timeout, the real/retro/selftest floors, the stub claim and class, and the crash check are not pinned by the table.
- **N-C2h** (F5) harness crashes produce the same exit code as a target miss and no SUMMARY.

## Integrity and what was not done

- The frozen counter, the landed tool, the control and every other tracked file were read only. No tracked file was written. The lane working tree was clean
  (`git status --porcelain` empty) when read. Git was used only as `clone`, `checkout` and `rev-parse`/`show` on a scratch clone.
- Mutants and probes ran in a clone of the lane at the tip, in `/fast/scratch/hyaku/souji-r42/R42w2mutationtester07/`. That clone and every fixture directory were deleted
  at the end of the seat. Evidence is in this seat directory (`mutants/`, `receipts/`, `scripts/`).
- No tool was installed or upgraded.
- Not run: the wave-2 held-out audit and any cross-seat comparison; the `score-candidate.sh` path. The seat scored through the counter's own `--tool` option against a clone,
  which is the same counter and the same tool bytes.

## Commands run (outputs in `receipts/`)

```
git clone --quiet --no-hardlinks /home/vgpnk/Projects/shokunin/souji-shokunin clone-tip      # scratch only
git -C clone-tip checkout --quiet 3105a63b23481fccf7df58e74d14a6681e0ea0c8
python3 -B …/census/round-42/c2-counter.py --root clone-tip --rev 3105a63… --scratch <scratch>                 # pristine landed: 37/37
python3 -B …/census/round-42/c2-counter.py --root clone-tip --rev 3105a63… --tool census/round-42/controls/c2-stub-tool.py --scratch <scratch>   # pristine control: 24/37
python3 -B scripts/driver.py     # 37 mutants (A-F) x 2 artifacts + BASE           -> receipts/results.json
python3 -B scripts/driver_g.py   # 15 G singles + 4 stacks x 2 artifacts           -> receipts/results-g.json
python3 -B scripts/driver_h.py   # 8 H singles x 2 artifacts                       -> receipts/results-h.json
python3 -B scripts/analyse_all.py                                                   # SUMMARY diffs, no-change set, exit codes
python3 -B scripts/mktables.py   > receipts/tables-from-mktables.md
python3 -B scripts/probe_stub.py > receipts/stub-probe.txt
python3 -B scripts/probe_vacuity.py                                                 # V1 V2 V3 receipts
python3 -B scripts/probe_d03.py                                                     # W1 W2 receipts
python3 -B scripts/make_report.py                                                   # writes this file from the receipts
sha256sum census/round-42/c2-counter.py   # fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1 (unchanged)
```

The scripts were run from the scratch directory and copied unchanged into `scripts/`.
"""

report = head + body + counts + findings
with open(OUT, "w", encoding="utf-8") as h:
    h.write(report)
print("wrote", OUT, len(report), "bytes")
