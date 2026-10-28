# W1ScoutArgparse — argparse usage-error exit (r39 C2 disclosure)

Axes: coverage (docs page + live probe + SOURCES row + C2 grounding), evidence (quoted commands), no harm to frozen bytes. Advisory only; no lane edit except this report.

## Verdicts

| check | verdict |
|---|---|
| Installed interpreter is Python 3.14 | **pass** — `Python 3.14.8`, module `/usr/lib/python3.14/argparse.py` |
| Required-arg usage error exit status | **pass** — process status **2**; `SystemExit.code` is int **2** |
| Stream | **pass** — **stderr only** (stdout 0 bytes; stderr 74 bytes) |
| Library-reference quote, ≤25 words, URL + access date | **pass** — 15-word quote on the 3.14 page, fetched 2026-10-28 (same sentence on the `/3` alias, which today serves 3.15.2) |
| Existing SOURCES row covers argparse scope | **yes — S249 only** — no S001–S248 row mentions argparse |
| r39 fact grounded | C2's declared exit map already puts usage and `REFUSAL REV-UNRESOLVED` on status 2, which is argparse's own usage-error status. **Disclosure only.** The frozen C2 predicate does not score argparse's exit. |

## 1. Interpreter

Command:

```
python3 --version; python3 -c 'import argparse,sys; print(sys.version); print(argparse.__file__)'
```

Output:

```
Python 3.14.8
3.14.8 (main, Oct  2 2026, 10:23:31) [GCC 16.2.1 20260810]
/usr/lib/python3.14/argparse.py
```

## 2. Probe (the assigned command)

Command (cwd fleet root; stderr and stdout were mixed in the tool capture):

```
python3 -c 'import argparse;ap=argparse.ArgumentParser();ap.add_argument("--x",required=True);ap.parse_args([])'; echo "EXIT=$?"
```

Output:

```
usage: -c [-h] --x X
-c: error: the following arguments are required: --x
EXIT=2
```

Stream split (scratch `/fast/scratch/hyaku/souji-r39/W1ScoutArgparse`, removed after this report):

```
mkdir -p /fast/scratch/hyaku/souji-r39/W1ScoutArgparse && S=/fast/scratch/hyaku/souji-r39/W1ScoutArgparse && python3 -c 'import argparse;ap=argparse.ArgumentParser();ap.add_argument("--x",required=True);ap.parse_args([])' >"$S/stdout.txt" 2>"$S/stderr.txt"; echo "EXIT=$?"; echo "--- stdout bytes ---"; wc -c "$S/stdout.txt"; echo "--- stderr bytes ---"; wc -c "$S/stderr.txt"; echo "--- stdout ---"; cat -A "$S/stdout.txt"; echo "--- stderr ---"; cat -A "$S/stderr.txt"
```

Output:

```
EXIT=2
--- stdout bytes ---
0 /fast/scratch/hyaku/souji-r39/W1ScoutArgparse/stdout.txt
--- stderr bytes ---
74 /fast/scratch/hyaku/souji-r39/W1ScoutArgparse/stderr.txt
--- stdout ---
--- stderr ---
usage: -c [-h] --x X$
-c: error: the following arguments are required: --x$
```

Stdout empty. Stderr is the usage line plus the error line. Exit 2.

Confirming probe (stdin script, so `prog` is `-` rather than `-c`; same status). Argparse writes the usage message, then raises `SystemExit`:

```
python3 - <<'PY'
import argparse, sys
try:
    ap = argparse.ArgumentParser()
    ap.add_argument("--x", required=True)
    ap.parse_args([])
except SystemExit as e:
    print(f"SystemExit.code={e.code!r} type={type(e.code).__name__}")
    sys.exit(0)
print("NO_SYSTEMEXIT")
PY
```

Output:

```
usage: - [-h] --x X
-: error: the following arguments are required: --x
SystemExit.code=2 type=int
```

Installed library agrees. `ArgumentParser.error` (`/usr/lib/python3.14/argparse.py:2774-2785`) calls `print_usage(_sys.stderr)` then `self.exit(2, ...)`. `exit()` (`:2769-2772`) writes its message to stderr and calls `_sys.exit(status)`. Default `exit_on_error` is `True` (`:1882`). `ArgumentParser.exit`'s own default status is 0; the usage-error path passes 2. That is the exclusion S249's scope already names.

