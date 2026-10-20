# LegacyPreserve — 38 legacy selftest assertions and config-fixture preservation map

Seat: `SoujiR15.LegacyPreserve` (scout, leaf). Axes: operability, calibration.
Mode: SOURCE INSPECTION ONLY. Nothing executed, no tests/probes/builds/edits outside this report. No credential path, operator-sweep path, or sibling file opened. Tool installs/updates: none.
Source state: `tools/souji-census.sh` sha256 `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9`, 1539 lines — byte-identical to the round-14 shipped tool and to the r14 closure's recorded changed digest (`.ufo/waves/round-15/w1/OutputLeak.md:6`). `tests/fixtures/r15-census-config.py` and `tests/fixtures/r15-preservation-frozen/` are absent at inspection. Everything about the new config fixture below is therefore **design-only**; every legacy assertion fact is source-observed at the named lines.

## 1. What "38" counts, exactly

`run_selftest()` spans `tools/souji-census.sh:1187-1497`. It contains **35 `st_ok` call sites** inside that range (verified `grep -c` + `awk NR>=1187 && NR<=1497`), because `st_ok` is a counter (`:1152`, `:1153`). One site sits inside the four-file malformed-baseline loop (`for f in bad empty blank-lead blank-before-header`, `:1437-1445`), contributing four runtime checks. Arithmetic: 34 single sites + 4 loop checks = **38 runtime checks**, matching the recorded r14 observation (`corpus/lessons/round-14-verifier-spotcheck.md:98`: `legacy census selftest: 38 checks, 0 failed`). A repair that changes the selftest must preserve this count *and* each check's subject; a count-only check is green-only evidence (Q22/C2).

Fixture fleet built at `:1194-1272`, all under `mktemp -d /var/tmp/...` (`:1192`), removed by trap (`:1193`):

| fixture | shape | source |
|---|---|---|
| `clean-shokunin` | 2 commits, local `master` = `origin/master`, future-dated `.ufo` sentinels committed | `:1197-1205`, `:1263-1272` |
| `dirty-shokunin` | pushed tip + `untracked.txt` + `.scratch/note.txt` + `.scratch/credentials.env` | `:1207-1219` |
| `unpushed-shokunin` | `origin/master`=u1, local `master`=u2, 3 worktrees (main, present dirty `wt1`, absent registration) | `:1221-1245` |
| `noremote-shokunin` | one local commit, no `refs/remotes` | `:1247-1252` |
| `plain-dir`, `.hidden-shokunin` | non-repo / dot-dir that must not become rows | `:1255-1261` |

**No fixture repo in this fleet writes a local `.git/config` key.** `st_init` is `git init` (`:1169-1172`); `st_commit` uses plumbing plus only `-c user.name/-c user.email` on `commit-tree` (`:1154-1167`). Grep of the whole selftest for config keys finds only the synthetic protected-store `config.yml` at `:1456` and comments. `guard_git_config` (`:493-522`) is consequently a no-op for all 38 checks: `git init` writes only `core.repositoryformatversion`, `core.filemode`, `core.bare`, `core.logallrefupdates`, none of which match the refusal patterns at `:504-506`. **0 of 38 assertions exercises any config family.** This is the central mapping fact: the 38/38 green observation is necessary but cannot discriminate a config-repair regression.

## 2. Control codes used below (design-only)

The fixture that can preserve the legacy fleet cases is `tests/fixtures/r15-census-config.py`, owned by `ConfigFixture`; it does not exist yet. Controls are named by class, not by invented case IDs; the fixture author pins the literal `R15CFG-NN` tuple (FixtureCounts floor: 49+ IDs, `FixtureCounts.md:25-46`).

