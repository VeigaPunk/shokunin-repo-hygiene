# R43connector01 — sibling-overlap scan

Axes: calibration, operability, coverage. Read-only investigation; no candidate, instrument, runtime, registry or sibling edit; no scoring/selftest execution. Findings attack claims of novelty/substitutability and rename safety, not the frozen instruments' correctness.

Evidence receipt: `.ufo/waves/round-43/w1/R43connector01/scan-receipts.json` contains every scan/ref command, exact unabridged stdout/stderr, and return code. All repo:path pointers below name committed Git objects, not working-tree state. Commands were run concurrently through Python subprocess argv (no shell glob expansion).

Important contradiction: the assignment requests every sibling's `master`, but kaidoku and kotodama have no such ref. All three requested master scans returned 128, `fatal: unable to resolve revision: master`. `for-each-ref` identified `main` and `origin/HEAD` at the same commit; explicit main fallbacks completed all three scans. A clean *14-master* scan is therefore NOT claimed. Twelve master scans plus two default-branch fallbacks are covered. Ref hashes below were recorded after the first scans, not atomically with those scans.

## 1. Owners and functional overlap

Exact primary command for each absolute sibling path (each expansion is recorded in the receipt):

```sh
git -C /home/vgpnk/Projects/shokunin/<name>-shokunin grep -n -i -E 'freeze-check|correction|RETRACT|JSON-TARGET-SYMLINK|NOFOLLOW' master -- tools/ SKILL.md
```

All 12 resolvable master scans returned 0 (matches); both main fallbacks returned 0. Match counts, including generic prose rather than just owned tools:

| Lane | Primary master rc / lines | Fallback |
|---|---:|---|
| mori-shokunin | 0 / 140 | none |
| tabi-shokunin | 0 / 63 | none |
| tsukuroi-shokunin | 0 / 561 | none |
| kengaku-shokunin | 0 / 9 | none |
| kasegi-shokunin | 0 / 22 | none |
| kaidoku-shokunin | 128 / 0 | main: rc 0, 268 lines |
| mado-shokunin | 0 / 27 | none |
| tameshi-shokunin | 0 / 24 | none |
| chousa-shokunin | 0 / 26 | none |
| kama-shokunin | 0 / 150 | none |
| kake-shokunin | 0 / 35 | none |
| kumitate-shokunin | 0 / 4 | none |
| kotodama-shokunin | 128 / 0 | main: rc 0, 69 lines |
| kotoba-shokunin | 0 / 2 | none |

**Freeze-check owners (real name/function collisions, not interchangeable contracts):**
- `chousa-shokunin:tools/freeze-check.py:2-5`, `SKILL.md:151`: round-61 claims/spec/dispatch/ready consistency, eight named checks; argv `--claims --dispatch --spec --ready`. This does not implement souji's preregistration/round grammar or committed FREEZE→REV comparison.
- `kasegi-shokunin:corpus/instruments/freeze-check.py:2,12-13`, `SKILL.md:1153`: `kasegi-round-claims-v2` replay at a base, argv `--claims --tool-root --base`, FC-* findings. A registry-only search would miss this implementation outside tools/.
- `kengaku-shokunin:SKILL.md:610`: `plans/attrib_probe.py freeze-check --frozen ...` checks an attribution table pin. `SKILL.md:567` registers its downstream caller. Same subcommand spelling is not the same freeze claim.

