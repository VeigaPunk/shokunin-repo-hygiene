STATUS: DONE — C1 and C2 are measurement-separable by their declared commands; C3 is not separable as written (no counting command, an overbroad parity predicate, and an untracked artifact); one hard C1 coupling (the r15 frozen re-pin) blocks a gate-clean C1 landing even with C2/C3 reverted.

# ConnClaimSeparability — can C1/C2/C3 each be verified with the other two reverted?

Base: lane HEAD `5fa6017ddcae9f6bd4412df44765f6360cb16294` (checked with `git rev-parse HEAD`). The worktree is mid-wave-1: `git status --porcelain` showed `M tests/vault/vadv54-harness.sh`, `M tools/souji-vault-verify.sh`, `?? .ufo/waves/round-17/`, `?? census/round-16/transcripts/`, `?? census/round-17/`, `?? corpus/knowledge/jj-colocation-receipts.md`, `?? tools/__pycache__/`. In-flight state is used only as evidence of the intended change shape, never as a passed check.

Two senses of "verified" are separated below, because they have different answers:

- **Measurement-separable**: the claim's declared counting command, run on a tree equal to base + that claim's files, produces the claim's evidence, and reads no file owned by another claim.
- **Landing-separable**: the round-end gate at the integrated revision is green when only that claim is applied. A claim can pass the first and fail the second; C1 does.

## 1. File ownership (wave-1 spec, 78 items)

| claim | owned changed files (from `.ufo/waves/round-17/w1-spec.json` items) | reads outside the claim |
|---|---|---|
| C1 | `tools/souji-census.sh` (CensusD1D2), `tests/fixtures/r17-census-hygiene.py` (FixtureR17Census, new), `census/round-17/run-matrix.py` (MatrixR17, new) | git history (`git show <rev>:tools/souji-census.sh`), `tests/fixtures/r15-census-config.py`, `tests/fixtures/r14-census-boundary.py` (both unchanged, pinned in the r15 frozen record) |
| C2 | `tools/souji-seat-audit.py` (SeatAuditPrecision), `census/round-16/transcripts/` 144 files + `MANIFEST.sha256` (TranscriptBundle, new), `census/round-17/transcript-manifest.py` (new) | `.ufo/waves/round-16/w1-spec.json`, `w2-spec.json`, the 144 transcript `.txt` files |
| C3 | `tools/souji-verify.sh` (VerifyJjRoots), `tools/souji-vault-verify.sh` (VaultJjRoots), `tools/souji-quarantine.sh` (QuarantineJjRoots), `tests/fixtures/r17-jj-receipts.sh` (FixtureJjReceipts, new), `tests/vault/vadv54-harness.sh` (Vadv54StubFix), `corpus/knowledge/jj-colocation-receipts.md` (ScribeKnowledgeJj, new) | none from C1/C2. `souji-quarantine.sh` invokes `tools/souji-verify.sh` as its receipt engine (`:6-7`, `VERIFY_BIN` at `:158`) — a dependency *inside* C3. |

No file is owned by two claims. Verified by static read of the ownership map and by cross-reference scan of the counting-command sources:

```
C1_runner   {'souji-census': 5}                          # no C2/C3 tokens
C2_audit    {'souji-census': 5, 'souji-seat-audit': 6, 'transcript': 13}   # regex/selftest literals only, no execution
C2_manifest {'transcript': 4}
```

## 2. Separability verdicts

### C1 — measurement yes, landing no

Measurement evidence:

- D1 site: `count_dirty()` at `tools/souji-census.sh:1021`, status call `:1037` — no untracked-files mode, as the closure says.
- D2 site: `guard_git_files()` `:519-535` (the `info/attributes` loop member is `:521`), called with `|| exit 2` at `:790`, `:831`, `:849`, `:873`, `:891` (grep-confirmed).
- The r17 runner is a generalization of `census/round-16/run-matrix.py`, whose interface is exactly what the claim cites: `suite()` runs `python3 <fixture> --tool <tool>` (`:46-47`), the fixture map is `:76`, and the invalidity set hardcodes only `r15-config`/`r14-namespace` (`:132`). It reads census bytes by revision and nothing else. C2/C3 bytes cannot enter the tallies. [Evidence: read of run-matrix.py; the recording fields `lane_head`/`fixtures_dirty` differ between an isolated and integrated tree, but the CASE maps do not.]

