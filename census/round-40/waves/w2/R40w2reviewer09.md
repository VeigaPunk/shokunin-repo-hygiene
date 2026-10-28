# R40w2reviewer09 — report-contract attack

## Verdict: INCONCLUSIVE (no round-40 souji report draft exists); required contract is enumerated below.

### Exact L1 requirements, from `tools/souji-report-contract.py`

The evaluator requires all seven checks to pass:

1. **Sections, exactly once and in order** (`:51-58`, `:129-143`): `## Work performed`, `## Landed changes`, `## Before → After measurements` (normalizes arrow to `->`), `## Sources & frontier`, `## Trend verdicts`, `## Stale-lane`. It accepts `Stale lane` as heading alias.
2. **SHONEN lines** (`:153-166`): a single heading whose text begins `SHONEN`; it must contain the same number of recognized checkbox lines as lane `SHONEN.md`. Lane checklist has four boxes at `souji-shokunin/SHONEN.md:5,7,9,11`; thus report needs exactly four `- [x]`, `- [~]`, or `- [ ]` lines. The checker compares counts, not checklist item identity/content.
3. **Trend verdicts** (`:49-50`, `:169-192`): in the Trend verdicts section, exactly one matching line for each `expansion`, `quality`, `discernment`, with the first token after `:` or em dash exactly one of `unprovable-but-better`, `improved`, `harmed`, `unchanged`; no duplicate trend labels.
4. **Stale lane** (`:195-204`): either a nonempty Stale-lane heading body or a line matching `Stale-lane: …` / `Stale lane: …`.
5. **Measurement row** (`:207-220`): at least one pipe-prefixed table row inside Before/After Measurements, containing two or more backtick spans, at least one of which starts with 7–64 lowercase hex characters. Description says second span is a counting command; implementation only tests presence of a second span, not that it is a command.
6. **Claim IDs** (`:223-229`): Work performed section contains 1–3 distinct IDs matching `C1`..`C9`; for this round use relevant frozen claim IDs `C1`, `C2`, `C3` (`census/round-40/preregistration.txt:4-11`). It does not enforce that IDs are specifically C1–C3.
7. **Evidence pointer** (`:65`, `:232-246`): at least one backticked token beginning `census/`, `corpus/`, `tools/`, `tests/`, `.ufo/`, or 40–64 lowercase hex commit ID, anywhere outside masked fenced blocks/comments.

The checker masks fenced code and HTML comments before parsing (`:79-112`). CLI reads the report and SHONEN as UTF-8 with replacement (`:383-408`).

### Exact commands and output

Command:
```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-report-contract.py --help
```
Output (contract description): six ordered headings; one report checkbox per SHONEN box; three unique trend verdicts from allowed tokens; non-empty stale-lane; at least one measurement row with measured commit plus second backtick span; 1–3 claim IDs; at least one repo-relative evidence pointer or 40+ hex commit. CLI syntax is `python3 -B tools/souji-report-contract.py --report ABS --shonen ABS` or `--selftest`; exit 0 all pass, 1 any fail, 2 usage/unreadable.

Command:
```sh
if test -f /home/vgpnk/Projects/shokunin/.ufo/reports/round-40/souji.md; then nl -ba /home/vgpnk/Projects/shokunin/.ufo/reports/round-40/souji.md; else printf 'MISSING\\n'; fi
```
Output:
```text
MISSING
```

Command:
```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-report-contract.py --report /home/vgpnk/Projects/shokunin/.ufo/reports/round-40/souji.md --shonen /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md
```
Output:
```text
ERROR REPORT-UNREADABLE: [Errno 2] No such file or directory: '/home/vgpnk/Projects/shokunin/.ufo/reports/round-40/souji.md'
exit=2
```

No current-draft predicate can be assessed because the target is absent. No scratch directory was created; scratch removed: not applicable. No tools installed.
