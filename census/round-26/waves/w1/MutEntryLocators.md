# MutEntryLocators — K2 gate locator mutation test (round 26, C2)

## Status
STATUS: PASS — locator mutation probe executed; verdicts conclusive on the staged
Gated entries (baseline green), and a live defect found: at lane tip the two
landed corpus entries have NO `## Gate`, so the frozen K2 counter itself fails
(`entries=2 ok=0 fail=2`). Neither planned Gate-locator mutation is caught by
the K2 gate; only total locator-token removal is.

## Evidence
Detector: frozen K2 command `python3 -B tools/souji-gate-check.py --root .`
--round-date 2026-10-25 --entries corpus/knowledge/... --snapshot-dir
census/round-26/sources --slice census/round-26/records/empty-slice
--slice-verdicts census/round-26/records/empty-verdicts` (mirrored into
/var/tmp/souji-r26-MutEntryLocators with byte-exact copies; lane tip HEAD
ba8b54b85814dd980aa96050fe111c7cbfd4956a). Also run Q54 fixture
`tests/fixtures/r23-locator-heading.py`.

- Baseline (staged w1 entries, both with Gate): `entries=2 ok=2 ... fail=0`, rc=0.
- M1 § OPTIONS→§ ENVIRONMENT (both entries, Gate ADMIT row only):
  `entries=2 ok=2 ... fail=0`, rc=0 — **survives K2**.
  Q54 fixture: `LOCATOR-BAD ... ENVIRONMENT 'ENVIRONMENT' is no heading in:
  ... git-fetch.1.txt`, `locators_bad=1`, rc=1 — **caught by Q54 only**.
  (grep -c 'environment' git-fetch.1.txt = 0; heading set has no ENVIRONMENT.)
- M2 line one-off (builtin/fetch.c line 2926→2927; builtin/pull.c line
  385→386): `entries=2 ok=2 ... fail=0`, rc=0 — **survives K2**; Q54
  `locators_bad=0`, rc=0 — **survives Q54 too** (lines not inspected).
- Control mutation (all locator tokens removed from the OPTIONS ADMIT row):
  K2 `FAIL entries/mut-a-no-loc.md check3-no-locator-gate-line-6`, fail=1,
  rc=1 — **caught by K2**; Q54 `locators=0 bad=0` (no § tokens to check).
- Live tip: exact K2 on the two landed corpus entries:
  `FAIL ... git-auto-maintenance-trigger-set.md check1-no-gate: ...`,
  `FAIL ... git-auto-maintenance-trigger-set-r23.md check1-no-gate: ...`,
  `entries=2 ok=0 ... fail=2`, rc=1. Both landed files end at `## Freshness`
  (67 and 92 lines); no `## Gate` section. Q54 reports them UNSCOPED
  ("Gate names no snapshot (predates Q54)"). Receipt c2-after.tsv binds rev
  e0f8dcd (K1 counter only: grounded_f1=2, registry_rows=132); no
  c2-gate.tsv exists in census/round-26/records/. Entry A first appears in
  commit 0833de9, B enriched in ea0bbe6; neither ever carried a Gate there.
- Planned locator resolution vs snapshot bytes (all verified verbatim this run;
  `sha256sum -c SHA256SUMS` → 7 OK): git-fetch.1.txt OPTIONS h2 @ 2995;
  --auto-maintenance/--no-auto-maintenance/--auto-gc/--no-auto-gc dt rows
  3190-3193, dd para 3194-3199 incl. "This is enabled by default."; builtin
  call lines fetch.c 2926, merge.c 509, rebase.c 572, am.c 1942, commit.c
  1965; pull.c 392 (`strvec_pushl(&cmd.args, "fetch", "--update-head-ok",
  NULL);`); plus cited pull.c 385, fetch.c 2528, merge.c 506, rebase.c 569.

## Findings
1. The K2 gate validates quote-substring presence in the snapshot body plus the
   *presence* of any locator token (`LOCATOR_RE` in tools/souji-gate-check.py
   line 42); it never resolves `§ NAME` to the snapshot's heading set and
   never parses line numbers. Wrong section (M1) and wrong line (M2) both
   pass it. Location: tools/souji-gate-check.py:42,87-89,111-113.
2. Q54 (`tests/fixtures/r23-locator-heading.py`) complements K2: it catches
   M1 (ENVIRONMENT not a heading in git-fetch.1.txt) but is blind to M2
   (line numbers are outside its scope). The two gates together still cannot
   catch a one-off line number. Location: tests/fixtures/r23-locator-heading.py:30,67-76,111-118.
3. LIVE DEFECT (not a mutant): the landed entries at tip have no `## Gate`;
   the frozen K2 counter fails `check1-no-gate` for both, so C2's kill rule
   ("After value entries=2 ok=2 fail=0, exit 0") is not met at HEAD
   ba8b54b. The Gates exist only in the staged w1 drafts
   (.ufo/waves/round-26/w1/entry-*.md) and were not carried into
   corpus/knowledge. Q54's clause is vacuous for these entries. This is
   independent of the mutation test; a baseline failure is inconclusive, not
   a killed mutant.
4. All planned § locators (git-fetch § OPTIONS switch text; builtin files
   :2926/:509/:572/:1942/:1965; pull.c :392) resolve correctly against the
   staged snapshot bytes — the pristine read is accurate, so the exposure is
   purely in what the gate will not re-check.

## Attack log
None (item is a mutation probe, not an attack).

## Notes
No tools installed (operator rule: record installs; none needed). Scratch
/var/tmp/souji-r26-MutEntryLocators removed before finish; no lane bytes
modified by this seat (read-only).
