# SwarmReviewer12 — S063 re-open: git-gc quotes in `jj-keep-ref-expiry.md` Gate

Seat: read-only reviewer, souji round 30 attempt 1 wave 2. Item: re-open S063 sources (live URL + v2.56.0 snapshot), verify each S063 quote in `corpus/knowledge/jj-keep-ref-expiry.md` `## Gate` against both, judge scope (held row vs new row). Prereg + amendments read first; SOURCES-CONTRACT-v1 (fleet `/home/vgpnk/Projects/shokunin/.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`) read for the scope/used-by rules. No tool installed or updated this run.

## Status

STATUS: PASS — the attack ran to completion: both sources opened this run, all three S063 Gate quotes mechanically verified against the snapshot bytes (whitespace-normalized substring match) and checked word-by-word against the live page; every attacked item HOLDS; no new row was needed.

## Evidence

Snapshot integrity (receipt [1] in `.ufo/waves/round-30/w2/SwarmReviewer12-s063-receipts.txt`):
- `census/round-30/sources/git-gc.adoc` is byte-identical (`cmp` IDENTICAL) to `raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc` fetched this run; sha256 `e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c`, 6744 bytes — equal to the entry's `verified-at:` line, `census/round-30/sources/SHA256SUMS:4`, and `census/round-30/records/fetch-receipts.tsv:5` (HTTP 200, 2026-10-26T04:43:49Z).
- Live page https://git-scm.com/docs/git-gc opened this run: banner "git-gc last updated in 2.52.0" and "2.53.0 → 2.56.0 no changes" — exactly the access record on row S063 (`corpus/SOURCES.md:84`), so live text and v2.56.0 snapshot are the same doc content.

Per-quote verification (mechanical: normalized-substring FOUND + word count + pipe check; spans read raw):

| Gate quote (S063) | Cited | Snapshot span | Snapshot | Live page | Words | Verdict |
|---|---|---|---|---|---|---|
| "removing unreachable objects which may have been created from prior invocations of 'git add'" | DESCRIPTION, lines 18-20 | 18-19 (de-wrapped join; cited range contains it) | FOUND, verbatim | present; `'git add'` renders as emphasis `*git add*` | 14 | HOLDS |
| "Prune loose objects older than date (default is 2 weeks ago, overridable by the config variable `gc.pruneExpire`)." | OPTIONS `--prune`, lines 81-83 | 82-83 (81 is the `--prune=<date>::` header) | FOUND, verbatim | exact, incl. backticks | 17 | HOLDS |
| "Any object with modification time newer than the `--prune` date is kept, along with everything reachable from it." | NOTES, lines 159-161 | 160-161 (159 blank; adoc list marker `. ` excluded) | FOUND, verbatim | same words as list item "1." | 18 | HOLDS |

All three ≤ 25 words, no pipe character, copied from bytes opened this run. The row's anchor quote also re-verified in the snapshot: "it will keep not only objects referenced by your current set of branches and tags, but also objects referenced by the index, remote-tracking branches, reflogs" (`git-gc.adoc:142-144`, 25 words) — the same sentence round-17 recorded (`corpus/lessons/round-17.md:44`) and the live page carries in NOTES.

## Findings

1. **[note, no action] Quote 1's quote-mark layer.** `'git add'` is verbatim against the adoc snapshot (`git-gc.adoc:19`); the live page renders the same two words as emphasis (`*git add*`) because asciidoc renders `'word'` as `<em>`. Wording identical; the Gate line names both the URL and the snapshot, and the snapshot is the hashed artifact. Not a mismatch.
2. **[observation, no action] Body point 5 mildly generalizes quote 1.** The DESCRIPTION sentence qualifies its unreachable objects "created from prior invocations of 'git add'" (`git-gc.adoc:18-19`); the entry's body says "git gc removes unreachable objects [S063, lines 18-20]". The generalization is carried by the paired `--prune` and NOTES quotes plus the row's recorded lesson, and the entry labels the fixture application `[INFERENCE]` ("Object removal is not measured"). No overreach.
3. **[observation, no action] The load-bearing refs-are-roots step is not re-quoted in the Gate.** "A keep ref is a ref, so the commit it names stays reachable" rests on S063's recorded `teaches` cell — "once a ref is gone its objects become prunable after the prune date" (`corpus/SOURCES.md:84`) — whose grounding quote is NOTES first paragraph, verified verbatim in round 17 (13/13 per `corpus/lessons/round-17.md:46`) and re-verified in the snapshot this run (`git-gc.adoc:142-144`). The registry row is the record of that fact; acceptable under contract Rule 1.
4. **[observation, benign] The `--prune`-default fact overlaps held row S002.** S002 (same URL, `corpus/SOURCES.md:23`) records "loose objects 2 weeks" under scope "git 2.55.0 grace periods on git's own deletions", anchored at § OPTIONS --prune. The entry cites S063 for the same fact; `corpus/lessons/round-30.md:18` discloses the overlap and records the flip condition ("Flip: land a row only for a git-gc claim `S002`/`S063` exclude"). S002 is version-pinned to the installed 2.55.0 man page and cannot carry the v2.56.0 adoc bytes the Gate hashes, so S063 is the correct vehicle. Benign.
5. **[hygiene, verified] Registry append-only respected.** S063's `used-by` change is logged old→new at `corpus/lessons/round-30.md:35` (and S054's at :34) per contract Rule 2 ("Only `status`, `recheck` and `used-by` change in place"); `corpus/lessons/round-30.md:37` records that no `status` or `recheck` cell changed. S063's `used-by` now names the entry (`corpus/SOURCES.md:84`).

