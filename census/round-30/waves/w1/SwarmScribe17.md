# SwarmScribe17 — round 30 w1, documentation for the C3 entry (F1 keep-ref expiry)

## Status

STATUS: PASS — the four requested documentation texts are drafted in one delivery file, each
after reading its target section; no lane file was modified, and the C3 entry itself
(`corpus/knowledge/jj-keep-ref-expiry.md`) is another seat's and is absent at the lane tip, so
every reference to it in the draft is a forward reference the L1 must land in one commit (Q56).

## Evidence

Read-only against the lane; working tree equal to master for the three target docs
(`git status --porcelain -- corpus/README.md PROVINCE.md SKILL.md` → empty).

| command | output excerpt | revision |
|---|---|---|
| `git -C <lane> rev-parse refs/heads/master` | `df6afe817d096e4ad71ba2b9cc21a83f126eb658`; `git merge-base --is-ancestor 9420341d… master` → yes | master df6afe8 (base 9420341, then d4928ec prereg, bae103c controls, df6afe8 r29-D3 receipts) |
| `awk 'NR>=35&&NR<=44' corpus/README.md` | row `39` is `F1 git-native housekeeping vs receipts` / `frontier, entries held` / four backticked entries; 272 chars at `master:corpus/README.md:39` | df6afe8 |
| `git -C <lane> cat-file blob master:corpus/README.md \| grep -c jj-keep-ref-expiry` | `0`; `grep -c '^## Round 30'` → `0` | df6afe8 |
| `git -C <lane> cat-file -e master:corpus/knowledge/jj-keep-ref-expiry.md` | `fatal: path … does not exist in 'master'` | df6afe8 |
| `grep -nE '^\| *S2[0-9]{2} *\|' corpus/SOURCES.md \| tail` | last row `S219`; count `143` — no round-30 source rows exist yet | df6afe8 |
| `jj --version` | `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5` | host, this run |
| `jj util gc --help` | three lines re-read: the `op abandon` sentence, the two-week default, the `now`-only sentence | host, this run |
| `grep -n expire .ufo/waves/round-30/w1/sources/cli-reference@.md.snap` | `--expire <EXPIRE>` at `:3799`; section text at `:3793`, `:3801`, `:3803` agrees byte-for-byte with the live help output | w1 snapshot |
| `cat .ufo/waves/round-30/w1/deliver-jj-keep-expiry-run.txt` | `jj-version: jj 0.45.1…`, `git-version: git version 2.56.0`, 8 `RESULT` lines: keep_refs `7,8,8,6,2,8,8,6`, `target_keep` `yes,yes,yes,no,no,yes,yes,no`, `object_present=yes` in all 8 | wave-1 delivery (not re-executed by this seat) |
| `grep -n '^- \*\*jj:' SKILL.md` | bullets at `:113`, `:114`, `:115`, `:116` — insertion point after `:114` | df6afe8 |
| `wc -l` | `corpus/README.md` 596, `PROVINCE.md` 193, `SKILL.md` 395 — append anchors are the file ends | df6afe8 |
| `grep -n 'Q56' corpus/QUALITY.md` | `:135`: a grounded entry and its map row land in the same commit; a status-cell mention does not map | df6afe8 |
| `grep -n 'MISSING-FROM-MAP\|DANGLING-MAP-PATH' tools/souji-coverage-agreement.py` | `:6` a knowledge path is a backticked entries-cell span ending `knowledge/<name>`; `:7`, `:8` the two findings | df6afe8 |

The fixture's numbers in the draft are transcribed from the wave-1 run record and the mechanism
receipt, not re-measured by me: I did not run `deliver-r30-jj-keep-expiry.sh`.

## Findings

1. **The F1 row needs one cell change, not two.** `corpus/README.md:39` already carries the
   requested status wording `frontier, entries held` and four backticked entries; only the
   entries cell changes, by appending `` `knowledge/jj-keep-ref-expiry.md` ``. Location:
   `corpus/README.md:39`.
2. **Item 1 is a counter leg, not style.** `census/round-30/c3-counter.py` leg L2 requires
   `grounded=16 mapped=16 dangling=0 mismatches=0`; the tool maps an entry only through a
   backticked `knowledge/<name>` span in an `entries`-headed row whose ground cell starts with
   `F<k>`. Without the row edit the new entry is `MISSING-FROM-MAP`. Location:
   `census/round-30/c3-counter.py` (L1/L2), `tools/souji-coverage-agreement.py:6-8`.
