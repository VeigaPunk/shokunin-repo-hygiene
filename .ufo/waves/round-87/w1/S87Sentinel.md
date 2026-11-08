# S87Sentinel — adversarial security review of the C2 repair (K4) as a privilege boundary

Lane: `souji-shokunin` (lane id souji) · Round 87, wave 1, seat `S87Sentinel`.
Subject: `tools/souji-record-agreement.py` key K4 — the repaired `truth_refusal`, `writer_binding`,
`_stderr_tail`, and the `--porcelain -z` status arm.
Scope: read-only. **No lane file was edited by this seat.** The lane's own tools, instruments, controls and
receipts are untouched; all probes ran against *copies* under this seat's scratch.

## 0. Verdict summary

The **C2 claim's own stated wording survives every probe I ran** — no artifact produced by this wave falsifies
it. The frozen counter is green on the filed bytes (`SUMMARY rows=12 mismatches=0 errors=0`, `EXIT=0`) and red on
the base control (`mismatches=3`, `EXIT=1`), as the prereg's kill rule requires.

But the repair is **not yet a closed privilege boundary**. Four residual defects survive on the current filed
bytes, all at the *writer-delegation* seam rather than in the status arm:

| # | Severity | Finding | Reader-misleading? |
|---|----------|---------|-------------------|
| F1 | **HIGH** | The `# writer path=… sha256=…` header digest is read at a *different time* from the bytes that are compiled. The header names bytes that did **not** run. | **YES** |
| F2 | **MEDIUM** | A delegated writer that prints the token `CLEAN` and then dies is read as a **clean verdict** — the tool concludes the tracked bytes *are* verified and emits no K4 row. Fail-open. | **YES** |
| F3 | **MEDIUM** | The `REFUSED` branch interpolates the writer's exit message into the detail cell **unescaped**. A newline in it injects a **forged second `MISMATCH\tK4` row** into the record stream — parsed as genuine by the frozen counter's own regex. | **YES** |
| F4 | **LOW/MEDIUM** | The `DETAIL` cell is not C-escaped. The real writer's own refusal message can carry a path with `U+2028`, which **tears one K4 record into two lines** for a `str.splitlines()` reader. | **YES** |

**F1 is the one that matters for the claim's own words.** The prereg says the header names "the receipt-writer
bytes it delegates its byte-truth and index-flag checks to". It does not: the header digest is computed by
`writer_binding()` (a separate `open()`), and the compile happens later in `truth_refusal()` (a second
`open()` inside the bootstrap subprocess). Between them the file can change. The frozen counter's KN2 row
cannot see this — it re-reads the file *after* the run and compares against the header, so a header that was
already stale at print time looks fine.

### Severity per shape, against the filed bytes

Each shape has a one-command reproducer (`repro.py --probe <NAME>`). Every row below was run and confirmed on
`821e3703…`; the four failing shapes were re-confirmed on the newest `50c769c7…` with identical results:

| Probe | Shape | Severity | Reader-misleading? | One command |
|-------|-------|----------|-------------------------------|-------------|
| `TOCTOU` | writer file replaced between the header digest read and the compile | **HIGH** | **YES** — header names bytes that did not run | `python3 -B repro.py --probe TOCTOU` |
| `CLEAN` | writer prints the token `CLEAN` then dies | **MEDIUM** | **YES** — fail-open, 0 K4 rows | `python3 -B repro.py --probe CLEAN` |
| `INJECT` | writer `SystemExit` message carries a newline + a `MISMATCH` row | **MEDIUM** | **YES** — 2 rows under the counter's own regex | `python3 -B repro.py --probe INJECT` |
| `DETAIL` | real writer's refusal message carries a path with `U+2028` | **LOW/MEDIUM** | **YES** — one row becomes two lines | `python3 -B repro.py --probe DETAIL` |
| `STDOUT` | writer prints to stdout then raises | **sound** | no — stderr wins, the exception name is carried | `python3 -B repro.py --probe STDOUT` |
| `ESCAPE` | literal `\n` vs a real newline in a path | **sound** | no — distinct spellings | `python3 -B repro.py --probe ESCAPE` |
| `SPLITLINES` | `U+2028` in a path | **sound** | no — the record cell is escaped | `python3 -B repro.py --probe SPLITLINES` |