**Correction readers / counters:**
- `mori-shokunin:tools/mori-round41-calibration.py:24-25,91-93`: parses a prose calibration correction and selects the last match. `SKILL.md:189` explicitly calls it a dated probe, not a standing gate. This contradicts treating all correction readers as equivalent to r43's duplicate/retraction-rejecting grammar.
- `tsukuroi-shokunin:SKILL.md:1778,1967,3111`: source-scope correction gate, appended-notices structural gate, and exact journalctl correction clusters. `tools/check-appended-notices.py:838-850` has correction notice cases. The registry explicitly separates structural conformance from semantic source agreement.
- `kaidoku-shokunin@main:SKILL.md:1785,1787`, `tools/round-44/c2-controls.py:1049-1111`: machine-rederived corrections and wrong-value correction-note rejection; scoped to kaidoku record atoms, not souji R39 derivations.
- `kama-shokunin:SKILL.md:1345,1362`: r31/r32 claim-row correction counters; r32 uses round-qualified unique keys. `SKILL.md:1600` registers a cited-path correction ledger but explicitly says it is data, not an executable gate.
- `kake-shokunin:SKILL.md:1354-1357`: anchored correction counter and append-guard that recognizes visible dated tags outside comments/backtick spans. This is closely related prose-boundary ground, but has different accepted placements and correction vocabulary.
- `kotoba-shokunin:SKILL.md:465`, `verifiers/check_correction_sweep.py:2-16,204`: round-52 correction sweep, with same-block rather than another-block correction requirements. This implementation lives in verifiers/, discovered from the registry rather than tools/.
- `tabi-shokunin:SKILL.md:2100`: routed correction counter, scoped to four closures. Other generic correction matches in registries are not proof of a general prose parser.

**Symlink guards (no exact drift-tool N10 counterpart found):**
- Closest *output* refusal: `chousa-shokunin:tools/build-spans.py:35-40,278-343`, `SKILL.md:26-27,149`: exit-2 refusal before writes and descriptor-relative O_NOFOLLOW publication. This is a derived-spans output contract, not a worktree drift report.
- Read-side precedents: `mori-shokunin:tools/mori-evidence-loss.py:38,91,126` and `tools/mori-seat-terminal.py:17-27`; `mado-shokunin:tools/mado-action-plan.py:151-157`; `tameshi-shokunin:tools/evidence-disposition.py:88-91,303-358` and `tools/pin-disposition.py:91,493`; `tabi-shokunin:SKILL.md:1586,1614`; `kake-shokunin:SKILL.md:850-852`.
- Other scoped nofollow uses: `kama-shokunin:tools/kama-llamacpp-live.py:344-347,684-705`; `kaidoku-shokunin@main:tools/round-42/fetch-carrier.py:53-57,276,307`; `kumitate-shokunin:SKILL.md:297,626`.
- No `JSON-TARGET-SYMLINK` match appeared in the primary ownership scans or two main fallbacks. No sibling freeze-check match proves support for souji's r43 grammar. Generic `NOFOLLOW` in kake also includes the unrelated HTML rel/nofollow subject; those are not filesystem evidence.

Verdict: real adjacent ownership exists, but no demonstrated drop-in replacement for the r43 freeze-check, correction grammar, or named drift JSON leaf refusal. Do not equate textual overlap with duplicate implementation authority.

## 2. Corpus citations endangered by r42 renames

Exact command (all 14 expansions in receipt):

```sh
git -C /home/vgpnk/Projects/shokunin/<name>-shokunin grep -n -E 'souji-round-42|r42-drift-conditions|souji-freeze-check' master -- corpus/
```

Observed: the twelve resolvable master searches each returned 1, empty stdout and stderr (no match); kaidoku/kotodama master returned 128 as above, then the identical searches with main returned 1, empty stdout and stderr.

**List: empty within the exact requested committed corpus search.** This is not a claim that arbitrary spellings, non-corpus files, uncommitted work or other refs cannot cite souji. No rename hazard was evidenced by these terms; no r42 rename is authorized or proposed here.

Verdict: clean scoped citation scan with the two explicit branch-name exceptions, not a universal absence proof.

## 3. Previously claimed round ground; one bounded move

Contract scan, again for all 14 sibling paths (two main fallbacks explicitly recorded):

```sh
git -C /home/vgpnk/Projects/shokunin/<name>-shokunin grep -n -i -E 'symlink.{0,70}refus|refus.{0,70}symlink|correction.prose|correction.{0,35}reader|JSON-TARGET-SYMLINK' master -- SCORECARD.md PROVINCE.md SKILL.md corpus/lessons/
```

The narrower spelling scan missed registered correction instruments. Therefore a second committed registry scan was run, not a clean result inferred from those misses:

```sh
git -C /home/vgpnk/Projects/shokunin/<name>-shokunin grep -n -i -E 'check-appended-notices|correction.{0,100}(gate|counter|parse|reader)|retract.{0,80}(gate|counter|parse)|symlink|nofollow' <master-or-explicit-main> -- SKILL.md PROVINCE.md
```

