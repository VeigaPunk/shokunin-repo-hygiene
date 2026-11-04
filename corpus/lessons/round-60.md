# Round 60 — freeze-record substance binding and atomic receipt writing

Two claims. C1 calibration (lowest legacy axis 7) + capability acquisition: the freeze checker gains
an opt-in `--substance` arm that binds a claim's `Control:` receipt to the declared `Counter:` bytes
and to a strict-ancestor revision, measured on a frozen 8-case matrix against the base tool bytes.
C2 operability: `tools/souji-receipt-write.py` writes receipts atomically, refuses overwrite, a dirty
tree and an oversized capture, and is measured by an 8-case fixture against the r57 recorder.
Base `1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4`. This round does not re-declare the rejected r56/r57
visibility-parser claims, the r58 receipt-gate claim or the r59 classification repair.

## Gate

Sources opened 2026-11-04 by the L1 (fetch: `curl -sSL`, HTTP 200, byte counts in
`census/round-60/sources/`; quote word counts by `split()`).

- **S288 admit** — Python 3.15.2 documentation, `os.replace`:
  https://docs.python.org/3/library/os.html#os.replace — page 791358 bytes. Located quote (14 words):
  `If successful, the renaming will be an atomic operation (this is a POSIX requirement).`
  Scope: the primitive the receipt writer publishes with.
- **S289 reject** — same page, different scope: the inference that a temp file under `$TMPDIR` can be
  renamed onto a receipt path on another device. The page says `The operation may fail on some Unix
  flavors if src and dst are on different filesystems.` Flip: place the temp beside the output. The
  page is not rejected; the inference is.
- **Re-opened, cells unchanged**: S110 `rename(2)` (man-pages 6.19), S213 POSIX `rename()`, S214 POSIX
  `fsync()` — the three primitives F4's `origin-record-exclusivity-r28.md` already holds — and S251
  `git merge-base --is-ancestor` (the strict-descendant contract of
  `git-strict-descendant-relation-r40.md`). This round applies held knowledge in a tool; it claims no
  new file-system ground.
- No package adoption: `/home/vgpnk/Projects/shokuknow/merge/souji/` not adopted this round (the r46
  mass-id-drift hold is retained). `considerthese/` is absent from the lane root.
- Rows added: A1 (S288) / B0 / C0; one rejection (S289). Registry 211 → 213 rows.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| vacuous: a freeze grammar that binds labels, not bytes | corpus/lessons/round-59.md `## Additional mistakes`; the five forgery states the substance arm now refuses | Q99 (label grammar) and the r59 critic F1/F2 | `CONTROL-INSTRUMENT-*` / `CONTROL-REV-*` / `CONTROL-COMMAND-*` classes, with the 5 forgeries as committed matrix rows |
| TO-BE-FILLED-BY-INTEGRATION | | | |

## Named limits

TO-BE-FILLED-BY-INTEGRATION
