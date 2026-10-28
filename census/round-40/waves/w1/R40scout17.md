# R40scout17 — C2 operability attack: TOTAL-ON-SECOND-CONTINUATION

- Seat: R40scout17 (scout, item 17). Axis: operability. Read-only on lane bytes.
- Named edge: `TOTAL-ON-SECOND-CONTINUATION` on the committed `RECORD-MALFORMED` docstring entry. The trigger word `TOTAL` is not on the class line and not on the first wrapped line. It is on the second continuation (third physical line of the entry). The same entry's first continuation carries `schema` and `duplicated`, which the r39 one-line map also drops.
- Frozen claim attacked: `census/round-40/preregistration.txt` C2. Predicate requires an r40 L4 analyser that joins wrapped continuation lines into one class entry, verifies every observed class/trigger pair in "the frozen list", and detects a synthetic wrapped-trigger probe that r39 `docstring_classes` misses. Kill if a wrapped trigger is missed, or if any observed class mapping disagrees with runtime.
- No production file written. No frozen claim edited. No tool installed.

## Verdict

**FALSIFIER for a one-line join and for a word-boundary check of the wave token `duplicate`. Not a falsifier of join-until-the-next-class-token plus a stem match.**

Measured on the committed r39 blob `0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py` (`5a2b32941bc5c3da628ee92f75be1c33192ca311`, sha256 `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76`, the same second component as `census/round-39/records/c2-after.txt` `tool_sha=…/e48ed08e6728`):

1. r39 `docstring_classes` (imported from `0242085:census/round-39/c2-counter.py`) stores only the first line of `RECORD-MALFORMED`. That line has no `TOTAL`, no `schema`, and no `duplicat`. Control holds: the one-line analyser misses these wrapped triggers.
2. A joiner that appends only the next physical line still misses `TOTAL`. It does see `schema` and `duplicated`. The obvious synthetic (trigger on the first continuation only) passes this joiner and fails r39, so that synthetic does not force the joiner to be deep enough for the committed entry.
3. A joiner that appends every following non-empty line until the next line whose `strip()` starts with a class token sees `TOTAL`, `schema`, and `duplicated` on `RECORD-MALFORMED`.
4. Runtime of that same blob agrees: a duplicated name, a non-schema line, and a disagreeing TOTAL row each exit 2 with `REFUSAL RECORD-MALFORMED`. A TOTAL row that matches the REPO rows does not raise `RECORD-MALFORMED`. The class mapping for these three triggers agrees with runtime once the whole continuation chain is joined.
5. Token shape still kills a strict reading of the wave word `duplicate`. The docstring continuation says `duplicated` (file line 47). The raise site says `duplicates` (`drift` line 159: `line %d duplicates %s`). `W1RevC2Doc` §6 names the trigger `duplicate`. `\bduplicate\b` matches none of the docstring or the refusal string. The substring `duplicate` matches all three. A word-boundary verifier reports the wrapped trigger missed on bytes whose mapping is right. A substring verifier accepts it, and is the same kind of check that treats `missing` as present inside the class token `RECORD-MISSING` (prose-only search of the joined `RECORD-MISSING` entry is False for `missing`; the continuation says the path `exists`).

The preregistration says "the frozen list" and does not enumerate class/trigger pairs. `TOTAL` and `duplicate` in that file are the C3 parser claim (`duplicate/multiple TOTAL rows`), not a C2 pair table. The nearest pair list is the r39 wave note in `.ufo/waves/round-39/w1/W1RevC2Doc.md` §6: seven triggers, "four" of them unprobed, then five names (`ELOOP`, non-regular, schema, duplicate, TOTAL). `ELOOP` and `non-regular` sit on first lines, so r39 already stores them. The continuation-only remainder is schema, duplicated, and TOTAL, and only TOTAL needs a second continuation.

## Bytes under test

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e

git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD:tools/souji-worktree-drift.py
5a2b32941bc5c3da628ee92f75be1c33192ca311

git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py
5a2b32941bc5c3da628ee92f75be1c33192ca311

git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 0242085909fb6a4ee041c5443d76316ac6d59d4b:census/round-39/c2-counter.py
953810db16fa0f7f308311b0aa65a49ad1d80223

