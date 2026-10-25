# SnapTrashSpec — re-grounding snapshot: freedesktop Trash Specification (C2 theme: restorable-quarantine staging)

STATUS: PASS

Seat: L1Souji22.SnapTrashSpec (leaf). Lane: round 22, attempt 2 (hyaku), wave 1.
Item: capture a re-grounding snapshot for the restorable-quarantine-staging theme (C2) and
quote the `info/<name>.trashinfo` layout passage verbatim (<=25 words) with its locator.
Preregistration read before any measurement:
`.ufo/waves/round-22/attempt2/preregistration.txt` (base rev `4edb25dfe262515d0da63224bbba71e02e36cba5`).
Nothing in this report redefines a frozen counter, predicate, or kill rule.

Axes for this item: calibration (evidence carries its own re-derivable receipts), operability
(exact fetch + exact conversion command reproduce the bytes), coverage (C2 entries get one
dated, hash-bound snapshot under the lane's own capture discipline). No axis is harmed: the
source is read-only, no cleanup ran, no deletion authority is created.

---

## 1. Fetch — executed

Command (exactly as assigned, run from this shell):

```
curl -fsSL -m 45 -A 'souji-r22-restructure/1.0' \
  -o /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence/snap-trashspec.raw \
  -w '%{http_code} %{size_download}' \
  'https://specifications.freedesktop.org/trash/latest/'
```

Observed output:

```
200 40146
EXIT=0
```

Redirect/final-URL receipt — executed (second request to `/dev/null`, identical UA and timeout):

```
code=200 url_effective=https://specifications.freedesktop.org/trash/latest/ redirects=0 size=40146
```

So: **fetch date 2026-10-25, HTTP 200, 40146 bytes, final URL after redirects =
`https://specifications.freedesktop.org/trash/latest/` (zero redirects — that URL is already
final)**.

The page is a static HTML document, not JS-rendered — executed check on the payload:

```
snap-trashspec.raw: HTML document, Unicode text, UTF-8 text, with very long lines (326)
<body class="single offline js-off">
<title>Trash Specification</title>
```

`js-off` in the body class and the full prose being present in the raw bytes are the evidence
that no script execution was needed. The unreachable/JS-only fallback clause of this item is
therefore not triggered.

## 2. Text snapshot — executed

The snapshot is a tag-stripped, word-order-preserving rendering of the raw HTML, produced with
Python's `html.parser` (no third-party tools, no HTML rewriting). Exact command used:

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence && python3 -c '
import html.parser, sys

class T(html.parser.HTMLParser):
    SKIP = {"script","style","head"}
    BLOCK = {"p","div","li","tr","td","th","h1","h2","h3","h4","h5","h6","pre","br","dt","dd","table","ul","ol","section","title"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip=0; self.out=[]
    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP: self.skip+=1
        if tag in self.BLOCK: self.out.append("\n")
    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip: self.skip-=1
        if tag in self.BLOCK: self.out.append("\n")
    def handle_data(self, d):
        if not self.skip: self.out.append(d)

p=T()
p.feed(open("snap-trashspec.raw",encoding="utf-8",errors="replace").read())
p.close()
lines=[]
for ln in "".join(p.out).split("\n"):
    ln=" ".join(ln.split())
    if ln: lines.append(ln)
sys.stdout.write("\n".join(lines)+"\n")
' > snap-trashspec.txt
```

Observed: `EXIT=0`, `24788 snap-trashspec.txt`, 460 lines.

Integrity of the written text file — executed:

```
valid utf-8; BOM= False NUL= False
```

The converter emits no page chrome beyond the document's own text, keeps every word in document
order, and collapses runs of whitespace to single spaces so a whitespace-collapsed
`in`-test is the correct containment check. Entity references (`&quot;`, `&#8220;`, …) are
resolved by `convert_charrefs=True`, so the snapshot carries real Unicode quotation marks —
quotes must be reproduced with the curly `“ ”` glyphs to match verbatim.

## 3. Hashes and sizes — executed

```
$ sha256sum snap-trashspec.raw
353442d2ed3db0ff0c59632796214df56ba24973621f2e7899711921ee454ae4  snap-trashspec.raw
$ wc -c snap-trashspec.raw
40146 snap-trashspec.raw

$ sha256sum snap-trashspec.txt
aa21fdcbc8f7226e1e05cac5ab89818abb0ad4b9dd9743a8f42b231a99b99511  snap-trashspec.txt
$ wc -c snap-trashspec.txt
24788 snap-trashspec.txt
```

| artifact | bytes | sha256 |
|---|---|---|
| `evidence/snap-trashspec.raw` | 40146 | `353442d2ed3db0ff0c59632796214df56ba24973621f2e7899711921ee454ae4` |
| `evidence/snap-trashspec.txt` | 24788 | `aa21fdcbc8f7226e1e05cac5ab89818abb0ad4b9dd9743a8f42b231a99b99511` |

Both digests were taken after the last write to each file; neither file was modified afterwards.

## 4. The passage — located and quoted verbatim

**Locator: § 6, "Contents of a trash directory"** (HTML anchor `id="contents-of-a-trash-directory"`;
the txt snapshot's § 6 heading is at line 220, and the info-file paragraph opens at line 246).
The answer to the item's "§ 5 or § 6?" question is **§ 6** — § 5 ("Trash directories") is about
*where* trash directories live; the `info/<name>.trashinfo` layout and the `Path` /
`DeletionDate` keys are defined in § 6.

Primary quote (14 words):

> “The $trash/info directory contains an “information file” for every file and directory in $trash/files.”
> — § 6, snapshot line 246

Naming rule for the same file (19 words):

> “This file MUST have exactly the same name as the file or directory in $trash/files, plus the extension “.trashinfo””
> — § 6, snapshot lines 247–249

The two keys, each quoted adjacently (15 and 13 words):

> “The key “Path” contains the original location of the file/directory, as either an absolute pathname”
> — § 6, snapshot line 256

> “The key “DeletionDate” contains the date and time when the file/directory was trashed.”
> — § 6, snapshot line 269

Format spine of the file (7 words):

> “Its first line must be [Trash Info].”
> — § 6, snapshot line 253

Note on the <=25-word constraint: no *contiguous* verbatim span of <=25 words in § 6 names both
keys at once (the "It also must have two lines that are key/value pairs…" sentence is followed by
separate paragraphs for `Path` and `DeletionDate`). The layout and the two keys are therefore
reported as adjacent spans, each individually <=25 words and each individually verbatim. They
should be cited as separate quotes; concatenating them into one quote would not be verbatim.

Verification that each quoted span occurs in the committed snapshot — executed, whitespace
collapsed, against `evidence/snap-trashspec.txt`'s own bytes:

```
PRESENT words=14 | The $trash/info directory contains an “information file” for every file and directory in $trash/files.
PRESENT words=19 | This file MUST have exactly the same name as the file or directory in $trash/files, plus the extension “.trashinfo”
PRESENT words=7  | Its first line must be [Trash Info].
PRESENT words=15 | The key “Path” contains the original location of the file/directory, as either an absolute pathname
PRESENT words=13 | The key “DeletionDate” contains the date and time when the file/directory was trashed.
```

All five `PRESENT`. No quote in this report was reconstructed from memory: every span was
extracted from the fetched bytes and then re-tested against the written snapshot.

## 5. Bounded findings

1. **Source is static and reachable.** HTTP 200, 40146 bytes, zero redirects, prose present in
   the raw HTML. The item's "unreachable or JS-only → stop" branch did not apply, so no
   fabrication fallback was used. [executed]
2. **The theme's §-anchor is § 6, not § 5.** The spec's own numbering is 6 = "Contents of a
   trash directory". [executed: heading text and anchor id read from the payload]
3. **Additional verbatim spans in § 6 that the two C2 entries may want** (all re-tested
   `PRESENT` against the snapshot; offered as candidates, not as verdicts, since entry authorship
   belongs to the entry seat):
   - no-clobber: `"the only limitation is that they must be unique within the directory"` (12 words, snapshot lines 230–231);
   - no-overwrite: `"Even if a file with the same name and location gets trashed many times, each subsequent trashing must not overwrite a previous copy."` (23 words, snapshot lines 231–233);
   - atomic staging: `"it MUST try to do this in an atomic fashion, so that if two processes try to trash files with the same filename"` (23 words, snapshot lines 290–292);
   - filename is not provenance: `"A filename in the $trash/files directory MUST NEVER be used to recover the original filename; use the info file"` (19 words, snapshot lines 240–241).
4. **C2 predicate 4 target path.** The frozen per-entry predicate requires the snapshot a Gate
   names to live under `census/round-22/attempt2/sources`. This item's assignment stages the
   snapshot at `.ufo/waves/round-22/attempt2/w1/evidence/` and forbids writing elsewhere, so the
   file under `census/round-22/attempt2/sources/` is **not** written by this seat. The binding for
   that copy is the digest above: a snapshot placed in the census directory must hash to
   `aa21fdcbc8f7226e1e05cac5ab89818abb0ad4b9dd9743a8f42b231a99b99511` (24788 bytes) to be the
   same bytes these quotes were verified against. [executed: digest; inferred: the copy is a
   later seat's step — I did not perform or observe it]
5. **Not done here, by design.** No knowledge entry, no `## Gate` block, no ADMIT/REJECT row, no
   slice verdict, and no `tools/souji-gate-check.py` run: those are the entry seat's and the
   governing counter's outputs, and writing them would be a verdict this preregistration does not
   define for this seat. This report therefore claims snapshot availability and quote
   verification only — not that C2 passes.
6. **Lane bounds respected.** Files written, total: the two evidence files above plus this report.
   No git/jj writes, no commits, no `.ufo/state`, no `MANIFEST.json`, no `templates/`, no
   `scripts/`, no sibling repo, no `/home/vgpnk/Projects/shokuknow` write, no mutating cleanup, no
   process signalling, no credentials or `/proc` reads. No tool was installed, so there is no
   tool/version/channel entry to record.
7. **Cross-seat note.** Two peer messages (L1Mado35.RevEntryR15, then L1Mado35.RevQuoteS210
   correcting it) reported that a *sibling wave's* scratch tree was **relocated**, not deleted:
   `.ufo/waves/round-35/scratch/<Seat>/` → `.ufo/waves/round-35/scratch-evidence/<Seat>/`. This
   item cites no round-35 scratch path and wrote no such path, so nothing here dangles and no
   citation needs the added path segment. Recorded as peer-reported; I did not inspect the
   round-35 tree (outside this lane's bounds) and I do not cite the checkpoint commit hash those
   messages name, because I have not verified it against bytes — an unverified revision token in
   a cell would be exactly the class-B defect this round exists to remove.
8. **Durability of this evidence.** This report body is the evidence locus: it inlines the fetch
   command and its `200 40146` receipt, the final URL and zero-redirect result, the exact
   tag-strip command, both byte counts, both sha256 digests, and every quoted span verbatim with
   its snapshot line numbers. The two files under `w1/evidence/` are a convenience copy, not the
   claim: the digest in §3 identifies the bytes any copy must have, and the `PRESENT` checks in §4
   are re-runnable from the snapshot alone. If that directory were lost or relocated, no
   statement in this report becomes unsupported — a re-fetch plus the recorded command must
   reproduce `aa21fdcbc8f7226e1e05cac5ab89818abb0ad4b9dd9743a8f42b231a99b99511`, or the
   divergence must be reported rather than assumed away.

---

Report: `.ufo/waves/round-22/attempt2/w1/SnapTrashSpec.md`

Evidence:
- `.ufo/waves/round-22/attempt2/w1/evidence/snap-trashspec.raw` (40146 B, `353442d2ed3db0ff0c59632796214df56ba24973621f2e7899711921ee454ae4`)
- `.ufo/waves/round-22/attempt2/w1/evidence/snap-trashspec.txt` (24788 B, `aa21fdcbc8f7226e1e05cac5ab89818abb0ad4b9dd9743a8f42b231a99b99511`)
