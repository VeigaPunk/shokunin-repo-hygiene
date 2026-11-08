# S86ExecK4 — C2 re-derivation and K4 break probes (round 86)

Seat: S86ExecK4 (executor, leaf). Owner of this file and `.ufo/waves/round-86/w1/S86ExecK4/` only.
Nothing here is committed, pushed, or judging; the L1 (SoujiR86) integrates.

Lane base: `2acbbfc80ac91e1b65cf5dae7287209fed9c7c86` (HEAD of the lane at probe time; `git log` showed
`2acbbfc8 round-86: C2 repair …` on top of `d77b4258` and `47602fa6`).
Frozen bytes verified by sha256 before any probe:

| file | sha256 |
|---|---|
| `tools/souji-record-agreement.py` | `4cc3b9450dc058e4c05a312b0918a5099b5e3fdbe3c62c779d781462068468df` |
| `tools/souji-receipt-write.py` | `70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa` |
| `census/round-86/c2-k4-counter.py` | `6438c0141ac818025dbd1bed5070befee2d731b7a0884609f54abb479fab6827` |
| `census/round-86/controls/c2-before-base-tool.py` | `0ade075152b0625cc0e9d77a2d4462951127e2f480f850c973451086a3958fb7` |
| `census/round-86/controls/souji-receipt-write.py` | `70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa` (identical to the writer) |

Environment: Python 3.14.8, git 2.56.0, `LC_ALL=C`, `GIT_CONFIG_NOSYSTEM=1`,
`GIT_CONFIG_GLOBAL=/dev/null`, fixed author/committer dates. Fixtures under
`/fast/scratch/hyaku/souji-r86/S86ExecK4/` (deleted before yield). No tool installs were needed
(stdlib only); nothing was installed or upgraded.

Verdict in one line: **both arms reproduce the prereg's numbers exactly, and no break probe escapes
the repair except a fully forged writer, which the prereg's stated limit already excludes.**

---

## 1. The two arms, re-derived

Command (after), run from the lane root:

```
python3 -B census/round-86/c2-k4-counter.py --tool tools/souji-record-agreement.py \
        --work /fast/scratch/hyaku/souji-r86/S86ExecK4/wA
```

Output (verbatim; receipt `c2-arms.txt`):

```
# tool path=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py sha256=4cc3b9450dc058e4c05a312b0918a5099b5e3fdbe3c62c779d781462068468df
# writer path=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-receipt-write.py sha256=70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa
# counter sha256=6438c0141ac818025dbd1bed5070befee2d731b7a0884609f54abb479fab6827
# fixture clone=/fast/scratch/hyaku/souji-r86/S86ExecK4/wA/clone rev=e295278b97d7513900e2f9a0e48bffad602a7479
ROW KH1 expect=clean k4=0 named=- rc=1 match=yes
ROW KH2 expect=clean k4=0 named=- rc=1 match=yes
ROW KU1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['a.txt|uncommitted-path']
ROW KU2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['untracked-scratch.txt|uncommitted-path']
ROW KF1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KF2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KF3 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KG1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|index-flag-concealed']
ROW KG2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
SUMMARY rows=9 mismatches=0 errors=0
EXIT=0
```

Command (before): the same counter on `census/round-86/controls/c2-before-base-tool.py`. Output:

```
# tool path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-86/controls/c2-before-base-tool.py sha256=0ade075152b0625cc0e9d77a2d4462951127e2f480f850c973451086a3958fb7
# writer path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-86/controls/souji-receipt-write.py sha256=70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa
# counter sha256=6438c0141ac818025dbd1bed5070befee2d731b7a0884609f54abb479fab6827
ROW KH1 expect=clean k4=0 named=- rc=1 match=yes
ROW KH2 expect=clean k4=0 named=- rc=1 match=yes
ROW KU1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['a.txt|uncommitted-path']
ROW KU2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['untracked-scratch.txt|uncommitted-path']
ROW KF1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KF2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KF3 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KG1 expect=flag k4=0 named=no rc=1 match=no detail=''
ROW KG2 expect=flag k4=1 named=no rc=1 match=no k4rows=['.|stat-cache-concealed'] detail=''
SUMMARY rows=9 mismatches=2 errors=0
EXIT=1
```

