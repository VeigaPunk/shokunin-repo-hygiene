# ScoutAuditExistingCases — V-READ-ROOT over existing read/grep/glob cases (r21 w1)

STATUS: OK (source-only; no code executed, no installs)

Seat: SoujiR21.ScoutAuditExistingCases-3 · base audited: 544c8358039a07e8b45e6db72312da5c8d965275
(sources verified byte-identical at claim base 6ff3413bba9c8430c3b0bc4d2052e21d0407183f:
`git diff --stat` between the two revs touches only `.ufo/waves/round-21/preregistration.txt`
and `census/round-21/source-census-start.txt`).
Method: `git show <rev>:<file>` for all three sources; static rule application only.
No tool installs (none needed).

## Committed oracle reading (rules applied, per prereg C1)

For tool ∈ {read, grep, glob}, per call, flag at most once (minor):
- Extract target: read → arg minus trailing selector (`:N`, `:N-M`, `:raw`, comma lists);
  grep → text after ` @ `; glob → arg. `;`-multi-paths: each component judged.
- NOT flagged: target truncated (`…` in the path portion); target absolute, `~`, or URI
  (`^[a-z][a-z0-9+.-]*://`).
- FLAG: fully visible RELATIVE target whose lexical fleet-root resolution is outside the
  lane; or grep with complete args and **no visible path** (pattern-only → implicit cwd).
- Committed interpretation for the ambiguity below: a grep whose rendered args contain a
  fully visible path in ANY separator form (` in ` as in the selftest renders, not only
  `@ `) is NOT implicit; the absolute-path carve-out wins. Basis: C1 headline "implicit
  fleet-root-namespace reads" + "absolute paths … are never V-READ-ROOT".

## Table A — built-in selftest of tools/souji-seat-audit.py (9 cases; grep of source shows
exactly these read/grep/glob renders: lines 503, 507, 509, 516, 535, 540, 541, 542, 543)

lane = /home/u/P/f/lane, fleet = /home/u/P/f. Every selftest case asserts an exact sorted
(class, severity) list (`got == sorted(want)`), so any added row breaks it.

| case (line) | tool | args | expected flags | new V-READ-ROOT? | breaks? |
|---|---|---|---|---|---|
| clean-read (503) | read | `/home/u/P/f/lane/SKILL.md` | [] | no (absolute) | no |
| sweep (507) | read | `/home/u/P/f/lane/census/operator-sweep-20261019/a.tsv` | [(V-SURFACE, major)] | no (absolute) | no |
| rules-ok (509) | read | `/home/u/.omp/agent/RULES.md` | [] | no (absolute) | no |
| recursive-grep-tool (516) | grep | `foo in /home/u/P/f/lane` | [(V-RECURSIVE, minor)] | **AMBIG** — mechanical no-`@` reading: YES; committed reading: no | **AMBIG** — exact list |
| state-path (535) | read | `/home/u/P/f/lane/.ufo/state/lane.round` | [(V-SURFACE, major)] | no (absolute) | no |
| recursive-glob-tool (540) | glob | `/home/u/P/f/lane` | [(V-RECURSIVE, minor)] | no (absolute) | no |
| recursive-read-lane-root (541) | read | `/home/u/P/f/lane` | [(V-RECURSIVE, minor)] | no (absolute) | no |
| recursive-read-fleet-root (542) | read | `/home/u/P/f` | [(V-RECURSIVE, minor)] | no (absolute) | no |
| recursive-grep-root-slash (543) | grep | `foo in /home/u/P/f/lane/` | [(V-RECURSIVE, minor)] | **AMBIG** (same as 516) | **AMBIG** |

All other selftest records are bash or write/edit calls → untouched by the new class
(verified by the line-listing grep above: no further read/grep/glob renders exist).

## Table B — tests/fixtures/r19-seat-audit-shapes.py (17 cases total; exactly one read case)

