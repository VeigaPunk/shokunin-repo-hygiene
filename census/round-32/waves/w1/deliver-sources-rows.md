# deliver-sources-rows — r32 C3 SOURCES rows (S223/S224, conditional S225)

Seat `SwarmScribe23-3` (item `ScribeSourcesRows`, lane souji). Read-only seat: this file and its
report are the only lane writes. Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d` (master),
preregistration `3ec84fc81b3243429c834a051880b0bcde06291c`. Both sources were opened by this seat
on 2026-10-26 from the raw tag URLs below; every quote here is a contiguous span of the bytes this
seat fetched, contains no `|`, and is 14 to 19 words.

Target: two rows appended after the registry's last row `S222` (`corpus/SOURCES.md:167`). The table
is 11 columns (NF=13); ids are placeholders for the L1 to renumber by document, as with S223 in the
entry draft.

## 1. Rows to append (exact bytes; validated, see §6)

```
| S223 | git Documentation/gitformat-pack.adoc at tag v2.56.0 — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc | docs | A | the per-object mtime carrier a cruft pack uses at git 2.56.0: a pack-*.mtimes companion file whose ith 4-byte value is the mtime of the ith object in index order, and the cruft writer's rule that only objects within the grace period become traversal tips; not the gc side that selects the prune date or the cruft switch (S224), not `--cruft-expiration` on git-repack (S004), and not the reachability roots that keep objects alive (S063) | Documentation/gitformat-pack.adoc at tag v2.56.0, 704 lines: :12-14 SYNOPSIS pack-*.{pack,idx,rev,mtimes}; :341-358 pack-*.mtimes format table; :611-616 cruft packs section opening; :629-642 why loose storage tracked the per-object mtime; :653-675 Cruft packs steps 1-3; :682-689 --cruft-expiration; HTTP 200, 27494 bytes, sha256 ec285ba4f4e15a68ad83a570eaf74e8549b477496e49933126ef935d9291381b; snapshot census/round-32/sources/gitformat-pack.adoc; opened 2026-10-26 | the pack carries the clock per object instead of in its own mtime: "A cruft pack eliminates the need for storing unreachable objects in a loose state by including the per-object mtimes" (:655-656), and the table's ith value is that object's mtime in index order (:351-353) | mined | 2026-10-26 | on-release | corpus/knowledge/jj-abandoned-object-mtime-clock.md |
| S224 | git Documentation/git-gc.adoc at tag v2.56.0 — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc | docs | A | the gc-side cruft switch and prune date at git 2.56.0: expiring unreachable objects are packed into a cruft pack rather than left loose, `--cruft` is on by default and `--no-cruft` turns it off, `--expire-to` has no effect without `--cruft`, and `--prune=<date>` defaults to two weeks ago overridable by `gc.pruneExpire`; not the grace-period default values (S002), not the reachability roots (S063), not the pack-*.mtimes format (S223), and not the `gc.cruftPacks` key text, which this file only includes from Documentation/config/gc.adoc at :136 | Documentation/git-gc.adoc at tag v2.56.0, 187 lines: :61-65 --cruft and --no-cruft; :67-72 --max-cruft-size; :74-79 --expire-to; :81-87 --prune=<date> overridden by gc.pruneExpire; :131-136 CONFIGURATION section includes config/gc.adoc; `grep -Fc gc.cruftPacks` = 0, `grep -Fc cruft-expiration` = 0; HTTP 200, 6744 bytes, sha256 e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c; snapshot census/round-32/sources/git-gc.adoc; opened 2026-10-26 | gc expires unreachable objects into a cruft pack by default: "When expiring unreachable objects, pack them separately into a cruft pack instead of storing them as loose objects." (:63-64) and that option is on by default (:64-65) | mined | 2026-10-26 | on-release | corpus/knowledge/jj-abandoned-object-mtime-clock.md |
```

## 2. Located quote grounding each `teaches` cell

| row | quote (verbatim, ≤ 25 words) | words | location in the fetched bytes |
|---|---|---|---|
| S223 | A cruft pack eliminates the need for storing unreachable objects in a loose state by including the per-object mtimes | 19 | `Documentation/gitformat-pack.adoc` v2.56.0 :655-656 (§ Cruft packs) |
| S224 | When expiring unreachable objects, pack them separately into a cruft pack instead of storing them as loose objects. | 18 | `Documentation/git-gc.adoc` v2.56.0 :63-64 (§ OPTIONS --cruft) |
| S225 (conditional) | Store unreachable objects in a cruft pack (see linkgit:git-repack[1]) instead of as loose objects. | 14 | `Documentation/config/gc.adoc` v2.56.0 :86-87 (gc.cruftPacks) |

Secondary anchors the rows carry, same bytes: `.mtimes` table rule "The ith value is the
modification time (mtime) of the ith object in the corresponding pack by lexicographic (index)
order." (:351-353, 20 words) and the traversal-tip rule "whose mtime is within the grace period"
(:668). Each quote was re-checked by whitespace-reflowed substring search against the fetched file,
and each mapped to its exact first and last line by offset (not by eye).

## 3. S224 admissibility: does a held row already cover this behaviour?

**No held row's scope covers it; the row is admitted, and its URL does not duplicate any held URL.**

- `grep -Fc gc.cruftPacks` over `Documentation/git-gc.adoc` = **0**; `grep -Fc cruft-expiration` = **0**.
  git-gc.adoc reaches that text only through `include::config/gc.adoc[]` (:136). So S224 grounds
  the gc-side `--cruft`/`--no-cruft`/`--expire-to`/`--prune` bytes only, and its scope says so.
- A sweep of every registry row's scope cell for `cruft` returns **nothing**:
  `awk -F'|' '$2 ~ /^ S[0-9]/ {s=$6; if (s ~ /[Cc]ruft/) print $2": "$6}' corpus/SOURCES.md` → empty.
- The two rows the seat named are the git-scm web page and hold different scopes:
  - S002 scope: "git 2.55.0 grace periods on git's own deletions"; anchor "§ OPTIONS --prune, --expire-to;
    § AGGRESSIVE; § CONFIGURATION gc.reflogExpire, gc.reflogExpireUnreachable, gc.rerereResolved,
    gc.rerereUnresolved, gc.worktreePruneExpire; installed man page git 2.55.0-1". It does not cite
    `gc.cruftPacks` or `gc.pruneExpire`, and teaches the grace-period values only.
  - S063 scope: "which refs keep objects alive during gc; not jj's own gc"; teaches the root set and
    the prune-date consequence, not the cruft switch. Its anchor does reach
    `Documentation/config/gc.adoc` v2.56.0 lines 96-147, so the `gc.pruneExpire` prose at :96-105 sits
    inside a held **anchor** but outside that row's **scope and teaches** — the closest overlap found.
  - S004 scope is `--expire-to` on 2.55.0 / `--drop-filtered` on 2.56.0 for **git-repack**; its teaches
    names the repack option, not gc's cruft switch.
- URL: S223/S224 use raw tag URLs; the held rows use the served git-scm page. Different URL text, so
  the duplicate-URL refusal does not apply, and the validator raised no E04 (see §6).

## 4. `used-by` changes on held rows the entry cites (old -> new)

The entry draft's `source:` lines name S223, S063 and S002
(`.ufo/waves/round-32/w1/deliver-entry-jj-abandoned-object-mtime-clock.md:1-3`). Exactly those held
rows need the append; the canonical set is whatever the landed entry's `source:` lines name.

- **S063** old: `corpus/knowledge/jj-colocation-receipts.md, corpus/knowledge/jj-keep-ref-expiry.md, corpus/knowledge/jj-dropped-keep-object-lifetime.md`
  new: same plus `, corpus/knowledge/jj-abandoned-object-mtime-clock.md`
- **S002** old: `corpus/knowledge/git-grace-periods-and-expire-to.md, corpus/knowledge/jj-dropped-keep-object-lifetime.md`
  new: same plus `, corpus/knowledge/jj-abandoned-object-mtime-clock.md`
- S223/S224/S225 are new rows: no `used-by` change, their `used-by` cell already names the entry.
- If the L1 also adds the entry's other held citations (S004, S054, S117, S220, S222 are cited by the
  earlier F1 entry, not by this draft), apply the same one-name append to each row the landed
  `source:` lines actually name; do not append to rows the entry does not cite (W03/E11 hygiene).

## 5. Integration notes for the L1

1. **L6 URL binding.** The counter takes cited ids only from lines matching `source:` and requires
   every `https://` URL in the entry's `## Gate` to appear in a cited row's source cell. The draft's
   Gate labels the git-gc.adoc quotes (`:63-65`, `:65`, `:82-83`, `:84-85`, `:90`, `:160-161`) `S063` with
   `https://git-scm.com/docs/git-gc`; if they are relabelled `S224`, the Gate URL must become the raw
   `https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc` **and** S224 must be
   added to the `source:` front matter, or `url_unbound` fails. Binding every git-gc.adoc quote to
   S224 and leaving S063 for the NOTES reachability sentence (:141-151) keeps each row inside its own
   scope.
