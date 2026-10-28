# W1ExecC2Docstring — C2 L4 discriminator: drift docstring class map vs behaviour

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Lane HEAD at measurement: `601195a0cebafa74fedb598e3f55da1708ae63f1` (`round-39: C2 — drift docstring
  puts each trigger on its class line (single-line rule)`)
- Base revision under test: `ed30b7f5b77939c9073348d810730bc4f355708d`
- Target file: `tools/souji-worktree-drift.py`
- Worktree file identity: `git diff --stat HEAD -- tools/souji-worktree-drift.py` printed nothing (no
  uncommitted edit); `sha256sum` of the worktree file equals `sha256sum` of the copy taken from it
  (`4e07f1df2a61c2bffdc1108fc97fe86feb6c6cc96bfdfa9c14415736877018be`); `git rev-parse
  HEAD:tools/souji-worktree-drift.py` = `554100b8ff2b98db90408cc40a7fbf236be02bea`.
- Pre-existing unrelated worktree change `M corpus/SOURCES.md` and untracked
  `census/round-39/records/c2-after.txt` / `c3-after.txt` were present before I ran; I touched none of
  them.
- Scratch: `/fast/scratch/hyaku/souji-r39/W1ExecC2Docstring` (created, used, removed at the end — see
  §Scratch).
- Tool installs: none. No mutating git/jj command was run; the only git calls were `show`,
  `rev-parse`, `diff`, `status`, `log`, and `init` inside a `mktemp -d` fixture (toplevel asserted).

## 0. The extraction script (ast only)

`ast.get_docstring(ast.parse(source), clean=False)` preserves the docstring's original two-space
indent, so the raw class lines begin with `"  RECORD-…"`. The script therefore selects on
`line.lstrip().startswith(...)` and prints the **raw** line with `repr()`, so the bytes are quoted
verbatim. This is the same selection the frozen counter makes
(`census/round-39/c2-counter.py:133-146`, `docstring_classes`: `line.strip()`, `clean=False`).

Scratch file `/fast/scratch/hyaku/souji-r39/W1ExecC2Docstring/classmap.py`:

```python
import ast, sys
TOKENS = ("RECORD-MISSING", "RECORD-MALFORMED", "RECORD-EMPTY")
for path in sys.argv[1:]:
    src = open(path, encoding="utf-8").read()
    doc = ast.get_docstring(ast.parse(src), clean=False)
    print("=== %s ===" % path)
    if doc is None:
        print("NO MODULE DOCSTRING"); continue
    for line in doc.splitlines():
        if line.lstrip().startswith(TOKENS):
            print(repr(line))
```

The class map is the **module** docstring (`ast.parse` on the whole file returns a `Module` whose
docstring holds it), so no function-docstring walking is needed.

## 1. Base blob class map — `git show ed30b7f...:tools/souji-worktree-drift.py`

Command (base blob extracted to scratch first, so the worktree is never read):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
git show ed30b7f5b77939c9073348d810730bc4f355708d:tools/souji-worktree-drift.py \
  > /fast/scratch/hyaku/souji-r39/W1ExecC2Docstring/base-drift.py
python3 -B /fast/scratch/hyaku/souji-r39/W1ExecC2Docstring/classmap.py \
  /fast/scratch/hyaku/souji-r39/W1ExecC2Docstring/base-drift.py
```

Observed output:

```
=== /fast/scratch/hyaku/souji-r39/W1ExecC2Docstring/base-drift.py ===
'  RECORD-MISSING         the record path cannot be read'
'  RECORD-MALFORMED       a line does not match the schema, duplicates a name,'
'  RECORD-EMPTY           no REPO rows'
```

Verbatim source block (`git show ed30b7f...:tools/souji-worktree-drift.py | sed -n '43,49p'`):

```
  RECORD-MISSING         the record path cannot be read
  RECORD-MALFORMED       a line does not match the schema, duplicates a name,
                         or disagrees with the TOTAL row
  RECORD-EMPTY           no REPO rows
  RECORD-OUTSIDE-ROOT    a record row, or the gitdir it resolves to, escapes
                         --root