**Answer to the L1's question (1) — does the final bytes still mislead a reader in any probe shape?** Yes, in
four of the seven shapes, and the four are exactly the delegation-seam ones above. Specifically on the FORGED
detail spelling after the bytes-read change: the `FORGED` **record** cell is now fully escaped
(`_escape_record`), and the `FORGED` **detail** cell is *still* not — the `FORGED` branch interpolates the
writer's message with only `\n`/`\t`/`\r` replaced, so a `U+2028` inside it survives verbatim. Measured
(`repro.py --probe DETAIL`): the K4 record bytes contain `e2 80 a8`, and `str.splitlines()` yields the record
truncated at `…(sep` plus an orphan continuation line `name.txt); the index stat cache conceals a worktree
change; no receipt written`. The frozen counter's `re.M`-anchored regex still counts 1 row, so the counter is
blind to it — but a line-oriented reader is not. **No new probe family was started** for this answer; it is the
already-measured `DETAIL` shape, re-confirmed on the final bytes.

## 1. What I measured first (integrity of the instrument set)

All nine frozen instrument hashes in my brief re-measure **exactly**:

```
b066fa0fc686efdf96c8ebf21a32764070661796c3b4d6e5e99f8aad18669220  census/round-87/c1-false-rows.tsv
ce80195de8b978e5ed00a03c22c3f9911d841c9f277a2a736c730c455178d2e9  census/round-87/c1-items.tsv
9368b34234bf3f56f6c5f3913979ad891a35ac048a54e4ec749895900338d132  census/round-87/c1-mutants.json
fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b  census/round-87/c1-pointer-counter.py
d6f4e612f08fe2aaf2b789e4fe3a2a8a965318161bab2a4dae39363c86fabaef  census/round-87/c1-false-row-harness.py
b0c1472be3d0d957b5b88a92d6d622d895cdd693de5ce491329a6cf3d3c1aaeb  census/round-87/c1-clause-battery.py
4e2b7c060625d3f4b77a26c05d93c167f0e42ea03b8828e8868afb4c8f1baf9e  census/round-87/c2-k4-counter.py
cf8753673b566da1e9a634d790dda70e93efef396f33bb3e42d4fad1425cbddc  census/round-87/controls/c2-before-base-tool.py
70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa  census/round-87/controls/souji-receipt-write.py
```

The frozen counter on the filed tool: `SUMMARY rows=12 mismatches=0 errors=0`, `EXIT=0`; on the base control:
`SUMMARY rows=12 mismatches=3 errors=0`, `EXIT=1`. Both as preregistered.

**The lane tool changed three times under this seat** (the sibling executor was repairing it in parallel):
`0ad9e3bf` → `c2b0784e` → `dbb8046d` → `821e3703`. Every finding below is re-measured against the **final**
bytes `821e37033bf244916f047431387eb65a165442ef1d92c5219a19214d48fb3023`, and the earlier bytes are attributed
explicitly. Where an earlier revision is implicated I name the revision.

## 2. The trust boundary, enumerated

Everything that reaches the new K4 code, and who controls it:

| # | Input | Controlled by | Reaches |
|---|-------|---------------|---------|
| 1 | `git status --porcelain -z` stdout (NUL-separated `XY <path>` records) | **the audited tree** | `k4()` → the `record` cell |
| 2 | the bytes of each path inside those records | **the audited tree** | `record` cell via `_escape_record()` |
| 3 | `git status` stderr | git | `status-failed` detail |
| 4 | the writer file's **bytes** | the tree beside the tool | compiled in a subprocess (`truth_refusal`) |
| 5 | the writer's **stdout** (the verdict channel: `CLEAN` / `FORGED …` / `REFUSED …` / `FLAGFAIL …`) | the delegated writer | parsed by `truth_refusal()` → **the verdict** |
| 6 | the writer's **stderr** | the delegated writer | the no-verdict detail |
| 7 | the writer's **SystemExit message** | the delegated writer | interpolated **unescaped** into the `REFUSED` detail |

Inputs 1–2 are the audited tree's own content: a hostile tree fully controls them. Inputs 4–7 are the
*delegated program's* output. The prereg's frozen limit says the delegation "is still resolved from beside the
tool (a forged writer inside the audited tree stays outside the claim, S85Sentinel F5)". So F2/F3 are *not*
claim-falsifying — they are boundary defects in a channel the prereg explicitly places outside the claim. F1 is
different: it is a defect **in the header mechanism the claim itself introduces**, so it lands inside the claim.

## 3. Probe table