2. **Config-fragment provenance (finding, not a row in the seat's order).** The draft's Gate lines for
   `gc.cruftPacks` (:86-88) and `gc.pruneExpire` (:97-102) quote **`Documentation/config/gc.adoc`**
   bytes while naming `S002` and the git-scm page; S002's anchor does not include those lines, and
   S063's anchor covers :96-147 but its scope is reachability. Either admit the conditional S225 in §7
   (a row whose scope is exactly that fragment) or narrow those sentences. This is the r31 routed
   defect 2 (C3 entry traceability) in a new place.
3. **Snapshots.** The three snapshot paths the entry's Gate names are already staged by the C3 anchor
   seat and are byte-identical to this seat's independent fetch (`cmp -s`, all three): `gitformat-pack.adoc`
   27494 B / `ec285ba4…1381b`, `git-gc.adoc` 6744 B / `e3dbc408…beafba8c`, `gc.adoc` 7753 B /
   `0ab75f6f…042f1a`; receipts carry http 200, so L4's three conditions are satisfiable.
4. **E11.** Both new rows are `mined` with the entry as `used-by`, so the validator's used-by check
   requires `corpus/knowledge/jj-abandoned-object-mtime-clock.md` to exist in the same tree — it will
   at landing; in the scratch validation below a placeholder supplied that path.
5. Do not add a round-32 provenance paragraph in the registry here: the registry's round prose is the
   L1's append (precedent: the round-25 paragraph above the table).

## 6. Validation (required: exit 0)

Scratch copy of the registry at `/fast/scratch/hyaku/souji-r32/C3Rows/lane/corpus/SOURCES.md`
(rows inserted directly after `S222`, every other `used-by` target symlinked, the new entry path a
scratch-only placeholder). Command and full output:

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file /fast/scratch/hyaku/souji-r32/C3Rows/lane/corpus/SOURCES.md --today 2026-10-26
file	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
file	W04	S036 duplicate url git-scm.com/docs/git across scopes
file	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
file	W04	S049 duplicate url git-scm.com/docs/git across scopes
file	W04	S057 duplicate url git-scm.com/docs/git-config across scopes
file	W04	S058 duplicate url git-scm.com/docs/git-worktree across scopes
file	W04	S059 duplicate url git-scm.com/docs/gitattributes across scopes
file	W04	S063 duplicate url git-scm.com/docs/git-gc across scopes
file	W04	S065 duplicate url www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html across scopes
file	W04	S072 duplicate url www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html across scopes
file	W04	S073 duplicate url man7.org/linux/man-pages/man2/kill.2.html across scopes
file	W04	S075 duplicate url man7.org/linux/man-pages/man5/proc_pid_stat.5.html across scopes
file	W04	S076 duplicate url man7.org/linux/man-pages/man5/proc_pid_exe.5.html across scopes
file	W04	S077 duplicate url man7.org/linux/man-pages/man2/open.2.html across scopes
file	W04	S086 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
file	W04	S087 duplicate url man7.org/linux/man-pages/man5/proc_pid_wchan.5.html across scopes
file	W04	S088 duplicate url man7.org/linux/man-pages/man5/proc_pid_status.5.html across scopes
file	W04	S089 duplicate url git-scm.com/docs/git across scopes
file	W04	S090 duplicate url git-scm.com/docs/git-filter-branch across scopes
file	W04	S091 duplicate url git-scm.com/docs/git-rev-parse across scopes
file	W04	S092 duplicate url git-scm.com/docs/git-for-each-ref across scopes
file	W04	S093 duplicate url git-scm.com/docs/git-diff across scopes
file	W04	S094 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
file	W04	S095 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
file	W04	S096 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
file	W04	S097 duplicate url git-scm.com/docs/git-filter-branch across scopes
file	W04	S098 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
file	W04	S099 duplicate url git-scm.com/docs/git-rev-parse across scopes
file	W04	S106 duplicate url docs.python.org/3/library/json.html across scopes
file	W04	S108 duplicate url docs.python.org/3/builtins/exceptions.html across scopes
file	W04	S123 duplicate url git-scm.com/docs/git-worktree across scopes
file	W04	S124 duplicate url git-scm.com/docs/gitrepository-layout across scopes
file	W04	S125 duplicate url git-scm.com/docs/git across scopes
file	W04	S126 duplicate url git-scm.com/docs/git-worktree across scopes
file	W04	S210 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c across scopes
file	W04	S216 duplicate url man7.org/linux/man-pages/man2/statx.2.html across scopes
file	ok	/fast/scratch/hyaku/souji-r32/C3Rows/lane/corpus/SOURCES.md
EXIT=0
```

Counts: `E` = 0, `W` = 36. That is **identical to the untouched registry** (same command over a
pristine copy: `E` = 0, `W` = 36, exit 0), so neither row adds a finding; no `E04` (duplicate URL) and
no `E11` line names S223/S224. The rows validated above were then extracted from **this file's own
bytes** (the `| S2…` lines longer than 900 characters) and revalidated in a fresh scratch copy twice —
two rows and all three rows — with the same result each time: `E` = 0, `W` = 36, `file ok`, exit 0.

## 7. Conditional third row — admit ONLY if the entry keeps the config-fragment quotes

Not part of the seat's two-row order; offered because the entry's Gate quotes
`Documentation/config/gc.adoc` and no held row's scope holds that fragment (§5 note 2). Validated
together with S223/S224: same command, same 36 warnings, `ok`, exit 0.

```
| S225 | git Documentation/config/gc.adoc at tag v2.56.0 — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc | docs | A | the config fragment git-gc(1) includes at git 2.56.0 for the cruft switch and the single prune date: gc.cruftPacks default true stores unreachable objects in a cruft pack instead of loose, gc.pruneExpire moves the date both the loose prune and the cruft repack receive, and now and never are its sentinels; not the reachability roots (S063) and not the command-line options that carry the same date (S224) | Documentation/config/gc.adoc at tag v2.56.0, 181 lines: :85-89 gc.cruftPacks; :90-94 gc.maxCruftSize; :96-105 gc.pruneExpire; :140-153 gc.recentObjectsHook; included by Documentation/git-gc.adoc:136; HTTP 200, 7753 bytes, sha256 0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a; snapshot census/round-32/sources/gc.adoc; opened 2026-10-26 | cruft packs are the configured default and one variable dates both expiry calls: "Store unreachable objects in a cruft pack (see linkgit:git-repack[1]) instead of as loose objects." (:86-87) with the default stated true (:85-88) | mined | 2026-10-26 | on-release | corpus/knowledge/jj-abandoned-object-mtime-clock.md |
```

## 8. How these rows were opened (provenance)

```
$ git --version
git version 2.56.0
$ curl -sS -o gitformat-pack.adoc -w '%{http_code}' https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc
200   bytes=27494  sha256=ec285ba4f4e15a68ad83a570eaf74e8549b477496e49933126ef935d9291381b  lines=704
$ curl -sS -o git-gc.adoc -w '%{http_code}' https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc
200   bytes=6744   sha256=e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c  lines=187
$ curl -sS -o gc.adoc -w '%{http_code}' https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc
200   bytes=7753   sha256=0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a  lines=181
```

All three are byte-identical (`cmp -s`) to the copies the C3 anchor seat staged in
`.ufo/waves/round-32/w1/sources/`. No source outside tag v2.56.0 was opened for these rows.