**Correction-ground list:** mori (r41, `SKILL.md:189`); tsukuroi (r13/r14/r18/r37, `SKILL.md:1737,1778,1967,3111`); tabi (r19, `SKILL.md:2100`); kama (r31/r32, `SKILL.md:1345,1362`); kaidoku@main (r47/r48, `SKILL.md:1785,1787`); kake (r54/r60, `SKILL.md:1354-1357`); kotoba (r52, `verifiers/check_correction_sweep.py:2`, registered `SKILL.md:465`). These claim bounded correction ground, not souji's exact CORRECTION-/RETRACT-CORRECTION grammar.

**Symlink-refusal-ground list:**
- tabi: fleet-round-1 freshness safety correction, `SKILL.md:1586`, `corpus/lessons/kaika-fleet-round-1.md:19`.
- mado: r23 analysis-tool boundaries, `PROVINCE.md:20,24-26`; r30 plain-tree gate/refusal capability, `SCORECARD.md:1933,2034`, `corpus/lessons/round-30.md:65,109`.
- chousa: r19 sweep/refusal `SCORECARD.md:986,1319`; r21 pointer screening `SCORECARD.md:1321`; r61 derived-output safety `SKILL.md:26,149`; r62 leaf-vs-component distinction `SKILL.md:27`.
- kama: snapshot-history refusal registry, `SKILL.md:308`; r50 mapped-model O_NOFOLLOW identity, `SKILL.md:1544`.
- kake: fixture symlink failures and expected.json refusal, `SKILL.md:850-852,879-889`; r58/r59 receipt/registry path boundaries, `SKILL.md:1293,1308`.
- kaidoku@main: r24 preexisting/symlink output refusal, `SKILL.md:1137`; r42 cache/image-cache/work refusal, `SKILL.md:1762`.
- kumitate: r50 sandbox-bind alias refusal, `SCORECARD.md:1836`, `corpus/lessons/round-50-verifier-spotcheck.md:30`; source-capture symlink drift contract `SKILL.md:626`.
- mori and tameshi additionally own descriptor-bound input guards (section 1 pointers); that evidence alone is not attributed to an unobserved particular round claim.

**Not ownership evidence:** tsukuroi's r49 traversal-source refusal (`corpus/lessons/round-49.md:48`) does not establish a filesystem output guard; tameshi's “correction prose” lesson mentions (`corpus/lessons/round-17-verifier-spotcheck.md:450`, `round-55.md:72`) do not establish ownership of r43's grammar. Kotodama@main and kengaku produced no narrow-contract matches, and no exact symlink-refusal/correction-prose claim is inferred from that absence.

**One proposed move — use an explicit contract fingerprint, not a shared helper or broadened authority.** In the L1's eventual r43 scope/novelty explanation, distinguish souji's “lane-local preregistration grammar + committed FREEZE/REV comparison”, “R39-derived correction prose”, and “--json final-leaf refusal” from the sibling entries above. Cite chousa's r61/r62 output-vs-component boundary as precedent, but keep souji's standalone candidate and exact N10 behavior; do not absorb chousa's whole path policy or call its runtime. This is a proposal only, not an edit/admission/judgment.

Affected axes: calibration improves by replacing an overbroad novelty/duplicate claim with named prior art and exact distinctions; operability and coverage remain unchanged because no argv, outcome, write boundary, fixture or frozen instrument changes. [INFERENCE] This is a non-regressing documentation/scope move, not a measured score gain.

Second-order surfaces: runtime stays standalone with no sibling import/process dependency; contract retains souji's exact exit 2 and `REFUSAL JSON-TARGET-SYMLINK:` plus frozen anchors; substrate distinction is leaf-vs-ancestor and Git mode 120000 control inputs vs live output leaves; verification continues to use the frozen c1/c2/c3 instruments, not a sibling's differently scoped selftest.

