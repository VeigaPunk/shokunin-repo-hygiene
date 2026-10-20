# RevGateCLI — landing-gate CLI, exit codes, `--json`, SUMMARY vs header docstring

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` @ `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
Reviewed object: `tools/souji-landing-gate.py`, blob sha256 `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`
(`git cat-file blob HEAD:…` hashes identically; `git diff --stat HEAD` empty).

Contract under test: the tool's header docstring, `tools/souji-landing-gate.py:26-38` (CLI at 26-29,
exit map at 31-32, output at 34-35, ids at 37-38), plus its registry restatement `SKILL.md:152`.
**Source-only**: no command in this review executed the tool; every claim below is a static reading
of the cited lines with no dynamic confirmation (no ALLOWED-EXEC was granted for this item).

## Findings

### F1 — high — `emit` returns 2 for a fully evaluated run (violates docstring:31-32)

Sites: `tools/souji-landing-gate.py:611-614` (destination exists) and `:629-635` (write `OSError`),
against the emission at `:596-608`.

`:596-608` prints every finding line and the `SUMMARY findings=K…` line first. Only then does
`:611-614` return 2 when `--json`'s path already exists, and `:629-635` return 2 for any write
failure. So `… --rev R --round N --json out.json` with a red landing prints
`LG-PARSE-REG\t…` + `SUMMARY\tfindings=1…` and exits **2**.

Docstring:31-32 defines 2 as "could-not-evaluate", with an enumerated cause list (usage, unknown
rev, no SKILL.md, missing wave dir, git failure) that contains neither refusal nor write failure;
`SKILL.md:152` repeats the same mapping. A caller keyed on the exit code therefore cannot tell a
red landing from an unevaluated one — the one distinction this gate exists to carry — and the
requested JSON record is also absent. `--json` is not exercised anywhere (`tests/fixtures/r16-landing-gate.py`
has no `--json` argument; `census/round-16/run-matrix.py` never invokes the gate), so nothing caught this.
The defect is conditional on `--json` with an existing destination or a failing write — no in-lane
caller does either today — but it is the exit code of the reviewed CLI surface, and any future caller
inherits the ambiguity.

Smallest fix — refuse before evaluating, keep the exit truthful afterwards:

```python
# main(), before the evaluate() call at :1000
if args.json_out and os.path.exists(args.json_out):
    print("--json output %s exists; refusing to overwrite" % args.json_out, file=sys.stderr)
    return 2
```

then delete `:612-614` (the `open(…, "x")` at `:630` still refuses a racing creation) and change
`:635` to `return result["exit"]` after its stderr note. If instead a missing requested artifact must
be fatal, the one-line alternative is to amend docstring:31-32 with "`--json` exists/unwritable" —
but then exit 2 stops meaning "not evaluated" and every consumer must additionally parse SUMMARY.

### F2 — medium — could-not-evaluate drops established findings while keeping their counters (partial; docstring silent, audit record wrong)

Sites: `:540-551` (`findings` local), `:548`/`:563` (`checked_reg` on `result`), `:571`, `:582-588`;
raise at `:313-314`.

`result["checked_reg"]` is incremented at `:548` and `:563`, but the corresponding finding goes to
the function-local `findings`; `result["findings"]` is assigned only at `:582`, inside the `try`.
Any `EvalError` after `:540` — e.g. `:313-314` when the wave directory holds no `.md` reports, or a
git failure inside `check_frozen_pins` — takes `:586-588`, leaving `result["findings"] == []` with
`checked_reg`/`checked_pins` nonzero. `emit` then prints `SUMMARY\tfindings=0\tchecked_reg=1…` and
`--json` records `"findings": []` with `"checked_reg": 1`.

Static trace, not executed: a repo whose `SKILL.md` cites `tools/bad.sh` (`bash -n` rc 2) and whose
`.ufo/waves/round-16/` has no `.md` ticks `checked_reg` at `:548`, appends `LG-PARSE-REG` at `:551`,
then aborts at `:313-314`; the SUMMARY reports the check but not its failure. For a gate whose
headline id is `LG-PARSE-REG`, that is the r15 defect class surviving inside the new gate.

Smallest fix — hoist the list and flush it on abort (note the `except` would otherwise hit an
unbound name when the raise happens before `:540`):

```python
    result = { … }                 # :518-526
    findings = []                  # add here
    snapdir = tempfile.mkdtemp(…)  # :527
…
        # findings = []            # delete the re-init at :540
…
    except EvalError as exc:       # :586
        findings.sort(key=lambda f: (f[0], f[1], f[2]))
        result["findings"] = [{"id": i, "path": p, "detail": d} for i, p, d in findings]
        result["error"] = str(exc)
```

Exit stays 2; SUMMARY/`--json` then show the proven finding together with the abort reason.

### F3 — medium — uncaught `OSError` gives a traceback + exit 1, colliding with "1 findings" and bypassing the documented "git failure → 2" (fails for absent git; partial for environment errors)

