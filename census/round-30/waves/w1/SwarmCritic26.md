# SwarmCritic26 — attack on C3 (F1 keep-ref expiry)

## Status
STATUS: PASS — attack delivered. Five cheating states scored with the frozen counter. Three reach the target `SUMMARY legs=9 fail=0 f1_entries=3`: A, whose run record was typed rather than measured; D2, where the `ground: F1` label sits on a stub instead of the admitted entry; E, where the entry is mapped under the plain-F1 row instead of the F1-jj row. C (a detached label after a heading) is caught by L2. The delivered draft's record is real: an independent replay of the delivered fixture reproduces it byte-for-byte. No lane bytes were written except this report and its receipt; no tool was installed.

## Evidence

Lane at scoring: `df6afe817d096e4ad71ba2b9cc21a83f126eb658` (branch master), prereg `d4928ec86b667e3d1ed0adb07fb088e500cf1631`. Scratch clone of the lane at the tip with `origin` removed, `/fast/scratch/hyaku/souji-r30/AttackC3/c`; every rev below is a scratch commit. Full transcripts: `.ufo/waves/round-30/w1/SwarmCritic26-c3-scores.txt`.

Command in every row: `python3 -B census/round-30/c3-counter.py --root <scratch clone> --rev <rev> --scratch <scratch>/counter`.

State | what the scratch commit adds | SUMMARY
---|---|---
base tip | nothing | `SUMMARY legs=9 fail=8 f1_entries=2 rev=df6afe8…`
A | entry + snapshot + registry row + README mapping + a **typed** run record (`RESULT default_14d keep_before=6 keep_after=0 deleted=6`, i.e. inverted against both the source and the real run) | `SUMMARY legs=9 fail=0 f1_entries=3 rev=fc2152c…`
B | A with `ground: F1-jj` | `SUMMARY legs=9 fail=0 f1_entries=3 rev=5c9540a…`
C | `ground: F1` appended after a heading in another entry, ENTRY ungrounded | `SUMMARY legs=9 fail=1 f1_entries=3 rev=eb0c240…` (L2 `grounded=15`)
D2 | ENTRY ungrounded; a stub `corpus/knowledge/jj-keep-ref-stub.md` carries `ground: F1` and is mapped | `SUMMARY legs=9 fail=0 f1_entries=3 rev=3705a8d…`
E | B, but the entry is mapped only in the plain-F1 row `corpus/README.md:39` | `SUMMARY legs=9 fail=0 f1_entries=3 rev=46048b4…`

Real measurements, this seat, jj `0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`, git 2.56.0, scratch repos only:

```
== arm 1: loose keep refs
after_abandon: keep_refs=6 target_ref=present
rc=0 after_DEFAULT_gc_14d: keep_refs=6 target_ref=present
$ jj util gc --expire 2020-01-01
Error: --expire only accepts 'now'
rc=0 after_expire_now: keep_refs=5 target_ref=absent
== arm 2: packed keep refs (git pack-refs before the default gc)
after_abandon: keep_refs=6 target_ref=present
after_pack_refs: loose_keep_files=0 packed_has_target=1
rc=0 after_DEFAULT_gc_14d: keep_refs=5 target_ref=absent
== non-head-operation refusal
$ jj --at-op @- util gc
rc=1
Error: Cannot garbage collect from a non-head operation
```

Replay of the drafted fixture (`.ufo/waves/round-30/w1/deliver-r30-jj-keep-expiry.sh`, run with `TMPDIR` under scratch): `fixture rc=0`; `diff` of its `jj-version`/`git-version`/`RESULT` lines against `.ufo/waves/round-30/w1/deliver-jj-keep-expiry-run.txt` → `IDENTICAL`. An independent reconstruction of the record's repo-1 sequence (commit A, commit B, `abandon @-`, with and without a `git gc --prune=now` step) also gives `keep_refs=7/8/8/6` and `target_keep=yes/yes/yes/no`, so the packing step does not confound the record's step 4.

## Findings

