# SwarmScribe33 — round 34 / w1 — S230 (bubblewrap mount semantics)

## Status

STATUS: PASS — S230 opened live (HTTP 200, 33 289 bytes, sha256 `2cb77df2…be1da` at tag v0.13.1,
the tag the host runs), id shown free at the freeze commit, registry row and lesson
`## Gate` entry drafted with located verbatim quotes; bytes saved under the wave dir, nothing
committed and nothing outside this seat's write scope touched.

## Evidence

All lane paths absolute; base `9c76c7222a8abff027af42e37f0d160d52526bba`, freeze
`2b0171e2071fdc9c16a69bed12b0d040e574d8c8`. Serialization/flock not applicable (no fixture run);
`cat /proc/loadavg` recorded beside each reading.

1. Freeze contract and registry shape read first:
   `census/round-34/preregistration.txt` (whole file, incl. A1–A6),
   `git -C <lane> show 2b0171e2…:corpus/SOURCES.md | sed -n '1,40p'` and `| tail -20`
   → 11-column header `| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`
   and the round-33 provenance paragraph naming S224–S229.
2. Id collision at the freeze commit:
   ```
   $ git -C <lane> show 2b0171e2…:corpus/SOURCES.md | grep -cE '^ {0,3}\|[[:space:]]*S230'
   0
   $ … | grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' | grep -oE 'S[0-9]+' | sort -u | wc -l
   153
   $ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' <lane>/corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort | tail -5
   S225 S226 S227 S228 S229
   ```
3. Live fetch (2026-10-27, load `21.70 12.06 6.09`):
   `curl -sS -D hdr.txt -o bwrap-v0.13.1.xml -w 'HTTP %{http_code} bytes %{size_download}\n' https://raw.githubusercontent.com/containers/bubblewrap/v0.13.1/bwrap.xml`
   → `HTTP 200 bytes 33289`; header `content-type: text/plain; charset=utf-8`, `date: Tue, 27 Oct 2026 11:40:31 GMT`, `content-length: 33289`;
   `sha256sum` → `2cb77df2f4be0b2a0302bb2f0a260fdb4d9e1299b76481ea66ed34c40f5be1da`.
   Saved as `.ufo/waves/round-34/w1/src-S230.html` (33 289 bytes, same sha256 after copy).
4. Tag choice grounded in the host: `command -v bwrap && bwrap --version` → `/usr/bin/bwrap`,
   `bubblewrap 0.13.1`, exit 0 — the bytes are the tag the lane's N3 leg would execute.
5. Quotes verified against the saved bytes by `grep -cF` (each 1 or more; `readonly` 2, one of
   them the `--ro-bind` listitem at `:312`):
   `creates a new mount namespace for the sandbox.` (1), `Bind mount the host path` (3),
   `It works by creating a new, completely empty, filesystem namespace where the root` (1),
   `is on a tmpfs that is invisible from the host, and which will be automatically` (1).
   `grep -c '|' src-S230.html` → 0 (no pipe character in the fetched bytes).
6. Screened candidate: `…/bubblewrap/main/README.md` → HTTP 200, 10 687 bytes,
   sha256 `0c1dc12c6d94017c45e220fc0e5b679f24c0f09494bdd4bc7157d8abcd75c001`; only `--ro-bind`
   hit is example line `:111`; no flag semantics → not used as the row's source page.

## Findings

1. **Man page source, not README, is the only page that states the flag semantics.**
   `bwrap.xml` at tag v0.13.1 `:295-296` (`--bind … Bind mount the host path SRC on DEST`) and
   `:311-312` (`--ro-bind … readonly`). The README documents the flags only inside an example
   (`README.md:111`).
2. **The "host destination untouched" half of the assignment's teaching is not a sentence in the
   source.** The bytes state a per-sandbox mount namespace (`:56`) and a filesystem namespace
   invisible from the host (`:49-50`); the host path being unaffected is the consequence, so the
   drafted row's `teaches` cell records the consequence explicitly and does not claim the page says
   it. Treated as `[INFERENCE]` in `deliver-s230-row.md`.
3. **S230 is free as a registry id but not unmentioned in the lane's history.**
   `corpus/lessons/round-24.md:207` ("staged S230 is a different URL"), the round-31 wave-1/wave-2
   lesson deliveries (a merge package's S226–S230), and
   `census/round-32/waves/w1/deliver-assim-sweep.md` (that package's S230 = git-worktree 2.56.0)
   all name S230; none appended a row. Disclosed in the delivery file so the id is not read as a
   reuse — same situation the round-33 provenance paragraph recorded for S224.
4. **Version alignment.** Host `bubblewrap 0.13.1` equals the fetched tag, so the row's `recheck`
   scope (`180d`) has a version-bounded meaning rather than a floating `main` line.

## Deliveries

- `.ufo/waves/round-34/w1/deliver-s230-row.md` — registry row (11 cells, append after `S229`),
  `## Gate` entry in the round-33 shape, optional provenance sentence, fetch + collision receipts.
- `.ufo/waves/round-34/w1/src-S230.html` — the fetched bytes (33 289 bytes, sha256 `2cb77df2…be1da`), saved per the seat spec; not committed by me.
- `.ufo/waves/round-34/w1/SwarmScribe33.md` — this report.

## Scope and cleanliness

- Wrote only the three paths above, all inside `<lane>/.ufo/waves/round-34/w1/`. No `git add/commit/
  push/stash/checkout/reset/switch/pull`, no `jj` mutation, no delete/move, no signal.
- Scratch: `/fast/scratch/hyaku/souji-r34/SwarmScribe33/` (with `tmp/`), `TMPDIR` exported there;
  receipts copied into the delivery file first, then the directory was removed.
- Tooling: no install/upgrade; no `pacman` invocation. `curl`, `sha256sum`, `grep`, `bwrap` are host
  binaries already present.
- Not touched: any path outside the lane, `.scratch/`, `.ufo/state/`, `watchdog.log`,
  `MANIFEST.json`, fleet scripts/templates, sibling lanes, `/home/vgpnk/Projects/shokuknow`.
- Certification OFF, K5 HELD observed: no credentials, no live `/proc` census, no
  `census/operator-sweep-*` or `.scratch/` contents read. No contract, counter, item or leg
  proposed for change.
