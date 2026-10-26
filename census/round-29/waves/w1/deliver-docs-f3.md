# Deliver — round 29 C3 documentation edits (F3)

Three edits, one paste target each. Ground: `census/round-29/records/preregistration.txt`
claim C3 ("Admit exactly two re-grounded entries … Both carry `ground: F3` … and are named
in the corpus/README.md coverage map F3 row") and `PROVINCE.md:69-71`
("F3 duplicate verdicts — byte-identical copies; a `duplicate` receipt class would be a
taxonomy change (operator decision)").

The two entries this documentation names are wave deliveries, not yet at HEAD:
`.ufo/waves/round-29/w1/deliver-duplicate-verdict-identity.md` and
`.ufo/waves/round-29/w1/deliver-duplicate-verdict-byte-equality.md`. The README row and the
entry files must land in the same commit, or the row's `knowledge/...` spans dangle
(`DANGLING-MAP-PATH`).

## 1. corpus/README.md

### 1a. Replace line 41 (the F3 row of the `### Coverage map` table, r12 block)

This is an **in-place map-row edit**, the habit r28 followed for the F4 row at `:42`
(`git show 765fe8b -- corpus/README.md` = 1 insertion, 1 deletion). The superseding record
is the appended `### Round 29 corrections` block in 1b. No other existing line changes.

Old (base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`, also HEAD `b8cb4b31`):

```markdown
| F3 duplicate verdicts | frontier, entry held | `knowledge/dupe-finders-detect-then-act.md` |
```

New:

```markdown
| F3 duplicate verdicts | frontier, entries held | `knowledge/dupe-finders-detect-then-act.md`, `knowledge/duplicate-verdict-identity.md`, `knowledge/duplicate-verdict-byte-equality.md` |
```

Format check against `tools/souji-coverage-agreement.py`: the row stays a 3-cell row
(`CELL_SPLIT`, `:35`), the ground cell keeps its `F3` prefix (`GROUND_TOKEN`,
`:33`), and each entry is a backticked `knowledge/<name>` span (`CODE_SPAN` :37,
`KNOWLEDGE_PATH` :38) in the third cell, which is what `map_rows` (:84, :89) consumes.
Measured, not inferred: see §4.

### 1b. Append after the last line (EOF, after `corpus/README.md:558`; file ends with a newline)

```markdown
## Round 29 — F3 duplicate verdicts re-grounded

Appended; the sections above stand. Two knowledge entries are admitted for F3, re-grounded
this round from the four probe rows S216–S219 opened this round, snapshotted under
`../census/round-29/sources/` and gated by `../tools/souji-gate-check.py`:

- `knowledge/duplicate-verdict-identity.md` — `link(2)`/`statx(2)`: a second name for an
  existing file works exactly as the original name and no name is the original, so a
  duplicate verdict compares identity — the `stx_ino` and `stx_nlink` fields of
  `struct statx` — not path strings; Broder's resemblance and containment enter as
  vocabulary only. Sources S216, S217, S218.
- `knowledge/duplicate-verdict-byte-equality.md` — `cmp(1)`'s three-valued exit contract
  ("Exit status is 0 if inputs are the same, 1 if different, 2 if trouble.") plus the same
  identity rule; supersedes nothing. Sources S219, S218, S217.

Coverage-map effect: the F3 row at `:41` now reads "frontier, entries held" and names all
three F3 entries. F3 stays frontier — no `duplicate` receipt class is created (taxonomy
change, operator decision), no near-duplicate threshold is admitted, and no tool changes.

### Frontier (r29)

- F3 — the identity half and the byte-equality half are now held as entries, and a SKILL
  classify row states the rule; remaining: a `duplicate` receipt class is an operator
  decision (taxonomy change), and any near-duplicate measure or threshold is outside this
  frontier's byte-identical scope (the Broder rows are vocabulary only).
- F1, F2, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.

### Round 29 corrections

- The r12 F3 row at `:41` was replaced in place rather than superseded by a later table:
  its status cell changed from "frontier, entry held" to "frontier, entries held" and its
  entries cell gained `knowledge/duplicate-verdict-identity.md` and
  `knowledge/duplicate-verdict-byte-equality.md`. Map rows are edited in place (r28 did the
  same to the F4 row at `:42`); the append-only record is this section.
- The `## Frontier` bullet at `:48` stands as written: "a `duplicate` receipt class is an
  operator decision (taxonomy change)" remains the next step; the r29 entries do not take it.
```

Why a `## Round 29` heading: the section imitates r22 attempt 2 / r24 / r25 (a round
heading, then `### Frontier (rN)` and a corrections block). Note the file has **no** r26,
r27 or r28 round section — the last round heading before this append is `## Round 25`
(`:538`) — so there is no newer style to imitate. `git log --oneline -- corpus/README.md`
shows `765fe8b` (round 28) touched exactly one line of this file, the F4 map row.

Snapshot bytes opened this run for the block's claims (staged under
`.ufo/waves/round-29/w1/sources/`, landing at `census/round-29/sources/`):
`cmp.1.html:113-114` carries the quoted exit-status sentence wrapped across two lines;
`link.2.html:100-102` carries the second-name sentence; `statx.2.html:93` and `:97` carry the
`stx_nlink` and `stx_ino` field comments.

## 2. PROVINCE.md — append at EOF (after `PROVINCE.md:172`)

Style: the Round 13–21 boundary notes (each states what the surface holds, then what it
does not, then what is unchanged). No existing line changes.

```markdown
## Round 29 boundary note (F3 duplicate verdicts)

F3 now holds two admitted, re-grounded entries — `corpus/knowledge/duplicate-verdict-identity.md`
(S216, S217, S218) and `corpus/knowledge/duplicate-verdict-byte-equality.md` (S219, S218,
S217) — beside the r12 held entry `corpus/knowledge/dupe-finders-detect-then-act.md`. The
identity half is the `link(2)`/`statx(2)` rule: two names may be one file, so a duplicate
verdict compares inodes (`stx_ino`, `stx_nlink`), never path strings. The byte-equality half
is the documented three-valued `cmp(1)` contract: 0 same, 1 different, 2 trouble — exit 2 is
trouble, never "different". Broder's resemblance and containment are vocabulary only.

What F3 does **not** hold: no `duplicate` receipt class (a taxonomy change, so an operator
decision — `## Core / Frontier / Adjacent` above at `:69-70` is unchanged), no
near-duplicate threshold (document-similarity ground sits outside this frontier's
byte-identical scope), and no tool change — nothing in `tools/` acquires a duplicate
verdict. The round-29 SKILL classify row states the rule; it creates no receipt and no
runnable verdict.

Core and Frontier are otherwise unchanged: Core is the `## Owns` and `## Work surfaces`
list above (`:60`), and this round adds no entry to either; F3 stays frontier. Certification
OFF, K5 HELD. Sources: `census/round-29/records/preregistration.txt` claim C3; the two
entries and their Gates.
```

## 3. SKILL.md — one row in `### Classify an artifact`

Insert as a new row immediately **before** the default row at `SKILL.md:52`
(`| Anything else, any doubt, any credential-shaped content | NOT-SAFE — stay silent in the dry run |`).
No other SKILL line changes; the receipt taxonomy at `:26-40` is untouched because no
receipt class is created.

```markdown
| Another artifact is offered as a duplicate (`cmp` byte-equality candidate or a same-content pair) | `NOT-SAFE` — no `duplicate` receipt class exists (taxonomy change, operator decision); before any verdict compare identity: `stat -c '%d:%i'` (or statx `stx_ino`/`stx_nlink`) reports one inode for two names — one file under two names, not two copies — and `cmp` exit 2 is trouble, never "different" |
```

Support: `stat -c '%d:%i'` and statx `stx_ino`/`stx_nlink` are named in the identity entry's
Gate (S216, S218); the three-valued `cmp` exit contract is the byte-equality entry's Gate
quote (S219); "no receipt class" is `PROVINCE.md:69-70` plus the `### Classify an artifact`
default row. The "no tool" clause's sweep, 2026-10-25:

```
$ grep -n 'duplicate' tools/souji-verify.sh tools/souji-quarantine.sh tools/souji-census.sh tools/souji-gate-check.py
tools/souji-census.sh:1840:      usage_err "compare file: duplicate repo $repo"
tools/souji-gate-check.py:171:                    fails.append("verdict-duplicate:%s" % vid)
```

Both hits are unrelated to an F3 verdict (a compare-file repo key and a duplicate gate
verdict id); no tool computes a duplicate verdict. Local observation of the commands,
2026-10-25 (scratch only):

```
$ stat -c '%d:%i %h %n' f g h        # f and g hardlinked
32:49364570 2 f
32:49364570 2 g
32:49364571 1 h
$ cmp -s f g; echo $?   -> 0
$ cmp -s f h; echo $?   -> 1
$ cmp -s f nosuch; echo $? -> 2
```

## 4. Verification performed (not inferred)

Base coverage agreement, lane HEAD (`b8cb4b31ce80e2e3314b88e85d40ea9873180804`):

```
$ python3 -B tools/souji-coverage-agreement.py --root . --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e
grounded=13 mapped=13 dangling=0 mismatches=0
rc=0
```

Simulation of this delivery in a throwaway clone (`/var/tmp/souji-r29-SwarmScribe27.VVf7q2/c`,
`git clone -q --no-local`), with the two delivery entries copied to `corpus/knowledge/` and
only the §1a row replaced, committed there as
`4f82faf851e60a2ece801205d63934a3ea1dc702`:

```
$ python3 -B tools/souji-coverage-agreement.py --root <scratch>/c --rev 4f82faf8…
grounded=15 mapped=15 dangling=0 mismatches=0
rc=0
$ python3 -B tools/souji-coverage-agreement.py --root <scratch>/c --rev 4f82faf8… --base-rev 691dd292…
grounded=15 mapped=15 dangling=0 mismatches=0 kill_tested=13 kill_violations=0
rc=0
```

So the row format is measured to satisfy the tool, including the kill rule over the 13
base-grounded entries. The scratch clone is removed before this seat finishes. Not run here:
`souji-gate-check.py` and `sources-census.sh validate` — gate and source seats own them;
this delivery claims no gate exit.

## 5. Forward references the L1 must satisfy

- Both entry files land with the README row (single commit) or the row dangles.
- The prose's "snapshots under `../census/round-29/sources/`" resolves only when the staged
  `w1/sources/` directory lands there.
- S216–S219 are lane ids per the sources append block; the S216 URL-scope warning is the
  source seat's to resolve.
