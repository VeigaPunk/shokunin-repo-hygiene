# W2C1MutFixture — mutation test of C1's fixture

## Status
STATUS: PASS. All 7 assigned weakenings were scored, plus 2 higher-order mutants, plus one environment mutant for the detector. Against the panel the task named (the stub and the plain `git -C PATH` cheater), none of the 7 weakenings changes any outcome. So by the task's rule, none of those assertions is tested by the stub or the cheater. Each of the 7 still has teeth: 6 flip a matching targeted bad tool from FAIL to a false 8/8 (exit 0). The case-7 weakening only matters when git's `fsck --lost-found` is shimmed, and the case-8 weakening only matters when combined with a fixture weakening of cases 2–5.

## Evidence
- Revision: fixture `tests/fixtures/r24-size-census.py` and tool `tools/souji-size-census.py` taken via `git show ca7fc1cb6dd1333096c6f3bdbad304686691d126:<path>`.
  - Fixture sha256 `373ef1f0a02f8ca11fccd4ff32d8511c1eaaf3ede672c37ed11ef2b10968084f`.
  - Tool sha256 `09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d`.
  - The lane tip at run time was `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`. `git diff --stat ca7fc1cb.. master -- <fixture> <tool>` was empty, so both files are byte-identical at the tip. git 2.56.0.
- Harness: every fixture copy, the pristine reference P0 included, had one harness-only edit, `SCRATCH_PARENT = '/var/tmp'` → `/var/tmp/souji-r24-W2C1MutFixture/run`. This kept scratch under my seat directory. The restored copy reproduces P0 (below).
- Command, per cell: `python3 -B fx/<F>.py --tool tools/<T>.py`, with `timeout 900`. 10 fixtures × 9 tools, plus 2 shim runs plus 3 restored runs, all with -P16.
- Mutants were built with exact-once string replacement, asserted by `gen.py`. Hashes (sha256, first 16 hex characters):

| fixture | change | hash16 |
|---|---|---|
| P0_pristine | none (relocated) | 2f9dcc7190c2f12a |
| F1_no_dirs | `manifest` appends a row only when the kind is not `'d'` (it still recurses) | 66e7f5901b36368f |
| F2_whole_sec | `st.st_mtime_ns // 1000000000` | 42a12b8e57c0aca6 |
| F3_no_size | `counts[1] == 2` and `counts_l[1] == 2` dropped | 14f1905a57d00999 |
| F4_witness_before | raw `git -C linked count-objects -v` read moved before `s.census` | c1b6381236c46d9a |
| F5_no_unset_arm | `and code_c == 2 and not delta_c` dropped (the arm still runs) | 029d77b21c2e6452 |
| F6_detector_skipped | `case_detector` returns `True, 'skipped'` | d70d0857814da507 |
| F7_control_zero_ok | control `bool(failed)` → `len(failed) >= 0` | c595300e98261258 |
| H1_cases235_countless | count checks removed from cases 2, 3 (both arms) and 5 | e5dfebcd9a8012bc |
| H2_countless_plus_F7 | H1 + F7 | 2b2e3d306c8aff51 |

- Tool panel (all scratch). Wrappers prepend one defect, then run the real tool:
  - T_real: the real tool.
  - T_stub: copy of `census/round-24/controls/stub-size-census.py`.
  - T_cheat_plain: strict argv, `git -C PATH count-objects -v` plus `fsck --unreachable`, no common dir, no promisor refusal.
  - T_dir_leak: leaves an empty dir `<common>/souji-census-tmp`.
  - T_lock_unlink: creates and unlinks `<common>/souji-census.lock`, so only the directory mtime changes.
  - T_mtime_sec: rewrites `config` with the same bytes, then restores its mtime truncated to whole seconds.
  - T_size_bytes: real tool reporting `size_garbage` as KiB×1024.
  - T_no_promisor_pack: real tool without the `objects/pack/*.promisor` refusal.
  - T_retarget_gitfile: rewrites `<linked>/.git` to `gitdir: <common>`, which is outside the common-dir manifest.
  - Shim: a PATH `git` that strips `--lost-found`. The real tool calls `/usr/bin/git` and is unaffected.