```

**Verdict: CONFIRMED GAP (base).** The base `RECORD-MALFORMED` entry enumerates only schema /
duplicate-name / TOTAL conditions — it says nothing about a record *path* at all, and does not
contain the word "missing". The base `RECORD-MISSING` entry is the generic "the record path cannot
be read" and names no `EACCES`.

## 2. Current worktree file class map

Command:

```
python3 -B /fast/scratch/hyaku/souji-r39/W1ExecC2Docstring/classmap.py \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py
```

Observed output:

```
=== /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py ===
'  RECORD-MISSING         EACCES, ELOOP or EISDIR opening the record path: the'
'  RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line'
'  RECORD-EMPTY           no REPO rows'
```

Verbatim source block (`sed -n '43,48p' tools/souji-worktree-drift.py`):

```

  RECORD-MISSING         EACCES, ELOOP or EISDIR opening the record path: the
                         path exists but cannot be opened or read
  RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line
                         that does not match the schema, a duplicated name, or
                         a TOTAL row that disagrees
```

**Verdict: CONFIRMED FIX (head), with one residual over-claim (§5).** The `RECORD-MALFORMED` line
names "missing (ENOENT)" and "non-regular"; the `RECORD-MISSING` line names "EACCES".

## 3. Behaviour — which class is actually raised

Fixture (every git call carries `-C "$D"`, toplevel asserted):

```
S=/fast/scratch/hyaku/souji-r39/W1ExecC2Docstring
D=$(mktemp -d "$S/probe.XXXXXX"); git -C "$D" init -q
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || exit 1
printf '# only a comment\n' > "$D/locked.tsv"; chmod 000 "$D/locked.tsv"
mkdir -p "$D/recorddir"
python3 -B "$S/base-drift.py" --root "$D" --record "$D/absent.tsv"   # missing
python3 -B "$S/base-drift.py" --root "$D" --record "$D/locked.tsv"   # EACCES
python3 -B "$S/head-drift.py" --root "$D" --record "$D/absent.tsv"
python3 -B "$S/head-drift.py" --root "$D" --record "$D/locked.tsv"
```

Observed (last stdout/stderr line, `rc` from `$?`):

```
=== base-drift.py ===
[missing] rc=2 :: REFUSAL RECORD-MALFORMED: /fast/scratch/.../probe.hKetPw/absent.tsv is not a regular file
[locked]  rc=2 :: REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '/fast/scratch/.../probe.hKetPw/locked.tsv'
[directory] rc=2 :: REFUSAL RECORD-MALFORMED: /fast/scratch/.../probe.hKetPw/recorddir is not a regular file
=== head-drift.py ===
[missing] rc=2 :: REFUSAL RECORD-MALFORMED: /fast/scratch/.../probe.hKetPw/absent.tsv is not a regular file
[locked]  rc=2 :: REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '/fast/scratch/.../probe.hKetPw/locked.tsv'
[directory] rc=2 :: REFUSAL RECORD-MALFORMED: /fast/scratch/.../probe.hKetPw/recorddir is not a regular file
```

Additional trigger probes (`probe2.IZlK59`: `ln -s loop.tsv loop.tsv`, `mkfifo fifo.tsv`,
`chmod 000 sealed/` with a readable file inside):

```
=== base-drift.py ===
[eloop]      rc=2 :: REFUSAL RECORD-MISSING: [Errno 40] Too many levels of symbolic links: '.../loop.tsv'
[fifo]       rc=2 :: REFUSAL RECORD-MALFORMED: .../fifo.tsv is not a regular file
[sealed-dir] rc=2 :: REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '.../sealed/r.tsv'
=== head-drift.py ===
[eloop]      rc=2 :: REFUSAL RECORD-MISSING: [Errno 40] Too many levels of symbolic links: '.../loop.tsv'
[fifo]       rc=2 :: REFUSAL RECORD-MALFORMED: .../fifo.tsv is not a regular file
[sealed-dir] rc=2 :: REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '.../sealed/r.tsv'
```

**Verdict: CONFIRMED, base and head behave identically.** Behaviour is unchanged by the C2 landing;
only the docstring moved. The only `open` of the record path is
`tools/souji-worktree-drift.py:132` (`os.open(path, os.O_RDONLY | os.O_NONBLOCK)`); `ENOENT`
maps to `RECORD-MALFORMED` (line 133), every other `OSError` (EACCES, ELOOP, EISDIR) to
`RECORD-MISSING` (line 134), and a non-regular descriptor (FIFO, directory) to `RECORD-MALFORMED`.

## 4. The L4 discriminator, per revision

| revision | class raised for a **missing** path | that class's docstring line | contains "missing"? | class raised on **EACCES** | that class's docstring line | names "EACCES"? |
|---|---|---|---|---|---|---|
| base `ed30b7f` | `RECORD-MALFORMED` | `RECORD-MALFORMED  a line does not match the schema, duplicates a name,` | **NO** | `RECORD-MISSING` | `RECORD-MISSING  the record path cannot be read` | **NO** |
| head `601195a` | `RECORD-MALFORMED` | `RECORD-MALFORMED  a missing (ENOENT) or non-regular record path, a line` | **YES** | `RECORD-MISSING` | `RECORD-MISSING  EACCES, ELOOP or EISDIR opening the record path: the` | **YES** |

Direct replication of the frozen predicate (`c2-counter.py:224-234`) using the counter's own
helpers (`docstring_classes`, `classify`) on the two revisions, with the probe file chmod-0 **while
the child ran** (a first attempt restored the mode too early and read `RECORD-EMPTY`; that defective
run was discarded, not reported as evidence):

```
base: missing=RECORD-MALFORMED locked=RECORD-MISSING L4_ok=False
   line[RECORD-MALFORMED] = 'RECORD-MALFORMED       a line does not match the schema, duplicates a name,'
   line[RECORD-MISSING] = 'RECORD-MISSING         the record path cannot be read'
