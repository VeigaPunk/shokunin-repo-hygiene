# SimplSizeVsStructure — YAGNI check for C1 (`tools/souji-size-census.py`)

## Status
STATUS: PASS. This is not a duplicate: the operations and outputs differ. Only the envelope overlaps (about 25 Python lines). Copy it inline, extract no shared module, and do not edit the r13 tool or fixture. The minimal manifest function is pasted below and was run in scratch.

## Evidence
Lane revision: HEAD `f9db2181647d91470a724a12d626bd6106805076` (base `a65fac9…`). git 2.56.0, Python 3.14.8. All probes ran under `/var/tmp/souji-r24-SimplSizeVsStructure/`, which was removed afterwards. These probes are design input, not C1 claim data.

- `wc -l tools/souji-repo-structure.sh tests/fixtures/r13-repo-structure.sh` returned `312` and `659`.
- `ls tools/souji-size-census.py` returned `No such file or directory` (absent at HEAD).
- `python3 -B probe.py` (the manifest function below, plus envelope probes) printed:
  ```
  stable_rerun True rows 41
  content_delta_seen True
  restore_equal True
  mtime_delta_seen True
  restore2_equal True
  atime_only_ignored True
  count_objects_stderr '' unchanged True
  fsck_unreach_rc 0 lines ['unreachable blob 4ba8ea60…', ''] stderr '' unchanged True lost_found False
  lost_found_rc 0 manifest_changed True other_oid True
  C_linked ['garbage: 1'] co_stderr 'warning: garbage found: …/.git/worktrees/linked/refs' unreachable_n 1
  gitdir_common ['garbage: 0'] co_stderr '' unreachable_n 1
  ```
  The linked case had a detached worktree HEAD on a commit that only that worktree references. Under both `-C <linked>` and `--git-dir=<common>`, fsck did not count that commit as unreachable.
- `python3 -B probe2.py` (all calls through `--git-dir=<common>`) printed:
  ```
  staged_only ['garbage: 0', 'size-garbage: 0'] unreach 0 fsck_err ''
  garbage_pack_junk ['garbage: 1', …] co_err 'warning: garbage found: …/objects/pack/junk' fsck_err ''
  garbage_loose_bad ['garbage: 1', …] co_err 'warning: garbage found: …/objects/12/zz' fsck_err 'bad sha1 file: …/objects/12/zz'
  alternates_existing [… 'alternate: …/altsrc/.git/objects'] co_err '' fsck_err ''
  alternates_missing ['garbage: 0', 'size-garbage: 0'] co_err 'error: unable to normalize alternate object path: …' fsck_err 'error: unable to normalize …'
  ```

## Findings
1. **Not a duplicate; keep a separate file.** `souji-repo-structure.sh` wraps `git repo structure --format=lines` (tools/souji-repo-structure.sh:271, `"${GIT[@]}" -C "$repo" repo structure --format=lines`). That gives refs-rooted reachable object counts and sizes. C1 needs debris figures (`garbage size_garbage unreachable alternates`) from `count-objects -v` and `fsck --unreachable`, which `repo structure` does not emit. Merging would also break the frozen Python CLI path (preregistration.txt:35, `python3 -B tools/souji-size-census.py --repo PATH`).
2. **Leave the r13 tool and fixture unchanged.** Their bytes are pinned by a knowledge recheck line and round-13 receipts: corpus/knowledge/git-repo-structure-readonly.md:3 `recheck: bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh`, and census/round-13/final-checks.md:20 pins sha256 `80025137…` / 312 lines. "Both fixtures could use" the manifest function only in the sense of the same field set. r13 is Bash and should keep its `manifest_all` (r13-repo-structure.sh:205-213).
3. **Copy, don't share.** The lane has no shared Python helper module, and Python tools inline their own guarded git environment: tools/souji-receipt-run.py:111-117 builds `env["GIT_NO_LAZY_FETCH"] = "1"` per call; tools/souji-landing-gate.py:184 `GIT_ENV["GIT_NO_LAZY_FETCH"] = "1"`. A new `souji_common.py` would add a second convention for one consumer. Copying the inline dict matches what the lane already does.
4. **Keep, merge or omit, per piece** (estimates are lines in the new Python tool and fixture):

   | Piece | Source | Verdict | Est. lines |
   |---|---|---|---|
   | Guarded env (`LC_ALL=C`, `GIT_OPTIONAL_LOCKS=0`, `GIT_NO_LAZY_FETCH=1`, `GIT_TERMINAL_PROMPT=0`, drop inherited `GIT_*`; `-c maintenance.auto=false -c maintenance.autoDetach=false`) | structure.sh:149-154,177 | KEEP (copy inline) | 8 |
   | Repo resolution: `rev-parse --path-format=absolute --absolute-git-dir` / `--git-common-dir`; failure gives exit 2 | structure.sh:180-193 | KEEP (copy) | 8 |
   | Promisor/partialClone refusal: `config --local --get extensions.partialClone` present gives exit 2; `--type=bool --get-regexp '^remote\..*\.promisor$'` any `true` gives exit 2; config read error gives exit 1 (contract), not r13's 4 | structure.sh:202-233 | KEEP (copy both markers) | 12 |
   | `--lost-found` refusal | prereg:38 | KEEP. It falls out of strict argv parsing: `argparse(allow_abbrev=False)` exits 2 on unknown argv. An explicit check is 1 line | 1-3 |
   | Capability check `repo structure -h` | structure.sh:236-247 | OMIT. `count-objects` and `fsck` are stable commands, not EXPERIMENTAL | 0 |
   | mktemp capture dir and EXIT trap | structure.sh:158-166,265-268 | OMIT. Use `subprocess.run(capture_output=True)`, which removes the tool's only filesystem write | 0 |
   | Bounded `probe.stderr=` echo | structure.sh:249-259 | REPLACE with contract passthrough: lines starting with `warning: garbage found:` become `census.warning=`; any other stderr gives exit 1 | 6 |
   | `probe.*` metadata block (12 keys) | structure.sh:297-311 | MERGE down to `census.git_version=`, `census.git_common_dir=`, then the `census.warning=` lines, with the counts line last | 4 |
   | count-objects parse (`garbage:`, `size-garbage:`, count of `alternate:` lines) on `--git-dir=<common>` | new | KEEP | 10 |
   | `fsck --unreachable --no-reflogs` count, same `--git-dir=<common>` (probe: same figure as `-C <linked>`; staged-only blob not counted) | new | KEEP; one resolution for both calls | 8 |
   | 95-line header comment | structure.sh:1-95 | OMIT the restatement. A docstring of about 12 lines should cite preregistration.txt C1 | 12 |
   | **Tool total** | | | **~70-80** (vs 312) |
   | Fixture: manifest function (below) | r13:205-213 semantics | KEEP (Python, same field set) | 19 |
   | Fixture: `env -i` allowlist around the measured run | r13:192-202 | KEEP (copy as a dict) | 10 |
   | Fixture: description-append/touch detector control | r13:321-374 | OMIT. Frozen case 7 (`fsck --lost-found` WRITE-DETECTED) is the detector, and no extra case id is allowed (C=8 frozen) | 0 |
   | Fixture: bogus/missing-path case | r13:490-541 | OMIT as a case (not in the frozen set). The tool still exits 2 per contract | 0 |
   | Fixture: id-set reconciliation loops | r13:617-659 | REPLACE with `cases/pass` tally per the frozen last line | 8 |
   | Fixture: 8 frozen cases, repo builders, case-8 stub | prereg:47-61 | KEEP | ~130 |
   | **Fixture total** | | | **~170-190** (vs 659) |

