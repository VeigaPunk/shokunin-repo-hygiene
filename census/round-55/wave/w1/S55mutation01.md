# S55mutation01 — kill-power of the new v4 checks (souji round 55, wave w1)

Seat: `S55mutation01` (role: mutation-tester), lane `/home/vgpnk/Projects/shokunin/souji-shokunin`
at `3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f`, measured revision
`4b10ddd1741a948c89d283358affd1da2ab3fd95` (frozen pins are byte-identical at both).
Scratch: `/fast/scratch/hyaku/souji-r55/S55mutation01/` (deleted at yield; every
receipt in this report was copied to `receipts/` under this seat directory first).

**Bottom line.** 18 of 21 assigned mutants are killed by the committed fixture
population, each by the fixture the task named, with the named finding and exit
code. Three survive; all three are `C2` selftest-harness gaps, not `C1` gaps:
one is a missing fixture for a frozen-prose shape (a *known* receipt key in
lowercase), and two are the same structural defect — the selftest never asserts
that every row of the committed expected TSV is exercised, so an arm deleted
from the arm list passes. Fixtures rebuild byte-identically, and the rebuilt
revs/exit/finding rows reproduce the committed v4 matrix with 0 mismatches
(27 C1 + 13 C2 rows).

## 0. Pins, bounds, method

Pins verified at seat start and again after the sweep (`receipts/pins-start.txt`,
`receipts/pins-end.txt`) — all six frozen sha256 values match the task statement,
including `c1-counter.py 944feafa…d921a2`, `c2-counter.py e4eb34e6…a568c`,
`build-fixtures.py e629a2e9…fa8d62`, `run-matrix.sh ce13d4ff…ef8315`,
`c1-selftest-expected.tsv ca096117…b7b6e`, `c2-selftest-expected.tsv 63391afa…bd2bc`.

No frozen byte was written. Every mutant is a **scratch copy** under
`mut/<id>/` (with a byte-identical copy of the committed builder beside it, so
the counter's own `--builder-sha256` pin still verifies the committed builder
bytes). The committed counters were only read; no mutating git/jj command ran in
the lane, the fleet repo, or any non-scratch repo, and nothing was committed
there. The only git mutations are the synthetic fixture repos the committed
builder creates under the seat scratch (its `init_repo` asserts
`git rev-parse --show-toplevel` equals the fixture dir before the first commit);
the GAP-1 probe clone carries the same assertion in `receipts/probe-toplevel.txt`
(toplevel == clone dir). `git status --porcelain` in the lane shows only sibling
seats' work (`SKILL.md`, `corpus/QUALITY.md`, `corpus/SOURCES.md`,
`corpus/knowledge/splitlines-line-model.md`, and later `corpus/lessons/round-55.md`),
untouched by this seat. Disk guard checked before the heavy pass:
`/fast/scratch/hyaku` 50 % used, 409.2 G free. No tool was installed or upgraded.

Two detectors, both over the committed fixture population and the committed
expected TSV:

- **Detector A (the committed oracle):** `python3 -B <counter> --selftest --work DIR
  --expected <committed TSV> --builder-sha256 e629… --expected-sha256 <pin>`.
  Exits 0 only when every case's exit code *and* first-finding id match the
  committed TSV. Baseline: C1 `SELFTEST pass cases=27` rc 0; C2
  `SELFTEST pass cases=15` rc 0 (`receipts/baseline-c1-selftest.txt`,
  `receipts/baseline-c2-selftest.txt`).
- **Detector B (wider):** pristine vs mutant `measure()` over every prebuilt
  fixture, comparing exit code, **all** FINDING lines and the SUMMARY line (the
  shape `run-matrix.sh` records). Used to attribute kills beyond the first
  finding and to prove a survivor is behaviourally invisible, not merely
  first-finding-invisible (`receipts/full-output-diffs.json`).

