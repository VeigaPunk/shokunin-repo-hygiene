# S230 — bubblewrap(1) man page source (`bwrap.xml`, tag v0.13.1)

Drafted by seat `SwarmScribe33` for L1 `SoujiR34a2` (single integration owner: it alone lands
`corpus/SOURCES.md` and `corpus/lessons/round-34.md`). Nothing below is committed by this seat.

## Fetch record

| field | value |
|---|---|
| fetched URL | https://raw.githubusercontent.com/containers/bubblewrap/v0.13.1/bwrap.xml |
| registry source URL (page) | https://github.com/containers/bubblewrap/blob/v0.13.1/bwrap.xml |
| HTTP status | 200 (`HTTP/2 200`) |
| content-type | `text/plain; charset=utf-8` |
| content-length header / bytes received | 33289 / 33289 |
| sha256 | `2cb77df2f4be0b2a0302bb2f0a260fdb4d9e1299b76481ea66ed34c40f5be1da` |
| date header | `Tue, 27 Oct 2026 11:40:31 GMT` |
| saved bytes (not committed by me) | `.ufo/waves/round-34/w1/src-S230.html` — 33289 bytes, sha256 re-checked after copy, identical |
| access date | 2026-10-27 |
| host tool | `/usr/bin/bwrap` → `bubblewrap 0.13.1` (`bwrap --version`, exit 0) — the host runs the same tag the bytes were taken from |

Fetch receipt:

```
$ curl -sS -D hdr.txt -o bwrap-v0.13.1.xml -w 'HTTP %{http_code} bytes %{size_download}\n' \
    https://raw.githubusercontent.com/containers/bubblewrap/v0.13.1/bwrap.xml
HTTP 200 bytes 33289
$ grep -iE '^(HTTP/|content-type|content-length|date)' hdr.txt
HTTP/2 200
content-type: text/plain; charset=utf-8
date: Tue, 27 Oct 2026 11:40:31 GMT
content-length: 33289
$ sha256sum bwrap-v0.13.1.xml
2cb77df2f4be0b2a0302bb2f0a260fdb4d9e1299b76481ea66ed34c40f5be1da  bwrap-v0.13.1.xml
$ cp … bwrap-v0.13.1.xml /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w1/src-S230.html
$ wc -c src-S230.html && sha256sum src-S230.html
33289 src-S230.html
2cb77df2f4be0b2a0302bb2f0a260fdb4d9e1299b76481ea66ed34c40f5be1da  src-S230.html
$ cat /proc/loadavg   # beside the reading (Q77)
21.70 12.06 6.09 21/6961 1212951
$ grep -c '|' src-S230.html
0
```

Screened and not used: `https://raw.githubusercontent.com/containers/bubblewrap/main/README.md`
— HTTP 200, 10687 bytes, sha256 `0c1dc12c6d94017c45e220fc0e5b679f24c0f09494bdd4bc7157d8abcd75c001`;
its only `--ro-bind` occurrence is an example line (`:111`), it documents no flag semantics.
No `pacman`, no install, no upgrade was performed for this row; `curl` and `sha256sum` are host
binaries already present.

## Aligned anchors in the fetched bytes (`src-S230.html` = `bwrap.xml` at v0.13.1)

| anchor | line(s) | verbatim fragment (copied from the bytes) |
|---|---|---|
| § DESCRIPTION, filesystem namespace | `:49` | `It works by creating a new, completely empty, filesystem namespace where the root` |
| § DESCRIPTION, invisibility | `:50` | `is on a tmpfs that is invisible from the host, and which will be automatically` |
| § DESCRIPTION, mount namespace default | `:56` | `creates a new mount namespace for the sandbox.` (preceded on the same line by man markup wrapping the command name) |
| § Options, `--bind` | `:295-296` | `--bind SRC DEST` term, then `Bind mount the host path` … `on` … (SRC/DEST are `<arg>` markup) |
| § Options, `--ro-bind` | `:311-312` | `--ro-bind SRC DEST` term, then `Bind mount the host path` … `readonly` … |

Honest limit of the bytes: the page states a new mount namespace per sandbox and a filesystem
namespace invisible from the host, and it states that `--bind` bind-mounts the host path `SRC` on
`DEST` (`--ro-bind` readonly). It never prints a sentence saying the host destination is
unaffected; that the host path is untouched follows from the per-sandbox mount namespace
(`[INFERENCE]`, the direct consequence, not an explicit sentence in the bytes).

