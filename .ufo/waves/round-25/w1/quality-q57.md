# Q57 / D6 / R24-M2 drafts — souji round 25, wave 1 (ScribeQualityQ57)

Base: lane HEAD `6deb53561aace9aa14a399f88cf8150da4d4f4bd`. Drafts only; the L1 integrates
them. Nothing in this file edits `corpus/QUALITY.md`, `corpus/lessons/*`, `census/round-24/*`,
`SCORECARD.md`, `LOG.md` or `corpus/README.md`.

---

## 1. Q57 row for `corpus/QUALITY.md` (new `## Round 25 criteria` section)

Append after the Round 24 section, as a single table line (cells contain no unescaped `|`):

```markdown
| id | criterion | applies to | check | motivating evidence |
|---|---|---|---|---|
| Q57 | A slice tally quoted anywhere must name one authoritative file — `census/round-24/records/slice-verdicts.tsv` — and the quote must match a recount of that file, or carry an appended `superseded by` note naming the exact citing record (`file:line`), the authoritative file and the recounted figure. When two slice artifacts disagree, the fix either makes them agree or ships a mapping that both files point to; a mapping named by only one artifact does not close the disagreement. Extends Q55. | lessons, LOG, SCORECARD, README and round evidence that quote a slice class or tally | `grep -F "corpus/lessons/round-25.md" census/round-24/records/slice-verdicts.tsv .ufo/waves/round-24/assimilation/slice-verdicts.tsv` must match both (each table names the mapping); and for every site that quotes a slice tally, a recount of `census/round-24/records/slice-verdicts.tsv` (`grep -v '^#' census/round-24/records/slice-verdicts.tsv \| cut -f2 \| sort \| uniq -c`) must equal the quoted figure, or the quoting record must carry an appended `superseded by` line naming its own `file:line`, the mapping and the recounted figure. Failure witness: at `6deb53561aace9aa14a399f88cf8150da4d4f4bd` neither TSV names the mapping, and `corpus/lessons/round-24.md:240`, `corpus/lessons/round-24.md:232`, `LOG.md:1692` and `SCORECARD.md:181` quote "7 accepted, 1 unverifiable" against a recount of 8 accepted | `corpus/lessons/round-24.md` R24-M22 (line 170); verifier spot-check D6 |
```

Lesson pointer (motivating evidence): R24-M22 — `corpus/lessons/round-24.md:170`.

---

## 2. R24-M2 old→new log line (for `corpus/lessons/round-25.md`)

Written in the round-24 lesson's "In-place change to log" style:

```markdown
**In-place change to log: README :40 F2 status cell (R24-M2 / D4).** Old
(`corpus/README.md:40`, r12 coverage-map row): status cell `frontier, no entry (r12 candidate
deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE
'size\|structure\|sizer'` → 0, 2026-10-19)`, entries cell `—`. New: the same text with the
appended span `; superseded by Round 24 F2 row (:517)` inserted before the status cell's closing
` | — |`; ground and entries cells are unchanged, so the coverage-map counts stay the same. The
marker names the r24 F2 row at `corpus/README.md:517`, not the r24 section heading at `:504`
(the round-24 lesson's R24-M2 row said ":504"; the row is the object the status cell supersedes).
```

## 3. D6 mapping statement (ScoutD6Slice's mapping; for `corpus/lessons/round-25.md`)

Adopted verbatim from ScoutD6Slice's report (Finding 5(a)), under the heading the pointer lines
below reference:

```markdown
### Quarantine-slice vocabulary (D6, R24-M22)

Round-24 quarantine-slice verdicts are keyed by campaign register (lane, id) = (souji, Sxxx),
not lane registry ids. `census/round-24/records/slice-verdicts.tsv` is the gate record.
`.ufo/waves/round-24/assimilation/slice-verdicts.tsv` is the scouts' detail reading, mapped
present / present-via-mirror / present-quote-needs-fix → `accepted`.

The r24 gate vocabulary collapses round 22's two pass classes into one. r22 `present` (span
verbatim in the cited document) and r22 `accepted` (span real in a reachable document; row
repairable by correction or re-cite) are both r24 `accepted`. `unverifiable` and `refused` keep
their round-22 meaning. S126 and S138 are r22 `present` and r24 `accepted` by this collapse, not
by re-grade.

S118 is the only re-grade: r22 `unverifiable` → r24 `accepted`, the flip round 22 named (re-cite
to the Crossref-registered IEEE record or the mirror). Its register class is `unreachable`.

For S123, S131 and S133, detail `present` records digest presence, not the quote predicate (0
matches in the cited payloads). Their `accepted` rests on the wrong-source span in git-worktree(1)
and rename(2).

Tally: r24 8 accepted / 0 present / 0 unverifiable / 0 refused. `census/round-22/attempt2/slice-verdicts.tsv`
stays 5/2/1/0 as round 22's measurement. The "7 accepted, 1 unverifiable" at
round-24.md:232/240, SCORECARD.md:181 and LOG.md:1692 is superseded by 8 accepted (R24-M22).
```

## 4. Pointer comment lines (L1 MAY append so both TSVs name the mapping)

Comment lines; `tools/souji-gate-check.py:157` skips lines starting with `#` (the detail table
is not read by any tool). Appending is append-only and does not change any verdict row.

