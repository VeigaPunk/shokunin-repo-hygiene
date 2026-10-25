# MutCounterStub — round-26 counter mutation test (probes a/b/c)

## Status
STATUS: PASS — probes a/b/c executed on isolated scratch repo; false-green paths
found for (b) and (c); the (a) "second SCORECARD" mutant is KILLED (no false-green).
No lane bytes touched; scratch removed; no tool installs.

## Evidence
Probe world: `/var/tmp/souji-r26-MutCounterStub/probe` (git init, toplevel
verified before first commit; all later git calls use `-C`). Counter blobs at
lane HEAD hash-identical to the committed receipts: c1 `c8dbb76…`, c2
`e3f7a67…`, c3 `fcf954f09…` (`git cat-file blob HEAD:<path> | sha256sum`).

### (a) second SCORECARD
- A0 baseline (HEAD 0c92c2e): `bash census/round-26/c1-counter.sh` →
  `markers=0` / `headings=17 44 78` (rc=0).
- A1: commit `SCORECARD.md.bak` = base 0eca7c8 bytes (sha256
  `b42a24f0…`); counter unchanged `markers=0` / `headings=17 44 78` —
  backup invisible, green unchanged. Receipt run writes rc=0 `counts=none`;
  verify refuses `RECEIPT-COUNTS-ABSENT` (rc=2).
- A2: swap — real `SCORECARD.md` = base dirty bytes (sha256 `b42a24f0…`),
  backup = clean bytes (`b659efc6…`); counter prints `markers=2` /
  `headings=17 175 231` — red, no false green. The counter reads exactly the
  single repo-root `SCORECARD.md` (`census/round-26/c1-counter.sh:2-4`, bash
  single-file args, no glob).

### (b) grounded_f1 counting
Knowledge set committed at rev `8bd7f17`:
`fa-entry.md` (front-matter `ground: F1` above title), `fb-entry.md` (NO front
matter; body-example line `ground: F1` in a fence below the title),
`fc-comment.md` (`# ground: F1`), `fd-escaped.md` (`\`ground: F1\``),
`fe-indented.md` (`  ground: F1`). `bash census/round-26/c2-counter.sh` →
`grounded_f1=2` (fa+fb), `registry_rows=132`. `grep -l '^ground: F1'` matched
exactly `fa-entry.md` `fb-entry.md`. Tool-style mirror of
`tools/souji-coverage-agreement.py` `front_grounds`
(`FRONT_GROUND = re.compile(r"^ground:\s*F([0-9]+)")`, stops at first `# `
line): `fa-entry.md [1]`, `fb-entry.md []`, fc/fd/fe empty.

### (c) verify semantics
- `tools/souji-receipt-run.py:4` — "A counter run is only evidence if the bytes
  that produced it are pinned." `:7-8` — "verify re-reads the same bytes from
  git and refuses a receipt whose recorded digest is not the committed blob at
  the named revision."
- C1 probe: `tools/ph-counter.sh` prints `entries=1 ok=1 fail=0` then `exit 1`;
  receipt records `rc=1`; verify → `verify=ok …` rc=0 (rc never examined).
- C2 probe: `tools/pv-counter.sh` receipt taken at rev `841bd17` (printed
  `entries=1 ok=1 fail=0`); tip advanced to `c8136e4` with data flipped — same
  counter now prints `entries=0 ok=0 fail=0`; verify of the old receipt → still
  `verify=ok` (never re-runs, never checks recorded counts against tip).
- Real receipts under current committed runner: c1-before / c1-after /
  c2-before / c2-after / c3-before ALL refuse `RECEIPT-COUNTS-ABSENT` (rc=2).
  c3-after and c2-k4-base verify ok (their stdout contains `cases=12 pass=12`
  resp. `grounded=7 …` shapes). The runners last changed at `315422b` (r24),
  predating every r26 receipt.

## Findings
1. [ATTACK, c] `verify=ok` is byte-binding, not truth: it re-hashes the tool
   blob at the recorded durable rev, checks the command string and the presence
   of any `COUNTS_RE`-shaped stdout line; it never re-runs, never compares
   recorded counts to the tip tree, and never inspects `rc=`
   (`tools/souji-receipt-run.py:292-330`). A counter that failed (rc=1) and a
   counter whose data flipped after the receipt verify identically `verify=ok`
   (measured). A green receipt therefore proves nothing about the claim's
   after-condition.
2. [ATTACK, c] most round-26 receipts are structurally unverifiable: c1/c2/c3
   counters print `markers=`, `headings=`, `grounded_f1=`, `registry_rows=`,
   `axis_check_tool=` lines, none of which match `COUNTS_RE` (regex at
   `tools/souji-receipt-run.py:67-75`). Five of six committed receipts refuse
   (measured). The prereg's "each `verify=ok`" is unreproducible; any scorer or
   landing re-run that treats the receipt files as verified evidence consumes
   unverified bytes.
3. [ATTACK, b] c2 K1 counts FILES whose ANY line equals `^ground: F1`
   (`census/round-26/c2-counter.sh:7-8`), while the tool's own parse scopes
   ground lines to front matter above the first `# ` heading
   (`tools/souji-coverage-agreement.py:92-100`). A body-example `ground: F1`
   line in a non-grounded file counts for grep but not for the tool (measured:
   grounded_f1=2 vs tool-grounded=1). Kill rule only tests `K1 != 2`, so one
   lost front-matter ground can be masked by a body-line match elsewhere —
   K1 stays 2 while only one entry is truly grounded (K4 not run → false green).
4. [ATTACK, b] the `corpus/knowledge/*.md` glob admits every `.md` directly in
   that directory (stray drafts, backups), so an unrelated file with one
   matching body line can supply the second count (aggravates finding 3).
5. [killed] (a) mutant dies: no counter reads a second SCORECARD (single-file
   args, no glob); a dirty backup cannot flip K1/K2 and a wrong-file surgery is
   detected red. No false-green path from stray backups.

## Attack log
The above items 1-4 are reported as ATTACKs (gameable/false-green counter
behavior), per contract; no predicate/target/case-set changes proposed.

## Restoration
All mutations lived in disposable scratch; blobs hashed above (A1/A2,
B variants, ph/pv counters). `/var/tmp/souji-r26-MutCounterStub` removed before
finish. Lane repo untouched (read-only `git cat-file/rev-parse/branch` plus
`verify --root` clones only).
