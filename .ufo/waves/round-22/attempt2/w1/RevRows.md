STATUS: PASS

# RevRows — SOURCES append rows (S115, S116, S117, S124, S126, S137)

Scope: the drafted rows in `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`
(lines 13, 14, 15, 22, 24, 35) reviewed against the lane registry schema in
`corpus/SOURCES.md` and the validator `scripts/sources-census.sh`. Read-only outside
`.ufo/waves/round-22/attempt2/w1/{RevRows.md,evidence/}`. No tool installed.

**Verdict: REJECT (as an append).** All six documents are already in the lane registry as
S109–S114, added by this attempt's commit `a211e4d` (base `4edb25d` registry max = S108, HEAD
max = S114, contiguous S001–S114). Re-appending them writes six duplicate rows, four dangling
`used-by` pointers, six E09-invalid `recheck` cells, and two non-verbatim quote spans. The
append must not be applied; the corrected cells below are already the landed cells.

`S022` is **not** in the append file (`grep -c '^| S022 '` → `0`), so the
do-not-re-append rule holds.

---

## 1. Executed evidence

### 1.1 Registry state and id continuity
```
$ git log -1 --format='%h %ad' --date=iso -S'| S109 |' -- corpus/SOURCES.md
a211e4d 2026-10-21 18:56:48 -0300
$ git show 4edb25d:corpus/SOURCES.md | grep -oP '^\| S\K[0-9]+' | tail -1   -> 108
$ grep -oP '^\| S\K[0-9]+' corpus/SOURCES.md | tail -1                      -> 114
$ python3 -c "... ids ..."  -> n 114 min 1 max 114 missing []
```
The six draft documents map to landed rows, by URL/bytes (not by number):

| draft id (line) | document | landed lane row | duplicate signal |
|---|---|---|---|
| S115 (13) | `man7.org/.../man1/mv.1.html` | **S111** | W04 duplicate url |
| S116 (14) | `man7.org/.../man2/rename.2.html` | **S110** | W04 duplicate url |
| S117 (15) | `man7.org/.../man2/statx.2.html` | **S114** | W04 duplicate url |
| S124 (22) | probe `noreplace_probe.py`, out sha256 `1634d206…` | **S109** | source cell + sha identity (no URL) |
| S126 (24) | `docs.gtk.org/gio/method.File.trash.html` | **S113** | W04 duplicate url |
| S137 (35) | `man.archlinux.org/man/gio.1.en` | **S112** | W04 duplicate url |

### 1.2 Baseline registry is clean (so landed rows already satisfy the contract)
```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --root /home/vgpnk/Projects/shokunin souji
… 30 × W04 (pre-existing cross-scope warnings) …
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
exit=0
```
No E-code fires on the shipped registry: all 91 mined rows' `used-by` paths exist, every
`recheck` cell is a clean token (`on-release` ×94, `365d` ×7, `180d` ×6, `90d` ×5,
`on-change` ×1, `on-correction` ×1).

### 1.3 Candidate registry (registry + the six draft rows) fails
Candidate composed at `evidence/RevRows.candidate-SOURCES.md` (draft rows injected at the end of
`## Registry`, before `## Paths`):
```
$ scripts/sources-census.sh validate --root … --file evidence/RevRows.candidate-SOURCES.md
exit=1
  E09 ×6, W04 ×35, E11 ×109
$ grep -F 'E09' evidence/RevRows.validate-candidate.out
file	E09	S115 recheck=on-release — `man mv` after a coreutils upgrade
file	E09	S116 recheck=on-release — re-read the man-pages 6.x `rename(2)` page
file	E09	S117 recheck=on-release — re-read the man-pages 6.x `statx(2)` page
file	E09	S124 recheck=90d — re-run `python3 evidence/noreplace_probe.py` (expect 5 devices, EEXIST on existing)
file	E09	S126 recheck=365d — re-fetch the GIO `File.trash` method reference
file	E09	S137 recheck=365d — re-fetch the `gio(1)` man page
$ grep -E 'W04\tS(115|116|117|124|126|137) ' …
file	W04	S115 duplicate url man7.org/linux/man-pages/man1/mv.1.html across scopes
file	W04	S116 duplicate url man7.org/linux/man-pages/man2/rename.2.html across scopes
file	W04	S117 duplicate url man7.org/linux/man-pages/man2/statx.2.html across scopes
file	W04	S126 duplicate url docs.gtk.org/gio/method.File.trash.html across scopes
file	W04	S137 duplicate url man.archlinux.org/man/gio.1.en across scopes
```
Every E09 above is a real grammar failure: the validator accepts only `/^[0-9]+d$/` or the
symbolic form `^[A-Za-z][A-Za-z0-9 _-]*$` (`sources-census.sh:582`). The draft cells carry an
em dash and backticks, so they match neither.

