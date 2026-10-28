# R40w2sentinel01 — C1 counter hostile-input review

Target: committed `census/round-40/c1-counter.py` at `128e412b0ced3c243dc27c3dd3332054a611bc2e`. Frozen predicate read from `census/round-40/preregistration.txt` lines 4–5. No packages installed.

## Verdict: SAFE (for the requested command construction, path-write, symlink, and inherited Git-environment attack surfaces)

The hostile cases below found no path in attacker-controlled register/items content that becomes an output path or an executed program. Git subprocesses are invoked as argument arrays, with fixed `git` command and `-C root`, and an explicit environment allowlist. The sole extracted executable is the reconciler source from the audited repository revision, written to a generated filename in the private scratch directory and run via fixed `python3`; register/item content is not executed.

### Source locations attacked

- `census/round-40/c1-counter.py:67-80`: `child_env()` constructs a fresh environment; Git command uses argv list and explicit `env`.
- `:83-96`: Git show/cat-file/merge-base arguments; evidence path is passed as a `git show REV:path` argument, not opened as a filesystem path.
- `:119-155`: items file parsed as TSV; evidence string split into path/revision, but filesystem-open only occurs on CLI items/forged arguments.
- `:158-176`: register TSV data parsed into strings.
- `:179-204`: repository-derived reconciler source written to `scratch/citation-reconcile.py`, then fixed `python3` command; child gets only PATH and TMPDIR.
- `:263-299`: validates root/revisions, reads CLI paths, creates scratch under supplied scratch root (or TMPDIR/default).
- `:328-329`: removes generated scratch tree.

### Exact commands and observed output

1. Confirmed the landed revision and inspected the command entrypoint:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat 128e412b0ced3c243dc27c3dd3332054a611bc2e
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c1-counter.py --help
```

Output included the exact commit `128e412b0ced3c243dc27c3dd3332054a611bc2e` and usage showing required `--root`, `--rev`, `--items`, `--register`, optional `--forged`, `--register-rev`, and `--scratch`. Both commands exited 0.

2. Scratch fixture extraction and root assertion:

```sh
S=/fast/scratch/hyaku/souji-r40/w2/R40w2sentinel01
mkdir -p "$S"
git -C /home/vgpnk/Projects/shokunin/souji-shokunin archive 128e412b0ced3c243dc27c3dd3332054a611bc2e | tar -x -C "$S"
git -C "$S" init -q
git -C "$S" config user.name x
git -C "$S" config user.email x@x
printf 'top='; git -C "$S" rev-parse --show-toplevel
printf 'status='; git -C "$S" status --short
```

Observed: `top=/fast/scratch/hyaku/souji-r40/w2/R40w2sentinel01`; `status` listed the extracted archive contents as untracked. This fixture was not committed. Exit 0.

3. Counted subprocess run sites in the exact counter source:

```sh
python3 -B -c 'import ast,pathlib; p=pathlib.Path("/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c1-counter.py"); t=ast.parse(p.read_text()); print("subprocess.run calls",sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="run" for n in ast.walk(t)))'
```

Output: `subprocess.run calls 2`; exit 0. Both sites were examined above: the Git helper and the reconciler launch.

### Attack outcomes

- **Path traversal / arbitrary write via register or items fields:** not reachable in inspected code. `items` and `forged` are opened only as the CLI-specified input filenames (`:281-289`); register is read from the Git tree (`:184-187`). Attacker-supplied `file`/`evidence_path` values only flow into Git argv (`:237`, `:256`), not local open/write. The only local write uses generated `citation-reconcile.py` beneath the private `mkdtemp` path (`:188-190`).
- **Symlink following:** no register/item value is used as a local path. Scratch is created by `tempfile.mkdtemp` (`:296-298`), yielding a newly created directory, and the output child name is fixed (`:188`). Input symlinks supplied as CLI filenames are followed by ordinary `open`; that behavior is caller-controlled CLI path handling, not a crafted record path. No content-driven symlink traversal found.
- **Inherited `GIT_TRACE*` / `GIT_CONFIG_*`:** excluded from the `git` subprocess environment because `child_env()` starts with only PATH then adds the fixed `GIT_ENV` keys (`:67-70`, `:78`). Reconciler child likewise receives only PATH and TMPDIR (`:203`).
- **Execution from audited tree:** the reconciler source is explicitly extracted from `--rev` (`:181-190`) and is executable Python by design, invoked with fixed `python3` (`:191-204`). That is trusted instrument code, not register/items content. No user-provided command/path is interpolated as an executable.

The scratch directory was removed by the command's `trap 'rm -rf -- "$S"' EXIT`.
