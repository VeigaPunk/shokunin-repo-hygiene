# RevD8 — routed defect D8 (S118 stray backtick): independent verification

STATUS: PASS — D8 is real at the lane base and slightly understated; it is **not** closed at
`1208bfb` and this round's plan does not close it (the plan is a disclosure). In-place repair is
barred by two committed digest bindings and by two byte-identical committed copies of the file.

Lane base read: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (preregistration line 2).
Claim source: `corpus/lessons/round-22-verifier-spotcheck.md` §6 D8, with §2 (slice re-extract)
and §5 (quality trend) as its evidence.

## Evidence

All commands run read-only from `/home/vgpnk/Projects/shokunin/souji-shokunin` on 2026-10-25.
No tool was installed or upgraded (nothing was needed). No `git` write, no `jj`, no `rm`/`mv`.

**E1 — defect reproduced from committed bytes (one command + output).**

```
$ git cat-file -p 1208bfb:census/round-22/attempt2/quarantine-slice | sed -n 8p | cat -A
 S118`   the cited source could not be fetched, so no quote was checked $
```

Sibling rows for contrast (same blob):

```
$ git cat-file -p 1208bfb:census/round-22/attempt2/quarantine-slice | sed -n '1p;7p' | cat -A
 S114   `payload-absent` $
 S138   `payload-absent` $
```

Worktree bytes are identical to the base blob (no `M` for this path in `git status --porcelain`;
`git rev-parse 1208bfb:census/round-22/attempt2/quarantine-slice` = `19fa47d72382c157845fd0638bd032570de07484`;
`sha256sum` = `12d3c325649ca6026bdb9b98b1edb1ebd2d2dcc61ac519bfa14d7d084c5da7e6`).

**E2 — provenance: the backtick is the register's id cell, carried verbatim by the frozen selector.**

```
$ sed -n '361p' /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md | cat -A | cut -c1-120
| `souji` | round1 | S118` | the cited source could not be fetched, so no quote was checked | https://doi.org/...

$ awk -F'|' -v l='souji' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ {print $4, $5}' "$R" \
  | diff - census/round-22/attempt2/quarantine-slice
EXIT=0
```