5. **Do not add these:**
   - Size attribution (largest objects or paths). `repo structure` already emits `max_size_oid` per type (r13-repo-structure.sh:445-452). README:68 keeps "wider size attribution remains frontier", and it is not in C1's counts line.
   - Per-pack listing (`count-objects` `packs/size-pack/in-pack/prune-packable`, `verify-pack -v`). It is not in the frozen counts line.
   - `prune --dry-run`, `--dangling`, `--lost-found` variants, or `--connectivity-only` tuning.
   - Linked-worktree enumeration. Resolving the common dir alone removes the false positive.
   - Multi-repo or fleet mode, JSON output, or cleanup suggestions. The preregistration says "It is a figure about this repo only; no fleet" (prereg:67).
   - A shared Python module.
   - Any edit to the r13 tool or fixture.
6. **Fixture hazard on case 5 (alternates).** If the alternates line names a path that does not exist, count-objects drops the `alternate:` line and both commands print `error: unable to normalize alternate object path` on stderr. The frozen any-other-stderr rule (prereg:40-41) then makes the tool exit 1. The case-5 builder must point at an existing `objects/` directory, as `alternates_existing` does in the probe. README:489 still requires alternates to be read: "`alternate` object databases must be read by any size figure (S115)."
7. **Fixture hazard on case 3 (garbage).** It must use the frozen `objects/pack` junk form. The loose-name form `objects/12/zz` (named in the design probe, prereg:18-19) makes fsck print `bad sha1 file:`, which gives the tool exit 1. Frozen case 3 already names `objects/pack`, so this is not an attack; it is a builder note.
8. **Residual (no attack).** Frozen case 6 tests only the partialClone repo. The tool's `remote.*.promisor=true` branch, which item 4 says to keep, is not exercised by the C1 counter. Mtime-only sensitivity of the manifest is also not witnessed by any frozen case (r13 witnessed it for the Bash field set). My scratch run witnessed it for this function (`mtime_delta_seen True`), but that run is design input, not claim data.

### Minimal manifest function (ran as pasted; scratch results above)
```python
import hashlib, os, stat
from pathlib import Path


def manifest(root: Path) -> list[tuple]:
    """Sorted (path, type, mode, size, mtime_ns, sha256-or-link-target) for root
    and every path under it; symlinks not followed; atime and ctime never read."""
    paths = [str(root)]
    for parent, dirs, files in os.walk(root):
        paths += [os.path.join(parent, n) for n in dirs + files]
    rows = []
    for path in paths:
        st = os.lstat(path)
        kind = stat.S_IFMT(st.st_mode)
        tail = ""
        if kind == stat.S_IFREG:
            with open(path, "rb") as fh:
                tail = hashlib.file_digest(fh, "sha256").hexdigest()
        elif kind == stat.S_IFLNK:
            tail = os.readlink(path)
        rows.append((os.path.relpath(path, root), kind, stat.S_IMODE(st.st_mode),
                     st.st_size, st.st_mtime_ns, tail))
    return sorted(rows)
```
Field parity with r13 `manifest_all`: `%y` maps to `kind`, `%m` to `S_IMODE`, `%s` to `st_size`, `%T@` to `st_mtime_ns`, `%p` to the relative path, `%l` to the link target, and `sha256sum` to `tail`. This meets the prereg:48-49 field list ("sorted path+type+mode+size+mtime+sha256 of regular files; atime/ctime excluded"). It needs Python 3.11 or later for `hashlib.file_digest`. Compare before/after with `manifest(gd) == manifest(gd)`; for case 7, report `set(after) - set(before)` if a diagnostic is wanted.

## Tooling
No installs or updates.