All rows are on the filed bytes `821e3703…`. "Reader-misleading" = a reader of the receipt can be led to a
wrong conclusion about the audited tree.

| # | Input | Observed output | Reader-misleading |
|---|-------|-----------------|-------------------|
| A | rename whose **source** name is `my file.txt`; `-z` stream `b'R  moved.txt\x00my file.txt\x00'` | `MISMATCH\tK4\tmoved.txt\tuncommitted-path\tR` — one row, second field skipped | **no** |
| B | untracked path with byte `0xff` (invalid UTF-8) | `MISMATCH\tK4\tbad\xffname.txt\tuncommitted-path\t??` — read as bytes, no crash | **no** |
| C | untracked path with a **raw `0x01`** byte | `MISMATCH\tK4\tctl\x01name.txt\tuncommitted-path\t??` (bytes `… 63 74 6c 5c 78 30 31 6e …`) | **no** |
| D | untracked path carrying **U+2028** | `MISMATCH\tK4\tsep\xe2\x80\xa8name.txt\tuncommitted-path\t??` — one physical line | **no** |
| E | two files: literal `same\nname.txt` **and** real-newline `same<LF>name.txt` | cells `['same\\nname.txt', 'same\\\\nname.txt']` — distinct | **no** |
| F | **real writer** + a **tracked** path named with U+2028, hidden by `--skip-worktree` | `splitlines()` sees the K4 record as `'MISMATCH\tK4\t.\tstat-cache-concealed\t…(sep'` and a **continuation line** `'name.txt); the index stat cache conceals a worktree change; no receipt written'` | **YES** |
| G | delegated writer prints the token `CLEAN` on stdout, then dies before any check | **K4 rows = []** — the tool concluded the tracked bytes *are* verified | **YES** |
| H | delegated writer raises `SystemExit('x\nMISMATCH\tK4\tINJECTED-ROW\tuncommitted-path\t??')` | the **frozen counter's own regex** finds **2** K4 rows: `('.', 'stat-cache-concealed', 'the receipt writer refused the tree (exit x')` **and** `('INJECTED-ROW', 'uncommitted-path', '??); tracked bytes are unverified')` | **YES** |
| I | the writer file is replaced between the header digest read and the compile | header `sha256=70bbf1c2…`; bytes that ran `sha256=57c40a0f…`; the reader sees `MISMATCH\tK4\t.\tstat-cache-concealed\tRECEIPT-WORKTREE-STAT-CONCEALED: EVIL-WRITER-RAN` | **YES** |
| J | the tool sits in a directory whose path contains a space | header `# writer path=/…/M-M10 with space/souji-receipt-write.py sha256=…`; the frozen counter's KN2 regex `^# writer path=(\S+) sha256=([0-9a-f]{64})$` **does not match** | **YES** |

### Attribution — which defects the r87 wave introduced, and which it repaired

The lane-base tool (`cf875367…`) behaves **identically** to the filed bytes on F, G and H: these are
**pre-existing** seams in the delegation protocol, not r87 regressions. But r87 *widened* their reach:

* **G (CLEAN spoof)** — the base tool also reports 0 K4 rows. r87 did not introduce it; it also did not close it.
* **H (REFUSED injection)** — the base tool also yields 2 rows under the counter's regex. r87 did not introduce it.
* **F (detail-cell tear)** — the base tool also tears the row. r87 hardened the **record** cell
  (`_escape_record`) but left the **detail** cell unescaped, so the same class of defect survives one column over.
* **I (TOCTOU)** — **introduced by r87.** The base tool has no header at all; the header *is* the r87 repair, and
  the header's digest is taken from a different read than the compile.

Two defects that r87 (and its wave repair) **did** close, which I verified and am not re-declaring:

* The **rename second NUL field**. At the first C2 revision `0ad9e3bf` the source path `my file.txt` was parsed
  as its own status record, producing a **phantom** row `MISMATCH\tK4\tfile.txt\tuncommitted-path\tmy` naming a
  path that does not exist in the worktree (`file.txt` was never created; the tree held `file.txt` and
  `moved.txt`). The wave repair `c2b0784e` decides the skip by the **status letters** (`R`/`C`) rather than by
  the field's shape, and the phantom is gone in `c2b0784e` and `821e3703`. The prereg's frozen limit — "the `-z`
  arm skips a rename's second NUL field" — now holds.
