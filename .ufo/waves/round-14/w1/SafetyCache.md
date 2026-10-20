# SafetyCache — C1 gate path containment and symlink TOCTOU (sentinel, r14 w1)

Seat: `SoujiR14.SafetyCache` (sentinel). Axes judged: calibration, operability.
Scope: the containment and symlink/TOCTOU behaviour of
`/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-evidence-cache.py`, and the
isolation of `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-evidence-cache.py`.
This seat edited no lane files; the only file it wrote is this report. Schema, exit-code and
stale-green questions belong to CacheReviewSchema, CacheAttack and FixtureCacheAudit.

Bytes reviewed (final snapshot, `sha256sum` at review end):
- gate `f8f541f79d6b61736b9a4b61395757f6902fe52226273c07250b1597fce05972`
- fixture `95b371ab667a61aebb673b003dda87ed2ade40d286706fa2bdf5785522b6d26a`

These revisions came after my findings. Between them they add the R4 stores, the R3
non-guarantee, and the R1/R2 fixes. I re-checked them by grep and re-read:
- the containment functions are unchanged;
- `copytree(..., symlinks=True)` is at fixture `:322` and `:330`;
- the HOME setup now sits inside `try` in both the gate selftest (`:1299-1300`) and the
  fixture (`:159-160`).

Line numbers in the table refer to revision `dc60c14b…`, which I read in full. Later edits
shifted them by about +17.

If L1 measures bytes other than these, treat the "fixed" statuses below as `to-verify`.

## Evidence kinds (kept separate)

**Code inspection only. Nothing in this section was run.** All findings and fix confirmations
below come from reading the gate source three times as it changed: the first draft,
the version with the fd walk, and the final version. They also draw on the existing
precedent `tools/souji-cert-evidence.py:273-375`. I did not run the gate, its `--selftest`,
or the fixture.

**Exercised. These are the only commands this seat ran:**
1. A kernel-semantics probe in `tempfile.mkdtemp(dir="/var/tmp")`, removed afterwards
   (printed `cleaned True`). On Linux 7.2.3 with Python 3.14.7, opening a symlink-to-directory
   with `O_RDONLY|O_DIRECTORY|O_NOFOLLOW` via `dir_fd` fails with **`ENOTDIR`**.
   Opening it with `O_RDONLY|O_NOFOLLOW|O_NONBLOCK` fails with **`ELOOP`**. This is the basis for M3.
2. Vendor docs read locally (`man-pages 6.19-1`):
   - `open(2)` O_NOFOLLOW: "If the trailing component … is a symbolic link, then the open
     fails, with the error ELOOP. Symbolic links in earlier components of the pathname will
     still be followed."
   - `openat2(2)` RESOLVE_NO_SYMLINKS: it "differs from the effect of the O_NOFOLLOW …
     which affects the handling of symbolic links only in the final component".
3. `findmnt -T` / `stat -c %d`. The lane and `tools/` are btrfs `@home` with st_dev 57 throughout.
   `/var/tmp` is btrfs `@` with st_dev 31. So the gate's same-device rule does not
   falsely refuse files inside the lane or inside a single `/var/tmp` fixture root.
   `/home` and `/home/vgpnk` are real directories, not symlinks.
4. `python3 -c` capability check: `os.open` and `os.stat` support `dir_fd`, and `os.stat`
   supports `follow_symlinks`.
5. `ls`/`find -type l` on the committed `tests/fixtures/r14-cache-frozen/`. It holds three
   regular files and no symlinks.

Not accessed: `~/.omp/agent/` (only `RULES.md` and skills were read), any credential store,
`census/operator-sweep-*`. No GUI, no `/dev/shm`. No tools were installed or upgraded, because
`python3`, `man-pages` and `findmnt` were already present.

