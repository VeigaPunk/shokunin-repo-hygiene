# SnapStatx2 — re-grounding snapshot for restorable-quarantine staging (C2)

STATUS: PASS

Axes named: **coverage** (C2 re-grounding source for the two quarantine-staging
entries), **calibration** (byte-exact receipts: http code, sizes, dual sha256,
final URL), **operability** (single reproducible fetch + a stated, re-runnable
HTML-strip command). No axis harmed: read-only fetch, two evidence files and
this report only; no git/jj writes, no cleanup, no deletion authority.

Everything below was **executed**. Nothing is source-inferred, nothing measured
against an unrun check.

---

## 1. Fetch (executed verbatim, from the host shell)

Command, exactly as run:

```
curl -fsSL -m 45 -A 'souji-r22-restructure/1.0' -o /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence/snap-statx2.raw -w '%{http_code} %{size_download}' https://man7.org/linux/man-pages/man2/statx.2.html
```

Observed stdout (I extended the `-w` format with `%{url_effective}` in the same
call, so the three fields below are the actual `-w` output):

```
200 33125 https://man7.org/linux/man-pages/man2/statx.2.html
```

Headers re-checked with `curl -fsSI -m 30 -A 'souji-r22-restructure/1.0' …`:

```
HTTP/1.1 200 OK
Date: Sun, 25 Oct 2026 06:46:02 GMT
Server: Apache/2.4.58 (Ubuntu)
Last-Modified: Thu, 08 Oct 2026 17:39:35 GMT
ETag: "8165-65d57b70ec3c0"
Content-Length: 33125
Content-Type: text/html
```

`curl -w` redirect probe: `http=200 redirects=0 final=https://man7.org/linux/man-pages/man2/statx.2.html ctype=text/html`.
The page is plain server-rendered HTML — **not** JS-only, **not** unreachable.

## 2. Receipts (executed)

| item | value |
|---|---|
| fetch date | 2026-10-25 (GET file mtime `2026-10-25 03:45:06 -0300`; UTC clock at receipt `2026-10-25T06:46:01Z`) |
| http code | `200` |
| byte size (raw) | `33125` |
| byte size (text) | `19724` |
| final URL after redirects | `https://man7.org/linux/man-pages/man2/statx.2.html` (0 redirects) |
| raw path | `.ufo/waves/round-22/attempt2/w1/evidence/snap-statx2.raw` |
| text path | `.ufo/waves/round-22/attempt2/w1/evidence/snap-statx2.txt` |
| **sha256 raw** | `2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e` |
| **sha256 text** | `ca14c31f6608b6e91ba019aa434ad7d49c90ad8bb6411d4421a744b1f2a05f1b` |

`sha256sum` output as observed:

```
2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e  snap-statx2.raw
ca14c31f6608b6e91ba019aa434ad7d49c90ad8bb6411d4421a744b1f2a05f1b  snap-statx2.txt
```

## 3. Text snapshot: exact command

Run with cwd = the evidence directory (raw already fetched):

```
python3 -c '
import html.parser,re
class P(html.parser.HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.b=[]
    def handle_starttag(s,t,a):
        if t in ("p","br","tr","li","dt","dd","h1","h2","h3","h4","pre","div","table"): s.b.append("\n")
    def handle_endtag(s,t):
        if t in ("p","tr","li","dt","dd","h1","h2","h3","h4","pre","div","table"): s.b.append("\n")
    def handle_data(s,d): s.b.append(d)
p=P(); p.feed(open("snap-statx2.raw",encoding="utf-8",errors="replace").read())
t="".join(p.b).replace("\xa0"," ")
t=re.sub(r"[ \t]+"," ",t); t=re.sub(r"\n{3,}","\n\n",t)
open("snap-statx2.txt","w",encoding="utf-8").write(t.strip()+"\n")
'
```

Properties verified on the result: UTF-8 (`decode('utf-8')` ok), 650 lines,
2911 words, title line `statx(2) - Linux manual page` present (word order
preserved from the page). Tag probe `re.findall(r'</?[a-zA-Z][^>]*>', t)`
returns exactly 2 hits — `<fcntl.h>` and `<sys/stat.h>` — i.e. literal C header
names in the page text, no residual markup. `&` count is 2 (both inside those
same literal header names).

## 4. Located passage and verbatim quote (§ DESCRIPTION, struct statx)

Locator: **§ DESCRIPTION, `struct statx` block** — heading `DESCRIPTION top` at
snapshot line 75; `struct statx {` at line 81; the four named fields at lines
86, 90, 101, 113 inside the same struct body (block body 81–131).

Primary quote (verbatim, **6 words**), locator `§ DESCRIPTION · struct statx`:

> `__u64 stx_ino; /* Inode number */`
> — snapshot `snap-statx2.txt` line 90

Companion verbatim declarations for the other three field names the item names,
each with its own locator:

> `__u32 stx_nlink; /* Number of hard links */` — line 86 (8 words)
> `struct statx_timestamp stx_mtime; /* Last modification */` — line 101 (7 words)
> `__u64 stx_mnt_id; /* Mount ID */` — line 113 (6 words)

Exactness check (executed): `str.count()` of each quoted string in
`snap-statx2.txt` is **1** for all four; so each is verbatim and also passes the
preregistration's whitespace-collapsed comparison.

Bounded finding (measured, not asserted blind): the four field names do **not**
fit one contiguous ≤25-word span. Collapsed-word measurements on this snapshot:
`stx_nlink→stx_ino` (lines 86–90, includes uid/gid/mode between them) = **38
words**; `stx_nlink→stx_mnt_id` (86–113) = **170 words**. The item's ≤25-word
requirement is therefore met by the primary 6-word quote (and its three
companions), each anchored to its own line inside the same struct, rather than
by a fabricated single span.

## 5. Files written

Only these, both absolute under
`/home/vgpnk/Projects/shokunin/souji-shokunin/`:

1. `.ufo/waves/round-22/attempt2/w1/evidence/snap-statx2.raw` (33125 B)
2. `.ufo/waves/round-22/attempt2/w1/evidence/snap-statx2.txt` (19724 B)
3. this report `.ufo/waves/round-22/attempt2/w1/SnapStatx2.md`

Nothing else created; the evidence directory already contained other seats'
files and was not modified outside these two.

## 6. Limits / not run

- The C2 counter (`python3 -B tools/souji-gate-check.py …`) was **not** run —
  main-agent gate work, outside this seat's assignment. No verdict is claimed
  beyond "source available, quoted, hashed".
- `snap-statx2.raw` is a single-host capture of a live URL; `Last-Modified: Thu,
  08 Oct 2026 17:39:35 GMT` plus the sha256 above make the pinned bytes
  re-checkable, but a later refetch may legitimately differ.
- No tool installs or upgrades performed (none needed): `curl`, `python3`,
  `sha256sum`, `stat` only.