Sites: `:527` (`mkdtemp` outside the `try:` at `:528`), `:199-203` (snapshot `open` + `bash` spawn),
`:118-122` (`_git` spawn), `:152-156` (`blob_at_path` spawn), `:469-473` (raw `measured_commit`
spawn), `:749` (selftest top `mkdtemp`), and the unguarded `evaluate(...)` at `:1000`.

None of these wrap `subprocess.run`/`open`/`mkdtemp`, and the only handler is `except EvalError`
at `:586`. `FileNotFoundError` (git or bash absent), or `OSError` from `mkdtemp`/`open`
(ENOSPC/EACCES/read-only `/var/tmp`), escapes `evaluate` to an uncaught traceback; the interpreter
exits **1** with no `COULD-NOT-EVALUATE`, no SUMMARY, and no `--json` — indistinguishable from
"findings". Docstring:31-32 promises 2 on "git failure"; that holds only for git present and
returning rc≠0 (`:123-127`), not for git absent.

Smallest fix:

```python
    snapdir = None                 # replace :527
    try:
        snapdir = tempfile.mkdtemp(prefix="souji-landing-gate-", dir="/var/tmp")
…
    except (EvalError, OSError) as exc:   # :586
…
    finally:
        if snapdir:
            shutil.rmtree(snapdir, ignore_errors=True)
```

and wrap the four `subprocess.run`/`open` sites with `except OSError as exc: raise EvalError(...)`
(at `:469-473` catch only `OSError`; rc≠0 must keep meaning "dangling `measured_commit`").

### F4 — low — `git diff --name-only` output split on all whitespace (fails, latent)

`:560` — `for path in sorted(set(changed_out.split())):`. `str.split()` splits on spaces too, so a
changed script path containing a space, e.g. `tools/my gate.sh`, yields fragments `tools/my` and
`gate.sh`; the latter matches `SCRIPT_EXT_RE` (`:93`) and is resolved as a repo-root path, where
`blob_at_path` returns `None` and `parse_script` returns `"blob unreadable at <rev>"` (`:228`) →
`LG-PARSE-CHANGED` on a tree where nothing is broken → exit 1 (`:585`). `git diff --name-only` is
newline-separated (spaces are not quoted by default), so the line is the intended delimiter.

Smallest fix: `changed_out.splitlines()` — or add `-z` to the diff at `:555-559` and split on `\0`
to also survive git's C-quoted paths.

### F5 — low — `--json` / `--selftest` / SUMMARY semantics are documented only partially (partial, documentation)

Docstring:26-35 names `--json OUT` and `--selftest` but omits:

- the `--json` payload (`:615-628`): `exit`, `findings[{id,path,detail}]`, `summary{findings,
  checked_reg,checked_pins,checked_markers,checked_reports}`, `resolved_rev`, `resolved_base`,
  `error` — six top-level keys, none of them named in the docstring;
- write policy: `--json` is skipped entirely when argument validation fails (`:994-996`) or `--root`
  is not a directory (`:997-999`), but is written on the `EvalError` path (`:609-635`); an existing
  path is refused at `:611-614`; nothing of this is in the docstring;
- `--selftest` exits 0/1 (`:970-971`), which the Exit line (31-32) does not cover;
- exit-2 breadth at `:313-314`: the code also exits 2 when `.ufo/waves/round-N/` exists but holds no
  `.md`, whereas docstring:32 says only "missing … at REV";
- undocumented field meaning: `checked_reg` counts registry citations *and* changed-script parses
  (double counting a cited script that also changed, `:548`+`:563`), and `checked_pins` counts both
  the per-revision `files[]`/`record_sha256` checks and the per-`measured_commit` re-checks
  (`:396`, `:426`, `:479`), so the SUMMARY numbers cannot be interpreted from the header alone;
- `docstring:32` lists "git failure" but `SKILL.md:152` omits it — the two public statements of the
  same contract differ.

Smallest fix (documentation only): append to the Output block

```text
--json payload: exit, findings, summary{findings,checked_reg,checked_pins,checked_markers,
checked_reports}, resolved_rev, resolved_base, error; written once after stdout, skipped when
argument/--root validation fails; an existing path is refused. SUMMARY counts: checked_reg =
registry citations + changed-script parses; checked_pins = files[]/record_sha256 at REV plus
files[] at measured_commit. --selftest: 0 all cases pass, 1 any case fails.
```

and add "git failure" to the `SKILL.md:152` exit column.

## Verified as documented (no finding)