**F1 — L8 is a line-shape check; a typed record passes.** `census/round-30/c3-counter.py:121` `nres = sum(1 for l in run.splitlines() if l.startswith("RESULT "))`; `:122` requires only `RUN in e`, a `jj-version: jj 0.45.1` line, `nres >= 3`, and the substrings `refs/jj/keep` and `util gc` in the entry. Nothing binds the record to a command, a fixture, or the entry's claims. State A: a record whose three RESULT lines contradict the behaviour the record's own cited source describes (`cli/src/commands/util/gc.rs@v0.45.1:55` `None => SystemTime::now() - Duration::from_secs(14 * 86400),`) still scores `legs=9 fail=0`. The prereg's kill rule (`any other SUMMARY is a miss`) has no arm that can see this.

**F2 — L1 does not bind the ground label to the admitted entry.** `c3-counter.py:55` greps every knowledge file (`"^ground: F1\b", V, "--", "corpus/knowledge/"`). State D2 keeps `corpus/knowledge/jj-keep-ref-expiry.md` free of any ground line and puts `ground: F1` on an unrelated stub; L1 reports `f1_entries=3`, L2 reports `grounded=16 mapped=16`, and the SUMMARY hits the target. The claim sentence says "Admit exactly one new entry `corpus/knowledge/jj-keep-ref-expiry.md` with `ground: F1`" (prereg line 9); the counter admits a pair of files instead.

**F3 — the ground token and the map row are unenforced.** `^ground: F1\b` matches `ground: F1-jj` (state B scores identically to A), so plain-F1 coverage and the jj edge class are indistinguishable. `tools/souji-coverage-agreement.py:33` maps both `F1` (`corpus/README.md:39`) and `F1-jj` (`corpus/README.md:216`) rows to k=1, so state E — the entry mapped only in the plain row — also passes. Q56's "the F1 coverage-map row names it" is therefore satisfied by the wrong row.

**F4 — ground attribution: this is F1-jj coverage, not F1.** `PROVINCE.md:63` reads `F1 git-native housekeeping vs receipts — git's own deleters`; the remover measured here is jj's own code, `lib/src/git_backend.rs@v0.45.1:900` ``/// Recreates `refs/jj/keep` refs for the `new_heads`, and removes the other``. `PROVINCE.md:129` `keep-only commits — disclosed, not widened. This is not a jj capability:`; `corpus/README.md:216` `F1-jj jj-colocated lane repos (edge class of F1)`. Against that, `corpus/README.md:46` says `remaining: keep-ref expiry unmeasured, fleet exposure numerator re-census.` under plain F1. Three lane texts, two attributions. The frozen `ground: F1` string picks the attribution PROVINCE's F1 definition does not support.

**F5 — new ground, not restatement (answer to the assigned question).** The mechanism skeleton is already in the held entry: `corpus/knowledge/jj-colocation-receipts.md:30` `Keep refs for current heads are kept.` plus the 14-day default and the `util gc` doc advice; its Limits (`:108`) `The docs read does not state it.` is what the draft closes. Against that, the drafted entry adds facts that are not in §§3/10/Limits: (i) `--expire` accepts only the literal `now` and rejects anything else (`gc.rs:57` `_ => return Err(user_error("--expire only accepts 'now'")),`), reproduced as rc=1 by this seat's replay of the delivered fixture's step 6; (ii) `--expire=now` sets the threshold to zero (`gc.rs:56` `Some("now") => SystemTime::now() - Duration::ZERO,`); (iii) `jj op abandon` reparents descendants and only makes commits unreachable (`cli/src/commands/operation/abandon.rs:34` `/// will abandon the specified operation and all its ancestors. The descendants`); (iv) git gc alone removes neither the keep ref nor its commit, measured; (v) an 8-step measured record where the held entry has only the Limits sentence; (vi) the single-ref-transaction deletion detail. Two facts it leaves open are settled already: `all_heads_for_gc()` is the whole indexed graph, `lib/src/default_index/composite.rs:637` `Ok(Box::new(self.commits().all_heads()))` (measured: 5 keep refs survive `--expire now` while `heads(all())` lists one visible head, which is one of the five), and the packed-ref path is real at the **default** threshold (arm 2: a keep ref created seconds earlier and then packed is deleted by `jj util gc` with no `--expire`). It also omits the non-head refusal (`gc.rs:51` `"Cannot garbage collect from a non-head operation",`, measured rc=1).

