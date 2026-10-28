# R40executor25 — C1 calibration attack

## Named failure mode: non-unique anchor masquerading as an item-line identity

**Verdict: concrete falsifier against treating r39's token predicate as evidence of an anchored item; bounded r40 measurement is needed.** The weakness is distinct from token-only forgery and commit ancestry: r39's anchor lookup is substring-based and accepts any hit line carrying the required tokens. Thus an anchor can identify a large, unrelated set of lines, and a token-bearing unrelated line can close the item. A revision-bound pointer must be checked against the exact intended line, not merely coexist with a matching substring hit.

### Evidence

- `census/round-39/c1-counter.py` lines 224–240: `hits = [l for l in text.split("\\n") if row["anchor"] in l]`, followed by `good` over those hits based only on `must`/`mustnot` tokens. A good hit prints `ITEM ... CLOSED`.
- `census/round-39/c1-items.tsv` line 10: R39-C1-04 uses the generic anchor `SUMMARY` with required tokens `records=,failed=0,uncovered=0`.
- `census/round-39/waves/w1-results.json` lines 64–65 records the observed anchor-collision audit: `SUMMARY` appears in 7706 lines across 1689 files; R39-C1-03's `dead=0` also occurs in 14 lines across 7 other files. This is committed r39 evidence that anchors need not uniquely name an item line.
- `census/round-39/records/c1-after.txt` lines 3–20 reports all 16 closed, `open=0`, and rc=0; the r39 counter does not bind those closed decisions to unique evidence locations.

### Commands actually run

1. Read `/home/vgpnk/.omp/agent/RULES.md` and `skill://godspeed`.
2. Read `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt`.
3. `ls -la /home/vgpnk/Projects/shokunin/souji-shokunin && echo ---- && ls /home/vgpnk/Projects/shokunin/souji-shokunin/census && echo ---- && ls /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40 2>/dev/null` — observed r39 `c1-counter.py`, `c1-items.tsv`, records, waves; r40 contains preregistration only.
4. Read `census/round-39/c1-counter.py` and its lines 107–259; read `census/round-39/records/c1-after.txt` and `census/round-39/records/c1-before.txt` via targeted search results.
5. Search `census/round-39` for `receipt_rev|REGISTER|ITEM .*CLOSED|SUMMARY`; observed item TSV and prior round-39 W1 collision-audit evidence above.

### Bounded measurement plan

At the candidate and named base revisions, run the r40 counter on (a) the frozen r39 item corpus and (b) a scratch-only adversarial pair where two lines share the anchor but only the unrelated line carries the required tokens. Keep the evidence pointer aimed at the intended line/revision in the pair. Record exact item verdicts and summaries. The candidate must reject the pair (OPEN / unbound or anchor mismatch) while retaining all legitimate r39 closures; the r39 control is expected to accept the token-bearing collision under its observed substring algorithm. Do not infer a pass until those command outputs exist.

No production files changed; only this assigned report was written. No tests/builds/linters run.