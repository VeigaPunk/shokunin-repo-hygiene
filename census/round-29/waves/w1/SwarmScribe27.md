# SwarmScribe27 — round 29 C3 documentation edits (F3)

## Status

STATUS: PASS — three drafted documentation edits (README F3 row + appended r29 blocks,
PROVINCE boundary note, one SKILL classify row) delivered to `.ufo/waves/round-29/w1/deliver-docs-f3.md`;
the row format is measured to satisfy `tools/souji-coverage-agreement.py` (15/15, kill_violations=0)
in a throwaway clone. No product file was edited, staged or committed; only this report and
the delivery were written. Gate and sources counters are not mine and were not run.

## Evidence

Lane tip read this run: `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (branch master); prereg
contract at `census/round-29/records/preregistration.txt`, claim C3.

Base coverage agreement, base rev, run from
`/home/vgpnk/Projects/shokunin/souji-shokunin`:

```
$ python3 -B tools/souji-coverage-agreement.py --root . --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e
grounded=13 mapped=13 dangling=0 mismatches=0
rc=0
```

Simulation of this delivery (clone `--no-local` under
`/var/tmp/souji-r29-SwarmScribe27.VVf7q2/c`, the two delivery entries copied into
`corpus/knowledge/`, only the §1a row replaced), scratch commit `4f82faf851e60a2ece801205d63934a3ea1dc702`:

```
$ python3 -B tools/souji-coverage-agreement.py --root <scratch>/c --rev 4f82faf8…
grounded=15 mapped=15 dangling=0 mismatches=0
rc=0
$ python3 -B tools/souji-coverage-agreement.py --root <scratch>/c --rev 4f82faf8… --base-rev 691dd292…
grounded=15 mapped=15 dangling=0 mismatches=0 kill_tested=13 kill_violations=0
rc=0
```

Tool-format check done in-process with the tool's own regexes (`GROUND_TOKEN` :33,
`CELL_SPLIT` :35, `CODE_SPAN` :37, `KNOWLEDGE_PATH` :38, `map_rows` :84/:89): 3 cells,
ground token `F3`, names `dupe-finders-detect-then-act.md`,
`duplicate-verdict-identity.md`, `duplicate-verdict-byte-equality.md`.

No-tool sweep for the SKILL row's negative clause:

```
$ grep -n 'duplicate' tools/souji-verify.sh tools/souji-quarantine.sh tools/souji-census.sh tools/souji-gate-check.py
tools/souji-census.sh:1840:      usage_err "compare file: duplicate repo $repo"
tools/souji-gate-check.py:171:                    fails.append("verdict-duplicate:%s" % vid)
```

Command behaviour observed once in the same scratch (f/g hardlinked):

```
$ stat -c '%d:%i %h %n' f g h
32:49364570 2 f
32:49364570 2 g
32:49364571 1 h
$ cmp -s f g -> 0 ; cmp -s f h -> 1 ; cmp -s f nosuch -> 2
```

Sources opened this run: `corpus/README.md` (:1-80, :380-558), `PROVINCE.md` (:1-60, :58-172),
`SKILL.md` (:1-120, :167-226), `tools/souji-coverage-agreement.py` (whole file),
`.ufo/waves/round-29/w1/deliver-duplicate-verdict-{identity,byte-equality}.md`,
`.ufo/waves/round-29/w1/deliver-readme-f3-row.md`, `.ufo/waves/round-29/w1/deliver-sources-append-block.md`,
and the staged snapshots `.ufo/waves/round-29/w1/sources/{cmp.1,link.2,statx.2}.html`.
Scratch removed (`ls -d /var/tmp/souji-r29-SwarmScribe27.*` → rc 2).

Snapshot locations of the drafted block's claims (read from those bytes):

```
cmp.1.html:113-114  Exit status is / 0 if inputs are the same, 1 if different, 2 if trouble.
link.2.html:100-102 This new name may be used exactly as the old one for any / operation; ...
statx.2.html:93     __u32 stx_nlink;       /* Number of hard links */
statx.2.html:97     __u64 stx_ino;         /* Inode number */
```

## Findings

1. **F3 row replacement is measured, not asserted.** Exact old/new line at
   `corpus/README.md:41`; status cell `frontier, entry held` → `frontier, entries held`; the
   two added paths are the delivered entries. Base 13/13 → simulated 15/15, dangling=0,
   kill_violations=0 (`deliver-docs-f3.md` §1a, §4).
2. **No r26-r28 round sections exist in `corpus/README.md`.** The last round heading is
   `## Round 25` (`:538`); `git log --oneline -- corpus/README.md` shows `765fe8b` (round 28)
   changed exactly one line — the F4 map row at `:42`. The assignment's "read its r24-r28
   sections" therefore reduces to r22/r24/r25 style; the appended block imitates those and
   cites `:538` nowhere.