`S124` produces **no** W04 because an `own-work` row has no URL: the duplicate is invisible to
the validator and detectable only by source text + digest (see 1.6). The 109 E11 lines in this
`.out` are a `--file`-mode artifact — `resolve_targets` sets `dir_abs = dirname(file)/..`
(`sources-census.sh:501`), i.e. `…/w1`, so every `corpus/...` pointer "misses". Genuine
`used-by` existence is the direct test in 1.5 (rule: `[ ! -e "$dir/$path" ]`,
`sources-census.sh:563`), and baseline 1.2 shows the shipped rows pass it at the lane root. The
109 lines are one per missing path (rows carry several), not one per row.

### 1.4 Structural checks — all six rows pass these
- 11 columns each; split on `|` yields exactly 11 cells (`NF=13` with the two boundary empties),
  same as every registry row.
- Zero literal or escaped `|` inside any cell (12 delimiters per line, `.count("\\|") == 0`).
- `kind` ∈ {docs, own-work}; `tier` = A; `status` = `mined` (registry vocabulary:
  mined/queued/rejected only).

### 1.5 `used-by` existence at the lane root
```
corpus/knowledge/quarantine-staging-no-copy.md            MISSING
corpus/knowledge/quarantine-staging-no-copy-r23.md        EXISTS
corpus/knowledge/quarantine-staging-no-copy-r24.md        MISSING
corpus/knowledge/duplicate-verdict-identity.md            MISSING
corpus/knowledge/quarantine-origin-record-fields-r23.md   MISSING
corpus/knowledge/quarantine-origin-record-fields-r24.md   EXISTS
```
`corpus/knowledge/` holds exactly 11 files; the only two entry files that exist are the two the
preregistration adopts. Four distinct draft pointers name files that do not and will not exist:
`quarantine-staging-no-copy.md`, `-r24.md`, `duplicate-verdict-identity.md`,
`quarantine-origin-record-fields-r23.md`.

### 1.6 Quote/snapshot fidelity (whitespace-collapsed, snapshots under `census/round-22/attempt2/sources/`)
| draft | quoted span | in snapshot |
|---|---|---|
| S115 | `--no-copy  do not copy if renaming fails` | **HIT** (`man7-mv.1.txt:90-91`) |
| S115 | `--exchange  exchange source and destination` | **HIT** (`:75-76`) |
| S126 | `Sends file to the 'Trashcan', if possible` | **MISS** |
| S137 | `files in the trash **with their original locations**` | **MISS** |
| S137 | `a file from trash to its original location` | **HIT** (`arch-gio.1.txt:568`) |

- S126 snapshot bytes are `Sends file to the “Trashcan”, if possible.` — codepoints
  `U+201C … U+201D`; the draft substitutes ASCII `'`, so the span is not verbatim.
- S137 snapshot bytes are `List files in the trash with their original locations.`; the draft
  injects Markdown `**` **inside** the quoted span. With `**` stripped the span is a HIT, so the
  sentence is right and only the emphasis placement is wrong.
- S137's other claims verify: `--restore` sentence and "If the original directory doesn't exist,
  it will be recreated." are present (`:566-570`), and `gio remove` says "removes files
  irreversibly … see the trash command" (`:443-444`).

### 1.7 Claim support
- S116: snapshot `:148-166` — `Return an error if newpath already exists`; matrix ext4 3.15,
  btrfs/tmpfs/cifs 3.17, xfs 4.0, "many other filesystems … Linux 4.9". Draft's teaches and
  matrix are accurate.
- S117: snapshot `:79, :83, :92, :106, :243` — `stx_nlink` "Number of hard links", `stx_ino`
  "Inode number", `stx_btime` "Creation", `stx_mnt_id` "Mount ID", `STATX_MNT_ID_UNIQUE
  … (since Linux 6.8)`. Accurate. (Note `STATX_MNT_ID` plain is since 5.8, `:240`.)
- S115 host claim: `/usr/bin/mv --version` → `mv (GNU coreutils) 9.12`; `man mv` footer →
  `GNU coreutils 9.12  September 2026`, and it lists `--exchange` and `--no-copy`. The man7 page
  is `GNU coreutils 9.11  April 2026` (`:192`). Claim holds.
- S115 teaches attribution: `grep -c 'copy+remove\|falls back\|cannot move' man7-mv.1.txt` → `0`.
  The cited page says only "do not copy if renaming fails"; "fail rather than fall back to
  copy+remove" is inference the row states as what the source teaches.
