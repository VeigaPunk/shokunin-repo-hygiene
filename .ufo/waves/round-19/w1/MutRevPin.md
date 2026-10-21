STATUS: PARTIAL — M1 and M2 were applied privately and restored exactly; the proposed fixture is contract-blocked, so both mutation verdicts are inconclusive.

# Findings

Axis: **operability**. Scope: item MutRevPin, round 19 wave 1 only. Date: 2026-10-21. This is a mutation probe, not a judgment or admission of C2.

1. **The requested full behavioral measurement conflicts with the binding seat contract.** The proposed fixture creates its sandbox with Git mutations: `tests/fixtures/r19-rev-pin.py:76-106` runs `init`, `add`, `commit`, `checkout` and `update-ref`. The contract forbids Git/JJ mutations anywhere, including private scratch. I did not execute any such operation. A guarded attempt stopped before `git init` was spawned. The fixture also hard-codes `/var/tmp` at `tests/fixtures/r19-rev-pin.py:143`, outside this seat's required private root; the guard redirects only the runtime temporary-directory allocation into the authorized root.
2. **M1: include `refs/jj/*` as durable roots.** The one-line mutation extends `DURABLE_NAMESPACES` at `tools/souji-rev-pin.py:33` with `refs/jj`. Expected detector: `keep-only-refuse` at `tests/fixtures/r19-rev-pin.py:166`, which requires exit 2 and `not reachable`. Actual: the fixture stopped during sandbox setup, before that case. **Verdict: inconclusive**, not killed and not survived.
3. **M2: drop the tracked-tree comparison.** The private mutation deletes `tools/souji-rev-pin.py:136-146`; path validation and the final return remain. Expected detector: `dirty-tree-refuse` at `tests/fixtures/r19-rev-pin.py:167`, which requires exit 2 and `differ from`. Actual: the same setup guard stopped the fixture before that case. **Verdict: inconclusive**, not killed and not survived.
4. **[INFERENCE, not a measured kill] M1's proposed detector distinguishes the refusal reason rather than necessarily proving illicit acceptance.** The sandbox's keep-only commit has `tool.sh` ending in `# keep-only`, while the working tree at `second` ends in `# second` (`tests/fixtures/r19-rev-pin.py:98-106`). If M1 permits the keep ref, the unchanged tracked-tree check can still refuse those different bytes. The case's `not reachable` assertion (`tests/fixtures/r19-rev-pin.py:175-179`) should then fail even though exit 2 remains. No dynamic acceptance/rejection result is claimed here.

The missing prerequisite for a full killed/survived result is a contract-compatible prebuilt synthetic sandbox, or an explicit revision of the no-Git-mutations-anywhere restriction. Neither was available to this seat. No expectations were weakened and no synthetic Git-response mock was substituted.

# Evidence

## Bytes probed and restoration

Both inputs were **worktree bytes**, not `git show 3ab2c81` bytes. The C2 obligation is `.ufo/waves/round-19/preregistration.txt:33-49`; the helper gates are `tools/souji-rev-pin.py:99-147`; the behavioral stimuli and oracle are `tests/fixtures/r19-rev-pin.py:164-193`.

Private root: `/var/tmp/souji-r19-MutRevPin-2/`. Only copies of `tools/souji-rev-pin.py` and `tests/fixtures/r19-rev-pin.py` were written there. No lane source was edited.

| State | Helper SHA-256 |
|---|---|
| Lane input / pristine private copy | `d00a947bbf457b4bd79e338f8c0aecc3407e5574c945bf2ec32ff2c157aebe40` |
| M1 | `581653faa04ac36f1bce5c607580791027229f5b04c88ae7a83c4e08086a8b6c` |
| Restored after M1 | `d00a947bbf457b4bd79e338f8c0aecc3407e5574c945bf2ec32ff2c157aebe40` |
| M2 | `351c45264a7991ebfdb502f4c2c4946c4761df8696598e8cd4c3152c45090de0` |
| Restored after M2 | `d00a947bbf457b4bd79e338f8c0aecc3407e5574c945bf2ec32ff2c157aebe40` |
| Lane helper at end | `d00a947bbf457b4bd79e338f8c0aecc3407e5574c945bf2ec32ff2c157aebe40` |

The fixture SHA-256 was unchanged throughout: `d87dc6e854d4edd0647ac483317a81df4fd5b78ca2d0d0dac8777fd70f9596df` (8,882 bytes). The helper input/restored size was 11,549 bytes. Final `cmp` of each restored private file against its lane input returned 0. Each mutation was restored in a `finally` block even though the detector failed.

