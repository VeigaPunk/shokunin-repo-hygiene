# RevD4 — routed defect D4 (README slice tally) verified against committed bytes

STATUS: PASS — D4 is **real, exactly as stated, not overstated, not already closed at the lane base**;
the minimal repair is a two-token in-place edit of `corpus/README.md` L440–441, which I proved closes the
frozen K3 predicate; the round's planned repair as worded is **insufficient and self-defeating** unless two
wording constraints are added, and no w1 item actually applies it.

Base measured: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (= lane HEAD this run). No lane file written except
this report; no tool installed or upgraded this run (none needed). Shell scratch
`/var/tmp/souji-r23-RevD4/` removed at end.

## Evidence

**E1 — one-command reproduction (frozen instrument, base revision).**

```
python3 tools/souji-record-agreement.py --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin
```
```
MISMATCH  K3  corpus/README.md:440  tally-disagree  1 present != receipt 2 present
MISMATCH  K3  corpus/README.md:440  tally-disagree  1 refused != receipt 0 refused
...
keys=4 records=3 occurrences=9 mismatches=15
```
rc=1. The two K3 rows are exactly D4.

**E2 — the receipt's own tally (canonical), derived not declared.**

```
git show 1208bfb:.../slice-verdicts.tsv | grep -v '^#' | awk -F'\t' '{print $2}' | sort | uniq -c
      5 accepted
      2 present
      1 unverifiable
```
`refused` = 0 rows. Row-level: S126, S138 = `present`; S118 = `unverifiable`; S114, S123, S124, S131, S133 =
`accepted`; no row carries `refused`. The lesson `corpus/lessons/round-22.md:351-355` agrees verbatim:
"2 **present** (S126; S138), 1 **unverifiable** … **0 refused**."

**E3 — the defective README bytes (base).**

```
git show 1208bfb:corpus/README.md | sed -n '439,442p'
The lane's absent-defect register slice (8 rows) now carries a verdict each —
5 accepted with corrected quotes, 1 present, 1 refused (wrong-source
citation), 1 unverifiable (unreachable DOI). Verdict table:
`../census/round-22/attempt2/slice-verdicts.tsv`.
```
Sweep of every mention at base (`git grep -nE '[0-9]+ (accepted|present|unverifiable|refused)' 1208bfb -- corpus/ LOG.md`):
`corpus/README.md:440,441` and `LOG.md:1509` only. No third occurrence in README.

**E4 — closure proof for the minimal repair** (synthetic repo: `git archive 1208bfb | tar -x`,
`git init`+commit = A `8c26376`, patched+commit = B `6b22123`, instrument copied in read-only; the lane
tree was not touched).

```
A: MISMATCH K3 corpus/README.md:440 ... keys=4 records=3 occurrences=10 mismatches=7
B: keys=4 records=3 occurrences=10 mismatches=4     # zero K3 rows; K1/K2/K4 rows unchanged
```
At B, README reads: `5 accepted with corrected quotes, 2 present, 0 refused, 1 unverifiable / (unreachable DOI).`

**E5 — the planned wording variants, measured against the same predicate** (`TALLY_RE = (\d+) (accepted|present|unverifiable|refused)`):

| variant written into README | K3 result at that rev |
|---|---|
| repaired line **plus** a note quoting the stale pairs ("corrects `1 present`, `1 refused`") | 2 mismatches, `README.md:444` (rev D `e104910`) |
| all four tallies bolded (`5 **accepted**, 2 **present** …`) | `class-absent: no occurrence of accepted,present,unverifiable` (rev E) |
| `2 present / 0 refused` (slash form) | matches both pairs — acceptable |
| `2 **present**` | no match at all |

## Findings

1. **D4 is real and exact.** `corpus/README.md:440-441` (base) states `1 present` and `1 refused`; the receipt
   `census/round-22/attempt2/slice-verdicts.tsv` derives `2 present`, `0 refused`. Both wrong pairs sit on one
   wrapped line, so the spot-check's "1 present … 1 refused" quotation is complete, not a sample. Not overstated.
   Not closed at base (E1 shows the live mismatch at HEAD `1208bfb`).
2. **The wrong parenthetical is a second, smaller error.** `1 refused (wrong-source citation)` attributes to the
   *refused* class a fact that belongs to an *accepted* row: S123 is `accepted` with "correction: quote belongs to
   git-worktree(1), not the payload". The refused class is empty, so the parenthetical must go, not be renumbered.
3. **Minimal repair — file, cell, wording.** `corpus/README.md`, lines 440–441, in place, no other line:
   replace `5 accepted with corrected quotes, 1 present, 1 refused (wrong-source\ncitation), 1 unverifiable`
   with `5 accepted with corrected quotes, 2 present, 0 refused, 1 unverifiable`. Constraints, each proven by E5:
   (a) literal bare `<n> <class>` adjacency — one space, no bold, no slash between them, digit and class word on
   the **same** physical line (a wrap between them kills the pair); (b) `0 refused` must be present as a literal
   pair — "no rows refused" or omitting the class fires `class-absent`; (c) `5 accepted` and `1 unverifiable` must
   be left alone (both already equal the receipt); (d) the stale pairs must not be quoted anywhere in README,
   because K3 — unlike K2 — has **no** "superseded by" escape and scores every occurrence.
