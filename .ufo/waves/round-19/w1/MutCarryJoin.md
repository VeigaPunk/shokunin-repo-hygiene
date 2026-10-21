STATUS: DONE — M2 killed by TC4; all five pinned historical carry verdicts and an additional strict round-18 control stayed unchanged; scratch bytes restored exactly and scratch removed.

# Findings

- Seat: `SoujiR19.MutCarryJoin-2`; assigned item `MutCarryJoin`; axis **calibration**; observation date **2026-10-21**. This is one mutation probe, not admission of C1 or judgment of the round.
- **Mutant M2:** bypass the lesson-side `carry_entries` join at its single behavior-bearing callsite, retaining normalization, report paragraph matching, carry-token matching, and the round threshold. Only the private copy of `tools/souji-landing-gate.py:497` was mutated:

  ```python
  # pristine / restored
  entries = carry_entries(carry_lines) if wrap_strict else []
  # M2
  entries = [norm_line(line) for line in carry_lines] if wrap_strict else []
  ```

- **Expected detector:** TC4 (`wrap-bullet-wrapped`) must carry the complete STATUS paragraph even though its lesson bullet wraps. M2 should wrongly emit `LG-SEAT-UNCARRIED`. TC1–TC3 are controls, and historical carry findings must be compared without changing their round numbers.
- **Observed:** pristine **10 pass / 0 fail**; M2 **9 pass / 1 fail**; restored **10 pass / 0 fail**. The sole changed case was TC4: no findings → one `LG-SEAT-UNCARRIED` → no findings. **Mutation verdict: KILLED**, with a passing pristine baseline and successful restored rerun.
- **Historical movement:** none in the tested population. The five preregistered replays retained their complete carry outputs, including finding details and counters. A sixth control at round-18 base `3ab2c81479f5004c8bc91946eea482caec45408f` also retained its strict-branch carry output. These controls are not a claim about every historical revision.

# Evidence

## Bytes and scope actually exercised

The proposed rule was copied from the **worktree**, not assumed to equal the base commit. The measured worktree gate contains the round threshold at `tools/souji-landing-gate.py:113-125`, lesson join at `:431-443`, and carry integration at `:467-539`. The test data were copied from `tests/fixtures/r19-carry-wrap.py:58-101`.

The same bounded Python detector was compiled once and invoked three times against the private gate pathname. It loaded the actual copied gate as a module and called its actual `check_carry`; it did not reimplement paragraph extraction or matching. The only substituted dependency was `blob_by_oid`, backed by a frozen in-memory blob map. Historical report and lesson blobs became fixture input; the gate did not read a live repository, execute repository code, run a census, or inspect fleet state.

The four synthetic cases preserve the fixture's exact REPORT and CASES values. Those constants were extracted from their AST assignment expressions; the fixture's CLI, environment setup, and repository builder were not executed. A direct fixture run would execute `git init`, `git add`, and `git commit` (`tests/fixtures/r19-carry-wrap.py:117-144`), contrary to this seat's no-git-mutations contract, and would allocate scratch outside the assigned seat directory (`:180`). This probe therefore exercises the carry behavior in memory, **not the complete CLI fixture**.

For each world, the detector computed `carry_exit = int(bool(findings))`. Synthetic cases checked that value, the exact finding-ID set, and one marker/report/STATUS plus a present carry heading. Historical cases checked the exact sorted carry `(id, path)` multiset against frozen expectations. Cross-stage comparison also checked the full historical result rows, including details and counters.

**Exit labels below are computed detector values, not observed CLI process return codes.** All Eval calls themselves completed normally. No gate CLI, gate selftest, or full replay runner was run.

## Exact synthetic stimuli

Each case uses round **18**, report path `.ufo/waves/round-18/w1/SeatWrap.md`, and lesson path `corpus/lessons/round-18.md`. The lesson prefix is `# Round 18\n\n## Seat-reported failures\n\n`. All displayed physical lines end with LF; neither the report continuation nor the TC4 lesson continuation is indented.