Verdict: **both ends reproduce the frozen wording.** After arm `rows=9 mismatches=0 errors=0`, EXIT 0,
KG1 and KG2 both `named=yes`; before arm `mismatches=2 errors=0`, EXIT 1, with KG1 `k4=0` and KG2
`named=no`; the seven r85 rows are identical in both arms. The delta is exactly the two rows the
repair answers.

---

## 2. Break probes — the six required shapes

Driver: `probe-k4.py` (this seat dir; sha256 `715b42463fa73358e50f687c290420c1a358f82a8a5d6f8c5b108c34d1b57e04`).
Each probe builds a fresh fixture (`git init`, toplevel asserted equal to the fixture dir before the
first commit), applies one state, runs `python3 -B <tool> --root <fixture> --rev <full40>`, and prints
the K4 rows. Full verbatim output: `c2-k4-break-probes.txt`.

### (a) Copy of the tool with NO writer beside it — **protected (fails closed)**

```
copied tool dir: …/probes/a-tool-lone (contents=['souji-record-agreement.py'])
-- on an honest clean tree --
rc: 1
k4_rows(1): [[".", "stat-cache-concealed", "the receipt writer is not beside this tool
  (…/probes/a-tool-lone/souji-receipt-write.py); tracked bytes are unverified"]]
-- on a concealed tree (skip-worktree gitlink moved) --
rc: 1
k4_rows(1): [[".", "stat-cache-concealed", "the receipt writer is not beside this tool (…); tracked bytes are unverified"]]
```

Constrains: stated limit *“a copy of the tool without a writer beside it fails closed rather than
measuring.”* Measured true, in both directions: no clean verdict on an honest tree and no clean
verdict on a concealed one. The cost is a K4 row on an honest tree, which is what “fails closed”
means here.

### (b) Copy with a LYING writer (returns None, defines no `_flag_refusal`) — **protected (fails closed)**

Stub beside the copied tool: `_truth_refusal(top) -> None`, a working `git()`, **no** `_flag_refusal`.

```
tool dir: …/probes/b-tool (contents=['souji-receipt-write.py', 'souji-record-agreement.py'])
-- on a concealed tree (skip-worktree gitlink moved) --
rc: 1
k4_rows(1): [[".", "stat-cache-concealed", "the receipt writer produced no verdict (exit 1: Traceback (most recent call last):"]]
-- control: same lying writer on an honest clean tree --
rc: 1
k4_rows(0): []
```

Constrains: the same limit sentence. The missing `_flag_refusal` raises `AttributeError` inside the
embedded sweep, which has no handler, so the writer subprocess exits nonzero with empty stdout and the
parent takes the no-verdict branch. Verdict is a K4 row, never a clean one: closed.

**Diagnostic defect (routed, low):** the message truncates the writer's stderr to 200 characters, so
the operator sees `Traceback (most recent call last):` and never learns *which* attribute is missing.
The failure is safe but the message does not name the cause. Suggested narrowing (not this round's
claim): keep the first traceback line *and* the final exception line, or cap at the last 200 chars.

### (c) Writer's flag read fails (corrupt index) — **protected (fails closed, by a different branch)**

```
index truncated 757 -> 20 bytes
git status --porcelain rc: 128
git ls-files -v -z rc: 128
rc: 1
k4_rows(1): [[".", "status-failed", "fatal: .git/index: index file smaller than expected"]]
```

