STATUS: PASS

Item: C2 / restorable-quarantine-staging re-grounding snapshot — Gio.File.trash, § Description recoverability sentence.
Scope kept: wrote only the two named evidence files plus this report. No lane repo writes elsewhere, no git/jj, no cleanup, no process signals, no tool installs (nothing installed or updated).

## 1. Fetch (executed)

Command as issued:

```
curl -fsSL -m 45 -A 'souji-r22-restructure/1.0' \
  -o /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence/snap-filetrash.raw \
  -w '%{http_code} %{size_download} %{url_effective}\n' \
  'https://docs.gtk.org/gio/method.File.trash.html'
```

Observed output (verbatim):

```
200 19401 https://docs.gtk.org/gio/method.File.trash.html
```

- Fetch date: **2026-10-25** (file mtime `2026-10-25 03:45:03 -0300`; capture confirmed at `utc_now=2026-10-25T06:45:39Z`).
- HTTP code: **200**.
- Bytes downloaded: **19401** (`size_download`), and on-disk `size=19401` (`stat`), i.e. complete body.
- Final URL after redirects: **https://docs.gtk.org/gio/method.File.trash.html** — identical to the requested URL, so **no redirect occurred** (`url_effective` is the evidence).
- Served document is static HTML, not JS-only: the `<div class="docblock">` text is present in the raw bytes (see § 3). No headless browser was needed and none was used.

## 2. Text snapshot derivation (executed)

Command as issued (exact; `argv[1]` = the raw path above, stdout redirected to `snap-filetrash.txt`):

```
python3 -c '
import sys
from html.parser import HTMLParser
BLOCK={"p","div","h1","h2","h3","h4","h5","h6","li","br","tr","td","dt","dd","pre"}
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.o=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in ("script","style"): s.skip+=1
        elif t in BLOCK: s.o.append("\n")
    def handle_endtag(s,t):
        if t in ("script","style"):
            if s.skip: s.skip-=1
        elif t in ("p","div","h1","h2","h3","h4","h5","h6","li","tr"): s.o.append("\n")
    def handle_data(s,d):
        if not s.skip: s.o.append(d.replace("\n"," "))
p=P(); p.feed(open(sys.argv[1],encoding="utf-8",errors="replace").read())
lines=[" ".join(l.split()) for l in "".join(p.o).split("\n")]
out=[l for l in lines if l]
sys.stdout.write("\n".join(out)+"\n")
' snap-filetrash.raw > snap-filetrash.txt
```

Result: UTF-8, **4140 bytes, 32 lines**, script/style content excluded, block boundaries as line breaks, all whitespace collapsed, words kept in document order (entities decoded via `convert_charrefs=True`, so `&nbsp;` renders as a space and `&#8220;/&#8221;` become curly quotes). Verification output from `wc -c -l` / `stat`: `4140`, `size=4140`.

## 3. Hashes (executed, `sha256sum`)

| file | sha256 | bytes |
|---|---|---|
| `…/w1/evidence/snap-filetrash.raw` | `a5af1920b16444e0a03d30fcf77de0389533bcedb7243175c915b34c38c21cf3` | 19401 |
| `…/w1/evidence/snap-filetrash.txt` | `23fb07ce8ca4946f49a78b7a3d00f7bcba45ec246219b5d47432b6d6d2a86c5e` | 4140 |

## 4. Located passage — verbatim quote with locator

Source: https://docs.gtk.org/gio/method.File.trash.html, **§ Description** (the `id="description"` block, first docblock paragraph, second sentence) of `gboolean g_file_trash (GFile* file, GCancellable* cancellable, GError** error)`.

> "This is similar to deleting it, but the user can recover it before emptying the trashcan."

- Length: **16 words** (limit 25).
- Locator tokens: `§ Description`, plus the surrounding first paragraph's opening "Sends file to the “Trashcan”, if possible." and the signature above it.
- Verbatim check (executed, whitespace-collapsed against the committed text snapshot):

```
words: 16
verbatim_in_txt: True
LOCATOR_CONTEXT: Description [src] Sends file to the “Trashcan”, if possible. This is similar to deleting it, but the user can recover it before emptying the trashcan. Trashing is disabled for system mounts by default (see g_unix_mount_entry_is_system_internal()), so this call can return the G_IO_ERROR_NOT_SUPPORTED error. …
```

C2-predicate fit for this URL (executed + source-read): predicate 3 is satisfiable from the sentence above (16 words, locator present); predicate 4 needs the Gate line's `snapshot:` path to be under `--snapshot-dir` and to contain the span verbatim — see finding F1.