git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD:census/round-39/c2-counter.py
953810db16fa0f7f308311b0aa65a49ad1d80223

git -C /home/vgpnk/Projects/shokunin/souji-shokunin merge-base --is-ancestor 0242085909fb6a4ee041c5443d76316ac6d59d4b HEAD
ANCESTOR=yes

git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel
/home/vgpnk/Projects/shokunin/souji-shokunin

git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- tools/souji-worktree-drift.py census/round-39/c2-counter.py
(empty)
```

HEAD has moved past the preregistration base. The two blobs this attack reads are identical at `0242085` and at HEAD. Extraction was `git show 0242085:path` into scratch, not a worktree read.

Committed refusal block (1-based lines of the extracted blob; indent 2 = class line, indent 25 = continuation):

```
44:  RECORD-MISSING         EACCES or ELOOP opening the record path: the path
45:                         exists but cannot be opened or read
46:  RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line
47:                         that does not match the schema, a duplicated name, or
48:                         a TOTAL row that disagrees
49:  RECORD-EMPTY           no REPO rows
```

`RECORD-MALFORMED` is three physical lines. No blank line inside the entry. Raise sites in the same blob:

```
159: raise Refusal("RECORD-MALFORMED: line %d duplicates %s" % (lineno, name))
166: raise Refusal("RECORD-MALFORMED: line %d does not match the census schema" % lineno)
171: raise Refusal("RECORD-MALFORMED: TOTAL repos=%d but %d REPO rows" % (total["repos"], len(rows)))
```

r39 selector, `census/round-39/c2-counter.py` lines 133-144: `ast.get_docstring(..., clean=False)`, then the first `strip()` line that `startswith` `RECORD-MISSING` or `RECORD-MALFORMED`.

## Commands and outputs

Scratch: `TMPDIR=/fast/scratch/hyaku/souji-r40/R40scout17`. Lane cwd was not used for writes. No git commit. The runtime probes call `parse_record` before any git child, so the `--root` was an empty directory, not a repository.

### 1. Imported r39 map (control)

`importlib` loaded `/fast/scratch/hyaku/souji-r40/R40scout17/c2-counter-r39.py` and called `docstring_classes` on the extracted drift blob.

```
IMPORTED_R39
RECORD-MISSING 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path'
RECORD-MALFORMED 'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line'
```

First-line token presence for `RECORD-MALFORMED`: `TOTAL` False, `schema` False, `duplicate` False, `duplicated` False, `missing` True, `non-regular` True, `ENOENT` True.

### 2. Three joiners on the committed docstring

`until_next_class`: skip blank lines; a line whose `strip()` starts with a known class token (longest match) starts a new entry; other non-empty lines append. `one_extra_line`: append only the immediately following non-empty, non-class line. `until_blank`: same as `until_next_class` but a blank line closes the entry.

```
until_next_class len 157
  has TOTAL True schema True duplicated True duplicate_substr True
  WORD duplicate False WORD duplicated True
  TEXT 'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line that does not match the schema, a duplicated name, or a TOTAL row that disagrees'
one_extra_line len 130
  has TOTAL False schema True duplicated True duplicate_substr True
  WORD duplicate False WORD duplicated True
  TEXT 'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line that does not match the schema, a duplicated name, or'
until_blank len 157
  has TOTAL True schema True duplicated True duplicate_substr True
```

On these committed bytes `until_blank` and `until_next_class` agree, because the entry contains no blank line. They diverge on the synthetic in §4.

Joined `RECORD-MISSING` text:

```
'RECORD-MISSING         EACCES or ELOOP opening the record path: the path exists but cannot be opened or read'
substr missing True
prose-only missing False
prose has exists True
physical_lines 3
```

### 3. Runtime of the extracted blob

```
python3 -B drift-r39.py --root "$TMPDIR/root" --record <tsv> --timeout 5
```

```
CASE dup rc 2
  STDERR REFUSAL RECORD-MALFORMED: line 2 duplicates a
  body: REPO<TAB>a<TAB>regs=1<TAB>prunable=0  (twice)
CASE schema rc 2
  STDERR REFUSAL RECORD-MALFORMED: line 2 does not match the census schema
  body: one valid REPO row, then NOT-A-ROW