"Killed" below means: detector A exits non-zero **and** the named fixture's
`SELFTEST-CASE` line flips from `pass`. Detector B's diff set is quoted as the
attribution; for all 18 kills it is exactly the one named fixture (no
over-determination, no collateral kills).

Determinism (task requirement): `receipts/determinism.txt`. Fixtures built twice
into the same work root produce a **byte-identical manifest**
(`637b262d…0b29b`, `cmp` IDENTICAL); built into a second work root the manifest
is identical once the path column is stripped (`cmp` IDENTICAL,
`5d6edb6c…822c`). Cross-check against the committed receipts
(`receipts/matrix-crosscheck.txt`): the rebuilt fixture revisions, exit codes and
first findings reproduce `records/matrix-dryrun/c1-matrix-v4.tsv` and
`c2-matrix-v4.tsv` with **C1 rows=27 mismatches=0, C2 rows=13 mismatches=0**
(the F7-FF rebuild rev is the prereg-quoted `e163e0fa6689`).

## 1. C1 — kill table (14 mutants for the 13 assigned checks)

| # | mutant (mutated check) | named fixture | before (exit / finding) | after (exit / finding) | detector A | verdict |
|---|---|---|---|---|---|---|
| 1 | `C1-01-splitlines` — `hidden_lines` numbered with `str.splitlines()` again (S1 one-line-model regression) | F7-FF | 1 / CORRECTION-IN-FENCE (`fenced=2 filed=0`) | 0 / — (`fenced=0 filed=2`) | 0→1 | **killed** |
| 2 | `C1-02a-indent-prefix` — both correction regexes lose ` {0,3}` (R1 indent tolerance) | F20-R1-INDENT-SWALLOW | 1 / BOGUS-RECOMPUTED (`bogus=2`) | 0 / — (`bogus=0`) | 0→1 | **killed** |
| 3 | `C1-02b-comment-prefix` — both correction regexes lose `(?:<!--\s*)?` (R1 wrapper tolerance) | F21-R1-ONELINE-SWALLOW | 1 / BOGUS-RECOMPUTED (+2 CORRECTION-IN-FENCE) | 0 / — | 0→1 | **killed** |
| 4 | `C1-03-alias-first-only` — anchor loop over `zones[:1]` (R2 alias) | F13-DUAL-ANCHOR | 1 / ANCHOR-ALIAS-MISMATCH (`alias=1`) | 0 / — (`alias=0`) | 0→1 | **killed** |
| 5 | `C1-04-pairinert-removed` — PAIR-FILING-INERT loop deleted (R3) | F14-PAIR-STALE-FILING | 1 / PAIR-FILING-INERT (`pairinert=1`) | 0 / — (`pairinert=0`) | 0→1 | **killed** |
| 6 | `C1-05-rows-required` — `rows?` re-required in PAIR_ANNOT_RE (R4) | F15-PAIR-NOROWS | 1 / UNFILED-SOURCES-ANNOTATION (`logunfiled=1`) | 0 / — (`logunfiled=0`) | 0→1 | **killed** |
| 7 | `C1-06-ascii-only-arrow` — `→` dropped from the pair separator (S2) | F16-PAIR-ARROW | 1 / UNFILED-SOURCES-ANNOTATION | 0 / — | 0→1 | **killed** |
| 8 | `C1-07-fence-indent` — fence-opener guard `if indent <= 3` → `if True` (R5) | F17-INDENT4-FENCE | 0 / — (`filed=2 fenced=0`) | 1 / CORRECTION-IN-FENCE ×2 (`filed=0 fenced=2`) | 0→1 | **killed** |
| 9 | `C1-08-backtick-info` — backtick-in-info rule removed (R5) | F18-BTINFO-FENCE | 0 / — | 1 / CORRECTION-IN-FENCE ×2 (`fenced=2`) | 0→1 | **killed** |
| 10 | `C1-09-pair-hidefence` — `if i in phidden: continue` removed (R6) | F19-PAIR-IN-FENCE | 0 / — | 1 / UNFILED-SOURCES-ANNOTATION (`logunfiled=1`) | 0→1 | **killed** |
| 11 | `C1-10-ptr-widened` — PTR_RE back to the v3 shape-only token | F22-PTR-TIMESTAMP | 1 / UNFILED-SOURCES-ANNOTATION | 0 / — | 0→1 | **killed** |
| 12 | `C1-11-closing-length` — `len(body) >= n` removed (M2) | F8b-BT4-SHORT-RUN | 1 / CORRECTION-IN-FENCE (`fenced=2`) | 0 / — (`fenced=0 filed=2`) | 0→1 | **killed** |
| 13 | `C1-12-recompute-branch` — SOURCES-RECOMPUTE-MISMATCH block deleted (N5) | F23-SOURCES-RECOMP | 1 / SOURCES-RECOMPUTE-MISMATCH (`logrecomp=1`) | 0 / — (`logrecomp=0`) | 0→1 | **killed** |
| 14 | `C1-13-exemption-removed` — `or PTR_RE.search(ln)` dropped (M7) | F12c-LOG-POINTER-EXEMPT | 0 / — | 1 / UNFILED-SOURCES-ANNOTATION (`logunfiled=1`) | 0→1 | **killed** |