## 3. Library reference quote

Fetched 2026-10-28 (HTTP 200) with `urllib.request` from this host:

- https://docs.python.org/3.14/library/argparse.html — final URL same; `<title>` is the **Python 3.14.10** documentation (docs build, not the installed 3.14.8 interpreter). Section id `exit-on-error` is present.
- https://docs.python.org/3/library/argparse.html — same bytes' sentence; `<title>` is **Python 3.15.2** documentation. This is the URL S249 cites.

Located quote (15 words), section `exit_on_error` / `#exit-on-error`, both pages, stripped text:

> it will print a message to sys.stderr and exit with a status code of 2

The sentence it sits in: "Normally, when you pass an invalid argument list to the `parse_args()` method of an `ArgumentParser`, it will print a message to `sys.stderr` and exit with a status code of 2."

A second hit of "status code of 2" is `ArgumentParser.error`: "This method prints a usage message, including the message, to sys.stderr and terminates the program with a status code of 2." That is the method the usage path calls; it is not the quote S249 locates.

Exact S249 string is present in the stripped 3.14 page (`EXACT_S249_QUOTE True`).

## 4. SOURCES coverage

`corpus/SOURCES.md` contains the substring `argparse` on exactly two lines (scan of the file):

- line 20, round-39 provenance: S249 "is argparse's usage-error exit status (docs.python.org/3, fetched 2026-10-28; installed interpreter Python 3.14.8)".
- line 198, registry row **S249** — kind docs, tier A, status `mined`, opened 2026-10-28, used-by `corpus/lessons/round-39.md`. Scope: "argparse's own usage-error exit status (2), which a tool's declared exit map must not contradict; not the `ArgumentParser.exit()` method's default status 0". Anchor: § `exit_on_error` (docs.python.org/3, Python 3.15.2 page fetched 2026-10-28; installed interpreter Python 3.14.8). Teaches quote is the 15-word sentence above.

No earlier row covers argparse. S249 already admits the fact this seat re-checked. This seat did not open or edit a row.

## 5. What r39 fact it grounds — disclose, do not claim

Frozen contract `census/round-39/preregistration.txt` C2: `tools/souji-citation-reconcile.py` resolves `--rev` / `--register-rev` and refuses a non-commit revision with exit 2 (`REFUSAL REV-UNRESOLVED`). Scored legs (same file, and `census/round-39/c2-counter.py` header) are L1 unresolvable `--rev` → rc 2 `REV-UNRESOLVED`, L2 blob `--rev` same class, L3 unresolvable `--register-rev` stays rc 2, L4 drift docstring class mapping, L5 fixture 8/8, L6 six consumers. None of those legs asserts argparse's usage-error status.

The tool's own map (`tools/souji-citation-reconcile.py:45-50`) is: "Exit: 0 mismatches=0, 1 any mismatch …, 2 usage / malformed register / unresolvable revision" and "`REFUSAL REV-UNRESOLVED` and exits 2". The counter's map (`census/round-39/c2-counter.py:27`) is the same overlap: "2 usage or could-not-evaluate input."

Because argparse's own usage errors already exit 2 on stderr, status 2 alone cannot mean "could-not-evaluate". The class token `REV-UNRESOLVED` is what separates that refusal from a usage error. `corpus/lessons/round-39.md:116-117` already records this as a named limit: "The `argparse` exit-2 fact (S249) is a disclosure, not a claim: C2's distinction rides on the class names, not on the status alone." The Gate row (`:41`) admits S249 for that reason.

**The claim does not need this fact as a predicate. It only discloses it**, so the declared exit map does not contradict the library. A do-nothing reading of C2 can be true while nobody re-proves argparse's exit; failing to mention the shared status would make "exit 2" look like a private could-not-evaluate code.

## Scratch

`/fast/scratch/hyaku/souji-r39/W1ScoutArgparse` held `stdout.txt` and `stderr.txt` for the redirected probe. Removed with `rm -rf` after those bytes were quoted above. No install. No git mutation. Frozen prereg, items, specs, and receipts untouched.
