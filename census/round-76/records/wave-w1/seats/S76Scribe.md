# S76Scribe — r76 scribe seat: S320 row + knowledge section, with independent re-derivation

**Verdict: PASS for both drafts; claim numbers reproduce; one MEDIUM evidence gap (domain-trial receipt).**

1. S320 row drafted (`.ufo/waves/round-76/w1/S76Scribe/sources-rows.md`): 11 cells, inserted after `corpus/SOURCES.md:278`.
   `sha256sum census/round-76/srcs/git-check-ignore.adoc` = 940177c7385eb3cf0ffb1f22ffba35661d16800f8ce787ac676e9a8c89d68208, `wc -c` = 4159.
   Live refetch `curl -sS -w 'HTTP=%{http_code} size=%{size_download}'` on the cited v2.56.0 URL: `HTTP=200 size=4159`, same sha256, `cmp` identical to the capture.
   Quote 18 words at offset 2355 of the whitespace-normalized capture (lines 81-82, `git-check-ignore.adoc:81`); offset convention cross-checked against S318 (its quote is at 3807 0-based).
2. r76 knowledge section drafted (`.ufo/.../S76Scribe/knowledge-r76.md`): attribution rule, f7 FAIL / f11 PASS / f12 PASS rulings, the `.jj/`+`.ruff_cache/` declaration, tally binding rule and its stated limit, with `census/round-76/records/*` and `controls/*` receipts.
3. Census validate (`S76Scribe/census-validate.txt`): `sources-census.sh validate --file v/corpus/SOURCES.md --today 2026-11-06` -> `BASE_RC=0`, `S320_RC=0`, output `file ok <path>`; `diff` against the row-less copy differs only in the printed path, so no new code (86 pre-existing W04 warnings remain).
4. C1 re-derived (not copied): gate+writer blobs at `e827d2b` copied to scratch (gate sha256 18587bd2…, writer 70bbf1c2…), `python3 -B census/round-76/c1-evade-counter.py --gate-dir $S/gw --work $S/c1b` -> `SUMMARY rows=30 mismatches=0 errors=0`, `C1_RC=0`. f7/f9/f10/f14 now `match=yes`; f11/f12 `PASS`.
5. C2 re-derived: `python3 -B census/round-76/c2-binding-counter.py --tally census/round-76/c2-kill-tally.py` -> `SUMMARY cases=10 mismatches=0 errors=0`, `C2_RC=0`; h-honest `killed=6 survived=0`.
6. Frozen pre-states confirmed from controls: K-a `SUMMARY rows=30 mismatches=4` EXIT=1 [f7 f9 f10 f14] (`controls/c1-K-a-do-nothing.txt`), K-b 4 [f2 f6 f11 f12], K-c 1 [f11]; c2 do-nothing 5, blanket 2. All match the prereg's parenthetical lists.
7. `.gitignore` at W (`git show e827d2b:.gitignore`) adds `.jj/` (line 4) and `.ruff_cache/` (line 5). Live attribution `git -c core.excludesFile=/dev/null check-ignore -v -n -z` on `.jj/repo/config-id` returns `.gitignore:4:.jj/` — the deciding rule is tracked, so f11's PASS is honest.

**MEDIUM — domain-trial receipt missing from committed bytes.** Prereg Target (binds a kill) requires the W gate on the lane to print check-clean=PASS at the report tip, but `census/round-76/records/` holds no domain-trial receipt at `eef6f30c` (only c1-after, c1-regress-r27/r36, c2-after, census-before, probe-coreworktree-*, rec-missing-bind-control). I ran it myself against lane HEAD: `EXIT=0`, `check-tip=PASS`, `check-clean=PASS` (`S76Scribe/domain-trial.txt`). L1 must file this as a receipt or the claim lands without one.

**LOW.** Prereg's C1 "before" gate blob ef3b04e4… and A's 18587bd2… both verified by `git show`; the 30-row population derives exactly as 20 r74 + 5 r75 + f9 f10 f14 f11 f12, and `c1-population.tsv`/`c2-population.tsv` hashes equal the prereg's. No HIGH findings.

Files written under `.ufo/waves/round-76/w1/S76Scribe/`: `sources-rows.md`, `knowledge-r76.md`, `census-validate.txt`, `c1-counter-run.txt`, `c2-counter-run.txt`, `domain-trial.txt`. Scratch `/fast/scratch/hyaku/souji-r76/S76Scribe/` removed; no lane file touched; no commits.
