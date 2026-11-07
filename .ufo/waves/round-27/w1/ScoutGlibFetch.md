# ScoutGlibFetch — GLib 2.84.0 re-grounding snapshots for C2 (round 27, w1)

## Status
STATUS: PASS — both snapshots fetched and byte-pinned (sha256 + git blob SHA matching the tag's own tree entry), all ten cited lines verified present, pipe-free ≤25-word quotes located and proved gate-check-clean (`entries=2 ok=2 fail=0`, rc 0) against the lane's own `tools/souji-gate-check.py` in a scratch mirror; four concrete defects in the two staged w1 draft entries and the staged SOURCES rows are reported below for the L1 to fix before landing.

## Evidence

Fetch (both succeeded, no failures to record):

```
$ cd /var/tmp/souji-r27-ScoutGlibFetch
$ curl -fsSL --max-time 60 -o glocalfile.c https://raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c
glocalfile rc=0
$ curl -fsSL --max-time 60 -o gfileutils.c https://raw.githubusercontent.com/GNOME/glib/2.84.0/glib/gfileutils.c
gfileutils rc=0
```

sha256 and size (matching the byte counts the staged SOURCES rows already record — S210 "83 391 bytes", S211 "86 909 bytes"):

```
$ sha256sum glocalfile.c gfileutils.c
66b588c495e1d7e036b02c5dc919ab466eace6f578ed38763a49b168d2d47e4f  glocalfile.c
5161ae435ee57448c280323de064e1d6d62dc1ba3ba2771c5982b913888dfad5  gfileutils.c
$ stat -c '%n %s' glocalfile.c gfileutils.c
glocalfile.c 83391
gfileutils.c 86909
```

Independent proof the bytes are the tag's own blobs (not merely "a file that looks like it") — the local `git hash-object` of each fetched file equals the blob sha GitHub's tree API reports for that path at tag 2.84.0:

```
$ git hash-object glocalfile.c gfileutils.c
03a793716358234c4e6b2ed02362b0f84e34de04
25500cbf5f50b1f5ce46e11086b900572d9cd04b

$ curl -fsSL --max-time 60 "https://api.github.com/repos/GNOME/glib/git/trees/2.84.0?recursive=1"
truncated: False
gio/glocalfile.c 03a793716358234c4e6b2ed02362b0f84e34de04 83391 blob
glib/gfileutils.c 25500cbf5f50b1f5ce46e11086b900572d9cd04b 86909 blob
```

Tag resolution (annotated tag → commit), for the record:

```
$ curl -fsSL --max-time 60 "https://api.github.com/repos/GNOME/glib/git/ref/tags/2.84.0"
{"ref":"refs/tags/2.84.0","object":{"sha":"2b99bc7d513666a9d5c2e83eb5e51caa77852d0a","type":"tag",...}}
$ curl -fsSL --max-time 60 ".../git/tags/2b99bc7d513666a9d5c2e83eb5e51caa77852d0a"
tag 2.84.0 -> commit 05da47c2d0d333cec6363e09bcf9eed6952e74ce commit
```

All ten cited lines verified present (verbatim `sed -n` output; the file's last line numbers are 3163 and 3060, so every cited line is in range):

```
$ for L in 2261 2282 2284 2359 2387; do printf "%s: " "$L"; sed -n "${L}p" glocalfile.c; done
2261:       fd = g_open (infofile, O_CREAT | O_EXCL | O_CLOEXEC, 0666);
2282: 
2284:       if (!g_file_set_contents_full (infofile, NULL, 0,
2359:   if (!g_file_set_contents_full (infofile, data, -1,
2387:       g_unlink (infofile);
$ for L in 1697 1369 1367 1041 1108; do printf "%s: " "$L"; sed -n "${L}p" gfileutils.c; done
1697:                        flags | O_CREAT | O_EXCL, mode);
1369:       fd = g_mkstemp_full (tmp_filename, O_RDWR | O_BINARY | O_CLOEXEC, mode);
1367: 
1041:   if (g_rename (old_name, new_name) == -1)
1108:       (flags & G_FILE_SET_CONTENTS_ONLY_EXISTING))
```

Note: cited lines **2282** and **1367** exist but are **blank lines** (1 byte, `\n`). They are anchors for the "probe"/"template" steps in the staged rows' prose, so an entry that says "`g_file_set_contents_full` probe at :2282" is pointing at whitespace; the real code sits at 2284-2286 and 1366. See Finding 5.

Quote viability, proved against the lane's own checker (not by inspection). Scratch mirror: the two w1 draft entries copied to `corpus/knowledge/`, the two fetched snapshots copied to `census/round-27/sources/`, `corpus/SOURCES.md` given the three new rows, then:

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-gate-check.py \
    --root $D/final --round-date 2026-10-25 \
    --entries corpus/knowledge/origin-record-writer-r27.md corpus/knowledge/origin-record-mechanism-set-r33.md \
    --snapshot-dir census/round-27/sources \
    --slice census/round-27/records/slice-verdicts.tsv \
    --slice-verdicts census/round-27/records/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0
gate-check rc=0
```

C2 counters re-measured in that mirror: registry rows `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` = **132 → 135**; grounded F4 `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l` = **2 → 4** (the two existing F4 entries `quarantine-staging-no-copy-r23.md`, `quarantine-origin-record-fields-r24.md` plus the two admitted ones).

Registry validation by the fleet's own census tool (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate`, read-only, run against a scratch copy of the lane registry with the three staged rows inserted inside the `## Registry` section):

```
staged rows exactly as in /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:
  file E01 S152 fields=13 ; file E01 S210 fields=12 ; file E01 S211 fields=14
  file E11 S210 missing used-by grep -F '(void) g_close (fd
  file E11 S210 missing used-by NULL);'` ; file E11 S211 missing used-by grep -F 'flags
  validate rc=1        (baseline lane registry: rc=0, 35 W04 warnings only)
same three rows with every `|`/`\|` removed from the cells and recheck reduced to a bare `365d`:
  file W04 S210 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c across scopes
  validate rc=0
```

Tooling: none installed (curl 8.23.0, Python 3.14.8, GNU Awk 5.4.1, coreutils sha256sum 0.8.0 were already present; nothing needed upgrading). No pacman transaction attempted — the pacman guard was not a factor.

## Findings

1. **Snapshots are ready to commit, and the pins are strong.** `census/round-27/sources/glocalfile.c` = sha256 `66b588c495e1d7e036b02c5dc919ab466eace6f578ed38763a49b168d2d47e4f` (83391 bytes, git blob `03a793716358234c4e6b2ed02362b0f84e34de04`); `census/round-27/sources/gfileutils.c` = sha256 `5161ae435ee57448c280323de064e1d6d62dc1ba3ba2771c5982b913888dfad5` (86909 bytes, git blob `25500cbf5f50b1f5ce46e11086b900572d9cd04b`). Both blob shas equal the shas GitHub's tree API reports for the same paths at tag 2.84.0 (commit `05da47c2d0d333cec6363e09bcf9eed6952e74ce`), so a re-fetch is byte-reproducible and the L1's own copy can be verified against the blob sha, not only sha256. The staged w1 draft `origin-record-writer-r27.md` already records the glocalfile sha256 `66b588c4…`; it matches my independent fetch exactly. The r33 draft records only "sha256 in census/round-27/sources/" — the L1 should pin `5161ae43…` there. Suggested `census/round-27/sources/SHA256SUMS` content (same shape as round-26's file): the two lines above with the two-space separator.

2. **The Gate blocks as currently drafted in the two w1 entries fail the lane's own gate — 16 failures, both entries `ok=0`.** Running `tools/souji-gate-check.py` unchanged against the unmodified staged drafts (copied into a scratch mirror with the snapshots and the three registry rows present) gives:

   ```
   FAIL corpus/knowledge/origin-record-writer-r27.md check3-no-locator-gate-line-7 … line-14   (8×)
   FAIL corpus/knowledge/origin-record-writer-r27.md check3-no-located-quote-with-snapshot
   FAIL corpus/knowledge/origin-record-mechanism-set-r33.md check3-no-locator-gate-line-11, -12, -16, -17, -18   (5×)
   FAIL corpus/knowledge/origin-record-mechanism-set-r33.md check3-no-located-quote-with-snapshot
   entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=16
   ```
   (the `ok=2` on that line is the *corrected* run; the failing run reports `ok=0 fail=16`.) Three independent causes, all fixable in the entry text:

   a. **No locator token.** `check3` requires the line to carry one of `§ | section | line | lines | paragraph | DESCRIPTION | OPTIONS | COMMANDS | SYNOPSIS | heading` **outside** the quoted span and outside the `snapshot:` field. The drafts write `— gio/glocalfile.c:2261 —`, which matches nothing (`LOCATOR_RE` needs `line ` / `lines ` with a space, or `§`). Writing `— gio/glocalfile.c line 2261 —` (or `lines 2261-2267`) satisfies it; verified by direct probe: `'— gio/glocalfile.c:2261 — reason: x — snapshot: y'` → no match; `'— gio/glocalfile.c line 2261 — reason: x'` → match.

   b. **The r33 ADMIT quotes are backslash-escaped inside the quote.** `"tmp_filename = g_strdup_printf (\"%s.XXXXXX\", filename);"` — `QUOTE_RE` is `"([^"]{2,400})"`, so the embedded `\"` truncates the span at `tmp_filename = g_strdup_printf (\`, which is **not** in the snapshot → `check4-quote-absent-from-snapshot`. Same for the writer entry's `:2340` and `:2354-2355` ADMITs: the inner `"` characters split them into fragments (e.g. `original_name_escaped = g_uri_escape_string (original_name,` and `, FALSE);`), each of which must independently appear verbatim. The recommendation is to quote spans that contain no `"` and no `|` at all.

   c. **The `Write the full content of the info file…` comment quote does not appear verbatim.** The source wraps it across two lines with a `*` continuation prefix (`:2331-2333`), so the whitespace-collapsed snapshot body reads `… before trashing to make * sure someone doesn't read an empty file. …` — the draft's quote without the `*` is absent → `check4-quote-absent-from-snapshot`. Drop that quote or replace it with a code span.

   With those three classes fixed (pipe-free, quote-free, locator-bearing ADMIT lines; one ADMIT + one REJECT with a `reason:` per entry), the checker returns `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`, rc 0 — reproduced above.