## Proposed registry row (11 cells, append after the `S229` row)

```
| S230 | bubblewrap(1) man page source, `bwrap.xml` at tag v0.13.1 — https://github.com/containers/bubblewrap/blob/v0.13.1/bwrap.xml | docs | A | the mount semantics of `--bind SRC DEST` and `--ro-bind SRC DEST` inside bwrap's default new mount namespace, the mechanism the round-34 C2 N3 leg uses to give a sandbox a private writable stand-in for `/var/tmp`; not the kernel mount(2) API, not the permission/cgroup/capability rules, and not the `--dev-bind` device case | § DESCRIPTION `:49-50` (filesystem namespace invisible from the host) and `:56-57` (a new mount namespace by default); § Options `--bind :295-297`, `--ro-bind :311-313`; `bwrap.xml` at tag v0.13.1, host `bubblewrap 0.13.1`; HTTP 200, 33 289 bytes, sha256 2cb77df2f4be0b2a0302bb2f0a260fdb4d9e1299b76481ea66ed34c40f5be1da, fetched 2026-10-27 | `--bind` bind-mounts the host path SRC on DEST and `--ro-bind` mounts it readonly, and bwrap creates a new mount namespace per sandbox by default, so that mount belongs to the sandbox; the page does not itself state that the host destination is unaffected | mined | 2026-10-27 | 180d | corpus/lessons/round-34.md |
```

Header of the registry it must fit (`corpus/SOURCES.md`, at freeze `2b0171e2`):
`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |` — 11 cells, matches.

## Proposed `## Gate` entry for `corpus/lessons/round-34.md`

Shape copied from `corpus/lessons/round-33.md:19-29` (`| Candidate | Decision | Source reopened | Located quote / evidence | Reason / flip |`):

```
| `S230` bubblewrap(1) man page source, `bwrap.xml` at tag v0.13.1 | ADMIT (new row, `mined`; scope restricted to the `--bind`/`--ro-bind` mount semantics) | https://github.com/containers/bubblewrap/blob/v0.13.1/bwrap.xml — HTTP 200, 33 289 bytes, sha256 `2cb77df2…be1da`, fetched 2026-10-27; bytes at `.ufo/waves/round-34/w1/src-S230.html`; host `bubblewrap 0.13.1` | § DESCRIPTION `:56` — "creates a new mount namespace for the sandbox." | C2 leg N3 binds a private writable directory over `/var/tmp` inside the sandbox; a mount namespace per sandbox is what keeps the pinned fixture's bytes on the host untouched. The page states that namespace and, at § Options `:295-296`/`:311-312`, that `--bind`/`--ro-bind` "Bind mount the host path" SRC on DEST (writable, or "readonly"); it prints no explicit sentence that the host destination is unaffected, and the row's teaches cell says so. |
```

## Optional provenance sentence above `## Registry` (REG-pattern precedent; L1's call)

> Round-34 source opening: new S230 was opened live on 2026-10-27 by wave-1 scribe SwarmScribe33 for the C2 N3 private-bind mechanism; URL, access date and a 25-word located quote are in `corpus/lessons/round-34.md` `## Gate`, the fetched bytes and their sha256 in `.ufo/waves/round-34/w1/src-S230.html`. No existing row changed.

## Collision check (run first, at the freeze commit)

```
$ git -C …/souji-shokunin show 2b0171e2…:corpus/SOURCES.md | grep -cE '^ {0,3}\|[[:space:]]*S230'
0
$ git -C …/souji-shokunin show 2b0171e2…:corpus/SOURCES.md | grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' | grep -oE 'S[0-9]+' | sort -u | wc -l
153
$ grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' …/corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort | tail -5
S225 S226 S227 S228 S229
```

`S230` is not a registry row anywhere. Historical **non-registry** mentions exist and are disclosed
so the id is not mistaken for a reuse: `corpus/lessons/round-24.md:207` ("staged S230 is a different
URL" — a staged candidate never appended), `census/round-31/waves/w1/deliver-lesson-gate.md`
(S226-S228/S230 named as a merge package's upcoming ids), `census/round-32/waves/w1/deliver-assim-sweep.md`
(that package's S230 = git-worktree 2.56.0, never appended). This mirrors the round-33 note that
S224 in `corpus/lessons/round-32.md` was never a registry row.
