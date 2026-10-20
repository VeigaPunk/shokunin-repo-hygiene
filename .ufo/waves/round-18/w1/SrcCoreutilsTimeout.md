STATUS: DONE — one draft SOURCES row for the GNU timeout `--foreground` caveat, grounded on a Wayback capture (live gnu.org unreachable from this host) plus the installed coreutils 9.12-2 info manual; S038 is the same URL under a different scope and its line anchors no longer resolve after today's package upgrade.

# SrcCoreutilsTimeout — source item: timeout `--foreground` and descendants

## 1. Access record

| object | attempt | result |
|---|---|---|
| https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html | `read` tool fetch | `Failed to fetch URL; Cause: The operation timed out.` |
| same | `curl -sS --max-time 45 …` | `curl: (28) Connection timed out after 45001 milliseconds`; 0 bytes written |
| same, `-4` | 20 s each | https `000 20.002515` FAIL; http `000 20.001930` FAIL; `https://www.gnu.org/` `000 20.001562` FAIL |
| DNS | `getent ahostsv4` / `ahostsv6` | A `209.51.188.116` and AAAA `2001:470:142:5::116` both resolve — the failure is connect timeout, not name resolution |
| Wayback | `https://web.archive.org/web/2026id_/…timeout-invocation.html` with `-L` | `http=200`; `memento-datetime: Sat, 19 Sep 2026 21:28:56 GMT`; `x-archive-orig-content-length: 3530`; `content-encoding: gzip` |
| capture body | gunzip | 11813 bytes HTML; sha256 `8e0c74666b842b0f745455f9e853ba65f82776f379d57640d26291555e85259c` |
| capture heading | `<title>` and rendered text | `timeout invocation (GNU Coreutils 9.12)`; no “last updated” line served (regex count 0) |
| installed vendor copy | `/usr/share/info/coreutils.info.gz` | coreutils `9.12-2` (`pacman -Q`); file sha256 `a2478c0f130ea61db02efefdf675e311a16ea16149bd0d309841d58bf77df494`; node `timeout invocation` starts :15710; `-f` :15726, `--foreground` :15727; caveat sentence :15737-15738 |

`/var/tmp` artifacts were deleted after the digests were taken; the capture is reproducible from the `id_` Wayback URL above (20260919212856).

## 2. Draft row

Provisional id **S067**: S064/S065 are already drafted by `ScribeRowsGit.md` (attr.c, cat-file) and S064/S065 by `ScribeRowsJobs.md` (bash job control, kill(2)), which also proposes S066 (`set -m`). L1 renumbers; the cells below are what matters.

```markdown
| S067 | GNU coreutils manual, timeout invocation — https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html | docs | A | the `--foreground` caveat that descendants are exempt from the timeout; not the group-signal mechanism (implementation), and not FIFO-open or shell job-control behaviour | live page unreachable from this host 2026-10-20 (read-tool fetch timed out; curl exit 28 over http, https and IPv4; A 209.51.188.116 and AAAA both connect-timeout); Wayback capture 20260919212856 (memento 2026-09-19 21:28:56 GMT) of the canonical URL, page heading "timeout invocation (GNU Coreutils 9.12)", no last-updated line, § 23.6 timeout invocation › --foreground; installed coreutils 9.12-2 /usr/share/info/coreutils.info.gz sha256 a2478c0f130ea61db02efefdf675e311a16ea16149bd0d309841d58bf77df494, node :15710, option :15726-15727, caveat :15737-15738 | with `--foreground` timeout creates no separate background program group, so descendants of COMMAND are not timed out and a blocked grandchild outlives the bound; a census watchdog must keep the default group model or signal its own process group, never `timeout -f` | queued | 2026-10-20 | on-release | — |
```

Cell check: 11 cells, no literal `|` inside a cell, `kind=docs`, `tier=A`, `status=queued` with `used-by —` (validator requires existing used-by paths for `mined`; `corpus/lessons/round-18.md` does not exist yet). Flip to `mined | 2026-10-20 | on-release | corpus/lessons/round-18.md` at landing when that lesson exists.

## 3. Quote verification

Primary quote (the assigned caveat), verbatim from the capture’s rendered text:

> In this mode of operation, any children of command will not be timed out.

- Words: **14** (`printf '%s\n' 'In this mode of operation, any children of command will not be timed out.' | LC_ALL=C wc -w`).
- Located: capture 20260919212856, § 23.6 `timeout invocation` → `--foreground` (`-f`); raw HTML is `<p>In this mode of operation, any children of <var class="var">command</var>\nwill not be timed out.` — the tag strips to the same words. Installed 9.12 info carries the identical sentence at :15737-15738, rendering the metavariable as `COMMAND`.
- Supporting fragment for the group model, verbatim from the installed 9.12 info :15728-15729 (the capture has the same words with a typographic apostrophe): “Don't create a separate background program group, so that the managed COMMAND can use the foreground TTY normally.” — **18** words.

