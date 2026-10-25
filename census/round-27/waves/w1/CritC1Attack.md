## Status
STATUS: PASS — C1 survives adversarial review (4/4 attack vectors survive, one structural fragility + one surface-class caveat noted). The claim's delta is mechanically reachable with exactly the two exemption rows, both verified to over-match only parser grammar, not real citation breaks.

## Evidence
All commands run this session from /home/vgpnk/Projects/shokunin/souji-shokunin (lane base e78ac7c4837b81b634db4a927605a751a7f006ba, `git rev-parse HEAD` = base; Python 3.14.8).

1. Base counter reproduced exactly (frozen command): `python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev e78ac7c4837b81b634db4a927605a751a7f006ba --round 27 --fleet-root /home/vgpnk/Projects/shokunin`
```
LG-DANGLING-PTR	corpus/knowledge/registry	corpus/QUALITY.md:143 cites path absent at e78ac7c4837b
LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:141 cites path absent at e78ac7c4837b
SUMMARY	findings=2	checked_reg=50	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-27/ at e78ac7c4837b81b634db4a927605a751a7f006ba
```
(rc=2: base has no round-27 reports; the claim pins only SUMMARY findings, so counter text is internally consistent.)
2. Same rev WITHOUT `--fleet-root`: findings=5 (three extra: `../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md`, `../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` (README.md:217), `.ufo/waves/hyaku/jj-w1/reports/` (jj-colocation-receipts.md:148)). All three paths verified present at /home/vgpnk/Projects/shokunin (readdir). The two C1 findings appear in both runs → claim delta is fleet-flag-independent.
3. Finding 1 is prose: QUALITY.md:143 (Q59) — "a corpus/knowledge/registry change is a coverage surface" (verbatim). `git ls-tree -r e78ac7c` corpus/ census: no `corpus/knowledge/registry` file or directory exists.
4. Finding 2 is a house-style citation argument: QUALITY.md:141 (Q57) verification shell line (verbatim) — "corpus/lessons/round-24.md:240 corpus/lessons/round-24.md:232:S118 LOG.md:1692 SCORECARD.md:181". `corpus/lessons/round-24.md:240` yields no finding (trim drops `:\d+`); `:232:S118` resists `_trim_pointer_token` (trailing non-digit), so the intact literal becomes a bogus path. The cited target resolves: round-24.md line 232 holds the `| S118 | unverifiable | ...` row (verified). round-24.md:388 quotes house syntax — "superseded by corpus/lessons/round-24.md:232" (verbatim).
5. After-scenario mechanics (scratch git repo under /var/tmp/souji-r27-CritC1Attack/after, `git clone --no-hardlinks` of lane + two appended TSV rows + commit 45114e345e7cfd211414cdc5a32eec4048e9378c; scratch removed after): `SUMMARY findings=0 checked_reg=50 ...` (no LG-DANGLING-PTR; rc=2 only for absent round-27 reports). `--json` output has keys error/exit/findings/fleet/resolved_base/resolved_rev/summary — no `used_exemptions` field; SUMMARY is blind to exemption usage.
6. Loader (`load_pointer_exemptions`, tools/souji-landing-gate.py:876-902) validates only format: unique 2-field row, safe path, starts with POINTER_ROOTS ("census/","tests/","tools/","corpus/",".ufo/waves/",".ufo/quarantine/"), no `<>*`. No cross-check that the exempted token appears in any source, no expiry, global and permanent. CLI (main, :2278-2322) exposes no pointer-disable flag; `--base` affects only changed-script checks.

## Findings
1. Both findings are parser grammar over-matches, not dangling references: (a) Q59 prose class-name token; (b) Q57 `file:line:site` citation argument whose target (round-24.md:232 S118) verifiably exists. `findings=2→0` measures gate noise removal, not a change in self-assessment content — legitimate as calibration only because the resolution is documented annotation, not silent deletion. [QUALITY.md:141,143; round-24.md:232,388]
2. No do-nothing invocation exists: dropping `--fleet-root` raises findings to 5; no flag disables pointer checks; the only sanctioned resolution (two TSV rows) is itself the minimal write. The counter cannot distinguish exempted-from-clean findings (no used_exemptions in SUMMARY/JSON) — pass state depends on the L1 disclosing the TSV diff in the report; without disclosure the kill rule is unverifiable from the counter alone. [tools/souji-landing-gate.py:876-902,2278-2322; --json output]
3. Exemption mechanism is trust-based and permanent: rows mask the exact absent path in every future round with no revalidation; a dishonest future round could silence a true defect with an identical row. This round's two rows are verifiably benign (prose class label; citation resolving to a real S118 row), so no false cleanliness accrues now. Structural fragility to flag for later rounds (suggest: exempted path must appear in a current source; round-scoped or expiring rows). [tools/souji-landing-gate.py:876-902,949-961]
4. `before=2` reproduces exactly (point 1), and `--fleet-root` is legitimate: it reclassifies only one-level `../` escapes and `.ufo/waves/hyaku/` prefixes, all verified real at the fleet root; internal findings unaffected. Caveat: the before-count is environment-dependent (depends on fleet files existing), so the counter is not repo-self-contained. [tools/souji-landing-gate.py:922-942]
5. Surface-class note (not a kill): machine block declares `surface-class=self-assessment-file`, but the file actually changed is `corpus/pointer-exemptions.tsv` — a gate-annotation data file, not self-assessment content; under Q59's own taxonomy it matches none of the enumerated classes (and Q59's example token is exactly the prose being exempted). Reported per contract as a counter/attribute observation, not a proposed change. [QUALITY.md:143; preregistration line 5/12]

## Attack log
- A1 (real improvement vs bookkeeping): SURVIVES — noise is instrument-level; calibration axis is instrument-tuning; truthfulness of the two reasons is the load-bearing condition.
- A2 (do-nothing control): SURVIVES — no invocation trick; mechanism is prescribed minimal annotation; required disclosure caveat recorded.
- A3 (future-round weakening): SURVIVES for this round; permanent-trust-based design flagged as fragility.
- A4 (reproducibility / --fleet-root): SURVIVES — exact repro; flag classification verified against real fleet files.