4. **Closure command** (isolates K3, independent of K1/K2/K4 noise):
   `python3 tools/souji-record-agreement.py --rev <landed40> --root /home/vgpnk/Projects/shokunin/souji-shokunin | grep -E 'MISMATCH[[:space:]]+K3'`
   → empty output; corroborate with `grep -cE '2 present|0 refused' corpus/README.md` ≥ 2 and the absence of
   `1 refused` anywhere under `corpus/`.
5. **The round's planned repair does not close D4 as written.** `ScribeReadme`
   (`.ufo/waves/round-23/w1-spec.json`) asks for "a `### Round 23 corrections` block that sweeps EVERY mention …
   and … list them with line numbers". Two independent failure modes, both measured (E5): a corrections block that
   *describes* the fix instead of editing L440 leaves the stale pairs in place (K3 keeps both mismatches); and the
   "list them with line numbers" instruction is an invitation to write `1 present` / `1 refused` into README, which
   **adds** the same two mismatches at the new line. The draft must therefore specify: edit L440–441 in place, and
   the optional note must say "one present / one refused" in words, or cite only the corrected pairs.
6. **No w1 item applies the repair.** All 41 items in `w1-spec.json` were enumerated: `ScribeReadme` is the only
   one that touches the content and it is instructed "Do not edit corpus/README.md"; no executor item consumes
   `ScribeReadme.md`. Closure is contingent on the L1 landing the scribe's content in place at a later wave —
   w1 alone cannot move K3. If the landed text is a block appended under a "corrections" heading while L440 stays
   stale, C1's K3 keeps `mismatches>=1` and the round must report it honestly rather than narrow K3.
7. **`LOG.md:1509` is the same error and is deliberately out of D4's repair file.** The frozen K3 scope is
   `corpus/README.md` + `corpus/lessons/round-22.md` (preregistration §C1 K3), and the lesson is already correct
   (`0 refused`). LOG.md is filed historical bytes: preregistration K2 requires the stale occurrence to **still
   exist** and to be named by a later `superseded by` line. So the append-only alternative is already the
   contract — append one LOG line carrying `superseded by` and both tuples (`1 present`, `1 refused`) pointing at
   `census/round-22/attempt2/slice-verdicts.tsv`. That is D5's item, not D4's; the README edit must not touch LOG.
8. **Repair needs no filed-evidence or operator-file edit.** `corpus/README.md` is the lane's live index, owned by
   this lane, and in-place correction is its own precedent (`README.md:216` carries "r18 correction: was a
   `ddb7347` record name never committed" inside the live cell; `README.md:85`, `:369` are correction sections).
   Nothing in `census/`, `.ufo/state/`, `MANIFEST.json` or a sibling lane needs to change.

## Attack log

**ATTACK (K3 is unenforceable on the lesson half of its own record set).** `TALLY_RE` requires a digit, one space,
then the class word. `corpus/lessons/round-22.md` writes its tallies bolded — `5 **accepted**`, `2 **present**`,
`1 **unverifiable**` — so none of those three match; only the line-final `**0 refused**` matches. Mutation proof on
the synthetic repo (repair already applied, so any K3 row would be attributable):

```
lesson mutated 2 **present** -> 7 **present**, 5 **accepted** -> 9 **accepted**   (rev C e104910)
python3 tools/souji-record-agreement.py --rev C ... | grep K3
(no output)   keys=4 records=3 occurrences=10 mismatches=4
```
K3 stayed green with the lesson asserting 9 accepted / 7 present against a receipt holding 5 / 2. Consequences, in
the round's own terms: (i) the claim "the instrument re-derives D4" is true only for README; (ii) `class-absent`
for `accepted`/`present`/`unverifiable` is currently satisfied by README alone, so a README wording that drops any
of those classes red-flags even though the lesson carries them; (iii) a future round could corrupt the lesson's
tally to any value and K3 would not fire. I did not edit the counter — this is reported for the L1's decision. The
cheapest honest fix is to make the lesson write one bare `<n> <class>` pair per class (e.g. a trailing
`5 accepted, 2 present, 1 unverifiable, 0 refused` line) so the same regex sees both records; that is a new
predicate-visible edit to a record K3 already names, so it belongs in the round's declared plan, not in this seat.

## Residual risk and verification gaps

- Closure of D4 depends on bytes that do not exist yet at `1208bfb`: E4 proves the *predicate* closes under the
  minimal edit in a synthetic repo, not that the round will land that text. Findings 5–6 are the live risk.
- `grep` was used only for literal occurrence sweeps; no language server serves these Markdown/data files, so no
  `lsp` reference/definition evidence exists for this item and none is claimed as semantic proof.
- I did not execute `slice-verdicts.tsv`'s claims (S118 DOI, S138 qiita page) — the tally is read from committed
  bytes, and whether those verdicts are *correct* is C3's ground, outside D4.
- K3 counts occurrences only within the two named records; a stale pair introduced in any other file (a lesson, a
  report, `SCORECARD.md`) is invisible to it. Not a defect of D4, but it bounds the "sweep every mention" claim to
  two files.