Two within-C1 build hazards that can make the claim's own command silently invalid, both mechanically fixable in the C1 slice:

1. **CLI mismatch between two C1 seats.** `FixtureR17Census` is specified with CLI `--census <path>` (w1-spec item of that name), while the r16 runner template invokes `--tool` (`run-matrix.py:47`). Unless MatrixR17 maps fixture→flag, every r17 arm returns no CASE lines and the suite is invalid. The claim text does not state the per-fixture flag.
2. **Invalidity accounting.** `run-matrix.py:132` invalidates only the r15/r14 suites. MatrixR17 must add the r17 suite to that set, or a broken hygiene fixture can produce a rc-0 record with an empty/misparsed r17 arm.

Landing evidence (the hard coupling):

- `tests/fixtures/r15-preservation-frozen/expected.json` pins `"tools/souji-census.sh": "64a60fd0…"`; `record.json` carries `measured_commit: c6207bd…` and `runs.changed.tool.sha256 = 64a60fd0…`.
- Current HEAD census bytes hash to `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` (`git show 5fa6017:tools/souji-census.sh | sha256sum`); C1 changes those bytes by construction (D1/D2).
- `tools/souji-seat-audit.py` is not pinned; `tools/souji-verify.sh`, `souji-vault-verify.sh`, `souji-quarantine.sh` are not pinned. Only C1 trips a frozen pin.
- The landing gate compares every frozen `files` pin to the **evaluated tree** (`tools/souji-landing-gate.py:390-424`, `oid = tree.get(repo_path) … actual != pinned`), and `LG-FROZEN-MEASURED` re-checks the pins at the record's `measured_commit` (`:466-505`).
- `souji-preservation-evidence.py --frozen DIR --root DIR` re-measures the pinned snapshot against `--root` bytes (doc `:30-31`; the `frozen-tampered` selftest at `:2394-2406` proves the pin-vs-root comparison), and additionally requires `runs.changed.tool.commit == measured_commit` (`:1269-1274`).

Consequence: at any revision containing C1's census change, both the landing gate (`LG-FROZEN-PIN`, and `LG-FROZEN-MEASURED` if the record is not regenerated) and `souji-preservation-evidence.py --frozen` fail. **C1 cannot land gate-clean alone**, even though its matrix command passes. This is a coupling to the R4/D6 workstream, not to C2/C3.

Smallest decoupling: include the re-pin in C1's declared change set and counting command — run `tests/fixtures/r15-preservation-frozen/regenerate.py --rev <C1 rev>` (or the D6-fixed equivalent) and `souji-preservation-evidence.py --frozen … --root .` (must print clean) as C1's final measurement. Ordering: today's `regenerate.py:130` writes `"verdict": "clean"` literally (R16-M2), so either D6's `RegenerateVerdict` lands first or the re-pin must be accepted only with the independent `--frozen` clean run in the same evidence file. Do not relax the gate to measured-commit-only in this round; that is a gate-semantics change, not a decoupling.

Also verified: the r15 fixture does **not** construct `.git/info/attributes` (no `info/` path in its source; only `core.attributesFile` and repo `.gitattributes` cases, `:521-584`). D2 therefore does not force editing the pinned r15 fixture; only the census bytes and the record move.

### C2 — measurement yes; one directory cohabitation and one manifest gap

Measurement evidence:

- The two false-positive mechanisms are exactly where the closure says: `write_target()` splits on the first comma (`tools/souji-seat-audit.py:68-73`), `allowed_target()` uses `target.lstrip("./")` (`:76-82`), which strips the dot of `.ufo`. The fix is local; the selftest cases live in the same file.
- The counting command reads `--spec` (r16 w1/w2 spec) plus `--transcripts`; `run()` builds each seat's report path from `lane` + `reportDir` and reads nothing else (`:143-176`). Neither census nor the receipt tools are executed or imported. Reverting C1/C3 cannot change the audit's per-seat classification.
- The r16 replay panic is not perturbed by the transcript bundle's location: the landing gate scans only `.ufo/waves/round-%d/` (`tools/souji-landing-gate.py:309-312`), while the bundle is committed under `census/round-16/transcripts/`. That is the correct side of the boundary (if it had landed under `.ufo/waves/round-16/`, every `.md` there would become a "seat report" for the round-16 replay and the 147/144 STATUS lines would change the routed D6 evidence). No change needed; keep it.

Two C2 gaps:

1. **The declared counting command does not verify the manifest.** The claim requires "transcripts committed with a sha256 manifest", but the stated command is only `souji-seat-audit.py --spec … --transcripts … --json …`. Add `python3 census/round-17/transcript-manifest.py --check census/round-16/transcripts` (or `sha256sum -c`) to the same command block; otherwise the manifest half is unverified.
2. **The claimed source counts do not match the bytes.** The context says `/var/tmp/souji-r16/transcripts` holds "w1 70 + w2 77" files. The actual dirs hold **65 and 79**; the wave specs list **65 and 79** items; `MANIFEST.sha256` pins **65 and 79** (`grep -c '^[0-9a-f]\{64\}  '` = 144 entries; 144 = 65 + 79). My set comparison over spec item names, manifest stems and `/var/tmp` filenames returned `missing [] extra []` for both waves. So the committed bundle is complete, and the 70/77 figure is wrong (or counts something other than seat transcript files; 70+77=147 ≠ 144). Fix the claim text to 65/79/144 and state the seat-set equality; do not let the 147 number reach the report or the lesson.

Directory cohabitation (not a correctness coupling): `census/round-17/` now holds C1's `run-matrix.py`, C2's `transcript-manifest.py`, and D6's `gate-replays.py`/`gate-replays-expected.json`. Files are disjoint, but "revert C1" cannot be implemented as "drop census/round-17/". Minimal fix: move `transcript-manifest.py` next to its data (`census/round-16/transcripts/transcript-manifest.py`) or name it explicitly as C2-owned in both the claim and the evidence record.

Meta-coupling (evidence layer, not claim measurement): `souji-seat-audit.py` is the tool L1 uses to audit **this round's** C1 and C3 seats. If C2 is reverted while C1/C3 are verified, the audit runs the base tool and re-emits the three known r16 false-positive `V-WRITE-SCOPE` majors on `.ufo/...` and prose-shaped writes. Minimal fix: treat the audit precision fix as a wave-0 prerequisite for all seat audits, or record the wave audit under both byte versions and publish the delta; do not present a base-tool audit of r17 seats as clean evidence either way.

### C3 — partial: behavior is independent, verification is not stated

Independence evidence:

- All changed call sites are inside C3 files and match the claim list exactly: verify `:234`, `:321`, `:351`, `:671`, `:809-813`, `:952`; vault `:412`, `:487`, `:517`, `:859`, `:997-1001`, `:1140`; quarantine `:299`, `:931`, `:1069-1073`, `:1251` (grep-confirmed at 5fa6017 plus the in-flight vault edit).
- No C3 file sources or executes the census or the seat audit. Quarantine's only engine dependency is `souji-verify.sh` (`:6-7`, `:158`), which is in the same claim.
- The plain-repo selftests are not broken by the durable-roots change: the metadata-prune fixture heads are branch/remote-reachable (`refs/heads/master`, `refs/remotes/origin/master`, `refs/heads/wt-pushed` at `souji-verify.sh:1126-1148`; `st_case F4 SAFE metadata-prune` at `:1244`, `E3` at `:1253`), so `--not --branches --tags --remotes` still yields `unique=0`. Same shape in quarantine's SKIP1 (`refs/heads/wt-clean`, `:1382`).

Why it is not separable **as stated**:

1. **No counting command.** C1 and C2 name a command, an input set and an output path. C3 names none. The wave-1 spec creates one (`tests/fixtures/r17-jj-receipts.sh`, item FixtureJjReceipts, J1–J5: keep-only absent worktree head → NOT-SAFE; unbookmarked jj commit touching a pushed file → NOT-SAFE; bookmarked+pushed control → SAFE(pushed); plain-shape parity; nested-`.git` observation), but a verifier reading only the claim cannot replay it. Minimal fix: add to C3, verbatim, `bash tests/fixtures/r17-jj-receipts.sh --tool-dir <rev-tree>/tools` at base and changed, with the expected CASE ids J1–J4 (J5 is informational), plus the plain-parity arm.
2. **The parity sentence is overbroad.** `--not --all` is not "all durable refs plus extras"; git-rev-list(1) (2.56.0, opened 2026-10-20) says: "Pretend as if all the refs in `refs/`, along with `HEAD`, are listed on the command line as `<commit>`" (artifact lines 497-500). Replacing it with `--not --branches --tags --remotes` changes the verdict in a **plain** repo whenever the registration head is held only by `HEAD` (detached owner) or only by a non-durable ref (`refs/stash`, `refs/notes`, `refs/replace`): old = `unique=0` → SAFE(metadata-prune); new = `unique>0` → NOT-SAFE. That is the intended safety direction, but it is not byte-identity. Minimal fix: state the parity domain precisely — "plain repo with no `refs/jj/*` and with the head reachable from a durable ref produces byte-identical output; a head held only by HEAD/stash/notes is deliberately reclassified NOT-SAFE" — and add that second shape as a fixture case (expected NOT-SAFE), so the delta is measured rather than contradicted.
3. **`--glob` placement is a live implementation trap.** In `git log [HEAD] --branches --not --remotes -- target`, the keep glob must be a *positive* rev before `--not` (`--branches --glob=refs/jj/keep/* --not --remotes -- target`). Placing it after `--not` makes it an exclusion and the case silently flips to SAFE. J1 exercises the roots site and would still pass; only J2 (a keep-only commit touching the target) catches the ordering. C3's evidence must therefore include J2, not just J1. Also keep the `jj-keep-unpushed` NOTES token conditional on a keep-ref contribution; the in-flight vault helper already gates on `for-each-ref refs/jj/keep/` before doing any extra work, which preserves plain byte-identity (`git diff tools/souji-vault-verify.sh`, helper `jj_keep_unpushed`).
4. **C3(e) rests on an untracked artifact and a conditional state.** At HEAD the harness creates the stub permanently during its build phase: `git show HEAD:tests/vault/vadv54-harness.sh` line 176 is `mkdir -p "$P/p6repo/.git" "$P/p6repo/inner"`; the committed run tree contains no `.git` (stat: "No such file or directory" for `tests/vault/vadv54-run/p/p6repo/.git` while `one.txt`/`inner/keep.txt` are tracked). So the stub exists only after a harness run (or after an interrupted run), and an untracked directory cannot be produced by reverting a commit. The in-flight fix (worktree diff) removes it from the build and creates/removes it around the P6 case (`mkdir -- "$P/p6repo/.git"`, trap `rmdir`, `rmdir` at the end). Minimal fix: (a) word (e) as "a harness run leaves ...", (b) put the exact scratch reproduction in the knowledge entry (create the empty nested `.git` in a /var/tmp colocated clone; `jj diff --summary` shows `D` for both tracked files), and (c) never let the claim's evidence depend on the lane's at-rest worktree.

Within-C3 integration note: `r17-jj-receipts.sh` must pass an explicit `--tool-dir` for **all three** tools, including the verify engine quarantine calls; otherwise a partially reverted C3 mixes base verify with changed quarantine and the J-cases no longer measure one claim slice.

## 3. Shared surfaces

| surface | shared by | kind | decoupling |
|---|---|---|---|
| `census/round-17/` directory | C1 runner, C2 manifest tool, D6 replay runner | directory only, files disjoint | move C2's tool beside its data or declare per-file ownership; never equate the directory with C1 |
| `tests/fixtures/` | C1 `r17-census-hygiene.py`; C3 `r17-jj-receipts.sh` | separate new files | none needed |
| `tests/vault/vadv54-run` | C3 only | C3 fixture tree | keep the harness stub transient; reproduce under /var/tmp |
| `tests/fixtures/r15-preservation-frozen/` (expected.json, record.json) | C1 (census bytes) and the landing gate/D6 | **hard** pin on C1 output | include the re-pin in the C1 slice; order D6's verdict fix first |
| `SKILL.md` | C1 registry row, C2 audit row, C3 recipes; L1 integrates | prose/registry, not a measurement input | section ownership; land per claim |
| `SCORECARD.md`, `LOG.md`, `corpus/lessons/round-17.md`, `corpus/SOURCES.md`, `corpus/QUALITY.md` | all claims plus D3/D5/D6/D7 | integration prose | per-claim commit slices; a revert must be content-scoped, never whole-file |
| counting commands | none shared | — | C1: matrix; C2: audit + manifest check; C3: undeclared (fix) |
| `tools/souji-seat-audit.py` as auditor | C2's file audits C1/C3 seats | evidence-layer | land the precision fix before wave audits, or publish both-version deltas |

No shared fixtures between claims. No shared counting command. The only byte-level hard coupling is C1 → r15 frozen pins (and its D6 ordering). The only evidence-layer coupling is C2's audit tool auditing the other claims' seats.