**E3 — count unaffected (D8's own qualifier), re-derived live from the committed tool.**

```
$ python3 -c "... m.check_slice('.', 'census/round-22/attempt2/quarantine-slice',
                              'census/round-22/attempt2/slice-verdicts.tsv') ..."
slice_verdicts=8 slice_total=8 fails=[]
ids from line 8: S118
```

Mechanism: `tools/souji-gate-check.py:45` `SLICE_ID_RE = re.compile(r"S\d{3,}")` is unanchored and
applied with `.search()` per line (`check_slice`, `tools/souji-gate-check.py:141-175`); the class
slot of the slice file is never read — the class authority is `slice-verdicts.tsv:2`
(`S118  unverifiable`). Matches the committed receipt
`.ufo/waves/round-22/attempt2/residual/evidence/counter.txt:41`
`entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`.

**E4 — the file is digest-bound filed evidence.**

```
$ sed -n '9p' .ufo/waves/round-22/attempt2/residual/evidence/counter.txt
census/round-22/attempt2/quarantine-slice                  19fa47d72382c157845fd0638bd032570de07484
$ sed -n '18p' .ufo/waves/round-22/attempt2/residual/evidence/ResClaims-commands.txt
  12d3c325649ca6026bdb9b98b1edb1ebd2d2dcc61ac519bfa14d7d084c5da7e6  census/round-22/attempt2/quarantine-slice
$ git log --format='%h %ad %s' --date=short -- census/round-22/attempt2/quarantine-slice
a211e4d 2026-10-21 round-22: declared-evidence audit tool, assimilation entries and gate checker
```

Two byte-identical committed copies also carry the malformed line:

```
$ diff -q census/round-22/attempt2/quarantine-slice .ufo/waves/round-22/attempt2/w1/evidence/CritC2Counter/real-slice-copy.txt
$ diff -q census/round-22/attempt2/quarantine-slice .ufo/waves/round-22/attempt2/w1/evidence/CritC2Counter/fx/F0/census/round-22/attempt2/quarantine-slice
(no output, both exit 0)
```

## Findings

**F1 — D8 is real as stated, and understated in one respect.** Location:
`census/round-22/attempt2/quarantine-slice:8`. The row carries (a) the trailing backtick in the id
cell (`S118` + `` ` ``) and (b) prose — `the cited source could not be fetched, so no quote was
checked` — in the *class* slot where lines 1-7 carry a backticked class token. (b) is the
structural defect; the spot-check names only (a) in §6 and does mention the prose slot in §2 and in
`residual/ResSliceVerdicts.md` F7. Neither changes a count.

**F2 — not closed at the lane base.** The base blob still contains the line (E1); the file has a
single commit, `a211e4d`, and no later revision repairs it.

**F3 — the defect is upstream and register-wide, not souji-local.** The register's id cell is the
malformed token; 109 register rows share the same trailing-backtick id cell
(`awk -F'|' '$4 ~ /`[[:space:]]*$/' "$R" | wc -l` → `109`), of which exactly 1 falls in souji's
frozen selection. A lane-local edit would make souji's slice the only normalized member of a
fleet-wide malformed family and would diverge from the frozen selector's output.

**F4 — the in-place repair is barred; the exact minimal repair that *would* close it is:**
file `census/round-22/attempt2/quarantine-slice`, line 8, whole-line replacement, preserving the
leading and trailing space of the sibling rows:

```
- S118`   the cited source could not be fetched, so no quote was checked
+ S118   `unverifiable`
```

Wording constraints: the id cell must be exactly `S118` with no backtick; the class token must be
the value at `census/round-22/attempt2/slice-verdicts.tsv:2` (`unverifiable`, one of the frozen
four-set) and must not be re-derived or invented; no prose in the class slot; nothing else on the
line. Proof of closure (only if that edit were legal):

```
$ git show <tip>:census/round-22/attempt2/quarantine-slice | sed -n 8p | cat -A
 S118   `unverifiable` $
$ git show <tip>:census/round-22/attempt2/quarantine-slice | grep -cE '^ S[0-9]{3,}`'
0
```

It is **not** legal here: the edit would (i) invalidate `counter.txt:9`'s blob binding
`19fa47d7…`, (ii) invalidate `ResClaims-commands.txt:18`'s sha256 binding `12d3c325…`,
(iii) falsify the frozen-selector receipt `residual/evidence/ResSliceVerdicts-slice-reextract.txt:22-24`
(`awk … | diff - …` `EXIT=0`), and (iv) break the byte-identity of `real-slice-copy.txt` and the
`CritC2Counter/fx/F0` fixture (E4) — the fixture mutation 6 in `residual/evidence/ResGateCheck.md:107`
is defined against that tree. The register itself is outside this lane and read-only, so the source
fix is unavailable too.

**F5 — this round's plan does not close D8; it discloses it.** No round-23 wave item edits
`census/round-22/attempt2/quarantine-slice` or its copies (`w1-spec.json`: 0 occurrences of
`quarantine-slice`; the only `S118`/backtick/D8 hits are ScribeEntryGarbage's and ScribeSourcesRows'
new `S118`/`S119` community rows, ScribeLog's and ScribeReport's "dispositions D1-D8", and this
item). The preregistration's C1 key set covers D1/D2/D4/D5 only; C1 K3 reads
`slice-verdicts.tsv`, never the slice file. So the round's D8 handling is a LOG.md + report
disposition, which records the defect and leaves the bytes as filed. That is the correct action,
but the round must not report D8 as repaired.

**F6 — append-only alternative (the achievable closure).** Two additions, no edit to filed bytes:
1. In the append-only LOG.md correction entry already planned for D5, carry a D8 line naming:
   `census/round-22/attempt2/quarantine-slice:8`; the register provenance
   (`absent-defect-register.md:361`, id cell `` S118` ``); the register-wide scope (109 rows); that
   the frozen selector reproduces the row byte-exactly (`diff` EXIT=0); and that no count moves
   (`slice_verdicts=8 slice_total=8 fail=0`, `SLICE_ID_RE` unanchored, class authority
   `slice-verdicts.tsv:2`). Constraint: `superseded by`-style wording is wrong here — nothing is
   superseded; use "inherited, unrepairable in place, count unaffected".
2. Optionally commit a *new* normalized derivative, e.g.
   `census/round-23/records/quarantine-slice-normalized` (8 rows, line 8 = ` S118   `unverifiable` `)
   with a receipt whose diff against the frozen extraction differs on line 8 only. Proof command:

```
$ git show <tip>:census/round-23/records/quarantine-slice-normalized | sed -n 8p | cat -A
 S118   `unverifiable` $
$ git show <tip>:census/round-22/attempt2/quarantine-slice | sed -n 8p | grep -q 'S118`'; echo "filed-intact=$?"
filed-intact=0
```

**F7 — adjacent, outside D8's scope (not counted here).** The preregistration's C3 counter invokes
`python3 tools/souji-gate-check.py … --expect-slice 0`; at the base tool that flag is unrecognized:
`tools/souji-gate-check.py --expect-slice 0` → `error: unrecognized arguments: --expect-slice 0`,
EXIT=2. Either the C3 counter text or the tool must change before C3's after-run; the C3 owner should
see this. `[INFERENCE]` the round may extend the tool for C2 digests and add the flag — unverified.

## Attack log

This item is a verification seat, not an attack: no counter, predicate, key set or target is
proposed for change and none is edited. The only counter-relevant claim tested (E3) was re-derived
from committed tool bytes, not from a sibling's report.
