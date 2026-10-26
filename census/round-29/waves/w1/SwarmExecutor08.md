# SwarmExecutor08 — C2UutilsEscape (r29 w1, attempt 1)

## Status
STATUS: PASS — GNU manifest escape handling probed on this host with three independent emitters and
four consumers; 148-row matrix delivered. The r28 closure claim is **REFUTED** in its binary
identification and **CONFIRMED** in its parser behaviour, with one hazard its wording hides.
Lane writes: this report and the one named delivery file only.

## Evidence

### Revisions and instrument identity
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3` → `b8cb4b3 round-29: freeze claims…`,
  `691dd29 round-28 verifier spot-check…`, `fec846d round-28: pin after measurements…`.
- `git -C <lane> rev-parse master` → `b8cb4b31ce80e2e3314b88e85d40ea9873180804`;
  the counter is not in the lane base (691dd29) but in the prereg commit:
  `git -C <lane> show b8cb4b31:…/census/round-29/c2-counter.py | sha256sum` →
  `5ab641c41459ca72529baa57268eef99bb16b849f92e8bc2b0dd6fd7df3b1b3f`, equal to the working-tree
  file. The decoder copied into scratch is therefore the frozen instrument's bytes.
- Preregistration read at `census/round-29/records/preregistration.txt:1-30` (C2 clause at line 7:
  "decodes GNU backslash-escaped records").

### 1. Host resolution (`command -v`, `--version`)
```
$ command -v sha256sum
sha256sum                      # shell builtin, not a path
$ sha256sum --version
sha256sum 0.8.0
$ /usr/bin/sha256sum --version
sha256sum (GNU coreutils) 9.12
$ type -a sha256sum
sha256sum is a shell builtin
sha256sum is /usr/bin/sha256sum
$ bash -c 'sha256sum --version | head -1'
sha256sum (GNU coreutils) 9.12 # child shells do not inherit the builtin
$ pacman -Q coreutils
coreutils 9.12-2
```
uutils 0.8.0 was obtained as the official release binary **into scratch only**, not installed:
`https://github.com/uutils/coreutils/releases/download/0.8.0/coreutils-0.8.0-x86_64-unknown-linux-gnu.tar.gz`,
tarball sha256 `ea8f0a4f6815c1da0df539c88b4776b976983c0139879662de03bc4010bd0504` (11 973 103 bytes),
`coreutils --version` → `coreutils 0.8.0 (multi-call binary)`; invoked as `<dir>/coreutils sha256sum`.
No pacman/uv/cargo transaction ran. Reason for scratch-only: a multicall `coreutils` in
`~/.local/bin` would shadow GNU tools for every fleet process (finding 3 is exactly that hazard).

### 2. Bytes emitted (`od -c`, scratch `/var/tmp/souji-r29-C2UutilsEscape/manifests/`)
```
newline       GNU 9.12 : \ 4 4 d 7 … 6 b b 1 6 b e _ _ . / n l \ n n a m e . t x t \n
backslash     GNU 9.12 : \ e f c 1 … 4 5 2 a f 3 9 _ _ . / b s \ \ n a m e . t x t \n
backslash+LF  GNU 9.12 : \ 1 c c c … 0 9 5 6 e c _ _ . / b o t h \ \ \ n n a m e . t x t \n
non-UTF-8     GNU 9.12 : d f 6 0 … 8 f 8 4 0 _ _ . / n u 377 376 . t x t \n
non-UTF-8   uutils 0.8.0: d f 6 0 … 8 f 8 4 0 _ _ . / n u 357 277 275 357 277 275 . t x t \n
tab / space / dash    : emitted verbatim, no escape, no quote, two-space separator only
tab escaped as `\t`   : not GNU grammar; rejected by all three consumers (see below)
```
`_` in the dump above marks a space column. The escape marker is **line-initial, before the
digest**, and the separator stays two spaces; exactly `\\` and `\n` are escaped, nothing else.

