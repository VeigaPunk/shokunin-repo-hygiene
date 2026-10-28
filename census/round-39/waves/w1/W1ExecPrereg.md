# W1ExecPrereg — r38 preregistration append proof (round 39, wave 1)

Seat: executor W1ExecPrereg. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Contract read first: `census/round-39/preregistration.txt` (freeze b769bfb, lane base ed30b7f).
No `git`/`jj` mutation was run. Only `/fast/scratch/hyaku/souji-r39/W1ExecPrereg` was written
outside this report. No tool was installed or upgraded.

Subject: `census/round-38/preregistration.txt` — routed defects R8 (stale prereg bytes) and
R9 (in-place-rewritten prereg bytes). The file at HEAD already carries the R39 append; this seat
proves the append is a pure EOF append and that the 227-line frozen prefix is untouched.

## Headline verdicts

| # | Check | Verdict |
|---|---|---|
| P1 | Base file digest (ed30b7f, 227 lines) and frozen-prefix digest | PASS — both `cb47d50f7e23…512fe` |
| P2 | Frozen prefix (first 227 lines) unchanged at HEAD | PASS — same digest, byte-identical prefix |
| P3 | Base→HEAD is append-only (no deleted/modified line) | PASS — `4 insertions(+), 0 deletions` at `@@ -227,0 +228,4 @@` |
| P4 | Scratch copy = base + explicit two-line amendment | PASS — reconstructs HEAD byte-for-byte `a43e337b682d…125b0` |
| P5 | Appended bytes parse as plain UTF-8 text | PASS — `UTF-8 text`, 0 control chars, 0 CR, no trailing whitespace |
| P6 | C1 counter reads the two anchor rows | PASS — `CLOSED` at HEAD, `OPEN ANCHOR-ABSENT` at base |
| P7 | A10's cited artifacts exist and its stale-pointer claim is true | PASS |
| P8 | Append shape / last three lines recorded | PASS (with shape caveat C1) |
| Q1 | A11's historical attribution and quotation fidelity | QUALIFIED — see caveats C2/C3 |
| Q2 | "No frozen sentence altered" relative to the **freeze commit** | NOT established by the append — see caveat C4 |

## P1 — base digest and frozen-prefix digest

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && \
  git show ed30b7f5b77939c9073348d810730bc4f355708d:census/round-38/preregistration.txt | wc -l
227
$ git show ed30b7f…:census/round-38/preregistration.txt | sha256sum
cb47d50f7e239fc629b8f7385fe4f03076a05f7849b4dfe742f715d89a8512fe  -
$ git show ed30b7f…:census/round-38/preregistration.txt | sed -n '1,227p' | sha256sum
cb47d50f7e239fc629b8f7385fe4f03076a05f7849b4dfe742f715d89a8512fe  -
```

Base file = 227 lines and the first 227 lines are the whole file, so the two digests coincide by
construction: **base sha256 = frozen-prefix sha256 = `cb47d50f7e239fc629b8f7385fe4f03076a05f7849b4dfe742f715d89a8512fe`**.
Last byte of the base file is `\n` (`tail -c 1 … | od -An -c` → `\n`), so an append starts a new line.

## P2 — frozen prefix unchanged at HEAD

```
$ sha256sum census/round-38/preregistration.txt
a43e337b682d8e00a249a4b4720a2de41489ca416bedb3b0fbb35f5fdfb125b0  census/round-38/preregistration.txt
$ sed -n '1,227p' census/round-38/preregistration.txt | sha256sum
cb47d50f7e239fc629b8f7385fe4f03076a05f7849b4dfe742f715d89a8512fe  -
$ git show HEAD:census/round-38/preregistration.txt | sha256sum    # HEAD = 2201778e7736af82e7d8a42dec2494f115bf3923
a43e337b682d8e00a249a4b4720a2de41489ca416bedb3b0fbb35f5fdfb125b0  -
$ git status --porcelain census/round-38/ census/round-39/
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
```

Working tree, HEAD-committed bytes and the reconstruct agree; the file has no uncommitted change.
Prefix digest at HEAD is identical to the base digest ⇒ **no frozen sentence in lines 1–227 was altered**.

## P3 — base→HEAD is a pure append

```
$ git diff --numstat ed30b7f5b77939c9073348d810730bc4f355708d HEAD -- census/round-38/preregistration.txt
4	0	census/round-38/preregistration.txt
$ git diff --stat ed30b7f… HEAD -- census/round-38/preregistration.txt
 census/round-38/preregistration.txt | 4 ++++
 1 file changed, 4 insertions(+)