## Attack log

1. **Quote 1 (DESCRIPTION, cited lines 18-20)** — attacked: byte presence in snapshot (FOUND, normalized), live-page presence (present, emphasis rendering), word count 14, pipe rule, line span (quote on 18-19; cited range containing). **HOLDS.**
2. **Quote 2 (OPTIONS `--prune`, cited lines 81-83)** — attacked: byte presence (FOUND), live-page exactness incl. `gc.pruneExpire` backticks, word count 17, pipe rule, span (82-83 under the 81 header). **HOLDS.**
3. **Quote 3 (NOTES, cited lines 159-161)** — attacked: byte presence (FOUND), live-page presence (same words, list marker differs), word count 18, pipe rule, span (160-161). **HOLDS.**
4. **Scope: DESCRIPTION citation** — attack: "the quote is gc's task list, not which refs keep objects alive". Fails: the row is `git-gc(1) reachability`; removal of unreachable objects is the complement of the keep-alive rule and the row's own `teaches` cell records the consequence ("prunable after the prune date"); the "not jj's own gc" exclusion is respected — every jj-side claim cites S054/S220/S221, S063 only git-side behavior. **Within scope; HOLDS.**
5. **Scope: `--prune`-default citation** — attack: "the 2-week default is a grace-period fact; S063's scope is 'which refs keep objects alive during gc; not jj's own gc' (`corpus/SOURCES.md:84`), so S002 should carry it or a new row was needed". Fails: (i) the row's `teaches` cell itself invokes "the prune date"; the citation defines that date's default from the same manual; (ii) the NOTES section the row anchors references the same `--prune` date (`git-gc.adoc:160-161`); (iii) S002 is pinned to the 2.55.0 installed man page and cannot carry the v2.56.0 adoc bytes the Gate hashes (verified-at, A2/E4 regime); (iv) a new row would repeat S063's url+scope (census E04 duplicate, exit 1) or re-scope grace periods S002 already covers; (v) the frozen prereg itself lists "git-gc docs as needed" among C3's source classes (`census/round-30/records/preregistration.txt:9`), and the reuse decision with its flip condition was recorded at `corpus/lessons/round-30.md:18` ("The raw adoc at the release in use is a locator upgrade to `S063`, not a distinct scope"). **Within scope; no new row needed; HOLDS.**
6. **Snapshot provenance** — attack: "the snapshot may not be what it claims (Documentation/git-gc.adoc at v2.56.0)". Fails: `cmp` IDENTICAL against the live tag fetch; sha256 matches the entry's `verified-at:` line, `sources/SHA256SUMS:4`, `fetch-receipts.tsv:5`; byte size 6744 matches the lesson's "6 744 bytes" (`corpus/lessons/round-30.md:18`). **HOLDS.**
7. **Frozen-sourcing constraint** — attack: "prereg says 'sourced from rows opened this round'; S063 was opened 2026-10-20". Fails: the prereg's own parenthetical enumerates "git-gc docs as needed" (and "jj source at tag v0.45.1" = held S054) as source classes, so it anticipates held-row reuse; the bytes were re-fetched live this round (HTTP 200, `fetch-receipts.tsv:5`) and the re-open is recorded with URL, access date and located quotes at `corpus/lessons/round-30.md:18`. **No violation; HOLDS.**

## Deliveries

- Report: `.ufo/waves/round-30/w2/SwarmReviewer12.md` (this file)
- Receipts: `.ufo/waves/round-30/w2/SwarmReviewer12-s063-receipts.txt`
- Scratch `/fast/scratch/hyaku/souji-r30/SwarmReviewer12/` removed after copying. No lane file outside `.ufo/waves/round-30/w2/` written; no git/jj mutation; no signals.