### 3. Generator byte identity (`cmp`, then `sha256sum` of the manifests)
```
newline    gnu-vs-py=SAME   gnu-vs-uutils=SAME     2d46bfb7a8c9e4b25eb22e564f6af0b3eaf54168b2850c2b3b974eebd3a5e009
bs_nl      gnu-vs-py=SAME   gnu-vs-uutils=SAME     c7b0518dd79abbce8d04d6990b1ebaa8047e3d27a8991f4d41ac9f0cc3a2241f
nonutf8    gnu-vs-py=SAME   gnu-vs-uutils=DIFF
ascii/backslash/dash/space/tab: SAME for both pairs
```
The `hashlib` emitter that follows the GNU grammar ("py-line-escape") reproduces GNU bytes for all
eight name classes; uutils differs only where the name is not valid UTF-8 (it is lossy).

### 4. Consumers over the same manifests (47 rows each; totals from the delivery TSV)
```
gnu-check (/usr/bin/sha256sum 9.12)                  : 40 ACCEPT / 7 REJECT
counter-decoder (c2-counter.py parse, copied)        : 40 ACCEPT / 7 REJECT   (identical reject set)
uutils-check (uutils coreutils 0.8.0 binary)         : 24 ACCEPT / 23 REJECT
```
Combined 8-record manifest, one run each:
```
/usr/bin/sha256sum -c all-gnu.sha256                 rc=0  ok=8  warn=0
/usr/bin/sha256sum --strict -c all-gnu.sha256        rc=0  ok=8  warn=0
<uutils> sha256sum -c all-gnu.sha256                 rc=0  ok=5  "WARNING: 3 lines are improperly formatted"
<uutils> sha256sum --strict -c all-gnu.sha256        rc=1  ok=5  same warning
<uutils> sha256sum -c all-uutils.sha256              rc=1  ok=4  + "./nu??.txt: No such file or directory" + 3 skipped
builtin `sha256sum -c all-gnu.sha256` (this tool shell) rc=0  ok=5  "WARNING: 3 line(s) are improperly formatted"
builtin `sha256sum --strict -c all-gnu.sha256`          rc=1
```

### 5. Frozen counter over COMMITTED bytes (scratch repos, `census/round-29/waves/`)
```
gnu-9.12       r29 records=8 failed=0 uncovered=0 floor_violation=0
py-line-escape r29 records=8 failed=0 uncovered=0 floor_violation=0
uutils-0.8.0   r29 records=8 failed=1 uncovered=1 floor_violation=0
py-name-escape r29 records=8 failed=3 uncovered=3 floor_violation=0
py-raw         r29 records=8 failed=4 uncovered=2 floor_violation=0
sweep, 6 escaped shapes, gnu-9.12  records=6 failed=0 uncovered=0 floor_violation=0
```
Command shape: `python3 -B census/round-29/c2-counter.py --root "$D" --rev "$(git -C "$D" rev-parse HEAD)"`
with `$D` a `mktemp -d /var/tmp/souji-r29-C2UutilsEscape/g.XXXXXX` repo confirmed by
`git -C "$D" rev-parse --show-toplevel`. Every one of the six runs exits 1: for `py-name-escape`/`py-raw` on their own `failed`/`uncovered`,
and for the three passing generators on the floor branch alone (`SUMMARY … floor_violations=3` — the
r26/r27/r28 manifests a probe repo does not carry). The `rc` column of those TSV rows is therefore the
real exit status, while the verdict column reads `failed`/`uncovered`, as the detail text shows.

