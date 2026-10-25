# W2Scorecard — attack on the Round 23 SCORECARD table

Seat: L1Souji23.W2Scorecard (wave 2, falsify). Read-only; every command below was run against the
lane at `/home/vgpnk/Projects/shokunin/souji-shokunin`.

Tip identity at measurement: `git rev-parse HEAD` =
`102690017115cb202f292828c90b72705f69bf09` (detached). Landed round commits:
`476525026cdb179f2d49441e1cb6c6f7316f3124`, `c0eeaa7a01d309710ab53c41afc6b0df734217a3`.
Lane base (control): `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`.

Target artifact: `SCORECARD.md:21-23` (the "Round 23 measurements" table) and the two r23 rows of
`## Capabilities` (`SCORECARD.md`, rows "blob-bound receipts (r23)" and "record agreement audit (r23)").

---

## 1. Per-row re-run

| row | number in table | command re-run | output at tip | verdict |
|---|---|---|---|---|
| C1 after | `mismatches=0` at the landing tip, receipt `census/round-23/records/agreement-after.txt` | `python3 -B tools/souji-record-agreement.py --rev 1026900…` (the row's own command, verbatim) | `keys=4 records=4 occurrences=17 mismatches=7`, RC=1 | **mismatch** |
| C1 after (revision-scoped) | same | `… --rev 1026900… --no-worktree` | `keys=4 records=4 occurrences=17 mismatches=0`, RC=0 | match, but the flag is not in the row |
| C1 before | `keys=4 records=3 occurrences=13 mismatches=6` | `… --rev 1208bfb… --no-worktree` | `keys=4 records=3 occurrences=13 mismatches=6`, RC=1 | match |
| C1 before (worktree arm) | `mismatches=29` | receipt `agreement-control-base-worktree.txt` read; live re-run | live re-run gives 8 (worktree has moved on); receipt holds 29 | match to its receipt, not re-derivable |
| C2 | 5 bound receipts, every one `verify=ok`; before 0 | `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ \| wc -l` | `5` | match |
| C2 | same | `python3 tools/souji-receipt-run.py verify --root . <each of 5>` | 5× `verify=ok`, RC=0 each | match |
| C2 | before `0` | `git grep -lE '^tool_sha256=[0-9a-f]{64}$' 1208bfb -- census/ \| wc -l` | `0` | match |
| C3 gate | `entries=2 ok=2 fail=0` | `python3 tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries … --snapshot-dir census/round-23/sources --slice … --slice-verdicts …` | `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`, RC=0 | match |
| C3 census | "census exit 0" | `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` | 30× `W04`, final line `souji<TAB>ok<TAB>…/corpus/SOURCES.md`, RC=0 | match |
| C3 registry | 119 rows (S115–S119) | `grep -cE '^\| *S[0-9]{3}' corpus/SOURCES.md`; base rev for before | `119`; base = `114`; max id `S119`; `uniq -d` on ids = empty | match |
| C3 F2 | F2 holds three entries | `grep -nE '^\|? *\*?\*?F2' corpus/README.md`; `ls corpus/knowledge/` | README:68 "**r23: the read side now holds three entries**"; all three files present | match |

The two C1 numbers that are *stated correctly* are the base control (`6` revision-scoped) and the
worktree arm (`29` at receipt time). The after number is the one that fails.

## 2. Capability rows — demonstrated?

| capability row | command in the row | ran | result |
|---|---|---|---|
| blob-bound receipts (r23) | `tests/fixtures/r23-receipt-run.py` 8/8 | yes | `selftest=8/8`, RC=0 (cases 1–8 all as declared, incl. `RECEIPT-TOOL-DIGEST-MISMATCH` at case 3) |
| blob-bound receipts (r23) | refusal surface named in the row text | yes, direct | `git -C . count-objects -v` → `GIT-DIRECTED-COMMAND`, RC=2; `git gc` → `MUTATING-SUBCOMMAND`, RC=2 |
| blob-bound receipts (r23) | positive re-derivation | yes, direct | `run --rev 1026900… --tool tools/souji-record-agreement.py … python3 -B tools/souji-record-agreement.py --rev 1026900…` → `rc=0 counts=keys=4 records=4 occurrences=17 mismatches=0`; `verify` → `verify=ok` |
| record agreement audit (r23) | `python3 -B tools/souji-record-agreement.py --rev <full40>`; fixture 9/9 `control=FALSE-GREEN-REJECTED` | yes | fixture `selftest=9/9`, `control=FALSE-GREEN-REJECTED`, RC=0; the tool runs (outputs quoted above) |

Both capability rows are demonstrated. Their *tool* digests are stable across the round:
`git cat-file -p <rev>:tools/souji-record-agreement.py | sha256sum` =
`617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9` at `4765250`, `c0eeaa7` and
`1026900` — the row's `617f4c96…a8c9` is correct.

---

## 3. Verdicts

- **C1 record agreement — `falsified` as written** (the *state* is repaired; the *evidence and the
  counting command in the row* are not). The row asserts `mismatches=0` and names a receipt that
  does not exist; the receipt that does exist under that name records `mismatches=1` at the very
  revision it names, and the row's literal command at the tip returns `mismatches=7`.
- **C2 blob-bound receipts — `survives`.** Counter 5, all five verify, digests independently
  re-derived from the tree at each receipt's `rev=`, refusal fires, before = 0.
- **C3 F2 read side — `survives`.** Gate `entries=2 ok=2 fail=0` RC=0, census RC=0, registry
  114 → 119 with no duplicate ids, F2 holds three entries.
- **Both r23 capability rows — demonstrated.**

---

## 4. Findings

### F1 — BLOCKING (C1): the row cites a receipt that does not exist, and the real one contradicts it

`SCORECARD.md:21` after-cell: `` `mismatches=0` at the landing tip (`census/round-23/records/agreement-after.txt`) ``.
The same pointer is repeated at `LOG.md:1578` and `corpus/lessons/round-23.md:22`.

```
$ ls census/round-23/records/agreement-after.txt
ls: cannot access 'census/round-23/records/agreement-after.txt': No such file or directory
$ git log --all --oneline -- 'census/round-23/records/agreement-after.txt'
(no output)
$ git ls-tree -r --name-only 1026900 -- census/round-23/records/ | grep agreement
census/round-23/records/agreement-after.tsv
census/round-23/records/agreement-control-base-worktree.txt
census/round-23/records/agreement-control-base.txt
```

The existing file of that name (`agreement-after.tsv`, committed at `c0eeaa7`) reads:

```
receipt=v1
rev=476525026cdb179f2d49441e1cb6c6f7316f3124
tool_sha256=617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9
cmd=python3 -B tools/souji-record-agreement.py --rev 476525026cdb179f2d49441e1cb6c6f7316f3124
rc=1
--- stdout ---
MISMATCH	K1	SCORECARD.md:14	value-disagree	assertions=55 resolved=52 skipped=33 mismatches=3 != receipt assertions=63 resolved=63 skipped=40 mismatches=0 at 9301d98c…
keys=4 records=4 occurrences=18 mismatches=1
```

Re-running at that revision reproduces the receipt exactly:

```
$ python3 -B tools/souji-record-agreement.py --rev 476525026cdb179f2d49441e1cb6c6f7316f3124 --no-worktree
MISMATCH	K1	SCORECARD.md:14	value-disagree	…
keys=4 records=4 occurrences=18 mismatches=1
RC=1
```

So the only receipt the round holds for C1's after-state is a **failed** run (`rc=1`,
`mismatches=1`) at the first landing commit, where `SCORECARD.md:14` still lacked the
`4edb25df…` revision token (the token was added in `c0eeaa7`:
`diff <(git show 4765250:SCORECARD.md | sed -n 14p) <(git show c0eeaa7:SCORECARD.md | sed -n 14p)`
→ `…before-final.tsv` → `…before-final.tsv` at `4edb25dfe262515d0da63224bbba71e02e36cba5`).