All 14 C1 mutants are killed. Detector B's full-output diff set is exactly the
named fixture for every row (`receipts/full-output-diffs.json`). Mutant byte
hashes: `receipts/results.json` (`sha_before` is the pristine counter sha and
equals the frozen pin for every row; `sha_after` is the mutant).

## 2. C2 — kill table (7 sweep mutants + 2 arm probes + 2 crash variants for the 6 assigned items)

| # | mutant (mutated check) | named fixture | before (exit / finding) | after (exit / finding) | detector A | verdict |
|---|---|---|---|---|---|---|
| 15 | `C2-14-tab-rule-narrow` — `'\t' in ln` → `ln.count('\t') >= 5` (NL-1) | FB1-TAB4-ROW | 1 / COMMENT-AMBIGUOUS-NAME | 0 / — | 0→1 | **killed** |
| 16 | `C2-15a-key-case` — RECEIPT_KV key class back to `[A-Z0-9_]+` (NL-3) | FB2-LOWER-KEY | 1 / RECEIPT-UNKNOWN-KEY | 0 / — | 0→1 | **killed** |
| 17 | `C2-15b-key-upper` — `kv.group(1).upper()` → `kv.group(1)` (probe of the same surface) | FB2-LOWER-KEY | 1 / RECEIPT-UNKNOWN-KEY | 1 / RECEIPT-UNKNOWN-KEY (**unchanged**) | 0→0 | **SURVIVED** |
| 18 | `C2-16-space-tolerance` — RECEIPT_KV `\s*#\s*` → `# ` (NL-4) | FB3-NOSPACE-KEY | 1 / RECEIPT-UNKNOWN-KEY | 0 / — | 0→1 | **killed** |
| 19 | `C2-17-fa9-arm-removed` — `'FA9-WRONG-TOOL-PIN'` deleted from the arm list | FA9-WRONG-TOOL-PIN | case present: rc 1 / TOOL-SHA-ARG-MISMATCH | case **absent** | 0→0, `SELFTEST pass cases=14` (15 expected rows) | **SURVIVED** |
| 20 | `C2-18-fb4-arm-removed` — `'FB4-PIN-SHAPE'` deleted from the arm list | FB4-PIN-SHAPE | case present: rc 2 / TOOL-SHA-ARG-MALFORMED | case **absent** | 0→0, `SELFTEST pass cases=14` | **SURVIVED** |
| 21 | `C2-19-classmismatch-id` — `CLASS-MISMATCH` prefix reverted (§5.2) | FA8-SYMLINK-CLASS | 1 / CLASS-MISMATCH (`class_mismatch=1`) | 1 / **`class`** (`class_mismatch=1`) | 0→1 | **killed** (finding column, as specified) |
| 22 | `C2-17b-fa9-pin-none` — arm kept, but passes `None` for FA9 (the M11 regression) | FA9-WRONG-TOOL-PIN | rc 1 / TOOL-SHA-ARG-MISMATCH | `SELFTEST-CASE … fail rc=0 want_rc=1 finding=-` | 0→1 | **killed** |
| 23 | `C2-18b-fb4-pin-none` — arm kept, but passes `None` for FB4 (the NL-5 regression) | FB4-PIN-SHAPE | rc 2 / TOOL-SHA-ARG-MALFORMED | `SELFTEST-CASE … fail rc=0 want_rc=2 finding=-` | 0→1 | **killed** |
| 24 | `C2-17c/18c-…-branch-removed` — name kept in the list, removed from the arm-specialization tuple | FA9 / FB4 | — | `unknown fixture <arm>` on stderr, rc 1, **no SELFTEST-CASE lines** | 0→1 | crash-kill, **not** an assertion kill |