Constrains: *“it runs the same index-flag sweep … `git ls-files -v -z :(top)`”* under a broken index.
The sweep never runs, because K4's own `git status --porcelain` (line 427) reads the same corrupt index
and fails first; the writer's `FLAGFAIL` branch ("the index-flag read failed") is **unreachable in this
shape**. That is still closed — the tree is refused — but nobody should expect the corrupt-index signal
to appear as `index-flag-concealed`. Not an escape; a wording/branch observation.

### (d) Honest tree with a stale mtime — **protected (no row)**

```
a.txt mtime moved back 3600s (…), bytes unchanged
git status --porcelain: ""
rc: 1
k4_rows(0): []
```

Constrains: the repair must not over-refuse. A stale stat cache over identical bytes must stay clean —
the same shape as the frozen KH2 row, one hour deeper. It does.

### (e) `--assume-unchanged` regular file, bytes changed, forged stat — **protected (refused; class differs)**

```
update-index --assume-unchanged a.txt rc: 0
git status --porcelain: ""                 (the flag hides the change)
ls-files -v a.txt: "h a.txt\n"
rc: 1
k4_rows(1): [[".", "stat-cache-concealed", "RECEIPT-WORKTREE-STAT-CONCEALED: 1 tracked path(s) git status
  reports clean do not hash to the object id the index records (a.txt); the index stat cache conceals a
  worktree change; no receipt written"]]
```

Constrains: *“any record whose tag is not `H` is refused through the writer's own `_flag_refusal`,
reported as `K4 . index-flag-concealed`.”* For an `h`-tagged regular file whose **bytes differ**, the
truth check refuses it first and the row is classed `stat-cache-concealed`, not `index-flag-concealed`.
The record *is* refused, so the sentence's operative content holds (“not H ⇒ refused”) but its class
name is accurate only for records that survive the byte-truth check (e.g. a gitlink, or a flagged file
whose bytes still match). The claim should say “refused through `_truth_refusal` or `_flag_refusal`,
whichever fires first”, or name both classes. Refinement, not an escape.

### (f) Stage-2 conflict whose worktree bytes match stage 0 — **protected (two rows)**

Fixture: base `conflict.txt = "base\n"`; side = `"side\n"`; master = `"master\n"`; merge conflicts;
then the worktree file is rewritten to `"base\n"` — exactly the pre-merge blob (stage 1; there is no
stage 0 for an unmerged path).

```
ls-files -s conflict.txt: stages 1,2,3
ls-files -v conflict.txt: "M conflict.txt" ×3
git status --porcelain: "UU conflict.txt\n"
rc: 1
k4_rows(2): [["conflict.txt", "uncommitted-path", "UU"],
             [".", "index-flag-concealed", "RECEIPT-INDEX-UNMERGED: conflict.txt is unmerged (index stages 1 2 3)
              and carries index flag M; a conflicted path is not a clean tree; resolve it with git add or git rm, then retry"]]
```

Constrains: the index-flag sweep on `M` records. Caught twice — status names it, and the sweep maps the
`M` tag through `_flag_refusal` to `RECEIPT-INDEX-UNMERGED`, which K4 classifies as
`index-flag-concealed`. Restoring the pre-merge bytes buys nothing: the unmerged index entry is the
evidence. Protected.

---

## 3. Extra probes (frontier attempts, all measured)

### (b2) Fully lying writer (defines `_flag_refusal -> None`) — **escapes, inside the named limit**

```
rc: 1
k4_rows(0): []        ← concealed skip-worktree gitlink moved, and K4 reports nothing
```

This is the only shape that escapes: a writer stubbed to return `None` from both hooks, beside the
tool, on a tree whose gitlink commit moved under `skip-worktree`, yields **no** K4 row. It is exactly
`census/round-86/preregistration.txt:100-101`: *“a forged writer inside the audited tree stays outside
the claim (S85Sentinel F5)”* — the writer K4 loads is `tools/souji-receipt-write.py`, i.e. inside the
audited tree. So the repair's whole K4 guarantee is delegated to that file; the delegation is stated,
and I am not calling this a defect. It is worth recording that the limit is **load-bearing**: if it is
ever retired, K4 would need the writer pinned (e.g. a frozen sha256 beside the tool) before any
“concealed ⇒ refused” sentence can be read as unconditional.