- 0/1 on the normal path: `:585` `result["exit"] = 1 if findings else 0`, returned by `:636`; matches docstring:31.
- 2 for unknown rev (`:164-169`; the message comes from the wrapper at `:166`), no `SKILL.md` (`:535-536`), empty/missing wave prefix (`:313-314`), and git rc≠0 (`:123-127`): matches docstring:31-32 apart from F3/F5.
- SUMMARY literal at `:599-608` has exactly the docstring:35 field order, and the `--json` `summary` object repeats exactly those five names (`:618-624`).
- TSV shape: `:596-598` prints `id\tpath\tdetail`, sanitizes tabs/newlines in `detail`, and emits the `:581` sort key (id, path, detail) to both stdout and JSON. `path` is not sanitized, but every emitted path is constrained (CITED_PATH_RE `[A-Za-z0-9_.-]+`, frozen-dir name, whitespace-split diff output), so a tab cannot reach column 2 — not filed.
- `--json` refusal is race-safe (`os.path.exists` plus `open(..., "x")` at `:630`); the payload is one JSON object with a trailing newline (`:631-632`).
- Emitted ids are exactly the seven at docstring:37-38. `FINDING_IDS` (`:96-104`) is never read by tool or fixture, so the "pinned" list is enforced only by the literals — dead constant, no behavioral effect (drop it, or assert `set(ids) <= set(FINDING_IDS)` in the selftest).
- `resolve_commit`'s `if not resolved:` branch (`:167-169`) is unreachable: `rev-parse --verify --quiet` prints a sha with rc 0 or returns rc≠0, which `_git` already converted at `:123-127`. Dead branch, no behavioral effect.
- `--selftest` returning before the required-argument check (`:992-993`) is consistent with the docstring's separate `--selftest` invocation; extra flags are ignored, not rejected.

## Residual risk / verification gaps

- No dynamic confirmation: I did not execute the gate or its selftest (source-only item, no ALLOWED-EXEC). F1-F4 are read from the cited lines; F2's scenario is a static trace.
- `--json` has zero coverage: no `--json` in `tests/fixtures/r16-landing-gate.py`, and the fixture's exit-code assertions (`:149-190`) only reach the normal and `EvalError` paths. The refusal/write-failure exits (F1) and the payload shape (F5) are untested by construction.
- The gate's own selftest cannot catch F1/F3: its cases call `evaluate()` in-process (`check()` at `:766`) and never exercise `emit` or `main`.
- Not verified: whether callers outside this lane pass `--json`; no recursive search of the lane was performed.

STATUS: ok

## Commands

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-landing-gate.py && ls -la tools/ | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain | head -30 && wc -l tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "mkdtemp\|snapdir = \|def emit\|return 2\|def main\|def resolve_commit\|unknown revision\|split()\|def evaluate\|except EvalError\|result\[\"findings\"\]\|checked_reg\|checked_markers\|checked_reports\|checked_pins\|COULD-NOT-EVALUATE\|print_usage\|add_argument" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "landing-gate\|--json\|--root\|--rev\|--round\|--base\|SUMMARY\|exit" tests/fixtures/r16-landing-gate.py | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=118 && NR<=172 {printf "%d: %s\n", NR, $0}' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=505 && NR<=645 {printf "%d: %s\n", NR, $0}' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1 && NR<=46 {printf "%d: %s\n", NR, $0}' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "subprocess.run\|rev-parse" tools/souji-landing-gate.py | awk -F: '$1>420 && $1<510'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "checked_reg\|checked_pins\|checked_markers\|checked_reports\|SUMMARY\|--json\|landing-gate" SKILL.md corpus/lessons/round-16.md 2>/dev/null | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "json\|returncode\|exit\|landing" census/round-16/run-matrix.py 2>/dev/null | head -40; echo "---FIXTURE---"; grep -n "json" tests/fixtures/r16-landing-gate.py | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "import json;d=json.load(open('census/round-16/c1-matrix-landing.json'));print(json.dumps(d,indent=1)[:1500])" 2>/dev/null || head -60 census/round-16/c1-matrix-landing.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=176 && NR<=215 {printf "%d: %s\n", NR, $0}' tools/souji-landing-gate.py; echo ---; awk 'NR>=455 && NR<=480 {printf "%d: %s\n", NR, $0}' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la .ufo/waves/round-16/w2/ | head -20 && grep -n '"--json"\|\-\-json' tests/fixtures/r16-landing-gate.py census/round-16/run-matrix.py | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file blob HEAD:tools/souji-landing-gate.py | sha256sum && git log -1 --format='%h %s' -- tools/souji-landing-gate.py && git diff --stat HEAD -- tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=979 && NR<=1005 {printf "%d: %s\n", NR, $0}' tools/souji-landing-gate.py; echo ---; grep -n "no .md reports\|def check_carry\|if not reports" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "FINDING_IDS" tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py; echo "---"; awk 'NR>=90 && NR<=106 {printf "%d: %s\n", NR, $0}' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "blob unreadable\|def parse_script\|SELFTEST\\tpass\|return 0 if failed\|def check(\|top = tempfile.mkdtemp\|def run_selftest\|return run_selftest\|result = evaluate\|return emit" tools/souji-landing-gate.py
```

Read-only `read` calls on `tools/souji-landing-gate.py` (lines 1-200, 202-523, 523-1005) and
`tests/fixtures/r16-landing-gate.py` via `grep` are included above; no other tool ran against the
lane, and no file outside this report was written.