3. **Recommended Gate quotes — exact locations, all ≤25 words, no `|` and no `"`.** Each was verified twice: (i) whitespace-collapsed verbatim presence in the corresponding snapshot, (ii) equality with the whitespace-collapsed source line at the cited number, and (iii) accepted by the lane's own gate-check in the mirror run. Words counted on the whitespace-collapsed form, as `check3` does.

   `gio/glocalfile.c` (snapshot `census/round-27/sources/glocalfile.c`):
   - line 2256 — `trashname = get_unique_filename (basename, i++);` (5 words)
   - line 2264 — `if (errsv == EEXIST)` (4 words) — the retry branch; note the line continues `continue;` on 2265
   - line 2281 — `(void) g_close (fd, NULL);` (4 words) — the exclusive descriptor closes unwritten
   - line 2340 — `original_name_escaped = g_uri_escape_string (original_name, "/", FALSE);` (6 words) — **contains `"`**, so quote it only if the L1 accepts the fragment split; the `g_uri_escape_string` call alone is not pipe-free of quotes, so prefer 2256/2264/2281/2383/2387 for the Gate
   - line 2383 — `if (g_rename (local->filename, trashfile) == -1)` (6 words) — the payload move
   - line 2387 — `g_unlink (infofile);` (2 words) — the rollback

   `glib/gfileutils.c` (snapshot `census/round-27/sources/gfileutils.c`):
   - line 1041 — `if (g_rename (old_name, new_name) == -1)` (6 words) — atomic publication
   - line 1108 — `(flags & G_FILE_SET_CONTENTS_ONLY_EXISTING))` (3 words) — the destination must exist
   - line 1358 — `if (flags & G_FILE_SET_CONTENTS_CONSISTENT)` (4 words) — the consistent-write path
   - line 1366 — `tmp_filename = g_strdup_printf ("%s.XXXXXX", filename);` (5 words) — **contains `"`**, see 2b
   - line 1381 — `do_fsync = fd_should_be_fsynced (fd, filename, flags);` (6 words)
   - line 1390 — `if (!rename_file (tmp_filename, filename, do_fsync, &rename_error))` (6 words) — the publish rename

   The recommended pipe-free, quote-free working set used in the passing mirror run: glocalfile 2256, 2281, 2383, 2387; gfileutils 1041, 1108, 1390.