For `census/round-24/records/slice-verdicts.tsv`:

```text
# r25 D6: one authority = this file; vocabulary map and row-by-row table in corpus/lessons/round-25.md § Quarantine-slice vocabulary
```

For `.ufo/waves/round-24/assimilation/slice-verdicts.tsv`:

```text
# r25 D6: detail evidence, not verdicts; authority is census/round-24/records/slice-verdicts.tsv; map in corpus/lessons/round-25.md § Quarantine-slice vocabulary
```

## 5. Check script (q57-check.sh) — the runnable form of the Q57 check

Final bytes (sha256 `9b3d8f58dac13b0d506de859d1052a493ccdd4d00182e46eaad7a5a434237e3a`):

```bash
#!/usr/bin/env bash
# q57-check.sh ROOT TABLE DETAIL MAPPING SITE...
# TABLE: authoritative id<TAB>class table; DETAIL: the second artifact over the same ids;
# MAPPING: repo path both must name; SITE: file:line (quotes the TABLE tally) or
# file:line:ID (quotes the class of one id). A stale site passes only via an appended
# "superseded by" line naming file:line, MAPPING and, after "recount", the current figure.
set -u
root=$1 table=$2 detail=$3 mapping=$4; shift 4
fail=0
counts=$(grep -v '^#' "$root/$table" | cut -f2 | sort | uniq -c)
echo "recount $table: $(echo "$counts" | awk '{printf "%s%s %s", (NR>1?", ":""), $1, $2}')"
for f in "$table" "$detail"; do
  if grep -qF "$mapping" "$root/$f"; then echo "POINTS $f -> $mapping"; else echo "NO-POINTER $f"; fail=1; fi
done
for site in "$@"; do
  IFS=: read -r file line id <<<"$site"
  text=$(awk -v n="$line" 'NR==n' "$root/$file")
  note=$(grep -F "superseded by" "$root/$file" | grep -F "$file:$line" | grep -F "$mapping" | tail -1)
  after=${note#*recount}
  ok=1 nok=1
  if [ -n "$id" ]; then
    cls=$(awk -F'\t' -v i="$id" '$1==i{print $2}' "$root/$table")
    echo "$text" | grep -qE "(^|[^[:alnum:]-])$cls([^[:alnum:]-]|$)" || ok=0
    for other in present accepted unverifiable refused; do
      [ "$other" = "$cls" ] && continue
      echo "$text" | grep -qE "(^|[^[:alnum:]-])$other([^[:alnum:]-]|$)" && ok=0
    done
    echo "$after" | grep -qE "$id[^[:alnum:]](.*[^[:alnum:]-])?$cls([^[:alnum:]-]|$)" || nok=0
  else
    while read -r n cls; do
      [ -z "$cls" ] && continue
      echo "$text" | grep -qE "(^|[^[:alnum:]])$n $cls" || ok=0
      echo "$after" | grep -qE "(^|[^[:alnum:]])$n $cls" || nok=0
    done <<<"$counts"
  fi
  if [ $ok = 1 ]; then echo "AGREE $site"
  elif [ -n "$note" ] && [ $nok = 1 ]; then echo "SUPERSEDED $site"
  else echo "STALE $site: $(echo "$text" | cut -c1-110)"; fail=1; fi
done
echo "q57=$([ $fail = 0 ] && echo PASS || echo FAIL)"
exit $fail
```