| code | control | oracle |
|---|---|---|
| **P0** | identical config-free mixed fleet, r14 tool (digest `fcff8b05…`) vs repaired tool, back-to-back on the same tree, no mutation between runs | stdout byte-identical for all 4 rows + header; this is the only oracle that preserves every legacy row value without re-encoding it |
| **P1** | benign single-family member inside the 4-repo mixed fleet (families F01-F10, F13, F14 of FixtureCounts) | changed exit 0; one row per expected repo, no extra/missing; unaffected peers' 6 fields equal the P0 rows; configured repo's own row present with fixture-pinned counts |
| **P2** | neutralization fidelity: benign `core.hooksPath`, `core.excludesFile`, `core.attributesFile`, `core.fsmonitor` values chosen so that *honoring* them would change `dirty` | dirty count/flag equals the current neutralized contract (`count_dirty:706-724` forces `-c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null` at `:710-712`); this is the only control that detects removal of the `-c` overrides |
| **P3** | benign config in worktree owner and in a worktree admin dir (`config.worktree`/admin `config`) | `worktrees=3`, flags `wt-dirty`,`wt-absent` retained; linked worktree still not its own row |
| **P4** | `noremote-shokunin` with a benign config key | `no-remote` flag and `unpushed>=1` retained |
| **P5** | unsafe values per family (protected target, `~`, `true` promisor, non-empty `alternateRefsCommand`, attribute-bound filter, matching protected `includeIf`) | exit 2 with stable `path-protected` finding; spy/strace show zero synthetic-store access (r14 pattern `tests/fixtures/r14-census-boundary.py:505-541`) |
| **P6** | compare on the config-bearing fleet: identical, then mutate `.scratch` size and dirty set | identical → exit 0, stdout exactly `DIFF_HEADER`; mutation → exit 3, rows `dirty-shokunin\t scratch_bytes` and `\t dirty` |
| **P7** | mtime/no-leak on the config-bearing fleet | `mtime_iso` is `YYYY-MM-DDTHH…`; future-dated `.ufo/watchdog.log`/`.ufo/state` ignored; secret-shaped contents absent from stdout+stderr |
| **P8** | protected `--root` / `--compare` alias with a config-bearing fleet | exit 2 `path-protected` before access (extends the two legacy protected checks) |

P0 is the preservation primitive; P1-P8 add the config dimension the legacy fleet lacks. All P-controls must run under synthetic HOME and `/var/tmp` only, with a cleanup trap (Q4).

## 3. The 38 assertions (execution order)

Line = PASS branch in current bytes; the quoted text is stable identity if `ConfigRepair` shifts lines.

| id | line | assertion (quoted text) | depends on | preserving control |
|---|---|---|---|---|
| L01 | 1281 | `repeat: two runs byte-identical` | whole fleet, no mutation | P0 (+ P1 repeat) |
| L02 | 1288 | `header matches contract` | `HEADER` | P0 |
| L03 | 1297 | `row count 4 (main repos only)` | enumeration | P0, P1 |
| L04 | 1300 | `plain-dir skipped` | enumeration | P0, P1 |
| L05 | 1301 | `dot-dir skipped` | enumeration | P0, P1 |
| L06 | 1303 | `linked worktree not a separate row` | `.git` file non-row | P0, P3 |
| L07 | 1309 | `clean-shokunin verdict=clean` | clean row | P0, P1 |
| L08 | 1313 | `clean worktrees=1` | clean row | P0, P1 |
| L09 | 1315 | `clean unpushed=0` | clean row, `count_unpushed` | P0, P1 |
| L10 | 1317 | `clean dirty=0` | `count_dirty` (neutralized status) | P0, P1, P2 |
| L11 | 1321 | `dirty count=2 (untracked file + collapsed .scratch/)` | dirty row, porcelain collapse | P0, P1, P2, P6 |
| L12 | 1324 | `dirty scratch_bytes=$v (>0)` | `scratch_bytes:726-742` | P0, P1 |
| L13 | 1328 | `dirty flags include dirty,scratch,secret-shaped` | `newest_mtime` secret classifier `:744-799` | P0, P1, P2, P7 |
| L14 | 1333 | `unpushed count=1` | `count_unpushed:694-703` | P0, P1, P3 |
| L15 | 1335 | `unpushed worktrees=3` | `count_worktrees:686-690` | P0, P3 |
| L16 | 1338 | `unpushed flag present` | `census_one:864-920` | P0, P1, P3 |
| L17 | 1342 | `wt-dirty flag present` | `worktree_extra_flags:800-840` | P0, P3 |
| L18 | 1346 | `wt-absent flag present` | absent registration path | P0, P3 |
| L19 | 1352 | `noremote flag present` | `count_unpushed:697-700` | P0, P4 |
| L20 | 1356 | `noremote unpushed=$v (>=1, unverifiable but counted)` | same | P0, P4 |
| L21 | 1363 | `secret file contents absent from census` | output purity | P0, P7 |
| L22 | 1368 | `forbidden surface contents absent` | `.ufo` sentinels not read | P0, P7 |
| L23 | 1374 | `mtime_iso shape` | `newest_mtime` | P0, P7 |
| L24 | 1378 | `mtime ignores future .ufo/state and .ufo/watchdog.log` | prune list `:748-752` | P0, P7 |
| L25 | 1391 | `compare identical: exit 0, header only` | `emit_compare:1083-1145` | P0, P6 |
| L26 | 1407 | `blank-after-header compares clean (exit 0, header only)` | `load_census:997-1030` | P6 (pure parser; config-independent) |
| L27 | 1421 | `compare mutation: exit 3` | `emit_compare` | P6 |
| L28 | 1424 | `compare reports scratch_bytes` | diff row | P6 |
| L29 | 1428 | `compare reports dirty delta` | diff row | P6 |
| L30 | 1443 | `bad compare baseline exits 2` | `load_census` header/columns | none (config-independent) |
| L31 | 1443 | `empty compare baseline exits 2` | same | none |
| L32 | 1443 | `blank-lead compare baseline exits 2` | same | none |
| L33 | 1443 | `blank-before-header compare baseline exits 2` | same | none |
| L34 | 1451 | `unknown flag exits 2` | arg parser | none |
| L35 | 1466 | `protected root refused before access (exit 2, path-protected)` | `protected_fail:160-164` | P8 |
| L36 | 1477 | `protected compare alias refused (exit 2, path-protected)` | alias resolution | P8 |
| L37 | 1486 | `no forbidden git subcommand` | source audit regex | none (source-only) |
| L38 | 1490 | `fixtures under mktemp ($ST_TMP)` | Q4 | none (external fixture must satisfy Q4) |

