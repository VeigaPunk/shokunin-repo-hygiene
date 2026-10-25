STATUS: PASS

# SnapManifest — C2 snapshot manifest (round 22, attempt 2 / hyaku)

Axes named before measuring: **calibration** (digest/date/status provenance that a
third party can re-derive), **coverage** (all six snapshot seats, both artifact
classes), **operability** (stable six-field TSV, sorted, byte-reproducible).

Preregistration read first: `.ufo/waves/round-22/attempt2/preregistration.txt`
(frozen, base `4edb25d`). This seat emits a manifest only; it renders **no** C2
verdict and did not run `tools/souji-gate-check.py`.

## 1. Seat presence (executed)

Roster from `.ufo/waves/round-22/attempt2/w1-spec.json`: the six snapshot seats are
`SnapMv1`, `SnapRename2`, `SnapFileTrash`, `SnapTrashSpec`, `SnapStatx2`, `SnapGio1`.

First scan (03:45) saw only 2 evidence files. The writers were still landing; by the
time of the build all six had written **both** artifacts. No seat is `absent`.

| seat | slug | `.raw` | `.txt` | seat report |
|---|---|---|---|---|
| SnapMv1 | mv1 | 11693 | 4610 | SnapMv1.md |
| SnapRename2 | rename2 | 23571 | 15799 | SnapRename2.md |
| SnapFileTrash | filetrash | 19401 | 4140 | SnapFileTrash.md |
| SnapGio1 | gio1 | 26697 | 12125 | SnapGio1.md (landed 03:47:01, after the evidence scan) |
| SnapTrashSpec | trashspec | 40146 | 24788 | SnapTrashSpec.md |
| SnapStatx2 | statx2 | 33125 | 19724 | SnapStatx2.md |

Late arrivals observed rather than waited on: `snap-gio1.raw` at 03:45:28,
`snap-gio1.txt` first at 03:45:54 (`gio1.txt appeared after 1x5s` on a bounded 60 s poll)
and rewritten at 03:46:08 — still **before** the 03:46:15 manifest write, so the TSV
digests the final bytes (re-checked after the fact: `12/12 digests valid from evidence/
cwd`). `SnapGio1.md` landed at 03:47:01, after the evidence build. All six seats
delivered both evidence artifacts, so the *manifest* is complete; no row reads `absent`.

## 2. Manifest as written (executed — full print)

`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence/snapshot-manifest.tsv`
(1358 bytes, 13 lines = header + 12 rows):

```
slug	file	bytes	sha256	http-code	fetch-date
filetrash	snap-filetrash.raw	19401	a5af1920b16444e0a03d30fcf77de0389533bcedb7243175c915b34c38c21cf3	200	2026-10-25
filetrash	snap-filetrash.txt	4140	23fb07ce8ca4946f49a78b7a3d00f7bcba45ec246219b5d47432b6d6d2a86c5e	200	2026-10-25
gio1	snap-gio1.raw	26697	3e7876d838c665f9afbd4e36c4fb7c022e946a44fccba7789b230ccb57419e84	200	2026-10-25
gio1	snap-gio1.txt	12125	cc4af34906f691370d4a1ea51ceae378b697a3673001a5150e0bb1543dd56f68	200	2026-10-25
mv1	snap-mv1.raw	11693	d20b49ad254a0c791f788920218f60da657a2f8ef765ba681a0f63fd2053ed0c	200	2026-10-25
mv1	snap-mv1.txt	4610	18dc9c2185fbf2b8839e780b2a9a88fdf392ffeff311785086c807a5aa4e6687	200	2026-10-25
rename2	snap-rename2.raw	23571	8772946a809a0db54f4854f200908f10bee758ea452e8df5efd955bc3b8e6e57	200	2026-10-25
rename2	snap-rename2.txt	15799	88cba52e7f5ee81985c34a33a3d4112ce0fecd377da5d0665ca7adb76c9631c4	200	2026-10-25
statx2	snap-statx2.raw	33125	2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e	200	2026-10-25
statx2	snap-statx2.txt	19724	ca14c31f6608b6e91ba019aa434ad7d49c90ad8bb6411d4421a744b1f2a05f1b	200	2026-10-25
trashspec	snap-trashspec.raw	40146	353442d2ed3db0ff0c59632796214df56ba24973621f2e7899711921ee454ae4	200	2026-10-25
trashspec	snap-trashspec.txt	24788	aa21fdcbc8f7226e1e05cac5ab89818abb0ad4b9dd9743a8f42b231a99b99511	200	2026-10-25
```

Column semantics (`slug` + `file` = primary key; two rows per slug, `.raw` then `.txt`):
* `bytes` — on-disk `stat` size.
* `sha256` — digest of the artifact's bytes **as they exist on disk** (for `.txt`,
  that includes any provenance header the seat prepended).
* `http-code` — status of the **source URL** for that slug, observed by an independent
  `curl -sSL -o /dev/null -w '%{http_code}'` probe during the build (not copied from
  the files; the files carry no status metadata except `snap-rename2.txt`, whose
  `# http-code: 200` agrees).
* `fetch-date` — capture date from the artifact's mtime (`2026-10-25`), identical for
  all 12; `snap-rename2.txt`'s own `# fetch-date: 2026-10-25` header agrees.

## 3. Digest verification — twice, then a third independent pass (executed)

1. Pass A: `hashlib.sha256` over the bytes.
2. Pass B: `sha256sum <file>`.
3. Pass C: rebuild the manifest in memory from the same rule and `diff` against disk:
   `DETERMINISTIC_REGEN_IDENTICAL: True` (`rows: 12 bytes_on_disk: 1358`).
