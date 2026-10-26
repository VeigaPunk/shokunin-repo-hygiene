# C3 source anchors — git v2.56.0 docs (jj abandoned-object mtime clock)

Pinned snapshots: `census/round-32/sources/{gitformat-pack,git-gc,gc,git-repack}.adoc`
(staged here in `.ufo/waves/round-32/w1/sources/` for the L1 to move under `census/round-32/sources/`).
`SHA256SUMS` is `sha256sum` format with basenames; `deliver-fetch-receipts.tsv` carries the http/bytes/digest rows.

Every quote below is a contiguous span of the cited bytes, verified present after whitespace reflow, 4–25 words,
and contains no `|` and no `"` (so it can be pasted inside a Gate `"…"` span). Line numbers are 1-based on the snapshots.

## F1 — cruft pack carries per-object mtimes in `.mtimes`

- `census/round-32/sources/gitformat-pack.adoc:659`
  "A cruft pack is written by `git repack --cruft` when generating a new pack." (14 words)
- `census/round-32/sources/gitformat-pack.adoc:674-675`
  "Write the pack out, along with a `.mtimes` file that records the per-object timestamps." (14 words)
- `census/round-32/sources/gitformat-pack.adoc:351-354` (`.mtimes` format table)
  "The ith value is the modification time (mtime) of the ith object in the corresponding pack by lexicographic (index) order." (20 words)
- Location only, no quotable span (single token line): `census/round-32/sources/gitformat-pack.adoc:14`
  lists `$GIT_DIR/objects/pack/pack-*.mtimes` among the pack sidecars; the section heading
  `== pack-*.mtimes files have the format:` is at line 341.

Full verbatim source lines 655-657 (definition sentence, 31 words — too long for a Gate span, use the 659 pair above):
```
A cruft pack eliminates the need for storing unreachable objects in a loose
state by including the per-object mtimes in a separate file alongside a single
pack containing all loose objects.
```

## F1 — `gc.pruneExpire` default two weeks, and `never` / `now`

- `census/round-32/sources/git-gc.adoc:82-83`
  "Prune loose objects older than date (default is 2 weeks ago, overridable by the config variable `gc.pruneExpire`)." (17 words)
- `census/round-32/sources/gc.adoc:97-99`
  "When 'git gc' is run, it will call 'prune --expire 2.weeks.ago' (and 'repack --cruft --cruft-expiration 2.weeks.ago' if using cruft packs via `gc.cruftPacks` or `--cruft`)." (24 words)
- `census/round-32/sources/gc.adoc:101` — `now` (sub-span; see hazard note)
  "used to disable this grace period and always prune unreachable objects immediately" (12 words)
- `census/round-32/sources/gc.adoc:102` — `never` (sub-span; see hazard note)
  "may be used to suppress pruning" (6 words)
- `census/round-32/sources/git-repack.adoc:76-77` (`--cruft-expiration`)
  "Expire unreachable objects older than `<approxidate>` immediately instead of waiting for the next `git gc` invocation." (16 words)

**Nesting hazard.** The doc spells the two values with its own double quotes, so the full lines cannot sit inside a
Gate `"…"` span. Full verbatim lines 100-102:
```
	grace period with this config variable.  The value "now" may be
	used to disable this grace period and always prune unreachable
	objects immediately, or "never" may be used to suppress pruning.
```
The two sub-spans above were cut to avoid the inner quotes; both stay verbatim and contiguous.

## F1 — `gc.cruftPacks` default `true`, and `false` ⇒ loose objects

- `census/round-32/sources/gc.adoc:86-87`
  "Store unreachable objects in a cruft pack (see linkgit:git-repack[1]) instead of as loose objects." (14 words)
- `census/round-32/sources/gc.adoc:87-88`
  "The default is `true`." (4 words — at the Gate minimum, keep it a separate span)
- Command-level mirror, `census/round-32/sources/git-gc.adoc:63-65`
  "When expiring unreachable objects, pack them separately into a cruft pack instead of storing them as loose objects." (18 words)
- `census/round-32/sources/git-gc.adoc:64-65`
  "`--cruft` is on by default." (5 words)

`false`/`--no-cruft` has no dedicated prose line: the "instead of as loose objects" / "instead of storing them as loose
objects" clauses above are the whole statement of what disabling it does. `--no-prune` (`git-gc.adoc:89-90`,
"Do not prune any loose objects.") is a different control and must not be cited for `gc.cruftPacks=false`.

## F1 — how `git gc` treats unreachable objects younger than the expiry

- `census/round-32/sources/gitformat-pack.adoc:668` — the grace window is per-object, from the object's own mtime
  "(b) whose mtime is within the grace period as a traversal tip" (12 words)
- `census/round-32/sources/gitformat-pack.adoc:683-686` — expired ones only leave when repack is told to expire them
  "which allows the generated cruft pack to omit expired objects instead of waiting for linkgit:git-gc[1] to expire those objects later on." (21 words)
- `census/round-32/sources/gitformat-pack.adoc:688` — who removes expired unreachable objects, location only (no quote needed):
  `It is linkgit:git-gc[1] that is typically responsible for removing expired unreachable objects.`

Why the clock has to be per-object and not the pack file's mtime —
`census/round-32/sources/gitformat-pack.adoc:635-636`:
"Git must store these unreachable objects loose in order to keep track of their per-object mtimes." (16 words)

Read together: an unreachable object younger than the expiry is a traversal tip, so it is kept — in the cruft pack with
`gc.cruftPacks` true (its own mtime written into `.mtimes` by the `git repack --cruft` that `git gc` calls, per
`gc.adoc:97-99`), loose otherwise. The expiry test is therefore already on the object's own mtime at the moment it enters
the pack.

## Integration contract used (from `census/round-32/c3-counter.py`)

- L4 keys `SHA256SUMS` by `os.path.basename(snapshot)` — basenames are correct, do not switch to full paths.
- L4 looks up the receipt row by the snapshot string exactly as the entry's `snapshot:` token reads it, requires
  column 2 to be the literal `200` and column 5 to equal the sha256 of the committed blob; every pinned file must be
  ≥ 512 bytes (all four are: 27494 / 6744 / 7753 / 15015).
- L5 requires each Gate `"…"` span to be 4–25 words; L6 additionally requires the entry's `source:` rows to name
  `corpus/SOURCES.md` entries opened 2026-10-26 — that is the entry author's row to open, not delivered here.

## Verified fetch evidence

```
$ sha256sum gitformat-pack.adoc git-gc.adoc gc.adoc git-repack.adoc > SHA256SUMS && sha256sum -c SHA256SUMS
gitformat-pack.adoc: OK
git-gc.adoc: OK
gc.adoc: OK
git-repack.adoc: OK
```

Re-fetched all four to scratch and compared byte-for-byte on 2026-10-26: `cmp -s` reported BYTE-EXACT for each.
`git-gc.adoc` also matches the blob already landed in `census/round-30/sources/git-gc.adoc`
(sha256 `e3dbc408…beafba8c`), so the digest is reproducible across rounds.