Group counts: determinism/schema 2 (L01-L02); enumeration 4 (L03-L06); clean 4 (L07-L10); dirty 3 (L11-L13); unpushed/worktree 5 (L14-L18); noremote 2 (L19-L20); no-leak/mtime 4 (L21-L24); compare 5 (L25-L29); malformed/usage 5 (L30-L34); protected boundary 2 (L35-L36); hygiene 2 (L37-L38). Total 38.

## 4. What the 38 cannot prove (blind spots a "38/38 green" claim must not hide)

1. **Config families: zero coverage.** No fixture repo writes a refused key; `guard_git_config` is inert in all 38. A repair that deletes the guard entirely, or that accepts every value including unsafe ones, still yields 38/38.
2. **Whole-fleet abort is invisible.** The refusal mechanism is `protected_fail` → `exit 2` (`:160-164`) from `guard_git_surface` during `list_repos` (`:922-968`), before `emit_census` prints the header (`:973-995`). One benign key suppresses every peer, and no legacy assertion has a config-bearing peer to lose.
3. **Neutralization removal is invisible.** `count_dirty` forces the three `-c` overrides at `:710-712`; the legacy fixtures have no excludes/attributes/hooks values that could reveal a change. Dropping `-c core.excludesFile=/dev/null` would silently change dirty counts only on configured repos — exactly the case absent from the 38.
4. **Unsafe-config refusal has no legacy control either.** The r14 namespace suite `R14C2-01..12` covers roots, aliases, gitfiles, commondir, worktrees, alternates, env poisoning and compare aliases — but no config key (`grep` of `tests/fixtures/r14-census-boundary.py` for `hooksPath|include|filter|promisor|worktreeConfig|excludesFile|attributesFile|fsmonitor|alternateRefs|partialClone` = 0 matches). Config safety and config preservation both depend on the new fixture.
5. **Exit-only assertions are green-only.** L30-L34 assert only exit 2; do not clone that style for the config fixture. P1/P5 must assert rows, field values, and access traces, not just exit codes (Q22: "preserve meaningful dirty counts and mixed-fleet rows").
6. **Baseline identity is not the r14 fixture's `BASELINE_SHA`.** `tests/fixtures/r14-census-boundary.py:61` pins `BASELINE_SHA = 6a000c59…` (a31642d, pre-guard). The harmful r14 tool is `fcff8b057b3e…`. The new fixture must take explicit `--tool PATH` and pin the harmful digest for the red arm; reusing `is_baseline` semantics would silently skip the access/reason check for the r14 bytes (design peer `FixtureCounts.md` §1.8; `AdmissionRules.md:155`).

## 5. Exact acceptance needed (design-only; fixture absent)

Owner of the fixture: `ConfigFixture`. L1 runs these only after all seats finish (Q24). Expectations below are requirements, not observations.