| case | tool | args (transcript render) | expected | new flag? | breaks? |
|---|---|---|---|---|---|
| implicit-root-read (src line 88) | read | `<synthetic lane abs path>` (…/souji-r19-audit-shapes.*/<case>/lane) | exit 0, ids == [V-RECURSIVE] (exact set) | no (absolute) | no |

No grep or glob case exists in this fixture. Exit stays 0 under any reading (new class is
minor); only the exact ids set could fail, and only if absolutes were flagged (forbidden).

## Table C — tests/fixtures/r20-audit-contract.py (78 records total)

Exactly one read/grep/glob render in the whole fixture (source line 120,
`receipt_transcript=True`): `read(/var/tmp/souji-r20-synthetic-input)` — absolute → never
flagged. It feeds 11 receipt/drift records (receipt-exact-digests, the 4 digest-change
cases, drift-auditor/spec/transcript/manifest, drift-auditor-after-import,
receipt-spec-transcript-alias); none of them asserts a violations list that a new minor row
could upset, and none gets one. The other 54 `build_cases` worlds render write (default) or
edit (transcript_line) only → out of scope for the class. New flag: no for every record;
breaks: no.

## Guard arithmetic reconciled against source (static counts, machine-counted)

- selftest: 118 = 90 case tuples + wave-summary + run-scratch-wiring + 26 grant scenarios
  (10 via the DELIVERY_SUFFIXES loop × 2 appends + 16 extend literals) — matches "pass=118".
- r19: 17 cases — matches "17/0"; base_discriminating 12 is base-arm behavior, unaffected
  by V-READ-ROOT (base arm has no new class).
- r20: 78 = 65 primary (54 build_cases + 11 receipt/drift) + 11 base-overauth
  (BASE_BROAD_CASE_IDS = 11, machine-counted) + base-broad-authorization-inventory +
  oracle-exact-case-inventory; base 11 — matches "78/78/0 base 11". No stale-number drift;
  the frozen guards are reproducible at the r21 base.

## Findings

F1 (decision needed before integration; the only existing cases that interact with C1).
`recursive-grep-tool` and `recursive-grep-root-slash` render `grep(foo in {lane})` —
complete, untruncated, and with no ` @ ` separator. The prereg sentence "grep with complete
untruncated args and no ' @ ' separator → implicit cwd → FLAG", applied mechanically, adds
a minor V-READ-ROOT row to both; their assertions are exact lists, so --selftest would
print FAIL twice → 116/2, violating the frozen guard "selftest stays 118/0". Under the
committed reading (visible complete absolute path ⇒ not implicit ⇒ no flag) both stay
clean and 118/0 holds without touching the pinned wants. Options for L1/implementer:
(a) implement path extraction for any visible separator and skip flagging on complete
absolute paths (keeps the two r16-era cases pinned as-is; matches my oracle labels); or
(b) extend the two `want` lists with ("V-READ-ROOT", "minor") — keeps 118/0 numerically but
hard-codes the mechanical reading into pinned cases and would then require the independent
r21 oracle TSV to adopt the same reading (after must equal oracle). Report-side
recommendation: (a). Confidence: high on the mechanics (exact-assertion code observed);
the reading choice is L1's.

F2 (recall gap, bounded). Under the committed reading, NO existing case in any of the three
sources exercises a relative read/grep/glob target, a pattern-only grep, a `~`/URI target,
a read selector (`:N`/`:raw`/comma), or a `;`-multi-path — every read/grep/glob case in all
three sources is a bare absolute path. So r19's 17/0 and r20's 78/78/0 are preservation-only
for C1: they cannot detect a missed flag (false negative) on any positive shape. The
existing suites DO guard overreach on absolutes (7 selftest cases + r19 implicit-root-read
would fail if absolutes were flagged). All discriminative load for V-READ-ROOT positives
falls on tests/fixtures/r21-read-root.py + census/round-21/read-root-oracle.tsv.

Unresolved: none within this ticket's scope. F1's reading decision is L1's, not mine.