CASE total rc 2
  STDERR REFUSAL RECORD-MALFORMED: TOTAL repos=9 but 1 REPO rows
  body: one REPO row, then TOTAL repos=9 regs=1 prunable=0
CASE total-ok-shape rc 1
  STDERR (empty)
  STDOUT DRIFT ABSENT a
  body: one REPO row, TOTAL repos=1 regs=1 prunable=0
```

The agreeing TOTAL row is not `RECORD-MALFORMED`. The continuation's verb is "disagrees", and the rc-2 case is the disagreement. `ABSENT` is the empty root having no repository named `a`; it is evidence only that parse accepted the record.

Stem table, copied from the script's `STEMS` lines (`wb-` is `re.search` of a word-boundary pattern):

```
STEMS
doc substr True wb-duplicate False wb-duplicated True wb-duplicates False
runtime substr True wb-duplicate False wb-duplicated False wb-duplicates True
wave substr True wb-duplicate True wb-duplicated False wb-duplicates False
```

`schema` is a substring of both the continuation ("the schema") and the refusal ("the census schema"). `TOTAL` is the same token in the continuation and in the refusal.

### 4. Synthetics (scratch strings passed through `ast.get_docstring(..., clean=False)`)

Depth 2 — `EACCES` only on the first continuation of `RECORD-MISSING` (the shape the claim's synthetic probe names):

```
  RECORD-MISSING         opening the record path: the path
                         EACCES or ELOOP
r39 EACCES=False
one_extra EACCES=True
until_next EACCES=True
until_blank EACCES=True
```

Depth 3 — `EACCES` only on the second continuation (the committed `TOTAL` shape, moved onto `RECORD-MISSING` so the token is not already on the class line):

```
  RECORD-MISSING         opening the record path: the path
                         exists but cannot be opened or read
                         EACCES or ELOOP
r39 EACCES=False
one_extra EACCES=False
until_next EACCES=True
until_blank EACCES=True
```

Blank line between the class line and the `TOTAL` continuation (not present in the committed entry):

```
  RECORD-MALFORMED       a missing path, a line

                         a TOTAL row that disagrees
r39 TOTAL=False
one_extra TOTAL=False
until_next TOTAL=True
until_blank TOTAL=False
```

Continuation whose `strip()` starts with another class token:

```
  RECORD-MALFORMED       a missing path
                         RECORD-EMPTY a TOTAL row that disagrees
until_next RECORD-MALFORMED TOTAL=False  text='RECORD-MALFORMED       a missing path'
until_next RECORD-EMPTY    TOTAL=True   text='RECORD-EMPTY a TOTAL row that disagrees'
```

## What this does to the C2 predicate

An r40 receipt that only shows "synthetic depth-2 probe detected, r39 missed it" can still miss `TOTAL` on the committed entry. That is the kill ("wrapped trigger is missed") for `one_extra_line`.

An r40 receipt that joins until the next class token, then checks the substring `TOTAL` / `schema` / `duplicate` on `RECORD-MALFORMED`, matches this edge and matches runtime. It still does not, by itself, satisfy "mapping disagrees with runtime" for a missing path raised as `RECORD-MISSING`, because `missing` occurs inside the class token and the joined continuation says the path exists. That vacuity is the r39 finding in `W1RevC2Doc` §3; joining does not remove it.

Blank-line policy and class-token-on-a-continuation are kill conditions the committed entry does not exercise. A later docstring edit that inserts a blank before `TOTAL`, or that wraps a line starting with `RECORD-EMPTY`, changes which joiner still sees `TOTAL`. The predicate text does not choose among those joiners.

## Other wraps seen and not taken

Same scan, indent 25, left for other items: `RECORD-OUTSIDE-ROOT` continues with `--root` (line 50); `JSON-IS-RECORD` continues with `inode` (line 53); `JSON-NOT-REGULAR` continues with `FIFO` (line 55); `JSON-UNWRITABLE` continues with `O_NOFOLLOW` (line 58). This item measured none of those at runtime.

## Scratch

`/fast/scratch/hyaku/souji-r40/R40scout17` held the two `git show` extracts, four record TSVs, and the empty `--root`. Removed with `rm -rf` before yield. Nothing under `/tmp`. No install.

## Trailer

Report path relative to the lane root: `.ufo/waves/round-40/w1/R40scout17.md`