1. **File and interface.** `tests/fixtures/r15-census-config.py` exists, committed; one identical file for baseline and changed arms; `--tool PATH`; exit 0 clean / 1 failed honest evidence / 2 could-not-evaluate (missing tool, missing strace, root, usage). `--list` prints a literal, fixture-owned ID tuple; the no-`--case` run asserts `ran == EXPECTED_IDS` and fails on set mismatch. No `--case` subset may produce a green gate (r14 partial-run gap, `r14-census-boundary.py:722-727`; FixtureCounts A1).
2. **Red arm (same command).** `--tool <r14 bytes, digest fcff8b057b3e…>` → exit 1, with every benign ID failing for the routed reason: exit 2 + `git-config-unsupported`, no TSV, whole fleet suppressed. Unsafe IDs must *pass* on the baseline too (both versions refuse), so per-ID expected baseline outcomes are mixed by design; do not require every ID to be red.
3. **Green arm.** `--tool <repaired>` → exit 0: benign IDs pass with exact rows; unsafe IDs still refuse exit 2 with the stable finding and zero synthetic-store access; P0 byte-identity vs the r14 tool on the config-free fleet; P1 mixed-fleet unaffected rows exact; P2 dirty fidelity; P3 worktree flags; P6 compare 0/3; P7 mtime/no-leak.
4. **Namespace retention.** `python3 tests/fixtures/r14-census-boundary.py --tool <repaired>` → 12/12 PASS; with the a31642d baseline → 2/12 PASS with access evidence (`r14-census-boundary.py:505-541`). The r15 fixture must not replace or edit this suite.
5. **Legacy retention.** `bash tools/souji-census.sh --selftest` → 38 checks, 0 failed, exit 0, and each assertion subject unchanged (not merely the count); `shellcheck -S warning tools/souji-census.sh` → exit 0. These are necessary preconditions only; C2 must reject a record whose sole C1 preservation evidence is 38/38 + green-only.
6. **Hermetic setup.** The fixture's own `git init`/commit setup must export `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1` and identity/date pins (r14 pattern `r14-census-boundary.py:139-171`) so the only config keys are the case-authored ones; the legacy selftest setup does not do this for its own fixtures (it relies on the tool clearing its environment at `:117-127`).
7. **Determinism for P0.** Run both tools back-to-back on the same tree with no writes between; `mtime_iso` and absolute repo paths are in the TSV, so a copied/rebased fleet breaks byte-identity. Use one fleet, two invocations.

## 6. Remaining unknowns (not resolved by source inspection)

- The fixture's literal case IDs and per-ID matrix (owner: ConfigFixture). Not invented here.
- **Repair contract for hooks/attributes/excludes:** exact-`/dev/null`-only acceptance vs broader value-boundary acceptance. This changes P2's expected dirty counts: if a benign excludes file is honored instead of neutralized, L11-equivalent counts change. The chosen contract must be pinned before the fixture expectations can be written (D4 in `FixtureCounts.md`).
- **Mixed fleet with a genuinely unsafe repo (D1):** abort-all (current) vs rows + exit 2 vs skip. P1 and P5 cannot share one case until this is decided; P0/P1 assume the benign case exits 0 with all rows.
- Whether `extensions.partialClone` without a promisor remote is accepted (D6).
- Whether worktree `config.worktree` with `extensions.worktreeConfig=true` is in scope this round (fixture prompt names only `false` as benign).
- `core.worktree` is already value-aware (`:509-521`, `~` refused, path boundary-checked) and must not regress to key-only refusal while other families are edited.

## 7. Process disclosure (boundary deviation, not repeated)

Before the authoritative no-query reminder arrived, one command traversed the lane root recursively: `grep -rn "selftest" --include=*.md -l .` with cwd `/home/vgpnk/Projects/shokunin/souji-shokunin`. Output was 20 `.md` paths, all under `corpus/` and `census/round-*` (round-6/8/etc.); no `census/operator-sweep-*` path appeared. The initial `read` of the lane root directory listed top-level names and mtimes, including the operator directory name; that is a directory listing, not content access.

Limitation, stated exactly: I cannot prove the recursive traversal did not `stat` entries beneath `census/operator-sweep-20261019/`. No file under any `operator-sweep-*` path was opened, read, copied, staged, emitted or modified; no operator-sweep content appears in this report or in any command output used for it. Every later search/read was restricted to explicitly named files or to `tools/`, `tests/fixtures/`, `corpus/` and `.ufo/waves/round-15/` paths; no further lane-root or census-recursive query was issued after the reminder.

## 8. Unrun checks

None of the acceptance commands in §5 were run (wave prohibition, Q24). This report is source review of `tools/souji-census.sh` at `fcff8b05…` and of the committed r13/r14 fixtures; it contains no runtime observation of the repaired tool, which does not exist yet (`ConfigRepair` in flight).