* The **non-UTF-8 path crash** and the **non-injective escape** (literal `\n` vs a real newline collapsing to one
  cell) — both closed by the wave repair; row B and row E above confirm.

## 4. Findings, with reproducer

### F1 — HIGH — the writer header names bytes that did not run

**Mechanism.** `writer_binding()` (line ~200) opens `K4_TRUTH_WRITER`, hashes it, and returns the header. It is
called from `main()` and printed **before** `rep.k4()` runs. `truth_refusal()` then launches the bootstrap
subprocess, whose **own** `open(path, 'rb').read()` reads the file **again** and compiles those bytes. Two reads,
two different moments.

**Exploit path.** Anyone who can write beside the tool replaces `souji-receipt-write.py` between the two reads.
The header still prints the digest of the *old* bytes; the *new* bytes are compiled and run, and their verdict is
what the reader sees.

**Evidence** (row I, reproduced by `repro.py --probe TOCTOU`):

```
header        : # writer path=/…/kit-toctou.ii7ukiqf/souji-receipt-write.py sha256=70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa
bytes executed: sha256=57c40a0f63f786bf0a71b0420d93ca08285d63a3450ac3dc92b44978c9c82cf8  (EVIL writer ran: True)
BOUND?        : NO — the header names bytes that did not run
```

The reader is shown `MISMATCH\tK4\t.\tstat-cache-concealed\tRECEIPT-WORKTREE-STAT-CONCEALED: EVIL-WRITER-RAN`
while the header names a digest that does not correspond to the code that produced it. The window is **not** a
micro-race: it is the entire K1/K2/K3 sweep — measured **0.020 s** between the header print and the compile on a
trivial tree, and proportionally longer on the real lane tree.

**Why the frozen counter cannot see it.** KN2 re-reads the writer file *after* the run and compares that digest
to the printed one. A header that was **already stale when printed** compares equal to the file only if the file
was changed back; in the general case KN2's "first == live" is checked against the *post-run* bytes and the
stale-during-the-run case slips past. Verified: `KN2 'first == live' : False` while the header regex still
matches.

**Impact.** The header is the artifact a reader uses to decide *which* writer produced a K4 verdict. F1 makes that
artifact untrustworthy in exactly the direction that matters: a writer that has been swapped in produces a
verdict while the receipt's provenance line names a different program. This is the "fabricated provenance"
failure the prereg's own stated limit was reaching for.

**Smallest remediation.** Read the writer bytes **once** and use that single byte string for both the digest and
the compile — e.g. have the bootstrap print the digest of the bytes it actually compiled, and have the parent
print *that* digest instead of a second independent read. One extra `print('DIGEST %s' % hashlib.sha256(src).hexdigest())`
in the bootstrap plus one parent-side substitution closes the seam; the header then names the bytes that ran by
construction.

### F2 — MEDIUM — a crashed delegation is read as a clean verdict (fail-open)

**Mechanism.** The verdict channel is the bootstrap's **stdout**, and the parent decides "clean" by
`if out == "CLEAN":` — it never consults `proc.returncode`. A writer that prints `CLEAN` and *then* dies leaves
`CLEAN` as the last stdout token, and the parent takes the clean branch.

**Evidence** (row G):

```
K4 rows       : []
=> the tool concluded the tracked bytes ARE verified (no K4 row): True
```

The writer's `AttributeError('never got to the truth check')` appears **nowhere** in the output. The tool reports
a clean tree for a tree whose truth check never ran. Identical on the base tool, so pre-existing.

**Impact.** A fail-open on the one arm whose whole purpose is to *not* certify unverified bytes. The prereg's
frozen limit puts a forged writer beside the tool outside the claim, so this is a boundary defect rather than a
claim falsifier — but the base tool has the same hole and the r87 wave closed the other two seams on this path
without closing this one.

**Smallest remediation.** Gate the verdict on the child's exit status: treat `CLEAN` as clean only when
`proc.returncode == 0` and the stdout token is exactly `CLEAN`. One extra condition at the `if out == "CLEAN":`
site closes it; any nonzero exit then falls through to the existing no-verdict branch, which already carries the
exception name.

### F3 — MEDIUM — the `REFUSED` branch injects a forged row into the record stream

**Mechanism.** `truth_refusal()` handles the refusal case with
`return f"the receipt writer refused the tree (exit {out.split(' ', 1)[-1]}); …"`. The writer's `SystemExit`
message is interpolated **raw** — no escaping. `emit()` then prints it as one `MISMATCH\tK4\t…` line, and a
newline inside it splits that line in two.