The raw reader omitted the terminal LF; adding the single LF reproduced the independently measured SHA-256 of both input files before any copy was written. This tool behavior was reported to `xd://report_issue`; it did not change either source file.

## Exact requested stimuli and detector expectations

These are the fixture's planned stimuli, **not executed case results**:

- `clean`: commit containing `tool.sh = "#!/bin/sh\ntrue\n"` and `record.json = "{}\n"`.
- `keep_only`: detached child of `clean` appending `# keep-only\n`, retained at `refs/jj/keep/keep-only` only.
- `second`: durable `master` child of `clean` appending `# second\n` instead; sandbox worktree initially equals this commit.
- M1 target invocation: `python <private-helper> --root <sandbox> --rev <keep_only-full-40-hex> --path tool.sh`; expect exit 2 with `not reachable`.
- M2 target invocation: append `# dirty\n` to tracked `tool.sh`, then `python <private-helper> --root <sandbox> --rev <second-full-40-hex> --path tool.sh`; expect exit 2 with `differ from`.
- The fixture's positive controls are durable-clean acceptance and historical acceptance with `--no-tree-check` (`tests/fixtures/r19-rev-pin.py:165,172-173`). No real synthetic commit IDs were generated, because setup was blocked before initialization.

## Actual bounded detector attempts

The exact same guarded detector was used for pristine, M1, restored-after-M1, M2 and restored-after-M2. Python: `3.14.8`; executable: `/usr/bin/python`. Per-attempt process deadline: 30 seconds; all returned normally to the driver without a timeout or signal.

The unchanged fixture was loaded with `runpy`; only temporary-directory placement and a pre-spawn policy hook were added by the driver. This is **not** a claim that the canonical unguarded fixture completed. The helper CLI was never reached. All five attempts exited 1 with empty stdout, no `CASE` rows and no `SUMMARY`. A failing pristine arm makes both mutant outcomes inconclusive.

| Arm | Driver exit | Stdout | Behavioral cases reached | Verdict |
|---|---:|---|---:|---|
| Pristine | 1 | empty | 0 | setup blocked |
| M1 | 1 | empty | 0 | inconclusive |
| Restored after M1 | 1 | empty | 0 | same setup block |
| M2 | 1 | empty | 0 | inconclusive |
| Restored after M2 | 1 | empty | 0 | same setup block |

Full captured stderr for each attempt follows. Stdout was the empty string for each.

### pristine

```text
Traceback (most recent call last):
  File "<string>", line 22, in <module>
    raise SystemExit(namespace['main'](['--tool', helper, '--tool-dir', lane]))
                     ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/tmp/souji-r19-MutRevPin-2/tests/fixtures/r19-rev-pin.py", line 149, in main
    repo, clean, keep_only, second = build_sandbox(top)
                                     ~~~~~~~~~~~~~^^^^^
  File "/var/tmp/souji-r19-MutRevPin-2/tests/fixtures/r19-rev-pin.py", line 92, in build_sandbox
    subprocess.run(["git", "init", "-q", "-b", "master", repo], check=True,
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                   env=ENV, capture_output=True)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 555, in run
    with Popen(*popenargs, **kwargs) as process:
         ~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 1039, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        pass_fds, cwd, env,
                        ^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
                        gid, gids, uid, umask,
                        ^^^^^^^^^^^^^^^^^^^^^^
                        start_new_session, process_group)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 1858, in _execute_child
    sys.audit("subprocess.Popen", executable, args, cwd, env)
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 19, in policy
    raise PermissionError('seat contract forbids git mutation: ' + ' '.join(map(str, argv)))
PermissionError: seat contract forbids git mutation: git init -q -b master /var/tmp/souji-r19-MutRevPin-2/souji-r19-rev-pin.hjztg8t_/sandbox
```

### M1 include refs/jj

```text
Traceback (most recent call last):
  File "<string>", line 22, in <module>
    raise SystemExit(namespace['main'](['--tool', helper, '--tool-dir', lane]))
                     ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/tmp/souji-r19-MutRevPin-2/tests/fixtures/r19-rev-pin.py", line 149, in main
    repo, clean, keep_only, second = build_sandbox(top)
                                     ~~~~~~~~~~~~~^^^^^
  File "/var/tmp/souji-r19-MutRevPin-2/tests/fixtures/r19-rev-pin.py", line 92, in build_sandbox
    subprocess.run(["git", "init", "-q", "-b", "master", repo], check=True,
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                   env=ENV, capture_output=True)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 555, in run
    with Popen(*popenargs, **kwargs) as process:
         ~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 1039, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        pass_fds, cwd, env,
                        ^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
                        gid, gids, uid, umask,
                        ^^^^^^^^^^^^^^^^^^^^^^
                        start_new_session, process_group)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 1858, in _execute_child
    sys.audit("subprocess.Popen", executable, args, cwd, env)
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 19, in policy
    raise PermissionError('seat contract forbids git mutation: ' + ' '.join(map(str, argv)))
PermissionError: seat contract forbids git mutation: git init -q -b master /var/tmp/souji-r19-MutRevPin-2/souji-r19-rev-pin.xh7ub7f4/sandbox
```