**F6 — the draft's record is sound.** Replay of the delivered fixture reproduces the delivered record exactly; my independent reconstruction of steps 1-4 reproduces its numbers. The counterexample states above are counter gaps, not an exploited fabrication in this wave.

**F7 — residual: L4's fetch receipt is self-declared.** `c3-counter.py:108` compares the blob hash with `census/round-30/sources/SHA256SUMS` and `census/round-30/records/fetch-receipts.tsv` rows, all written by the same landing commit; the `http 200` cell is an assertion, not a fetch. Not exploited here (L3 binds quotes to snapshot bytes), so low.

## Attack log

**ATTACK-1 (high, counter).** Counterexample: state A — typed `RESULT` lines that invert the cited source's own default, scored `legs=9 fail=0 f1_entries=3`. Evidence: `c3-counter.py:121-123`; receipt `### A-fabricated-record`. Impacted axis: coverage (the credit is granted without content); calibration and operability untouched. Smallest safe correction: fold a replay into L8 — run the committed `tests/fixtures/r30-jj-keep-expiry.sh` under a scratch `TMPDIR` (the contract already requires that file; the counter never opens it) and require the record's `jj-version`/`git-version`/`RESULT` lines to equal its stdout. Red-before is automatic at base (fixture absent). Feasibility measured: replay takes seconds and the draft passes it; state A fails it.

**ATTACK-2 (high, counter).** Counterexample: state D2 — the target met with the admitted entry carrying no ground line and a stub carrying it. Evidence: `c3-counter.py:55-56`; receipt `### D2-stub-carries-ground`. Impacted axis: coverage. Smallest safe correction: L1 evaluates only the admitted path — `git grep -E '^ground: F1\b' <rev> -- corpus/knowledge/jj-keep-ref-expiry.md` — plus exactly one new grounded file versus base. Target string unchanged.

**ATTACK-3 (medium, counter).** Counterexample: states B and E — `ground: F1-jj` and the plain-row mapping both score the target. Evidence: `souji-coverage-agreement.py:33`, `corpus/README.md:39` and `:216`; receipt `### B-ground-f1-jj`, `### E-mapped-under-plain-F1`. Impacted axis: coverage attribution. Smallest safe correction: require ENTRY to be named by a map row whose ground cell begins `F1-jj` (`mapped_by_k` at `souji-coverage-agreement.py:154` unions all F1 rows; restrict to that row for this entry), while keeping the frozen `ground: F1` string.

**ATTACK-4 (medium, contract attribution).** Counterexample: the claim as frozen attributes a jj deleter to plain F1, whose PROVINCE definition is git's own deleters. Evidence: `PROVINCE.md:63`, `:129`; `corpus/README.md:216`, `:46`. Impacted axis: coverage map honesty. Smallest safe correction: keep the frozen `ground: F1` string, make the entry's claim line name `F1-jj` explicitly, land the map edit on `corpus/README.md:216` (never `:39`), and have the L1 log the `:46` wording as a wave-2 bookkeeping correction.

**ATTACK-5 (low, draft).** Counterexample: the draft's "What this does NOT establish" leaves `all_heads_for_gc()` unsettled and the packed-ref deletion as `[INFERENCE]`, and it never states the non-head refusal — all three are settled by source or by measurement now. Evidence: `composite.rs:637`; arm 2 of the receipt; `gc.rs:51`. Impacted axis: coverage depth (not honesty). Smallest safe correction: add a source row for `lib/src/default_index/composite.rs` and one fixture step (pack refs, then the **default** `jj util gc`), and state the refusal; no target change.

**ATTACK-6 (low, residual).** L4's receipt is self-declared (`c3-counter.py:108`). Correction if hardening is wanted: require the fetch receipt's `fetched_at` to be produced by the landing seat's own run recorded elsewhere, or accept it and state the residual in the entry's Limits. No counterexample built.

## Deliveries
- `.ufo/waves/round-30/w1/SwarmCritic26.md` (this report)
- `.ufo/waves/round-30/w1/SwarmCritic26-c3-scores.txt` (all six counter transcripts, both jj arms, the refusal, the replay diff)

Scratch `/fast/scratch/hyaku/souji-r30/AttackC3/` was removed after the receipt was written; nothing was installed or upgraded.
