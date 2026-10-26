## Status

STATUS: PASS — four git v2.56.0 doc snapshots pinned byte-exact under `.ufo/waves/round-32/w1/sources/`, `SHA256SUMS` and the six-column fetch-receipt TSV written and re-verified against the blobs, and fourteen Gate-safe quotes located for the four requested C3 facts. No counter was run (not this seat's item).

## Evidence

Revision context: lane worktree HEAD `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1` (controls) on base `85b61a151923986e7e6b48f7084b9122561b5f3d`; prereg `3ec84fc81b3243429c834a051880b0bcde06291c`. Fetched over the network, so the pinned bytes are upstream `git/git` at tag `v2.56.0`, not lane bytes.

```
$ curl -fsSL -m 60 -o <snap> -w '%{http_code}\t%{size_download}\n' <url>
rc=0 file=gitformat-pack.adoc code=200	27494
rc=0 file=git-gc.adoc        code=200	6744
rc=0 file=gc.adoc            code=200	7753
rc=0 file=git-repack.adoc    code=200	15015
```

```
$ cd .ufo/waves/round-32/w1/sources && sha256sum gitformat-pack.adoc git-gc.adoc gc.adoc git-repack.adoc > SHA256SUMS && sha256sum -c SHA256SUMS
gitformat-pack.adoc: OK
git-gc.adoc: OK
gc.adoc: OK
git-repack.adoc: OK
```

Byte-exactness re-check (second fetch to `/fast/scratch/hyaku/souji-r32/SwarmExecutor19/recheck`, then `cmp -s`): `BYTE-EXACT` for all four. Scratch dir removed.

Receipt/blob agreement, read the way `c3-counter.py:206-223` reads it (`f[1]`=http, `f[4]`=sha256, `f[5]`=snapshot; `sums` keyed by `os.path.basename(snapshot)`):

```
SHA256SUMS keys: ['gc.adoc', 'git-gc.adoc', 'git-repack.adoc', 'gitformat-pack.adoc']
header: url<TAB>http<TAB>fetched_at<TAB>bytes<TAB>sha256<TAB>snapshot
OK   6 200 27494 bytes census/round-32/sources/gitformat-pack.adoc ec285ba4f4e15a68
OK   6 200  6744 bytes census/round-32/sources/git-gc.adoc        e3dbc4081095faf8
OK   6 200  7753 bytes census/round-32/sources/gc.adoc            0ab75f6f40ebdbda
OK   6 200 15015 bytes census/round-32/sources/git-repack.adoc     474d4147f1390401
```

Quote verification: a `python3 -B` pass flattened whitespace in each snapshot and asserted each candidate quote is a contiguous substring, 4–25 words, no `|`, no `"`. All fourteen: `FOUND`, `pipe=False`, `dquote=False`; word counts 4,5,6,12,12,14,14,14,16,16,17,18,20,21,24.

Corroboration: `census/round-30/sources/git-gc.adoc` hashes to `e3dbc408…beafba8c`, identical to this round's pin, so the digest reproduces across rounds.

## Findings

1. **Cruft packs carry the per-object clock in a `.mtimes` sidecar.** `census/round-32/sources/gitformat-pack.adoc:659` and `:674-675`; the format table is `:341-354` and the sidecar is listed at `:14`. The per-object, not per-pack, clock is stated at `:635-636`.
2. **`gc.pruneExpire` defaults to `2.weeks.ago`, and `git gc` drives both `prune --expire` and `repack --cruft --cruft-expiration`.** `census/round-32/sources/gc.adoc:96-99`; the command-level default is `git-gc.adoc:82-83`; `--cruft-expiration` itself is `git-repack.adoc:75-77`.
3. **`gc.cruftPacks` defaults to `true`, and `false` means loose objects — that clause is the entire documented effect.** `census/round-32/sources/gc.adoc:85-88` ("instead of as loose objects", "The default is `true`."); mirrored at `git-gc.adoc:61-65`. There is no separate prose line for `false`; `--no-prune` (`git-gc.adoc:89-90`) is a different control and must not be cited for it.
4. **An unreachable object younger than the expiry is a traversal tip and is kept.** `census/round-32/sources/gitformat-pack.adoc:667-669` (grace period read off the object's own mtime); the cruft destination is `git-gc.adoc:63-65`; removal of expired objects is `gitformat-pack.adoc:688`.
5. **Gate-span nesting hazard for the `never`/`now` values.** `gc.adoc:100-102` spells both values with the doc's own double quotes, and `c3-counter.py:224` captures Gate quotes with `re.findall(r'"([^"]{2,400})"', gate)`, so the full lines cannot sit inside a `"…"` span. `deliver-c3-anchor-lines.md` therefore supplies two verbatim sub-spans cut around the inner quotes (`gc.adoc:101` and `:102`) plus the full lines in a fenced block.
6. **L4 needs the snapshot path spelled identically in two places.** `c3-counter.py:206` keys `SHA256SUMS` by `os.path.basename(sp)`; `:211-214` looks the receipt up by the full `snapshot` token taken from column 6 and compares the committed blob's sha256 and the literal `200` at `:216-223`. Receipts here carry `census/round-32/sources/<basename>` and http `200`; the blobs are 6744–27494 bytes, all above the 512-byte floor in the same leg.
7. **L6 owes rows this seat cannot open.** `c3-counter.py:227-232` requires every `source:` line's `S###` id to exist in `corpus/SOURCES.md` as a row dated `2026-10-26` with the URL in its cell. `deliver-c3-anchor-lines.md` supplies URLs and quotes, but opening the registry row is the entry author's write.

## Attack log

Not an attack seat; no counter predicate was probed. Finding 5 is a mechanical constraint of the frozen L5 regex, not a counter defect — the regex forces quote-free spans, which the sources permit.

## Deliveries

- `.ufo/waves/round-32/w1/sources/gitformat-pack.adoc` — 27494 B, sha256 `ec285ba4f4e15a68ad83a570eaf74e8549b477496e49933126ef935d9291381b`
- `.ufo/waves/round-32/w1/sources/git-gc.adoc` — 6744 B, sha256 `e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c`
- `.ufo/waves/round-32/w1/sources/gc.adoc` — 7753 B, sha256 `0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a`
- `.ufo/waves/round-32/w1/sources/git-repack.adoc` — 15015 B, sha256 `474d4147f1390401f38e07a7c5950f21d6d402212984e1f7d98dd6c71da460f6`
- `.ufo/waves/round-32/w1/sources/SHA256SUMS` — basenames, `sha256sum -c` clean
- `.ufo/waves/round-32/w1/deliver-fetch-receipts.tsv` — header plus four rows, verified field-by-field
- `.ufo/waves/round-32/w1/deliver-c3-anchor-lines.md` — location + word-counted quotes per fact, plus the L4/L5/L6 integration notes

Integration handoff for the L1: the four `.adoc` files and `SHA256SUMS` must land at `census/round-32/sources/`, and `deliver-fetch-receipts.tsv` at `census/round-32/records/fetch-receipts.tsv`, before the C3 counter can read them (`c3-counter.py:206,211`). No tools were installed; no lane file outside `w1/` was written; scratch removed.
