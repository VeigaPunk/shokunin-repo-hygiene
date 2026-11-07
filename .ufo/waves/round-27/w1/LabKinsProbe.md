# LabKinsProbe — C1 landing-gate token-grammar probe (round 27, wave 1)

## Status
STATUS: PASS — six-token grammar probe run at base `e78ac7c4837b81b634db4a927605a751a7f006ba` in an isolated scratch clone (`/var/tmp/souji-r27-LabKinsProbe/probe`, git, removed on finish). Exactly two tokens are flagged — the two frozen `LG-DANGLING-PTR` findings; every sibling token is accepted. Simulated exemption rows for exactly those two paths clear both findings (2→0 in scratch) with no stale-exemption finding and leave all sibling verdicts unchanged. No installs; no lane file touched; report-only write.

## Evidence
Baseline, lane, at `e78ac7c` (frozen counter shape):
```
$ python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev e78ac7c4837b81b634db4a927605a751a7f006ba --round 27 --fleet-root /home/vgpnk/Projects/shokunin
LG-DANGLING-PTR	corpus/knowledge/registry	corpus/QUALITY.md:143 cites path absent at e78ac7c4837b
LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:141 cites path absent at e78ac7c4837b
SUMMARY	findings=2	checked_reg=50	checked_pins=13	checked_measured=3	checked_reports=0
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-27/ at e78ac7c...
```
Scratch clone at same rev reproduces the identical two findings (gate exit 2 = carry no-reports, pre-wave normal; SUMMARY is the counter surface).

Per-variant runs (scratch clone; one probe line in `corpus/README.md` per run; gate `--rev <full40>` of that commit):
| probe | scratch rev | verdict | findings |
|---|---|---|---|
| `corpus/knowledge/registry` | c5447f02f607e8b816d55b67a86af8085c704812 | FLAGGED (README:560) | 3 |
| `corpus/lessons/round-24.md:232:S118` | 39856162230546ee9db63a0a249d09bc11f3ae84 | FLAGGED (README:560) | 3 |
| `corpus/lessons/round-24.md:240` | c72e94d1a041abc83fdcd62c3040705e1ff648ad | ACCEPTED | 2 |
| `corpus/knowledge/nonexistent.md` | 6b20fe747150d74a36ef8ddb3dd8f4b9ca1c683d | FLAGGED (README:560) | 3 |
| `LOG.md:1692` | 56b1b8f8063dd06d23f1a2152eb5219e2c5630d1 | ACCEPTED | 2 |
| `SCORECARD.md:181` | fcfda38aaff84ed77df54c90853c67e1b9a55286 | ACCEPTED | 2 |

Combined run (all six probes, rev f62c5905b23f8db2939fca3990a8ec0f7fd80bc2): `findings=5` = registry@QUALITY:143, S118@QUALITY:141, registry@README:560, S118@README:562, nonexistent@README:566; `round-24.md:240`, `LOG.md:1692`, `SCORECARD.md:181` stay absent from findings.

Exemption-row simulation (two rows appended to scratch `corpus/pointer-exemptions.tsv`: `corpus/knowledge/registry`, `corpus/lessons/round-24.md:232:S118`):
- rev 4e369c2b200acb7c31d10915a889744717a5fd5d (rows only): `SUMMARY findings=0`, no `LG-DANGLING-PTR-EXEMPT-STALE`.
- rev f21cf89e2638f8a07ae48d18a1c4fa8c5313652a (rows + all six probes): `findings=1`, only `corpus/knowledge/nonexistent.md`.

White-box tokenizer (`_pointer_paths`, module `tools/souji-landing-gate.py` at base):
```
probe: corpus/knowledge/registry            -> ['corpus/knowledge/registry']
probe: corpus/lessons/round-24.md:232:S118 -> ['corpus/lessons/round-24.md:232:S118']
probe: corpus/lessons/round-24.md:240      -> ['corpus/lessons/round-24.md']
probe: corpus/knowledge/nonexistent.md     -> ['corpus/knowledge/nonexistent.md']
probe: LOG.md:1692                         -> []
probe: SCORECARD.md:181                    -> []
```

## Findings
1. Token grammar (POINTER_PATH_RE + `_trim_pointer_token`) explains every verdict: the trailing-suffix trim `:\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*$` strips plain line numbers but not composite `:NNN:S###` enumerators (`tools/souji-landing-gate.py:795-798`).
2. `corpus/knowledge/registry` (QUALITY.md:143, Q59 prose: "a corpus/knowledge/registry change is a coverage surface") is an over-match: prose noun phrase, not a citation; flagged because the path is absent.
3. `corpus/lessons/round-24.md:232:S118` (QUALITY.md:141, Q57 check-command argument) is an over-match: enumerated-site citation shape `file:line:S###`; suffix unstripped, path absent.
4. Sibling `corpus/lessons/round-24.md:240` (same Q57 site family, QUALITY.md:141) resolves via trimming to the existing `corpus/lessons/round-24.md` → accepted without any exemption.
5. Siblings `LOG.md:1692` and `SCORECARD.md:181` (same Q57 site list, QUALITY.md:141) are not even tokenized — top-level files lack the required root prefix (`census|tests|tools|corpus|.ufo/waves|.ufo/quarantine`) → accepted without exemption.
6. `corpus/knowledge/nonexistent.md` (synthetic knowledge-class sibling) is flagged: absence detection still fires for a genuinely missing path, so the registry exemption is per-path, not class-wide; such a token needs fixing, not an exemption.
7. Simulated exemption rows for exactly the two flagged paths clear both over-matches (findings 2→0) with no `LG-DANGLING-PTR-EXEMPT-STALE` and no change to any sibling verdict → the rows precisely cover the two over-match classes, and no sibling token in the authority files needs one.

Conclusion: at base the two frozen findings are the ONLY over-matches of their kind across all scanned sources; two exemption rows (exact paths) are sufficient and exactly scoped.

## Attack log
None — probe item. No counter/predicate anomaly observed; gate exit 2 at base is the expected pre-wave carry no-reports state.