3. **In-place F3 row edit has precedent but no in-file marker.** r28 edited the F4 map row
   in place (`git show 765fe8b -- corpus/README.md` = 1 insertion, 1 deletion), so the
   drafted `:41` replacement follows that habit; the append-only record is the drafted
   `### Round 29 corrections` bullet naming the old and new status cell. If the L1 prefers
   r24's "status prose stays as history" form instead, the counter still reaches 15/15 by
   adding a new F3 row rather than replacing `:41` — but only the replacement was instructed.
4. **PROVINCE F3 sentence stays valid; the promotion sentence is addressed.** F3 at
   `PROVINCE.md:69-70` is unchanged, and Core is defined as the `## Owns`/`## Work surfaces`
   list (`:60`); the drafted note says so explicitly so the r12 "moves to Core only with an
   admitted entry and a SKILL rule" sentence (`:61-63`) is not read as a promotion the round
   did not make.
5. **SKILL.md has no existing F3/duplicate rule.** `grep -n -i 'duplicate|dupe'` returns only
   the description line, a historical error-pattern sentence (`:87`), the gate registry rows,
   and prose at `:298`/`:388`; the classify table (`:44-52`) default row at `:52` is the
   insertion point, and the receipt taxonomy (`:26-40`) gains nothing.
6. **Duplicate sibling draft of the same row.** `.ufo/waves/round-29/w1/deliver-readme-f3-row.md`
   already drafts a byte-identical `:41` replacement and cites a scratch rev
   `53264d05f4163c876eb9c4ddf297ddba1a9723c3` that is not in this lane; my §1a matches it
   exactly, so the L1 lands one of them. My 15/15 measurement is independent of that file.
7. **Forward references.** Both entries' Gates name `census/round-29/sources/*` snapshots that
   currently sit uncommitted under `.ufo/waves/round-29/w1/sources/`; the drafted README prose
   resolves only when entries, snapshots and the row land together. `souji-gate-check.py` and
   `sources-census.sh validate` were not run by this seat, and the drafts claim no gate exit.
8. **Local artifact, not mine, left in place.** `tools/__pycache__/souji-gate-check.cpython-314.pyc`
   exists and is gitignored (`.gitignore:3`), i.e. a gate run without `-B`; per the hard bound
   this seat reports it and removes nothing. Lane worktree otherwise shows only the
   pre-existing ` M .ufo/waves/round-26/w1/ScribeGateDraft.md`.
9. **The F3 Gate quotes are wrapped paragraphs.** `cmp.1.html:113-114` and
   `link.2.html:100-102` wrap mid-sentence; the drafted README sentence uses the joined
   paragraph, which is the rule at `SKILL.md:119` (Q36: a first-physical-line quote hides a
   wrapped cut). A line matcher run on the first physical line would miss both.
10. **Whitespace normalization inside the identity Gate quote.** The entry's Gate quotes
    `stx_ino; /* Inode number */`, while `statx.2.html:97` carries aligned columns
    (`stx_ino;         /* Inode number */`). Whether that is verbatim depends on
    `souji-gate-check.py`'s normalization; the gate seat owns the verdict, this seat only
    records the byte difference it observed.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-docs-f3.md` — README §1a replacement line, §1b append block
  (`## Round 29` + `### Frontier (r29)` + `### Round 29 corrections`), PROVINCE §2
  `## Round 29 boundary note`, SKILL §3 classify row, plus verification and forward references.
- `.ufo/waves/round-29/w1/SwarmScribe27.md` — this report.
