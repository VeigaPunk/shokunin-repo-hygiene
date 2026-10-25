STATUS: PASS

# ScoutCensusMirror — scratch-mirror regime proof for the gated append

Seat: `L1Souji22.ScoutCensusMirror`. Lane: repo/workspace hygiene (掃除). Leaf member; no subagent dispatch.
Base lane revision named by the preregistration: `4edb25dfe262515d0da63224bbba71e02e36cba5`.
Everything below is **executed** unless explicitly marked `[INFERENCE]` or `[source-inferred]`.
Full transcripts: `.ufo/waves/round-22/attempt2/w1/evidence/ScoutCensusMirror.txt` (369 lines, 25,663 bytes).

## What was proven

The census can be driven against a scratch copy of the lane corpus under `/var/tmp`, so the
append can be pre-flighted without any write to `corpus/`. The synthetic-row probe is a real
signal, not a false green: one duplicate-URL row turns exit 0 into exit 1 with `E04`, one
duplicate-id row adds `E03`, and removing the row returns stdout **byte-identical** to the
pre-probe baseline. The probe also measures exactly which duplicates `validate` cannot see —
which is the part the gate must not assume away.

## Executed commands and transcripts

Tool identity at run time: `scripts/sources-census.sh` sha256 `3fb7261569f46423dd80ecc23e0a23789a7926f667c7a3fc559d2439d4a64e30`,
GNU Awk 5.4.1. No tool installed or upgraded this seat.

### 0. Control — real registry, no synthetic row (read-only)

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
[exit 0]
  30 × "souji  W04  <id> duplicate url <url> across scopes"   (S035 S036 S038 S049 S057 S058 S059 S063 S065
                                                               S072 S073 S075 S076 S077 S086 S087 S088 S089 S090
                                                               S091 S092 S093 S094 S095 S096 S097 S098 S099 S106 S108)
  souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

### 1. Mirror build (copy only)

```
$ mkdir -p /var/tmp/souji-r22-mirror/corpus
$ cp  <lane>/corpus/{SOURCES.md,QUALITY.md,README.md}  /var/tmp/souji-r22-mirror/corpus/
$ cp -r <lane>/corpus/{knowledge,lessons}/             /var/tmp/souji-r22-mirror/corpus/
$ du -sh /var/tmp/souji-r22-mirror/corpus   ->  808K
```

Fidelity (not assumed, checked):

```
cmp-identical  corpus/SOURCES.md      (sha256 4b6456c4d7a0cd49f2980c904d20c3f0c435c35bfbd64516cf657e1ff64cb223 both sides)
cmp-identical  corpus/QUALITY.md
cmp-identical  corpus/README.md
diff -r corpus/knowledge -> exit 0
diff -r corpus/lessons   -> exit 0
```

### 2. Mirror baseline — no synthetic row

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file /var/tmp/souji-r22-mirror/corpus/SOURCES.md
[exit 0]
  file	W04	... (same 30 W04 rows)
  file	ok	/var/tmp/souji-r22-mirror/corpus/SOURCES.md
```

Finding rows with only the lane-name column dropped are **identical** to the real registry's
(`identical: True`, 30 rows, distinct codes `['W04']`). The only divergence is the lane label
(`souji` vs `file`) and the `ok`-line path — both functions of `--root`/`--file`, not of the
registry bytes.

### 3. ONE synthetic candidate row — duplicate URL, duplicate scope (E04)

Row appended as the last row **inside `## Registry`** (registry table ends at line 134;
appending after the file's later `## Paths`/`## Search log` headings would have produced `E12`
instead, so position matters):

```
| S999 | SYNTHETIC MIRROR PROBE — duplicate of S001's URL, never an adopted row — https://git-scm.com/docs/git-maintenance | docs | B | git 2.55.0 maintenance tasks, strategies and maintenance.auto | synthetic probe, no locator | synthetic probe row: duplicates S001 url and scope, not adopted | queued | 2026-10-25 | 90d | — |
```

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file /var/tmp/souji-r22-mirror/corpus/SOURCES.md
[exit 1]
  file	W04	... (30 unchanged rows)
  file	E04	S999 duplicate url git-scm.com/docs/git-maintenance within scope git 2.55.0 maintenance tasks, strategies and maintenance.auto
```

Delta vs the mirror baseline: exactly that one line. `E03` did **not** fire (correct — the id was
fresh). So the duplicate-URL signal is `E04`, exit 1.

### 4. Same slot, duplicate id as well — E03 precision probe

```
| S001 | SYNTHETIC MIRROR PROBE — duplicate of S001's URL, never an adopted row — https://git-scm.com/docs/git-maintenance | docs | B | git 2.55.0 maintenance tasks, strategies and maintenance.auto | synthetic probe, no locator | synthetic probe row: duplicates S001 url and scope, not adopted | queued | 2026-10-25 | 90d | — |

$ ... validate --file /var/tmp/souji-r22-mirror/corpus/SOURCES.md
[exit 1]
  file	E03	S001 duplicate id
  file	E04	S001 duplicate url git-scm.com/docs/git-maintenance within scope git 2.55.0 maintenance tasks, strategies and maintenance.auto
```

`E03` and `E04` are independent detectors; both fire, neither masks the other.

### 5. Remove the synthetic row, re-run

```
$ grep -v 'SYNTHETIC MIRROR PROBE' /var/tmp/souji-r22-mirror/corpus/SOURCES.md > restored && mv restored /var/tmp/souji-r22-mirror/corpus/SOURCES.md
$ ... validate --file /var/tmp/souji-r22-mirror/corpus/SOURCES.md
[exit 0]
  file	W04	... (30 rows)
  file	ok	/var/tmp/souji-r22-mirror/corpus/SOURCES.md