### (g) + (q) Newline path listed by status, `core.quotePath=false` — **protected (git quotes, not the tool)**

```
default:   git status --porcelain: " M \"bad\\nname.txt\"\n"
-c core.quotePath=true :  " M \"bad\\nname.txt\"\n"
-c core.quotePath=false:  " M \"bad\\nname.txt\"\n"
-c core.quotePath=false -z: " M bad\nname.txt\0"
rc: 1
k4_rows(1): [["\"bad\\nname.txt\"", "uncommitted-path", "M"]]
```

Both arms (repo default, and repo-local `core.quotePath=false`) give one record, one physical line,
path recoverable in C-quoted form. Constrains: *“A path that carries a newline or a tab is C-escaped in
the record instead of being space-joined, so one K4 record stays one physical line and still names the
path.”* In the `uncommitted-path` arm the escaping is done by git's porcelain v1 format, not by the
tool: porcelain v1 C-quotes newline/tab paths **regardless** of `core.quotePath` (measured with `-c`
on both values; `-z` is what would emit raw bytes, and K4 does not use `-z` there). So the sentence
holds on every measured shape, but its mechanism differs per arm — the tool's own escape
(`souji-record-agreement.py:226`) covers only the truth/flag detail, while the status arm inherits
git's quoting. A future switch to `status --porcelain -z` in that loop would lose the quoting and the
sentence would go false.

### (t) Tab-in-name path concealed by a forged stat — **protected (tool's escape does the work)**

```
config core.quotePath = ""            (unset)
git status --porcelain: ""            (hidden by the forged stat)
ls-files -v: H "tab\tname.txt"        (quoted for display; the sweep uses -z, raw bytes)
rc: 1
k4_rows(1): [[".", "stat-cache-concealed", "… index records (tab\\tname.txt); …"]]
```

Byte check of the record: `od -c` shows `t a b \ t n a m e . t x t`, i.e. a literal backslash + `t`;
the line splits into exactly **5** tab-separated fields and is **one** physical line. The newline arm
(KG2 replica, same driver) is identical: `repr` of the detail contains `bad\\nname.txt` and the record
bytes are `b'MISMATCH\tK4\t.\tstat-cache-concealed\tRECEIPT-WORKTREE-STAT-CONCEALED: … (bad\\nname.txt); …'`
— 5 fields, one line. Constrains: the same sentence, tab arm. Holds.

### (m) `skip-worktree` on an UNCHANGED file — **protected (refused; over-refusal by design)**

```
bytes unchanged; git status --porcelain: ""
ls-files -v a.txt: "S a.txt\n"
k4_rows(1): [[".", "index-flag-concealed", "RECEIPT-INDEX-FLAG-CONCEALED: a.txt carries index flag S; …"]]
```

An honest-bytes record carrying a flag is refused. This is the writer's inherited rule (`the flag
sweep inherits the writer's classes`), and the writer refuses the same tree before writing a receipt,
so K4 is consistent with the lane's rule. It is not a KH1/KH2 violation — those rows have no flags.
Recorded so nobody reads “honest tree” as “any tree whose bytes match”.

### (s) Repo-local `status.showUntrackedFiles=no` + an untracked file — **protected (pinned)**

```
default:                                       "?? untracked-scratch.txt\n"
after repo-local status.showUntrackedFiles=no: ""
with the writer's pin:                         "?? untracked-scratch.txt\n"
k4_rows(1): [["untracked-scratch.txt", "uncommitted-path", "??"]]
```