**Process deviation (recorded at L1's request).** Exercised item 1, the kernel symlink-open
probe, was an empirical check run mid-flight. The round's no-tests/no-smoke-run contract
prohibited it, even though it was synthetic, isolated under `/var/tmp`, cleaned up, and did
not touch the gate, the fixture, or any real store. I keep the observation (`ENOTDIR` vs
`ELOOP`) as recorded single-seat evidence for M3. Main will not rerun it, so treat it as
unconfirmed by L1. This seat ran no further probes after this note. The final run of the
owned fixtures (selftest and `tests/fixtures/r14-evidence-cache.py`) is a separate acceptance
requirement. It is not replaced by this probe. The real credential store was not accessed.

## Findings and status

Every finding below was sent to CacheGate as a peer message during the wave.

| id | sev | exploit path | evidence | impact | smallest remediation | status (inspection) |
|---|---|---|---|---|---|---|
| H1 | high (draft) | First draft: lstat-walk, then `os.open(full path, O_NOFOLLOW)`. An ancestor directory swapped for a symlink between the walk and the open sends the read outside `--root`. | draft `_open_dependency` (lstat loop, then path open). The draft's own docstring admitted "not a parent-directory swap". `open(2)` quote above. | Out-of-root bytes get hashed, and their digest is printed on mismatch. | fd walk: `os.open(part, O_DIRECTORY\|O_NOFOLLOW\|O_CLOEXEC, dir_fd=cur)` per component | **fixed**: `_open_dir_beneath` / `_open_dir_component` / `_open_leaf_checked` (`:545-660`) |
| H2 | high (draft, frozen) | First draft `--frozen`: `_digest_regular(root / rel)` lstat'd only the leaf, so a pinned `sub/x` where `sub` is a symlink to a store was followed. This contradicted the draft docstring ("through non-symlink components"). | draft `evaluate_frozen` and `_digest_regular` | A tampered snapshot dir could read a store through its pins. | Route pins, `expected.json` and the record through the dependency fd walk | **fixed**: `_open_regular_beneath` at `:1092`, `:1123`, `:1143` |
| H3 | high (draft) | `--root ~` or `--root /` plus a dependency key under a store missing from the name list (`.local/share/keyrings/…`, `.pgpass`, `.npmrc`). `--record` was read from any path with no protected check. | draft `_resolve_root` (realpath plus name patterns only), draft `_record_text` | Credential bytes read and hashed. | Lexical tree check (equal / inside / **ancestor**) on `--root`, `--frozen` and the `--record` path before any access | **fixed**: `_tree_reason`, `_protected_trees`, `_resolve_boundary` (`:380-490`); `record-protected` |
| M1 | medium (calibration) | The synthetic HOME was created but no case used it. The tree, ancestor and alias logic was never exercised: `root-protected` and `record-protected` passed only through the `.ssh` name pattern. | selftest before revision | The C1 boundary claim had no discriminating falsifier. | Cases `--root <HOME>`, `--root base/home-alias/sub`, and `--record base/config-alias/rec.json` | **fixed**: `home-root-protected`, `home-alias-root-protected`, `home-alias-record-protected` (`:1516-1534`) |
| M2 | medium (contract) | `_resolve_root` ran `os.lstat(value)` **before** the boundary check, so `--root ~/.omp/agent` would stat a protected path. The docstring claimed "before any filesystem access". | previous `_resolve_root` | A metadata query inside the protected tree. The falsifier `--root <HOME>/.ssh/absent` gave `root-not-directory` instead of `root-protected`. | Run the lexical and name checks, then the walk, then `lstat` | **fixed**: `_resolve_root` `:770-803` |
| M3 | medium (id calibration) | An ancestor-symlink dependency (`linkdir/a.txt`) hits `ENOTDIR` (exercised probe #1). It was mapped to `path-not-directory`, not `path-symlink`. It still exits 2, but the finding id was wrong. The ancestor-swap case was the reason for the fd walk, and it was untested. | probe #1; previous `_errno_reason` mapping | A false finding id. | On `ENOTDIR`, run `os.stat(part, dir_fd, follow_symlinks=False)`; if `S_ISLNK`, report `symlink`. Add a selftest case. | **fixed**: `_open_dir_component` `:545-560`; `symlink-ancestor` case `:1353-1362` |
| L1 | low | Root and record were reopened by path after the walk. An ancestor swap in that window followed a symlink. | previous `os.open(resolved, O_DIRECTORY\|O_NOFOLLOW)` | A narrow race. It needs a hostile writer in an ancestor of the root. | Per-component `O_NOFOLLOW` walk from `/` | **fixed**: `_open_no_symlink` `:602-621`, used at `:720` and `:803` |
| L2 | low | Raw `%s` of readlink targets and candidate paths. A newline in a symlink target could forge `finding …` or status lines. `name` allowed U+0085 and U+2028. | previous `_walk_boundary`, `_validate_record` | Spoofed stdout lines on refusal paths. The exit code stays 2, but consumers that grep for substrings could be misled. | `%r` in details; `name.isprintable()` | **fixed**: `:447-471`, `:844` |
| L3 | low | The leaf was opened before any type check, so a FIFO or device leaf was `open()`ed and only then refused. | previous `_open_leaf_beneath` | Open side effects only. Reads are already refused. | Pre-check with `os.stat(leaf, dir_fd, follow_symlinks=False)` for `S_ISREG`; add `O_NOCTTY` | **fixed**: `_open_leaf_checked` `:563-582` |
| R1 | low (fixture) | `shutil.copytree(frozen, …)` followed symlinks by default. A caller-supplied `--frozen-dir` containing a symlink would make the **fixture itself** copy out-of-tree bytes before the gate can refuse them. | fixture `:322`, `:330` | The fixture reads outside the tree. The committed snapshot has no symlinks (exercised #5). | `shutil.copytree(frozen, dst, symlinks=True)` | **fixed** in fixture `95b371ab` (`:322`, `:330`) |
| R2 | low (operability) | `home/.ssh` and its siblings were created **before** `try/finally` in both the selftest and the fixture. | source | An early `OSError` leaves the `/var/tmp` base behind (QUALITY Q4 cleanup). | Move the HOME setup inside `try` | **fixed**: gate `f8f541f7` `:1299-1300`, fixture `95b371ab` `:159-160` |
| R3 | low (bounded) | Protected trees are lexical, built from `$HOME`, the passwd home, `/root` and `PI_*`. A store relocated by symlink (for example `~/.config` pointing to `/data/cfg`) is covered only by name patterns at its canonical location. | `_protected_trees` | Possible store read if an operator relocates a store. On this host `/home` and `/home/vgpnk` are real dirs (exercised #3). The store entries themselves were not inspected, by contract. | Document it as a non-guarantee, or `readlink` the store entry names in HOME without traversing them | **documented** as a non-guarantee in `b4b50d00` (docstring `:244-246`); the behaviour is unchanged, which is acceptable as bounded |
| R4 | low (bounded) | The first denylist omitted `~/.mozilla`, `~/.thunderbird`, `~/.pki`, `~/.var/app` and `~/.local/share/kwalletd`. A root inside one of them reads files that don't match a pattern. Digests are printed only on mismatch, which works as an oracle only if the attacker guesses the full content. | `PROTECTED_ABSOLUTE`, name patterns | A credential-adjacent read through operator error. | Extend the list, or allowlist roots under HOME (for example `~/Projects`) | **fixed** in `b4b50d00`: added to `PROTECTED_ABSOLUTE` (`:309-310`) and `PROTECTED_DIRS` (`:288-289`). The list is still a denylist, by design. |

Non-guarantees the gate states, in its own words. I checked that these are present and accurate
by inspection:
- The verdict is point-in-time; no lock is held.
- Path validation and output emission are not atomic.
- `--require` sets only the caller's floor.
- Bind mounts are refused for dependencies through the `st_dev` check. A root that is itself
  inside a privileged bind mount of a store is not detected. That requires privilege, so it is
  outside the "no hostile execution" threat model.

I confirmed by inspection that the CLI evaluation path (outside `--selftest`) has no mutating
call. Every `write_text`, `mkdir`, `unlink`, `symlink` and `rmtree` sits in the selftest section
(`_write_text` at `:1232` and later in `f8f541f7`; re-grepped lines 1-1280 for
`O_WRONLY|O_RDWR|O_CREAT|unlink|remove|rename|rmtree|write_text|mkdir|symlink|link`: no hit
before `:1232`). So every rejection mutates nothing: an evaluation only opens files
`O_RDONLY`.

## Verdict for this slice

By inspection, containment and symlink TOCTOU handling are acceptable for the round-14 threat
model ("no hostile execution expected, still reject known escapes"). All high- and medium-severity
items found in this review were fixed in the final bytes. Of the low-severity items, R1, R2 and R4
are fixed, and R3 is documented as a bounded non-guarantee. Nothing found by this seat remains open
that blocks C1. CacheGate also reports (I have not checked this) that it reworded the
root/record race limit: a directory rename or mount swap is not fd-bound. This is not a certification:
certification is OFF, and these fixes are not confirmed by any run until L1 executes the
commands below.

## Commands for L1 (this seat did not run them)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
sha256sum tools/souji-evidence-cache.py tests/fixtures/r14-evidence-cache.py   # compare to digests above
python3 tools/souji-evidence-cache.py --selftest                                # expect exit 0; symlink-ancestor, home-root-protected, home-alias-root-protected, home-alias-record-protected all pass
python3 tests/fixtures/r14-evidence-cache.py --tool tools/souji-evidence-cache.py   # expect exit 0
python3 tests/fixtures/r14-evidence-cache.py --tool /var/tmp/absent-tool.py         # expect exit 2 "tool missing" (baseline discrimination)
ls -d /var/tmp/souji-r14-cache-selftest.* /var/tmp/souji-r14-cache-fixture.* 2>/dev/null | wc -l   # expect 0 residue
```