$ git diff -U0 ed30b7f… HEAD -- census/round-38/preregistration.txt
@@ -227,0 +228,4 @@ permitted; routed to round 39 as a register design item.
+
+R39-C1-08 — A10 (appended 2026-10-28 by round 39): …
+
+R39-C1-09 — A11 (appended 2026-10-28 by round 39): …
```

Zero deletions and a single zero-length-context hunk anchored at EOF ⇒ the landed round-39 bytes are
append-only, which is the shape R9's in-place rewrite did not have.

## P4 — scratch reconstruction (the requested experiment)

```
$ S=/fast/scratch/hyaku/souji-r39/W1ExecPrereg; mkdir -p "$S"
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && \
  git show ed30b7f…:census/round-38/preregistration.txt > "$S/base-227.txt" && cp "$S/base-227.txt" "$S/append-copy.txt"
$ wc -l "$S/base-227.txt"
227 /fast/scratch/hyaku/souji-r39/W1ExecPrereg/base-227.txt
$ sha256sum "$S/base-227.txt"
cb47d50f7e239fc629b8f7385fe4f03076a05f7849b4dfe742f715d89a8512fe  /fast/scratch/hyaku/souji-r39/W1ExecPrereg/base-227.txt
$ # write the two amendment lines to "$S/amend-block.txt" (891 bytes, wc -l -> 4 physical lines)
$ cd "$S" && cat amend-block.txt >> append-copy.txt
$ sha256sum append-copy.txt
a43e337b682d8e00a249a4b4720a2de41489ca416bedb3b0fbb35f5fdfb125b0  append-copy.txt
$ wc -l append-copy.txt
231 append-copy.txt
$ sed -n '1,227p' append-copy.txt | sha256sum
cb47d50f7e239fc629b8f7385fe4f03076a05f7849b4dfe742f715d89a8512fe  -
$ git diff --no-index --numstat base-227.txt append-copy.txt
4	0	base-227.txt => append-copy.txt
$ sha256sum append-copy.txt /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-38/preregistration.txt
a43e337b682d8e00a249a4b4720a2de41489ca416bedb3b0fbb35f5fdfb125b0  append-copy.txt
a43e337b682d8e00a249a4b4720a2de41489ca416bedb3b0fbb35f5fdfb125b0  /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-38/preregistration.txt
```

Verdict: base + the explicit two-line block reproduces the landed file **byte for byte**
(`a43e337b…`). That is only possible if the landed append is exactly four physical lines and no
character of the 227-line prefix changed. Per-line digests for reproduction:

```
$ sed -n '229p' append-copy.txt | sha256sum
e1e8a0d020246ec743e075e0c79a2a997bfa96c27a1e8ff996ef7631eeb0ab8b  -
$ sed -n '231p' append-copy.txt | sha256sum
4a4aa7308fe6f933e93a11fd04efbbbf9fad4aeb8918e5c4e141e2407b80792e  -
$ sed -n '229p' … | wc -c ; sed -n '231p' … | wc -c
449
440
```

## P5 — appended bytes are plain text

```
$ file -b amend-block.txt
Unicode text, UTF-8 text, with very long lines (442)
$ file -b append-copy.txt
Unicode text, UTF-8 text, with very long lines (442)
$ python3 -B - <<'PY'   # reads base and copy as bytes, decodes the copy as UTF-8
prefix_bytes_identical= True prefix_sha256= cb47d50f7e239fc629b8f7385fe4f03076a05f7849b4dfe742f715d89a8512fe
valid_utf8=True lines_split= 231 ends_with_newline= True
appended_bytes= 891 appended_repr= '\nR39-C1-08 — A10 (appended 2026-10-28 by round 39): the A7
appended_nonblank_lines= 2
  starts= R39-C1-08 — A10 (appen | utf8_bytes= 448 | printable= True
  starts= R39-C1-09 — A11 (appen | utf8_bytes= 439 | printable= True
control_chars_excluding_newline= 0 nul= False
blank_separators= 1
```

```
$ sed -n '228,231p' census/round-38/preregistration.txt | grep -n ' $'    # trailing whitespace
$ grep -c $'\r' census/round-38/preregistration.txt
0
```

Two non-blank lines, one blank separator, no NUL, no control characters, no trailing whitespace, no
CR bytes, file still ends with `\n` ⇒ the appended bytes parse as plain text.

## P6 — the two C1 anchor rows read CLOSED at HEAD, OPEN at base

Probe file = the items header (lines 1–6) plus rows `R39-C1-08`/`R39-C1-09` (lines 14–15) copied
verbatim from the frozen `census/round-39/c1-items.tsv`.

```
$ TMPDIR="$S/tmp" python3 -B census/round-39/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 2201778e7736af82e7d8a42dec2494f115bf3923 --items "$S/two-items.tsv" \
    --register census/round-39/cells.tsv --scratch "$S/tmp"
ITEM R39-C1-08 CLOSED
ITEM R39-C1-09 CLOSED
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=2 open=0 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=256259f25d49
rc=1
$ … --rev ed30b7f5b77939c9073348d810730bc4f355708d …
ITEM R39-C1-08 OPEN ANCHOR-ABSENT census/round-38/preregistration.txt anchor='R39-C1-08'
ITEM R39-C1-09 OPEN ANCHOR-ABSENT census/round-38/preregistration.txt anchor='R39-C1-09'
SUMMARY items=2 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=256259f25d49
rc=1
```

`rc=1` in both arms is the register-leg shortfall of a two-row item probe (`register_cells=0<6`), not
an item failure; the item legs are what this seat needed. Note the counter matches tokens on the
anchor line only (`hits = [l for l in text.split("\n") if row["anchor"] in l]`), so the fact that
`tighter-only` also occurs on line 120 and `A0` on lines 121/123/130/132 does not weaken item 09:

```
$ for t in a7-counter-fixes2.txt r38-counter-arms.py tighter-only A0 superseded; do grep -n "$t" file | cut -d: -f1; done
a7-counter-fixes2.txt    lines: 229,
r38-counter-arms.py      lines: 229,
tighter-only             lines: 120,231,
A0                       lines: 121,123,130,132,231,
superseded               lines: 231,
```

## P7 — A10's citations are real and its stale-pointer claim holds

```
$ ls -l census/round-38/records/a7-counter-fixes2.txt tests/fixtures/r38-counter-arms.py census/round-38/records/a7-counter-fixes.txt
-rw-r--r-- … 846 … census/round-38/records/a7-counter-fixes.txt
-rw-r--r-- … 627 … census/round-38/records/a7-counter-fixes2.txt
-rwxr-xr-x … 7528 … tests/fixtures/r38-counter-arms.py
$ grep -n "9b44320" census/round-38/records/a7-counter-fixes.txt
1:# A7 evidence at 9b4432000f51ea28caa21e8f92df23e9a5d9a01e — the three counter first-falsifications, …
```

The old receipt's label names `9b44320…`, the regenerated receipt and the named fixture exist, so
A10's asserted facts are consistent with lane bytes at HEAD.

## P8 — exact append shape and last three lines

Shape as landed (4 physical lines, appended at EOF; the leading blank line separates the block from
line 227, the middle blank line separates the two amendments):

```
<blank>
R39-C1-08 — A10 (appended 2026-10-28 by round 39): <single-line body>
<blank>
R39-C1-09 — A11 (appended 2026-10-28 by round 39): <single-line body>
```

A10 body (448 bytes) states the stale `a7-counter-fixes.txt` pointer, the regenerated
`a7-counter-fixes2.txt`, and `tests/fixtures/r38-counter-arms.py` as the round's instrument; A11 body
(439 bytes) names the superseded sentence, declares the in-place edit superseded, and states the rule
that a frozen sentence is amended only by an appended block naming it. Both bodies are single
physical lines (no wrapping) so the anchor stays one line.

Last three lines (`sed -n '229,231p'`, line 230 is empty):

```
R39-C1-08 — A10 (appended 2026-10-28 by round 39): the A7 block's evidence pointer names `a7-counter-fixes.txt`, whose label reads "at `9b44320`" and therefore predates A7; the regenerated receipt is `a7-counter-fixes2.txt`, and `tests/fixtures/r38-counter-arms.py` — the only fixture that kills the RECEIPT-REV-* guards — is named here as this round's instrument and was absent from A7's instrument table. The frozen sentences stay as filed.

R39-C1-09 — A11 (appended 2026-10-28 by round 39): A0's clarification replaced the frozen rule sentence "must be tighter-only." with "is tighter-only unless stated otherwise." in place; that edit is superseded by this appended amendment, and the rule reads: a frozen sentence is amended only by an appended block that names the superseded sentence, never by rewriting it in place. A0's clarification text stands only as an appended note.
```

That is how an L1 distinguishes the round-39 append from R9's in-place rewrite: append ⇒
`<prefix bytes> + <new bytes>` with `4 0` in numstat and the prefix digest unchanged; R9's rewrite
shows both `+` and `-` lines inside the frozen body (see C4 evidence below).

## Caveats and first-falsifications (advisory)

**C1 — shape deviates from the file's own amendment convention.** Every prior block carries a
`### A<n> — <title> (date, seat)` heading; A10/A11 are flat label lines with no heading:

```
$ grep -o "^### A[0-9]*" census/round-38/preregistration.txt | sort | tr '\n' ' '
### A0 ### A0 ### A1 ### A2 ### A3 ### A4 ### A5 ### A6 ### A7 ### A8
$ grep -n "^### A9\|^### A10\|^### A11" census/round-38/preregistration.txt
(no output)
$ grep -n "A9" census/round-38/preregistration.txt
(no output)
```

Consequences: the two round-39 amendments are invisible to `grep '^### A'`, and the series already
skips A9 (commit cb5737a's message says "A9 random record names" while the file heading it landed is
`### A6 — opaque record filenames…`, so the commit-message numbering and the file numbering already
disagree). Future appends should start with a heading line
`### A12 — <title> (<date>, <seat>)` before the `R39-C1-…` label to restore enumerability.
Recommendation only — I did not write lane bytes.

**C2 — A11's causal attribution does not match history.** The rule rewrite was made by commit
`2843805` ("round-38: tighten-only amendments A0-A2"), which rewrote the freeze text
`None. Any later amendment is appended below with the seat that produced it and must be\n`
`tighter-only.` into `Any amendment below was appended after the wave seat that produced it and is`
`tighter-only unless\nstated otherwise. …`. The block titled "A0 clarification" was added later, by
`4bda5f6`:

```
$ git log --oneline -S"must be tighter-only." -- census/round-38/preregistration.txt
c0b007b round-39: C1 — 14 routed-defect corrections, r39 lesson with Gate/Mistakes, three source rows, gate-registry rows
$ git log --oneline -S"A0 clarification" -- census/round-38/preregistration.txt
4bda5f6 round-38: A8 (docstring token by AST span, whole-token behavioural cases), S244/S245 supersession rows, gate corrections
$ git show 2843805:census/round-38/preregistration.txt | grep -c "A0 clarification"
0
```

So the in-place rewrite came with A0's *amendment*, not with A0's *clarification*; and
`-S"must be tighter-only."` matches only the round-39 commit, i.e. the quoted string never existed
verbatim in the file. A11's quoted sentence is a whitespace-folded reconstruction of the freeze's
line-wrapped `must be` / `tighter-only.` pair (freeze commit `4090ee5`, raw bytes
`m u s t   b e \n t i g h t e r - o …`). The claim's substance (an in-place rewrite occurred and is
superseded) survives; the attribution and the quotation are not byte-faithful.

**C3 — the pre-base prefix already differs from the freeze.** The frozen sentence is absent from the
file at base and at HEAD:

```
$ grep -c "None. Any later amendment" census/round-38/preregistration.txt
0
$ git show 4090ee5:census/round-38/preregistration.txt | sed -n '118,122p'
## Amendments

None. Any later amendment is appended below with the seat that produced it and must be
tighter-only.
```

The original bytes survive only in git history (`4090ee5`, later rewritten by `2843805`).

**C4 — scope of "without altering a frozen sentence".** It holds **relative to the lane base
ed30b7f** (proved byte-exactly in P2/P4) and it is exactly what the append adds. It does **not**
establish that the r38 freeze commit's sentences are intact in the current file — R9's rewrite
happened before the base and the append only supersedes it. Any r39 wording that reads "the r38
prereg is unaltered" would be false; the defensible wording is "the append altered no base byte and
the file differs from its freeze only through the pre-base rewrite that A11 names". The C1 item row
for R39-C1-09 is unaffected: its anchor line `R39-C1-09` occurs once (line 231) and carries
`tighter-only`, `A0`, `superseded`.

**C5 — HEAD moved during the seat.** The first observation was `790d16b`; the counter arm and the
final digest check ran at `2201778e7736af82e7d8a42dec2494f115bf3923`. The r38 prereg bytes are
identical at both readings (`a43e337b…`), so the sibling landings in between did not touch the
subject file.

## Commands run (complete list of material checks)

All from `/home/vgpnk/Projects/shokunin/souji-shokunin` unless prefixed by `cd "$S"`; every path
absolute or relative to the lane root; `$S=/fast/scratch/hyaku/souji-r39/W1ExecPrereg`.

1. `ls -la census/round-39/`, `ls census/`, `ls -la census/round-38/`, `wc -l` on both preregs.
2. `git log --oneline -5`, `git status --porcelain census/round-38/ census/round-39/`, `git log --oneline -6 -- census/round-38/preregistration.txt`.
3. `sha256sum census/round-38/preregistration.txt`, `tail -3 … | cat -A`.
4. `git show ed30b7f…:census/round-38/preregistration.txt | wc -l | sha256sum | sed -n '1,227p' | sed …`.
5. `sed -n '1,227p' census/round-38/preregistration.txt | sha256sum`, `sed -n '224,231p' … | nl -ba -v224`.
6. `git diff --numstat|--stat|-U0 ed30b7f… HEAD -- census/round-38/preregistration.txt`.
7. `grep -n "tighter-only"` on the base and HEAD bytes; `grep -o "^### A[0-9]*"`; `grep -n "^### A9\|^### A10\|^### A11"`; `grep -n "A9"`.
8. `git log --oneline -S"must be tighter-only." | -S"unless stated otherwise" | -S"A0 clarification"`, `git log --oneline --diff-filter=A -- census/round-38/preregistration.txt`.
9. `git show 4090ee5… | sed -n '118,122p'`, `| sed -n '120,121p' | od -c`, `git show 2843805 -- … | grep '^[-+].*tighter'`, `git show 2843805:… | grep -c "A0 clarification"`, `git show cb5737a:… | grep -n "^### A"`.
10. Scratch: `mkdir -p "$S"`, `git show ed30b7f…:… > "$S/base-227.txt"`, `cp "$S/base-227.txt" "$S/append-copy.txt"`, `wc -l`, `sha256sum`, `tail -c 1 | od -An -c`.
11. `cat amend-block.txt >> append-copy.txt`, `sha256sum`, `wc -l`, `sed -n '1,227p' | sha256sum`, `sed -n '228,231p' | cut -c1-90`.
12. `git diff --no-index --numstat base-227.txt append-copy.txt`, `diff -u base-227.txt append-copy.txt | grep '^@@'`, `sha256sum append-copy.txt lane-file`.
13. `file -b amend-block.txt`, `file -b append-copy.txt`, the inline `python3 -B` prefix/UTF-8/control-char parser (quoted in P5), `grep -n ' $'` on lines 228–231, `grep -c $'\r'`.
14. `sed -n '229p' | sha256sum`, `sed -n '231p' | sha256sum`, `| wc -c`.
15. `head -1 … | sed -n '14,15p'` → `$S/two-items.tsv` (first attempt used only the comment header and the counter refused: `REFUSAL USAGE: items … has no header before line 2`, `rc=2`; corrected to include the header row `id\tfile\tanchor\tmust\tmustnot`).
16. Two `c1-counter.py` arms (HEAD, base) quoted in P6; `git rev-parse HEAD`; `git show HEAD:… | sha256sum`.
17. `ls -l` on the A10 artifacts and `grep -n "9b44320" census/round-38/records/a7-counter-fixes.txt`.
18. `mkdir -p .ufo/waves/round-39/w1`; `sed -n '229p' | wc -c`, `sed -n '231p' | wc -c`, `sed -n '120,121p'`.

No mutation of lane bytes, no `git add/commit/checkout/reset`, no `jj` call, no fleet-root write, no
tool install. The scratch tree `/fast/scratch/hyaku/souji-r39/W1ExecPrereg` was removed after the
evidence above was captured (`rm -rf`; `test -e` → `no`), so nothing of this seat remains on disk;
the shared parent `/fast/scratch/hyaku/souji-r39` still exists and is not mine to delete.

## Verdict

The r38 preregistration file accepts R8/R9 as an **appended** amendment set: at HEAD its first 227
lines are byte-identical to the lane base (`sha256 cb47d50f…`), the base→HEAD delta is four added
lines and zero removed lines, and base bytes plus the explicit two-line A10/A11 block reproduce the
landed file exactly (`sha256 a43e337b…`). The appended bytes are plain UTF-8, single-line-per-anchor,
and the frozen C1 counter reads both anchor rows CLOSED at HEAD while reading them OPEN
ANCHOR-ABSENT at the base. Two qualifications for the L1: A11's attribution ("A0's clarification")
and its quoted sentence are not byte-faithful to r38 history, and the append does not undo the
pre-base in-place rewrite of the freeze sentence — it only supersedes it by name.
