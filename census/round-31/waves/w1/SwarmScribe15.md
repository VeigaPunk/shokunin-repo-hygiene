## Status

STATUS: PASS — C3 entry draft delivered at `.ufo/waves/round-31/w1/deliver-entry-jj-dropped-keep-object-lifetime.md` (20158 B, sha256 `49b7912be6b054be75854e82c80f82494671538434534f55d66189551845484f`). It passes the assimilation gate in a scratch rehearsal, every entry-side leg of `c3-counter.py` that can be evaluated before a landing rev is green including a whole-line L10 match against the run record, and its Observed section quotes six whole `RESULT` lines read from the fixture seat's record.

## Evidence

Frozen contract read first: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-31/records/preregistration.txt` (C3 paragraph, line 20; lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, prereg `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`). Lane head at read time via read-only `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -1` → `1b81136 round-31: C1 base output and M1 red-before receipt`.

Sources opened this run (fetch + hash, in my scratch, `TMPDIR=/fast/scratch/hyaku/souji-r31/SwarmScribe15{,b,c}/tmp`):

```
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-reflog.adoc     -> 59e7f0f15204a8c9f9b058ee62cb26aa2fa726b35dc85c702b75243424d6bf54  5657 B
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc     -> 0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a  7753 B
curl -fsSL https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/git-compatibility.md      -> 0fb71f992b0ed05d547e597d3f5f1cd33ed9e5d56a4e4e4cb851ba30c766c641 12284 B
curl -fsSL https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs         -> 95147270e5bc2a689e1191256c0f214d8e52ac6d4523756eb6b8ec8113d86c69 (identical to S054's round-30 capture)
curl -fsSL https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/src/commands/util/gc.rs    -> 9c4d6a3704abb6f3afbb63cfd44153437b83d7e68d0f2426f84f8cdbbb0b4b9b
```

Run record read at `.ufo/waves/round-31/w1/deliver-jj-object-clock-run.txt` (the seat's delivery; L1 installs it at `census/round-31/records/jj-object-clock-run.txt`): 19 lines, sha256 `085b87c781dcd323a1576ee92a4a2779c1fa69dce3b62e978e0db315bad207e5`, line 1 `jj-version: jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`, line 2 `git-version: git version 2.56.0`, lines 3-19 the 17 `RESULT` lines over arms `solo`, `descendant`, `reflog-only`.

Quote verification: every double-quoted span in the entry (Gate and body) is a whitespace-squashed substring of the file its line cites, and none is under 4 words. Gate: 9 spans, word counts `23 6 11 10 10 11 14 11 16`, no interior double quotes, no pipe. L10 shape check: 6 backticked `RESULT` spans, all six whole lines of the record (`grep -Fx` equivalent), with both `object_present=yes` and `object_present=no` represented.

Gate rehearsal in scratch (export + the three peer-pinned snapshots + the record at its install path + a **stub S222 row** appended to a scratch copy of `corpus/SOURCES.md` + the entry at its integration path):

```
python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-26 \
  --entries corpus/knowledge/jj-dropped-keep-object-lifetime.md --snapshot-dir census/round-31/sources \
  --slice census/round-31/records/empty-slice --slice-verdicts census/round-31/records/empty-verdicts
entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0    rc=0
```

Entry-side counter legs emulated on the same scratch copy: L4 `sha_ok=True` for all three snapshots against `.ufo/waves/round-31/w1/sources/SHA256SUMS` (5657/7753/12284 B); L5 `bad=[]`; L6 `cited=['S002','S054','S063','S117','S220','S222'] missing=[] fresh=['S222'] url_unbound=[]`; L7 `[]`; L8 preconditions on the record hold (version lines, 17 `RESULT`, both yes and no); L10 `result_spans=6 not_in_record=[]`; `ground: F1` on line 9; `|` count 0.

Two corrections from `SwarmExecutor08` are folded in. (i) Seconds after my first draft, the seat reported that `solo step=reflog-expire-then-prune` is still `object_present=yes` — the removal I had put in `solo` belongs to a third repo, arm `reflog-only`, because the assigned four-step order expires the reflog before any descendant ref is dropped. (ii) The run record then landed and I read it: the six `RESULT` spans are copied from those bytes, and the run measures what step 5 previously only inferred (`git-gc-prune-now` leaves `reflog_hits=1` in all three arms).

Not run, and not claimed: `census/round-31/c3-counter.py` and `c3-counter-v2.py` at any rev (L1/L2/L9/L11/L12 need the landing rev, the committed record, the fixture and the registry row); no `jj` invocation at all; no lane command beyond read-only `git log`; I did not run the fixture, so no `RESULT` value is a measurement I performed — the spans are read from the seat's record.

Tooling: no install or upgrade this run (`curl`, `bash`, `python3 -B`). Scratch dirs `/fast/scratch/hyaku/souji-r31/SwarmScribe15`, `SwarmScribe15b.*`, `SwarmScribe15c.*` removed after delivery.

## Findings

1. **Snapshot basenames are fixed by the snapshot seat, and my draft matches them.** `SwarmExecutor09` pinned `git-reflog.adoc`, `gc.adoc`, `git-compatibility.md` under `.ufo/waves/round-31/w1/sources/` with a `SHA256SUMS` carrying exactly those basenames; the draft names those three and nothing else, so L4 needs no extra `SHA256SUMS` or `fetch-receipts.tsv` row from me. My `Documentation/config/gc.adoc` fetch is byte-identical to their `gc.adoc` (`0ab75f6f…`).
2. **The config quotes carry the `git-gc(1)` URL, not a new row.** `census/round-30/sources/git-gc.adoc:136` is `include::config/gc.adoc[]`, so `gc.pruneExpire`, `gc.reflogExpire` and `gc.reflogExpireUnreachable` bytes are part of the `https://git-scm.com/docs/git-gc` page that S002 and S063 already bind; L6's `url_unbound` is empty for that reason, and no registry row beyond S222 is owed.
3. **L6's freshness leg rests entirely on S222.** The row the L1 adds for git-reflog must keep `opened=2026-10-26` and its source cell must contain the exact string `https://git-scm.com/docs/git-reflog`, or both `fresh` and `url_unbound` go red. My `source:` line marks the id as a placeholder to be renumbered by document.
4. **A descendant keep ref outranks both removers, and the record shows it three ways.** `solo step=reflog-expire-then-prune` is `reflog_hits=0 object_present=yes`; `solo step=op-abandon-and-util-gc` drops `keep_refs` 6 to 2 and still leaves B; deletion appears only at `solo step=delete-descendant-keep-refs-and-prune` (`keep_refs=1`, `object_present=no`), and in `descendant` only at `abandon-descendant-and-op-abandon-and-util-gc`, staying `no` at `git-gc-prune-now-again`. The receipt rule in the entry now demands prune date + reflog state + keep-ref state for that reason.
5. **Reflog reachability is isolable only in the third repo.** `reflog-only step=git-gc-prune-now` is `reflog_hits=1 object_present=yes` after every keep ref naming B was deleted, and `reflog-only step=reflog-expire-then-prune` is `reflog_hits=0 object_present=no`. Without that arm the entry would have no measurement of a reflog entry holding an object on its own.
6. **`--prune=now` does not expire the reflog — measured, not inferred.** `git-gc-prune-now` leaves `reflog_hits=1` in all three arms; only the explicit `git reflog expire` step reaches 0. That upgrades the entry's step 5 from `[INFERENCE]` to an observation of this run and is the basis for refusing a prune invocation as evidence of an empty reflog.
7. **jj's lever sets only the object date.** `lib/src/git_backend.rs:974-977` builds `git --git-dir=. gc` with `format!("--prune=@{} +0000", keep_newer.as_secs())`, and `cli/src/commands/util/gc.rs:54-58` derives `keep_newer` from `--expire` alone; the reflog dates come from `gc.reflogExpire`/`gc.reflogExpireUnreachable` (`git-reflog.adoc:111-127`, `gc.adoc:115-132`).
8. **The junk control's arm names are not the fixture's.** `census/round-31/controls.sh:71-74` emits only `arm=solo step=a|b|c` and `arm=descendant step=c`; the record uses `solo`, `descendant`, `reflog-only` with nine named steps. Field order matches, naming does not — the L1 must fill or confirm spans from the record, never from the control. (My first draft's role order came from that control and was wrong; finding 5 is the fix.)
9. **The run record is a delivery file, not yet the counter's path.** It sits at `.ufo/waves/round-31/w1/deliver-jj-object-clock-run.txt`; L8/L9/L10 read `census/round-31/records/jj-object-clock-run.txt`, so the L1 must install these bytes unchanged or the entry's six spans and the record diverge.
10. **Fragility, not a defect: L4 keys `SHA256SUMS` by basename and receipts by full path.** A snapshot named `gc-config.adoc` instead of `gc.adoc` would pass gate-check (file exists, quote present) and fail L4 silently on `sums.get(basename)`. The draft avoids the trap.

## Attack log

Not an attack seat. Finding 10 is a fragility note with its reproduced condition, not an ATTACK: no predicate, target or case set is claimed wrong, and I changed nothing.

## Deliveries

- `.ufo/waves/round-31/w1/deliver-entry-jj-dropped-keep-object-lifetime.md` — the C3 entry draft to integrate at `corpus/knowledge/jj-dropped-keep-object-lifetime.md`; sha256 `49b7912be6b054be75854e82c80f82494671538434534f55d66189551845484f`. L1 must (a) install `deliver-jj-object-clock-run.txt` at `census/round-31/records/jj-object-clock-run.txt` byte-unchanged, (b) resolve the S222 placeholder to the row it commits, with the git-reflog URL in its source cell and `opened=2026-10-26`. No span substitution is left over: the six `RESULT` quotes are already whole record lines.
- `.ufo/waves/round-31/w1/SwarmScribe15.md` — this report.

Out of scope, untouched: `corpus/`, `SCORECARD.md`, `PROVINCE.md`, `census/round-31/*` counters and records, the lane index and jj state, `/home/vgpnk/Projects/shokuknow`, and everything under `/home/vgpnk/Projects/shokunin` outside `souji-shokunin/`.