3. **The entry, not these docs, must carry `ground: F1`.** Leg L1 counts files in
   `corpus/knowledge/` with a `ground: F1` line and expects 3. Location:
   `census/round-30/c3-counter.py` L1.
4. **Two measured facts the docs may state, and one they may not.** `git gc --prune=now` left
   the keep ref naming the abandoned commit (`target_keep=yes`, step 3); `jj util gc
   --expire=now` removed it (step 4); `jj op abandon ..@-` plus a second `jj util gc
   --expire=now` left 2 keep refs where 8 stood (step 5); `object_present=yes` at every step, so
   object pruning is NOT measured and the draft says so. Locations:
   `.ufo/waves/round-30/w1/deliver-jj-keep-expiry-run.txt`, `receipt-SwarmExecutor06-keepref-mechanism.txt`.
5. **The `--expire` control is a rejection, not a future timestamp.** jj 0.45.1 prints "Only the
   string "now" can be passed to this parameter." and the fixture's step 6 records `rc=1`
   rejected; the not-yet-expired arm is the default-threshold run (step 7). Locations:
   `jj util gc --help` this run; `.ufo/waves/round-30/w1/sources/cli-reference@.md.snap:3803`;
   the doc sentence "run `jj op abandon ..<some old operation>` before `jj util gc`" is at
   `:3793` and the two-week default "By default, only obsolete objects and operations older
   than 2 weeks are pruned." at `:3801`.
6. **The r17 entry's inference is now superseded in effect, not rewritten.**
   `corpus/knowledge/jj-colocation-receipts.md` §3 labels the keep-ref timing `[INFERENCE]` and
   its `Limits` first bullet says the docs read do not state the lifetime; the r30 correction
   note records the measured timing and leaves the r17 bytes alone (append-only). Location:
   `corpus/knowledge/jj-colocation-receipts.md` §3, `## Limits` bullet 1.
7. **One entry does not promote F1.** The draft keeps Core as the `## Owns` / `## Work surfaces`
   list (`PROVINCE.md:60`), keeps the row status, and states that jj's own store GC is out of
   scope; no `tools/` change and no receipt class. Locations: `PROVINCE.md:60`, `:58-88`.
   The remaining F1 item stays the fleet exposure numerator re-census named at
   `corpus/README.md:46`; I added the object-prune clock as a disclosed non-measurement rather
   than a new claim (that wording is the L1's call, flagged here for it).
8. **Anchor discipline for the L1.** Other round-30 docs may append to the same files, so each
   edit in the delivery names a unique text anchor and a line number as of `df6afe8`: item 1
   matches once; item 2 appends after line 596 (end of README); item 3 after `PROVINCE.md:193`;
   item 4 is inserted between `SKILL.md:114` and `:115`.
9. **Not drafted, named as out of scope.** A `SKILL.md` `## Gate registry` row for
   `r30-jj-keep-expiry` (the C3 counter reads the entry's Gate and the fixture, not the
   registry); the `corpus/SOURCES.md` rows, whose S-ids the L1 assigns at integration — the
   delivery cites no S-id so the entry's `source:` line stays the single authority; the
   `corpus/lessons/round-30.md` and the C1/C2 README sections.
10. **Path provenance inside the delivery.** `../census/…` appears only inside fences that are
    `corpus/README.md` text, because the landing gate normalizes a relative pointer against the
    citing document's directory (`tools/souji-landing-gate.py:801-806`); the delivery file is
    not a report and is not a gate input, and the draft's own paths use lane-root form.

## Deliveries

- `.ufo/waves/round-30/w1/deliver-docs-f1.md` — items 1-4 (row replacement, appended README
  section with `### Frontier (r30)` and `### Round 30 corrections`, PROVINCE boundary
  paragraph, SKILL error-pattern bullet), plus the out-of-scope list above.

## Notes

- No tool install or upgrade; no `pacman` transaction; no credentials, no `/proc` census, no
  `.scratch/` or `.ufo/state/` reads. Scratch `TMPDIR=/fast/scratch/hyaku/souji-r30/SwarmScribe17`
  was used only for the `jj util gc --help` read and is removed (`ls` → no such file or
  directory).
- Lane writes: only the delivery file and this report. No `git add/commit/push`, no `jj`
  mutation, no signal.
