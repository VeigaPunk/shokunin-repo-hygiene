# Round 50 — the S267 token readings re-derivable by committed command, and census receipts that verify

Fresh-start reading done first (round prompt §7): the last three REJECTED
closures (r43, r44, r45 — lessons + reports) were re-read and spot-checked
before anything was declared; the ruling-out table is in the round report.
The r49 non-author closure (round-49-verifier-spotcheck.md, verdict
`ok, admitted`) routed two carry-in items; both are addressed this round:
item 1 (the census conf-form rc-2 host mismatch, carried since r48, L0
open) is addressed by claim C2's receipt capability plus an appended,
append-only L0 proposal line naming the cross-lane lineage (revenger r79
carries the same shape) and a concrete resolution option set; item 2 (the
S267 "zero histor*" wording — exact for content, not raw bytes) is claim
C1's erratum, below. Two claims, two axes; C1 works the lowest non-retired
axis (calibration 7). No exploratory claim. Preregistration frozen before
any claim receipt exists; the do-nothing controls are committed in the
freeze commit (control-first). No wave was dispatched: this host has no
seat dispatch surface (standing L0 questions; dispatched=0, completed=0,
dead=0; no WAVE-DONE claimed; nothing assumed answered).

## Gate

- S273 admitted: https://docs.python.org/3/library/html.parser.html opened
  live 2026-11-01 by this session (curl -sSL, HTTP 200, no redirect, 55260
  bytes, sha256 13ba271cea644c22a10c51836844e7a1089bf53af82ef1da5978338bf7c777f4;
  full-page capture census/round-50/sources/s273-htmlparser-page.html).
  Located quote (20 words, counted by the pasted command in the capture —
  tags stripped display-faithfully, whitespace flattened): "all character
  references (except the ones in elements like script and style) are
  automatically converted to the corresponding Unicode characters."
  Context: HTMLParser(convert_charrefs=True) — the exact default the r50
  counting instrument relies on when it decodes a page's text content
  before counting a token at the content scope. The page grounds the
  character-reference decoding only; which elements the instrument excludes
  (site chrome: script/style/header/nav/footer tags and class~=footer
  elements) is the instrument's own named policy, recorded in every
  record's METHOD line.
