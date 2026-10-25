## Status

STATUS: PASS — PROJECTION (not a landing): an independent surgery of claim C1 applied in a private clone at
`89e0fceeefcf28db313c94120be6d25e03c60094` yields `markers=0` and an ordered heading triple (18 43 77), and the
projected bytes converge with the landed tip. Two observed defects in the landed shape are recorded below (one
was repaired at `07f83e6`; one is unobserved by every frozen counter and is filed as ATTACK A1).

## Evidence

**Scratch clone** (removed at end of run): `/var/tmp/souji-r26-LabC1AfterSim/repo`
`git clone --no-hardlinks <lane> repo`; `git -C repo rev-parse --show-toplevel` → `/var/tmp/souji-r26-LabC1AfterSim/repo`;
`git checkout --detach 89e0fce…` → `89e0fceeefcf28db313c94120be6d25e03c60094`; tree clean (0 porcelain lines).
Base blob identity: `SCORECARD.md` 254 lines, sha256 `b42a24f019b2dfa5084a5399dd750302e6ce11bf019820a81db78ada05229310`, and
`git show 89e0fce:SCORECARD.md` compared with `cmp` → `base_blob_identical=yes`.
Instrument identity: clone `census/round-26/c1-counter.sh` sha256 `c8dbb76cc4495b814ba0ad6bf24298f8d3f3977069e0ce70c319a1130c16bf5a`
equals `git show 89e0fce:census/round-26/c1-counter.sh | sha256sum` (same digest) — the labeled instrument is the committed one.

**Do-nothing control (base bytes untouched), inside the clone:**
```
$ bash census/round-26/c1-counter.sh     # on the 89e0fce blob
markers=2
headings=17 175 231
```
**PROJECTION — post-edit, inside the same clone:**
```
$ bash census/round-26/c1-counter.sh
markers=0
headings=18 43 77
rc=0
```
Independent re-derivation (not the counter) on the projected file:
`grep -cE '^(Insert the table below directly above|Optional same-landing correction)'` → `0`;
`awk '/^### Round (23|24|25) measurements/{printf "%s ", NR} END{print ""}'` → `18 43 77 `.
Exactly three headings; n25=18 < n24=43 < n23=77 → K2 order holds. Projected file: 233 lines,
sha256 `960ec78bd647457ee62a2e1047117b9967d45363a18c8e4e71949bbf922f8d18`. `git -C repo status --porcelain` → ` M SCORECARD.md` only.