## 4. Contradictions stated, not smoothed

1. C3: "plain repos (no refs/jj) must behave byte-identically" vs durable roots that deliberately exclude `HEAD`/`refs/stash`/`refs/notes` (git-rev-list `--all` definition). Overbroad predicate; carve out and measure the delta.
2. C3: claim lists (a)–(e) but no counting command; the executable proof exists only in the wave-1 dispatch (`r17-jj-receipts.sh`, J1–J5). Claim/evidence binding is missing.
3. C2: source counts "70 + 77" vs actual 65 + 79 = 144 (directories, specs, manifest all agree; set diff empty).
4. C1: `FixtureR17Census` is specified with `--census` while the runner template calls `--tool`; and `invalid_suites` only covers the two legacy fixtures.
5. C1: census bytes and the r15 frozen pins cannot both be current at the same revision; C1 has no re-pin step in its claim.
6. C3(e): present-tense "the empty untracked fixture stub ... makes jj see phantom deletions" vs the stub being absent at a clean checkout and existing only after a harness run; plus the fix artifact is untracked and not revertible.

## 5. Proposed move — claim-slice receipts (one, bounded)

Make isolation a measured predicate instead of an assumption. Each claim's committed evidence JSON gains a `slice` object:

```
"slice": {
  "base": "5fa6017ddcae9f6bd4412df44765f6360cb16294",
  "owned":        { "<path>": "<sha256>", ... },   # this claim's changed files
  "foreign_base": { "<path>": "<sha256>", ... }    # the other two claims' files at base
}
```

and the claim's counting command (or the round-17 runner wrapper) verifies both maps with `sha256sum` before running, refusing with exit 2 on any mismatch. The slice list is generated from `git diff --name-only base..<claim-slice>`, not hand-written. C1's `owned` includes the regenerated r15 frozen record (expected.json + record.json); C3's includes `r17-jj-receipts.sh` and both parity domains; C2's includes the manifest tool relocated beside its data.