- Outcome matrix. Each cell is cases 1–8 as P (pass) or F (fail), then the fixture exit code. `*` marks a cell that differs from the P0 cell for the same tool.

| fixture | cheat_plain | stub | real | dir_leak | lock_unlink | mtime_sec | size_bytes | no_promisor_pack | retarget_gitfile |
|---|---|---|---|---|---|---|---|---|---|
| P0 | PPFFPFPP e1 | PFFPFFPP e1 | PPPPPPPP e0 | FFFFFFPP e1 | FFFFFFPP e1 | FFFFFFPP e1 | PPFPPPPP e1 | PPPPPFPP e1 | PPPFPPPP e1 |
| F1 | same | same | same | PPPPPPPP e0* | PPPPPPPP e0* | same | same | same | same |
| F2 | same | same | same | same | PFPPPPPP e1*; 6/6 reruns PPPPPPPP e0 | PPPPPPPP e0* | same | same | same |
| F3 | same | same | same | same | same | same | PPPPPPPP e0* | same | same |
| F4 | same | same | same | same | same | same | same | same | PPPPPPPP e0* |
| F5 | same | same | same | same | same | same | same | PPPPPPPP e0* | same |
| F7 | same | same | same | same | same | same | same | same | same |
| H1 | PPPFPFPF e1* | PPPPPFPF e1* | PPPPPPPF e1* | …F at 8 | …F at 8 | …F at 8 | PPPPPPPF e1* | PPPPPFPF e1* | PPPFPPPF e1* |
| H2 | PPPFPFPP e1* | PPPPPFPP e1* | PPPPPPPP e0 | FFFFFFPP e1 | FFFFFFPP e1 | FFFFFFPP e1 | PPPPPPPP e0* | PPPPPFPP e1 | PPPFPPPP e1 |

  - F6 changes nothing in any column: case 7 does not depend on the tool.
  - Shim, real tool: P0 gives `PPPPPPFP e1` with `CASE 7 detector FAIL fsck_exit=0 manifest_changed=0 lost_found_other_oid=False`. F6 gives `PPPPPPPP e0*`.
- Output excerpts from P0 (the gaps these defects hit):
  - Stub: `CASE 4 linked PASS exit=0 counts=0,0,0,0 manifest_changed=0 raw_linked_garbage=1`.
  - Cheater: `CASE 4 linked FAIL exit=0 counts=1,0,0,0`.
  - lock_unlink: `CASE 1 clean FAIL exit=0 counts=0,0,0,0 manifest_changed=1 first=.`.
  - retarget: `CASE 4 linked FAIL exit=0 counts=0,0,0,0 manifest_changed=0 raw_linked_garbage=0`.
  - H1, stub: `CASE 8 control FAIL`, which gives `control=FALSE-GREEN-ACCEPTED`.

## Findings
1. **Directories in the manifest are untested by the stub and the cheater, but load-bearing.** Location: fixture line 102, `rows.append((rel, kind, stat.S_IMODE(mode), st.st_size, st.st_mtime_ns, digest))`.
   - Under F1, T_dir_leak and T_lock_unlink both go from FAIL to `cases=8 pass=8`, exit 0. That is a false green for a tool that writes the repo.
2. **ns mtime is untested by the stub and the cheater, but load-bearing.** Location: the same line 102 (`st.st_mtime_ns`).
   - Under F2, T_mtime_sec reaches 8/8 exit 0.
   - T_lock_unlink reached 8/8 exit 0 in 6 of 6 reruns. One run of 7 caught case 2 only, when a second boundary fell inside that tool run. Second-resolution detection is timing-dependent.
3. **Case 3's size check is untested by the stub and the cheater, but load-bearing.** Location: lines 164–165 and 173–174, `and counts[1] == 2 and not delta)`.
   - Under F3, T_size_bytes reaches 8/8 exit 0. No other case asserts a non-zero `size_garbage`, so case 3 alone carries amendment 1's `size_garbage=2`.