```

`after-removal stdout == mirror baseline stdout: True`. Mirror `SOURCES.md` sha256 back to
`4b6456c4…cb223`, equal to the lane file's. Exit code returns to 0.

### 6. Negative control — why the mirror must carry the trees

```
# SOURCES.md-only mirror
$ ... validate --file /var/tmp/souji-r22-mirror/corpus/SOURCES.md
[exit 1]   E11 findings: 97
  file	E11	S001 missing used-by corpus/knowledge/git-auto-maintenance-prunes-worktrees.md
  ...

# same mirror + corpus/{knowledge,lessons}/
[exit 0]   E11 findings: 0
  file	ok	/var/tmp/souji-r22-mirror/corpus/SOURCES.md
```

`--file` resolves `dir` as `dirname(file)/..`, so `E11` "used-by path missing on disk" is judged
against the mirror root. Every `used-by` cell in this registry is `corpus/…`-relative, so the
mirror is only valid with `corpus/knowledge` **and** `corpus/lessons` present. A `SOURCES.md`-only
mirror is a false red, not a clean baseline.

### 7. Cleanup

```
$ rm -rf /var/tmp/souji-r22-mirror
test -e /var/tmp/souji-r22-mirror -> False
```

Lane `corpus/SOURCES.md` sha256 was `4b6456c4…cb223` before the first probe, after every probe,
and after cleanup: unchanged. The lane file's mtime is 2026-10-25T06:39:41Z (someone else's
write, pre-dating this seat's 06:46:03Z run). Only write this seat made under the lane:
`.ufo/waves/round-22/attempt2/w1/evidence/ScoutCensusMirror.txt` and this report.

## Bounded findings

1. **`E04` is scope-exact, so `validate` exit 0 does not prove URL uniqueness.** `[executed]`
   Duplicate URL + reworded scope cell → `W04` only, exit 0:

   ```
   | S999 | ... https://git-scm.com/docs/git-maintenance | docs | B | git 2.55.0 maintenance tasks, strategies and maintenance.auto (synthetic reword) | ... | queued | ... |
   [exit 0]  codes=['W04']
   ```

   This is contract-intended (the registry legitimately carries 30 cross-scope `W04` rows), but
   it fixes the shape of the append gate: **`exit 0` alone is not evidence the append added no
   duplicate.** The gate must also diff the `W04` set against the pre-append baseline and fail if
   a `W04` line names an appended id. (Real registry today: 114 registry rows, 30 `W04`.)

2. **Two documented `E04` bypasses.** `[executed]` Same URL *and* same scope cell still exits 0
   when the new row is `status=rejected`, and when the `teaches` cell contains
   `supersedes S<id>` (`sources-census.sh:646-649` `[source-inferred]`, then confirmed by probe):

   ```
   PROBE D (status=rejected)          [exit 0]  codes=['W04']   E-lines: <none>
   PROBE E (teaches: ...supersedes S001) [exit 0] codes=['W04']  E-lines: <none>
   ```

   The gate must therefore assert the appended rows are `status=mined` (the adopted shape) and
   carry no `supersedes` claim unless the supersession is intentional and named in the report.

3. **Only the first URL of a `source` cell is censused.** `[source-inferred]` `url_of()` extracts
   the first `https?://` match only (`sources-census.sh:601-606`). One registry row already carries
   two URLs (S051), whose second URL is invisible to `E03/E04/W04`. Adopted rows in this round
   each name a single URL, so this does not weaken the planned append — but a multi-URL adopted
   row would bypass duplicate detection for every URL after the first. Gate check: verify each
   appended `source` cell contains exactly one URL, or check the extra ones by hand.

4. **Mirror layout requirement (operability).** `[executed]` `--file` implies `lane="file"` and
   `dir=<mirror root>`; the registry must sit at `<mirror>/corpus/SOURCES.md` and the trees must be
   copied beside it, else 97 spurious `E11` findings appear. The regime is: `mkdir -p
   /var/tmp/<round>-mirror/corpus`, copy `SOURCES.md QUALITY.md README.md knowledge/ lessons/`,
   then `validate --file`. That recipe reproduced the real finding set exactly (F above).

5. **Instrument positioning.** `[executed]` The synthetic row must be inserted *inside*
   `## Registry`; appended at end-of-file it lands under `## Leads (unopened)` and yields `E12`
   ("row outside Registry section") with **no** `E04` — a probe placed at the wrong offset would
   have been read as "duplicate not detected".

6. **Cost/risk.** `[executed]` Full probe cycle: mirror build 808K, 8 `validate` invocations,
   total wall time seconds; the tool is read-only by construction (stdout/`--out` only), and the
   real registry was never mutated. Scratch removed.

## Remaining unknowns

- `corpus/SOURCES.md` is a live lane file; the mirrored snapshot is pinned at sha256
  `4b6456c4…cb223` (mtime 06:39:41Z). If a sibling seat appends between now and landing, the
  final-tip gate must be re-run — this probe proves the *mechanism*, not the final bytes.
- Whether `SOURCES-CONTRACT-v1` itself narrows "duplicate URL+scope" the same way the tool does
  was not checked (contract document out of this item's scope); the probe measures the tool's
  behaviour only.
- The absent-defect register slice/verdicts for C2 were not touched by this seat (other lanes own
  them); this report makes no C1/C2 verdict.

## Checks for the main agent (run once, after all seats land)

```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji ; echo EXIT=$?
# expect EXIT=0, 30 W04 rows and no W04 row naming an appended id, no E-code
```

## Tooling record

No installs or upgrades. `pacman` untouched (host transactions paused); no service restarted.
