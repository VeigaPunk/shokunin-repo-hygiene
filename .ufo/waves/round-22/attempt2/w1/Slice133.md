# Slice133 — hand-check of absent-defect register row `souji`/round3/S133

STATUS: PASS

Frozen-class verdict for this row: **`accepted`** (quote bytes are verbatim and correct;
the citation pointer is corrected — see §4). The register's own label for the row,
`payload-absent`, is **overturned**: the sentence is not fabricated, it is mislocated.
No register rewrite was performed (out of scope by contract).

Preregistration read first, unmodified:
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/preregistration.txt`
(frozen 2026-10-25; base rev `4edb25dfe262515d0da63224bbba71e02e36cba5`; four classes
present|accepted|unverifiable|refused, nothing else is reportable).

---

## 1. Row extraction (frozen command, field 4 = id cell)

Executed, from `/home/vgpnk/Projects/shokuknow`:

```
awk -F'|' '$4 ~ /S133/ && $2 ~ /souji/ {print}' \
  .ufo/waves/corpus-expansion-1/absent-defect-register.md
```

Observed output (exactly one row; `wc -l` = 1):

```
| `souji` | round3 | S133 | `payload-absent` | lanes/souji/round3/evidence/r24-renameat2-probe.out | `RENAME_NOREPLACE Don't overwrite newpath of the rename.` | cited source, companion URLs and local artifacts were all checked; the quote is in none of them |
```

Claimed quote: `RENAME_NOREPLACE Don't overwrite newpath of the rename.` (7 words).
Cited source: local artifact `lanes/souji/round3/evidence/r24-renameat2-probe.out`.

## 2. Does the payload with that name exist at all? — YES

Executed (read-only):

```
ls -l lanes/souji/round3/evidence/r24-renameat2-probe.out
wc -l  < lanes/souji/round3/evidence/r24-renameat2-probe.out
sha256sum lanes/souji/round3/evidence/r24-renameat2-probe.out
```

Observed: `-rw-r--r-- 1315 bytes, 11 lines, 2026-10-23 19:29`;
sha256 `a53f1e301d0c6969d589f9071b8a3bac9db8f6e1d3ebbb0ace42c300904b0809`.
Directory inventory (`ls -1 lanes/souji/round3/evidence/`) lists 4 files total; the named
payload is one of them. **The payload is present** — this row is therefore *not* a
missing-payload case.

## 3. Is the quote in the cited artifact? — NO (three independent normalizations)

Executed against the artifact:

```
for pat in "Don't overwrite" "overwrite newpath" "RENAME_NOREPLACE Don"; do grep -Fci "$pat" "$A"; done
tr -s '[:space:]' ' ' < "$A" | grep -c "RENAME_NOREPLACE Don't overwrite newpath"
```

Observed: `0`, `0`, `0`, and collapsed-match count `0`.
The artifact's only `NOREPLACE` tokens are probe key/value pairs:

```
1 NOREPLACE
8 NOREPLACE_existing=
8 NOREPLACE_new=ok
```

The artifact's actual content is the filesystem probe census (`/dev/shm`, `/fast`,
`/home/vgpnk`, … `fstype=… NOREPLACE_new=ok NOREPLACE_existing=EEXIST …`) and
`SUMMARY: every writable mount implements RENAME_NOREPLACE`. It carries no prose from
`rename(2)`.

## 4. Where the sentence actually lives — fetched source, decoded

Fetched: `https://man7.org/linux/man-pages/man2/rename.2.html` (public https, permitted).
Access date: **2026-10-25**. Response: `HTTP/1.1 200 OK`,
`Date: Sun, 25 Oct 2026 06:45:35 GMT`, `Content-Length: 23571`,
`Last-Modified: Thu, 08 Oct 2026 17:39:35 GMT`.

- raw HTML sha256: `8772946a809a0db54f4854f200908f10bee758ea452e8df5efd955bc3b8e6e57`
- page identity (COLOPHON): `Linux man-pages 6.19   2026-02-08   rename(2)`

Exact located span (14 words, <= 25):

> `RENAME_NOREPLACE Don't overwrite newpath of the rename. Return an error if newpath already exists.`

Locator: **DESCRIPTION → `renameat2()` → "The flags argument is a bit mask…" list entry
`RENAME_NOREPLACE`, first sentence** — snapshot lines 137–139:

```
137:       RENAME_NOREPLACE
138:              Don't overwrite newpath of the rename.  Return an error if
139:              newpath already exists.
```

Verbatim-prefix test of the claimed quote against the whitespace-collapsed page:
`RENAME_NOREPLACE Don't overwrite newpath of the rename.` → **True** (the flag label sits
immediately before its definition, so the 7-word quote is a prefix of the 14-word sentence;
the claimed quote's terminal period is the sentence's period, not an elision).

Snapshot saved (only file written besides this report):

```
/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence/slice133-renameat2-probe.out
16839 bytes  sha256 5e4a81c7f259b711479ff18ebfdb6746a3990ce42b3392e98aae9e1d281afbf7
```

