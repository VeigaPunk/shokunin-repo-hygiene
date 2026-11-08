# DRAFT for the L1 — a new section for `corpus/knowledge/filter-filemode-witness.md`

Seat: `S86Scribe`. Lane: `souji` (`/home/vgpnk/Projects/shokunin/souji-shokunin`). Draft only: the L1 integrates.
Nothing here is filed; the lane's `corpus/` files are unchanged.

**This draft APPENDS a section to `corpus/knowledge/filter-filemode-witness.md`; it replaces nothing.** The file's last
section is "r85: the lane's own audit instrument was the last one trusting the stat-cache verdict"; the new section
continues its r73 → r74 → r75 → r76 → r77 → r85 sequence and closes the class r85 left open. It is the same file
because that file already owns the subject: its title is "A clean `git status` is not a clean tree when attributes or
stat settings say so", and the r85 section it follows is about the same tool reading the same status.

Evidence this draft cites — every pointer is a committed path and line number at lane base `2acbbfc8` unless stated:

- `tools/souji-record-agreement.py` — `K4_TRUTH_WRITER` (`:78-79`), `truth_refusal` (`:171`), the writer's
  `_truth_refusal` call in the isolated bootstrap (`:196`), the index-flag sweep in the same bootstrap (`:199-211`),
  the `FLAGFAIL` arm (`:201-203`, `:221-222`), the C-escape of the refusal message (`:224-226`), the K4 key (`:411`),
  the bare status read (`:427`), the class split between `index-flag-concealed` and `stat-cache-concealed` (`:440-441`),
  and the record emitter (`:443-445`).
- `tools/souji-receipt-write.py` — `_truth_refusal` (`:262`), the skip condition that leaves two classes unhashed
  (`:283`), the refusal message that names the offending paths (`:308-311`), `_flag_refusal` (`:338`), its three
  classes (`:344-357`), the writer's own flag sweep that calls it (`:587-595`), and `_cquote` (`:227-241`).
- `census/round-86/c2-k4-counter.py` — the frozen 9-row instrument: the row list (`:48`), the path each row must be
  named by (`:50-51`), the K4 record regex (`:53`), the KG1 fixture (`:201-210`) and the KG2 fixture (`:211-215`), the
  fixture builder (`:117-157`), and the scoring (`:252-279`).
- `census/round-86/controls/c2-before-base-tool.py` — the lane-base tool bytes (byte-identical to
  `tools/souji-record-agreement.py` at `89d02c90`), and the space-join it performs at its `:199`.
- `census/round-86/records/c2-after.txt` and `census/round-86/controls/c2-before-base-tool.txt` — the two arms.
- `census/round-86/preregistration.txt` — the frozen C2 wording (committed alone at `d77b4258`).
- `.ufo/waves/round-85/w1/S85ExecK4.md` §2d (`probe-d2b`) and `.ufo/waves/round-85/w1/S85ExecK4/out-probe2.txt` — the
  r85 measurement of the escaping class.