This is the D2 shape ("no receipt binds the named revision") that C1 exists to repair, recurring in
the round that repairs it. **Required action: fix.** Bind the tip with the round's own C2 runner and
cite the bound receipt. A receipt produced that way already verifies:

```
$ python3 -B tools/souji-receipt-run.py run --root . --rev 102690017115cb202f292828c90b72705f69bf09 \
    --tool tools/souji-record-agreement.py --out /var/tmp/…/c1-clean.tsv \
    python3 -B tools/souji-record-agreement.py --rev 102690017115cb202f292828c90b72705f69bf09
receipt=/var/tmp/…/c1-clean.tsv rev=1026900… tool_sha256=617f4c96… rc=0 counts=keys=4 records=4 occurrences=17 mismatches=0
$ python3 -B tools/souji-receipt-run.py verify --root . /var/tmp/…/c1-clean.tsv
verify=ok rev=1026900… tool_sha256=617f4c96…
RC=0
```

(That receipt was written under my `/var/tmp` scratch and is removed; it is a demonstration, not a
landed artifact.) The C1 after-value of `0` **is** reachable at the tip — the claim's number is
right, its evidence is wrong.

### F2 — BLOCKING (C1): the row's counting command does not produce the row's number

`SCORECARD.md:21` counting-command cell is `python3 -B tools/souji-record-agreement.py --rev <full40>`
— no `--no-worktree`. At the tip that command returns:

```
$ python3 -B tools/souji-record-agreement.py --rev 102690017115cb202f292828c90b72705f69bf09
MISMATCH	K4	corpus/lessons/round-23.md	uncommitted-path	M
MISMATCH	K4	.ufo/waves/round-23/report-draft.md	uncommitted-path	??
MISMATCH	K4	.ufo/waves/round-23/w2/W2C2Run.md	uncommitted-path	??
MISMATCH	K4	.ufo/waves/round-23/w2/W2FixAgree.md	uncommitted-path	??
MISMATCH	K4	.ufo/waves/round-23/w2/W2Misroot.md	uncommitted-path	??
MISMATCH	K4	.ufo/waves/round-23/w2/W2Seats.md	uncommitted-path	??
MISMATCH	K4	tools/__pycache__/	uncommitted-path	??
keys=4 records=4 occurrences=17 mismatches=7
RC=1
```

The count moved 1 → 7 within minutes of my session (`report-draft.md` alone at first read; the rest
appeared as wave-2 seats wrote reports). The row's own named limit admits "K4 is a live-worktree
observation, not a revision snapshot", but the row then states a worktree-dependent number as the
after-value without the flag that makes it stable. **Required action: fix the cell** (state
`--no-worktree`, or bind the receipt as in F1) **and disclose** that the K4 arm is 0 only on a clean
tree.

### F3 — MAJOR: verifying C1 with the round's own fixture increments the C1 counter

`tests/fixtures/r23-record-agreement.py` imports the tool as a module and has no bytecode guard:

```
$ grep -n "dont_write_bytecode\|PYTHONDONTWRITEBYTECODE" tests/fixtures/r23-record-agreement.py
(no output)
$ python3 tests/fixtures/r23-record-agreement.py   # as cited in the capability row
… selftest=9/9 / control=FALSE-GREEN-REJECTED
$ ls -la tools/__pycache__/
-rw-r--r-- 1 vgpnk vgpnk 24758 Oct 25 05:42 souji-record-agreement.cpython-314.pyc
```

`tools/__pycache__/` is not in `K4_ALLOWED` (only `census/operator-sweep-20261019/` is,
`tools/souji-record-agreement.py:70`), so running the capability row's own command turns C1's
`mismatches=0` into `mismatches=1`. A claim that cannot be checked without being falsified is not
checkable. **Required action: fix** — set `sys.dont_write_bytecode = True` (or
`PYTHONDONTWRITEBYTECODE=1`) at the top of the fixture, and say so in the capability row.

Disclosure: the `.pyc` above is **my** residue (mtime 05:42 = my fixture run). My contract forbids
`rm`/`mv`, so it is still on disk as an untracked K4 row; the round should land or ignore it
deliberately, not inherit it silently.

### F4 — MAJOR: LOG.md and README carry a base number that disagrees with the receipt they cite

```
$ grep -n "mismatches=20" LOG.md corpus/README.md
LOG.md:1576:mismatches=20, rc 1 (receipt census/round-23/records/agreement-control-base.txt).
corpus/README.md:456:| C1 record agreement | calibration (7) | `mismatches=20` at the base revision → `0` at the landing tip | …
$ cat census/round-23/records/agreement-control-base.txt | tail -1
keys=4 records=3 occurrences=13 mismatches=6
$ python3 -B tools/souji-record-agreement.py --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd --no-worktree | tail -1
keys=4 records=3 occurrences=13 mismatches=6
```

