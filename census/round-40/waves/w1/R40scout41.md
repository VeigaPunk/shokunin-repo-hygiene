# R40scout41 — C2 operability attack

Named edge: **same-indent second continuation**. On the committed drift docstring, `RECORD-MALFORMED` is three physical lines. The first continuation (indent 25) carries `schema` and `duplicated`. The second continuation is indented 25 as well, not deeper, and is the only class-entry line that carries `TOTAL`.

Verdict: **measurement gap, with a concrete miss for any joiner that keeps only one continuation.** The r40 predicate is not scored: no r40 counter exists in the tree. Re-running r39 L4 cannot show a join, because `EACCES`, `ELOOP`, `ENOENT`, and `non-regular` already sit on physical line 1 of their class entries. A synthetic probe that puts the token on the *next* physical line is detected by a one-continuation joiner and still leaves `TOTAL` unbound. Unbounded join (from the class header through the end of the docstring) puts `TOTAL` inside `RECORD-MISSING` as well as `RECORD-MALFORMED`. Runtime of a disagreeing TOTAL row is only `RECORD-MALFORMED`.

Axes used: trigger depth, which class entry receives the token, runtime class, probe shape.

## Identity

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Preregistration base: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (ancestor of HEAD)
- HEAD at measurement: `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e` (only `corpus/lessons/round-39-verifier-spotcheck.md` differs; `git diff --stat 02420859..HEAD`)
- Drift blob: `git rev-parse 02420859:tools/souji-worktree-drift.py` = `5a2b32941bc5c3da628ee92f75be1c33192ca311`
- sha256 of that blob = `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76` (same drift half as `census/round-39/records/c2-after.txt` `tool_sha=…/e48ed08e6728`)
- Worktree `tools/souji-worktree-drift.py` and `census/round-39/c2-counter.py` match those blobs (`git status --porcelain` empty for both; `git hash-object` equals the blob id). Analyser under test is the committed function, loaded from the extracted counter, not a rewrite.
- euid 1000. Python 3.14.8. No packages installed.
- `census/round-40/preregistration.txt` C2 names "the frozen list" of class/trigger pairs and does not enumerate it. This seat does not invent that list. Pairs below are the conditions written in the committed docstring, checked against classes this seat raised.

r39 extractor (`census/round-39/c2-counter.py`, lines 133–144): `ast.get_docstring(..., clean=False)`, then the first stripped line that `startswith` `RECORD-MISSING` or `RECORD-MALFORMED`. Continuations are dropped because they do not start with the class token.

## Committed entry

`tools/souji-worktree-drift.py` lines 44–48, blob above. Leading spaces counted by the script: header indent 2, both continuations indent 25.

```
  RECORD-MISSING         EACCES or ELOOP opening the record path: the path
                         exists but cannot be opened or read
  RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line
                         that does not match the schema, a duplicated name, or
                         a TOTAL row that disagrees
```

`docstring_classes` on that blob:

```
r39[RECORD-MISSING]='RECORD-MISSING         EACCES or ELOOP opening the record path: the path'
  word_TOTAL=False word_duplicated=False word_schema=False word_EACCES=True word_ENOENT=False
r39[RECORD-MALFORMED]='RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line'
  word_TOTAL=False word_duplicated=False word_schema=False word_EACCES=False word_ENOENT=True
```

Token owners on the same blob. `r39` = first class line. `join1` = that line plus one following line. `joinall` = lines until the next header whose indent is exactly 2. `rest` = from the header through the end of the docstring. Docstring line numbers are `ast.get_docstring` lines (file line = docstring line + 1). Word match, not substring: `TOTAL` does not match inside another token.

```
TOKEN schema     docstring_lines=[46]  r39=[]  join1=[RECORD-MALFORMED]  joinall=[RECORD-MALFORMED]  rest=[RECORD-MISSING, RECORD-MALFORMED]
TOKEN duplicated docstring_lines=[46]  r39=[]  join1=[RECORD-MALFORMED]  joinall=[RECORD-MALFORMED]  rest=[RECORD-MISSING, RECORD-MALFORMED]
TOKEN TOTAL      docstring_lines=[24, 47]  r39=[]  join1=[]  joinall=[RECORD-MALFORMED]  rest=[RECORD-MISSING, RECORD-MALFORMED]
TOKEN ENOENT     docstring_lines=[45]  r39=[RECORD-MALFORMED]  join1=[RECORD-MALFORMED]  joinall=[RECORD-MALFORMED]  rest=[RECORD-MISSING, RECORD-MALFORMED]
TOKEN EACCES     docstring_lines=[43]  r39=[RECORD-MISSING]  join1=[RECORD-MISSING]  joinall=[RECORD-MISSING]  rest=[RECORD-MISSING]
TOKEN ELOOP      docstring_lines=[43]  same owners as EACCES
TOKEN ENOTDIR    ABSENT from the docstring at every depth
TOKEN ENAMETOOLONG ABSENT from the docstring at every depth
TOKEN EISDIR     ABSENT from the docstring at every depth
```

