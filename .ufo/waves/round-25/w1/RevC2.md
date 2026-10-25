# RevC2 — falsify C2 (size-census refusal surfaces), souji round 25 wave 1

## Status
STATUS: PASS — I ran all five attacks. Nothing falsifies C2 at the tip (12/12 under ExecC2's draft, rc 0). Three findings limit what the claim can say: 7 of 10 tool-clause mutants also score 12/12; the envelope disclosure is worded too broadly; and amendment 2 §3 describes a manifest gate on cases 11/12 that neither draft has.

## Evidence
Lane HEAD during review: de736c2 (prereg frozen at 6e4737e, amendments 1 and 2 at 1814de5 and de736c2; neither amendment touches tools/ or tests/). Tool blob at HEAD: 182001dbc9aecbd5c877af34301a383fe79c8e02 (sha256 c5690681…6eb3). git 2.56.0. Scratch: /var/tmp/souji-r25-RevC2/ (removed at the end).

Fixtures exercised:
- committed tests/fixtures/r24-size-census.py (8 cases)
- ExecC2 draft .ufo/waves/round-25/w1/r24-size-census.py, sha256 9c8a512f94d5682efee725dc7ed7519c127fde6a775a038ec3292374970bd528 (the fixture_sha256 cited in ExecC2-2-receipts/c2-red.tsv)
- a variant at w1/ExecC2-receipts/r24-size-census.py, sha256 5bd7e74f…8238
- my own harness, which implements prereg cases 9–12 literally and imports the committed fixture's Scratch/manifest/changed, so the envelope is identical.

A1. Independent probes at tip (direct `python3 -B tools/souji-size-census.py --repo …`):
```
9  bare1.git (init --bare + pushed commit): rc=0, census.invoked_from=bare, last line garbage=0 size_garbage=0 unreachable=0 alternates=0
10 bare2.git (init --bare): rc=1 "souji-size-census: git failure: … fsck --unreachable --no-reflogs --no-progress exited 0: notice: No default references", stdout empty
11 w/sub: rc=2 "refused: --repo must name the repository itself (…/w), not a directory inside or below it"
12 init + extensions.partialClone=origin (empty, and again with one commit): rc=2 "refused: partial-clone repository (extensions.partialClone=origin)"
```
Draft fixture run against the tip tool: `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc=0. Cases 9–12 all report manifest_changed=0.

A2. Matrix: each tool run through the draft fixture. The variant fixture and my harness give identical pass/fail sets.
```
tip            12/12 rc0
stub            4/12 rc1  fails 2,3,5,6,9,10,11,12
old-1efe406    11/12 rc1  fails 11
778747e        10/12 rc1  fails 9,10
M1 bare: unreachable forced 0                 12/12  SURVIVES
M2 bare: alternates forced 0                  12/12  SURVIVES
M3 resolve(): return common, "bare" always    12/12  SURVIVES
M4 remote.*.promisor clause disabled          12/12  SURVIVES
M5 .promisor pack clause disabled             11/12  killed by 6
M6 extensions.partialClone clause disabled    11/12  killed by 12
M7 top-level check disabled                   11/12  killed by 11
M8 top-level check skipped for bare           12/12  SURVIVES
M9 pack lookup at PATH/.git/objects/pack      12/12  SURVIVES
M10 promisor refusal skipped for bare         12/12  SURVIVES
stub2 = stub + "census.invoked_from=bare"     5/12   case 9 PASS
```
Witnesses: one scratch repo per survivor, tip output versus mutant output.
```
W1 bare + dangling blob:             tip unreachable=1     M1 unreachable=0
W2 bare + objects/info/alternates:   tip alternates=1      M2 alternates=0
W3 plain repo:                       tip invoked_from=main M3 invoked_from=bare
W4 clone + remote.origin.promisor=true, no pack: tip rc=2 "promisor remote"  M4 rc=0 census
W8 --repo b1.git/objects:            tip rc=2 "must name the repository itself"  M8 rc=0 census of b1.git
W9 clone --bare --filter=blob:none, promisor config unset: tip rc=2 "promisor pack"  M9 rc=0 census
W10 clone --bare --filter=blob:none: tip rc=2 "promisor remote"  M10 rc=0 census (unreachable=1)
```

A4. Case 6 setup at git 2.56.0 (`git clone -q --no-checkout --filter=blob:none file://src partial; git config --list --local`):
```
core.repositoryformatversion=1 … remote.origin.promisor=true  remote.origin.partialclonefilter=blob:none
(no extensions.partialclone line)  objects/pack/pack-….promisor present
after `config --unset remote.origin.promisor`: `config --get extensions.partialClone` rc=1; tool refuses via "promisor pack (objects/pack/pack-….promisor)"
```

A5. Envelope probe: I called the committed fixture's `manifest()`/`changed()` on a synthetic directory, restoring mtimes after each write.
```
content change, size kept, mtime restored          detected=True ['a']
identical-bytes rewrite, mtime restored            detected=False
atomic replace same bytes (new inode), restored    detected=False
create+delete temp file, dir mtime restored        detected=False
new entry left behind, dir mtime restored          detected=True ['.', 'lost-found']
chmod and back (ctime only)                        detected=False
read (atime only)                                  detected=False
setxattr user.* (ctime only)                       detected=False
```

## Findings
1. **[Medium, coverage/calibration] Bare special-casing and promisor-clause survivors: 7 of 10 clause mutants score 12/12.** Survivors: M1, M2, M3, M4, M8, M9, M10, each broken on the witness repo shown above. The simplest still-broken tool that scores 12/12 is **M3**. It replaces the main/linked label return in `resolve()` (tools/souji-size-census.py:154-155) with `return common, "bare"`, so every main and linked repo is labelled bare. No case 1–8 checks `census.invoked_from`, and case 9 only requires the `bare` label. The bare-specific survivors are M1 (bare unreachable not counted), M2 (bare alternates dropped), M8 (`--repo bare.git/objects` accepted), M9 (promisor pack missed in bare and linked repos) and M10 (bare partial clone censused).
   - Case 9 builds a clean bare repo with no dangling objects and no alternates, so it cannot tell a real bare census from canned zeros.
   - Case 11 covers only a work-tree subdirectory, not a subdirectory of a bare repo.
   - No case has a bare or linked partial clone, or a promisor remote without a pack.
   - This does not trigger the C2 kill rule, which only concerns cases failing at tip. It does bound the claim: the counter proves the four named refusal surfaces and nothing about bare-census correctness or the remote-promisor clause.
   - Should be disclosed as the D3 survivor set, with the witness repos above named as future case candidates. They cannot be added now: the case set is frozen.
2. **[Medium, calibration] Amendment 2 §3 describes a gate the fixture does not have.** preregistration-amendment-2.txt:18-19 says "the implementing fixture adds an unchanged-manifest condition to both, disclosed in the report." Neither draft has it. In w1/r24-size-census.py, `case_subdir` returns `code == 2 and named` and `case_partialclone_only` returns `code == 2 and partial`. Its docstring says "cases 10-12 report manifest_changed but do not gate on it (not in the frozen r25 C2 predicates)." The ExecC2-receipts variant also has `ok = proc.returncode == 2 and named`. Before landing, either add the gate (tip measures manifest_changed=0 on cases 11 and 12, so it would still pass 12/12) or correct the amendment text. As written, the disclosure claims a check the counter does not make.
3. **[Low, calibration] The envelope disclosure is worded too broadly.** Prereg :84-85 says "the no-write envelope excludes atime/ctime; a write that restores mtimes is invisible."
   - The atime/ctime exclusion is **confirmed**. The row tuple at tests/fixtures/r24-size-census.py:102 is `(rel, kind, stat.S_IMODE(mode), st.st_size, st.st_mtime_ns, digest)`, and the docstring at :5-6 says "atime/ctime excluded."
   - "A write that restores mtimes is invisible" is **false as stated**. Because of the sha256 column, a content-changing write is detected even with its mtime restored (A5, `detected=True ['a']`). A new entry left behind is also detected.
   - What actually goes unseen: byte-identical rewrites, atomic same-byte replacements, transient files created and deleted with the directory mtime restored, mode round-trips, and xattrs. From reading the row tuple (not tested): uid/gid, inode and nlink are not recorded either.
   - Suggested wording: "invisible: writes that leave every (type, mode, size, mtime_ns, sha256) row identical — same-byte rewrites, transient files with directory mtime restored, ownership/xattr/inode changes."
4. **[Low, operability] The control flag says nothing about cases 9–12.** `case_control` (tests/fixtures/r24-size-census.py:258, unchanged in both drafts) is `failed = [name for name, check in CASES[1:5] if not run(check, stub)[0]]`, which covers cases 2–5 only.
   - When run as the tool, the stub does fail 9, 10, 11 and 12 (A2). So the prereg requirement "stub must fail >=1 case" is met on the new cases.
   - However, case 9 rejects the stub only through the label string: stub2 (the stub plus one `print("census.invoked_from=bare")`) passes case 9.
   - `control=FALSE-GREEN-REJECTED` therefore should not be read as evidence about 9–12.
5. **[Info, coverage] No r24 case overlaps the new ones.**
   - Case 6 covers three things: `--lost-found` argv, a blobless clone (refused through `remote.origin.promisor=true`, A4), and the same clone with the promisor config unset (refused through the `.promisor` pack). At git 2.56.0 the clone never sets `extensions.partialClone`.
   - Case 12 is the only case reaching the extensions.partialClone clause (M6 is killed by 12 alone), and case 11 is the only case reaching the top-level check (M7 is killed by 11 alone). Cases 9 and 10 are the only bare cases.
   - Case 6 only checks rc==2, not the refusal reason, which is why M4 survives: the pack clause still refuses with rc 2.
6. **[Info, calibration] The red-arm misattribution is independently confirmed; amendment 2 §1 already fixes it.** Prereg :80 said "(the bare cases discriminate)". In fact 1efe406 fails only case 11, under both drafts and my harness. 778747e fails cases 9 and 10 (rc=2, "fatal: this operation must be run in a work tree"). The amended two-blob red arm holds: each blob fails at least one of 9–12, and 778747e fails case 9 or 10.

## Attack log
- **A1 frozen expected values for 9–12: HELD (not falsified).** Tip output matches each frozen predicate (rc, stdout counts line and label, stderr substrings), independent of ScoutC2Probe. Amendment 2 §3 states that git exits 0 on the empty-bare `notice:`; the tool's message confirms it ("exited 0: notice: No default references").
- **A2 stub on the new cases: HELD.** The stub fails all of 9–12 through the draft fixture (4/12 overall, rc 1). Caveat: see Finding 4.
- **A3 simplest still-broken 12/12 tool: FOUND.** M3 (one return statement), plus six more survivors (Finding 1). The bare-plus-alternates and bare-partialClone examples in the brief are concretely M2 and M10/M9.
- **A4 overlap with r24 case 6: NONE** (Finding 5).
- **A5 envelope disclosure:** the atime/ctime exclusion is confirmed; the mtime-restoring sentence is overstated (Finding 3).
- **Adjudication:** C2 is expected to verify at tip (12/12, rc 0, under both drafts). The claim text should be bounded to "the four refusal surfaces named in cases 9–12". Before landing, the survivor set (Finding 1), the corrected envelope wording (Finding 3) and the amendment §3 discrepancy (Finding 2) should be fixed or disclosed. None of these needs a predicate, case set, or target change.

No tools installed or upgraded. No lane writes other than this report. Scratch /var/tmp/souji-r25-RevC2/ removed.