## 4. What it teaches for souji r18 (C1)

1. **Never wrap the per-repo bound in `timeout -f/--foreground`.** The documented foreground mode starts no separate program group, and “any children of command will not be timed out”. The hung process in L1’s reproduction is a *grandchild* (`census_one` → bash → `git status` blocked in `open(2)`), so a foreground-mode wrapper would time out only the wrapper and leave the blocked git exactly as the 58 leaked processes now sit. The declared watchdog (`set -m` around the fork, SIGTERM to the group, SIGKILL 2 s later) is the group model the page describes as the default.
2. **The docs half is only the exemption.** The page says foreground mode exempts children; it does not say the default signals the group. The mechanism is in the implementation (supplementary, not part of this row): coreutils v9.12 `src/timeout.c` :567-572 `if (!foreground) setpgid (0, 0);` with the comment “Ensure we're in our own group so all subprocesses can be killed”, and :244-246 `if (!foreground) send_sig (0, sig);` — `kill(0, …)` reaches the group. Fetched from the GitHub mirror raw at tag v9.12, sha256 `bf1f0d998729f12ddd2323d69db34648763d807d9c4d769eb1414a8738652cc9`, byte-identical to v9.11.
3. **`timeout` cannot invoke `census_one`.** `emit_census` (:1394-1416) calls `census_one` (:1261) as a shell function (`if row=$(census_one "$repo")`, :1403). `timeout` execs COMMAND, so a function name is not a valid COMMAND; the fix’s fork must be a subshell or script, otherwise the bound never starts. [INFERENCE from exec semantics; the page only states COMMAND must not be a special built-in utility.]
4. **Do not inherit S038’s exit-status claims.** `--preserve-status` would replace 124 with COMMAND’s status; the contract’s rc mapping (timeout → `error` row, 2 → whole-run exit 2, other nonzero → exit 1) presumes the default 124 and must not add `-p`.

## 5. What it does NOT establish

- That the default sends the signal to the process group — only the implementation shows that (the page states the separate group exists, not the signal target).
- That descendants which `setsid()`/`setpgid()` into another group are covered. A group signal is bounded by PGID; nothing in the page or the code closes that escape.
- Anything about FIFO `open(2)` blocking (S062, fifo(7)) or git’s open of `$GIT_DIR/info/attributes` (S064 draft, attr.c:711 `open` before :718 `fstat`).
- Bash job-control behaviour: `set -m`, one pipeline = one job = one group (peer S064 draft and the set -m lead S066). The coreutils page names no shell mechanism.
- Reaping or zombie cleanup after the group dies; the page says nothing about wait semantics.
- A version stamp beyond the heading: no “last updated” line exists, and the Wayback capture is a third-party archive with no signature verification. Coreutils 9.12 is the page version; the host package is 9.12-2.
- Whether the lane’s watchdog actually works — this item is documentation only; no runtime was exercised.

## 6. Comparison with existing S038 (same URL, different scope) — and a drift finding

S038 (`corpus/SOURCES.md:54`) cites the same URL and node, scoped to `--kill-after` and exit-status locations; it says nothing about `--foreground` or descendants. This row is therefore a distinct-scope row: the validator should emit W04 (same URL across scopes, warning only) and no E04 (same URL + same scope). Do not add “supersedes S038” to this row, and do not edit S038’s scope to mention `--foreground`, or the pair becomes an E04 duplicate.

**Observed drift in S038, independent of this row.** S038’s anchor cell says “coreutils 9.11-2 … `--kill-after` lines 15319-15320; Exit status line 15365”. On this host now:

```
$ pacman -Q coreutils
coreutils 9.12-2
$ grep coreutils /var/log/pacman.log | tail -2
[2026-10-03T20:41:58+0000] [ALPM] installed coreutils (9.11-2)
[2026-10-20T09:16:28-0300] [ALPM] upgraded coreutils (9.11-2 -> 9.12-2)
$ zcat /usr/share/info/coreutils.info.gz | sed -n '4p'
This manual documents version 9.12 of the GNU core utilities, including
$ zcat /usr/share/info/coreutils.info.gz | grep -n 'Node: timeout invocation'
15710:File: coreutils.info,  Node: timeout invocation,  Prev: stdbuf invocation,  Up: Modified command invocation
$ zcat /usr/share/info/coreutils.info.gz | sed -n '15744p;15791p'
‘--kill-after=DURATION’
     124 if COMMAND times out, and ‘--preserve-status’ is not specified
$ zcat /usr/share/info/coreutils.info.gz | sed -n '15319,15320p;15365p'
     1 xyz 2 xyz 3
     1 xyz 2 xyz 3
‘\\’    A backslash character.  This escape sequence works inside
```