Risks/contradictions: chousa rejects more path components and protects publication races, while r43 N10 names a leaf only; copying its policy wholesale could change accepted inputs or exceed scope. Mori's last-match correction policy contradicts souji's duplicate-reject policy. Kasegi/chousa/kengaku all say freeze-check but bind different objects and CLI grammars. Existing sibling scored numbers in registries are historical claims, not tests exercised by this seat.

Verification: this seat exercised only the logged read-only searches/ref enumeration, not runtime behavior or candidate scoring. For any eventual L1 candidate integration, retain the frozen C2 table/hidden/r42 legs and C3 anchors, nine old fixtures, and exact JSON-leaf refusal criterion; those checks are unrun here, not passed. Frozen-instrument defects, if found elsewhere, remain findings for L1, never edits here.

Verdict: contested *general* correction/symlink/freeze-check ground is demonstrated; exact souji r43 contract duplication is not. Report the boundary; never absorb sibling scope.

### Command receipts and branch observations

The receipt includes full exact commands/results for all scans above, focused git greps over the named implementations, the two `for-each-ref` discoveries and all ref resolutions. Exit-count matrix for the narrow contract search:

- mori-shokunin: master rc=1, matches=0.
- tabi-shokunin: master rc=0, matches=3.
- tsukuroi-shokunin: master rc=0, matches=1.
- kengaku-shokunin: master rc=1, matches=0.
- kasegi-shokunin: master rc=1, matches=0.
- kaidoku-shokunin: master rc=128, matches=0; main rc=0, matches=4.
- mado-shokunin: master rc=0, matches=12.
- tameshi-shokunin: master rc=0, matches=2.
- chousa-shokunin: master rc=0, matches=10.
- kama-shokunin: master rc=0, matches=2.
- kake-shokunin: master rc=0, matches=1.
- kumitate-shokunin: master rc=0, matches=2.
- kotodama-shokunin: master rc=128, matches=0; main rc=1, matches=0.
- kotoba-shokunin: master rc=1, matches=0.

Observed ref resolutions (not an atomic fleet snapshot):

- `mori-shokunin`: `7370a731abcafc4c803111de7c22cd6264d63be1` (`master`).
- `tabi-shokunin`: `5c3f4cca86e9d0c548d41e21524525c5095652d5` (`master`).
- `tsukuroi-shokunin`: `4ee3226daa221c72acab23eacaacc8f3c9616954` (`master`).
- `kengaku-shokunin`: `d244d4d324636953cd7192f2586fe0332b874e57` (`master`).
- `kasegi-shokunin`: `d8dfbcbf4ab53db0045d55ea588a3af90af5906d` (`master`).
- `kaidoku-shokunin`: `39f41d4f15a87689a41c16c5c17ed885fbfb7da3` (`main`; no master).
- `mado-shokunin`: `0f3a54361a9824484d0801679ceb1fd8ac7c32e1` (`master`).
- `tameshi-shokunin`: `2c51affd37e15cd7cd258d76ba0f5f73ff235924` (`master`).
- `chousa-shokunin`: `4ece131ca826c646bd28a50802d41bc78d8a9717` (`master`).
- `kama-shokunin`: `361c620c33edf8d19ec63b287250287f34f95484` (`master`).
- `kake-shokunin`: `1a48131577ba82c967650561be34e8dba909432a` (`master`).
- `kumitate-shokunin`: `14057f3e3899180c95713bace088fb9c0d0046e3` (`master`).
- `kotodama-shokunin`: `44f76d456c1b326a71ffdb381590af825cbf11be` (`main`; no master).
- `kotoba-shokunin`: `47dbe8781657de563ff867caca6244d28e3db504` (`master`).

Other commands executed: the initial `git -C /home/vgpnk/Projects/shokunin/mori-shokunin rev-parse --show-toplevel --show-prefix master` printed the mori repository root, empty prefix and `7370a731abcafc4c803111de7c22cd6264d63be1`; its chained primary ownership grep is repeated in the receipt. `mkdir -p /fast/scratch/hyaku/souji-r43/R43connector01 && rmdir /fast/scratch/hyaku/souji-r43/R43connector01` exited 0 with no output: no fixtures/clones were made, and the empty own scratch directory was removed. No installs/updates. Relevant skill/operator rules and the known c1/c2 counter docstring sections were read; no mutation of their bytes.
