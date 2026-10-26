# SwarmCritic21 — attack on `corpus/knowledge/jj-keep-ref-expiry.md` and `SKILL.md:115` (r30 w2)

## Status

STATUS: PASS — the attack ran: fixture replay, four replication probes on the recorded jj/git versions, source-byte and hash checks, C3 v1/v2 at the landing commit and the tip. The frozen C3 target is met; the entry's Consequence is falsified by its own fixture.

## Evidence

- Read-only clone (origin dropped) at `/fast/scratch/hyaku/souji-r30/SwarmCritic21/c`, lane tip `9dcd367655fc28ba73d679a0e2cadaff96d2bcb8`. No installs performed.
- `tests/fixtures/r30-jj-keep-expiry.sh` replayed under `$TMPDIR` on the host binaries the entry names (jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5, git 2.56.0): `diff -u census/round-30/records/jj-keep-expiry-run.txt replay.out` → BYTE-IDENTICAL, 10/10 lines. "byte-identical on replay" (entry:52-53) HOLDS.
- Counters: `c3-counter.py` → `SUMMARY legs=9 fail=0 f1_entries=3` at `76c94eb…` and at tip; `c3-counter-v2.py` → `SUMMARY-V2 e1=ok e2=ok e3=ok e4=ok f1_exact=3` at both (E3 `replay_lines=10 record_lines=10`). The L1's C3 reading reproduces.
- Snapshot hashes of all four files equal the entry's `verified-at`, `sources/SHA256SUMS` and `records/fetch-receipts.tsv`. Gate quotes opened against the snapshot bytes.
- Receipts: `.ufo/waves/round-30/w2/SwarmCritic21-receipts.txt` (probe transcripts, counter output, source excerpts, hashes).

## Findings

1. **Consequence overclaims reachability — BROKEN.** `corpus/knowledge/jj-keep-ref-expiry.md:64-66` says "after which the object is unreachable and a later prune can drop it". Counterexample, replicating steps 1-4 with the fixture's own commands: `keep_refs` 8→6 and `target_keep=no` (matches the record), yet `git rev-list --all | grep -c <B>` = 1 — the surviving `refs/jj/keep/5d7d5e64…` has B as its parent (`git log -1` → `parents=b59d737`). After the exact step-5 sequence the surviving `refs/jj/keep/c6deca2…` again has B as parent; the control repository's step 8 leaves D ref-reachable the same way. `git reflog expire --expire=now --all` followed by `git gc --prune=now` still leaves `git cat-file -e B` = 0 (present) in all three. Ref removal is not unreachability, and no later prune can drop the object while a keep ref names a descendant. This contradicts the entry's own Observed ("the run separates ref removal from object removal, and only ref removal is measured here.", :59-60) and does-NOT 3 (:78-80). Axes: calibration (7) — the claim is the product and it is wrong; coverage 8 unmoved (entry exists, legs green); operability 8 untouched.
   Smallest safe correction: replace the causal clause with what the record shows — the ref named after the commit is removed at step 4 (and step 8); the object stayed reachable from other keep refs in the measured fixture; object removal is unmeasured.

2. **"Steps 4, 5 and 8 remove its keep ref" — BROKEN for step 5.** Entry:64. Step 4 already removed the target's ref (ref-set diff at step 4: `63341903…` and `cd8c12f…`, the latter being B); step 5 removed four further refs, none naming B (`keep_refs` 6→2, `target_keep=no` both before and after). Step 8 is the control repository, a different commit. Correction: "steps 4 and 8 remove the ref that names it; step 5 removes further keep refs".

3. **"not of git" — BROKEN.** Entry:24: "the index/operation views jj reads and of a caller-supplied `keep_newer` instant — not of git." Packed arm: after `git pack-refs --all`, a keep ref packed seconds earlier is deleted by plain `jj util gc` under the 14-day default (`keep_refs` 8→6, `target_keep=no`), while the loose control keeps it (8, yes). git's ref storage form decides whether the age gate can save a ref — which item 2 (:26-30) itself says. The mechanism is `if let Ok(metadata) = loose_ref_path.metadata()` (`census/round-30/sources/git_backend.rs:939`): a missing loose file falls through to deletion. Correction: drop the clause, or say git does not build the ref set while the packed/loose form changes the age gate's reach. Axes: calibration.

