# ExecShonenFile — round-26 SHONEN section + L1 `--check` assertions

## Status

STATUS: PASS — four `[~]` lines drafted (one per `SHONEN.md` box) with every pointer resolved against the lane tip bytes, plus a 20-assertion `--check` list whose shape, pointer and value arms all pass and whose negative arms discriminate; one delivery file written, no lane file touched.

## Evidence

Lane tip at read time: `0c92c2e6fbe18f2f3009504d87240b6a22ad3d5b` (prereg frozen at `89e0fcee`, 14 commits since; `git rev-list --count 89e0fcee..HEAD` = 14). The tree moved twice under this seat (`9a6e0f1`, `166baa1`) while it ran; every pointer assertion below was re-run at the current tip `166baa18f808071bc385187691713044a26bd663` and returns the same values. `SHONEN.md` itself is unmodified by this round.

Delivery file: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/shonen-lines.md`, written by this seat and swept into commit `166baa1` by the integrator (`git diff HEAD --` on it is empty); this seat ran no `git add`/`commit`.

```
$ grep -c '^- \[~\]' SHONEN.md                      -> 4      (box count)
$ grep -cE '^- \[[ x]\]' SHONEN.md                  -> 0      (no [x]/[ ] in checklist)
$ sed -n '42p;78p;147p;167p' SKILL.md | grep -cE '^## (Decision tables|Error patterns \(false-SAFE signatures\)|Checklists|Gate registry)'
                                                     -> 4
$ sed -n '121,124p' corpus/SOURCES.md | grep -cE '^\| *S10[0-3] '   -> 4
$ sed -n '149,153p' corpus/SOURCES.md | grep -cE '^\| *S1(28|29|30|31|32) '  -> 5
$ sed -n '25p'  corpus/lessons/round-21.md | grep -c '^## Gate'                    -> 1
$ sed -n '38p'  corpus/lessons/round-21.md | grep -c '^### Boundaries and teaching' -> 1
$ sed -n '362p' LOG.md | grep -c '^## 2026-10-19 — operator sweep (execution)'      -> 1
$ sed -n '1723p' LOG.md | grep -c '^## 2026-10-25 — Round 25 honest stop'           -> 1
$ sed -n '161p' PROVINCE.md | grep -c '^### Round21 privacy boundary'               -> 1
$ python3 -B -c "...accepted-matrix.json: scenarios==3, replayed==3, [matched_command_count]==[18,18,18]"  -> rc 0
$ python3 -B -c "...remote-source-after.json: all_matched is True"                  -> rc 0
$ grep -c '^markers=0$' census/round-26/records/c1-after.tsv                        -> 1
$ grep -c '^registry_rows=132$' census/round-26/records/c2-after.tsv                -> 1
$ grep -c '^cases=12 pass=12 control=FALSE-GREEN-REJECTED$' census/round-26/records/c3-after.tsv -> 1
```

Assertion self-test (scratch under `/var/tmp/souji-r26-ExecShonenFile/`, a synthetic report built from the drafted section, since removed):

```
A1=1  A2=4  A3=0  A4=4  A5=0  A6=## SHONEN     (all 20 A/B/C assertions pass)
negative arms: drop-[x]->A3=1; drop-one-[~]->A2=3; ## Shonen->A1=0
```

Raw receipt values quoted above are the committed receipt bytes (`rev=07f83e6`/`e0f8dcd`/`c594901` inside the tsv headers); this seat ran no lane counter and re-ran no receipt.

## Findings

1. **The scout's slot produced nothing to read.** `ScoutShonen` is registered with no agent: `.ufo/waves/round-26/w1/swarm-registry.json` → `"ScoutShonen": {"kind": "spawn", "agentId": null, ...}`, and no `ScoutShonen*.md` exists in `.ufo/waves/round-26/w1/`. The four lines were therefore derived here from `SHONEN.md` + the lane bytes, not copied from a scout.
2. **All four boxes stay `[~]`; none moves to `[x]`.** Promotion is operator-owned and the round-25 D4 note only calls the boxes *plausibly* non-author checkable next round (`corpus/lessons/round-25-verifier-spotcheck.md:74`). The drafted section carries zero `[x]` and the assertion list forbids one (A3).
3. **Box 2's original pointer was a bare line number in a growing file.** `SHONEN.md` box 2 cited `LOG.md:362` with no anchor text; `LOG.md` grows by appending, so a stale number would read as a passing pointer. The drafted line carries the heading text *and* the number, and B6 asserts both (closing the class of defect raised as r17-style line drift).
4. **Box 3's `18/18` was unverifiable from the pointer as written.** `SHONEN.md` box 3 says "each18/18"; the number is not in the named sentence but in the records: `census/round-21/accepted-matrix.json` → `records[].matched_command_count` = 18 for S1/S2/S3 with `all_matched: true`. The line now names that field, and C1 asserts it. `census/round-21/remote-source-after.json:all_matched` is also `true` (C2).
5. **Box 1's source pointer now spans two rounds.** The checklist names `corpus/SOURCES.md` S100-S103; this round appended S128-S132 at `corpus/SOURCES.md:149-153`, which the drafted line adds as additional evidence without retiring the original pointer (B2 4/4, B3 5/5).
6. **Box 4 gained fresh round-26 cover.** `.ufo/waves/round-26/w1/ConnSiblings.md` (STATUS PASS, 21 lanes, zero collision, every verdict `routed`) was untracked when scanned and is committed at `166baa1`; the line pairs it with the committed r21 triad (`PROVINCE.md:161`, `.ufo/waves/round-21/w1/ConnSiblingOverlap.md`, `corpus/lessons/round-21.md:38`), so box 4 resolves even if the wave file is later reorganized.
7. **The filing check must run against the filed bytes, not this draft.** At read time the tree was moving: `git diff --stat` showed two knowledge entries with +9 uncommitted lines each and 68 untracked `w1/` files, and an earlier `git status` showed the two `c3-*.tsv` receipts modified; both conditions were closed by `9a6e0f1` and `166baa1` before this seat finished. None of those paths touch `SHONEN.md`, `SKILL.md`, `LOG.md`, `PROVINCE.md` or the cited `corpus/SOURCES.md` line ranges, and B1-B8/C1-C5 return identical values at `0c92c2e` and `166baa1` — but A1-A6 belong to the filed revision, so run them there, not against this draft.
8. **The `ConnSiblings` scan predates the C2 Gate fix; the failure it recorded is closed.** At `ba8b54b` the K2 gate returned `check1-no-gate` twice (`entries=2 ok=0 fail=2`, rc 1; `.ufo/waves/round-26/w1/ConnSiblings.md` §Evidence). `33e6807` added Gate sections to both entries and `9a6e0f1` committed `census/round-26/records/c2-gate.tsv` (rev `33e6807`, `rc=0`, `entries=2 ok=2 fail=0`). Not a SHONEN defect — no drafted line asserts C2 — but the L1 must not read the SHONEN `[~]` set as cover for an unadmitted claim.
9. **Two frozen literals the report contract should keep distinct.** A2 uses the round-25 column-0 form (`^\[~\]`); the round-24 filing used `- [~]`. The assertion list names both forms and forbids mixing them, so a form change cannot silently halve the count.
10. **No tool installs or updates this run**; no `pacman`, no credentials, no `/proc` census, no campaign-tree writes. Scratch `/var/tmp/souji-r26-ExecShonenFile/` created and removed.

## Attack log

None filed. No frozen predicate, target, case set or axis is contested here; C1/C2/C3 predates this seat and nothing in this section scores them.

Report: .ufo/waves/round-26/w1/ExecShonenFile.md
