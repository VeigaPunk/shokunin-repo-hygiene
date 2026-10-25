# D5 / D6 drafts — souji round 25, wave 1 (ScribeD5D6)

Drafts only. The L1 integrates; no corpus file was edited by this seat. Line numbers are against
lane commit `6e4737eab43d8fde1b85eb9f57023d29046705b4` (round-22.md is 492 lines there; the
round-24 lesson and both slice TSVs are unchanged since `315422b`).

---

## Draft 1 — D5: text to append to `corpus/lessons/round-22.md`

Cover line (for the report and commit message, not for the appended text):
`round-22-verifier-spotcheck.md` is not edited because it is non-author-owned filed evidence —
it was committed by the protocol-shokunin verifier (`4edb25d`, `1208bfb`), not by this lane — and
rewriting an audit of the lane's work would let the audited party alter its audit. The
preregistration routes the note to the lesson and the report instead ("the spot-check file is
non-author-owned; the note lives in the lesson and report instead", prereg D5). The note below
names the spot-check line, so a reader of either file reaches the same disambiguation.

Text to append (verbatim, after the last line of the file):

```markdown

## Round-25 disambiguation — campaign register ids in the slice paragraphs (D5)

Appended by round 25; the filed text above is unchanged.

Every bare `S<id>` in M14 (L297–L299) and in the **Register slice** paragraph (L348–L366) is a
campaign register id — the row id of `absent-defect-register.md` and of the staged
`merge/souji/SOURCES.append.md` — not a lane `corpus/SOURCES.md` id. The same holds for the bare
id in `round-22-verifier-spotcheck.md` L199 and in `LOG.md` L1509 and L1538. When this lesson was
filed the lane registry ended at S114, so only S114 collided; round 23 opened S115–S119 and round
24 opened S120–S123, so three of these bare ids now name a different lane document:

| bare id at | means (campaign register / staged row) | lane row with the same number |
|---|---|---|
| S123 — round-22.md L298, L351, L363; spot-check L199; LOG.md L1509, L1538 | staged own-work row: souji round-2 fixture `r23-trigger-prune.sh`, evidence `lanes/souji/round2/evidence/r23-trigger-prune.out` (sha256 `510722c1…`); register quote is git-worktree(1) SYNOPSIS text | git-worktree(1) § REFS and § DETAILS (opened round 24) |
| S118 — round-22.md L354 | Broder 1997, DOI 10.1109/SEQUEN.1997.666900 | Qiita koseki, `git gc` article |
| S114 — round-22.md L351, L360 | git-prune(1) (`git-repack[1]` markup row) | statx(2), man-pages 6.19 |

S124, S126, S131, S133 and S138 in the same paragraphs are also campaign ids; lane S124 and S125
are opened in round 25 (preregistration C3), at which point L352 and L363 "S124" collide too.
Ids at L331–L343 (S109–S114, S022 under **Gate — attempt 2**) are lane ids, as is "S114
(`struct statx`)" at L336. Resolve every id in this file by document, never by number: the
by-document maps are M16/M21 here and `.ufo/waves/round-24/assimilation/renumber-map.tsv`.
Source of the hazard: round 24 `W2Collisions` F6 and `corpus/lessons/round-24.md` § Id collisions
and renumbering; routed as D5 by `round-24-verifier-spotcheck.md`.
```

---

## Draft 2 — D6: authoritative slice-mapping paragraph for the round-25 lesson

Intended home: `corpus/lessons/round-25.md` (routed fix D6 / R24-M22). It supersedes, append-only,
the S118 row and the tally of `corpus/lessons/round-24.md` § Quarantine-slice verdicts; the
verdict classes themselves are unchanged (preregistration § Assimilation: "the r24
quarantine-slice verdicts stand unchanged").

```markdown
### Quarantine-slice vocabulary — one authority (D6, R24-M22)

**One authority.** The verdict for each of the eight campaign-register slice ids is the class in
`census/round-24/records/slice-verdicts.tsv` (the gate table: the file `souji-gate-check.py
--slice-verdicts` reads and `gate-check-r24-entry.tsv` binds). Every other artifact that states a
slice class or tally — the round-24 detail table, the round-24 lesson table, the verifier
spot-checks, LOG and SCORECARD — is a view of it. A tally quoted anywhere names this file; where
a view disagrees with it, the view is wrong, and the repair either makes the two agree or adds a
mapping that both files point to. Ids are campaign register ids, not lane ids (round-22 D5 note).

**Two tables, two predicates.** `.ufo/waves/round-24/assimilation/slice-verdicts.tsv` (detail
table) is scout evidence, not a verdict. Its `verdict` column answers "are the row's figures
and bytes real?" — for web rows, the span is on the cited page; for own-work rows (S123, S131,
S133) only that the named digests and figures match, which is not the register's quote
predicate (`W2Slice` F3). The gate table answers round 22's class question, with round 22's
definitions (`corpus/lessons/round-22.md` § Register slice): `accepted` = span real, row
repairable by re-citing; `present` = span verbatim at the cited source, no correction;
`refused` = span in no reachable document; `unverifiable` = the source cannot be read at all.

**Class map (detail → gate).**

| detail `verdict` | gate class | rows | why |
|---|---|---|---|
| `present` (own-work) | `accepted` | S123, S131, S133 | digests match, but the register quote is man-page prose (git-worktree(1), rename(2)) absent from the cited payload: wrong-source, fixed by re-citing |
| `present` (web) | `accepted` | S114, S126, S138 | span on the page; S114 needs the `git-repack[1]` markup correction, S126 a 120-char truncation, S138 none stated (see drift below) |
| `present-via-mirror` | `accepted` | S118 | DOI answers 202 with 0 bytes, but the Crossref-registered IEEE record and a PDF mirror carry the span: readable, re-cite |
| `present-quote-needs-fix` | `accepted` | S124 | quote drops `NOREPLACE_new=0(ok)`; corrected quote before any append |
| register class `payload-absent` / "could not be fetched" | — | all | the campaign checker's input label, never a verdict |

**Both tables, row by row** (round 22 for lineage; gate table authoritative).

| id | r22 gate | r24 detail (register → verdict) | r24 gate | evidence status |
|---|---|---|---|---|
| S114 | accepted | payload-absent → present | **accepted** | web, re-fetched r24 |
| S118 | unverifiable | could not be fetched → present-via-mirror | **accepted** | web: Crossref IEEE record + PDF mirror; venue cell wrong |
| S123 | accepted | payload-absent → present | **accepted** | shokuknow own-work, `510722c1` matches; not lane-re-derivable |
| S124 | accepted | payload-absent → present-quote-needs-fix | **accepted** | payload lane-resident (`census/round-22/attempt2/sources/vendor-noreplace-probe.out`) |
| S126 | present | payload-absent → present | **accepted** | web, verbatim prefix |
| S131 | accepted | payload-absent → present | **accepted** | fleet census, `1ac71c4f` matches; not lane-re-derivable |
| S133 | accepted | payload-absent → present | **accepted** | `a53f1e30`/`a4506492` match; 8 mounts, 7 paths |
| S138 | present | payload-absent → present | **accepted** | web, `.md` endpoint line 17 including the 6-line front matter (r22 said "line 11"; that it counts after the front matter is `W2Slice` F6's inference) |

Tally (authority): **8 accepted, 0 present, 0 refused, 0 unverifiable**. The round-24 lesson's
"7 accepted, 1 unverifiable, 0 rejected" predates the S118 re-grade made in the same commit
(`315422b`) and is superseded; "rejected" there means `refused`.

**S118 is `accepted` everywhere.** Gate table: `accepted` since `315422b`. Detail table:
`present-via-mirror`, which maps to `accepted`. Round-24 lesson table row "unverifiable": superseded
by this paragraph. Round-24 verifier spot-check: "accepted (re-graded)" — but its source cell cites
`https://qiita.com/koseki/items/f1af58f1ec1693f0536a`, which is lane S118 (and campaign S138), not
campaign S118 (DOI 10.1109/SEQUEN.1997.666900); its class agrees, its document does not. Round
22's `unverifiable` stays as filed history: round 22 read "source" as the DOI URL; under its own
definition the work was readable elsewhere, which is what the r24 re-grade applies.

**Disclosed drift, not repaired.** S126 and S138 are `present` in round 22 and `accepted` in the
round-24 gate, with the same evidence; under round 22's definitions both are `present` (`W2Slice`
F4). The gate table's header collapses every detail `present*` into `accepted`, which hides
round 22's `present` class instead of mapping to it. The classes stand this round (no claim rests
on them and the gate reads class membership only, `W2Slice` F5); re-classing S126/S138 to
`present` is a decision for a round that re-opens the slice.
```

Pointer lines the L1 MAY append so both TSVs point to the one mapping (comment lines;
`tools/souji-gate-check.py:157` skips lines that start with `#`, and the detail table is not read
by any tool):

```text
# r25 D6: one authority = this file; vocabulary map and row-by-row table in corpus/lessons/round-25.md § Quarantine-slice vocabulary
```

for `census/round-24/records/slice-verdicts.tsv`, and for
`.ufo/waves/round-24/assimilation/slice-verdicts.tsv`:

```text
# r25 D6: detail evidence, not verdicts; authority is census/round-24/records/slice-verdicts.tsv; map in corpus/lessons/round-25.md § Quarantine-slice vocabulary
```