head: missing=RECORD-MALFORMED locked=RECORD-MISSING L4_ok=True
   line[RECORD-MALFORMED] = 'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line'
   line[RECORD-MISSING] = 'RECORD-MISSING         EACCES, ELOOP or EISDIR opening the record path: the'
```

**Verdict: PASS for C2 L4.** `new_ok and not old_ok` holds exactly as the counter requires
(`new_maps=True old_maps=False`); the base gap is precisely the one the preregistration names (§C2
(b), R10). The preregistered discriminator is not falsified.

## 5. Residual defect found (advisory — outside the frozen L4 predicate, does not falsify it)

The head `RECORD-MISSING` line advertises **`EISDIR`** as one of its triggers ("EACCES, ELOOP or
EISDIR opening the record path"). A directory passed as `--record` does **not** raise `EISDIR` on
this code: the single open is `O_RDONLY | O_NONBLOCK`, which succeeds on a directory on Linux, and
the `fstat` guard then refuses it as non-regular. Observed identically on both revisions:

```
[directory] rc=2 :: REFUSAL RECORD-MALFORMED: .../recorddir is not a regular file
```

`EISDIR` is only raised by a write-mode open, which this tool never issues, so the word is
unreachable in this code path. `ELOOP` (observed `RECORD-MISSING`) and the EACCES/EACCES-on-a-parent-
directory cases are accurate; `non-regular` covering directories and FIFOs is accurate.

**Verdict: RESIDUAL OPERABILITY DEFECT (doc-only, one word).** The head docstring still misdescribes
one trigger of the same class pair the round exists to reconcile — the R10 defect class, narrowed.
Cheapest correction: drop `EISDIR` from the `RECORD-MISSING` line, or move it to the
`RECORD-MALFORMED` "non-regular record path" clause. No frozen predicate tests `EISDIR`, so this does
not change any counter reading; the L1 decides whether to land it in this round. I did not edit the
file: my assignment is the measurement, and lane bytes belong to the L1.

## 6. Verdicts summary

1. Base class map extracted with `ast` only — **executed**, gap reproduced: `RECORD-MALFORMED` line
   lacks "missing", `RECORD-MISSING` line lacks "EACCES".
2. Head class map extracted with `ast` only — **executed**, both trigger names present on the class
   lines the tool actually raises (`missing (ENOENT)` on `RECORD-MALFORMED`; `EACCES` on
   `RECORD-MISSING`).
3. Behaviour identical on base and head bytes (`RECORD-MALFORMED` for missing, `RECORD-MISSING` for
   EACCES/ELOOP/EACCES-through-parent, `RECORD-MALFORMED` for FIFO and directory) — **executed**;
   the C2 landing changed documentation only, so L4 is a doc-arm leg with no behaviour harm.
4. Frozen L4 predicate replicated with the counter's own helpers: `base L4_ok=False`,
   `head L4_ok=True` → **C2 L4 passes; contract not falsified.**
5. One residual doc over-claim (`EISDIR`) reported for the L1's disposition — no counter leg reads it.

## Scratch

`/fast/scratch/hyaku/souji-r39/W1ExecC2Docstring` (with `probe.hKetPw`, `probe2.IZlK59`,
`c2import.*`, `base-drift.py`, `head-drift.py`, `classmap.py`) was removed with `rm -rf` after
measurement; nothing of mine remains on disk. No file inside the lane was written except this report.