K4 still reports the untracked path because `souji-record-agreement.py`'s `git()` (`:112-127`; pins at `:114-119`) pins
`status.showUntrackedFiles=all` (and `core.fsmonitor=false`, `core.fileMode=true`,
`core.checkStat=default`, `core.trustctime=true`, `core.excludesFile=/dev/null`) through
`GIT_CONFIG_COUNT`, which also strips caller-injected `GIT_CONFIG_*`. Repo-local config loses.

### (k) KG1 shape with `--assume-unchanged` instead of `--skip-worktree` — **protected**

```
update-index --assume-unchanged nest rc: 0
ls-files -v nest: "h nest\n"
k4_rows(1): [[".", "index-flag-concealed", "RECEIPT-GITLINK-CONCEALED: nest is a gitlink (mode 160000)
  carrying index flag h; …"]]
```

Both flag letters are swept; the gitlink class names the mode, not the letter. Good.

### (j) Symlinked tool beside a lying writer — **protected (realpath)**

```
tool invoked through j-link/souji-record-agreement.py (a symlink into j-real/);
lying writer placed only in j-link/; real writer beside the real tool.
k4_rows(1): [[".", "index-flag-concealed", "RECEIPT-GITLINK-CONCEALED: nest is a gitlink … flag S …"]]
```

The r85 `realpath` resolution holds: the link's neighbour is ignored, the real writer is loaded.

### (h) Gitlink moved, `submodule.<name>.ignore=all`, no index flag — **protected**

```
status --porcelain with ignore=all: " M nest\n"     (not hidden: no .gitmodules entry to bind it)
ls-files -v nest: "H nest\n"
k4_rows(1): [["nest", "uncommitted-path", "M"]]
```

The ignore config does not bind without a `.gitmodules` entry, so status still names the gitlink and
K4 reports it. This narrows the reach of the stated limit *“the writer still does not read submodule
state”*: the escape requires an index flag (which the sweep catches) — a bare dirty gitlink is caught
by status. The limit is accurate but not cheaply reachable.

---

## 4. Real-lane clause (kill rule, last item)