- Reject sample (stated explicitly, r48-closure carry-in practice): this
  Gate opens exactly ONE new source (S273, the only candidate fetched,
  admitted) and lands ZERO new reject rows; the standing rejection S267 was
  re-opened a second time WITH the counting method named (the r49
  verifier's routed fix): receipt
  census/round-50/sources/s267-reopen-count-receipt.txt — content histor=0,
  raw histor=1 (the site-chrome footer link "History and License"), factual
  0/0, page bytes byte-identical to the r49 fetch (sha256 0a9474e3…f5d3);
  the rejection HOLDS, no row cell changed. The sweep that bounds the
  reject sample to one fetch: the round fetched exactly two pages (the
  capture above and the S273 page), both receipts committed.
- Reject sample (stated explicitly, r48-closure carry-in practice): this
  Gate opens exactly ONE new source (S273, the only candidate fetched,
  admitted) and lands ZERO new reject rows; the standing rejection S267 was
  re-opened a second time WITH the counting method named (the r49
  verifier's routed fix): receipt
  census/round-50/sources/s267-reopen-count-receipt.txt — content histor=0,
  raw histor=1 (the site-chrome footer link "History and License"), factual
  0/0, page bytes byte-identical to the r49 fetch (sha256 0a9474e3…f5d3);
  the rejection HOLDS, no row cell changed. The sweep that bounds the
  reject sample to one fetch: the round fetched exactly two pages (the
  capture above and the S273 page), both receipts committed.
S267-COUNT-ERRATUM (r49 receipt wording; append-only, history not rewritten): census/round-49/sources/s267-reopen-receipt.txt's "zero occurrences of 'factual' and zero of 'histor*'" is exact at the CONTENT scope only — the raw page bytes carry exactly 1 occurrence (the site-chrome footer link "History and License"). Re-derivable by committed command per the counting receipt census/round-50/sources/s267-reopen-count-receipt.txt: `python -B tools/souji-page-token-count.py --capture census/round-50/sources/s267-stdtypes-capture.html --token histor` → SCOPE-CONTENT-MATCHES=0, SCOPE-RAW-MATCHES=1; `--token factual` → 0/0. Method: content = HTML text content via html.parser (character references decoded per S273; script/style/header/nav/footer elements and class~=footer elements excluded — site chrome); raw = case-insensitive byte-prefix count over the exact page bytes. Decision unaffected; S267 stays rejected; the r49 receipt bytes stay as filed.
- Census before→after: before taken at the round start both ways — raw
  adapter capture census/round-50/records/census-before.txt (rc 0, 59 W04,
  rows 196, `shokunin-repo-hygiene ok`; the conf form's raw rc-2 `souji
  missing` verdict recorded inside — the documented host state) and, new
  this round, as a digest-bound v1 receipt census/round-50/records/
  census-before-receipt.txt (FLEET-SCRIPT-SHA256 3fb72615…4e30,
  ADAPTER-SHA256 a159f2db…f74b, CONF-RC=2, DIR-RC=0, DIR-RESULT=ok,
  DIR-WARN-W04=59; `verify` ok over every check including both script
  hashes). After: the end-of-round receipt lands with the round's end
  receipts, exit 0 required.
- NTFS exclusion set re-derived at base: exactly the six pinned paths
  (census/round-50/records/ntfs-exclusion-check-base.txt — the six quoted
  control-char paths from the porcelain D rows, count=6; the porcelain
  receipt records/porcelain-at-base.txt additionally shows the inherited
  integrator-landing drift: the r49 spotcheck file staged-deleted beside
  its untracked twin). The base drift repair could NOT run mid-round: the
  committed fail-closed tool refused it — receipt
  census/round-50/records/idx-repair-base-refused-50.txt (REFUSAL
  fail-closed: 14 unexpected row(s); nothing repaired — the round's own
  in-progress untracked files are unexpected rows, the same disclosed
  behavior as r49's idx-repair-freeze2-49). The repair therefore lands
  once, after the round's final landing, at the final tip: its receipt
  (AFTER rows=6, unexpected=0) is quoted in the round report; the
  tolerance is not widened.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| a quote-count command whose tag-stripping substitutes a space for every removed tag turns a verbatim displayed quote into a non-substring — inline elements inside the sentence (`<code>style</code>)`) gain a phantom space before the parenthesis, so the presence check printed False while the word count printed 20 | the round's first S273 count command: `re.sub(r'<[^>]+>',' ',…)` → `False 20`; the corrected command (empty replacement) → `True 20` (both runs pasted in census/round-50/sources/s273-htmlparser-located-quote.txt) | the count command itself, on the round's own first run | the located-quote practice strips tags display-faithfully (empty replacement) and pastes BOTH the command and its output; lineage: the r45/r48/r49 word-count errata (this is the fourth occurrence of the quote-counting class and the first where the method, not the number, was wrong) |
| a selftest's tamper arms that mutate one shared file in sequence poison each other: arm A2's header flip was still in place when arm A3 ran, so A3's expected COUNT-MISMATCH was preempted by RC-INCONSISTENT (and later arms "passed" for the wrong reason) | census-receipt tool selftest first runs: `SELFTEST-CASE fail count-mismatch`, `SELFTEST cases=6 pass=5 fail=1` (session log, round-50 scratch; reproduced twice before the fix) | the tool's own selftest failing its intended class | every arm now restores the clean receipt before tampering (`restore()` from the A1 bytes kept in memory); the fixed tool reads `SELFTEST cases=6 pass=6 fail=0` EXIT=0, and each arm asserts its exact refusal class: DIGEST-MISMATCH, COUNT-MISMATCH, RC-INCONSISTENT, ADAPTER-DRIFT, MALFORMED |
| a receipt that carries only derived numbers without the listing that produced them is not a receipt: the first NTFS exclusion take wrote bare counts (7, then 0 — the second from a sed pattern that matched nothing) instead of the six quoted paths | the discarded first take of census/round-50/records/ntfs-exclusion-check-base.txt (session scratch copy kept; never landed) | pre-freeze receipt review | re-taken as the listing plus `count=6`, command recorded in the receipt; standing rule: a count line in a receipt names or embeds the rows it counted |

Fresh-start sweep (three rejected closures, re-checked this round): r43's
shape was preregistration-after-ready-handoff plus counters that could not
bind their captured tokens — ruled out by freezing (prereg + counter +
population + controls in ONE commit) before any claim receipt exists, and
by a counter whose every value is parsed from the instrument's own emitted
grammar at a named revision. r44's shape was a frozen predicate honest work
could not meet (tuple identities disagreed in the frozen counter) — ruled
out by deriving each target from readings the base already exhibits or the
routed defect itself names, and by pre-freeze feasibility runs of every
legged command against a synthetic tip containing exactly the claimed
bytes. r45's shape was the different-instrument limit — ruled out
structurally: the SAME counter bytes measure both arms (red at the base
rev, green at the tip rev; only the world moves), and both claims' repair
direction is the r49 non-author closure's own routed items, not new
instruments invented to flip verdicts.

## Admission distinction

C1 is a record-accuracy instrument landing a calibration verdict: the
lane's own r49 receipt stated a reading ("zero occurrences") that no
committed command could re-derive, and the statement was imprecise at the
raw-byte scope; after C1 the reading is re-derivable by committed command
at two named scopes and the erratum is on file. No new factual correction
credit is asserted for the underlying S267 decision (it was already
correct). C2 is a capability acquisition: census receipts become verifiable
(digest-bound, tamper-refusing, script-drift-detecting) — a class the
round contract mandates every round; its row enters the SCORECARD
capabilities table this round. Numeric axis scores unchanged (calibration
7, operability 8, coverage 8): no reproducible 0–10 mapping exists, no new
province surface, no Core promotion.

R51-CORRECTION corpus/lessons/round-50.md ## Gate: the "Reject sample (stated explicitly, r48-closure carry-in practice)" bullet appears TWICE verbatim, consecutively (the second and third Gate paragraphs are byte-identical duplications; the r50 non-author closure's routed item 1); this line is the appended r51 correction naming the duplication — the duplicated bytes above are preserved as written, append-only, history not rewritten; both instances carry identical text, so any citation of the bullet is a citation of both.
