STATUS: PASS

# C2 re-grounding snapshot — glib2 `gio(1)`, § `trash` COMMAND (`--list` / `--restore`)

Seat `L1Souji22.SnapGio1`. Scope executed: fetch + UTF-8 text snapshot + located verbatim quote for the
`restorable-quarantine-staging` theme (C2). No verdict on C1/C2 is issued here; the frozen counters were
not run (parent owns post-integration gate execution).

Preregistration read first: `.ufo/waves/round-22/attempt2/preregistration.txt` (frozen 2026-10-25,
base `4edb25dfe262515d0da63224bbba71e02e36cba5`). No counter, predicate or kill rule is redefined below.

## 1. Fetch record (executed)

First attempt with the assigned command failed transiently:

```
curl: (35) TLS connect error: error:0A000126:SSL routines::unexpected eof while reading
000 0 https://man.archlinux.org/man/gio.1.en
exit=35
```

Three immediate retries of the identical command all returned `200 size=26697` (exit 0), and the host was
independently reachable (`getent hosts man.archlinux.org` → `2604:cac0:a104:d::`;
`curl https://man.archlinux.org/` → 200; `--http1.1` variant → 200). The delivered file was then produced
by the assigned command verbatim:

```
curl -fsSL -m 45 -A 'souji-r22-restructure/1.0' -o /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence/snap-gio1.raw -w '%{http_code} %{size_download}\n' https://man.archlinux.org/man/gio.1.en
200 26697
exit=0
```

| field | value |
|---|---|
| fetch date | **2026-10-25** (system clock at capture: `2026-10-25T06:45:54Z`) |
| requested URL | `https://man.archlinux.org/man/gio.1.en` |
| final URL after redirects | `https://man.archlinux.org/man/gio.1.en` (`num_redirects=0`, `%{url_effective}`) |
| http code | **200** |
| bytes downloaded | **26697** |
| raw snapshot | `.ufo/waves/round-22/attempt2/w1/evidence/snap-gio1.raw` (26697 B) |
| sha256 raw | `3e7876d838c665f9afbd4e36c4fb7c022e946a44fccba7789b230ccb57419e84` |
| text snapshot | `.ufo/waves/round-22/attempt2/w1/evidence/snap-gio1.txt` (12125 B, 236 lines, valid UTF-8) |
| sha256 text | `cc4af34906f691370d4a1ea51ceae378b697a3673001a5150e0bb1543dd56f68` |

Determinism control (executed): the retry bodies were byte-identical to the delivered raw file
(`cmp -s snap-gio1.raw /tmp/gio1.try1` and `/tmp/gio1.try3` → identical), so the raw bytes are stable
across independent fetches, not a single lucky response.

## 2. Exact text-extraction command (executed)

`python3` + `html.parser`, entities decoded (`convert_charrefs=True`), block-level elements only become
line breaks, source-level wrapping is collapsed so sentences stay whole, empty lines dropped, UTF-8 out:

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence && python3 - <<'PY'
from html.parser import HTMLParser

class Text(HTMLParser):
    BLOCK = ("p","div","br","h1","h2","h3","li","tr","section","table","ul","ol")
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style"): self.skip+=1
        if tag in self.BLOCK: self.out.append("\n")
    def handle_endtag(self,tag):
        if tag in ("script","style") and self.skip: self.skip-=1
        if tag in self.BLOCK: self.out.append("\n")
    def handle_data(self,data):
        if not self.skip: self.out.append(data.replace("\n"," "))

src="snap-gio1.raw"; dst="snap-gio1.txt"
p=Text(); p.feed(open(src,encoding="utf-8",errors="replace").read())
lines=[" ".join(l.split()) for l in "".join(p.out).split("\n")]
open(dst,"w",encoding="utf-8").write("\n".join(l for l in lines if l)+"\n")
print("wrote",dst)
PY
wrote snap-gio1.txt
```

No HTML word is dropped or reordered: `handle_data` writes every text node in document order; `script`/
`style` nodes are the only skipped content and the page has no substantive body text inside them (the
page is a static man-page render — not JS-only: the quoted sentences are present in the raw HTML).

## 3. Located verbatim quote — § `trash` COMMAND, `--list` / `--restore`

Locator: `§ COMMANDS › trash` (`snap-gio1.txt` line 200, `trash [OPTION…] [LOCATION…]`), Options block,
`--list` at line 209 / its sentence line 210, `--restore` at line 211 / its sentence line 212.

- `--list` sentence — 9 words:
  "List files in the trash with their original locations."
- `--restore` sentence — 9 words:
  "Restore a file from trash to its original location."

Both quoted spans verified verbatim against the delivered snapshot by
`python3 - <<'PY' … q in " ".join(t.split()) … PY` → `words= 9 verbatim_collapsed=True` and
`words= 9 verbatim_collapsed=True`; combined 18 words, each individual quote ≤ 25 words. Checking the
raw HTML directly confirms the same words in the same order (`--list`/`--restore` headings with their
`Bd-indent` bodies).

Adjacent, not quoted here (paraphrase only, to keep the quote inside the 25-word cap): the same
`--restore` paragraph goes on to say that a `trash://` URI is expected and that a missing original
directory is recreated; the `trash` command description says files are sent to / restored from the
“Trashcan”, whose location is `$XDG_DATA_HOME/Trash` in the common home-directory case.