Report source: `tests/fixtures/r19-carry-wrap.py:58-62`, [local source URL](file:///home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r19-carry-wrap.py#L58-L62), accessed 2026-10-21:

```text
# SeatWrap

STATUS: PARTIAL — guarded repos measured and the
remaining arm never runs under a bound.
```

TC1 lesson bullet (`wrap-unmarked`): `tests/fixtures/r19-carry-wrap.py:64-66,76-80`, [local source URL](file:///home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r19-carry-wrap.py#L76-L80), accessed 2026-10-21:

```text
- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "STATUS: PARTIAL — guarded repos measured and the" — open
```

TC2 lesson bullet (`wrap-marked`): `tests/fixtures/r19-carry-wrap.py:67-69,82-86`, [local source URL](file:///home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r19-carry-wrap.py#L82-L86), accessed 2026-10-21:

```text
- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "STATUS: PARTIAL — guarded repos measured and the …" — open
```

TC3 lesson bullet (`wrap-complete`): `tests/fixtures/r19-carry-wrap.py:70-73,88-92`, [local source URL](file:///home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r19-carry-wrap.py#L88-L92), accessed 2026-10-21:

```text
- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "STATUS: PARTIAL — guarded repos measured and the remaining arm never runs under a bound." — open
```

TC4 lesson bullet (`wrap-bullet-wrapped`): `tests/fixtures/r19-carry-wrap.py:94-100`, [local source URL](file:///home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r19-carry-wrap.py#L94-L100), accessed 2026-10-21:

```text
- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "STATUS: PARTIAL — guarded repos measured and the remaining
arm never runs under a bound." — open
```

## Actual synthetic outputs

`U` below means one `LG-SEAT-UNCARRIED`; `[]` means no carry findings.

| Case | Expected carry_exit / findings | Pristine | M2 | Restored |
|---|---|---|---|---|
| TC1 wrap-unmarked | 1 / U | 1 / U, pass | 1 / U, pass | 1 / U, pass |
| TC2 wrap-marked | 0 / [] | 0 / [], pass | 0 / [], pass | 0 / [], pass |
| TC3 wrap-complete | 0 / [] | 0 / [], pass | 0 / [], pass | 0 / [], pass |
| **TC4 wrap-bullet-wrapped** | **0 / []** | **0 / [], pass** | **1 / U, FAIL** | **0 / [], pass** |

All twelve synthetic observations had `markers=1 reports=1 statuses=1 heading=1`. The mutant's TC4 finding was exactly:

```json
["LG-SEAT-UNCARRIED", ".ufo/waves/round-18/w1/SeatWrap.md", "line 3: STATUS: PARTIAL — guarded repos measured and the; paragraph continues at line 4 (mark the cut with ...)"]
```

Actual detector summary lines:

```text
SUMMARY pristine pass=10 fail=0 detector_exit=0
SUMMARY M2 pass=9 fail=1 detector_exit=1
HISTORICAL_CHANGED []
TC_CHANGED ['wrap-bullet-wrapped']
SUMMARY restored pass=10 fail=0 detector_exit=0
```

## Historical carry controls

The first five worlds use the exact replay revisions and original round numbers enumerated at `census/round-17/gate-replays.py:69-78`. Expected carry pairs are the carry-only projection of `census/round-17/gate-replays-expected.json:10-184`. The additional strict control uses the named round-18 base and the carry-only projection of `census/round-19/gate-r18-under-strict.json:3-36`; that record's unrelated pointer findings are not carry findings.

For every revision, inputs were **all** `.md` reports under `.ufo/waves/round-<round>/` plus `corpus/lessons/round-<round>.md`, read with read-only git and frozen before the pristine run. The detector did not force old rounds into the strict branch.

| World / immutable revision | Round | Reports / markers / STATUS lines / heading | Carry findings, pristine → M2 → restored | Complete output moved? |
|---|---:|---|---|---|
| r15-landing `b410186cea626a67c92396ac58fbd57fb86876ac` | 15 | 64 / 1 / 17 / 0 | 1 → 1 → 1 | No |
| r13-admitted `a31642d14006830ec62edf40b0354c3699728c4a` | 13 | 32 / 0 / 1 / 0 | 0 → 0 → 0 | No |
| r14-landing `cc2168325768d5356a82c039dcdf787377c55784` | 14 | 32 / 0 / 0 / 0 | 0 → 0 → 0 | No |
| r16-landing `6ff91f534eece9adde5f667cb7dad400c145351b` | 16 | 141 / 30 / 146 / 1 | 0 → 0 → 0 | No |
| r16-precarry `79bbe7a62199260694943ec7186fef6ebff9d41a` | 16 | 141 / 30 / 146 / 1 | 29 → 29 → 29 | No |
| r18-base-strict `3ab2c81479f5004c8bc91946eea482caec45408f` | 18 | 175 / 10 / 172 / 1 | 0 → 0 → 0 | No |

Every nonzero historical finding was `LG-SEAT-UNCARRIED`. The r15 finding remained at `.ufo/waves/round-15/w1/ConfigRepair.md`; the r16-precarry multiset matched all 29 frozen expected pairs. SHA-256 of sorted `(id, path)` JSON pairs was unchanged in all stages:

- Empty pair list: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- r15-landing: `d54c38ba86be581618d32cdf8cf479cc73e828cab7d0461c331a138c948fd25b`.
- r16-precarry: `c19d75a95af996904a85d7e0bd207e994c3142e5c28d604962a9cc907e0a631b`.

Calibration limit: r13/r14 have zero failure markers and are not positive carry-coverage evidence. The five pinned rounds precede the strict threshold and therefore cannot themselves detect M2. The additional r18 control exercises the strict branch but contains no M2-sensitive carry; TC4 supplies that discrimination. No unconditional-strict counterfactual or whole-gate replay is claimed.

## Hashes, frozen inputs, and restoration

| Object / stage | SHA-256 |
|---|---|
| Proposed worktree gate snapshot / pristine | `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd` |
| Same private gate with M2 | `e32165e39ee42d600d968cae409cb74c86153f79d7e942cf19e12f0fc551831f` |
| Same private gate restored | `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd` |
| Fixture source / unchanged private copy | `fa30d377cb52a5fe529aad401eca3c451acac878a29629cfba865cbf4a5e431c` |
| Detector source, unchanged across runs | `166b6e21d9fc849c74297768fc895546fe7dbb8d41d84e764cbc6c66556ec06a` |
| Complete ten-world input JSON, unchanged across runs | `d49476c992b4ed480ccb4eccf9d65c508bf267da4e7a9175af54b7fdaf921065` |
| Pinned replay expectation source | `d11d3413146e7c90c8afac5b8afa1a4acc32bfcefa0a7d76edbe1a3e9d6c7346` |
| Strict-r18 expectation source | `a1b688b0b7de9a592409cf94ed54e34188ff0f61d2dae66523f9999ba1d6a198` |

Historical input manifest hashes (each manifest sorts by path and contains path, original git blob OID, raw-byte SHA-256, and byte count):

| World | Files including lesson | Manifest SHA-256 |
|---|---:|---|
| r15-landing | 65 | `5675b645029dd64016a1205019b117b7c117e35b615b98dc4e004e5550c495d5` |
| r13-admitted | 33 | `856588b17beae29e21ece5ed8c1fa05755b867bc7a74ccb382c6ea4569603cc0` |
| r14-landing | 33 | `75d08267ff70d0f8da2f34fa186c4d72c2676368411cc69ff4a67654900a063a` |
| r16-landing | 142 | `ac113cf1395f1ede50469a05340f96625b48139db1baa8ef8dbf27ca7e4ac691` |
| r16-precarry | 142 | `73567134621c4d97e593c6de7a346d1faadd3f999459bdf9a7e07b4d1a0bbbc2` |
| r18-base-strict | 176 | `1a968d7250f9e652d0db8182f9ee948dd513697f1249539eb9260363c6663049` |

Input and pair hashes use UTF-8 JSON with `ensure_ascii=False`, `sort_keys=True`, `separators=(',', ':')`. The complete input JSON includes all fixture file texts, names, revisions, original rounds, and expectations.

Actual restoration/immutability output:

```text
RESTORE exact_bytes=True sha256=02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd
RESTORE identical_detector_results=True
INVARIANT detector_bytes_unchanged=True
INVARIANT fixture_bytes_unchanged=True
INVARIANT stimuli_unchanged=True
CLEANUP scratch_absent=True
```

# Commands run

- Used `read`, `glob`, and scoped `grep` to read the requested skills, tooling rules, preregistration, closure/residual/planned context, carry code, fixture, and historical replay definitions/expectations. Preregistration references: `.ufo/waves/round-19/preregistration.txt:7-27`; prior TC4 rationale: `.ufo/waves/round-18/w1/ScoutCarryWrap.md:175`.
- Used Python **3.14.8** through Eval for private byte copies, AST extraction of fixture constants, hashing, read-only historical input collection, and the three detector calls. No persistent Python bytecode was written (`sys.dont_write_bytecode=True`).
- Historical input collection made **603 read-only git commands**: six `rev-parse`, six `ls-tree`, and 591 `show`. Command shapes, instantiated only with the six revisions and round/path pairs above:

  ```text
  /usr/bin/git --no-pager -C <lane> rev-parse --verify <40-hex>^{commit}
  /usr/bin/git --no-pager -C <lane> ls-tree -r -z --full-tree <40-hex> -- .ufo/waves/round-<N>/ corpus/lessons/round-<N>.md
  /usr/bin/git --no-pager -C <lane> show <40-hex>:<selected-report-or-lesson-path>
  ```

  Child git environment was explicitly limited to `PATH`, private scratch `HOME`, `LC_ALL=C`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_TERMINAL_PROMPT=0`, `GIT_NO_LAZY_FETCH=1`, `GIT_NO_REPLACE_OBJECTS=1`, and `GIT_OPTIONAL_LOCKS=0`.
- Wrote one temporary detector under the assigned scratch root. Its execution core, identical for all stages, was:

  ```python
  source = Path(gate_path).read_bytes()
  gate = types.ModuleType("private_carry_gate")
  exec(compile(source, str(gate_path), "exec"), gate.__dict__)
  for world in worlds:
      blobs, tree = {}, {}
      for path, text in world["files"].items():
          data = text.encode("utf-8")
          oid = hashlib.sha256(data).hexdigest()
          blobs[oid], tree[path] = data, oid
      gate.blob_by_oid = lambda root, oid: blobs[oid]
      findings, markers, reports, statuses, heading = gate.check_carry(
          str(Path(gate_path).parent), tree, world["rev"], world["round"])
  ```

  Called `detect(scratch / 'souji-landing-gate.py', worlds)` for pristine, M2, and restored bytes. The pristine result was required to have zero detector failures before mutation. No exception or prerequisite failure occurred.
- Applied and reversed the single-line M2 change using `edit` on the private gate. Compared restored bytes directly with the pre-mutation byte snapshot; reran the same detector; checked that fixture, detector, and input bytes were unchanged; removed only `/var/tmp/souji-r19-MutCarryJoin/` using `shutil.rmtree` after restoration evidence was captured.
- **Unrun:** external fixture CLI, gate CLI, gate selftest, full historical replay runner, census, builds, linters, and fleet-reading fixtures. None is represented as passed.

# Contract compliance

- Leaf seat only: no subagents, swarm, peer broadcast, other agent runtime, or ask call; no integration or round judgment.
- Only persistent lane write is this assigned report. No lane tool, test, census, corpus, skill, scoreboard, log, province, driver, fleet, or sibling source was edited. Concurrent worktree changes by other seats are not attributed to this probe; this report binds the source snapshot actually measured.
- All scratch writes remained under `/var/tmp/souji-r19-MutCarryJoin/`. Exact pre-mutation bytes were restored before cleanup; the scratch directory was confirmed absent afterward. No global `TMPDIR` change.
- No git or jj mutations, jj command, process signal, live census, `/proc`/environment-secret inspection, credential read, network request, or public-document quote.
- Tool installs/updates: **none**. No pacman transaction. Tooling rules were read before work.
- No additional patch/artifact is delivered. **Final mutation outcome: KILLED by TC4; 0 of 6 tested historical carry controls moved; exact restoration observed.**
