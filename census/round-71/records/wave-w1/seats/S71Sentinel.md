# S71Sentinel — round-71 writer security / fail-closed review

Verdict: **C1's prose is FALSIFIED** — "the clean-tree witness is not forgeable through a clean filter
driver" is false. Two deterministic rc=0/EXIT=0 receipts over a worktree differing from HEAD; neither has
a matrix row, so the frozen predicate cannot see them. Bytes: `git show a1db6c85:tools/souji-receipt-write.py`
(sha256 56b6be03…c85207). Fixtures in `/fast/scratch/hyaku/souji-r71/S71Sentinel` (removed after the pass).

## HIGH-1 — in-run clean filter removes its own attribute (deterministic, no race)
`python3 -B selfunlink.py`: the command writes `.git/info/attributes` = `tools/counter.py filter=t`, sets
`filter.t.clean=<py>` (emits `counter v2`→`counter v1`, then unlinks the attribute), forges
`tools/counter.py` to `counter v2\n` (size-equal to committed `counter v1\n`).
Observed: `writer rc=0 receipt=WRITTEN`, receipt `EXIT=0`; after the run `status= M tools/counter.py`,
`worktree=b'counter v2\n'`, `blob=b'counter v1\n'`, `attr exists=False`.
Cause: `cand-writer.py:557` reads post-run status **before** `:559 post_drivers = _filter_drivers(top)`;
git had already selected the filter, and the attribute is gone by `check-attr` time → `[]`. Contradicts
`:558-559`. Fix: `_filter_drivers(top)` **before** `post_st` (mirror `:449`); and/or fingerprint tracked
worktree content on the clean path (snapshot exists only under `--allow-dirty`, `:467-472`).

## HIGH-2 — repository-local core.checkStat=minimal / core.trustctime=false
`git()` pins only `-c core.fileMode=true` (`:132`); a size-equal edit with `os.utime` mtime restore is
invisible to `git status`, and the clean path takes no content snapshot.
`python3 -B wprobe.py` + `python3 -B misc.py`: W1 pre-run, W2 in-run, W3 pre-run, M3 in-run → all
`rc=0 receipt=WRITTEN` (M3 leaves `git status` empty); control W4 → `rc=2 refused: lane worktree is dirty`.
`git -c core.checkStat=default status` → ` M tools/counter.py`, so pinning `core.checkStat=default` +
`core.trustctime=true` closes it. Not a named limit; same class as the F2 fileMode route.

## LOW
- `working-tree-encoding=UTF-16` LE↔BE swap: size-equal, same decoded text, status clean (`edge3.py` D3);
  byte-level divergence only — the receipt binds git-clean, and instrument bytes are compared directly.
- `.git/info/exclude` hides an untracked file (`misc2.py` D2/D3, rc=0) — declared named limit at `:59-60`.

## Closed (probed, rc=2, no receipt)
`attr.tree`→filter commit (W5), repo-local `core.attributesFile` (W6), driver name `T`/`a.b` (W7),
`filter.t.process` config (M1) → `RECEIPT-FILTER-DRIVER-SET`; in-run driver+attr+edit with the attribute
left in place (W8/W9/D1) → same. `check-attr` and `status` agreed on every attribute source (`attrsrc.py`,
`asym.py`). `ident` (E6), `text`+autocrlf (D2), wte other text (D3), `core.ignoreStat=true` (E3),
`core.untrackedCache` (D4/E9): no size-preserving hidden edit (clean/ident only shrink or preserve).

## F3/F4/F5 — closed
`ctr.py`: `verify_members` rejects `../M1`, `M1/../M2`, `/etc/passwd`, `a/b`, `''`, `.M1`, `..`, `M1 `;
SHA256SUMS `../M1.py`, `./M1.py`, `a/M1.py`, `.hidden.py` → "names a non-plain file" (selftest
`c1-counter.py:1584-1605`). Harness labels `../esc`, `a/b`, `..`, `.hidden`, `x y`, `x\ny` →
`C2-HARNESS-FATAL: --label must be one plain path component` EXIT=2; `-rf` → usage error; nothing created
outside `--work` (`c2-harness.py:108-126`).

Files in `.ufo/waves/round-71/w1/S71Sentinel/`: `t1-receipt.txt`, `t1-evidence.txt`, `probe-transcript.txt`,
`selfunlink.py wprobe.py statcfg.py misc.py misc2.py edge3.py ctr.py asym.py attrsrc.py procfilter.py`
(`procfilter.py`: attempted v2 filter, deadlocks in handshake — the `.process` route is decided at
config-read, M1, not by a live driver). Report: `.ufo/waves/round-71/w1/S71Sentinel.md`.