- S126 modality: the page says "so this call **can** return the `G_IO_ERROR_NOT_SUPPORTED`
  error", and "Since 2.82, the x-gvfs-trash unix mount option can be used to enable
  g_file_trash() support for particular system mounts" (`gtk-filetrash.txt:407-413`). The draft's
  absolute "returns … instead of removing the file" is stronger than the source.
- S124 digests: `sha256sum census/round-22/attempt2/sources/vendor-noreplace-probe.out` →
  `1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5`; the campaign probe
  `lanes/souji/round2/evidence/noreplace_probe.py` →
  `11df88f1f5687e9af93526943d875514d4c6b8e891a998edcc0aab73f1d4739f`. Both draft prefixes are
  correct.
- S124 "5 devices" is an overcount:
  `stat -c '%d %n'` → `32 /var/tmp`, `56 …/shokunin`, `56 …/shokuknow`, `33 /dev/shm`,
  `66308 /tmp` = **5 paths, 4 st_dev, 3 filesystems** (`findmnt -T`: btrfs `/dev/mapper/root`
  for `/` and `/home`, tmpfs, xfs `/dev/nvme0n1p1`) — not five devices.
- S137 `glib2 2.90.1` verified (`pacman -Q glib2` → `2.90.1-1`; man-page raw `<dd>2.90.1-1</dd>`).

---

## 2. Per-row result

`OK` means the cell passes; a row is `DEFECT` if any cell fails.

### S115 — DEFECT (do not append)
- dup: document already **S111** (same URL).
- `opened` `2026-10-23` → corrected `2026-10-25`.
- `recheck` `on-release — \`man mv\` after a coreutils upgrade` → corrected `on-release` (E09).
- `used-by` `corpus/knowledge/quarantine-staging-no-copy.md, corpus/knowledge/quarantine-staging-no-copy-r23.md` → corrected `corpus/knowledge/quarantine-staging-no-copy-r23.md` (first path missing).
- `teaches` → corrected `` `--no-copy` stops mv copying when the rename fails ("do not copy if renaming fails"); `--exchange` swaps source and destination `` (drop the unsourced copy+remove/failure mechanism).
- OK: columns, no pipes, quoted option strings verbatim, host coreutils 9.12 claim.

### S116 — DEFECT (do not append)
- dup: already **S110**.
- `opened` → `2026-10-25`; `recheck` → `on-release` (E09).
- `used-by` (3 paths) → corrected `corpus/knowledge/quarantine-staging-no-copy-r23.md`.
- OK: columns, no pipes, teaches and support matrix accurate.

### S117 — DEFECT (do not append)
- dup: already **S114**.
- `opened` → `2026-10-25`; `recheck` → `on-release` (E09).
- `used-by` (3 paths) → corrected `corpus/knowledge/quarantine-origin-record-fields-r24.md`.
- OK: columns, no pipes, all four statx field claims supported.

### S124 — DEFECT (do not append)
- dup: already **S109** (same probe, same out digest `1634d206…`; S109 also vendors the bytes at `census/round-22/attempt2/sources/vendor-noreplace-probe.out`).
- `opened` → `2026-10-25`; `recheck` `90d — re-run \`python3 evidence/noreplace_probe.py\` …` → corrected `90d` (E09).
- `scope` `evidence/noreplace-probe.out (sha256 1634d206…), 5 devices, …` → corrected `census/round-22/attempt2/sources/vendor-noreplace-probe.out (sha256 1634d206…8bb5), 5 probed paths on 4 devices (btrfs /var/tmp + /home, tmpfs /dev/shm, xfs /tmp), kernel 7.2.11-arch1-1, produced 2026-10-23`. `evidence/noreplace-probe.out` and `evidence/noreplace_probe.py` do not exist in the lane (only in the read-only campaign repo).
- OK: columns, no pipes, `used-by` path exists, both digest prefixes correct.

### S126 — DEFECT (do not append)
- dup: already **S113**.
- `opened` → `2026-10-25` (also the anchor text `opened 2026-10-23`); `recheck` → `365d` (E09).
- `used-by` (2 paths) → corrected `corpus/knowledge/quarantine-origin-record-fields-r24.md`.
- `scope` quote → corrected `§ Description, "Sends file to the “Trashcan”, if possible."; GLib GIO docs, opened 2026-10-25` (curly quotes as in the snapshot).
- `teaches` "returns `G_IO_ERROR_NOT_SUPPORTED`" → corrected "can return `G_IO_ERROR_NOT_SUPPORTED`" (page is modal; 2.82 `x-gvfs-trash` can re-enable).
- OK: columns, no pipes, recoverability and refusal semantics are in the page.

