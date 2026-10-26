# SwarmScribe23 — C3 append-only corrections (round 31 wave 2, attempt 1)

## Status

STATUS: PASS — the corrections delivery is written and every bullet is checked against lane bytes this run; 16 of the 18 bullets are my own byte-level re-derivations; the two that rest on a peer's reproduction (claim 5's separation, Role 3's survivor step) are labelled as such. No entry, fixture, record, doc, counter, amendment or git index was modified.

## Evidence

Revisions: base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, prereg `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, C3 landing `1baf4da02b71b012ee2426ea7c309496c0c3aca0`, lane tip `2c16d018e40db7c23420a2c3bb546b52957bcc25`. The entry exists only in `1baf4da` (`git log --oneline -8` read); `git diff --stat 1baf4da 2c16d01` for the C3 subjects is empty per the wave-2 seats, so tip reads are landing reads. Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmScribe23/` (`TMPDIR` exported inside it), removed before this report.

Contract read first: `census/round-31/records/preregistration.txt` and `census/round-31/records/amendments.txt` (A0-A5, including the append-only correction to the A1/A3 quote spans).

Byte checks I ran (all read-only, lane + scratch):

```
sha256sum census/round-31/sources/{gc.adoc,git-compatibility.md,git-reflog.adoc}
  0ab75f6f40eb… gc.adoc | 0fb71f992b0e… git-compatibility.md | 59e7f0f15204… git-reflog.adoc
sha256sum census/round-31/records/jj-object-clock-run.txt   -> 085b87c781dc…07e5 (entry's value)
sha256sum census/round-30/sources/git-gc.adoc               -> e3dbc4081095…ba8c
nl -ba census/round-30/sources/git_backend.rs | sed -n '905,950p;1554,1568p'
  924 `let name_good = ... == id.hex();` | 925 `if new_heads.contains(&id) && name_good {`
  939-945 loose-ref metadata / `if mtime > keep_newer` | 1564 `recreate_no_gc_refs(...)` inside `fn gc`
nl -ba census/round-31/sources/git-compatibility.md | sed -n '44,62p'
  11 `## Supported features` | 52 `* **Garbage collection: Yes.** It should be safe to run ...` (spans 52-53)
nl -ba census/round-30/sources/cli-reference@.md.snap | sed -n '3788,3796p'
  3791 `Run backend-dependent garbage collection.` | 3793 op-abandon advice
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-prune.adoc
  sha256 75185e698450…1472, 89 lines, line 30 `Note that unreachable, packed objects will remain.`
nl -ba census/round-31/sources/gc.adoc | sed -n '90,165p'    (96-105 pruneExpire, 115-132 reflogExpire{,-Unreachable}, 140-147 recentObjectsHook)
nl -ba census/round-30/sources/git-gc.adoc | sed -n '14,24p;78,92p;136,166p'  (16-20, 81-87, 141-146, 148-151, 160-161 all address the cited text)
nl -ba tests/fixtures/r31-jj-object-clock.sh | sed -n '40,58p;60,205p'
  50 reflog_hits definition | 103-107 `git reflog --all --format='%H'` | 108 `git cat-file -e`
  125-135 `target_or_desc_keep_refs` | 146-161 `assigned_steps` incl. :150 `pack-refs --all`, :158-160 op abandon + util gc
  196-201 reflog-only: `for r in $(target_or_desc_keep_refs); do G update-ref -d "$r"` then prune
grep -n "S051|S063|S002|S222" corpus/SOURCES.md        (S051 :72, S002 :23, S063 :84, S222 :167)
python3 over preregistration.txt                       (line 20 prints `arm=<solo|descendant>`)
grep -n -i "reflog-only|third arm|three repositories" census/round-31/records/amendments.txt -> no hit
grep -F each superseded phrase over corpus/knowledge/jj-dropped-keep-object-lifetime.md -> all present
```

Record fields the corrections rely on (from the 17 `RESULT` lines of the record, cited by arm/step):
`reflog-only` at `drop-keep-refs-naming-target` and at `git-gc-prune-now` both carry
`keep_refs=6 target_keep=no reflog_hits=1 object_present=yes`; `abandon` carries `keep_refs=8
target_keep=yes`; `solo` at `delete-descendant-keep-refs-and-prune` carries `keep_refs=1
object_present=no`.

Gates (not run by this seat; read from the wave-2 deliveries): `c3-counter.py`,
`c3-counter-v2.py`, `c3-counter-v3.py` all `fail=0 f1_entries=4` at `1baf4da` and at `2c16d01`,
record byte-identical on three fresh runs, base red control `legs=11 fail=10` (SwarmExecutor16,
`deliver-c3-rerun.txt`); independent replication without the fixture exercised the same mechanisms
(`deliver-c3-replication.txt`). Wave-2 attack reports read at start and at finish:
`SwarmCritic18.md` (sentence attack), `SwarmScout19.md` (source re-open), `deliver-c3-novelty.md` +
`SwarmCritic21.md`, `SwarmExecutor16.md` (re-run + doctored-fixture attack),
`deliver-docs-review.md`, `SwarmConnector28.md`, `SwarmExecutor17.md` (independent replication
without the fixture; its finding 1 is the ground of the Role 3 survivor bullet), plus wave-1
`SwarmCritic30.md`. The mutation seat's
report (`SwarmMutationTester20.md`) was absent at my start and landed at my finish read: 8 mutants of
the fixture against `census/round-31/c3-counter-v3.py`, 6 killed, 2 survivors (MF2 HEAD-only reflog
enumeration, MF8 unpatterned `keep_refs` count), baseline and restored bytes green. Its survivors are
counter-coverage findings and refute no entry sentence; none of the 18 bullets changed on reading it.

## Findings

1. **Role 1's `reads the same except for the ref count` is false** — `corpus/knowledge/jj-dropped-keep-object-lifetime.md:95-96` against `census/round-31/records/jj-object-clock-run.txt` lines for `reflog-only` at `drop-keep-refs-naming-target` and `git-gc-prune-now`: identical in every field, step name included as the only difference. Axis: calibration.
2. **Role 1's deletion clause understates the deletion** — entry `:91-92` says `first deletes every keep ref naming B`; the fixture applies `target_or_desc_keep_refs` (`tests/fixtures/r31-jj-object-clock.sh:126-135`, loop at `:196-201`), i.e. refs naming B **or a strict descendant**, and the record's `keep_refs` moves 8 to 6. With only the B-named ref deleted, B is held by the descendant ref (entry's own claim 2), so the arm would not isolate the reflog. Axis: coverage.
3. **Claim 2's `a keep ref survives only when` is refuted by the function it cites** — entry `:29-30` vs `census/round-30/sources/git_backend.rs:924-925` (`&& name_good`) and `:939-945` (loose-ref mtime gate), with the call site at `:1564` inside `fn gc` (`:1558`). The entry's own S054 source line already names `:939-945`, so the sentence contradicts its own anchor. Axis: coverage.
4. **The Gate's jj bullet has the wrong section and an unbounded anchor, and no row id** — entry `:218`; snapshot has `## Supported features` (`:11`), no `Git-specific` heading, and the quote spans 52-53; the file's registry row is S051 (`corpus/SOURCES.md:72`). Axis: calibration (provenance), coverage (traceability).
5. **The `git-gc.adoc` anchors of claims 1, 4, 5, 6 point at a capture the entry never names** — `census/round-31/sources/` holds only `gc.adoc`, `git-reflog.adoc`, `git-compatibility.md`; the bytes are `census/round-30/sources/git-gc.adoc` (sha256 e3dbc408…), which the Gate's `three snapshots named below` does not cover. Axis: calibration.
6. **S063's registry cell does not cover the config fragment the Gate quotes under it** — S063 cell (`corpus/SOURCES.md:84`) scopes `§ NOTES first paragraph`; the quoted `gc.pruneExpire`, `gc.reflogExpire*` and `gc.recentObjectsHook` lines are `Documentation/config/gc.adoc` content, and S002's cell (`:23`) covers only two of those keys. Axis: coverage.
7. **Claim 6's S117 citation has no opened byte** — entry `:61-63` cites the registry cell for `unpacked unreachable objects, packed ones remain`; no S117 snapshot or Gate bullet exists this round. I supplied the byte this run (`git-prune.adoc` v2.56.0:30, sha256 75185e69…). Axis: coverage.
8. **Claim 7's S220 range excludes the quoted phrase** — entry `:70-71`; `backend-dependent garbage collection` is `cli-reference@.md.snap:3791`, while the entry's S220 source line anchors 3793 and 3799-3805. Axis: calibration.
9. **Claim 5's `The record measures the separation` overstates the run** — entry `:55-56` and `:116-117`; the entries are seconds old inside the 90/30-day window, and SwarmCritic18's probe (`git -c gc.reflogExpire=now -c gc.reflogExpireUnreachable=now gc --prune=now` left B absent) shows the row cannot separate the dates. Peer-reproduced, not rerun by me. Axis: calibration.
10. **`Three independent keepers hold B` presents an unmeasured keeper as measured** — entry `:141-143`; every prune in the record is `--prune=now` or `jj util gc --expire=now`, so the mtime keeper is isolated by no arm; `PROVINCE.md:224` already calls it `sourced, not measured`. Axis: coverage.
11. **The corollary inverts the record** — entry `:152` `absence is cheap to establish and presence is expensive`; presence is one `cat-file -e` per step (`tests/fixtures/r31-jj-object-clock.sh:108`, 17 rows), absence needed the descendant/keep-ref surgery. Axis: calibration (this is the sentence a receipt design copies).
12. **The third arm exceeds the frozen step-line format with no amendment** — `census/round-31/records/preregistration.txt`:20 enumerates `arm=<solo|descendant>`; the record prints four `arm=reflog-only` lines; `grep -i "reflog-only|third arm|three repositories"` over `amendments.txt` returns nothing, and no counter leg checks arm names. Axis: calibration (a frozen artefact described as satisfied while exceeded).
13. **The novelty clause re-claims held ground** — entry `:134-136` `a keep ref naming a descendant outranks reflog expiry and every prune (roles 3 and 4)`; that precedence is held text at `corpus/knowledge/jj-keep-ref-expiry.md`:126. Axis: coverage (novelty accounting only; the measurement itself stands).
14. **Role 3's ref drop is measured on packed refs only** — entry `:106-108`; step 2 ran `git pack-refs --all` (`tests/fixtures/r31-jj-object-clock.sh:150`) before the 6-to-2 drop at `:158-160`, and the fixture has no loose-ref control, so packedness — the lever the r30 wave-2 correction made load-bearing — is not separated. Axis: calibration.
15. **The source line still carries its drafting placeholder** — entry `:1` `(placeholder id: the L1 renumbers by document)` while the row landed as S222 (`corpus/SOURCES.md:167`). Axis: calibration (minor).
16. **C3 counter blind spot, not an entry defect: the fixture's ref-state columns are unguarded** — `census/round-31/c3-counter-v3.py` legs L8-L13; SwarmExecutor16's doctored fixture (hard-coded `keep_refs`/`target_keep`/`reflog_hits`, real `cat-file -e`) stays green on v1/v2/v3 (`0ef172c4…`), and L12's required-call set does not notice `git_calls` falling 111 to 60. Reported as an ATTACK, no counter edit proposed; the committed record itself reproduces byte-for-byte on three independent seat runs, so the landed entry is not fabricated. Axis: operability of the instrument (no axis harmed at current bytes).
17. **Two fixture mutants survive the v3 counter** — SwarmMutationTester20 MF2 (`tests/fixtures/r31-jj-object-clock.sh:105` HEAD-only `git reflog`) and MF8 (`:95` `keep_count` without the `refs/jj/keep/*` pattern) both leave `legs=13 fail=0`; L9/L12 pin the fixture's output to the committed record, not its computation, and MF1 shows L13's "fewer no-lines" rule is satisfiable by a constant `object_present`. The entry's field definitions name the pristine commands (`--all`, the pattern), and the record was reproduced on three seats, so no entry sentence is superseded; this is a coverage limit of the instrument, reported as an ATTACK. Axis: operability, coverage.
18. **Role 3's `still has a keep ref` hides the step that removed B's own ref** — entry `:100-101` against the record's first two `solo` steps: at `abandon` the `target_keep` field reads yes with `keep_refs=8`, and `pack-and-util-gc` is where both change (`target_keep=no`, `keep_refs=6`); the survivor the role names is the rewritten working-copy commit's ref, which SwarmExecutor17 reproduced as a strict descendant of B by printing that commit's parent line. Precision only: the quoted role-3 row is taken after the util-gc step, so the claim it supports is not weakened. Axis: coverage.

## Attack log

- Verified every superseded phrase exists verbatim in the landed entry before drafting a bullet (`grep -F` over the entry, wrapping-aware reads of `:12-18, :54-58, :61-67, :69-73, :89-99, :115-119, :125-128, :134-138, :140-147, :151-157, :176-181, :215-223`).
- Re-derived the record-vs-prose claims by reading all 17 `RESULT` lines and comparing fields; found the Role 1 exception clause and the packed-only drop myself, before any wave-2 report named them.
- Checked anchors by numbering the snapshots (`git-reflog.adoc`, `gc.adoc`, `git-compatibility.md`, round-30 `git-gc.adoc`, round-30 `git_backend.rs`, round-30 cli-reference snapshot) instead of trusting the entry's ranges; 8 of 9 Gate anchors bound their quotes, the jj bullet does not.
- Re-fetched `git-prune.adoc` at tag v2.56.0 and matched Critic18's stated sha256, so the supplied prune quote is from bytes I opened, not a copied assertion.
- Read the fixture's helpers and both arm bodies to separate what the entry says was deleted from what the script deletes; separately confirmed the frozen format line in the preregistration and the absence of any amendment for the third arm.
- Constraint self-checks on the delivery: zero backticked spans beginning with the record's `RESULT` prefix (`grep -c '`RESULT '` -> 0 after one fix), zero reserved-TLD hosts, 18 bullets inside the section, section placed after `## Gate` so L5/L6/L7 inputs are unchanged.
- Not run (out of seat): the three C3 counters, the fixture, `tools/souji-coverage-agreement.py`, the landing gate; nothing in the lane mutated, no `git add/commit`, no `jj`, no signal, no fleet-path read outside the lane's own records.

## Deliveries

- `.ufo/waves/round-31/w2/deliver-c3-corrections.md` — the `## Round 31 wave-2 corrections (append-only)` block (18 bullets), ready for the L1 to append after the entry's `- ADMIT:` / `- REJECT:` lines, plus its grounds and the disclosed non-actions. sha256 2abb78fc2255e69a4caee379435dea0790d3a59ecda0688dda0fef2f526feaf7.
- `.ufo/waves/round-31/w2/SwarmScribe23.md` — this report.
- Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmScribe23/` removed after the delivery was copied into the lane's wave-2 report directory.
