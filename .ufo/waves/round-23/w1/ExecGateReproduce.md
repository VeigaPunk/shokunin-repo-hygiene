# ExecGateReproduce — independent r22 gate-check (C2) before/after reproduction

author: L1Souji23.ExecGateReproduce (leaf seat, round 23 w1)
date: 2026-10-25
lane base: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`; `git rev-parse master` = `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`
tooling: none installed, none upgraded (no package transaction attempted; host pacman pause not touched)

## Status

STATUS: PASS — both mirrors built read-only from `git archive` and run against their own corpus; the tip mirror
reproduces `fail=0`, the base mirror does **not** reproduce `fail=10` (it reports `fail=0`), and the recorded
`fail=10` reproduces only with the pre-`af73b8b` tool blob, which the frozen C2 rule forbids.

## Evidence

Scratch: `/var/tmp/souji-r23-ExecGateReproduce/` (removed at end of run; no lane write except this report).
Every mirror is `git -C /home/vgpnk/Projects/shokunin/souji-shokunin archive <rev> | tar -x -C <mirror>`; every
tool invocation used cwd = the mirror and `--root .` (the frozen r22 command form), so no run touched the live
lane tree.

Frozen command form (`.ufo/waves/round-22/attempt2/preregistration.txt:71-76`, reproduced from committed bytes):

    python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
      --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
                corpus/knowledge/quarantine-origin-record-fields-r24.md \
      --snapshot-dir census/round-22/attempt2/sources \
      --slice census/round-22/attempt2/quarantine-slice \
      --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv

### Mirror matrix (counts line, rc, tool sha256 in that mirror)

| mirror | rev | tool blob in tree | tool sha256 | counts line | rc |
|---|---|---|---|---|---|
| m-base1208 | `1208bfb` (lane base) | `63ac63b8` | `d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d` | `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0` | 0 |
| m-tip | `master` = `1208bfb` | `63ac63b8` | `d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d` | `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0` | 0 |
| m-r22tip | `77d6595` (r22 tip) | `63ac63b8` | `d5ed0805…` | `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0` | 0 |
| m-r22base | `4edb25d` (r22 base) | **ABSENT** | n/a | injected tip tool: `entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=3` | 1 |

`find <mirror> -type f | wc -l`: m-base1208 = 3880, m-tip = 3880 (identical trees, see Finding 1),
m-r22base = 3533, m-r22tip = 3880.

### Before-state reconstruction (the only state that yields the recorded number)

`4edb25d` holds neither the tool nor `census/round-22/attempt2/` at all (`git ls-tree -r --name-only 4edb25d
census/round-22/attempt2` → empty), so the before-state is a mid-round *working tree* that no commit contains.
Reconstructed faithfully in scratch from the `a211e4d` tree by removing the two entries and the verdicts TSV
(slice kept: 8 ids, `grep -cE 'S[0-9]{3,}'` = 8). Same root, three tool blobs:

| tool blob | tool sha256 | counts line | rc |
|---|---|---|---|
| `4309d769` (at `a211e4d`) | `d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00` | `entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=10` | 1 |
| `f26aa728` (at `af73b8b`..`8680755`, the recorded after-run blob) | `5b8025a83f16957cb2ff6aca0adecfc3a6a1ff796c3eed1d70018ecc339b3062` | `entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=2` | 1 |
| `63ac63b8` (tip) | `d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d` | `entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=2` | 1 |

`fail=10` detail under `4309d769` (all ten lines, verbatim):

    FAIL corpus/knowledge/quarantine-staging-no-copy-r23.md entry-missing: corpus/knowledge/quarantine-staging-no-copy-r23.md
    FAIL corpus/knowledge/quarantine-origin-record-fields-r24.md entry-missing: corpus/knowledge/quarantine-origin-record-fields-r24.md
    FAIL slice verdict-missing:S114
    FAIL slice verdict-missing:S123
    FAIL slice verdict-missing:S124
    FAIL slice verdict-missing:S126
    FAIL slice verdict-missing:S131
    FAIL slice verdict-missing:S133
    FAIL slice verdict-missing:S138
    FAIL slice verdict-missing:S118

`fail=2` under `5b8025a8`/`d5ed0805` is the same two `entry-missing` lines only; the eight `verdict-missing`
lines are gone.

### Stale-blob after-run still green

`python3 tools/tool-f26aa728….py --root /var/tmp/souji-r23-ExecGateReproduce/m-r22tip <frozen args>` →
`entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, rc 0. The counter cannot see the digest mismatch.

### Tool blobs (identity of the digests in play)

`git cat-file blob f26aa728 | sha256sum` → `5b8025a8…b3062` (the digest the r22 report cites);
`git cat-file blob 63ac63b8 | sha256sum` → `d5ed0805…c9d` (the digest `census/round-22/attempt2/instrument-digests.txt`
records). So the report's cited digest is *correct for the blob it ran*, and wrong for the tip — exactly the D3 shape.

### Direct answers

- **Base mirror (`1208bfb`) reproduce `fail=10`? NO.** It reports `entries=2 ok=2 slice_verdicts=8 slice_total=8
  fail=0`, rc 0.