Invocation (the SITE list used for the proofs below):

```bash
bash q57-check.sh <root> \
  census/round-24/records/slice-verdicts.tsv \
  .ufo/waves/round-24/assimilation/slice-verdicts.tsv \
  corpus/lessons/round-25.md \
  corpus/lessons/round-24.md:240 \
  corpus/lessons/round-24.md:232:S118 \
  LOG.md:1692 \
  SCORECARD.md:181
```

Red arm (lane `6deb53561aace9aa14a399f88cf8150da4d4f4bd`, current tip; `rc=1`):

```text
recount census/round-24/records/slice-verdicts.tsv: 8 accepted
NO-POINTER census/round-24/records/slice-verdicts.tsv
NO-POINTER .ufo/waves/round-24/assimilation/slice-verdicts.tsv
STALE corpus/lessons/round-24.md:240: Tally: 7 accepted, 1 unverifiable, 0 rejected (`slice_verdicts=8 slice_total=8`). These are not lane
STALE corpus/lessons/round-24.md:232:S118: | S118 | unverifiable | DOI → IEEE 202, 0 bytes, twice; quote in IEEE staging + PDF mirror; venue cell wrong |
STALE LOG.md:1692: only), 4 rejected. Quarantine slice 8 rows: 7 accepted, 1 unverifiable
STALE SCORECARD.md:181: | assimilation (rides inside C1; no claim slot) | coverage 8 | F2 grounded entries 2 (`ground: F2` lines at `a
q57=FAIL
```

Green arm (scratch copy of the same five files at `6deb535` plus the two pointer lines from §4
and one appended `superseded by` note per site; `rc=0`):

```text
recount census/round-24/records/slice-verdicts.tsv: 8 accepted
POINTS census/round-24/records/slice-verdicts.tsv -> corpus/lessons/round-25.md
POINTS .ufo/waves/round-24/assimilation/slice-verdicts.tsv -> corpus/lessons/round-25.md
SUPERSEDED corpus/lessons/round-24.md:240
SUPERSEDED corpus/lessons/round-24.md:232:S118
SUPERSEDED LOG.md:1692
SUPERSEDED SCORECARD.md:181
q57=PASS
```

Controls (each fails as designed): (a) mapping pointer removed from one TSV → `NO-POINTER`;
(b) authoritative-table class swapped (S114→`refused`) → recount `7 accepted, 1 refused` and all
four sites `STALE`; (c) superseded note without the exact `file:line` → `STALE`; (d) reverting
S118 to `unverifiable` while notes say 8 accepted → tally sites `AGREE` (the quote matches the
reverted table) but the recount line shows the reverted state — the check verifies agreement,
not which side is correct (limitation below).

Known limits (disclose in the lesson):

- The check reads only the class column of the authoritative table and verifies *agreement*,
  not correctness: a reverted authoritative table agrees with the stale quotes. Judging which
  artifact is right stays a human/W2Slice task.
- Row-level sites (`file:line:ID`) pass only via a `superseded by` note when the row text
  retains a token of another class (e.g. the S118 wave-2 note mentions `accepted` while the
  gate cell says `unverifiable`); such a row can never `AGREE`, only `SUPERSEDED`.
- The SITE list is an explicit sweep enumeration, not derived automatically; a new stale quote
  is missed until its site is added.
- The check does not verify that the mapping text itself is consistent with the detail table
  (that is ScoutD6Slice's cross-table check, a separate instrument).