Why it is worth doing: it converts "can each be verified with the other two reverted" from a prose claim into a replayable check; an integrated run and an isolated run must produce identical arm/CASE maps, and any accidental cross-claim read surfaces as a digest refusal. It acts directly on **calibration** (the round's lowest axis, 7) by making the r16 closure's separability question mechanically answerable, and it leaves operability and coverage untouched because no tool behavior changes.

## 6. Risks

- An allowlist can miss a transitive dependency (e.g., a fixture importing a lane helper). Mitigation: derive the list from `git diff` per claim slice and include every file any changed file opens, rather than curating by hand.
- C1's re-pin depends on D6's `regenerate.py` verdict computation; if D6 is not first, require the independent `--frozen` clean run in the same evidence file.
- C3's slice needs `jj` 0.45.1 in path and a /var/tmp sandbox; a fixture that touches the lane or the user's jj config invalidates the claim. The in-flight fixture is specified with `JJ_CONFIG` isolation; keep it.
- C2's audit is self-referential for this round: the same tool audits its own wave. That does not affect the claim measurement (r16 transcripts) but must be disclosed in the report.

## 7. Verification of the proposal (for L1; not run here — no git writes, no writes outside this report)

1. Build per-claim trees from base: `git -C <lane> worktree add --detach /var/tmp/souji-r17-slice-C1 5fa6017`, then overlay only C1's files from the integrated rev (`git show <rev>:<path>`); repeat for C2 and C3.
2. C1: `python3 census/round-17/run-matrix.py --changed WORKTREE --output /var/tmp/.../c1-slice.json`; compare `arms.*.r15-config.cases`, `r14-namespace.cases`, the new hygiene suite and selftest counts with the integrated run — must be identical. Then `python3 tools/souji-preservation-evidence.py --frozen tests/fixtures/r15-preservation-frozen --root /var/tmp/souji-r17-slice-C1` must print clean only if the re-pin is in the slice.
3. C2: `python3 tools/souji-seat-audit.py --spec .ufo/waves/round-16/w2-spec.json --transcripts census/round-16/transcripts --lane <lane> --json /var/tmp/.../w2.json` (expect exit 0, major 0) and the same for w1 (expect exit 1 with exactly the real `SrcGitNoLazyFetch` major); `python3 census/round-17/transcript-manifest.py --check census/round-16/transcripts` (expect 0). Re-run both with C1/C3 reverted: numbers unchanged.
4. C3: `bash tests/fixtures/r17-jj-receipts.sh --tool-dir /var/tmp/souji-r17-slice-C3/tools` (expect J1–J4 PASS, J5 informational), then the same fixture against base tools (J1 must FAIL, i.e. the fixture is able to fail); add a plain-repo case with a stash-held head and assert the disclosed NOT-SAFE delta.
5. Negative control: run each claim's command in a tree where the other two claims' slice files are at base and the claim's `foreign_base` digests match; a nonzero rc from a digest mismatch means the isolation predicate is wired.

## 8. Commands run (verbatim where composite, with observed output)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD
→ 5fa6017ddcae9f6bd4412df44765f6360cb16294
git status --porcelain | head -30
→ M tests/vault/vadv54-harness.sh; M tools/souji-vault-verify.sh; ?? .ufo/waves/round-17/;
  ?? census/operator-sweep-20261019/; ?? census/round-16/transcripts/; ?? census/round-17/;
  ?? corpus/knowledge/jj-colocation-receipts.md; ?? tools/__pycache__/
stat -c '%F %n' tests/vault/vadv54-run/p/p6repo/.git
→ stat: cannot stat ...: No such file or directory
git -C ... ls-files tests/vault/vadv54-run/p/p6repo
→ tests/vault/vadv54-run/p/p6repo/inner/keep.txt
  tests/vault/vadv54-run/p/p6repo/one.txt
git show 5fa6017:tools/souji-census.sh | sha256sum
→ 64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c
sha256sum tools/souji-census.sh tools/souji-seat-audit.py tools/souji-verify.sh tools/souji-vault-verify.sh tools/souji-quarantine.sh
→ census 64a60fd0…; seat-audit c9ff355c…; verify 9adb1764…; vault f9e778ca…; quarantine df407511…
wc -l census/round-16/transcripts/MANIFEST.sha256; grep -c '^[0-9a-f]\{64\}  ' ...
→ 144; 144
ls census/round-16/transcripts/w1 | wc -l; ls census/round-16/transcripts/w2 | wc -l
→ 65; 79
python3 (set comparison over r16 w1/w2 spec item names, MANIFEST stems, /var/tmp dirs)
→ w1 spec 65 manifest 65 missing [] extra []; var_tmp 65
  w2 spec 79 manifest 79 missing [] extra []; var_tmp 79
python3 - (w1-spec ownership/ALLOWED-EXEC map over 78 items)
→ C1: CensusD1D2/FixtureR17Census/MatrixR17; C2: SeatAuditPrecision/TranscriptBundle;
  C3: VerifyJjRoots/VaultJjRoots/QuarantineJjRoots/FixtureJjReceipts/Vadv54StubFix/ScribeKnowledgeJj
grep -n 'guard_git_files|showUntrackedFiles|untracked-files' tools/souji-census.sh
→ guard_git_files defined at 519, calls at 790/831/849/873/891; count_dirty at 1021; status at 1037
grep -n 'refs/jj|--not --all|for-each-ref|--glob=|--branches' tools/{souji-verify,souji-vault-verify,souji-quarantine,souji-census}.sh
→ verify 234/321/351/671/809/952; vault 412/487/517/859/997/1140; quarantine 299/931/1069/1251; census 923-931
read tests/fixtures/r15-preservation-frozen/expected.json, record.json
→ census pin 64a60fd0…; measured_commit c6207bd…; changed tool sha 64a60fd0…
read tools/souji-preservation-evidence.py (frozen semantics), tools/souji-landing-gate.py (pin checks)
→ --frozen re-measures pins under --root; landing gate compares tree blobs at the evaluated rev
git show HEAD:tests/vault/vadv54-harness.sh | grep -n p6repo
→ 176: mkdir -p "$P/p6repo/.git" "$P/p6repo/inner"
git diff -- tests/vault/vadv54-harness.sh
→ removes the at-rest stub; adds mkdir/trap rmdir/rmdir around the P6 case
read https://git-scm.com/docs/git-rev-list
→ "Pretend as if all the refs in refs/, along with HEAD, are listed on the command line as <commit>."
```

No command wrote outside this report; no census/verify/vault/quarantine was executed against any directory; no `jj` and no git write was run. Tool installs: none.

## Commands
See section 8; all commands are read-only and executed from `/home/vgpnk/Projects/shokunin/souji-shokunin` or via `read`/`grep` on the named files. The only write is this report.