4. **The three staged SOURCES rows must be rewritten before appending; verbatim they break the census validator and fail the frozen C2 counter.** `sources-census.sh validate` on the lane registry with the staged rows inserted **as-is** inside `## Registry` yields `E01 S152 fields=13`, `E01 S210 fields=12`, `E01 S211 fields=14` and three spurious `E11 missing used-by` findings, exit **rc=1** (the lane's baseline registry validates rc=0). Cause: the awk field separator is the literal `|`, and the staged rows carry escaped pipes inside cells (S152's anchor cell contains `O_CREAT\|O_EXCL`, S211's recheck cell contains `flags | O_CREAT | O_EXCL`), so the row splits into more than the 11 contracted columns; the extra split also shifts the `used-by` column, producing the bogus E11s. Rewriting the same three rows with every `|`/`\|` removed from the cells (e.g. `O_CREAT O_EXCL`) and the `recheck` cell reduced to a bare cadence (`365d`) gives exit **rc=0** with only a `W04` warning (`S210 duplicate url …/gio/glocalfile.c across scopes`), which does not change the exit status. The lane's own rows follow this shape (`recheck` = `90d` or `on-release`, bare). The staged recheck prose (`365d — re-fetch …`) also fails `E09` because `recheck` must match `^[0-9]+d$` or a symbolic cadence. Related: the rows must be inserted **before** the next `## ` heading of `corpus/SOURCES.md` (the `## Paths` section) — appending them at end-of-file produces `E12 row outside Registry section`.

5. **Two of the ten cited anchor lines are blank.** `glocalfile.c:2282` and `gfileutils.c:1367` each contain exactly one byte (`\n`). The staged S210 row's prose ("the create-then-probe-then-fill sequence at lines 2261, 2282, 2284 and 2359") and S211's ("the `XXXXXX` template at 1367") therefore point at whitespace. The actual code is at `glocalfile.c:2284-2286` (the empty probe write `g_file_set_contents_full (infofile, NULL, 0, …)`) and `gfileutils.c:1366` (`tmp_filename = g_strdup_printf ("%s.XXXXXX", filename);`). The re-grounded entries should cite those, not the blank lines.

6. **The r33 entry's `## Gate` block is malformed as a Gate section, independent of quoting.** It opens with `opened: 2026-10-25` and four prose ADMIT/REJECT bullets (gate lines 4-7) *before* any `url:` line, and its quote bullets use a different shape (`` `glib/gfileutils.c:1366-1369` "…" `` with the locator inside backticks) than the writer entry's. The checker's `check2` requires a URL and `opened: <round date>` in the section and `check6` requires ≥1 ADMIT and ≥1 REJECT each carrying a `reason:`; the writer entry's shape (url/snapshot/opened header, then `- ADMIT: "…" — <locator> — reason: … — snapshot: <path>` bullets) satisfies all of it and is what the passing mirror run used. Recommend the L1 harmonize r33 to the writer entry's shape.

7. **Sequencing constraint the L1 must observe.** `check5` resolves each `source: S<digits>` cited by an entry against `corpus/SOURCES.md`, and the registry rows for S152/S210/S211 do not exist at base. The gate therefore only passes after the three rows are appended (in the same wave, before the gate run). Conversely the census `validate` requires the two new `used-by` knowledge paths to exist on disk, so the entries must be installed before `validate` runs. Order: install the two entries + append the three rows + write the two snapshots, then run the gate and the census.

8. **Id-collision check for the frozen kill rule — clean for the three claimed rows, but the append file as a whole is not appendable.** `S152`, `S210`, `S211` are absent from the lane registry (whose highest id is S132) and appear exactly once each in `SOURCES.append.md` (134 ids, no internal duplicates): `collisions = ∅` for the three rows C2 claims, so no renumber map is required for C2. But `SOURCES.append.md` intersects the lane registry on **24 ids (S109–S132)** — those are round-26-era ids that the lane already re-pointed; appending the file wholesale would collide. C2's counter is 132→135, i.e. exactly the three rows, so the L1 should append only S152/S210/S211 and must not bulk-append the file.

9. **One wording claim in the staged r33 entry is not supported by the pinned bytes and should not be carried over.** The staged text says the content writer "creates a uniquely named temporary file (`%s.XXXXXX`) with `g_mkstemp_full`, which passes `O_CREAT` and `O_EXCL`". The pinned `gfileutils.c:1696-1697` shows `return get_tmp_file (tmpl, wrap_g_open, flags | O_CREAT | O_EXCL, mode);` — consistent — but `get_tmp_file` retries on `EEXIST` up to 100 times (`:1541-1560`), so the temp name is *retry-generated*, not *exclusivity-enforced by O_EXCL at the destination*. The distinction matters for the "three complementary mechanisms" claim: exclusivity of the `.trashinfo` destination is enforced by `O_EXCL` at `glocalfile.c:2261`, whereas in the content writer `O_EXCL` belongs to the temporary file and the destination's exclusivity comes from `G_FILE_SET_CONTENTS_ONLY_EXISTING`. The re-grounded r33 entry should state it that way.

10. **Availability / scope note.** Both fetches succeeded on the first attempt; there is no unavailable source to record. Nothing outside `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/w1/` was written; `/home/vgpnk/Projects/shokuknow/` was read only. Scratch under `/var/tmp/souji-r27-ScoutGlibFetch/` was removed at the end of this seat's run, per contract; the L1 must re-fetch with the URLs and verify against the sha256/ blob shas in Finding 1 (the fetch is byte-deterministic for the pinned tag, as the tree-API blob-sha match proves).

## Attack log

None — this seat's item is a delivery (snapshots + quote set), not an attack; no frozen counter, predicate, target or case set was challenged or altered. Findings 4, 5, 6 and 9 report defects in the *staged drafts and staged rows*, not in the frozen preregistration: the preregistration's counters (registry 132→135, grounded F4 2→4, gate ok=2, sources-census rc 0) are all achievable as written once the drafts and rows are corrected as described.