**Evidence** (row H) — the frozen counter's **own** regex sees the forged row as genuine:

```
counter-regex rows=[('.', 'stat-cache-concealed', 'the receipt writer refused the tree (exit x'),
                    ('INJECTED-ROW', 'uncommitted-path', '??); tracked bytes are unverified')]
```

**Impact.** A reader of the record stream (and the counter's own parser) sees a K4 row naming
`INJECTED-ROW` with class `uncommitted-path` — a path the tool never observed in the tree. The row count, and any
consumer that keys on `uncommitted-path` rows, is corrupted by the delegated program's own error text. Identical
on the base tool.

**Smallest remediation.** C-escape the `REFUSED` payload exactly as the `FORGED` payload is already escaped
(`replace("\n","\\n").replace("\t","\\t").replace("\r","\\r")`) before interpolating it. Two lines.

### F4 — LOW/MEDIUM — the detail cell is not escaped, so one K4 record becomes two lines

**Mechanism.** `_escape_record()` was added for the **record** cell; the **detail** cell is not escaped. The real
writer's `_truth_refusal` builds its message from `os.fsdecode(p)` of the offending path, so a path containing
`U+2028` reaches the detail cell verbatim. `U+2028` is a line boundary for `str.splitlines()`.

**Evidence** (row F, re-confirmed on the final bytes `821e3703…` by `repro.py --probe DETAIL`) — **no forged
writer needed; the audited tree alone suffices**:

```
K4 record (splitlines) : 'MISMATCH\tK4\t.\tstat-cache-concealed\tRECEIPT-WORKTREE-STAT-CONCEALED: 1 tracked path(s) git status reports clean do not hash to the object id the index records (sep'
continuation line      : 'name.txt); the index stat cache conceals a worktree change; no receipt written'
detail bytes carry U+2028 (e2 80 a8)? True
torn?                  : True
```

The record bytes contain `e2 80 a8` (U+2028) unescaped. The counter's own regex still finds 1 row (it is
`re.M`-anchored), so the frozen counter is blind to it — but a reader that splits the receipt on lines sees a
truncated first line and an orphan second line that begins `name.txt);`, i.e. **two** lines where the receipt
format promises one `MISMATCH` row per line. Identical on the base tool.

**Note on the final bytes.** The `FORGED` branch on `821e3703…` replaces only `\n`/`\t`/`\r` in the message; it does
**not** run the message through `_escape_record()`, and it does not escape `U+2028`/`U+2029`. So the wave repair
that hardened the *record* cell left the *detail* cell one column over with the same class of defect.

**Smallest remediation.** Route the detail cell through the same byte-escaping used for the record cell, or
escape `U+2028`/`U+2029` alongside `\n`/`\t`/`\r` at the point the detail is built.

### J — LOW — the header path is not escaped, so the counter's own KN2 regex can miss it

`# writer path=…` interpolates an absolute path raw. The frozen counter's KN2 row parses it with
`^# writer path=(\S+) sha256=([0-9a-f]{64})$`; `(\S+)` cannot match a path containing a space. On this lane's
own path there is no space, so the counter is green today — but the counter's `--work` directory is
operator-chosen and the tool is copied into `<work>/kits/<row>/`, so any work path with a space silently
degrades KN2 to "no header found". **Smallest remediation:** percent-escape or quote the path in the header, and
relax the counter's regex to `(.+?) sha256=([0-9a-f]{64})$`.

## 5. What I checked and found sound

* **The rename second NUL field** (row A) — skipped correctly by status letters, not by shape.
* **A non-UTF-8 path** (row B) — read as bytes; no crash; the row is emitted.
* **A raw `0x01` in a path** (row C) — spelled `\x01`; the record cell stays one physical line.
* **A `U+2028` in a path** (row D) — spelled `\xe2\x80\xa8`; one physical line.
* **Escape injectivity** (row E) — a literal `\n` and a real newline now have **different** spellings, so a
  reader can tell two files apart.
* **An unstaged worktree rename** — `-z` gives ` D old\0?? new\0`; both paths are reported (no `R` record exists,
  so the skip is not triggered).
* **Copy detection** — a repo-local `status.renames=copies` produced `?? copy.txt\0`; the tool and the writer's
  own `_porcelain_paths` name the same path set.
