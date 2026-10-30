# S44reviewer66 — C3 inherited-diff review

Axes: calibration / operability / coverage (assigned axis: coverage).
Recommendation: repair the concrete error-path regression below before closure. This is review advice, not admission; certification and numeric deltas are not claimed.

## Findings, severity first

### P2 — new leaf lstat leaks ordinary path errors as traceback / exit 1

`tools/souji-worktree-drift.py:326-332` introduces `os.lstat(json_path)` but catches only `FileNotFoundError`. An output whose parent is a regular file raises `NotADirectoryError`; a looping symlink parent raises `OSError(ELOOP)`. Neither is caught by `main` (`:462-466`, catches only Refusal). Previously both reached the existing writer error translation (`:431-447`) and returned `REFUSAL JSON-UNWRITABLE`, exit 2. Now they exit 1 with a Python traceback and no SUMMARY. Exit 1 is also the normal drift result (`:448`), so this changes the caller-visible classification, not merely cosmetic diagnostics.

Observed against exact base `55d7af6f5a22340f7a3de1c386e514ababfaa75f` and frozen `d314fd6e85d62565344fa6c4b102f52f62297884` blobs:

| --json shape | base | frozen |
|---|---|---|
| regular-file parent / out.json | rc=2; REFUSAL JSON-UNWRITABLE: [Errno 20] | rc=1; traceback at line 328, NotADirectoryError |
| self-loop symlink parent / out.json | rc=2; REFUSAL JSON-UNWRITABLE | rc=1; traceback at line 328, OSError [Errno 40] |

Fix recommendation: preserve missing-leaf handling, translate other lstat OSErrors into the existing JSON-UNWRITABLE refusal contract; add the two bounded error cases to the governed battery. Do not silently treat errors as an absent leaf.

## Changed semantic statements and guard review

Read-only diff command:

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff 55d7af6f5a22340f7a3de1c386e514ababfaa75f d314fd6e85d62565344fa6c4b102f52f62297884 -- tools/souji-worktree-drift.py tests/fixtures/r38-drift-write-envelope.py
```

Full output: `inherited.diff` beside this report. Overall round diff: 14 files, 1347 insertions, 14 deletions; tool 14 changed lines and legacy fixture 35 changed lines. No broad source rewrite in the two assigned files.

* Tool adds documented JSON-TARGET-SYMLINK class and pre-realpath leaf lstat. Existing and dangling leaf symlinks now refuse before drift reporting or JSON output. Parent resolution is retained. Existing record-alias, containment, fd-level regular-file/hardlink checks, O_NOFOLLOW walk, nonblocking open, and delayed truncation remain unchanged.
* r38 fixture replaces only the leaf-symlink expectation: renamed `json-symlink-resolved` to `json-symlink-refused`, requires rc 2 and whole-token refusal, requires dangling target absent and original link retained (`tests/fixtures/r38-drift-write-envelope.py:242-256`). It adds that case to the behavioral base-failure classification (`:315-318`) and updates explanatory documentation. The other case assertions are unchanged.
* Observed bounded probes: existing/dangling/directory-target links all produce the new refusal; existing victim bytes remain `keep\n`, dangling target stays absent, link remains a link, record remains identical. Base follows existing/dangling leaf links and writes JSON, demonstrating intended discrimination. Regular output and symlink-parent output still return normal drift rc 1 with SUMMARY in both revisions. These probes use one intentionally absent recorded repo, not a healthy repository, and perform no git mutations.
* Canonical implementation remains `run` -> `open_nofollow`; no second runtime, rerouting, resume path, saturation claim, or deletion authorization is introduced by this diff.

## Commands, receipts, and limitations

Bounded driver:

```
mkdir -p /fast/scratch/hyaku/souji-r44/S44reviewer66
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer66/probe.py
```

`probe.py` preserves the exact blob extraction and 14 subprocess invocations; `probe-output.txt` preserves every exact argv, stdout, stderr, return code, and final victim/record state. Driver completed rc 0; that means collection completed, not that the reviewed tool passed. Initial empty-record setup hit RECORD-EMPTY in all cases; corrected to a valid one-row record before the reported run. No production changes, fixture git writes, or whole-suite execution occurred.

Read preregistration and frozen C3 counter, including legacy/base and battery controls. Observed SHA256:

```
eba3e69ffef1493f4733c5c5537b8b2e5ed0a4cdcbaf551f560e03e8bcc64d66  census/round-44/c3-counter.py
efd4919ed58cfd7692ee14c074041ac1aab76810cecad3592cfc0476415f03df  census/round-44/c3-surface.tsv
```

They match preregistration. Counter and prior suites were not executed; no prior=5/5 or aggregate target claim is made. r38 fixture reviewed statically rather than rerun. Permission-denied and concurrent path-replacement cases were not probed; no race-proof refusal claim is made for lstat-before-realpath. Existing later O_NOFOLLOW protection was inspected, not stress-tested.

LSP unavailable: `read xd://lsp` returned `No such tool: xd://lsp` (device not mounted). References/callers were checked with literal scoped text search and direct source review only; no semantic references/definition/diagnostics proof claimed. No tools installed or upgraded. Seat scratch removed before submission; durable receipts retained only in seat output.

Self-evaluation: accuracy 4/5 (exact differential receipts, no race test); completeness 4/5 (assigned changed statements and guard covered, fixture execution intentionally omitted); clarity 4/5 (finding and evidence separated); actionability 5/5 (specific error translation and regression cases); conciseness 4/5 (full argv output kept separately). Overall 4.2/5. Highest-impact next action is the P2 fix, then its bounded error-path tests. User agreement expected on observed evidence; not an admission judgment.
