STATUS: DONE — pin reconstructed end-to-end; reversion was mechanically forced by three coupled pin carriers; legitimate r19 re-derivation is a 7-step ceremony, fully specified below.

# RevengeR14Pin — why `tools/souji-preservation-evidence.py` pins `tests/fixtures/r14-census-boundary.py` by NAMESPACE_SHA256, and what a legitimate re-derivation for r19 requires

All paths relative to the lane root. Revision inspected: tip `5efb519` (clone at `/var/tmp/souji-r18w2-RevengeR14Pin/lane`, detached, deleted after use). Tool installs/updates: none (pacman pause respected; nothing needed).

## 0. Attacked claim

C1 (r18 wave 1) states: r14-census-boundary.py "was reverted to b576341 bytes because tools/souji-preservation-evidence.py pins its digest". Verified true, and the pin's reach is wider than the claim states: **three live carriers** enforce the r14 bytes, not one.

## 1. The pin and its identity

- `tools/souji-preservation-evidence.py:306-307`:
  `NAMESPACE_FIXTURE_PATH = "tests/fixtures/r14-census-boundary.py"` /
  `NAMESPACE_SHA256 = "e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2"`.
- Measured: `git cat-file -p <rev>:tests/fixtures/r14-census-boundary.py | sha256sum` → `e6a984b1…d14b2` at **b576341**, at **5efb519**, and in the **working tree** — pin and fixture agree today; the wave-1 revert (`2fc5f33`, message "r14 fixture back to pinned bytes") restored byte identity. `git diff --stat b576341 5efb519 -- <fixture> <checker>` is empty.
- Docstring repeats the literal at `:106-108` (BASELINE/NAMESPACE pins, `NAMESPACE_IDS R14C2-01 .. R14C2-12`) — a fourth textual site that must move with any re-pin or the doc lies (r16 overclaim discipline, R16-M1 class).

## 2. Why the pin exists (reconstructed contract)

The r14 fixture is the **unchanged third-party control** of the r15/r16 preservation admission claim. Checker docstring `:10-12`: "changed tool passes every config case while the **unchanged r14 namespace fixture** passes 12/12"; `:76-82` schema: `namespace_fixture` measured under `--root` **AND equal to the pinned r14 digest**; `namespace_controls` one run over the R14C2-01..12 universe, all pass on changed (`:116-117`).

Contract root (round-15 lesson, `corpus/lessons/round-15.md`): R15-M1 fix cell — "**Q22 requires** value/effect-aware configuration treatment and paired benign/mixed-fleet behavioral controls alongside **unchanged namespace controls. C1 is admitted only if the committed identical fixture distinguishes baseline red from changed green** for the routed reason." Gate: "C2 only with actual self-invocation negative controls and **pinned frozen evidence**." The pin is the mechanical enforcement of "committed identical fixture": a control oracle that could drift with the code under test makes the preservation claim unfalsifiable — green could be manufactured by weakening the fixture instead of the census. The fixture is a strace+PATH-spy isolation oracle authored in r14 (`tests/fixtures/r14-census-boundary.py:2-26`: synthetic store under /var/tmp, canary `:44`, 12 case ids `:45-58`, `FINDING = "path-protected"` `:43`, `BASELINE_SHA = 6a000c59…` `:61`), i.e. evidence predating every census change it controls for.

Provenance (`git log -S e6a984b1…`): digest first recorded by r14's own measurement records (`552cae4` → `census/round-14/run-targeted.py`, `verification-attempt-1.json`; `42d0b7b` → `census/round-14/{counts,verification}.json`), then hardcoded into the checker at r15 landing `b410186`; later commits touch only records/lessons citing it (`0a70bef`, `7a79dc2`, `163158a`, `4f48343`, `95519a7`, `3f822e8`). Fixture file history: created r14 (`48f8945`, `552cae4`), changed once by r18 wave 1 (`3f822e8`), reverted (`2fc5f33`).

## 3. The enforcement web (what breaks if r14 bytes change without re-derivation)

