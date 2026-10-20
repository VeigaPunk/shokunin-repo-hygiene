STATUS: DONE — Static review completed; no lane code or runtime checks were executed.

# Attacked claim

C3's independent `leak-count.py` counter agrees with `souji-proc-census.sh` about which current-UID processes retain deleted scratch paths.

# Findings (severity order)

## P2 — The counter's argv predicate is broader than the census tool's

`census/round-18/leak-count.py:21,53-64` scans each argument for any `/tmp`, `/var/tmp`, or `/dev/shm` substring, then accepts it when the first scratch component is missing. In contrast, `tools/souji-proc-census.sh:214-228` considers only an argument that starts with `/` or a `--*=/*` option whose value starts with `/`.

For example, if `/tmp/r18-missing-x/file` is absent, an argv item `--url=https://host/tmp/r18-missing-x/file` matches the Python regex (the `/tmp` is preceded by `t`, not `/`) and is counted as `argv-path-gone`; the shell case does not match because the option value starts with `https`, not `/`. Thus the purported independent counter can exceed the census on a process whose URL merely contains a scratch-looking path. This directly invalidates source-level exact parity for argv-path-gone.

**Smallest fix:** align the Python recognizer with the shell's accepted argument forms (or vice versa), and add a paired fixture for an embedded URL/path argument so both census results are asserted.

## P2 — A dangling top-level symlink is “gone” to the shell but present to Python

For argv/fd paths, Python `census/round-18/leak-count.py:37-49` tests the top-level entry with `os.path.lexists`. Shell `tools/souji-proc-census.sh:162-179` tests it with `[[ ! -e $TOP_LEVEL_PATH ]]`, which follows symlinks. Given a dangling symlink at `/tmp/r18-link` and candidate `/tmp/r18-link/child`, `lexists('/tmp/r18-link')` is true while Bash `-e` is false; if the candidate is also missing, the shell reports it as gone and Python rejects it. This is a concrete partial-delete edge where the two predicates differ.

**Smallest fix:** make the shell's top-level absence test distinguish a dangling symlink from an absent entry (for example, require both `! -e` and `! -L`) to match `lexists`; add this case to the paired counter/tool fixture.

## P2 — Deleted cwd paths bypass every scratch-prefix boundary in both implementations

Python `census/round-18/leak-count.py:101-120` returns `cwd-deleted` as soon as the cwd link ends in ` (deleted)`; failure to classify it under a configured scratch root only changes its family to `other` (lines 107-111). Shell `tools/souji-proc-census.sh:325-328` likewise sets `cwd-deleted` solely from the suffix, without calling `top_level_scratch_gone` or checking `PREFIXES`. Therefore a deleted cwd such as `/home/job (deleted)` or `/tmpfoo/job (deleted)` is counted by both, including when `--prefix` names a different tree. This is a shared scope defect if the documented “scratch-path prefix to inspect” (`souji-proc-census.sh:22-25`) is intended to constrain cwd paths as well. It also means the `/tmpfoo` boundary protection does not apply to cwd classification.

**Smallest fix:** if cwd is meant to be restricted to scratch roots, strip the suffix and require a component-boundary prefix match before assigning `cwd-deleted` in both implementations. Otherwise document explicitly that deleted cwd is global and exempt from `--prefix`.

# Checked edge cases and residual coverage

- **S5 / partial deletion:** For a deleted nested path while its top-level scratch entry still exists, both predicates omit the process: Python rejects when `lexists(prefix/top_level)` is true (`leak-count.py:37-49`); shell rejects when `-e TOP_LEVEL_PATH` is true (`souji-proc-census.sh:162-179`). This agrees with the explicit P10 fixture expectation (“deleted /var/tmp/<top>/sub while <top> lives -> absent”, `tests/fixtures/r18-proc-census.sh:14,471-472`). The dangling-symlink case above is the exception to this agreement.
- **`/tmpfoo`:** argv/fd checks correctly enforce the component boundary in both tools: Python requires `path.startswith(prefix + "/")` (`leak-count.py:37-45`); shell uses exact-prefix-or-prefix-plus-slash matching (`souji-proc-census.sh:154-160`). The Python selftest checks `/tmpfoo` at `leak-count.py:187-189`. This does not protect the unfiltered cwd branch described above.
- **Coverage gap:** the counter's selftest checks the `/tmpfoo` helper case and a FIFO/argv-path case (`leak-count.py:187-216`); the P10 partial-delete case is in the shell fixture only. There is no paired test of the counter and tool for embedded argv text, dangling top-level symlinks, or cwd outside a prefix. Source review shows the first two are divergent already.

# Verdict and verification gaps

**Verdict: FAIL for exact independent-counter parity.** The accepted argv languages differ, and the dangling-symlink absence tests differ. Both count deleted cwd outside scratch prefixes, which is either a shared false positive or an undocumented exception to prefix scoping. P10 partial-delete and argv/fd `/tmpfoo` behavior agree for ordinary directories/paths.

Read-only comparison performed:

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --no-ext-diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- census/round-18/leak-count.py tools/souji-proc-census.sh
```

Output: `2 files changed, 761 insertions(+), 0 deletions(-)`; both target files are additions in this range. No executable check was authorized or run, so runtime counts remain unverified here. LSP status was attempted first, but `xd://lsp` is not mounted (`No such tool: xd://lsp`); findings therefore rely on literal source inspection, not LSP semantic analysis. No tools were installed.