Header lines 1–16 record the register row, the cited-artifact hash, the URL, the access
date, the response headers, the raw-HTML hash, the extraction method and the located span;
the page text follows verbatim. Post-write containment check on the body
(`awk 'NR>18' … | tr -s '[:space:]' ' '`) re-finds the 14-word sentence.
Independent corroboration of the fetched bytes: the sibling snapshot already in this
evidence directory, `slice124-rename2.html`, hashes to the identical
`8772946a…3b8e6e57`.

## 5. Why `accepted` and not `refused`

The lane's own round-3 registry already names the correct source for this sentence —
`lanes/souji/round3/SOURCES-PROPOSED.md`, lines 37–46:

```
## Gate — S133
- URL: lanes/souji/round3/evidence/r24-renameat2-probe.out
- Quoted (fleet path line): "/home/vgpnk   fstype=btrfs   NOREPLACE_new=ok   NOREPLACE_existing=EEXIST …"
- Upstream semantics for the same operation: https://man7.org/linux/man-pages/man2/rename.2.html — "RENAME_NOREPLACE Don't overwrite newpath of the rename."
```

So the entry's `URL:` field (the probe artifact) correctly backs the probe line it quotes,
and the sentence is attributed to the man page under *Upstream semantics for the same
operation*. The absent-defect register collapsed the citation onto the Gate's `URL:`
value. That is a **citation-class defect in the register's "cited source" column**, not
fabricated text: the bytes are verbatim in the page the lane itself names.

Correction stated (the `accepted` requirement): the row's quote stands unchanged;
its cited source must be
`https://man7.org/linux/man-pages/man2/rename.2.html` — DESCRIPTION → `renameat2()` →
`RENAME_NOREPLACE` first sentence — with the probe artifact
`lanes/souji/round3/evidence/r24-renameat2-probe.out` retained only as the environment
receipt for `NOREPLACE_new=ok / NOREPLACE_existing=EEXIST`.

`refused` would be wrong here: it would assert the payload/sentence is absent or that the
row must be dropped, and both are contradicted by the read bytes.

## 6. Bounded findings (no verdict assigned outside the row)

1. **Row S133 → `accepted`; register label `payload-absent` is misapplied.** Grounded on
   the artifact read (§2–3) and the fetched span (§4). *Executed.*
2. **Citation-class defect shape:** a Gate whose `URL:` is a local receipt and whose prose
   quote belongs to a companion "Upstream semantics" URL. Any checker that reads only the
   `URL:` field will classify this correctly-sourced quote as absent. This is a blind spot
   of the register's cited-source extraction, not a lane fabrication. *Executed +
   [INFERENCE] on the register's extraction step (its generator was not read).*
3. **Duplicate gate id in the lane registry (unscored observation):**
   `grep -c "^## Gate — S133$" lanes/souji/round3/SOURCES-PROPOSED.md` → `2`. Two
   `## Gate — S133` blocks (lines 37 and 42) quote two different lines of the same
   artifact and repeat the same man-page sentence. If registry ids are meant to be
   unique, this is a second, separate defect — it is **not** part of my row's verdict.
   *Executed.*
4. **Out of scope, deliberately unscored:** register row `souji`/round2/S124 shows the same
   shape (local probe artifact cited for a man-page sentence). I did not extract, parse or
   judge it. *Not executed.*

## 7. Compliance and side effects

- Read-only on `/home/vgpnk/Projects/shokuknow` (only `ls`, `wc`, `grep`, `sha256sum`,
  `sed -n`, `cut`, `awk -F'|'` row selection); no git/jj command, no fetch/push, no
  campaign tool, no write.
- Wrote exactly two files, both absolute under
  `/home/vgpnk/Projects/shokunin/souji-shokunin/`: this report and the named evidence
  file. Nothing else created under `.ufo/waves/round-22/attempt2/w1/evidence/` by me.
- Did not touch the lane repo, lane index, `.ufo/state`, `.ufo/watchdog.log`,
  `MANIFEST.json`, `templates/`, `scripts/`, or any sibling repo. No `/proc`, credentials,
  private TSVs, `.tower`, or operator-sweep census contents read. No deletion authority
  created; no cleanup run; no process signalled.
- Tool/version/channel record: **none installed, none updated** (pacman paused host-wide;
  `curl`, `awk`, `grep`, `sha256sum`, `python3` were already present).
- Transient scratch: `/tmp/rm2.html`, `/tmp/rm2.hdr` (fetch staging outside the lane; the
  fetched bytes are preserved in the hashed snapshot above).
- No subagent dispatch (leaf member).

## 8. Outstanding unknowns

None for this row. The only residual is procedural: whether the register's generator
intentionally prefers the Gate `URL:` field over "Upstream semantics" (finding 6.2) — that
determines how many other rows share this shape, and it was not investigated here because
it lies outside the single-row assignment.