4. **"which is the state a later `gc` reads" — DEFECT-NOT-FATAL.** Entry:41-42. `gc` reads `index.all_heads_for_gc()` (:22-23), and the keep refs surviving step 5 name hidden descendants; the entry's own does-NOT 5 (:83-88) says which heads that returns for hidden heads is unsettled. The two sentences cannot both stand. Correction: qualify :41-42 with the same uncertainty.

5. **S221 citation range — DEFECT-NOT-FATAL.** Gate row "S221 … lines 5-8" and entry:41: the second quoted fragment "as well as the set of heads in the repo" is on line 9 of `census/round-30/sources/operation-log.md` (lines 6-7 carry the first quote). Correction: cite 5-9.

6. **"a `jj util gc` that no lane action requests" — DEFECT-NOT-FATAL.** Entry:64-65 contradicts does-NOT 1 (:73-75): "whether any other jj command invokes backend `gc` was not opened or measured here". The grep supports only the tooling form: no `util gc`/`op abandon` in `tools/` or `scripts/hyaku/jj-lane.sh`. Correction: "that no lane tool invokes".

7. **`SKILL.md:115` heading — BROKEN as a headline.** "a keep-only commit's lifetime is the operation log's, not the ref's": step 4 deletes B's keep ref while an operation still names B (step 5's `ops_naming_target=1` is measured before the first `jj op abandon`), so the op log neither preserves the ref nor owns the lifetime; surviving keep refs are what hold the object. The bullet's body HOLDS: counts 8→6→2, object present at every step, 14-day default, `--expire` only `now` (`cli/src/commands/util/gc.rs@v0.45.1:54-58`; cli-ref 3803 reads: Only the string "now" can be passed to this parameter.). Correction: headline the measured fact ("a keep ref is removed by jj's own gc threshold, never by `git gc` alone") and keep the r17 receipt rule. Axes: operability 8 — this is the line a lane operator reads before choosing a receipt root.

8. **A green claim ships a false sentence — DEFECT-NOT-FATAL, structural.** Both C3 instruments check provenance (entry token, map row, fixture replay, snapshot hashes), not the Consequence; finding 1 passes every leg. The frozen C3 target holds, so this is not a kill-rule miss; it is the round's calibration gap and the next calibration move (a sentence-to-record check, alongside the A3-style counter).

Positive results worth recording: item 2's `[INFERENCE]` ("the ref goes regardless of age") is now measured true by the packed arm; item 3's two-clock and single-literal claims verify against the snapshot and `gc.rs`; item 5 verifies against `git-gc.adoc:18-20, 81-83, 159-161`; the Observed paragraph matches all eight RESULT lines.

## Attack log

| attacked item | verdict |
|---|---|
| Observed paragraph vs `jj-keep-expiry-run.txt` (8 steps) | HOLDS |
| Fixture replay byte-identity | HOLDS |
| Item 1 — `recreate_no_gc_refs` rewrites the ref set | HOLDS except "— not of git" (F3) |
| Item 2 — age gate and packed-ref hole | HOLDS; `[INFERENCE]` verified true by probe3 |
| Item 3 — `--expire`, two clocks, single literal | HOLDS (cli-ref 3801-3803; gc.rs 54-58; git_backend 1558-1564, 977) |
| Item 4 — `jj op abandon` | DEFECT-NOT-FATAL (F4); citation F5 |
| Item 5 — `git gc` alone | HOLDS (step 3; control steps 7/8) |
| Consequence — "Steps 4, 5 and 8 …" | BROKEN (F2) |
| Consequence — "unreachable … later prune can drop it" | BROKEN (F1) |
| Consequence — "no lane action requests" | DEFECT-NOT-FATAL (F6) |
| does-NOT list | HOLDS as written; bullets 1 and 5 contradict the Consequence |
| `[INFERENCE]` labels | HOLDS — all labelled and conservative; two now measured |
| Gate quotes (14) | 13 verbatim and in range; S221 range off by one (F5) |
| Snapshot hashes / `verified-at` | HOLDS (4/4 equal) |
| `SKILL.md:115` | body HOLDS; heading BROKEN (F7) |
| C3 v1 and v2 at landing and tip | HOLDS (`legs=9 fail=0`; `e1..e4=ok`) |

## Deliveries

- `.ufo/waves/round-30/w2/SwarmCritic21.md` — this report.
- `.ufo/waves/round-30/w2/SwarmCritic21-receipts.txt` — probe transcripts, counter output, source excerpts, hashes.