## 4. Finding: this capture duplicates a snapshot that is already committed

Read-only comparison against the lane's existing snapshot directory (`--snapshot-dir` in the frozen
counter is `census/round-22/attempt2/sources`):

```
sha256 census/round-22/attempt2/sources/arch-gio.1.raw  = 3e7876d838c665f9afbd4e36c4fb7c022e946a44fccba7789b230ccb57419e84
sha256 .ufo/.../w1/evidence/snap-gio1.raw               = 3e7876d838c665f9afbd4e36c4fb7c022e946a44fccba7789b230ccb57419e84   (cmp → identical)
sha256 census/round-22/attempt2/sources/arch-gio.1.txt  = 546462a5aa6769a86d7a634434088a874f06c7725b0c3ec0600ac81b5031a12d  (12626 B)
sha256 .ufo/.../w1/evidence/snap-gio1.txt               = cc4af34906f691370d4a1ea51ceae378b697a3673001a5150e0bb1543dd56f68  (12125 B)
```

Consequences for the C2 Gate (parent decision, not mine to make):

- The URL's bytes are already captured in the lane at `census/round-22/attempt2/sources/arch-gio.1.raw`
  with the same sha256 — an independent re-fetch reproduced the committed bytes, which is a
  re-grounding receipt rather than a second artifact. Committing `snap-gio1.raw` too would be a
  duplicate artifact of identical content.
- Both frozen quotes are present (whitespace-collapsed) in the pre-existing
  `census/round-22/attempt2/sources/arch-gio.1.txt` (`True` for both, at its lines 563 and 568), so a Gate
  naming that committed snapshot satisfies the per-entry predicate without moving bytes.
- The two `.txt` files are **not** byte-identical (12626 vs 12125 B) because they were produced by
  different strippers (the existing one keeps source wrapping; mine collapses blocks into whole
  sentences). Quote membership was verified in both, so either names a valid snapshot; the Gate must
  name exactly the one whose path it cites and must not mix digests across the two.

## 5. Executed vs inferred

- Executed: the fetch commands and their `-w` outputs; the TLS failure and its retries; the strip script;
  `sha256sum` on all four files; `cmp` identity checks; `wc`/`file`/UTF-8 decode check; the verbatim and
  word-count checks above; `grep -n` locators; read-only listing/hashing of the pre-existing snapshot dir.
- Inferred (not measured here): that the C2 `Gate` block will accept these two quotes once the parent
  writes the entry — I did **not** run `tools/souji-gate-check.py` (entries do not exist yet, and the
  wave is in flight). No gate verdict is claimed.

## 6. Bounds, tools, risks

- Wrote exactly two files: `snap-gio1.raw`, `snap-gio1.txt` under
  `.ufo/waves/round-22/attempt2/w1/evidence/`, plus this report. No other path was created or modified;
  no git/jj write, no deletion authority, no lane index/state/MANIFEST/`.ufo/state`/watchdog contact, no
  sibling repo touched; `shokuknow` untouched; no credentials, `/proc`, `.tower`, private TSVs or
  operator-sweep census contents read.
- Tools: none installed or upgraded (no pacman/uv/npx transaction); used pre-existing
  `curl 8.23.0 (OpenSSL/3.6.5)` and `Python 3.14.8` only.
- Risk 1 (transport): the endpoint dropped TLS mid-handshake once (`curl: (35)`) before three clean 200s.
  A future Gate re-fetch should be tolerant of one retry; the raw sha256 is the stability anchor.
- Risk 2 (placement): my assigned output lives under `w1/evidence/`, while the frozen counter's
  `--snapshot-dir` is `census/round-22/attempt2/sources`. If the Gate is to name my file it must be
  staged there by the parent; otherwise the byte-identical committed `arch-gio.1.txt` should be cited and
  my copy left as the wave's independent re-fetch receipt.
- Risk 3 (quote scope): the two quotes are separate, each 9 words (18 combined). They cover exactly the
  `--list` and `--restore` sentences named in the item; the `trash://`-recreation clause is deliberately
  left out of the quotation to stay inside the 25-word cap and is paraphrased in §3.