So the S038-cited lines now land in the `env` node, not `timeout`. The row was plausibly correct before the 09:16 upgrade; it is false now, and a re-open cannot reproduce it. The new C2 gate (`LG-DANGLING-PTR`) checks that a *path token* exists, so this line-anchor drift is invisible to it; Q25(b) covers `measured_commit`, not anchor lines.

Smallest fix: land a correction row whose `teaches` begins `supersedes S038` and whose anchor pins coreutils `9.12-2`, the info-file sha256 `a2478c0f…`, and the current lines (`--kill-after` :15744, exit status :15791), rather than rewriting landed cells in place if append-only is enforced. Policy line for C2: an anchor into a *mutable installed vendor file* must carry the file digest, because a package upgrade silently moves every line.

Candidate mined mistake for the round: **anchoring an authority row to an installed file by line number without a digest — the host upgraded the package the same day and the anchor stopped resolving.**

## 7. Verdict

- Draft row: **holds** for the quoted statement and the two located objects. The row’s teaching (foreground exempts descendants) is directly quoted; its implication for the watchdog is stated as design consequence, not as a page claim.
- C1 grounding: **partial by design** — this docs row grounds the hazard (descendants escape a direct-child signal) but not the group-signal mechanism; the mechanism needs the peer bash/kill rows or a code row (`src/timeout.c` :567-572, :244-246).
- S038: **fails to resolve** at its stated version/lines on this host after today’s upgrade; route the correction.

## 8. Exact commands run (all read-only)

```
read https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html
  → Failed to fetch URL; Cause: The operation timed out.
curl -sS --max-time 45 -D hdr -o …timeout.html <url>
  → curl: (28) Connection timed out after 45001 milliseconds; rc=28
curl -4 -sS -o /dev/null -w '%{http_code} %{time_total}\n' --max-time 20 <https|http|gnu.org>
  → 000 20.002515 / 000 20.001930 / 000 20.001562 (all FAIL)
getent ahostsv4 www.gnu.org → 209.51.188.116; getent ahostsv6 → 2001:470:142:5::116
curl -sSL --max-time 60 -o …timeout-wb.html 'https://web.archive.org/web/2026id_/<url>'
  → http=200, 3530 bytes gzip, memento-datetime Sat, 19 Sep 2026 21:28:56 GMT
zcat …timeout-wb.html > …-dec.html; sha256sum → 8e0c7466…
pacman -Q coreutils → coreutils 9.12-2
grep coreutils /var/log/pacman.log | tail -2 → installed 9.11-2 (2026-10-03); upgraded 9.11-2 -> 9.12-2 (2026-10-20T09:16:28-0300)
zcat /usr/share/info/coreutils.info.gz | grep -n 'Node: timeout invocation\|kill-after\|preserve-status\|foreground'
  → node 15710; -f/--foreground 15726-15727, caveat 15737-15738; --kill-after 15744; exit 124 15791
sha256sum /usr/share/info/coreutils.info.gz → a2478c0f130ea61db02efefdf675e311a16ea16149bd0d309841d58bf77df494
curl -sSL https://raw.githubusercontent.com/coreutils/coreutils/v9.12/src/timeout.c
  → 200, 21183 bytes, sha256 bf1f0d99…; grep setpgid/send_sig → :567-572, :244-246
sed -n '1394,1416p;1261,1268p;546,585p' tools/souji-census.sh (lane)
grep -n 'foreground' corpus/SOURCES.md → no --foreground row
```

No LSP server was mounted (`xd://lsp` absent, and the source item is a web document plus an installed info file, not a code tree), so the semantic-proof requirement was met with direct bytes/anchor inspection only; no grep was presented as semantic proof.

## 9. Next for L1

1. Assign the id (provisional S067) and append after S063; keep `queued` until `corpus/lessons/round-18.md` exists, then `mined` with that used-by.
2. Round-18 Gate line, round-17 format:
   `- **S067** https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html (live page unreachable 2026-10-20; Wayback capture 20260919212856, memento 2026-09-19; heading "GNU Coreutils 9.12"; § 23.6 › --foreground; installed coreutils 9.12-2 info :15737-15738; SrcCoreutilsTimeout): "In this mode of operation, any children of command will not be timed out." (14 words)`
3. Route the S038 anchor drift (correction row with version + sha256 + :15744/:15791, or a Gate annotation); this is a C2 calibration defect the new pointer gate will not catch.
4. Carry into the C1 implementation: no `timeout -f`, fork must be an executable/subshell (not the `census_one` function), and group signalling rather than a direct-child signal.

Cleanup: `/var/tmp/souji-r18-timeout*` removed after digesting; no processes started or signalled; no tool installs or upgrades (none needed).