## 5. Findings (bounded)

**F1 — duplicate snapshot of the same URL already exists under the frozen `--snapshot-dir`, with byte-identical raw.** (executed) `census/round-22/attempt2/sources/` holds `gtk-filetrash.raw` and `gtk-filetrash.txt` (mtime 03:36/03:37, a different seat). Measurements:

```
a5af1920b16444e0a03d30fcf77de0389533bcedb7243175c915b34c38c21cf3  gtk-filetrash.raw
8bed4dac2aacf3de7b58fcc3ce5e3d6baf6a98841700b59c3ad152c3fd8673c9  gtk-filetrash.txt
gtk-filetrash.txt has_quote: True
RAW_BYTES_IDENTICAL
```

So (a) the HTTP body is byte-stable between the two independent fetches — digest agreement is a real receipt, not a coincidence; (b) `snap-filetrash.raw` and `census/.../gtk-filetrash.raw` are the *same* 19401 bytes; (c) the **text** renderings differ (`4140` vs `4904` bytes, different `sha256`) because each seat used a different stripper, but the sibling text already contains the quoted span verbatim.

**F2 — Gate should cite the snapshot dir path, not this file.** (source-inferred from frozen contract + tool source) `tools/souji-gate-check.py:80` resolves `snap_root = normpath(join(root, --snapshot-dir))` and predicate 4 requires the named snapshot to live under it. My artifact lives at `.ufo/waves/round-22/attempt2/w1/evidence/snap-filetrash.txt`, which is **outside** `census/round-22/attempt2/sources`. Consequence for the entry author: a `snapshot:` line naming my path would fail predicate 4, while naming `census/round-22/attempt2/sources/gtk-filetrash.txt` passes (F1c). I did not copy bytes into the snapshot dir — that path is owned by another seat and my write authority covers only the two named files. This item therefore supplies the adjudicating duplicate + the quote; it does not itself satisfy predicate 4.

**F3 — two digests exist for "the same" snapshot; quote binding must name one.** (executed) `gtk-filetrash.txt` and `snap-filetrash.txt` are not interchangeable by digest (`8bed4d…` vs `23fb07…`). Any entry that records a sha256 alongside the quote must pair it with the exact file name it measured; either text file is sufficient for verbatim matching, neither is sufficient to validate the other's digest.

**F4 — availability rule not triggered.** (executed) HTTP 200 with static, tag-strippable body. No JS-only/unreachable condition occurred, so no invented or paraphrase-substituted quote was needed or used.

**F5 — no side effects.** (executed) This seat created exactly three paths and no others: `…/w1/evidence/snap-filetrash.raw`, `…/w1/evidence/snap-filetrash.txt`, `…/w1/SnapFileTrash.md`; it created no scratch directory and therefore cites no scratch path (the round's `scratch/` tree was relocated to `scratch-evidence/` per peer correction at ~03:45, not deleted; either way nothing here dangles — all three paths were re-listed afterwards, digests unchanged). Other files present in `w1/evidence/` (`slice*`, `snap-*`, `mutquote-work/`) belong to sibling seats, not this one. No deletion authority, no repository mutation, no process signalling, no network write, nothing read from `/proc`, credentials, private TSVs, `.tower`, or operator-sweep census contents.

## 6. Risks / hand-off notes

- R1 (risk): the description sentence asserts user-level recoverability of `g_file_trash`; it says nothing about a *no-clobber rename primitive* or per-item origin records. If the theme's other leg needs a source for those, this URL does not carry it — it only grounds "trash is recoverable", which is the premise, not the mechanism.
- R2 (risk, source-inferred): the sibling `gtk-filetrash.txt` (4904 B) and mine (4140 B) will keep disagreeing; a later census that treats text-snapshot size as an identity signal will flag a false duplicate. Recommend the entry cite one and record its digest.
- R3 (durability, from the peer relocation/checkpoint lesson): the durable evidence locus for this item is **this report body**, which inlines the fetch receipt, both sha256 digests, the stripper command, the locator and the 16-word quote verbatim — so the C2 predicate-3 material survives loss of any scratch or evidence directory. The two `w1/evidence/` files are convenience copies for byte-level re-verification, and their content is independently reproducible from the same URL (raw digest `a5af19…` was reproduced independently by the snapshot-dir seat, see F1). No claim is made here about the git tracking status of either copy — that was not measured.
- Hand-off: nothing to verify beyond what is printed above; the parent's `souji-gate-check.py` run over the two entries is the only check that consumes this item, and per F2 it consumes the `census/.../sources` copy.
