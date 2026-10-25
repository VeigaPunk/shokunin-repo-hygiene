# Round 23 · C1 fixture — record-agreement instrument oracle

## Status

STATUS: PASS — fixture delivered and runnable at `.ufo/waves/round-23/w1/r23-record-agreement.py`
(sha256 `3b1bc5e6…a66537`), 9 cases both directions, `selftest=8/9` against the in-flight
instrument bytes; the one red case is an instrument defect (`rev-disagree` unreachable,
finding 2), not a fixture defect.

## Evidence

Fixture: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-23/w1/r23-record-agreement.py`
(485 lines, executable, stdlib only, hard-coded `/var/tmp` scratch, trap-cleaned).
Lane base for all revision readings: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`.

Run against the instrument as it stood at the end of this wave
(`tools/souji-record-agreement.py` sha256 `e41db304…e596`):

```
$ python3 .ufo/waves/round-23/w1/r23-record-agreement.py
tool=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py
tool_sha256=e41db3043b865acc292d2993a92d2a8a6f79df2d2c6f138b275192454e57e596
scratch=/var/tmp/souji-r23-ExecFixtureAgreement
case=1 expect=rc=0 mismatches=0 keys=4 json-bound got=rc=0 mismatches=0 keys=4
case=2 expect=rc!=0 K1 receipt-absent>=1 got=rc=1 mismatches=1 keys=4 [K1/receipt-absent]
case=3 expect=rc!=0 K1 value-disagree>=1 rev-disagree=0 got=rc=1 mismatches=1 keys=4 [K1/value-disagree]
case=4 expect=rc!=0 K1 rev-disagree>=1 got=rc=1 mismatches=1 keys=4 [K1/occurrence-absent] -> FAIL
  > K1	SCORECARD.md	occurrence-absent	no r22 counts tuple bound to the receipt rev 209300c55baa43e8870e54e4ffa598d82cffdeb9
case=5 expect=rc!=0 K2 uncorrected*>=1 got=rc=1 mismatches=3 keys=4 [K2/uncorrected]
case=6 expect=rc!=0 K2 filed*>=1 got=rc=1 mismatches=1 keys=4 [K2/filed-occurrence-missing]
case=7 expect=rc!=0 K3 tally-disagree>=1 got=rc=1 mismatches=1 keys=4 [K3/tally-disagree]
case=8 expect=rc!=0 K4 uncommitted-path naming the stray round path got=rc=1 mismatches=1 keys=4 [K4/uncommitted-path]
case=9 expect=K4 rows=0 (exempted operator path is not a mismatch) got=rc=0 mismatches=0 keys=4
selftest=8/9
control=FALSE-GREEN-REJECTED
EXIT=1
```

Same fixture, same bytes, one case earlier in the wave: `selftest=9/9` (instrument sha256
`52d98536…4af8`) — case 4 regressed when the K1 body was rewritten, not when the fixture changed.

False-green control, measured (a stub that always prints `keys=4 records=4 occurrences=0
mismatches=0` and exits 0):

```
$ python3 .ufo/waves/round-23/w1/r23-record-agreement.py --tool /var/tmp/…/always-zero.py
case=9 expect=K4 rows=0 (exempted operator path is not a mismatch) got=rc=0 mismatches=0 keys=4
selftest=2/9
control=NOT-REJECTED
FAKE_EXIT=1
```

Read-only instrument run at the lane tip, mid-wave tree (siblings writing `corpus/README.md`,
`LOG.md`, `tools/`), instrument sha256 `f9ec0091…5fe2`:

```
$ python3 tools/souji-record-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin
MISMATCH	K1	census/round-23/records/declared-evidence-after.tsv	receipt-absent	not in tree at 1208bfb…
MISMATCH	K2	LOG.md:1478	uncorrected	'assertions=56 resolved=53 skipped=33 mismatches=3' has no later 'superseded by' line
MISMATCH	K2	LOG.md:1495	uncorrected	'1 present' / '1 refused' …
MISMATCH	K3	corpus/README.md:440	tally-disagree	1 present != receipt 2 present
MISMATCH	K4	census/operator-sweep-20261019/	uncommitted-path	??
… 13 K4 rows (round-22 wave reports, impl-a evidence, round-23 wave dir, two tools/) …
keys=4 records=3 occurrences=13 mismatches=19
```

Base-revision facts, pinned from committed bytes:

```
$ git show 1208bfb:corpus/pointer-exemptions.tsv | grep -c '^uncommitted:'      -> 0   (4 rows total)
$ git show 1208bfb:SCORECARD.md | sed -n '14p' | grep -oE 'assertions=…' | sort | uniq -c
      2 assertions=55 resolved=52 skipped=33 mismatches=3
      2 assertions=63 resolved=63 skipped=40 mismatches=0
$ git show 1208bfb:corpus/README.md | grep -noE '[0-9]+ (accepted|present|unverifiable|refused)'
      440:5 accepted   440:1 present   440:1 refused   441:1 unverifiable
```

Scratch removed: `ls /var/tmp/souji-r23-ExecFixtureAgreement` → *No such file or directory*.
No tool installs (no `pacman` transaction; `git`/`python3` already present).

## Findings

