# SwarmCritic09 — seat report (AttackE05)

## Status

W1's C1 E05 finding is **CONFIRMED**. The do-nothing MISMATCH is real and independently reproduced;
the proposed argv-correction restatement satisfies every frozen rule in
`census/round-34/c1-counter.py`; no honest rule-conforming route was missed. The mismatch is a
measurement artifact (counter's out+err concatenation + a stale six-case registry literal), exactly as
W1 diagnosed. Two minor evidence-quality defects in W1's deliverable do not change the verdict.

## Evidence

- Frozen row `c1-items.tsv:44` (list-rev `2b0171e…`, byte-identical at worktree; sha256 of committed
  bytes `5de3678206dcc091d2a2f911f0fe085021c90431d1e40edeea9dd15765b06127`).
- Counter rules: stderr appended after stdout (`c1-counter.py:304`), last digit-bearing line
  (`:110-112`), statement equality (`:312-313`), argv-correction checks (`:267,275,286-300`).
- Four bounded probes in `/fast/scratch/hyaku/souji-r34/SwarmCritic09` (17 MB sparse shared clone,
  counter-exact scrubbed env; scratch ceiling respected):
  - base + frozen argv → rc=0, last digit line = usage banner (reproduces W1's quoted ITEM verbatim);
  - base + corrected argv `… 2>/dev/null` → rc=0, stderr 0 bytes, last digit line =
    `cases=15 pass=15 control=TAMPER-REJECTED` (matches proposed statement exactly);
  - cause parent `de478b4…` + frozen argv → old fixture passes fully on stdout
    (`cases=6 pass=6 control=TAMPER-REJECTED`) yet predicate fails under out+err (lane-2 stderr path);
  - cause `fec846dd…` + frozen argv → identical failure mode.
- Read-only git checks: blame `fec846dd` wrote SCORECARD.md:23; list-rev line 23 absent at parent
  blob / present at cause blob; cause is ancestor of list-rev; Q76 grep = 3 R29-CORRECTION prose lines
  (SCORECARD.md:295-297) none binding the fixture literal (line 297 explicitly disclaims it);
  SCORECARD.md:314 r33 row records the same argv → `cases=15 pass=15 control=TAMPER-REJECTED`.

## Findings

1. Defect real, reproduced; six-case literal unreachable at base (fixture prints hard-coded `cases=15`).
2. No value-drift cause: frozen predicate fails at both parent and cause under out+err even though the
   era-correct fixture passed fully on stdout at both — the r28 claim was true when written; the
   counter's measurement rule is what breaks agreement.
3. Proposed correction conforms to all frozen judge checks (traced line-by-line; inputs reproduced).
4. No missed honest route: binding the usage banner (only mechanical alternative) is false provenance;
   binding the lane-2 error path is not judge-conforming; no argv restores six cases; value drift
   unavailable.
5. Minor defects in W1's evidence (verdict-neutral): (a) quoted list sha256 `1ad8c86c…` ≠ committed
   bytes `5de36782…`; (b) r33 row quoted as a tidy mini-row but is a paraphrase of the full r29 row;
   (c) W1's sim receipt not re-run (scratch ceiling) — inputs verified instead [labeled inference].

## Attack log

Attempted falsifications, all defeated: (1) "usage banner has no digits → W1's ITEM quote impossible"
— wrong, `<full40>` supplies `4`/`0`; reproduced exactly. (2) "value-drift cause might exist" —
defeated by parent+cause probes. (3) "`2>/dev/null` might be judge-rejected/dishonest" — defeated by
judge trace + probe 2 + fixture's documented stdout contract. (4) "an honest out+err route keeping
the frozen basis might exist" — alternatives exhausted, all dishonest/impossible. (5) Q76 duplicate
authority check — clean. Read-only throughout; no lane or frozen-artifact mutation.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w2/AttackE05.md` (full report)
- This seat report.
- Probe outputs retained under `/fast/scratch/hyaku/souji-r34/SwarmCritic09/probe*/`.
- Recommendation to main: accept W1's E05 restatement as valid; optionally have W1 correct the two
  evidence quotes (list hash; r33 row citation) before integration.
