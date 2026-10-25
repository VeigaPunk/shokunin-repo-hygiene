STATUS: PASS

# Slice123 — absent-defect register row S123 (lane `souji`), hand-check

## Frozen class for S123: `refused`

Reason: the named local artifact does not contain the quoted span (byte-level
receipt below); the span is nevertheless a **real sentence** that lives in
`git-worktree(1)` and on https://git-scm.com/docs/git-worktree. That is a
**wrong-source citation** — a citation-class defect, not a fabrication.

## Row under test (extracted read-only; field 4 = id cell)

The preregistration freezes counters, per-entry predicate, slice predicate and
kill rules; it contains **no** register-extraction awk line. Extraction was
therefore the field-4 id selection prescribed for this item:

```
$ awk -F'|' '$4 ~ /S123/ {print NR": "$0}' \
    /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
172: | `souji` | round2 | S123 | `payload-absent` | lanes/souji/round2/evidence/r23-trigger-prune.out | `git worktree prune [-n] [-v] [--expire <expire>]` | cited source, companion URLs and local artifacts were all checked; the quote is in none of them |
```

Line 364 (`tameshi`) also matches the literal `S123` but belongs to another
lane and was deliberately **not** parsed.

## 1. Payload check — executed

Source: `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-trigger-prune.out`
(opened read-only; nothing written back)

```
size   1043 bytes, 15 lines
sha256 510722c11a97f6bca8f93e49b8a279f1f109d0222e40f675d001058768e069b4
$ grep -c -i 'worktree' <file>  -> 0
$ grep -c -i 'prune'    <file>  -> 1
$ grep -n -i 'prune'    <file>  -> 10:# provenance: produced by fixtures/r23-trigger-prune.sh on git 2.56.0
$ grep -n 'expire'      <file>  -> no match
$ grep -qF 'git worktree prune [-n] [-v] [--expire <expire>]' <file> -> SPAN_ABSENT
```

The payload is an 8-case `fetch`/`pull`/`merge`/`rebase` refcount probe
(`SOUJI-R23-TRIGGER-*`, all `verdict=PASS`); it invokes **no** `git worktree`
command. The register's `payload-absent` label is reproduced from bytes.

## 2. Located span — executed

Exact span (9 words, verbatim in both sources):

> git worktree prune [-n] [-v] [--expire <expire>]

| source | access date | locator | snapshot sha256 |
|---|---|---|---|
| `man git-worktree \| col -b` (git 2.56.0, installed) | 2026-10-25 | **SYNOPSIS**, heading line 6, entry line 12 | `b9d571b305dd725dcfea8b7194a2be562377efa789bed6e09b190ee1d5951f4f` (738 bytes, embedded in evidence) |
| https://git-scm.com/docs/git-worktree | 2026-10-25 (curl exit 0, HTTP 200) | **SYNOPSIS**, `<h2 id="_synopsis">` line 2409; span line 2417 (markup splits it across `<code>` spans) | `fa25690b04900cfc1f1b52bb6b23a85d63f8b763477cca71e655434adbfc63d2` (98918 bytes raw HTML); tags-stripped 58-byte line → `831edb0a0e45f5c939e21e72a18d0d219e4fe61e4b60f4f57cc47f9418f701c8` |

The man snapshot round-trips: the block embedded in the evidence file hashes to
`b9d571b3…d5951f4f`, identical to the pipeline output.

## 3. Where the citation went wrong — executed (read-only scan)

```
$ grep -rIl -F 'git worktree prune [-n] [-v] [--expire <expire>]' \
    /home/vgpnk/Projects/shokuknow/lanes/souji
./round2/SOURCES-PROPOSED.md
./round15/evidence/cnblogs-worktree-zh.txt
./round16/evidence/git-worktree-c-247.c
./round16/evidence/git-worktree-c-248.c
```

- `round2/SOURCES-PROPOSED.md:44` — the lane already pairs this exact sentence
  with `https://git-scm.com/docs/git-worktree`, i.e. the sentence's true home was
  on record in the lane, but not in the artifact this register row names.
- `round16/evidence/git-worktree-c-247.c:40` and `-248.c:42` — the upstream
  usage string `N_("git worktree prune [-n] [-v] [--expire <expire>]")`.
- `round15/evidence/cnblogs-worktree-zh.txt:90, :370` — mirrored copy.

## Bounded findings

1. **Payload absence confirmed, not weakened.** 1043 bytes containing zero
   `worktree` tokens cannot carry a `git worktree prune` synopsis.
2. **The quote is authentic.** It is the SYNOPSIS line of `git-worktree(1)` at
   git 2.56.0 (the same version the payload's provenance line names) and of the
   published page. Suppressing the row as "fabricated" would be wrong; "wrong
   source" is right.
3. **The row's tail clause is overbroad.** "companion URLs and local artifacts
   were all checked; the quote is in none of them" is false for the one
   companion URL the lane itself associates with the sentence
   (`git-scm.com/docs/git-worktree`). The artifact-scoped half of the claim
   stands. Which companions were actually checked is not recorded in the row, so
   the overbreadth is reported, not attributed.
4. **[INFERENCE]** `SOURCES-PROPOSED.md:44` pins the locator as "§ OPTIONS",
   but both sources place the span under SYNOPSIS; the page's OPTIONS entry for
   `--expire` reads `--expire <time>`, a different string. That is a locator
   drift, one level below the register row.
5. **Register untouched.** The row was quoted, not edited; no correction written
   back, no rewrite proposed.

## Evidence

`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-22/attempt2/w1/evidence/slice123-trigger-prune.out`
— 6620 bytes, sha256 `537e35b32b1653f3beb29622b289001877bed83dfb0b4debeabc5ffb6ea335d3`;
contains the payload census, both source snapshots with their digests, and the
lane-local scan.

Bounds: no git/jj writes, no commit, no lane-index/`.ufo/state`/`watchdog.log`/
`MANIFEST.json`/templates/scripts writes, no sibling-repo writes, no signals, no
deletion authority; `shokuknow` read-only; one https fetch (git-scm.com). No tool
installed or upgraded. Writes limited to this report and the named evidence file.

Executed: all `grep`/`awk`/`man`/`curl`/`sha256sum` calls above.
Source-inferred: finding 4 (locator section mismatch) and the attribution in 3.
