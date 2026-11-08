# S86Sentinel — adversarial security review of the C2 repair (K4 as a privilege boundary)

Lane souji round-86, wave 1, seat S86Sentinel. Scope: `tools/souji-record-agreement.py`
(sha256 `4cc3b9450dc058e4c05a312b0918a5099b5e3fdbe3c62c779d781462068468df`), the r86 C2 repair
"record-agreement K4 carries the writer's index-flag sweep and keeps record paths one line".

Every probe below runs the FILED tool bytes (or a byte-identical copy of them, with the single
stated constant change) against a synthetic fixture under
`/fast/scratch/hyaku/souji-r86/S86Sentinel/` — never against the lane tree, never against
`tools/`. Receipts and the probe drivers are in this seat's `receipts/` directory.

**Verdict in one line: the repair is sound on the tree it is pointed at, but the flag sweep is
routed through the writer's `git()` helper, which reads a DIFFERENT config view from the tool's
own status read; a caller-supplied `GIT_CONFIG_PARAMETERS`/`GIT_CONFIG_COUNT` masks the
skip-worktree tag from `git ls-files -v` and K4 returns a CLEAN verdict for a tree whose nested
repository commit moved — the exact KG1 class the repair exists to catch. This is a fail-open.
It is invisible to the frozen counter, whose own `ENV` strips every `GIT_*` variable.**

---

## 1. The repair, exactly as filed

`git diff 2acbbfc8..HEAD -- tools/souji-record-agreement.py` (the C2 repair commit) adds two
halves:

**Half A — the index-flag sweep.** Inside the `-I -B` bootstrap subprocess, after
`mod._truth_refusal(root)` returns no message, the tool now calls the writer's own
`mod.git(root, 'ls-files', '-v', '-z', ':(top)')`, and for the first record whose tag is not `H`
calls `mod._flag_refusal(root, tag, p)`. The bootstrap's verdict string becomes `FORGED <msg>`.

**Half B — the record escaping.** The `FORGED` branch's detail text is now
`out[len("FORGED "):].replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")`, and K4's
class is chosen by `msg.startswith(("RECEIPT-GITLINK-CONCEALED", "RECEIPT-INDEX-"))` →
`index-flag-concealed` instead of `stat-cache-concealed`.

**Verified baseline.** The frozen counter is green on the filed bytes:

```
python3 -B census/round-86/c2-k4-counter.py --tool tools/souji-record-agreement.py \
    --work /fast/scratch/hyaku/souji-r86/S86Sentinel/wA
→ ROW KG1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|index-flag-concealed']
  ROW KG2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
  SUMMARY rows=9 mismatches=0 errors=0 ; EXIT=0
```
(receipt `receipts/counter-filed.txt`). The filed before-control is unchanged:
`census/round-86/controls/c2-before-base-tool.txt` → `SUMMARY rows=9 mismatches=2 errors=0`,
`KG1 k4=0 named=no`, `KG2 named=no`, `EXIT=1`. Both arms are as the preregistration states, and
the seven r85 rows are unchanged. **I do not dispute the counter's result.**

---

## 2. HEADLINE — the two halves of K4 read different config views (FAIL OPEN)

### 2.1 The mechanism

`tools/souji-record-agreement.py` has its own `git()` helper; the r86 sweep now runs the
**writer's** `git()` helper instead. They scrub different things:

| | `tools/souji-record-agreement.py` `git()` (the tool's status read) | `tools/souji-receipt-write.py` `git()` (the writer's — now the sweep's) |
|---|---|---|
| scrubs | `GIT_DIR`, `GIT_WORK_TREE`, every `GIT_CONFIG_*` | `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`, `GIT_ATTR_SOURCE`, `PATHSPEC_ENV` |
| pins | `core.fsmonitor=false`, `core.fileMode=true`, `core.checkStat=default`, `core.trustctime=true`, `core.excludesFile=devnull`, `status.showUntrackedFiles=all` | `core.fsmonitor=false`, `core.fileMode=true`, `core.checkStat=default`, `core.trustctime=true`, `core.excludesFile=devnull` |
| **does NOT scrub** | `GIT_INDEX_FILE`, `GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_REPLACE_REF_BASE`, `PATH` | **`GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_*`/`GIT_CONFIG_VALUE_*`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_REPLACE_REF_BASE`, `PATH`** |

`core.sparseCheckout` is pinned by **neither** helper (probe Q3, receipts `probe-set-Q.txt`).
When `core.sparseCheckout` is enabled (`true` or `1`; the key alone suffices — `core.sparseCheckoutCone`
alone does **not** mask, verified separately), `git ls-files -v` renders a skip-worktree index
entry as tag `H` instead of `S` — the bit is still in the index (`ls-files --debug` shows
`flags: 40004000` in the default view and `flags: 4000` in the sparse-checkout view), but the
tag the sweep keys on is `H` (probe H1/K2/K3).

### 2.2 The reproducer (KG1 class — the class the repair exists to close)

Command (probe I1, receipts `probe-set-I.txt`):

```
# fixture: nested repo 'nest' commit moved forward; its gitlink entry marked skip-worktree
git -C $D update-index --skip-worktree nest
env GIT_CONFIG_PARAMETERS="'core.sparseCheckout=true'" \
    python3 -B tools/souji-record-agreement.py --root $D --rev <40-hex>
```

Output:

```
[2] TOOL half of K4: git status --porcelain (GIT_CONFIG_* scrubbed)
    rc=0 out=b''   -> the tool sees a CLEAN tree, so no uncommitted-path row
[3] WRITER half of K4 (the r86 flag sweep): git ls-files -v -z :(top)
    with the tool's config view : [b'S nest']
    with the writer's config view: [b'H nest']    <- the sweep sees tag 'H': no refusal
[4] the truth check _truth_refusal skips mode 160000 (gitlink) entirely
[5] the tool under the env route:  rc=1 k4_rows=0   K4 rows: []
    control (no env route):         k4_rows=1  -> index-flag-concealed / RECEIPT-GITLINK-CONCEALED
VERDICT I1: FAIL OPEN
```

`GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.sparseCheckout GIT_CONFIG_VALUE_0=true` gives the
same result (probe F5). On the plain-file class (worktree bytes changed under skip-worktree) the
env route also silences the **stat-cache** check, because the writer's `_truth_refusal` skips
every path its own `git status` lists, and under the sparse-checkout view the writer's status
lists `a.txt` while the tool's status does not (probe K1):

```
TOOL view (GIT_CONFIG_* scrubbed)  rc=0 out=b''
WRITER view (GIT_CONFIG_PARAMETERS kept) rc=0 out=b' M a.txt\n'
```

so `a.txt` is neither reported by K4 nor re-hashed by the truth check.

### 2.3 Base vs filed, same tree, same environment (probe L1)

| tree | tool | no env route | env route |
|---|---|---|---|
| KF-like (tracked file changed under skip-worktree) | BASE (lane-base bytes) | 1 `stat-cache-concealed` | **0 (SILENT)** |
| KF-like | **FILED (r86 repair)** | 1 `stat-cache-concealed` | **0 (SILENT)** |
| KG1 (nested commit moved under skip-worktree) | BASE | 0 (SILENT) | 0 (SILENT) |
| KG1 | **FILED (r86 repair)** | 1 `index-flag-concealed` | **0 (SILENT)** |

**The repair's new capability is the thing the env route removes.** On KG1 the filed tool is the
only one that ever reports the class, and under the env route it stops reporting it. The stat-cache
silencing of the KF-like tree is a pre-existing r85 defect (the r85 repair already pinned the
*tool's* status read but the *writer's* read inside the truth check was never pinned), so the
env route does not introduce that one; it does newly neutralise the r86 addition.

### 2.4 Why the counter cannot see this

`census/round-86/c2-k4-counter.py` builds its own environment:

```python
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
```

so no `GIT_CONFIG_*` variable can reach the tool under the counter. **The frozen 9-row counter
is structurally incapable of exercising this route.** A counter that ran one additional arm with
`GIT_CONFIG_PARAMETERS="'core.sparseCheckout=true'"` in the child environment would score the
filed tool `k4=0` on KG1. That is the single highest-value addition to the instrument, and it is
one line.

### 2.5 Why the writer's own entry point does not cover it

The receipt writer refuses these environments at its own entry point, before any git call
(probe I2/F3, receipts `probe-set-F.txt`):

```
GIT_CONFIG_PARAMETERS  writer entry point: rc=2 refused: RECEIPT-ENV-CONFIG-SET: GIT_CONFIG_PARAMETERS set in the writer's environment; unset them and retry
GIT_CONFIG_COUNT       writer entry point: rc=2 refused: RECEIPT-ENV-CONFIG-SET: GIT_CONFIG_COUNT, GIT_CONFIG_KEY_0, GIT_CONFIG_VALUE_0 set in the writer's environment; unset them and retry
GIT_INDEX_FILE         writer entry point: rc=2 refused: RECEIPT-INDEX-ENV-SET: GIT_INDEX_FILE is set in the writer's environment (value not shown); unset it and retry
```

**But the K4 bootstrap does not go through the writer's entry point.** It `exec()`s the writer's
source and calls `mod.git()` / `mod._truth_refusal()` directly, so *none* of those refusals is
ever reached. The repair routes the sweep through the writer's helper while bypassing the
writer's guard on that helper. That is the shape of the defect: **the repair inherits the
writer's implementation and not the writer's preconditions.**

### 2.6 Smallest remediation

Two independent one-line-ish fixes; either closes the route:

1. **Pin the config on the sweep's own read.** The bootstrap already runs in an isolated
   interpreter; add the same pins the tool's `git()` uses to the sweep's `mod.git(...)` call, or
   (better) do not call the writer's `git()` at all — issue `git ls-files -v -z :(top)` from the
   tool's own pinned helper and pass the tag to `mod._flag_refusal`. The sweep then reads the
   same view as the status read and the split-brain disappears. This also removes
   `GIT_INDEX_FILE` and `GIT_OBJECT_DIRECTORY` from the sweep's reach.
2. **Refuse the env in the tool.** Add to `tools/souji-record-agreement.py`'s own `git()` (or to
   `truth_refusal`'s caller) the writer's r66 refusals: `GIT_CONFIG_PARAMETERS`,
   `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_*`/`GIT_CONFIG_VALUE_*`, `GIT_INDEX_FILE`,
   `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_REPLACE_REF_BASE` →
   refuse, never measure. This restores the invariant r85's repair established for the status
   read (r85 S85Sentinel F6) to the whole K4 measurement.

Fix 1 is strictly better: it makes the two halves of one measurement agree by construction
rather than by refusal. Fix 2 alone would still leave `core.sparseCheckout` reachable if it
arrived by another route (e.g. the repository's own `.git/config` — see §3.1).

---

## 3. Every mechanism by which the repaired K4 can return CLEAN for a tree it did not measure

The assignment asked for at least five; I probed **nine** distinct mechanisms. Each is a
separate copy under my scratch, each with its command, output and a fail-open/fail-closed
verdict. "Names the mechanism?" = does the record say *why* it reported (or, for a fail-open,
is there any record at all?).

### 3.1 `GIT_CONFIG_PARAMETERS` / `GIT_CONFIG_COUNT` — **FAIL OPEN** (highest severity)

Probes F1, F2, F5, H1, H2, I1, K1, K2, K3, K4, L1, Q2, Q3.
Tree: honest, uncommitted nested-repo commit move + skip-worktree gitlink (KG1 class), or a
plain tracked file changed under skip-worktree.

```
GIT_CONFIG_PARAMETERS="'core.sparseCheckout=true'"  -> k4_rows=0 (SILENT)
GIT_CONFIG_COUNT=1 core.sparseCheckout=true          -> k4_rows=0 (SILENT)
control (no env route)                               -> k4_rows=1 index-flag-concealed
```

**Names the mechanism?** No record at all. K4 is silent on a tree with a concealed nested-repo
commit move. The class the repair was filed to close is invisible.

Related, weaker, and *inside* the claim: the same key set in the **repository's own
`.git/config`** (`core.sparseCheckout=true`) does **not** produce a fail-open — the tool's status
read sees ` M nest` and reports `uncommitted-path` (probe H2). So the in-tree route fails closed
but for the wrong reason (a different mechanism than the class the repair answers). The env route
is the one that fails open, because it desynchronises the two halves.

Severity: **HIGH.** The attack needs no write access to the tree and no write access to
`tools/` — only the ability to set an environment variable in the tool's process. The lane's own
receipt writer treats exactly that variable as a refusal condition, so the lane's threat model
already declares it hostile. The instrument's verdict silently depends on it.

### 3.2 The writer's `_flag_refusal` returns an empty message — **FAIL OPEN**

Probe P3 / C1 / G2. A writer whose `_flag_refusal` returns `""` (or a writer whose `git()` returns
an empty index) makes the sweep find nothing to report.

```
P3  writer whose _flag_refusal returns an empty message -> k4_rows=0 (SILENT)
C1  a stub writer that answers CLEAN itself               -> k4_rows=0 (SILENT)
G2  the writer beside the tool is a symlink to a stub      -> k4_rows=0 (SILENT)
P5  a writer whose git() hides the index from the sweep   -> k4_rows=0 (SILENT)
```

**Names the mechanism?** No record at all.

The code shape (probe M3, receipts `probe-set-M.txt`):

```python
for rec in fl.stdout.split(bytes([0])):
    ...
    tag, _, p = rec.partition(bytes([32]))
    if tag != bytes([72]):
        msg = mod._flag_refusal(root, tag, p)
        break
print('CLEAN' if not msg else 'FORGED ' + msg)
```

`msg` is the refusal message and is tested for **truth**, not for **non-None**. The r85 code's
`msg` came from `_truth_refusal`, whose contract is "None or a message". The r86 repair routes a
*second* function's return value through the same truth test, so an empty refusal string is
indistinguishable from "no concealment". A writer that declines to refuse is read as a clean
tree.

This is a genuine widening of the r85 S85Sentinel F5 blast radius. Probe M1 puts base and filed
side by side on one tree: the base tool never consults `_flag_refusal` at all, so a doctored
writer changes nothing for it; the filed tool now asks the writer for **three** things
(`_truth_refusal`, `git()`, `_flag_refusal` — probe L3) instead of one, so the same unpinned
writer now decides whether the index-flag class is reported.

Severity: **MEDIUM** as a standalone (the preregistration's stated limits put "a forged writer
inside the audited tree" outside the claim), but it is the mechanism that makes §3.1's class
unreportable *and* it is what the repair newly added. The stated limit says the forged writer is
out of the claim; it does not say the repair routes the *new* check through it.

Smallest remediation: in the bootstrap, treat "a non-H record was found" as the finding and the
refusal text as its decoration — e.g. `msg = mod._flag_refusal(root, tag, p) or ("RECEIPT-INDEX-FLAG-CONCEALED: " + p.decode("utf-8","replace"))` — so a falsy message can never become CLEAN.

### 3.3 The writer has no `_flag_refusal` at all — **FAIL CLOSED**

Probe P4. The AttributeError surfaces as a traceback and the tool reports:

```
MISMATCH	K4	.	stat-cache-concealed	the receipt writer produced no verdict (exit 1: Traceback (most recent call last):
  File "<string>", line 26, in <module>
    msg = mod._flag_refusal(root, tag, p)
AttributeError: module 'souji_receipt_write' has no att); tracked bytes are unverified
```

**Names the mechanism?** Yes, in the detail — but see §4: the *class* says `stat-cache-concealed`,
which names the wrong mechanism.

### 3.4 A subprocess timeout — **FAIL CLOSED**

Probe D1 (tool copy with `timeout=3` instead of the filed `timeout=600`; the only difference from
the filed bytes is that one constant — `TimeoutExpired` is a `subprocess.SubprocessError`
subclass, so the same branch fires at 600 s):

```
MISMATCH	K4	.	stat-cache-concealed	the receipt writer could not be run (TimeoutExpired: Command '[...'
```

**Names the mechanism?** Yes ("could not be run (TimeoutExpired…)"). No writer process survives
the timeout (probe E7: `leftover writer processes: []`) — the tool's cleanup is adequate.

### 3.5 The writer is absent — **FAIL CLOSED**

Probe P6 (a copy of the tool with no writer beside it):

```
MISMATCH	K4	.	stat-cache-concealed	the receipt writer is not beside this tool
(/fast/scratch/hyaku/souji-r86/S86Sentinel/fx/p6/tool/souji-receipt-write.py); tracked bytes are unverified
```

**Names the mechanism?** Yes, by name and path.

### 3.6 The writer is a symlink / a copy — **FAIL OPEN** (when the target is a stub)

Probe G2 / P7. The tool resolves the writer with `realpath` on **its own** path (r85's fix) and
then checks `os.path.isfile(K4_TRUTH_WRITER)`. `isfile` follows symlinks, so a symlink at the
writer path is loaded and executed:

```
G2  the writer beside the tool is a symlink to an outside file -> k4_rows=0 (SILENT)
P7  the writer beside the tool is a symlink to the REAL writer -> k4_rows=1 index-flag-concealed
```

So the symlink is followed (P7 shows the real writer is loaded through the link and works), and
when the link targets a stub, the stub decides the verdict. **Names the mechanism?** No record.

Note the asymmetry with the r85 repair: r85's fix realpaths the *tool*, so a symlinked tool no
longer loads whatever sits beside the link; the *writer* path is not realpath'd. A symlink at
`tools/souji-receipt-write.py` is loaded as-is.

### 3.7 `GIT_INDEX_FILE` — **FAIL CLOSED, but the mechanism is mis-attributed**

Probes B1, C5, G4, E6. The tool's own `git()` does **not** scrub `GIT_INDEX_FILE`, so the
caller can point the whole measurement at a different index view. On the KG1 tree:

```
C5/G4  GIT_INDEX_FILE=doctored -> K4ROW 'MISMATCH\tK4\tnest\tuncommitted-path\tM'
```

A row is emitted — but it reports `uncommitted-path` for `nest`, i.e. it describes the *doctored
view*, not the concealment the real index holds. The row does not name the mechanism it should.

**Names the mechanism?** No — the class is a different mechanism's class. This is the same
pre-existing defect r85 S85Sentinel F6 named for the status read; the r86 repair inherits it
into the sweep because the sweep also runs under the doctor's `GIT_INDEX_FILE`.

### 3.8 `GIT_OBJECT_DIRECTORY` / `GIT_ALTERNATE_OBJECT_DIRECTORIES` / `GIT_COMMON_DIR` — **FAIL CLOSED**

Probes E5, D5, B6.

```
GIT_OBJECT_DIRECTORY        -> MISMATCH K4 . status-failed  fatal: bad object HEAD
GIT_ALTERNATE_OBJECT_DIRECTORIES -> MISMATCH K4 . index-flag-concealed  RECEIPT-INDEX-FLAG-CONCEALED: a.txt carries index flag S ...
GIT_COMMON_DIR             -> MISMATCH K4 . status-failed  fatal: bad object HEAD
```

**Names the mechanism?** Partly: the `status-failed` rows name git's own error, not the env
route; the alternate-objects row happens to report the right class.

### 3.9 `--root` inside a subdirectory — **FAIL CLOSED**

Probes B2, D6, N3. The writer's own entry point resolves the repository toplevel before every
`ls-files` (r64 C1); the K4 bootstrap passes `--root` where the writer expects the toplevel:

```
D6  --root=repo/sub -> MISMATCH K4 . stat-cache-concealed  the receipt writer refused the tree (exit 2); tracked bytes are unverified
N3  git -C repo/sub ls-files -v -z :(top) -> [b'S ../a.txt', b'H ../ln', ...]
```

**Names the mechanism?** Weakly: "the receipt writer refused the tree (exit 2)" — the *reason* the
writer refused is lost (see §4.2). Note the sweep's paths would carry `../` prefixes (relative to
the CWD, not the repo top), so had the sweep run, it would have named a path the reader cannot
resolve from the repo root.

### 3.10 A substituted `git` on `PATH` — **FAIL OPEN** (outside the claim)

Probe Q1. Both helpers exec a bare `git` resolved through `PATH`; neither scrubs `PATH`. A fake
`git` that answers `ls-files` and `status` with success and empty output yields `k4_rows=0
(SILENT)`. The tree's own bytes are not the audited surface here, so this is outside the claim,
but it is a named mechanism.

### 3.11 `--no-worktree` — **FAIL OPEN by design**

Probe D4: the flag skips K4 entirely, so a concealed change yields no K4 row. That is the
flag's documented purpose; it is named here only so the sweep is complete.

---

## 4. The escaping change: what it does and does not fix

### 4.1 What it fixes (holds)

Probe P1. A path whose name is
`x\nMISMATCH\tK4\t.\tindex-flag-concealed\tFORGED-BY-PATH.txt` is planted as a tracked file with
a skip-worktree flag. The r86 escaping renders it as a single physical line and the path is
**not** able to forge a second `MISMATCH` row:

```
K4ROW 'MISMATCH\tK4\t.\tindex-flag-concealed\tRECEIPT-INDEX-FLAG-CONCEALED:
        x\\nMISMATCH\\tK4\\t.\\tindex-flag-concealed\\tFORGED-BY-PATH.txt carries index flag S; ...'
rows forged by the path name: []
physical MISMATCH rows: 8
```

So **for the class the repair targets, the escaping holds**: a path name cannot split the record
or forge a second row. The claim's "one K4 record stays one physical line" is true for the
`FORGED` branch.

### 4.2 What it does not fix

**(a) The escaping is applied to one branch only.** The r86 change touches exactly one line —
the `FORGED` branch inside `truth_refusal`. The other K4 detail producers are untouched
(probe O2, receipts `probe-set-O.txt`):

```
truth_refusal:  return (out[len("FORGED "):].replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r"))
k4():           self.bad("K4", ".", "status-failed", proc.stderr.strip())
k4():           self.bad("K4", path, "exemption-not-allowed", ...)
k4():           self.bad("K4", path, "uncommitted-path", line[:2].strip() or "??")
```

With an **honest** writer and a **corrupt index** — no writer substitution, no environment
manipulation — the `status-failed` detail embeds git's raw two-line stderr and the record splits
(probe O1):

```
git status --porcelain rc=128 stderr=b'error: bad index version 9\nfatal: index file corrupt\n'
tool stdout: b'MISMATCH\tK4\t.\tstatus-failed\terror: bad index version 9\nfatal: index file corrupt\nkeys=4 ...'
physical lines NOT starting with MISMATCH but inside the K4 detail: ['fatal: index file corrupt']
RECORD SPLIT: True
```

Probe P2 confirms this is **pre-existing** (the BASE tool splits identically), so it is not a
regression introduced by r86 — but it means the claim's "one K4 record stays one physical line"
holds only for the `FORGED` branch, and a reader parsing the tool's stdout line-by-line can be
misled by a second physical line inside one record.

**(b) The escaping is not injective.** Probe D2: a path whose name literally contains the two
characters `\n` (backslash, n) and a path whose name contains a real newline produce the **same**
record text:

```
detail(real newline)       = 'RECEIPT-INDEX-FLAG-CONCEALED: a\\nb.txt carries index flag S; ...'
detail(literal backslash-n)= 'RECEIPT-INDEX-FLAG-CONCEALED: a\\nb.txt carries index flag S; ...'
COLLISION: True
```

The record still *names* a path, but it cannot say **which** of two distinct paths it names. The
preregistration says "still names the path"; strictly, it names *an* escaped rendering of the
path, and two distinct trees can produce byte-identical records. This is a fidelity limit, not a
fail-open.

**(c) Invalid UTF-8 aliases.** Probe D3: two distinct invalid-UTF-8 names both render with
U+FFFD and collide:

```
detail(bad\x80) = 'RECEIPT-INDEX-FLAG-CONCEALED: amb\ufffdone.txt carries index flag S; ...'
detail(bad\x81) = 'RECEIPT-INDEX-FLAG-CONCEALED: amb\ufffdone.txt carries index flag S; ...'
COLLISION: True
```

The writer's `_flag_refusal` decodes with `errors="replace"`, so the record cannot name the path
byte-exactly. (The preregistration's stated limits acknowledge "\r only" escaping and other
control bytes not being escaped.)

**(d) Other control bytes pass through raw.** Probe C2 / P3: the escape covers LF, TAB, CR only.
A path named `esc\x1b[2Jname.txt` puts a **live ESC byte** into the record:

```
raw ESC present in the record: True
K4ROW 'MISMATCH\tK4\t.\tindex-flag-concealed\tRECEIPT-INDEX-FLAG-CONCEALED: esc\x1b[2Jname.txt carries index flag S; ...'
```

One physical line, but the byte is live for whatever renders the record (a terminal interprets
ESC sequences). Low severity, but the escape set is incomplete and the gap is easy to close
(`str.translate` over all C0 bytes).

**(e) The `record` field is not escaped at all.** The `uncommitted-path` class puts the raw
porcelain path in the `record` column. Probe J1 shows git quotes such paths, so every K4 row
keeps exactly 5 tab-separated fields — but the quoted form `"nl\nname.txt"` is a **different
string** from the path, and the record column is not the path the reader must act on. The
`index-flag-concealed` class puts the path in the `detail` column (correctly escaped), while
`uncommitted-path` puts it in `record` (quoted). Two different conventions in one instrument.

---

## 5. Which half is a security boundary, and which is actionability

**Half A (the index-flag sweep) is the security boundary; Half B (the escaping) is
actionability.** But the split is not where the round's framing puts it, and the boundary
Half A claims to draw is drawn in the wrong place.

- **Half A answers "is there uncommitted work in this tree?"** — a security question about the
  audited tree, whose answer determines whether the lane may proceed. Its correctness is a
  *boundary* property: it must not report CLEAN for a tree it did not measure. **It fails that
  property today** (§2, §3.1, §3.2, §3.6, §3.10): under a caller-supplied
  `GIT_CONFIG_PARAMETERS`, or with a writer that declines to refuse, or with a substituted
  `git`, K4 reports CLEAN for a tree whose nested repository commit moved under a skip-worktree
  gitlink — the KG1 class, verbatim. The r86 counter cannot see this because the counter's own
  `ENV` strips `GIT_*`.
- **Half B answers "can a human act on the record?"** — an operability property. It holds for
  the class it targets (a path name cannot forge a second `MISMATCH` row: probe P1) and does not
  hold outside it (§4.2a: the `status-failed` branch still splits a record on a corrupt index,
  pre-existing; §4.2b/c: the escaped form is not injective, so the record may name the wrong
  path).

So: **the repair's security half is the one that is broken, and its operability half is the one
that works.** The round's C2 axis label ("operability 8") describes the *axis*, not the risk
distribution.

A sharper way to put the boundary: **the boundary is not between the tool and the tree, it is
between the tool's own read and the writer's read.** r85's repair already made the tool's status
read and the writer's status read agree (r85 S85Sentinel F1/F6). The r86 repair adds a *third*
read — the flag sweep — that runs under the **writer's** environment, and thereby re-opens the
exact split-brain r85 closed, on the check r86 added. The repair is, in one sentence, a
regression of an r85 fix into the r86 addition.

---

## 6. Does the claim's wording say more than the probes support?

The preregistration's stated wording for C2 says:

> "After its own truth_refusal (which re-hashes status-clean stage-0 regular files and symlinks
> against the index object id) it runs the same index-flag sweep the receipt writer runs before
> a receipt: `git ls-files -v -z :(top)`, and any record whose tag is not `H` is refused through
> the writer's own `_flag_refusal`, reported as `K4 . index-flag-concealed`."

Three words carry more than the probes support:

1. **"the same index-flag sweep the receipt writer runs"** — it is the same *command*, but not
   the same *read*. The writer's sweep runs under the writer's entry-point preconditions
   (`GIT_CONFIG_*`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_COMMON_DIR` all refused before
   any git call: probe I2) and under the writer's own config pins. The K4 sweep runs under
   neither: it calls the writer's `git()` helper directly, past the entry point, in an
   environment where `GIT_CONFIG_PARAMETERS` is honoured. **The sweep the repair runs is not the
   sweep the writer runs.** This is the single sentence in the claim that the probes falsify.

2. **"any record whose tag is not `H`"** — true of the *rendered* tag, and the rendering is
   config-dependent: `core.sparseCheckout=true` renders a skip-worktree entry as `H`. The claim
   reads as a statement about the index; it is a statement about one rendering of the index, in
   one config view, chosen by the caller.

3. **"one K4 record stays one physical line and still names the path"** — the first half holds
   only for the `FORGED` branch (the `status-failed` branch still splits a record on a corrupt
   index, §4.2a), and the second half holds only up to the escape's non-injectivity (§4.2b/c).

Two further points where the *implementation* is narrower than the *intent*:

4. **The class taxonomy is chosen by message prefix, not by which check fired**
   (`msg.startswith(("RECEIPT-GITLINK-CONCEALED", "RECEIPT-INDEX-"))`). Every new r86 failure
   mode therefore lands in the **`stat-cache-concealed`** class, whose name describes a
   *different* mechanism (probe G3):

   ```
   writer has no _flag_refusal   -> class='stat-cache-concealed'  detail='the receipt writer produced no verdict (exit 1: Traceback...)'
   the index-flag read fails      -> class='stat-cache-concealed'  detail='the index-flag read failed (fatal: bad index); tracked bytes are unverified'
   ```

   A reader who sees `stat-cache-concealed` will go looking for a stat-cache forgery that is not
   there, and will not know the flag sweep itself is what broke. The claim's phrase "reported as
   `K4 . index-flag-concealed`" is true only for the one happy path where the writer's own
   message begins with the expected token.

5. **The `REFUSED` branch keeps only the exit code and loses the writer's reason.** The writer
   prints `refused: <reason>` on *its* stderr; the bootstrap catches the `SystemExit` and
   prints `REFUSED <code>` on stdout; the tool's branch keeps only the code (probe N2/D6):

   ```
   MISMATCH	K4	.	stat-cache-concealed	the receipt writer refused the tree (exit 2); tracked bytes are unverified
   ```

   The operator gets "exit 2" and no reason. The `FLAGFAIL` branch has the same shape but keeps
   git's stderr — and that stderr is **not escaped** (probe C4: a multi-line git stderr splits
   the record).

---

## 7. Named list: mechanisms K4 still does not measure, each with why it is out of the claim

1. **`GIT_CONFIG_PARAMETERS` / `GIT_CONFIG_COUNT` reaching the sweep's `git ls-files -v`** —
   **inside the claim**; the claim's "the same index-flag sweep" does not hold. Not covered by
   any stated limit. **This is the finding to route.**
2. **`GIT_INDEX_FILE` reaching both the tool's status read and the sweep** — pre-existing
   (r85 F6), inherited by the r86 sweep; the claim says nothing about it. Named limit? No —
   r85's stated limit was "the flag sweep inherits the writer's classes but K4 does not run the
   writer's filter/attribute witnesses"; `GIT_INDEX_FILE` is not in that list, and the r86
   repair newly routes a check through it.
3. **`GIT_OBJECT_DIRECTORY` / `GIT_ALTERNATE_OBJECT_DIRECTORIES` / `GIT_REPLACE_REF_BASE` /
   `GIT_COMMON_DIR`** — inherited from the writer's helper; all four currently fail closed, but
   the writer's entry point refuses them and the bootstrap does not.
4. **The writer's own environment preconditions** (the r66 `RECEIPT-ENV-*` refusals) — the
   bootstrap bypasses the entry point entirely, so none of them apply to K4.
5. **`core.sparseCheckout` / `index.sparse`** — pinned by neither helper, so the sweep's tag
   rendering is caller-influenced even when the environment is clean. (`core.sparseCheckoutCone`
   alone does not mask; `index.sparse` alone does not either.)
6. **The writer's bytes** (r85 S85Sentinel F5) — inside the preregistration's declared limit
   ("a forged writer inside the audited tree stays outside the claim"). The r86 repair widens
   the writer's authority from one function to three, which the limit does not contemplate.
7. **A substituted `git` on `PATH`** — outside the claim (the tree's own bytes are not the
   audited surface).
8. **The writer's filter/attribute witnesses** (`_witness_refusal`) — explicitly named in the
   preregistration's stated limits as out of the claim ("K4 does not run the writer's
   filter/attribute witnesses"). Confirmed still out: the r86 repair did not add them.
9. **Submodule state** — explicitly named in the stated limits ("the writer still does not read
   submodule state"). Confirmed still out: KG1 proves the flag sweep sees a concealed gitlink
   *commit*, not any submodule state.
10. **The writer's `_witness_refusal` / filter-driver class** — same as 8.

---

## 8. Recommendations, ranked

1. **Route the sweep through the tool's own pinned `git()`**, not the writer's — pass the tag
   to `mod._flag_refusal`. One edit; removes §3.1, §3.2's env half, §3.7 and §3.8 in one
   stroke, and makes the two halves of the measurement agree by construction. (Alternatively
   pin the same six config keys on the sweep's read.)
2. **Restore the writer's env refusals in the tool** (r66 class): `GIT_CONFIG_PARAMETERS`,
   `GIT_CONFIG_COUNT`/`KEY`/`VALUE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`,
   `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_REPLACE_REF_BASE` → refuse, never measure.
3. **Make the sweep's finding independent of the refusal text**: a non-H record must be a
   finding even if `_flag_refusal` returns an empty string.
4. **Give the new failure modes their own classes**: `index-flag-read-failed`,
   `writer-verdict-missing`, `writer-refused` — instead of folding them into
   `stat-cache-concealed`. And keep the writer's refusal *reason*, not just its exit code.
5. **Extend the escape to all C0 bytes and apply it to every detail producer**, not only the
   `FORGED` branch, so "one K4 record is one physical line" is a property of the instrument.
6. **Add one counter arm** with `GIT_CONFIG_PARAMETERS="'core.sparseCheckout=true'"` in the
   child environment. The current counter cannot see §3.1 by construction; this arm would fail
   the filed tool today.

---

## 9. Tooling

No packages were installed, upgraded or removed. The host guard (all `pacman` transactions
paused) was not exercised. Everything ran on the system python3 (`python3 -B`, no bytecode
written) and the system `git` (git version 2.56.0). No tool was added to `~/.local/bin` or any
other PATH directory.

**Lane mutability.** No git/jj mutating command was run in the lane; the only path this seat
wrote inside the lane is `.ufo/waves/round-86/w1/S86Sentinel/` (this report and its
`receipts/`). `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain` now
lists `M LOG.md`, `M SCORECARD.md`, `M corpus/QUALITY.md`, `M corpus/README.md`,
`M corpus/SOURCES.md`, `M corpus/knowledge/filter-filemode-witness.md`,
`M corpus/knowledge/own-tree-pointer-binding.md` plus untracked `census/round-86/records/`,
`census/round-86/srcs/`, `corpus/lessons/round-86.md` and `plans/round-86.md`. **Those tracked
file modifications are not mine** — they are appends made by the integrator (L1 SoujiR86) and
other seats running concurrently in the same lane, with mtimes interleaved with mine
(LOG.md 06:06, SCORECARD.md 05:56, both inside my session window, none of them touched by any
command I issued). I did not write, revert or "clean up" any of them: the lane belongs to the
integrator and reverting another seat's work would be exactly the wrong move.

All fixtures were created under `/fast/scratch/hyaku/souji-r86/S86Sentinel/` with `git init`
inside the fixture directory and `git rev-parse --show-toplevel` asserted equal to the fixture
path before the first commit (the `probe.py` `build_fixture` helper asserts it).

Scratch directory `/fast/scratch/hyaku/souji-r86/S86Sentinel/` was deleted after the receipts
were copied into `.ufo/waves/round-86/w1/S86Sentinel/receipts/`.