`20` is a stale measurement of earlier tool bytes (`.ufo/waves/round-23/w1/CritPrereg.md:35`,
"333-line bytes"), left uncorrected against a receipt that says `6`. This is the D5 class
("superseded numbers uncorrected") inside the round that claims D5 repaired — and `K2` cannot see
it, because `K2_RECORD`/`K2_SECTION_START` scope the key to LOG.md's `Round22 attempt2` section
only (`tools/souji-record-agreement.py:47-50`). **Required action: fix** — correct both numbers to
`6` (revision-scoped) with an append-only `superseded by` line; **disclose** that the K2 scope
excludes the round's own section; widen K2 at r24.

Note the record disagrees with itself: `SCORECARD.md:21` says `6`, `LOG.md:1576` and
`corpus/README.md:456` say `20`, `corpus/lessons/round-23.md` says `6`.

### F5 — MINOR (C2): the prereg-named receipt set is not the delivered set

Preregistration C2 names "(declared-evidence before, declared-evidence after, gate-check before,
gate-check after)". The five delivered receipts are `declared-evidence-after`,
`gate-check-at-first-landing` (`rev=a211e4d1…`), `gate-check-at-lane-base` (`rev=1208bfb…`),
`gate-check-c3` (`rev=4765250…`), `agreement-after`. There is no `declared-evidence-before`
receipt carrying a bound digest:

```
$ grep -c '^tool_sha256=' census/round-22/attempt2/declared-evidence-before-final.tsv
0
```

The frozen counter (`grep … | wc -l` ≥ 4) is still met at 5, so the row's number stands.
**Required action: disclose** (the parenthetical in the preregistration describes a set the round
could not produce, since the r22 before-receipt predates the runner).

### F6 — MINOR (C2): `verify` has a precondition the capability row does not state

A receipt whose digest matches the committed blob is still refused when the recorded stdout has no
counts line:

```
$ python3 -B tools/souji-receipt-run.py run … --tool tools/souji-record-agreement.py … git count-objects -v
… rc=0 (receipt written, tool_sha256=617f4c96… matches the blob)
$ python3 -B tools/souji-receipt-run.py verify --root . /var/tmp/…/pos.tsv
RECEIPT-COUNTS-ABSENT	no counts line in the recorded output
RC=2
```

The capability row describes `verify` only as a digest check ("`verify` refuses a digest that is not
the committed blob at the receipt's rev"). **Required action: disclose** — name the counts-line
precondition in the row text. (It does not weaken C2: all five committed receipts carry counts
lines and verify.)

---

## 5. Residual risk

- The K4 arm is live-worktree: every number in the worktree column is a timestamp. My readings were
  1 → 7 across one session, driven by sibling seats' untracked reports. Any C1 figure quoted
  without `--no-worktree` is unreproducible by construction.
- `census/operator-sweep-20261019/` is exempted by a hardcoded allowlist
  (`tools/souji-record-agreement.py:70`), not by the committed `uncommitted-exemptions.tsv`; I did
  not test whether a row in that file would also exempt it (the file exists; I did not exercise the
  path).
- `agreement-after.tsv` being one of C2's five `verify=ok` receipts is consistent with C2's claim
  (verify binds bytes, not outcome) and is *not* a C2 defect — but it means C2's "5, every one
  verify=ok" can be satisfied while every receipt records a failing run. The row does not say so.

## 6. Verification gaps (not run)

- The cited C3 sources were not re-opened by me; the C3 gate (`entries=2 ok=2`) and the census were
  run, which is the row's own evidence surface.
- The C3 gate's slice arm is inert this round (`slice_verdicts=0 slice_total=0`); I did not construct
  a non-empty slice to test it.
- I did not run the r21 historical matrix or any historical replay; out of this row's scope.
- I did not attempt `jj` inspection beyond `jj log -r @` (read-only, no state touched).

## 7. Tooling / scratch

- No installs, no upgrades, no `pacman`, no network fetch.
- Scratch: `/var/tmp/souji-r23-w2-W2Scorecard/` (two receipt files), removed before finishing. The
  fixtures' own `/var/tmp` trees are trap-cleaned by the fixtures (`ls -d /var/tmp/souji-receipt-*`
  → empty).
- Only file written inside the lane: this report. It is itself an untracked path
  (`?? .ufo/waves/round-23/w2/W2Scorecard.md`) and therefore one more K4 row until it is landed —
  the same live-worktree effect F2 describes.
