STATUS: DONE — LOG.md is a single h1 + 34 h2 (27 round sections, 7 non-round) blocked by h2; only r1–r11 and r17 are single-section; corrections are separate appended h2 entries, never edits; r17 = 944–946.

# Scout — LOG.md heading shapes and round-section extraction

Scope: `LOG.md` at `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` (lane root
`/home/vgpnk/Projects/shokunin/souji-shokunin`). Read-only; no installs, no writes
outside this report.

## Evidence base

Commands run and observed output:

| command | output |
|---|---|
| `wc -l LOG.md` | `946` (57137 bytes; sha256 `1e41c9c5367a410912dff23e5c5381ea11677f1a7c59b731713182d6b5571328`) |
| `git rev-parse HEAD` | `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` (HEAD == base) |
| `git cat-file -s b576341:LOG.md` | `57137` |
| `git cat-file -p b576341:LOG.md \| sha256sum` | `1e41c9c5…b5571328  -` (identical to worktree `sha256sum LOG.md`) |
| `git diff --numstat b576341 -- LOG.md` | empty (REV bytes == worktree bytes) |
| `git log --numstat --format='commit %h' -- LOG.md` | 32 commits, every numstat row `N 0 LOG.md` — zero deletions in the file's whole git history |
| grep `^#+[^# ]`, `^={3,}$`, `^-{3,}$`, `\r$` on LOG.md | no matches (no malformed/setext headings, no CRLF) |
| fence scan (`^````) | 0 fence lines, so no heading can be fence-quoted |

Python audit (regex `^#{1,6}\s` + fence toggle) over the 946 lines: 37 headings total
= 1 h1 (`LOG.md:1`), 34 h2, 2 h3 (`LOG.md:657`, `LOG.md:716`), 0 headings inside
fences, 0 h4–h6, no wrapped heading lines (lengths 45–127 chars), only non-ASCII
character in any heading is U+2014 (`—`).

## F1. Exact heading shape per round (r1..r17)

Every round block is an h2 line of the exact form

```
## <YYYY-MM-DD> — round <N><optional space + free-text suffix>
```

with one ASCII space either side of U+2014; strict regex
`^## \d{4}-\d{2}-\d{2} — round \d+\b` matches all 27 round h2 lines and none of the
7 non-round ones. There is **no** `r<N>`-style round heading and no heading that
omits the date.

| round | h2 line(s) — exact heading text |
|---|---|
| r1 | 34 `## 2026-10-18 — round 1 admitted (claims: coverage + calibration)` |
| r2 | 92 `## 2026-10-18 — round 2 admitted (claim: operability)` |
| r3 | 122 `## 2026-10-18 — round 3 admitted (claims: coverage + calibration) — PROBATION GATE CLEARED` |
| r4 | 162 `## 2026-10-18 — round 4 admitted AMENDED (operator withdrew the obsidian claim)` |
| r5 | 192 `## 2026-10-18 — round 5 admitted (verification round; 3 material defects found and fixed)` |
| r6 | 219 `## 2026-10-18 — round 6 REJECTED as a round; deliverables completed by parent` |
| r7 | 246 `## 2026-10-18 — round 7 REJECTED as a round (2/3); receipts deny every candidate` |
| r8 | 267 `## 2026-10-18 — round 8 admitted (all 3 claims)` |
| r9 | 298 `## 2026-10-18 — round 9 REJECTED (O1 NOT-MET); tools patched but uncertified` |
| r10 | 332 `## 2026-10-18 — round 10 REJECTED on O1 (3 residual census-contract); merge installed` |
| r11 | 349 `## 2026-10-18 — round 11 closed (operator: finish + push before reboot)` |
| r12 | 453 `## 2026-10-19 — round 12 (kaika campaign; steered r12, goal cancelled after r11)` · 493 `## 2026-10-19 — round 12 closing note (measured commit)` · 503 `## 2026-10-19 — round 12 post-review fixes (orchestrator adjudication)` |
| r13 | 514 `## 2026-10-20 — round 13: bounded operations, declared-evidence integrity, F2 census` · 562 `## 2026-10-20 — round 13 measured closing evidence` · 605 `## 2026-10-20 — round 13 ending source census` |
| r14 | 618 `## 2026-10-20 — round 14: digest-bound retention and credential-store census fence` · 671 `## 2026-10-20 — round 14 measured closure evidence` (+ h3 657, 716) |
| r15 | 726 `## 2026-10-20 — round 15: repair rejected-harmed configuration support first` · 770 `## 2026-10-20 — round 15 operator-stopped landing; claims unprovable` |
| r16 | 817 `## 2026-10-20 — round 16 correction: round 15 landed a census that does not parse` · 836 `## 2026-10-20 — round 16: parsing value/effect-aware census (C1), landing gate (C2), r15 checker executed (R4), seat audit (R5)` · 886 `## 2026-10-20 — round 16 wave-2 corrections (appended; the entry above stands as written)` · 908 `## 2026-10-20 — round 16 correction: the uncarried wave-2 count is 29, not 28` · 927 `## 2026-10-20 — round 16 correction: pre-harm fails R15CFG-03 and R15CFG-18, not only refusal/safety cases` |
| r17 | 944 `## 2026-10-20 — round 17 (souji L1, hyaku phase 2): census hygiene, reproducible seat audit, jj-colocated receipts` |

Non-round h2 (7, all parse-fails by design): 3 mint, 78 obsidian-cli probe,
154 operator routing directive, 292 operator routing amendment 2, 324 operator
scheduling amendments 3-4, 362 operator sweep, 439 operator decisions.

Dates are wall-clock write dates, not round-specific: 2026-10-18 covers mint, r1–r11
and three operator entries; 2026-10-19 covers the sweeps and all r12 entries;
2026-10-20 covers r13–r17. A date prefix therefore identifies nothing by itself.

## F2. "Exactly one section per round?" — No.

Measured h2-section counts (by heading's round slot): r1–r11 = 1 each; **r12 = 3,
r13 = 3, r14 = 2 (+2 h3 inside), r15 = 2, r16 = 5, r17 = 1**. Only r1–r11 and r17
are single-section. A tool that assumes one section per round silently drops
`LOG.md:493,503` (r12 closure + post-review), `562,605` (r13 evidence), `770` (r15
operator stop) and all four r16 correction entries.

The h3s (`### Round 14 historical-runner provenance correction` at 657,
`### Round 14 ending contract census` at 716) are sub-entries **inside** r14's
618–670 and 671–725 h2 sections; they do not open new h2 sections and must not
terminate one.

## F3. Where append-only corrections live

`LOG.md:1` declares the file append-only, and that is literal: 32 commits touch
LOG.md and every one adds lines with **0 deletions**. Corrections are therefore new
h2 entries, never in-place edits. Two placements exist:

1. **Same round, appended after the entry** — r12 closing note/post-review
   (`493`, `503`), r13 closing evidence (`562`, `605`), r15 operator-stopped landing
   (`770`), r14 h3 sub-entries (`657`, `716`).
2. **A later round's region, carrying the writing round's slot** — r16's correction
   of r15 is `LOG.md:817`, whose heading slot is **16** (`round 16 correction:
   round 15 …`), physically the first entry of the 817–943 r16 region; r16's own
   later corrections are `886` ("wave-2 corrections (appended; the entry above
   stands as written)"), `908` and `927`, which cite their targets by line:
   `LOG.md:902-903` and `LOG.md:858-859`. Body-only forwards also exist
   (`LOG.md:906` "routed to round 17").

Consequence: "round N's LOG section" (heading slot == N) is the record *as N wrote
it plus N's own post-fixes*; it excludes later corrections of N. The corrected
record for N < 17 must additionally pull later sections that name `round N` or
whose `LOG.md:<line>` anchors land in N's ranges. At `b576341`, the only such
later-section correction is 817 → r15 (plus the 906 body mention of r17).

`LOG.md:<line>` anchors are load-bearing across the corpus — `QUALITY.md:29,32,38`
cite `LOG.md:58`, `:373`, `:381`, `:403`, `:421`; `corpus/lessons/round-17.md:15`
cites `LOG.md:858-859`/`:902-903`; the r17 spotcheck cites `LOG.md:916`. All were
spot-checked and resolve to the cited content; they stay valid only while appends
do not reflow earlier lines (verified: no deletions ever).

## F4. The rule a tool should use to extract "round N's LOG section"

Tested implementation:

```python
ROUND_HEAD = re.compile(r'^## (\d{4}-\d{2}-\d{2}) — round (\d+)\b')
H2 = re.compile(r'^## ')

def sections(lines):
    starts = [i for i, l in enumerate(lines, 1) if H2.match(l)]
    for k, s in enumerate(starts):
        e = starts[k + 1] - 1 if k + 1 < len(starts) else len(lines)  # EOF clamp
        yield s, e, lines[s - 1]

def round_sections(lines, n):
    return [(s, e) for s, e, h in sections(lines)
            if (m := ROUND_HEAD.match(h)) and int(m.group(2)) == n]
```

Rules, in order:

1. **Section boundary is h2 only.** An h3 (`657`, `716`) never ends an h2 section;
   h1 occurs once (`LOG.md:1`) and never recurs.
2. **Take the round number from the anchored slot** immediately after
   `## <date> — `. Never `re.search(r'round N')` over the heading (see F5) and
   never the `rN` abbreviations or `R15CFG-*` ids that appear inside headings.
3. **Union all sections with slot == N, report each range.** They are contiguous
   among h2 sections at `b576341` (verified for all 17 rounds), but contiguity
   should be asserted, not assumed.
4. **The last section ends at EOF** (`len(lines)`), not "before the next h2". The
   r17 body is a single 1360-char line and the file ends newline-terminated with no
   trailing separator line.
5. **Absent round ⇒ empty result.** At `b576341` round 18 has no section. For a
   pre-landing REV this must yield zero lines scanned (no findings), not exit 2;
   the C2 counting rule "changed gate `--rev b576341 --round 18` findings before →
   0" depends on it.
6. **Sanity assertions against silent drift**: 34 h2 total, 27 round h2, 7
   non-round h2 at lines `3,78,154,292,324,362,439`; per-round count vector
   `[1,1,1,1,1,1,1,1,1,1,1,3,3,2,2,5,1]`; file is LF-only. Fail loudly (exit 2)
   when a future commit breaks these instead of extracting nonsense.
7. **Read REV bytes, not the worktree** (`git cat-file -p <rev>:LOG.md`). Equal
   today (sha256 match), but the gate contract is "at REV".

Expected extraction at `b576341` (inclusive ranges):

```
r1  34-77      r2  92-121     r3  122-153    r4  162-191    r5  192-218
r6  219-245    r7  246-266    r8  267-291    r9  298-323    r10 332-348
r11 349-361
r12 453-492, 493-502, 503-513
r13 514-561, 562-604, 605-617
r14 618-670, 671-725
r15 726-769, 770-816
r16 817-835, 836-885, 886-907, 908-926, 927-943
r17 944-946
r18 absent
```

## F5. Traps that break cheaper implementations (all observed)

- **Substring `round 15` in headings returns 3 lines**, not 2: 726, 770, **817**
  (`round 16 correction: round 15 landed…`). The anchored slot returns exactly
  `[726, 770]`.
- **Substring `round 17` over the whole file** hits `LOG.md:906`, which lives in the
  r16 region ("routed to round 17"), so body-text scanning for a round number is
  not a section selector either.
- **Abbreviations inside headings**: `r12` (453), `r15 checker` (836),
  `R15CFG-03 / R15CFG-18` (927) — all look like round references and none is the
  section's round.
- **Dates repeat** and are wall-clock; `2026-10-20` alone covers five rounds.
- **Heading length up to 127 chars** (836); do not cap at ~100 or split on width.
- No fences, no setext underlines, no CRLF, no h4–h6 today — but a parser should
  still keep the fence guard (`HEADING_RE = ^#{1,6}\s` is the repo's existing
  convention, cf. `tools/souji-landing-gate.py:101`) because `LOG.md` is
  append-only and future entries may quote markdown.

## F6. Round-17 section line range

**`LOG.md:944-946`** inclusive: heading 944 (114 chars), blank 945, body 946
(1360 chars, one physical line, ends `…Author verdicts only; the non-author
closure decides.`), then EOF. One h2, zero h3. Note the body line is long enough
that line-oriented tooling must not assume heading+short paragraph, and a scanner
must include line 946 when collecting path tokens (`census/round-17/
gate-replays-4f48343.json`, `tests/vault/vadv54-run/p/p6repo/.git`,
`.ufo/quarantine/round-17/…`, `corpus/lessons/round-17.md` all sit on it).

## F7. Consumer notes for C2 `LG-DANGLING-PTR`

- The landing gate does not read `LOG.md` today: grep for `LOG\.md` in
  `tools/souji-landing-gate.py` returns nothing (it parses
  `corpus/lessons/round-N.md` and `.ufo/waves/round-N/**` only). The spec's
  "LOG.md's round-N section" is therefore new code; the F4 rule is the interface.
- With slot extraction, `--round 17` scans 944-946 only. `LOG.md:916`
  (`census/round-17/gate-replays-ddb7347.json`, the R2 dangling pointer) sits in
  r16's 908–926, so a round-17 scan will not see it. That is consistent with the
  C2 contract (round-N section only) but the token inventory must not assume a
  round-17 scan covers r16 correction prose — R2's fix is a separate routed item.
- Source files checked for an existing documented convention (none found):
  `SKILL.md`, `SCORECARD.md`, `PROVINCE.md`, `corpus/QUALITY.md`,
  `corpus/README.md`, `tools/souji-verify.sh`, `tools/souji-seat-audit.py`,
  `tools/souji-census.sh`, `tools/souji-landing-gate.py`. Only `LOG.md:<line>`
  anchors exist (QUALITY Q5/Q7/Q8/Q14), never a section-extraction rule.

## Verdict

**Holds** for the asked facts: heading shapes, per-round section counts, correction
placement, extraction rule, and the r17 range are all measured at `b576341` and
reproduce deterministically. **Partial** on provenance only: the rule is derived and
tested here, not specified anywhere in the tree I was allowed to read.

Smallest fix (for L1, not applied): in the C2 gate skeleton, add
`ROUND_HEAD = r'^## \d{4}-\d{2}-\d{2} — round (\d+)\b'`, select all h2 sections
whose slot == N, end each at the next h2 or EOF, return `[]` when N is absent, and
assert the 34/27/7 and count-vector invariants. That is the whole interface; no
line-offset constants beyond the sanity checks, so round 18's appended section is
picked up automatically.

Confidence: high on every line number, count and regex result above (each was
recomputed from bytes, and REV bytes were hash-compared to the worktree). Remaining
unknowns: none material for this question; I did not scan tools or corpus beyond
the nine named files, so a hypothetical undocumented parser elsewhere cannot be
excluded.

No tools installed or upgraded; no commits, no git writes, no `jj`.