4. Pass D: feed the manifest back to coreutils —
   `awk -F'\t' 'NR>1{print $4"  "$2}' snapshot-manifest.tsv | sha256sum -c --quiet -`
   → all 12 digests re-verified via sha256sum -c.

`digest2_matches=True` for all 12 rows; `ISSUES: none`. No `.raw` or `.txt` byte was
rewritten by this seat: mtimes remain the seats' own stamps (`03:45:03`–`03:46:08`),
while `snapshot-manifest.tsv` carries `03:46:15` and this report `03:47:11`. Other seats
keep adding unrelated files to `evidence/` (`rev-*.html`, `impl-gate/`); the manifest is
frozen over the six-seat artifact set and does not chase those.

## 4. Live re-fetch: every `.raw` is byte-identical to the URL today (executed)

`curl -sSL -m 45 -A 'souji-r22-restructure/1.0' -w '\n%{http_code}' -o /dev/stdout <url>`
for the six canonical URLs, digesting the body:

```
https://man7.org/linux/man-pages/man1/mv.1.html                200 11693  IDENTICAL to snap-mv1.raw
https://man7.org/linux/man-pages/man2/rename.2.html            200 23571  IDENTICAL to snap-rename2.raw
https://docs.gtk.org/gio/method.File.trash.html                200 19401  IDENTICAL to snap-filetrash.raw
https://man.archlinux.org/man/gio.1.en                         200 26697  IDENTICAL to snap-gio1.raw
https://specifications.freedesktop.org/trash/latest/           200 40146  IDENTICAL to snap-trashspec.raw
https://man7.org/linux/man-pages/man2/statx.2.html             200 33125  IDENTICAL to snap-statx2.raw
```

All six `.txt` correctly `DIFFERS` from the live body: they are text extractions, not
HTTP bodies. That is expected, not a defect.

Semantic spot-check that each 200 is the page it claims to be (not a soft 404):
`Gio.File.trash` ×5 in filetrash; `renameat2`/`RENAME_NOREPLACE` in rename2;
`stx_` ×106 and `statx(2)` title in statx2; `Trash Specification` in trashspec;
`gio trash` in gio1; `--no-clobber` in mv1.

## 5. Error-page / redirect-stub / empty audit (executed)

Among the 12 snapshot-seat artifacts: **none** empty, **none** an HTML error page
(no `<title>4xx/5xx`, no "404 Not Found"/"Page Not Found" in the head), **none** a
redirect stub (no `<meta http-equiv=refresh>`, no "301 Moved"/"302 Found"), and every
`<title>` is the expected document title. All 6 URLs answered **200** with
`num_redirects=0`-equivalent behaviour (final URL == requested URL on the probes).

Findings **outside** this manifest's scope, reported because they sit in the same
directory (each written by a non-snapshot seat; none is in the TSV):

* `rev-doi-S118.body` — **0 bytes, empty** at audit time (Slice118's).
* `slice118-doi.txt` — **was 0 bytes** at the first scan (03:45:07) and is **736 bytes**
  at audit time; the seat evidently re-ran its fetch after the first, empty, write.
  Recorded as transient-empty, not a current defect.
* Three byte-identical cross-seat fetch groups — corroboration, not duplication errors:
  `rev-docs.gtk.org_gio_method.File.trash.html.html` = `slice126-filetrash.html.txt` =
  `snap-filetrash.raw` (`a5af1920…`); `rev-git-scm.com_docs_git-prune.html` =
  `slice114-git-scm-git-prune.html` (`5d3dcd3b…`); `slice124-rename2.html` =
  `snap-rename2.raw` (`8772946a…`). Independent seats re-fetched the same URL and got
  the same bytes, which *raises* confidence in those snapshots.

## 6. Structural conformance of the TSV (executed)

```
header fields=6 -> slug	file	bytes	sha256	http-code	fetch-date
data rows=12
slug order: sorted
```

Six fields on every row, ASCII-tab separated, no trailing spaces; slugs
`filetrash, gio1, mv1, rename2, statx2, trashspec` are in `LC_ALL=C` order, ties in a
slug broken by filename (`.raw` before `.txt`), so the file is a function of the
evidence directory alone.

## 7. Cross-check against the writers' own receipts (executed)

Grep of the five landed seat reports: every one records `HTTP 200` and
`fetch date 2026-10-25`, matching the manifest. `SnapMv1.md` additionally states
`Raw sha256 d20b49ad…`, `Text sha256 18dc9c21…` — byte-for-byte the two `mv1` rows.
`SnapRename2.txt`'s embedded header states `http-code: 200`, `fetch-date: 2026-10-25`,
`raw-sha256: 8772946a…`, all three equal to the manifest row.

## 8. Writes and prohibitions

* Written: `evidence/snapshot-manifest.tsv` and this report. Nothing else.
* Created/deleted: one throwaway `/tmp/.s1` scratch file used by the sort check, removed
  in the same command; nothing created outside `…/w1/evidence/`.
* No git/jj command; no commit, push, fetch; no lane index, `.ufo/state`,
  `.ufo/watchdog.log`, `MANIFEST.json`, or `templates/`/`scripts/` touched;
  `shokuknow` untouched; no `/proc`, credentials, or operator-sweep census read.
* Tool installs: **none** (needed none; `curl`, `sha256sum`, `python3` were already present).

## 9. Handoff (inferred, not claimed as done)

C2's gate-check reads snapshots from `census/round-22/attempt2/sources`
(`--snapshot-dir`). This manifest is the digest reference for any such staging copy,
but populating that directory is not this seat's write scope and was not performed.
All six seat reports are now present; `SnapGio1.md` landed at 03:47:01, after the
manifest build, and describes `gio1` evidence the manifest already digests.