- `.ufo/waves/round-86/w1/S86Scribe/probe-k4-record-text.py` and `.ufo/waves/round-86/w1/S86Scribe/receipts/` — my own
  re-derivation (this seat's own files).

---

## The audit tool's own concealment classes (r86)

`tools/souji-record-agreement.py` key K4 answers "does this lane still carry un-authored round work". r85 gave it a
byte-truth layer: it re-hashes every status-clean stage-0 tracked path against the object id its index entry records,
through the receipt writer's own `_truth_refusal` (`tools/souji-receipt-write.py:262`). r86 gives it a second layer,
because the first one had a blind spot that was not a limitation of the rule but a limitation of the CALL.

**K4's two layers, and what each one can see.**

1. **The truth re-hash** (`tools/souji-record-agreement.py:171-232`, running the writer's `_truth_refusal` in an
   isolated `-I -B` subprocess from the writer's source bytes beside the tool, `:196`). It re-hashes regular files and
   symlinks and compares against the index's object id. It SKIPS two classes outright, and the skip is written into the
   writer's own function at `tools/souji-receipt-write.py:283`:

   ```
   283:        if stage != b"0" or mode == b"160000" or path in listed:
   284:            continue
   ```

   A non-zero-stage entry and a gitlink (mode 160000) are never hashed, so neither can ever be found CONCEALED by
   this layer. For a gitlink that is not an oversight: the writer does not read submodule state, so there is nothing
   for it to hash against — the concealment is not in the bytes, it is in the INDEX ENTRY's flag.
2. **The index-flag sweep** (`tools/souji-record-agreement.py:199-211`), which K4 now runs inside the same isolated
   subprocess, after the truth check returns clean:

   ```
   199:        "if not msg:\n"
   200:        "    fl = mod.git(root, 'ls-files', '-v', '-z', ':(top)')\n"
   ...
   207:        "    tag, _, p = rec.partition(bytes([32]))\n"
   208:        "    if tag != bytes([72]):\n"       # 72 == b'H'
   209:        "        msg = mod._flag_refusal(root, tag, p)\n"
   210:        "        break\n"
   ```

   This is the writer's OWN sweep, called through the writer's OWN `_flag_refusal` (`tools/souji-receipt-write.py:338`),
   which is the only implementation in the lane that names a concealed gitlink (`RECEIPT-GITLINK-CONCEALED`,
   `:349-351`) and the only one that classes an unmerged, a gitlink and an absent path separately (`:344-357`). It
   reads `git ls-files -v`, whose tag is the index entry's flag: `H` is the normal cached entry, and `S`
   (skip-worktree) / `h` (assume-unchanged) / `M` / `R` / `C` / `K` / `?` mark the others.

**Why skipping `stage != 0` and `mode 160000` left a class unmeasured.** The r85 repair applied the lane's truth rule
through the writer's `_truth_refusal`, and the writer's `_truth_refusal` SKIPS exactly the two classes the gitlink
concealment lives in (`:283`). The implementation that DOES name that concealment — `_flag_refusal` — lived in a code
path K4 never called: the writer runs its flag sweep inside `write_receipt` (`tools/souji-receipt-write.py:587-595`),
which is the receipt-writing entry point, not a function K4 could import. So the r85 repair was complete in the sense
that it applied the rule the writer applies, and INCOMPLETE in the sense that the rule the writer applies has two
parts, and K4 inherited only the part that was reachable as a function.

This was measured, not suspected. r85 A2 / S85ExecK4 §2d `probe-d2b`
(`.ufo/waves/round-85/w1/S85ExecK4/out-probe2.txt`): a nested repository's commit moves, then its gitlink entry is
marked skip-worktree.

```
===== (d2) gitlink + skip-worktree concealment =====
porcelain before skip-worktree: b' M submod\n'
porcelain after skip-worktree: b''
ls-files -s submod: 160000 ab8c5170b5427d1b3d9e2cc2ba01bf462eb3b0fd 0	submod
--- (d2) gitlink commit changed + skip-worktree: rc=1 K4rows=0
(no K4 rows)
```

Porcelain is EMPTY, `ls-files -s` still records the `160000` entry, and K4 emitted ZERO rows. The concealment is
invisible to the status read (the flag hides it) and invisible to the truth re-hash (the mode is skipped), so only an
index-flag sweep can see it. The same probe shows the ordinary classes ARE caught: `(d3)` a regular file with
skip-worktree and forged bytes gives `K4rows=2`, including `stat-cache-concealed` naming `a.txt`, and `(d4)`
assume-unchanged and `(d5)` a deleted file behave the same. The gap was narrow and specific: the GITLINK.

**Why a record must keep a path name one physical line.** A K4 record is one line of TAB-separated fields
(`tools/souji-record-agreement.py:445`: `MISMATCH\t{key}\t{record}\t{class}\t{detail}`), and its detail field carries
the path the reader must act on. A path name may legally contain a newline, and when the detail carries it raw, the
record splits: the reader gets a truncated first line and an orphan tail, and a line-oriented parser (the frozen
counter's own `^MISMATCH\tK4\t…` regex, `census/round-86/c2-k4-counter.py:53`) sees only the first physical line. The
r85 seat measured this at §2e: the newline path is DETECTED, but the record does not escape it.

r86's repair escapes it instead of dropping it — the refusal message is C-escaped before it becomes a record
(`tools/souji-record-agreement.py:224-226`):

```
224:        # r86: a path may carry a newline or a tab (S85ExecK4 §2e). C-escape them so one K4 record stays one
225:        # physical line and still names the path a reader must act on.
226:        return (out[len("FORGED "):].replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r"))
```

The lane already had this convention in the writer — `_cquote` (`tools/souji-receipt-write.py:227-241`) C-quotes a path
for `git hash-object --stdin-paths` so a newline, CR, quote or backslash path hashes correctly — and the repair uses
the same idea at the record boundary. A space-join would have been worse than the raw newline: it keeps the record on
one line but makes the name UNRECOVERABLE, because `bad\nname.txt` and `bad name.txt` are different paths and the
reader cannot tell which one the record names. That is exactly what the lane-base bytes did
(`census/round-86/controls/c2-before-base-tool.py:199`, byte-identical to the tool at `89d02c90`):
`"print('CLEAN' if not msg else 'FORGED ' + msg.replace(chr(10), ' '))\n"` — the newline is replaced by a SPACE.

**And the space-join leaves the TAB behind.** The base bytes replace only `chr(10)`. A TAB in a path name is not
replaced at all, so it lands RAW inside a TAB-delimited record and splits the record's FIELD structure. I measured this
over the counter's own fixture (`probe-tab-name-field-split.py`, receipt `receipts/f4-tab-name-field-split.txt`): a
tracked file named `bad<TAB>name.txt`, forged under the index stat cache.

```
--- FILED rc=1
   fields=5  repr='MISMATCH\tK4\t.\tstat-cache-concealed\t... (bad\\tname.txt); ...'
--- BASE rc=1
   fields=6  repr='MISMATCH\tK4\t.\tstat-cache-concealed\t... (bad\tname.txt); ...'
```

The filed tool emits five tab-separated fields and the base tool SIX: the base record's detail field is split in two by
the raw TAB, so a reader parsing on the tab boundary reads the detail as two fields and the path as a fragment. The
newline is the one control byte the base bytes happen to handle (by destroying it), which is why the round's KG2 row —
a NEWLINE name — never exposed this. The round's frozen 9-row population has no tab-named row, so the class is outside
this round's coverage; it is an r87 candidate, stated here so the r86 section does not read as if the escape were
complete.

**Measured.** The frozen 9-row counter `census/round-86/c2-k4-counter.py` over a hermetic synthetic repository:

- filed tool `tools/souji-record-agreement.py` (sha256 `4cc3b945…8df`): `SUMMARY rows=9 mismatches=0 errors=0`,
  `EXIT=0`; KG1 `k4=1 named=yes` with `k4rows=['.|index-flag-concealed']`, KG2 `k4=1 named=yes`
  (`census/round-86/records/c2-after.txt`);
- lane-base tool bytes (`census/round-86/controls/c2-before-base-tool.py`, sha256 `0ade0751…8fb7`): `SUMMARY rows=9
  mismatches=2 errors=0`, `EXIT=1`; KG1 `k4=0 named=no` (no row at all), KG2 `k4=1 named=no`
  (`census/round-86/controls/c2-before-base-tool.txt`).

The seven r85 rows are unchanged between the arms (KH1, KH2 clean; KU1, KU2 `uncommitted-path`; KF1, KF2, KF3
`stat-cache-concealed`), so the repair adds two rows and moves no verdict.

The raw records, byte for byte, from my own re-derivation over the counter's own fixture
(`.ufo/waves/round-86/w1/S86Scribe/probe-k4-record-text.py`):

```
--- row KG1 | FILED (tools/souji-record-agreement.py) | rc=1
   'MISMATCH\tK4\t.\tindex-flag-concealed\tRECEIPT-GITLINK-CONCEALED: nest is a gitlink (mode 160000) carrying index flag S; the writer does not read submodule state and skip-worktree or assume-unchanged hides it from git status; clear it with git update-index --no-skip-worktree or --no-assume-unchanged, then retry'
--- row KG1 | BASE (census/round-86/controls/c2-before-base-tool.py) | rc=1
   (no K4 row: keys=4 records=3 occurrences=0 mismatches=7)
--- row KG2 | FILED (tools/souji-record-agreement.py) | rc=1
   'MISMATCH\tK4\t.\tstat-cache-concealed\tRECEIPT-WORKTREE-STAT-CONCEALED: 1 tracked path(s) git status reports clean do not hash to the object id the index records (bad\\nname.txt); the index stat cache conceals a worktree change; no receipt written'
--- row KG2 | BASE (census/round-86/controls/c2-before-base-tool.py) | rc=1
   'MISMATCH\tK4\t.\tstat-cache-concealed\tRECEIPT-WORKTREE-STAT-CONCEALED: 1 tracked path(s) git status reports clean do not hash to the object id the index records (bad name.txt); the index stat cache conceals a worktree change; no receipt written'
```

KG1's filed record names the gitlink (`nest`), which the base emits no record for at all. KG2's filed record keeps the
newline path as the two characters `\n` — one physical line, and the name is recoverable; the base's record reads
`bad name.txt`, one physical line and an unrecoverable name. Note also that KG2 is NOT a flag class: its concealment
is the stat cache, so it is caught by layer 1 and reported as `stat-cache-concealed`, while KG1 is caught by layer 2
and reported as `index-flag-concealed` (`tools/souji-record-agreement.py:440-441` splits the two by the refusal
message's prefix). The two rows exercise the two layers separately, which is why the repair needs both.

**What the repair does not cover, stated rather than claimed away.** The fixture is synthetic and hermetic; KG1's
nested repository is bound by an index gitlink with NO `.gitmodules`, so the row proves the flag sweep SEES a concealed
gitlink commit — not that every submodule state is read (the writer still does not read submodule state). KG2 proves
the record is single-line and names the path; it does not prove that every control character is escaped (`\r` is
handled, and other control bytes are not). The flag sweep inherits the writer's classes, but K4 does not run the
writer's filter/attribute witnesses. A forged writer inside the audited tree stays outside the claim. And a copy of
the tool with no writer beside it fails closed rather than measuring — `tools/souji-record-agreement.py:181-182` says
so and returns a message, never a clean verdict.

## Gate

- Destination: `corpus/knowledge/filter-filemode-witness.md`, a NEW section appended after "r85: the lane's own audit
  instrument was the last one trusting the stat-cache verdict". It replaces nothing; the r85 section stands as
  written, and this section continues its sequence.
- The heading is "The audit tool's own concealment classes (r86)". It is not a new corpus entry and not
  `corpus/knowledge/gate-signal-handling.md`: the subject is the concealment classes an audit tool's own check cannot
  see, and `filter-filemode-witness.md` already owns the stat-cache and flag-concealment ground (its r73 section names
  the index stat cache; its r85 section is about this very tool).
- The file's front matter (`source:`, `verified-at:`, `recheck:`) is the L1's to update; this draft does not touch it.
  The sources the section leans on (S315, S316, S317 for the index/stat-cache ground, and S339 for the index file's own
  checksum) are already admitted in `corpus/SOURCES.md`; the section needs no new source row.
- Every pointer resolves to a committed path and line number at lane base `2acbbfc8`, except the two files under this
  seat's own directory (`.ufo/waves/round-86/w1/S86Scribe/`), which are this seat's draft instruments. I audited this
  mechanically over the three drafts: 45 `path:line` references, 0 unresolved.
- The L1 landed its own r86 section for this file in the working tree while I was measuring; this draft was written
  against the committed bytes and is a draft for the L1 to merge, not a replacement for what the L1 has written. The one
  thing this draft adds that the round's own receipts do not carry is the RAW RECORD TEXT (the `MISMATCH\tK4\t…` lines,
  which show the space-join's unrecoverable name) and the TAB-class measurement.
- No claim here exceeds what the round's own receipts carry: the two arms are `census/round-86/records/c2-after.txt`
  and `census/round-86/controls/c2-before-base-tool.txt`; the RAW RECORD TEXT (the `MISMATCH\tK4\t…` lines quoted
  above) is not in either receipt and is supplied here by this seat's own re-derivation, reproducible with
  `probe-k4-record-text.py`.
- Nothing outside the seat's own directory was written. The lane's `corpus/` files are unchanged.