1. **Record admission** — `:1154-1164`: any record whose `namespace_fixture.sha256 ≠ NAMESPACE_SHA256` gets finding `pinned-mismatch` (not in `LEVEL1_FINDINGS` `:269-281` → level 2) → status `could-not-evaluate`, exit 2 (docstring `:58-62`).
2. **On-disk binding** — `:1243-1248` (`_check_bindings`): record declaring the pinned digest over bytes that hash differently under `--root` → `binding-digest-mismatch` (level 2).
3. **Selftest hard gate** — `:1962-1966`: `--selftest` first checks `_lane_fixture_available(lane)` (`:1920-1925`, digest equality) and **exits 2 printing `selftest-unavailable: … missing or differs from the pinned r14 digest`** if the lane fixture ≠ pin. With wave-1 bytes in the tree, the whole checker selftest refuses to run. (`_selftest_root` `:1907-1917` copies the real fixture into test roots; `_record` `:1879-1886` derives the record's ns digest from those bytes — the synthetic fallback `:1913-1916` only feeds expected-red cases.)
4. **Frozen mode** — `_record_bound_paths` `:1640-1641` and `_frozen_expected` `:1943-1945` require snapshot pins over {r15-config, r14 fixture, census}; `tests/fixtures/r15-preservation-frozen/record.json:96-99` carries `namespace_fixture.sha256 = e6a984b1…` and `expected.json:3` pins the same digest in `files` — **two more live carriers**. A changed fixture → `snapshot_tampered`/`pinned-mismatch` (the exact r15 defect, resolved only by re-pinning at `7a79dc2`). The landing gate audits these pins (`LG-FROZEN-PIN`/`LG-FROZEN-MEASURED`, `census/round-18/gate-replays-r18.json:78-107`).
5. **Case universe** — `NAMESPACE_IDS` `:364-367` is a literal; dropping/renaming R14C2 ids → `case-missing`/`namespace-incomplete`. Transcript shape is exempted from r15-only token rules only for the plain-`ok` r14 form (`:1488-1491`) — a reworded transcript loses that exemption.

This is why wave 1 took the session-kill change only into r15/r17 fixtures and reverted r14: steps 3–4 are immediate, mechanical, and would have turned the preservation gate and its selftest red at landing.

## 4. What wave 1 actually changed in r14 (recovered diff, `git show 3f822e8`)

Harness-only session-kill, mirroring the census's own `--repo-timeout` semantics: new `run_isolated()` (`Popen(start_new_session=True)`, on `TimeoutExpired` → `kill_session(proc.pid)` scanning `/proc/<pid>/stat` field 6 + `os.killpg(SIGKILL)` fallback), substituted into `run_setup` (timeout 60), `probe_strace` (20), `run_tool` (90, timeout → `Result(124, …)`). No case id, oracle, expected exit, canary, or transcript-format change. Resulting digest `6c1c0cfde846be2f9c56402eddf24de0337350f007998d0c48da3ce9eb6fb5e3`.

**Divergence found (disclosed, but real):** the landed C1 record `census/round-18/c1-matrix-worktree.json` `fixtures_sha256["r14-namespace"] = 6c1c0cfd…` with `fixtures_dirty: "M tests/fixtures/r14-census-boundary.py …"` and `"allow_dirty_fixtures": true` — i.e. **the landed r14-namespace acceptance numbers (12: 10/0/0/0) were measured on the session-kill bytes, which are not in the tree at tip**; the tree ships `e6a984b1…`, whose 0-fail behavior at the r18 census is certified only via the b576341-arm run in the same record. Disclosed (`--allow-dirty-fixtures`; lesson: "measured on the integrated worktree whose code is committed at 3f822e8"), but it means tip evidence for the pinned bytes and the session-kill harness never coexist in one record. r19's re-derivation closes exactly this.

Precedent that the ceremony works: wave 1 already ran it for the r15 fixture — `tests/fixtures/r15-preservation-frozen/record.json:7` `measured_commit: 2fc5f33d0b000c0e10450a5139137bf4300fe54b`, regenerated from real runs and landed at `5efb519` ("r15 frozen preservation record regenerated at 2fc5f33"), with `expected.json` pins updated (r15-config `61208dbd…` = session-kill version). Frozen-record regenerations: `7a79dc2` (c6207bd), `d7e648d` (ddb7347), `5efb519` (2fc5f33).

## 5. Legitimate re-derivation for r19 (so r14 can take the session-kill change)

Substantive precondition (control integrity, Q22): the change must stay harness-only as in `3f822e8` — same 12-case universe, same oracles (exit/finding/canary/spy/strace), same plain-`ok` transcript shape. Weakening a case is not re-derivation; it is control tampering and the checker cannot bless it.

1. Land the r14 fixture change; `sha256sum tests/fixtures/r14-census-boundary.py` → new digest D.
2. Update the checker literals: `NAMESPACE_SHA256` at `tools/souji-preservation-evidence.py:307` **and** the docstring line `:107`. Nothing else in code carries the digest. Order matters: the constant must move **before** regenerating the frozen record, else step 3 records `pinned-mismatch` (exit 2, no clean verdict).
3. Regenerate `tests/fixtures/r15-preservation-frozen/record.json` from real runs at the r19 integration commit (README `:12-17` procedure; `regenerate.py` re-runs the `namespace_controls` arm of the changed census under the new r14), then refresh `expected.json` `files` pins (r14 → D, r15-config, census) and `record_sha256`.
4. Re-run the matrix (`census/round-18/run-matrix.py` r19 successor) **without** `--allow-dirty-fixtures`, so the fresh record's `fixtures_sha256["r14-namespace"] == D`; state that equality in the round record (R16-M2 lesson: pins were recorded, not checked — make the equality an asserted check, not prose).
5. Run `tools/souji-preservation-evidence.py --selftest`: it exits 2 `selftest-unavailable` unless lane bytes == new pin (`:1962-1966`), so this is the natural post-edit proof; record the check count.
6. Re-run and re-record the landing-gate replays (the `expected.json` digest change feeds the tip-replay `LG-FROZEN-PIN`/`LG-FROZEN-MEASURED` checks; cf. `census/round-18/gate-replays-r18.json`).
7. Disclose the re-derivation in the round lesson/LOG: before/after digests, the integration commit, the fresh records, and the reason the control's bytes moved (harness-only, oracles unchanged). Historical r14–r18 records keep the old digest — they are never rewritten.

Required post-state: preservation evaluate (frozen) `clean`; `namespace_controls` 12/12 pass on changed; baseline discrimination intact (preharm a31642d still fails its ~10 red cases; cc21683/b576341/changed arms 0 fail).

## 6. Exact commands and outputs (evidence)

- `git cat-file -p b576341…:tests/fixtures/r14-census-boundary.py | sha256sum` → `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2`; same for `5efb519…` and the working-tree file (three-way identity).
- `git log --format='%h %ad %s' -S NAMESPACE_SHA256` → `2fc5f33`, `fb23b12`, `b410186`; `-S e6a984b1…` → `3f822e8, 95519a7, 4f48343, 163158a, 7a79dc2, 0a70bef, b410186, 42d0b7b, 552cae4`.
- `git log -- tests/fixtures/r14-census-boundary.py` → `2fc5f33, 3f822e8, 552cae4, 48f8945`; `git show 3f822e8 -- <fixture>` → the session-kill diff (§4); `git cat-file -p 3f822e8:<fixture> | sha256sum` → `6c1c0cfd…`, equal to `c1-matrix-worktree.json` `fixtures_sha256["r14-namespace"]`.
- `git log -- tests/fixtures/r15-preservation-frozen/{record,expected}.json` → `5efb519, 95519a7, d7e648d, 7a79dc2, b410186`; `git rev-parse 2fc5f33d0b000c0e10450a5139137bf4300fe54b` → resolves (the record's `measured_commit` is a real commit).
- Static reads only; the checker and fixtures were **not executed** (no ALLOWED-EXEC on this item; all `:line` citations from grep/read of the tip clone).

## 7. Verdict and smallest fix

**Verdict: holds.** The claim's mechanism is real and understated: three coupled carriers (checker constant+docstring, frozen `record.json`/`expected.json` pins, plus the selftest exit-2 gate) force the r14 revert; §3.3 alone (`selftest-unavailable`, exit 2) would have failed the landing. No defect in the pin design found; the pin did its job (tamper-evident control).

Smallest fix (r19, as routed): execute §5 — a deliberate, disclosed re-derivation: fixture harness change + `NAMESPACE_SHA256`/docstring re-pin + frozen-record regeneration at the integration commit + clean-tree matrix re-record (closing the §4 dirty-bytes divergence) + selftest and gate-replay re-runs. No code change to the checker's logic is required; only the literal at `:307` (and docstring `:107`) moves, together with the records.

[INFERENCE] marks: §2 "tamper-evidence" rationale is reconstructed from the r15 lesson text and checker docstring (no commit message states intent); §5 ordering (constant before regeneration) is derived from the `pinned-mismatch` code path, not from a witnessed failure.