**Exact awk used** (span concatenation per amendment 2's 7-span order; no `sed`):
```awk
awk -v note="r23; r26 note (2026-10-25): since r24 the digest binds the labelled committed file bytes and that label in argv, not the executed program" '
{ a[NR]=$0 }
END {
  for (i=1;   i<=16;  i++) print a[i]      # span 1
  print ""
  for (i=231; i<=254; i++) print a[i]      # span 2: Round 25 block + corrections + superseded-by lines
  print ""
  for (i=175; i<=207; i++) print a[i]      # span 3: Round 24 payload (fenced content only)
  print ""
  for (i=17;  i<=62;  i++) print a[i]      # span 4: Round 23 block
  for (i=63;  i<=94;  i++) {               # span 5: Capabilities + payload rows + R3 note
    if (i==92)      { print a[i] " " note }
    else if (i==93) { print a[i]; print a[213]; print a[214] }
    else            { print a[i] }
  }
  for (i=95;  i<=137; i++) { print a[i]; if (i==136) { print a[225]; print a[226] } }   # span 6
  for (i=138; i<=169; i++) print a[i]      # span 7 (Saturation .. None.); scaffold 170-230 deleted
}' SCORECARD.base > SCORECARD.new
```
Span verification against base bytes (verbatim containment in the projection): spans `1:1-16`, `2:231-254`,
`3:175-207`, `4:17-62`, `6:95-137`, `7:138-169` → `present_verbatim=true`; `5:63-94` → `false` by design, and its
isolated diff is exactly the sanctioned content: 1 modified line (R3 note appended to the `blob-bound receipts (r23)`
row) + 2 added lines (base 213, 214 verbatim), nothing else.

**Convergence check (read-only `git show` against the lane).** Projection vs `a529c76` (first landing):
4 hunks — (i) my extra blank after span 1, (ii) `a529c76` inserts `---` + blank before the Round 24 heading,
(iii) R3 note form (in-cell vs 5th cell), (iv) `a529c76` inserts a blank between the r25 and r24 bullets.
Projection vs tip (`ba8b54b`, `SCORECARD.md` byte-identical at the read-time tip `c594901`, sha256
`b659efc68303b9b20f371b9ee6b77a86a2eb11cdaf81a4a8fddf1680ca14286a`): 5 hunks = the same four plus the 26-line `### Round 26 append-only
corrections` EOF block (`SCORECARD.md:237-261`), which is an append outside C1's span list. Counter over the tip
blob in a second scratch copy: `markers=0`, `headings=17 44 78 `, rc 0.

## Findings

1. **PROJECTION satisfies the frozen counters.** Post-edit `markers=0` (K1 after-value) and exactly three
   `### Round {23,24,25} measurements` headings ordered n25 < n24 < n23 (K2), with all seven amendment-2 spans
   present and the whole scaffold region (base 170-230) absent. Location: projected `SCORECARD.md` in the clone;
   base rev `89e0fce`, counter `census/round-26/c1-counter.sh`.
2. **`a529c76` dropped both required r24 capability rows.** At `a529c76`, the `## Capabilities` table ends at
   line 154 `| record agreement audit (r23) | …`; `grep -c 'debris census (r24)'` → 0 and
   `'coverage-map agreement (r24)'` → 0. Amendment 2 item 5 requires exactly those two rows verbatim from base
   lines 213-214. Repaired at `07f83e6` (rows now `SCORECARD.md:155-156` at `HEAD`). My projection carried them
   from the start, which is how the omission surfaced.
3. **The scaffold separator survived the landing.** `a529c76:SCORECARD.md:42` and `HEAD:SCORECARD.md:42` are
   byte-identical to base line 229 `---` (`od -c` → `- - - \n`), the separator amendment 2 lists among deleted
   scaffold content ("instruction lines, fences, separator"). No frozen counter and no protected span observes it.
4. **R3 note placement differs from the landed shape.** Landed appends it as a fifth cell on a four-column table
   (`HEAD:SCORECARD.md:153` → `| r23 | *(R3 dated 2026-10-25: …)*`); the projection appends inside the row's last
   cell. Both discharge "append a dated note to the row"; the landed 5-cell row is schema-inconsistent but
   counter-inert.
5. **Both shapes satisfy "r24 table above the r23 heading"**, but by different separators: projection has a blank
   line after span 1 (headings 18/43/77), landed has none (17/44/78). Order holds either way; K2 compares
   positions, not absolute values.

## Attack log

ATTACK A1 — **C1's frozen counters cannot observe the payload they claim to integrate.** Running the committed
counter over the `a529c76` blob prints `markers=0` / `headings=17 44 78 ` with rc 0 while both required r24
capability rows are absent (Finding 2). K1 counts only the two scaffold marker lines; K2 counts only heading
positions; amendment 2's span check covers the base spans *and* requires scaffold 170-230 deleted — the payload
lines live inside 170-230 (base 213-214, 225-226), so nothing in the frozen rule requires them to reappear. A
surgery that deletes the scaffold and pastes back only the Round 24 table heading greens C1. Demonstrated, not
hypothetical: it is exactly the `a529c76` state. No predicate change is proposed after data; the landing gate
must byte-check base 213-214 and 225-226 verbatim in the post-edit file (the wave's own diff at `07f83e6` did
this by hand).

No other attack; the instrument itself is the committed one (digest above).