* **A status record whose first two bytes are not a status pair** — the shape test `rec[2:3] != b" "` plus the
  status-letter skip handles it; a path like `ab cd.txt` is reported once, as `ab cd.txt`.
* **A writer whose stderr carries a forged `MISMATCH\tK4\t…` line** — the detail is built by `_stderr_tail`,
  which takes the **last** non-empty line only; the forged line does **not** become a row. (Verified directly.)
* **A multi-line exception message** — `_stderr_tail` keeps the last line, which loses the exception *name*
  (`RuntimeError` → only `boom on line two` survives). This is the trade-off the r87 code documents
  ("keep both ends" now applies to a long line); the prereg's KN1 only requires `AttributeError` to appear, which
  it does for a single-line message. **Not filed as a finding** — the r87 wave repair `_stderr_tail` keeps both
  ends of an over-long line, and a multi-line *exception message* is a rarer shape than the traceback the claim
  names.

## 6. Reproducer

`repro.py` sits beside this report in the seat directory and runs every probe. It never writes to the lane:
the tool under test is **copied** into a scratch kit beside a chosen writer, and every fixture is a fresh
`mktemp -d` repo under the seat scratch with `git rev-parse --show-toplevel` asserted equal to the fixture dir
before the first commit.

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-87/w1/S87Sentinel
python3 -B repro.py                 # all probes
python3 -B repro.py --probe TOCTOU  # one probe
```

Exit status of each probe is printed as `BOUND?`, `stderr name present?`, `=> the tool concluded …`,
`rows the frozen counter's own regex sees`, `collide?`, `torn?`.

**Instrument hashes re-measured at the time of writing.** `tools/souji-record-agreement.py` =
`50c769c7c3c347333966a1f7b536125e6c3c9b962dcf113248bcb5f5d728c9a6` at the moment of the final re-check — it
changed **four** times during this seat (`0ad9e3bf` → `c2b0784e` → `dbb8046d` → `821e3703` → `50c769c7`), the
sibling executor repairing it in parallel. The four findings (F1–F4) and the three "sound" shapes were each
re-confirmed on `821e3703…`, and F1 (TOCTOU), F2 (CLEAN), F3 (INJECT) and F4 (DETAIL) were re-confirmed once more
on the newest `50c769c7…` with identical results (`BOUND?: NO`, `=> the tool concluded the tracked bytes ARE
verified: True`, `rows the frozen counter's own regex sees: 2`, `torn?: True`). The wave repair `578cbf2c`
closed the rename-phantom and non-UTF-8-crash defects I reproduced against `0ad9e3bf`.
`tools/souji-receipt-write.py` = `70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa` (unchanged).

`repro.py` always hashes and prints the tool bytes it actually ran against, so a reader can confirm which
revision a given probe result belongs to.

## 7. Scope note for the L1

These findings are **outside** the frozen C2 claim's scope for F2/F3/F4/J (the prereg's stated limit places a
forged writer beside the tool outside the claim), and **inside** it for **F1** — F1 is a defect in the very
mechanism the claim introduces, namely that the header names the delegated bytes. Under the frozen kill rule F1
does not fail the claim (the counter is green on the filed bytes and the before-arm reproduces `mismatches=3`),
so this is a **narrowing input for `plans/round-87.md`**, not a claim falsifier. I have not touched
`census/round-87/preregistration.txt`.

I did **not** file the multi-line-exception-message case as a finding (see §5) and I did **not** re-declare the
rename-phantom or non-UTF-8-crash defects — the sibling wave repair closed both, and I verified the closure.

## 8. Cleanup

Scratch `/fast/scratch/hyaku/souji-r87/S87Sentinel/` held this seat's clones, kits and probe scripts and is
**removed** — verified absent (`ls` → "No such file or directory"). The other directories under
`/fast/scratch/hyaku/souji-r87/` belong to sibling seats and were left untouched. `repro.py` recreates its own
scratch on demand (it `mkdir -p`s and writes only under the seat scratch path).

The only files this seat leaves in the lane are this report and `repro.py` beside it, both under
`.ufo/waves/round-87/w1/S87Sentinel/`. **No lane tool, instrument, control, receipt, preregistration or
`MANIFEST.json` was edited by this seat**; the two modified entries in `git status` (`tools/souji-record-agreement.py`,
`census/round-87/c2-byte-arm.py`) are the sibling executor's wave repairs, which were in flight throughout.