### restored after M1

```text
Traceback (most recent call last):
  File "<string>", line 22, in <module>
    raise SystemExit(namespace['main'](['--tool', helper, '--tool-dir', lane]))
                     ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/tmp/souji-r19-MutRevPin-2/tests/fixtures/r19-rev-pin.py", line 149, in main
    repo, clean, keep_only, second = build_sandbox(top)
                                     ~~~~~~~~~~~~~^^^^^
  File "/var/tmp/souji-r19-MutRevPin-2/tests/fixtures/r19-rev-pin.py", line 92, in build_sandbox
    subprocess.run(["git", "init", "-q", "-b", "master", repo], check=True,
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                   env=ENV, capture_output=True)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 555, in run
    with Popen(*popenargs, **kwargs) as process:
         ~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 1039, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        pass_fds, cwd, env,
                        ^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
                        gid, gids, uid, umask,
                        ^^^^^^^^^^^^^^^^^^^^^^
                        start_new_session, process_group)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 1858, in _execute_child
    sys.audit("subprocess.Popen", executable, args, cwd, env)
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 19, in policy
    raise PermissionError('seat contract forbids git mutation: ' + ' '.join(map(str, argv)))
PermissionError: seat contract forbids git mutation: git init -q -b master /var/tmp/souji-r19-MutRevPin-2/souji-r19-rev-pin.tvnc41it/sandbox
```

### M2 drop tracked-tree comparison

```text
Traceback (most recent call last):
  File "<string>", line 22, in <module>
    raise SystemExit(namespace['main'](['--tool', helper, '--tool-dir', lane]))
                     ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/tmp/souji-r19-MutRevPin-2/tests/fixtures/r19-rev-pin.py", line 149, in main
    repo, clean, keep_only, second = build_sandbox(top)
                                     ~~~~~~~~~~~~~^^^^^
  File "/var/tmp/souji-r19-MutRevPin-2/tests/fixtures/r19-rev-pin.py", line 92, in build_sandbox
    subprocess.run(["git", "init", "-q", "-b", "master", repo], check=True,
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                   env=ENV, capture_output=True)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 555, in run
    with Popen(*popenargs, **kwargs) as process:
         ~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 1039, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        pass_fds, cwd, env,
                        ^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
                        gid, gids, uid, umask,
                        ^^^^^^^^^^^^^^^^^^^^^^
                        start_new_session, process_group)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 1858, in _execute_child
    sys.audit("subprocess.Popen", executable, args, cwd, env)
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 19, in policy
    raise PermissionError('seat contract forbids git mutation: ' + ' '.join(map(str, argv)))
PermissionError: seat contract forbids git mutation: git init -q -b master /var/tmp/souji-r19-MutRevPin-2/souji-r19-rev-pin.30ag2cmb/sandbox
```

### restored after M2

```text
Traceback (most recent call last):
  File "<string>", line 22, in <module>
    raise SystemExit(namespace['main'](['--tool', helper, '--tool-dir', lane]))
                     ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/tmp/souji-r19-MutRevPin-2/tests/fixtures/r19-rev-pin.py", line 149, in main
    repo, clean, keep_only, second = build_sandbox(top)
                                     ~~~~~~~~~~~~~^^^^^
  File "/var/tmp/souji-r19-MutRevPin-2/tests/fixtures/r19-rev-pin.py", line 92, in build_sandbox
    subprocess.run(["git", "init", "-q", "-b", "master", repo], check=True,
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                   env=ENV, capture_output=True)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 555, in run
    with Popen(*popenargs, **kwargs) as process:
         ~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 1039, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        pass_fds, cwd, env,
                        ^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
                        gid, gids, uid, umask,
                        ^^^^^^^^^^^^^^^^^^^^^^
                        start_new_session, process_group)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 1858, in _execute_child
    sys.audit("subprocess.Popen", executable, args, cwd, env)
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 19, in policy
    raise PermissionError('seat contract forbids git mutation: ' + ' '.join(map(str, argv)))
PermissionError: seat contract forbids git mutation: git init -q -b master /var/tmp/souji-r19-MutRevPin-2/souji-r19-rev-pin.eplr0wmr/sandbox
```