Docstring line 24 is the format example at file line 25 (`TOTAL<TAB>repos=N…`), before the refusal block. It is not inside any class entry under `joinall`. The class-entry hit is docstring line 47, file line 48, the second continuation.

Within one entry, depth splits the triggers:

| trigger | where | r39 | one continuation | full entry (indent > 2) | runtime class |
|---|---|---|---|---|---|
| `duplicated`, `schema` | first continuation, file line 47, indent 25 | absent | present on `RECORD-MALFORMED` | present on `RECORD-MALFORMED` | `RECORD-MALFORMED` |
| `TOTAL` | second continuation, file line 48, indent 25 (equal to the previous continuation, not deeper) | absent | absent | present only on `RECORD-MALFORMED` | `RECORD-MALFORMED` |
| `EACCES`, `ELOOP` | physical line 1, file line 44 | present | present | present | `RECORD-MISSING` |

`rest` fails the kill text "mapping disagrees with runtime": it reports `TOTAL` inside `RECORD-MISSING`, and a disagreeing TOTAL row does not raise `RECORD-MISSING`.

## Probe shapes

Synthetic modules lived only under scratch. Each is a module docstring passed through the real `docstring_classes`.

**Two-line wrap** (the shape the preregistration's "synthetic wrapped-trigger probe" reads as). `EACCES` only on the next physical line. `TOTAL` and `ENOENT` only on the next physical line of `RECORD-MALFORMED`.

```
r39[RECORD-MISSING] EACCES=False
r39[RECORD-MALFORMED] ENOENT=False TOTAL=False
join1[RECORD-MISSING] EACCES=True
join1[RECORD-MALFORMED] ENOENT=True TOTAL=True
```

r39 misses the token. One continuation finds it. This is the control the preregistration states, and it holds for this shape only.

**Three-line wrap, same continuation indent** (this seat's edge). `EACCES` only on physical line 3 of `RECORD-MISSING`. `TOTAL` and `ENOENT` only on physical line 3 of `RECORD-MALFORMED`.

```
r39[RECORD-MISSING] EACCES=False
r39[RECORD-MALFORMED] ENOENT=False TOTAL=False
join1[RECORD-MISSING] lines=3 EACCES=False
joinall[RECORD-MISSING] lines=3 EACCES=True
join1[RECORD-MALFORMED] lines=3 ENOENT=False TOTAL=False
joinall[RECORD-MALFORMED] lines=3 ENOENT=True TOTAL=True
```

A counter whose only wrap probe is the two-line shape accepts `join1`. `join1` misses this probe and misses file line 48.

**Class-token-leading continuation** (bound on the control sentence, not the named edge). Continuation indent 25, stripped text `RECORD-MALFORMED for the other class. Trigger EACCES`.

```
r39[RECORD-MISSING] EACCES=False text='RECORD-MISSING         opening the record path failed; see'
r39[RECORD-MALFORMED] EACCES=True text='RECORD-MALFORMED for the other class. Trigger EACCES'
indent-stop joinall[RECORD-MISSING] EACCES=True
indent-stop joinall[RECORD-MALFORMED] EACCES=False
startswith-stop: line indent 25 becomes its own RECORD-MALFORMED header, EACCES=True there; the real indent-2 RECORD-MALFORMED line has EACCES=False; RECORD-MISSING has EACCES=False
```

r39 does not drop the token. `startswith` stores it under `RECORD-MALFORMED` because the continuation's stripped text starts with that token. "The r39 one-line analyzer misses it" is false for this shape if "misses" means the token is absent from the map. An indent stop attributes `EACCES` to `RECORD-MISSING`. A startswith stop does not. The candidate check has to name the runtime class's entry, not "token occurs somewhere".

## Runtime

Tool: extracted blob, `python3 -B <scratch>/drift-0242085.py --root <scratch>/probes --record <path> --timeout 10 --skip-unrecorded`. `TMPDIR` was the scratch directory. `--root` was an existing directory so `parse_record` ran before any git read. euid 1000.

```
ENOENT-absent          rc=2 RECORD-MALFORMED  …/absent.tsv is not a regular file
mode-000               rc=2 RECORD-MISSING    [Errno 13] Permission denied
symlink-loop           rc=2 RECORD-MISSING    [Errno 40] Too many levels of symbolic links
directory              rc=2 RECORD-MALFORMED  …/recorddir is not a regular file
fifo                   rc=2 RECORD-MALFORMED  …/fifo.tsv is not a regular file
ENOTDIR                rc=2 RECORD-MISSING    [Errno 20] Not a directory (file used as a parent)
ENAMETOOLONG           rc=2 RECORD-MISSING    [Errno 36] File name too long (one component of 300 x)
TOTAL-repos-disagree   rc=2 RECORD-MALFORMED  TOTAL repos=2 but 1 REPO rows
TOTAL-regs-disagree    rc=2 RECORD-MALFORMED  TOTAL regs=9 but REPO rows sum to 1
duplicate-name         rc=2 RECORD-MALFORMED  line 2 duplicates foo
schema                 rc=2 RECORD-MALFORMED  line 1 does not match the census schema
comment-only-empty     rc=2 RECORD-EMPTY      no REPO rows
```

Record bodies used:

```
REPO	foo	regs=1	prunable=0
TOTAL	repos=2	regs=1	prunable=0
```

```
REPO	foo	regs=1	prunable=0
TOTAL	repos=1	regs=9	prunable=0
```

```
REPO	foo	regs=1	prunable=0
REPO	foo	regs=1	prunable=0
```

`TOTAL` and `duplicated` agree with the docstring once the joiner can see the line that names them. Seeing `duplicated` is not evidence the joiner saw `TOTAL`.

`ENOTDIR` and `ENAMETOOLONG` raise `RECORD-MISSING` and those tokens occur nowhere in the docstring. Joining continuations cannot create them. That omission is the r39 wave finding in `census/round-39/waves/w1/W1RevC2Harm.md` (F2), reproduced here, not this seat's edge. It kills a reading of C2 in which the joined entry must mention every errno the open path raises. It does not, by itself, decide the frozen list, because the preregistration never writes the list down.

## Bounded measurement

Score the r40 analyser only from `git show <rev>:tools/souji-worktree-drift.py` into a scratch directory, `TMPDIR` set to that directory.

1. **P2** — token only on continuation 1. Pass the leg only if the candidate's entry for the runtime class contains the token and r39's first line for that class does not.
2. **P3, this edge** — token only on continuation 2, and continuation 2's indent equals continuation 1's indent (both greater than the header's 2 spaces). Pass only if the candidate entry contains the token. `join1` must fail this and must not be accepted on the strength of P2.
3. **Committed blob** — the joined `RECORD-MALFORMED` entry contains `TOTAL`, `duplicated`, `schema`, `ENOENT`, and `non-regular`. The joined `RECORD-MISSING` entry contains `EACCES` and `ELOOP` and does not contain `TOTAL`. That rejects `rest`.
4. **Runtime on the same blob** — both TOTAL-mismatch records above, the duplicate-name record, and the schema record raise `RECORD-MALFORMED` rc 2. chmod-0 and the symlink loop raise `RECORD-MISSING` rc 2. The class whose joined entry contains `TOTAL` is the class those TOTAL records raise.
5. **Negative control** — a continuation at indent 25 whose stripped text starts with `RECORD-MALFORMED` and contains `EACCES`. Pass only if `EACCES` is attributed to `RECORD-MISSING` (indent stop) and is not stored as the `RECORD-MALFORMED` entry (r39 `startswith`). Do not define "r39 misses the trigger" as "the token is absent from the whole map".

Kill the candidate if P3's token is missing from the runtime class's entry, if `TOTAL` is present on `RECORD-MISSING`, or if the committed file's line 48 is outside the `RECORD-MALFORMED` entry. A receipt that only diffs a two-line probe against r39 does not discharge this.

## Commands

Run from the lane, outputs as quoted above. Scratch was `/fast/scratch/hyaku/souji-r40/R40scout41` and was removed after this report was written.

```
git rev-parse --show-toplevel
git rev-parse HEAD
git rev-parse 0242085909fb6a4ee041c5443d76316ac6d59d4b
git merge-base --is-ancestor 0242085909fb6a4ee041c5443d76316ac6d59d4b HEAD
git status --porcelain -- tools/souji-worktree-drift.py census/round-39/c2-counter.py
git log --oneline 0242085909fb6a4ee041c5443d76316ac6d59d4b..HEAD
git diff --stat 0242085909fb6a4ee041c5443d76316ac6d59d4b..HEAD
git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py
git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:census/round-39/c2-counter.py
sha256sum of both blobs and the worktree files
git rev-parse 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py
git hash-object tools/souji-worktree-drift.py
id -u
python3 --version
TMPDIR=/fast/scratch/hyaku/souji-r40/R40scout41 python3 -B <scratch>/edge_total_line3.py
```

`edge_total_line3.py` loaded `docstring_classes` from the extracted counter via `importlib` and ran the drift blob as a subprocess. No git or jj mutation. No lane file written except this report.

trailer: .ufo/waves/round-40/w1/R40scout41.md