`git clone --shared` of the lane into scratch, then the filed tool against the clone at the frozen
revision (read-only; the clone's toplevel asserted as itself):

```
$ python3 -B tools/souji-record-agreement.py --root cleanclone --rev 2acbbfc80ac91e1b65cf5dae7287209fed9c7c86
MISMATCH	K3	corpus/README.md:1017	tally-disagree	3 refused != receipt 0 refused
keys=4 records=4 occurrences=18 mismatches=1
EXIT=1
```

**No K4 row** on the lane's own clean tree — the kill-rule clause is satisfied.

The single `K3` row is **pre-existing and orthogonal**, and I confirmed it is not the repair's: the
base tool `census/round-86/controls/c2-before-base-tool.py` produces the byte-identical row on the same
clone (`keys=4 records=4 occurrences=18 mismatches=1`). Cause: `corpus/README.md:1017` is r73 prose —
“rows FX1-FX3 refused, honest FXh/FXc accepted” — and `TALLY_RE` (`(\d+)\s+\*{0,2}(accepted|present|unverifiable|refused)\*{0,2}`)
reads the `3` of `FX1-FX3` plus `refused` as a tally of 3 refused, while
`census/round-22/attempt2/slice-verdicts.tsv` contains no `refused` line (tally 0). Routed as an
observation for the L1: the lane's record-agreement instrument is **non-green on its own tree at the
frozen rev for K3 reasons**, which any round summary that says “record-agreement green” must
reconcile. It is outside C2's wording (C2 is about K4 and record paths) and unchanged by the repair.

---

## 5. Claim assessment

| probe | shape | verdict |
|---|---|---|
| (a) | tool with no writer | protected (fails closed) |
| (b) | lying writer, no `_flag_refusal` | protected (fails closed) |
| (c) | corrupt index | protected (fails closed, `status-failed`) |
| (d) | honest stale mtime | protected (no row) |
| (e) | assume-unchanged + changed bytes | protected (refused as `stat-cache-concealed`) |
| (f) | stage-2 conflict, bytes = base | protected (2 rows) |
| (b2) | **fully lying writer** | **escapes — within the stated limit (prereg:99-101)** |
| (g)/(q) | newline path, quotePath=false | protected (git quoting) |
| (t) | tab path, forged stat | protected (tool escape; 5 fields, 1 line) |
| (m) | skip-worktree, bytes unchanged | protected (refused) |
| (s) | showUntrackedFiles=no | protected (pinned) |
| (k) | assume-unchanged gitlink | protected |
| (j) | symlinked tool + lying neighbour | protected |
| (h) | submodule ignore=all | protected |

C2's wording holds on every measured shape. No escape exists outside the filed stated limits. Three
items for the L1 to fold into plans/round-86.md (the prereg itself is frozen and must not be edited):

1. **(e)** `any record whose tag is not H … reported as K4 . index-flag-concealed` — true only when the
   byte-truth check passes first; an `h`/`S` regular file with different bytes is refused as
   `stat-cache-concealed`. Narrow the sentence to “refused through `_truth_refusal` or `_flag_refusal`”.
2. **(c)** the writer's `FLAGFAIL` branch is not the corrupt-index signal; K4's own status read fails
   first and reports `status-failed`. Do not cite `index-flag-concealed` as the corrupt-index row.
3. **(g)/(t)** the record sentence holds for two different reasons: the tool's C-escape covers the
   truth/flag detail, while the status arm relies on porcelain v1 quoting (which `core.quotePath`
   does not change). Switching that loop to `-z` would falsify it.

Routed non-claim defects/observations:
- `souji-record-agreement.py:229-230` truncates the writer's stderr to 200 chars; the (b) failure
  hides `AttributeError: … _flag_refusal`.
- K3 prose-misparse row on the lane's own tree at the frozen rev (identical in both arms).

---

## 6. Evidence and hygiene

| artifact | sha256 |
|---|---|
| `.ufo/waves/round-86/w1/S86ExecK4/c2-arms.txt` (both arms verbatim) | `25b91e6dd9aa2561a194ddf87edaa672223b92d1f72d2107ba3bca04fa393780` |
| `.ufo/waves/round-86/w1/S86ExecK4/c2-k4-break-probes.txt` (all 15 probe sections) | `bdccfaf105f3f80e854cb6e8c7d7a326aa542c3a3caf1ab8da9fc58859b7f175` |
| `.ufo/waves/round-86/w1/S86ExecK4/probe-k4.py` (driver) | `715b42463fa73358e50f687c290420c1a358f82a8a5d6f8c5b108c34d1b57e04` |

Scratch `/fast/scratch/hyaku/souji-r86/S86ExecK4/` (fixtures, clones, counter `--work` dirs) was
deleted after these receipts were copied out. No lane file was mutated by this seat: the only lane git
calls were read-only (`log`, `status`, `sha256sum`); the clone lived in scratch and was deleted with it.
No commit, push, jj write, no `agent://all`, no subagent dispatched, no pacman, no installs.

Working-tree state at yield time, for the L1 (not this seat's writes, not reverted):
`M corpus/SOURCES.md`, `M corpus/knowledge/filter-filemode-witness.md`, `?? census/round-86/records/`,
`?? census/round-86/srcs/`. At probe start the tree showed only `?? census/round-86/records/`; the two
tracked modifications appeared during the wave and are sibling-seat work. They are why a later
real-lane K4 run will legitimately report those paths unless the wave's own edits are intended and
committed by the L1.

Risks: (i) probe fixtures are synthetic and hermetic, like the frozen counter's; (ii) the (h)/(b2)
results are single-tree measurements on git 2.56.0 only; (iii) `git clone --shared` created an
alternates link into the deleted scratch — informational only, the lane's objects were only read.