# Commands run

1. Read the godspeed skill, applicable shokunin binding/protocol sections, operator rules, preregistration and its named prior-round context through read-only tools. Read only the assigned helper and proposed fixture for the probe; no operator-sweep contents were opened.
2. `sha256sum tools/souji-rev-pin.py tests/fixtures/r19-rev-pin.py` in the lane recorded the original input hashes.
3. Copied the two snapshots through `read`/`write` to the private root, preserving their exact byte hashes. Applied M1 and M2 independently with `edit` only on the private helper; restored the full saved helper bytes after each attempt. Ran `sha256sum <private-helper>` for each mutant and restoration.
4. Five bounded invocations used this command shape (the Python `-c` source is reproduced below):

```text
/usr/bin/python -B -c <guard-source> /var/tmp/souji-r19-MutRevPin-2/tests/fixtures/r19-rev-pin.py /var/tmp/souji-r19-MutRevPin-2/tools/souji-rev-pin.py /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r19-MutRevPin-2
```

Guard-source SHA-256: `c052834aa6b5e897231f0041a87c75b1f997718e557244952c638a2d434cbc69`. The outer `subprocess.run` used `cwd=/var/tmp/souji-r19-MutRevPin-2`, captured stdout/stderr, `timeout=30`, and child-only `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`. No global TMPDIR was changed.

```python
import os, runpy, sys, tempfile
fixture, helper, lane, scratch = sys.argv[1:]
real_mkdtemp = tempfile.mkdtemp
def scoped_mkdtemp(*args, **kwargs):
    kwargs['dir'] = scratch
    return real_mkdtemp(*args, **kwargs)
tempfile.mkdtemp = scoped_mkdtemp
def policy(event, args):
    if event != 'subprocess.Popen':
        return
    executable, argv, cwd, env = args
    if isinstance(argv, (list, tuple)) and argv and os.path.basename(str(argv[0])) == 'git':
        allowed = {'rev-parse', 'for-each-ref', 'merge-base', 'diff', 'ls-tree', 'cat-file', 'log', 'show', 'status'}
        i = 1
        while i < len(argv) and str(argv[i]).startswith('-'):
            token = str(argv[i])
            i += 2 if token in {'-C', '-c', '--git-dir', '--work-tree'} else 1
        if i >= len(argv) or argv[i] not in allowed:
            raise PermissionError('seat contract forbids git mutation: ' + ' '.join(map(str, argv)))
sys.addaudithook(policy)
namespace = runpy.run_path(fixture, run_name='policy_guarded_fixture')
raise SystemExit(namespace['main'](['--tool', helper, '--tool-dir', lane]))
```

5. `sha256sum tools/souji-rev-pin.py tests/fixtures/r19-rev-pin.py /var/tmp/souji-r19-MutRevPin-2/tools/souji-rev-pin.py /var/tmp/souji-r19-MutRevPin-2/tests/fixtures/r19-rev-pin.py` followed by both corresponding `cmp` commands exited 0. Lane and private-copy hashes matched the input hashes.
6. `rm -r -- /var/tmp/souji-r19-MutRevPin-2 && test ! -e /var/tmp/souji-r19-MutRevPin-2` exited 0; own scratch was removed after exact restoration and comparison.

# Contract compliance

- Only this scoped report was written in the lane. The helper, fixture, callers, corpus, scorecard and other lane sources were not edited. No patch artifact was requested or created.
- No Git or JJ mutation executed anywhere. The policy hook refused the fixture's first mutating command before process creation. No Git or JJ command otherwise ran during this probe.
- No subagents, swarm, alternate runtime, judgment, integration or shipping. A concise contract blocker was sent only to parent `SoujiR19`; there was no broadcast.
- No signals, live census, fleet-reading fixture, `/proc/*/environ`, credentials, network access, operator-sweep read, driver-state read or write outside the assigned private scratch/report scope.
- Scratch stayed under the private root and was removed. Both helper restorations were exact, with matching full hashes; the fixture remained byte-identical.
- No tool was installed or updated; no pacman transaction occurred. Existing Python and coreutils were sufficient. No unrelated test, linter, formatter or build was run.
- **No killed-mutant claim:** two inconclusive probes, because the pristine detector could not legally reach any behavioral refusal case. Full C2 behavior and no-record effects remain unmeasured by this seat.