1. **Fixture delivered.** `.ufo/waves/round-23/w1/r23-record-agreement.py` builds a synthetic lane
   repo under `/var/tmp/souji-r23-ExecFixtureAgreement` (`git init` + payload + `git add`/`commit`
   inside the scratch repo only), runs the frozen CLI
   (`--root <repo> --rev <full40> --json <path>`) once per case, and prints
   `case=<n> expect=… got=…`, `selftest=<pass>/<total>`, `control=…`; exit 0 iff every case holds.
   Each case is a fresh repo, so a case cannot inherit another's defect. `--json` is *verified*
   (line, rev and row count must bind the stdout), not merely passed.

2. **K1 `rev-disagree` is unreachable — instrument defect.** `tools/souji-record-agreement.py:167`
   reads `elif rev in m.group(0) or not rev:`. `rev` is a 40-hex commit and `m.group(0)` is a
   counts tuple, so the first disjunct is never true, and the second is false whenever the receipt
   carries a `rev=` header — the only state in which the check matters. A line whose token differs
   from the receipt therefore falls through to `occurrence-absent` (`:171`), a class that means
   "no tuple at all". Frozen C1 names the class explicitly: *"Mismatch classes: receipt-absent,
   value-disagree, rev-disagree"* (`.ufo/waves/round-23/preregistration.txt`, C1 K1). Fixture case 4
   is the measurement. Restoring the branch is a predicate repair before any after-data, not a
   narrowing: retiring the class after data would be a contract change.

3. **K1 real-tip double tuple.** `SCORECARD.md:14` at `1208bfb` carries the base tuple **twice** and
   the after tuple **twice** on one `r22`-scoped physical line. K1 requires *every* tuple on a
   scoped line to equal the receipt, so once the receipt lands the two base-tuple occurrences report
   `value-disagree` even though the after figure is right. The fixture deliberately carries one
   tuple, so it cannot catch this — named coverage gap, not a fixture claim. Owner must choose: stop
   quoting the base tuple on an r22-scoped line, or make K1 select the tuple bound to the receipt
   rev (the current `if rev and rev in line` guard already exists and would do it if the base tuple
   were not on that line).

4. **K4 has no exemption to work with at the base.** `git show 1208bfb:corpus/pointer-exemptions.tsv`
   has 0 rows carrying the frozen `uncommitted:` prefix (4 rows, none prefixed). The frozen K4
   predicate exempts only prefixed rows, so `census/operator-sweep-20261019/` — operator-owned,
   deliberately untracked — is counted as round work. Fixture case 9 proves the prefix is
   sufficient to exempt (K4 rows = 0). The row needs the prefix; the predicate must not be widened
   to guess, and the path must not be committed or deleted (hard bound).

5. **K3 has no quoted-historical allowance.** The D4 correction sentence quotes the stale tally
   verbatim (`corpus/README.md:440-444` in the tree I opened, mid-wave): *"this sentence said
   1 present, 1 refused (wrong-source citation) until r23"*. K3 scans every `<n> <class>` occurrence
   with no `superseded by` escape (unlike K2), so a verbatim quote of the repaired numbers keeps the
   record red after the repair. Cheapest legal fix is wording — describe the old tally without the
   `<n> <class>` pattern — not a predicate change. Fixture case 7 covers the disagreeing tally only.

6. **K2 receipt constant diverges from the frozen text.** `tools/souji-record-agreement.py:48` names
   `census/round-22/attempt2/declared-evidence-before-final.tsv`; C1 in the preregistration names
   `census/round-22/attempt2/declared-evidence-before.tsv`. Both files exist in the lane. The fixture
   writes both with identical bytes so no case depends on the choice — but the round must state which
   one is the frozen K2 receipt, since a receipt swap changes the expected tuple.

7. **Self-reference is structurally impossible; do not "fix" it back.** A commit cannot contain a
   receipt whose `rev=` names that same commit. The fixture therefore uses two commits: commit 1 is
   the measured revision, commit 2 (the tip, `--rev`) carries the receipt whose `rev=` and whose
   SCORECARD token both name commit 1. That is exactly what the frozen text asks (token equals the
   receipt header; receipt exists in the tree at `--rev`). An earlier instrument revision
   (`03393e3d…`) enforced `receipt.rev == --rev` and made `mismatches=0` unreachable; the current
   bytes agree with the fixture. Keep it that way.

8. **The fixture models the real LOG's physical shape on purpose** — header `LOG.md:1469`, the `=`
   rule on the very next line (`:1470`), and the 4-tuple wrapped across `:1484-1485` — plus a decoy
   tuple outside the section. Cases 1/5/6 therefore fail if the underline-skip or the
   paragraph-join handler regresses. Both handlers are confirmed live on real bytes: the mid-wave
   run reported `LOG.md:1478` and `:1495` as `uncorrected`, i.e. it found the wrapped tuple inside
   the real section.

## Attack log

- **A1 (measured, rejected).** The cheapest false green is an emitter that always prints
  `mismatches=0`. Measured: `selftest=2/9`, `control=NOT-REJECTED`, exit 1. Cases 2-8 each demand a
  named class, so no zero-only emitter can pass them.
- **A2 (measured, open).** Class substitution: reporting a revision-token disagreement as
  `occurrence-absent` makes the D2 binding check pass review while the record is bound to the wrong
  revision. Finding 2 is this attack landing by accident in the instrument; case 4 is the guard.
- **A3 (design, open).** K4 is exemption-by-prefix with no allowlist: any seat can hide its own
  round work by writing an `uncommitted:` row. The fixture shows the prefix alone is sufficient
  (case 9). Code cannot close this; it is a review surface, so the exemption file must be read as
  part of the landing gate, not trusted.