4. **Case 4's witness-after ordering is untested by the stub and the cheater, but load-bearing.** Location: lines 185–186, `raw = s.git('-C', linked, 'count-objects', '-v').stdout`.
   - Under F4, T_retarget_gitfile reaches 8/8 exit 0. That defect rewrites `<linked>/.git`, which lies outside the common-dir manifest, and only the post-run witness sees it.
   - [INFERENCE] This is the only case that watches anything outside the common dir.
5. **Case 6's promisor-unset arm is untested by the stub and the cheater, but load-bearing.** Location: lines 233–235, `and code_c == 2 and not delta_c)`.
   - Under F5, T_no_promisor_pack reaches 8/8 exit 0.
6. **The case-7 detector does not depend on the tool.** Location: lines 241–251, `return bool(delta) and written`.
   - Skipping it (F6) changes no outcome for any of the 9 tools. Its only teeth are environmental: with git's `--lost-found` shimmed away, P0 reports `lost_found=NOT-DETECTED` and exits 1, while F6 reports 8/8 exit 0.
   - It calibrates the manifest against a known writer, not the tool. It still passed under F1 and F2: `lost-found/other/<oid>` is a regular file, so the weakened manifests still see it.
7. **The case-8 control does not depend on the tool.** Location: line 258, `return bool(failed), 'stub_failed=%s' % (','.join(failed) or 'none')`.
   - F7 changes no outcome alone, because the stub is hardcoded in `STUB` (lines 31–32) and does not depend on `--tool`.
   - It does guard the fixture itself. Under H1, P0's control turns `FALSE-GREEN-ACCEPTED` and every tool fails, the real one included. Under H2 (H1 + F7), that guard is gone: T_real and T_size_bytes both exit 0.
   - The stub is still rejected under H2, by case 6 (refusal). Case 8's own outcome is not what catches it.
8. **Coverage note: the stub passes case 4.** Output: `CASE 4 linked PASS exit=0 counts=0,0,0,0 ... raw_linked_garbage=1`. Case 4's tool assertion is `garbage=0`, which a zero emitter meets trivially. Case 4 discriminates the cheater, not the stub. This is not an attack on the frozen contract: case 8 is defined over cases 2–5, so "fails at least one" still holds.
9. **Counter verdict unchanged.** The pristine fixture at ca7fc1cb gives `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, exit 0, with the real tool. The stub gives pass=4 and the cheater pass=5, both exit 1. No mutant of the fixture lets the stub or the cheater exit 0.

## Attack log
| mutant | expected detector | stub / cheater outcome changed? | targeted tool flipped to exit 0 | verdict |
|---|---|---|---|---|
| F1 no dirs | manifest delta on `.` and new dir | no / no | dir_leak, lock_unlink | killed by targeted (untested by stub/cheater) |
| F2 whole-second mtime | ns mtime delta | no / no | mtime_sec, lock_unlink (6/6 reruns) | killed by targeted |
| F3 case 3 no size | `size_garbage=2` | no / no | size_bytes | killed by targeted |
| F4 witness before tool | `raw_linked_garbage=1` after run | no / no | retarget_gitfile | killed by targeted |
| F5 no promisor-unset arm | `code_c == 2` | no / no | no_promisor_pack | killed by targeted |
| F6 detector skipped | fsck `--lost-found` write seen | no / no (does not depend on tool) | real tool under `--lost-found` shim | killed by environment mutant only |
| F7 control 0 failures | stub fails ≥ 1 of cases 2–5 | no / no (does not depend on tool) | real, size_bytes under H2 | killed by higher-order mutant only |

Restoration evidence:
- Committed bytes re-extracted from `ca7fc1cb:tests/fixtures/r24-size-census.py` hash to `373ef1f0…084f`. That equals the pre-mutation scratch copy and the lane working-tree file.
- The restored copy (relocated the same way) gives: T_real `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` exit 0; T_stub pass=4 exit 1; T_cheat_plain pass=5 exit 1. These are identical to P0.
- The fixture's `run/` scratch parent was empty after the runs (0 entries).
- No lane file was written except this report.

Tooling: no installs or updates.