- **Tip mirror (`master`) reproduce `fail=0`? YES** — but trivially: `master` *is* `1208bfb`, so the two mirrors
  are the same tree and the "before/after" pair of this assignment degenerates to one measurement.
- **`fail=0` after-state reproduces at the real r22 tip** `77d6595` with both the tip blob and the recorded
  `5b8025a8` blob, rc 0 both times.

## Findings

1. **The assigned base and tip revisions are the same commit.** `git rev-parse HEAD` and `git rev-parse master` in
   `/home/vgpnk/Projects/shokunin/souji-shokunin` both return `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`
   (matching `.ufo/waves/round-23/preregistration.txt:2`, "ahead=0 behind=0"). The r22 `fail=10` before-state is
   therefore unreachable from either mirror named in the ticket; only the r22 revisions can express it.
2. **`fail=10` is a blob-dependent artifact, not a reproducible state property.** The `a211e4d` blob counts each
   missing verdict row as a failure — `tools/souji-gate-check.py` at `a211e4d`, lines 173-174:
   `for i in ids:` / `fails.append("verdict-missing:%s" % i)`. The frozen C2 contract forbids that
   (`.ufo/waves/round-22/attempt2/preregistration.txt:96-99`, "counted in neither V nor F"), and `af73b8b`
   removed it (`tools/souji-gate-check.py:175-177` at the tip, "so no `fail` entry"). Consequence: the recorded
   before/after pair spans two different fail semantics — 8 of the 10 before-fails are an accounting rule the
   contract later declared wrong.
3. **No committed revision contains the before-state.** At `4edb25d` the tool is absent (`git cat-file -e
   4edb25d:tools/souji-gate-check.py` fails) and `census/round-22/attempt2/` does not exist, so the base tree scores
   `fail=3` with `slice_total=0`, not `fail=10` with `slice_total=8`. The tool, the slice, the verdicts and both
   entries all first appear in one commit, `a211e4d` (`git log --diff-filter=A --` on each path). The
   `slice_total=8` in the recorded before line proves the before run happened in a working tree where the slice
   existed and the entries/verdicts did not — a state only a file-level reconstruction can rebuild.
4. **Difference from spot-check D3** (`corpus/lessons/round-22-verifier-spotcheck.md:193-194`): D3 asserts the
   before receipt is *missing* and the digest is stale; it does not say the before number is unreproducible.
   Measured: (a) D3's stale-digest half is confirmed and is invisible to the counter (evidence above, rc 0 under
   `5b8025a8`); (b) D3's remedy "commit the before receipt" is not satisfiable as written — re-running the
   before-state with the tip blob yields `fail=2`, so an honest before receipt must bind `4309d769`/`d85c2696…`
   *and* record the reconstruction (which paths were absent), or the round must re-state the before figure as
   `fail=2`. Anything else pins a number to bytes that did not produce it.
5. **D8 confirmed at the bytes.** The committed slice line for S118 is `` S118` `` with a stray backtick
   (`census/round-22/attempt2/quarantine-slice`, line 8). `SLICE_ID_RE = re.compile(r"S\d{3,}")` uses `search`,
   not an anchored match, so the id still extracts and `slice_total=8` is unaffected — cosmetic, as D8 says.
6. **Read-only claim holds for the counter path, not for `--selftest`.** The non-selftest path of the tip tool
   (`tools/souji-gate-check.py:1-313`) performs only `open`/`isfile`/`realpath` reads; `--selftest` creates
   `tempfile.mkdtemp(dir="/var/tmp")` and tears it down with `subprocess.run(["rm","-rf", base])` in its `finally`
   block. A receipt that must be write-free has to bind a non-selftest run (the `-B` in the frozen command only
   suppresses `__pycache__`).

## Attack log

- **A1 — the round-23 C3 counter line cannot execute.** `.ufo/waves/round-23/preregistration.txt:96-97` freezes
  `python3 tools/souji-gate-check.py --entries … --snapshot-dir <dir> --expect-slice 0`. Measured in the base
  mirror: `souji-gate-check.py: error: unrecognized arguments: --expect-slice 0`, rc 2; `--help` lists only
  `--root --round-date --entries --snapshot-dir --slice --slice-verdicts --selftest`. Dropping the bogus flag
  leaves a second failure — the line has no `--round-date`, so `error: --round-date and --entries are required
  unless --selftest`, rc 2. The frozen C3 counter is unrunnable as written; re-freezing is the parent's call, I did
  not edit it.
- **A2 — the C3 "do nothing" control is not distinguishable on this counter.** At the lane base `1208bfb` the r22
  entries already score `entries=2 ok=2 … fail=0` (matrix row 1), so gate-check cannot separate before from after
  for round 23 by fail count; only the two r23 entry paths (absent at base) can, and those are the entries the
  round itself authors. Any "before: gate-check fails" statement for r23 needs its own frozen before line.

## Not run / not claimed

No lane write other than this report; no `git add/commit/push/stash/checkout`, no `jj` mutation, no `rm`/`mv`
outside `/var/tmp/souji-r23-ExecGateReproduce/`; the tool was never run against the live lane tree; no registry
census, no receipt-run.py verify (a sibling seat owns C2's receipt chain). Scratch removed after this report.