### S137 — DEFECT (do not append)
- dup: already **S112**.
- `opened` → `2026-10-25` (also `opened 2026-10-23` in the anchor); `recheck` → `365d` (E09).
- `teaches` → corrected `` `gio trash --list` lists "files in the trash with their original locations" and `--restore` restores "a file from trash to its original location" (recreating the original directory if it is gone) — so a per-item record must carry the **original path**, and `gio remove` is the explicitly irreversible alternative `` (bold markers moved outside the quoted spans).
- OK: columns, no pipes, `used-by` path exists, restore/remove claims supported, `glib2 2.90.1` correct.

---

## 3. Findings by severity

**F1 (blocker) — the append is a duplicate of landed rows S109–S114.** Six of six draft rows
restate a document already registered by commit `a211e4d` at the lane's next-free ids (S109 was
the next free id at the frozen base). Appending would (a) split citations for one document across
two ids, (b) add five `W04` warnings, (c) break the "cite, do not duplicate" adopted-row rule of
the preregistration. The validator cannot catch this for S124 (`own-work` rows carry no URL), so
the duplicate review has to be done by document, as here.

**F2 (blocker) — six E09 `recheck` cells.** Every draft `recheck` cell carries prose after the
token. The registry's grammar (and all 114 shipped rows) is a bare `on-release` / `NNd` /
`on-change` / `on-correction`. Fix: keep only the token; move the operator instruction to the
lesson Gate or the row's `scope`.

**F3 (blocker) — four dangling `used-by` paths** across S115, S116, S117, S126
(`quarantine-staging-no-copy.md`, `-r24.md`, `duplicate-verdict-identity.md`,
`quarantine-origin-record-fields-r23.md`). With the six rows appended, `validate` from the lane
root would emit E11 and exit 1, failing the C2 target `validate … exit 0`.

**F4 (major) — two non-verbatim quote spans.** S126 substitutes ASCII `'` for `U+201C/U+201D`
around Trashcan; S137 puts `**` inside a quoted sentence. Both fail Gate predicate 4
("appears verbatim, whitespace-collapsed") if the same span is reused in the entry Gate.

**F5 (minor) — `opened = 2026-10-23` on all six.** The round date is 2026-10-25 (frozen C2
predicate 2), the snapshots under `census/round-22/attempt2/sources/` are this round's fetches
(mtime 2026-10-25 03:36–03:38), and the landed rows already say `2026-10-25`. `2026-10-23` is the
campaign staging date, not a lane open date.

**F6 (minor) — "5 devices" overcount** in S124 (5 paths, 4 st_dev, 3 filesystems, 2 block
devices). Severity is low for the claim's substance (`NOREPLACE` holds on every probed path) but
it is the kind of count that a later census will contradict.

**F7 (minor) — attribution and modality.** S115's `teaches` asserts a failure/`copy+remove`
mechanism the cited page does not contain (`0` hits), and S126's "returns" hardens the page's
"can return". Both survive review only as paraphrase drift; fix the wording, not the source.

**Residual on the landed rows (outside my write scope, worth a look):** S109 says "all five
probed devices" (same count slip as F6); S111 says "--no-copy makes mv fail rather than fall back
to copy+remove, on any filesystem" (F7's inference plus a universal the page does not state);
S113 says "returns G_IO_ERROR_NOT_SUPPORTED … on unsupported mounts" (page: "can return … system
mounts by default"). None is a quote, so none is E-level, but they are the same two defects the
draft rows carry.

## 4. Verification gaps / residual risk

- E11 for the draft rows is argued from the frozen path-existence rule (`sources-census.sh:563`)
  plus a direct `[ -e ]` test at the lane root, not from validator output: `--file` mode pins
  `dir_abs` to the file's grandparent, so its E11 stream is unusable for row-level adjudication
  (all 109 lines, including rows that demonstrably pass at the lane root). Re-running `validate`
  after a real append is the only fully authoritative check.
- Quote checks compare against the committed text extractions
  (`man7-*.txt`, `gtk-filetrash.txt`, `arch-gio.1.txt`), whitespace-collapsed. A raw-HTML check
  of `gtk-filetrash.raw` was not needed because the `.txt` carries the page's own curly quotes,
  but the `.txt` extraction is the byte source relied on.
- I did not re-fetch any URL and did not run `mv`, `gio` or `renameat2` probes; no new
  measurement was needed for a schema review.

## 5. Artifacts written

- `evidence/RevRows.tsv` — 47 check receipts (row, line, check, expected, observed, verdict).
- `evidence/RevRows.candidate-SOURCES.md` — registry + the six draft rows (input to the validator).
- `evidence/RevRows.validate-candidate.out` — raw `validate --file` output (E11 stream is the
  `--file` artifact described in §1.3).