### 6. Reproduction of the r28 claim (command cited in the claim's own terms)
Lane statement under test — `corpus/lessons/round-28-verifier-spotcheck.md:77`, quote:
"this host's `/usr/bin/sha256sum` is uutils 0.8.0, which rejects every escaped line".
```
$ d=$(mktemp -d /var/tmp/souji-r29-C2UutilsEscape.XXXXXX) && cd "$d" && printf a > $'nl\nname.txt'
$ UU=/var/tmp/souji-r29-C2UutilsEscape/uu/coreutils-0.8.0-x86_64-unknown-linux-gnu/coreutils
$ /usr/bin/sha256sum ./$'nl\nname.txt' > m.sha256 && od -c m.sha256 | head -1
0000000   \   c   a   9   7   8   1   1   2   c   a   1   b   b   d   c   a   f   a   c
$ /usr/bin/sha256sum -c m.sha256      ; echo rc=$?
'./nl'$'\n''name.txt': OK            rc=0
$ $UU sha256sum -c m.sha256           ; echo rc=$?
sha256sum: m.sha256: no properly formatted checksum lines found   rc=1
```
Same shape across nine escaped name shapes (`nl\name`, `bs\name`, `both\\n`, `endbs\`, `\`,
`\nlead.txt`, `trail\n`, `two\n\nnl.txt`, `a\\b.txt`): GNU 9/9 ACCEPT, uutils 9/9 REJECT.

## Findings
1. **The r28 identification is wrong for `/usr/bin`.** `/usr/bin/sha256sum --version` →
   `sha256sum (GNU coreutils) 9.12` (`/usr/bin/sha256sum`); uutils 0.8.0 is the *shell builtin* in
   this tool shell and any PATH copy. Corroborated by
   `census/round-26/waves/w1/sha256sums-recipe.md:140` — "resolve first to uutils 0.8.0 **builtins**".
2. **The r28 parser behaviour is confirmed.** Every record line beginning with `\` is unparseable to
   uutils 0.8.0; nine escaped name shapes, two independent probe sets, all rc=1 with
   "no properly formatted checksum lines found" (`deliver-escape-matrix.tsv`, consumer `uutils-check`).
3. **Hazard the claim's word "rejects" hides.** On a *mixed* manifest uutils exits **0** while
   skipping the escaped records (`rc=0 ok=5 "WARNING: 3 lines are improperly formatted"`); only
   `--strict` makes it fail. `tools/souji-wave-evidence-capture.sh:159` and `:176` write and re-verify
   the manifest with `xargs -0 sha256sum` and a byte `cmp` — never `sha256sum -c` — so a capture run
   whose PATH `sha256sum` were uutils would self-verify while three records were never parsed, and
   would exit 0 ([INFERENCE] from the measured byte identity of uutils' escaping plus the tool's own
   `cmp` logic; the capture tool itself was not executed).
4. **uutils cannot write a verifiable non-UTF-8 record.** It maps each invalid byte to U+FFFD
   (`357 277 275`), so its own `-c` then reports "No such file or directory" and the frozen counter
   reports `failed=1 uncovered=1` (`c-uutils-0.8.0-nonutf8.sha256`; TSV row
   `nonutf8/uutils-0.8.0/*`).
5. **GNU grammar, as measured.** Line-initial `\` marker before the digest; two spaces; only `\\`
   and `\n` escaped; every other byte (tab, space, leading `-`, raw non-UTF-8) verbatim; names kept
   as passed (`find .` → `./name`, which the counter strips at
   `census/round-29/c2-counter.py:63-64`).
6. **Marker placement is the implementers' trap.** A generator that writes
   `<hash>  \./name` (marker before the name, not before the digest) is rejected by GNU, uutils and
   the counter on 3/3 escaped classes (`generator=py-name-escape`).
7. **An unescaped newline is unrecoverable.** `generator=py-raw` splits into one valid-looking
   record plus one bad line: counter `failed=4 uncovered=2 bad_lines=1..2`, GNU/uutils "improperly
   formatted" plus a failed open (`newline/py-raw/*`, `bs_nl/py-raw/*`).
8. **GNU consumer and frozen counter agree wherever the generator is GNU-grammar**: gnu-9.12 8/8 and
   py-line-escape 8/8 ACCEPT for both; the 7 non-accept rows are the same set for both
   (3 name-marker, 2 raw-newline, 1 `\t`-escape, 1 uutils non-UTF-8). Divergence is confined to
   escaped records under uutils (counter OK, uutils skips) and raw-backslash records (counter OK,
   uutils decodes `\n` even without the marker → open failure).
9. **Counter observation (frozen; no change requested).** `census/round-29/c2-counter.py:57-62`
   collects records into a dict keyed by the decoded name, so two records decoding to one name leave
   only the last hashed; a duplicate-name record is silently unchecked. Not reachable from the
   capture tool's `find`-derived names, but it is the one place where "failed" can miss a record.
10. **Lane state observed, not touched.** `git -C <lane> status -sb` → `## HEAD (no branch)` with
    `M .ufo/waves/round-26/w1/ScribeGateDraft.md`; `master` resolves to the same commit `b8cb4b31`,
    so HEAD is detached at master's tip. Reported for the L1's integration decision only.

## Attack log
- **A1 — REFUTE (identification).** `/usr/bin/sha256sum` is GNU 9.12, not uutils 0.8.0. Any r29
  statement that inherits the r28 sentence must name the *shell builtin/PATH* copy, not `/usr/bin`.
  Evidence: Evidence §1, §6.
- **A2 — CONFIRM (parser).** uutils 0.8.0 fails every line-initial-`\` record: 9/9 escaped shapes,
  rc=1 each when the manifest holds only that record. Evidence: Evidence §6, TSV `uutils-check` rows
  for `newline`/`backslash`/`bs_nl` and the six sweep shapes.
- **A3 — silent partial verification.** Same consumer exits 0 on a mixed manifest (5 OK, 3 skipped);
  the lane's capture tool never consults `-c`, so "captured+verified" can be printed with records
  unparsed. Evidence: Evidence §4, `tools/souji-wave-evidence-capture.sh:159,:176`.
- **A4 — lossy receipt writer.** uutils writes non-UTF-8 names as U+FFFD, producing a receipt its own
  verifier rejects and the frozen counter counts `failed`. Evidence: TSV `nonutf8/uutils-0.8.0/*`.
- **A5 — duplicate-name collapse in the frozen counter.** Two records that decode to one name verify
  only the last; `failed` cannot see the dropped one (`c2-counter.py:57-62`). Contract says counters
  are frozen; filed as an observation for the L1, not a repair request.

## Recommendation for the v2 tool
1. **Emit records yourself in the GNU grammar; do not shell out to `sha256sum`.** The probe's
   `hashlib` emitter is byte-identical to GNU 9.12 for all eight classes (`cmp` SAME, §3), and the
   PATH hasher on this host is not stable (builtin uutils today, GNU in a child shell).
   ```python
   def record(digest: str, name: bytes) -> bytes:          # GNU sha256sum text-mode grammar
       if b'\\' in name or b'\n' in name:
           return b'\\' + digest.encode() + b'  ' + name.replace(b'\\', b'\\\\').replace(b'\n', b'\\n') + b'\n'
       return digest.encode() + b'  ' + name + b'\n'
   ```
2. **Rules that follow from the measurements**: marker on the line, before the digest; two spaces;
   escape only `\\` and `\n` (never `\t`, `\xNN`, `\ooo`); every other byte verbatim, including raw
   non-UTF-8; keep the `./`-prefixed name bytes exactly as the walk produced them (`bytes`, never a
   lossy `str` round-trip); no `--tag`/BSD form and no `-b` binary marker.
3. **Verify with GNU and with `--strict`, by absolute path**: `/usr/bin/sha256sum -c --strict
   <manifest>` must exit 0 — `--strict` is what turns a skipped record into a failure. Never rely on
   PATH `sha256sum`, never pass `--ignore-missing`.
4. **Keep the frozen-counter decode as the second gate over committed bytes** (it is the C2
   instrument); GNU-grammar records are the only shape both a GNU consumer and that counter accept on
   every class tested, so no re-encoding of the two r26 escaped records is needed for C2.
5. **Do not use uutils 0.8.0** to produce or verify receipts on this host: it is unparseable for its
   own escaped output and lossy for non-UTF-8 names (A2–A4).

## Deliveries
- `.ufo/waves/round-29/w1/deliver-escape-matrix.tsv` — 148 data rows, 6 columns
  (`name_class`, `generator`, `consumer`, `rc`, `verdict`, `detail`); sha256
  `e5bd9efac7dc52b3b586f76b0158803c15ddc2beb25e485bc54f9cd76f38e31a`; byte-stable across two
  assembly runs; scratch commit ids elided as `<scratch-throwaway-commit>`.
- `.ufo/waves/round-29/w1/SwarmExecutor08.md` — this report.

Scratch `/var/tmp/souji-r29-C2UutilsEscape/` was removed after the run; every scratch git repo was
created under it and `git -C <dir> rev-parse --show-toplevel` was asserted equal to the scratch dir
before each first commit. No lane path was written outside the two files above. Deviation disclosed:
one throwaway byte file (`/var/tmp/probe-uu.txt`) and two `/tmp/o`,`/tmp/e` capture files were
written outside the scratch root in the first two probe commands and have been removed.