Note on row 21: exit code and SUMMARY (`class_mismatch=1`) are unchanged; only
the finding name changes (`FINDING CLASS-MISMATCH …` → `FINDING class …`). The
committed expected TSV is what kills it — exactly the §5.2 defect being repaired.

## 3. Survivors — r56 coverage-gap list

### GAP-1 (C2, NL-3/NL-4): no committed fixture for a **known** receipt key in a tolerant shape

`C2-15b` removes the key-case normalisation (`kv.group(1).upper()`). On the
committed population nothing changes — FB2 carries an *unknown* lowercase key,
which the widened regex still reports as unknown with or without `.upper()`.
Detector B: empty diff over all 13 C2 fixtures.

The frozen C2 prose names the uncovered shape explicitly ("a KNOWN key in any of
those shapes is recognized and validated instead of ignored", prereg C2 / NL-4).
Scratch probe (`receipts/probe-known-lower-*.txt`, re-run with the guard
assertion in `receipts/probe-toplevel.txt`; mutant sha256 `396e3c26…f717a`
reproduced identically on the re-run): FH-HONEST rebuilt, receipt line
`# RECEIPT_VERSION=1` rewritten to `# receipt_version=1`, committed in the
scratch clone (toplevel asserted equal to the clone dir before the commit):

```
pristine  rc=0  receipt=ok
mutant    rc=1  FINDING RECEIPT-UNKNOWN-KEY receipt carries unknown key receipt_version
                FINDING RECEIPT-MALFORMED … does not carry the RECEIPT_VERSION=1 grammar
```

So the mutant is *behaviourally* caught by a shape the contract names, but no
committed fixture covers it. **Route:** add a committed fixture with a known key
in lowercase and/or no-space shape (e.g. `# receIpt_version=1`,
`#TOOL_SHA256=…`), expecting exit 0. No frozen byte edited.

### GAP-2 (C2 selftest harness): expected-TSV rows are not a closed set

`C2-17` / `C2-18` delete an arm name from
`names = list(mod.C2_FIXTURES) + ['FA9-WRONG-TOOL-PIN', 'FB4-PIN-SHAPE']`.
`run_selftest` iterates `names` only and never asserts `set(exp) - set(names)`
is empty, so the committed expected row is simply never visited:

```
$ tail -1 receipts/selftest/C2-17-fa9-arm-removed.txt
SELFTEST pass cases=14          # committed TSV has 15 rows (16 lines incl. header)
rc=0
```

The task statement expected this mutant to fail against the committed TSV; it
does not. Two adjacent variants show where kill-power actually lives:

- **arm kept, branch input reverted** (`pin=None` for the arm) → the committed
  TSV kills it (`SELFTEST-CASE … fail rc=0 want_rc=1`, selftest rc 1). Rows 22–23.
- **arm kept in `names`, removed from the specialization tuple** → the run
  crashes before any case (`unknown fixture FA9-WRONG-TOOL-PIN`, rc 1, no
  `SELFTEST-CASE` lines). Non-zero exit, but not an assertion failure; the
  detector cannot distinguish a deleted arm from a broken harness.

**Route:** assert row coverage, e.g.
`missing = set(exp) - set(names); ok = ok and not missing` (and print them).
Same structural weakness exists in the C1 selftest; there it is currently latent
because `c1-selftest-expected.tsv` has exactly the 27 `C1_FIXTURES` names, so no
live gap — record it as a structural note, not a finding.

**Not** a survivor: the literal FA9/FB4 *behaviour* (wrong pin → rc 1
TOOL-SHA-ARG-MISMATCH; uppercase pin → rc 2 TOOL-SHA-ARG-MALFORMED) is
kill-powered by the committed TSV whenever the arm is exercised. The gap is the
harness's non-enforcement of arm presence.

## 4. Restoration evidence

Committed bytes were never written; the sweep ran only on scratch copies.
After the sweep (`receipts/pins-end.txt`):

```
944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2  census/round-55/c1-counter.py
e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c  census/round-55/c2-counter.py
e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62  census/round-55/fixtures/build-fixtures.py
ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e  census/round-55/records/c1-selftest-expected.tsv
63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc  census/round-55/records/c2-selftest-expected.tsv
```

Each mutant's `sha_before` in `receipts/results.json` equals the pristine pin, so
before/after hashes pair per mutant. The scratch tree is deleted at yield.

## 5. Appendix — exact byte diffs

Full unified diffs (context 2, pristine → mutant) are in
`receipts/mutants.diff`. Compact form; every mutant changes only the lines shown:

```
C1-01  - for i, raw in enumerate(text.split('\n'), 1):
       + for i, raw in enumerate(text.splitlines(), 1):
C1-02a CORR_RE/CORR2_RE (2 lines):  - '^ {0,3}(?:<!--\s*)?R5x-CORRECTION …'
                                    + '^(?:<!--\s*)?R5x-CORRECTION …'
C1-02b CORR_RE/CORR2_RE (2 lines):  - '^ {0,3}(?:<!--\s*)?R5x-CORRECTION …'
                                    + '^ {0,3}R5x-CORRECTION …'
C1-03  - for k, (ok_tokens, straddle) in enumerate(zones):
       + for k, (ok_tokens, straddle) in enumerate(zones[:1]):
C1-04  - "            for f in (fil or []): … finding('PAIR-FILING-INERT', …)"
       + "            pass"
C1-05  - PAIR_ANNOT_RE = re.compile(r'(\d+)\s*(?:->|→)\s*(\d+)(?:\s+rows?\b)?')
       + PAIR_ANNOT_RE = re.compile(r'(\d+)\s*(?:->|→)\s*(\d+)\s+rows?\b')
C1-06  - PAIR_ANNOT_RE = re.compile(r'(\d+)\s*(?:->|→)\s*(\d+)(?:\s+rows?\b)?')
       + PAIR_ANNOT_RE = re.compile(r'(\d+)\s*(?:->)\s*(\d+)(?:\s+rows?\b)?')
C1-07  -         if indent <= 3:          (the fence-OPENER guard only; the closer guard stays)
       +         if True:
C1-08  -             if m and not (m.group(1)[0] == '`' and '`' in m.group(2)):
       +             if m:
C1-09  -             if i in phidden:
       -                 continue  # r54 reviewer R6 routed fix: fenced examples are not annotations
C1-10  - PTR_RE = re.compile(r'(?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+\.[A-Za-z0-9]{1,5}:\d')
       + PTR_RE = re.compile(r'[A-Za-z0-9_.\-]+:\d')
C1-11  -                 if body and set(body) == {ch} and len(body) >= n:
       +                 if body and set(body) == {ch}:
C1-12  - "            for f in match: … finding('SOURCES-RECOMPUTE-MISMATCH', …)"
       + "            pass"
C1-13  -             if 'corpus/SOURCES.md' not in ln or PTR_RE.search(ln):
       +             if 'corpus/SOURCES.md' not in ln:
C2-14  -             if '\t' in ln:
       +             if ln.count('\t') >= 5:
C2-15a - RECEIPT_KV = re.compile(r'\s*#\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\S+?)\s*')
       + RECEIPT_KV = re.compile(r'\s*#\s*([A-Z0-9_]+)\s*=\s*(\S+?)\s*')
C2-15b -             key = kv.group(1).upper()
       +             key = kv.group(1)
C2-16  - RECEIPT_KV = re.compile(r'\s*#\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\S+?)\s*')
       + RECEIPT_KV = re.compile(r'# ([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\S+?)\s*')
C2-17  -     names = list(mod.C2_FIXTURES) + ['FA9-WRONG-TOOL-PIN', 'FB4-PIN-SHAPE']
       +     names = list(mod.C2_FIXTURES) + ['FB4-PIN-SHAPE']
C2-18  -     names = list(mod.C2_FIXTURES) + ['FA9-WRONG-TOOL-PIN', 'FB4-PIN-SHAPE']
       +     names = list(mod.C2_FIXTURES) + ['FA9-WRONG-TOOL-PIN']
C2-19  -             problems_pre.append('CLASS-MISMATCH class %r want %r for %r' % (cls, want, name))
       +             problems_pre.append('class %r want %r for %r' % (cls, want, name))
C2-17b -             pin = '0' * 64 if name == 'FA9-WRONG-TOOL-PIN' else 'A' * 64
       +             pin = None if name == 'FA9-WRONG-TOOL-PIN' else 'A' * 64
C2-18b -             pin = '0' * 64 if name == 'FA9-WRONG-TOOL-PIN' else 'A' * 64
       +             pin = '0' * 64 if name == 'FA9-WRONG-TOOL-PIN' else None
C2-17c/18c
       -         if name in ('FA9-WRONG-TOOL-PIN', 'FB4-PIN-SHAPE'):
       +         if name in ('FB4-PIN-SHAPE',):            (17c; 18c keeps FA9 only)
```

## 6. Receipts index (this seat directory)

- `receipts/pins-start.txt`, `receipts/pins-end.txt` — six frozen pins, before/after.
- `receipts/baseline-c1-selftest.txt` — 27 cases, all pass, rc 0.
- `receipts/baseline-c2-selftest.txt` — 15 cases, all pass, rc 0.
- `receipts/mutate-run.txt` — the 21-mutant sweep, per-mutant kill lines.
- `receipts/probe-run.txt` — arm-regression probes (17b/18b) + lowercase-key probe.
- `receipts/full-diff-run.txt`, `receipts/full-output-diffs.json` — detector B.
- `receipts/results.json`, `results2.json`, `results3.json` — machine tables + mutant hashes.
- `receipts/mutants.diff` — exact unified diffs for the 21 sweep mutants (the 17b/18b/17c/18c probe diffs are quoted compactly in §5).
- `receipts/selftest/*.txt` — raw selftest output per mutant.
- `receipts/fixture-manifest-a.tsv`, `fixture-manifest-a2.tsv` — determinism.
- `receipts/determinism.txt`, `receipts/matrix-crosscheck.txt`.
- `receipts/probe-known-lower-pristine.txt`, `probe-known-lower-mutant-15b.txt` — GAP-1.
- `receipts/probe-toplevel.txt`, `probe2-run.txt`, `probe2.py` — guard assertion for the probe commit.

No named limit was converted into an edit of frozen bytes; GAP-1 and GAP-2 are
recorded for the r56 coverage packet, not repaired here.
