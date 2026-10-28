# W1SimpC2 — YAGNI review of `census/round-39/c2-counter.py`

seat: W1SimpC2 (simplifier, leaf — no subagent dispatch)
role: advisory. No lane bytes were written; the proposal was measured in scratch only.
lane: /home/vgpnk/Projects/shokunin/souji-shokunin
base rev: ed30b7f5b77939c9073348d810730bc4f355708d
lane HEAD at review time: 5230a3414d062152aa76f141ab45afb62bcfcc4c
reviewed bytes: `census/round-39/c2-counter.py`, sha256
`732b1e425a6ddc37a9632431269c9c679b32cbe18a22cb35b5b4f4cec151ee11`, 290 lines.
tooling: none installed; no `uv tool`/`npx`/binary install was needed (pacman not touched).

Review chronology (the lane moved under me, once): the review began on
`326caa16224605bb0cbfc9a62f0d9ce39f6c9df729b0829a589a1a0bee39a781` (286 lines, HEAD `d4c1755`) and
the L1 then landed `5230a34`, whose only delta in this file is a scratch-root exit-2 guard around
`tempfile.mkdtemp`. The proposal was re-based onto the new bytes and every arm re-run against them;
all evidence below is from the current bytes. The guard is preserved untouched by the proposal
(§4, hunk `@@ -162,12 +167,14 @@`). Later lane commits (`9440270`, `a6fe389`) did not touch
this file: at HEAD `a6fe389` its sha256 is still `732b1e42…`, so the §4 patch still applies.

## 1. What I ran, and what it printed

All runs used absolute paths. Every run used an explicit `--scratch`/`TMPDIR` under
`/fast/scratch/hyaku/souji-r39/W1SimpC2/`.

### 1.1 Counter bytes are the committed bytes

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain census/round-39/c2-counter.py
(no output)
$ sha256sum census/round-39/c2-counter.py
732b1e425a6ddc37a9632431269c9c679b32cbe18a22cb35b5b4f4cec151ee11  census/round-39/c2-counter.py
$ git log --oneline -1 --format='%h %s' -- census/round-39/c2-counter.py
5230a34 round-39: integrate wave-1 lane edits (LOG/SKILL/QUALITY cells with revision pins), scratch-root exit 2 in the three counters, A2 consumer count, receipts
```

Verdict: the bytes I reviewed are the committed bytes at HEAD `5230a34`; no sibling was mid-edit
in this file.

### 1.2 Base arm — original bytes

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && \
  TMPDIR=/fast/scratch/hyaku/souji-r39/W1SimpC2/w-base python3 -B census/round-39/c2-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --scratch /fast/scratch/hyaku/souji-r39/W1SimpC2/w-base
LEG L1 FAIL new rc=1 class=False old rc=1 class=False
LEG L2 FAIL new rc=1 class=False old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=e555d8281484
EXIT=1
```

Verdict: the frozen base-arm reading `legs=6 pass=2 fail=4 harm=0` reproduces on the original
bytes. `tool_sha` equals `census/round-39/records/c2-before.txt` exactly. `fixture_sha` and the L5
tuple differ from that receipt — see §5.1; the leg verdicts are identical.

### 1.3 HEAD arm — original bytes

```
$ TMPDIR=.../w-head python3 -B census/round-39/c2-counter.py --root <lane> \
  --rev 5230a3414d062152aa76f141ab45afb62bcfcc4c --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --scratch .../w-head
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
EXIT=0
```

Verdict: the C2 predicate reading `legs=6 pass=6 fail=0 harm=0` holds on HEAD `5230a34`, and
`tool_sha` equals `c2-after.txt`. (The same reading was obtained at the earlier HEADs
`d4c1755` and `2201778e7736af82e7d8a42dec2494f115bf3923`.)

### 1.4 Proposed minimal form — equivalence, byte for byte

Proposal measured as `/fast/scratch/hyaku/souji-r39/W1SimpC2/c2-min.py` (sha256
`7217c9ddae37b9cbd3f90dfd94235f5da3e05cd844e49f54f321f52b53ec14e3`, 291 lines). Each arm was run
twice — original then proposal — into files, then compared with `diff -q`:

```
$ TMPDIR=.../w-base python3 -B <lane>/census/round-39/c2-counter.py --root <lane> --rev ed30b7f... --base-rev ed30b7f... > w-base/orig.txt 2>&1
$ TMPDIR=.../w-base python3 -B .../c2-min.py                     --root <lane> --rev ed30b7f... --base-rev ed30b7f... > w-base/min.txt  2>&1
$ diff -q w-base/orig.txt w-base/min.txt && echo "DIFF: identical"
DIFF: identical          (both exit 1; SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=e555d8281484)

$ ... --rev 5230a341... --base-rev ed30b7f...   (original vs proposal)
DIFF: identical          (both exit 0; SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484)

$ ... --root <synthetic harm repo> --rev 047f8f9... --base-rev 651ae10...   (original vs proposal)
DIFF: identical          (both exit 1; SUMMARY legs=6 pass=0 fail=6 harm=1 tool_sha=6c295408449d/b61a237f29f5 fixture_sha=e555d8281484)
```

Verdict: every LEG line, the SUMMARY line and the exit code are byte-identical on the base arm,
the HEAD arm, and a synthetic failing arm that actually exercises the `harm` path. The proposal
changes no leg verdict.

### 1.5 Compile check on the proposal

```
$ python3 -B -c "import py_compile; py_compile.compile('.../c2-min.py', cfile='.../c2-min.pyc', doraise=True)"
COMPILE OK                                   # first pass, before the re-base onto 5230a34
$ python3 -B -c "import py_compile; py_compile.compile('.../c2-min.py', cfile='.../c2-min.pyc', doraise=True)"
py_compile rc: 0                             # re-based proposal
```

Verdict: the proposal parses/compiles, before and after the re-base.

### 1.6 The §4 patch applies to the current lane bytes and reproduces the measured proposal

```
$ python3 -B <<'PY'                          # extract the ```diff block from this report, patch a copy
... re.findall(r"```diff\n(.*?)```", report) ; patch -s <copy of lane file> <block> ; diff -q <copy> c2-min.py
PY
diff blocks in report: 1
patch rc: 0 |
report patch reproduces measured proposal: True
proposal sha: 7217c9ddae37b9cbd3f90dfd94235f5da3e05cd844e49f54f321f52b53ec14e3
patched  sha: 7217c9ddae37b9cbd3f90dfd94235f5da3e05cd844e49f54f321f52b53ec14e3
```

Verdict: the patch in §4 is self-contained — applied to `census/round-39/c2-counter.py` at
`5230a34` it yields byte-identical bytes to the proposal that produced the §1.4 readings.

### 1.7 Synthetic arm that makes `harm` non-zero (built for §3.2)

```
$ D=$(mktemp -d) && git -C "$D" init -q        # via tempfile.mkdtemp(dir=/fast/scratch/...)
toplevel = /fast/scratch/hyaku/souji-r39/W1SimpC2/harm-demo.b8ylbjkc | matches: True
base = 651ae10da2db93d4f3f2852add69523c239a4c38
new  = 047f8f9380a32a1dbf2b817255606fdae17c6064
```

Fixture repo contents: a `tools/souji-citation-reconcile.py` that always `sys.exit(1)` (so both
revisions break L3), a `tools/souji-worktree-drift.py` that always `sys.exit(1)` with
`RECORD-MALFORMED: nope`, `corpus/SOURCES.md`, and copies of the six `tests/fixtures/*.py`
instruments. `git rev-parse --show-toplevel` was asserted equal to `$D` before the first commit.
No mutating git command was run anywhere except inside this `mktemp -d` fixture.

## 2. Findings that improve operability, harm nothing (KEEP)

Each item below is proved dead or duplicated from the call sites, and each was measured identical
in §1.4.

### F1 `lane_root_of` → one `lane` local (3 normalisation sites → 1)

`lane_root_of(args)` is `os.path.abspath(args.root)` and is called at two sites (L5, L6), while
`fixture_sha` repeats the same normalisation inline as `os.path.join(os.path.abspath(root), ...)`.
Replace the helper with one local next to `root = args.root`, carrying the helper's docstring as a
comment, and use it at all three sites. Removes a 3-line helper and one duplicated normalisation;
the "instrument bytes come from the worktree" rule gains one authority instead of two spellings.

### F2 `run_fixture`'s `extra` parameter and CONSUMERS' `--tool` column are dead

```
def run_fixture(fixture, tool, scratch, work, extra=None):
    cmd = ["python3", "-B", fixture] + list(extra or ["--tool", tool]) + ["--work", work]
```

Every consumer row in `CONSUMERS` carries `"--tool"` as its fourth field, and both L6 call sites
pass `extra=[flag, new_tool]` where `flag == "--tool"` and `new_tool` is the tool. So at every call
site `list(extra or ["--tool", tool])` is exactly `["--tool", tool]`: the `extra` parameter, its
`or` fallback (which can never fire — `extra` is never `None`/empty at a call site), the two
`extra=` arguments and the five `"--tool"` tuple fields all carry no information. Delete all of
them.

### F3 `run_fixture`'s `work` parameter is dead

Both call sites pass `base_scratch` for `scratch` *and* for `work`, so `--work` always receives the
same directory the tool file was staged into. Drop the parameter and pass `scratch`.

### F4 `run_citation`'s default is dead and duplicates `ZERO`

`def run_citation(tool, root, rev, scratch, register_rev="0" * 40)` — all three call sites (L1,
L2, L3) pass `register_rev` explicitly. The default is never used and repeats the `ZERO = "0" * 40`
constant 4 lines above it. Drop the default.

### F5 The record-class vocabulary is duplicated, and its asymmetry is invisible

`classify` iterates `("RECORD-MISSING", "RECORD-MALFORMED", "RECORD-EMPTY", "RECORD-OUTSIDE-ROOT")`
in priority order; `docstring_classes` iterates `("RECORD-MISSING", "RECORD-MALFORMED")`. That the
two sets differ — and that `classify`'s order is load-bearing (first token present wins) — is
nowhere stated. Name both:

```
RECORD_CLASSES = ("RECORD-MISSING", "RECORD-MALFORMED", "RECORD-EMPTY", "RECORD-OUTSIDE-ROOT")
DOC_CLASSES = ("RECORD-MISSING", "RECORD-MALFORMED")
```

Behaviour is identical on every input (same tuples, same order). Grounding for the comment: the
drift tool's docstring maps `RECORD-MISSING` to EACCES/ELOOP, `RECORD-MALFORMED` to
ENOENT/non-regular/schema/TOTAL violations, `RECORD-EMPTY` to "no REPO rows" and
`RECORD-OUTSIDE-ROOT` to a row escaping root (`tools/souji-worktree-drift.py:44-50`, raise sites at
:135-136, :168, :293, :310). L4's two probes are an absent path (ENOENT → MALFORMED) and a mode-0
path (EACCES → MISSING); neither probe can reach row parsing, so the last two classes are
unreachable *for these probes* — which is exactly why the asymmetry deserves a name rather than
being implied by two inline literals.

## 3. Simplifications REFUSED

### 3.1 REFUSED — narrowing `classify` to the two reachable classes

Deleting `RECORD-EMPTY`/`RECORD-OUTSIDE-ROOT` from `classify` cannot change L4's verdict on the two
probes (a class outside `DOC_CLASSES` fails `new_ok` whether `classify` returns it or `NO-CLASS`).
It is refused anyway because it changes `classify`'s semantics: the token order is a priority rule,
and a message carrying two tokens would classify differently, so a later probe (or a reused
`classify` over a real record file) could flip L4. F5 gets the documentation benefit with zero
semantic risk.

### 3.2 REFUSED — replacing the `harm` counter with a constant / deleting the field

`harm` has two increment sites and both are live, and they are two different classes:
`census/round-39/c2-counter.py:223` (`harm += 1` when L3 fails — the contract harm the leg exists
for) and `:274` (`harm += 1` when a consumer's passing-case count drops against base, which is a
*strictly narrower* condition than L6 failing, since L6 also fails on `NO-SUMMARY` or non-green).
It is therefore **not** redundant with the leg verdicts.

Measured, not asserted: the synthetic arm in §1.7 makes L3 fail on both revisions, and the three
variants print

```
original   SUMMARY legs=6 pass=0 fail=6 harm=1 ...
proposal   SUMMARY legs=6 pass=0 fail=6 harm=1 ...
const-harm SUMMARY legs=6 pass=0 fail=6 harm=0 ...     <- harm deleted / literalised
```

(`c2-constharm.py` = the proposal with `harm = 0` and both increments removed, `harm=0` printed as
a literal, and `and harm == 0` dropped from the return.) The frozen summary field would then read
`harm=0` on a run that contains a genuine harm class — the one field that distinguishes "a consumer
lost cases" from "a leg failed for another reason" would become non-evidential. REFUSED. The field
is 4 lines and it is the only harm signal the counter has.

### 3.3 REFUSED — dropping `and harm == 0` from the return

The clause is unreachable today: `harm > 0` implies `fail > 0` at both sites (site :223 is guarded
by `if not ok:` on the leg's own `ok`; site :274 sets `consumer_ok = False`, i.e. L6 fails). So
`return 0 if passed == len(legs) and harm == 0 else 1` and `return 0 if passed == len(legs) else 1`
agree on every possible input — no run can distinguish them, which is why no measurement is
offered for it. Refused on cost/benefit: it saves one clause and removes the only place where a
harm class could fail the run without a leg flipping, i.e. it would make future strictness harder
to add. `harm` stays as written.

### 3.4 REFUSED — a shared `stage()` helper for `extract` and the fixture staging

`extract` (git bytes → scratch, then `chmod 755`) and the fixture staging (worktree bytes → scratch)
share a 3-line "open/write" shape. Hoisting it into a third helper would remove those 3 lines from
two places and add a function plus a call-indirection; after F2/F3 the staging lives in exactly one
place (`run_fixture`) and the remaining `extract` body is 4 statements. Refused: it is a second
convention for the same thing, which is what this seat exists to prevent.

## 4. Proposed minimal form (verbatim patch)

290 → 291 lines; 28 removed / 31 added non-blank lines (the net +1 line is the 3 added
comment/docstring lines). Removed: one helper, three dead parameters/columns (`extra`, `work`,
`--tool`), one dead default, one duplicated normalisation, two duplicated class literals.

Verbatim `diff -u census/round-39/c2-counter.py <proposal>` against the current lane bytes (only
the `---`/`+++` header lines are dropped):

```diff
@@ -51,20 +51,19 @@
 }
 CITATION = "tools/souji-citation-reconcile.py"
 DRIFT = "tools/souji-worktree-drift.py"
+# classify() priority order over the drift tool's refusal classes; the drift docstring must map
+# only DOC_CLASSES (the two L4 probes can reach: ENOENT -> MALFORMED, EACCES -> MISSING).
+RECORD_CLASSES = ("RECORD-MISSING", "RECORD-MALFORMED", "RECORD-EMPTY", "RECORD-OUTSIDE-ROOT")
+DOC_CLASSES = ("RECORD-MISSING", "RECORD-MALFORMED")
 CONSUMERS = (
-    ("r38-drift-record", "tests/fixtures/r38-drift-record.py", DRIFT, "--tool"),
-    ("r36-worktree-drift", "tests/fixtures/r36-worktree-drift.py", DRIFT, "--tool"),
-    ("r38-drift-envelope", "tests/fixtures/r38-drift-write-envelope.py", DRIFT, "--tool"),
-    ("r37-citation", "tests/fixtures/r37-citation-reconcile.py", CITATION, "--tool"),
-    ("r38-citation-commit", "tests/fixtures/r38-citation-commit.py", CITATION, "--tool"),
+    ("r38-drift-record", "tests/fixtures/r38-drift-record.py", DRIFT),
+    ("r36-worktree-drift", "tests/fixtures/r36-worktree-drift.py", DRIFT),
+    ("r38-drift-envelope", "tests/fixtures/r38-drift-write-envelope.py", DRIFT),
+    ("r37-citation", "tests/fixtures/r37-citation-reconcile.py", CITATION),
+    ("r38-citation-commit", "tests/fixtures/r38-citation-commit.py", CITATION),
 )
 
 
-def lane_root_of(args):
-    """Instrument (fixture) bytes come from the working tree; audited tool bytes come from --rev."""
-    return os.path.abspath(args.root)
-
-
 def child_env(scratch=None):
     env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")}
     env.update(GIT_ENV)
@@ -105,7 +104,7 @@
     return dest
 
 
-def run_citation(tool, root, rev, scratch, register_rev="0" * 40):
+def run_citation(tool, root, rev, scratch, register_rev):
     return subprocess.run(
         ["python3", "-B", tool, "--root", root, "--rev", rev,
          "--register", "census/round-38/cells.tsv", "--register-rev", register_rev],
@@ -124,7 +123,7 @@
 
 def classify(proc):
     out = (proc.stdout + proc.stderr).replace("\n", " ")
-    for cls in ("RECORD-MISSING", "RECORD-MALFORMED", "RECORD-EMPTY", "RECORD-OUTSIDE-ROOT"):
+    for cls in RECORD_CLASSES:
         if cls in out:
             return cls
     return "NO-CLASS"
@@ -138,15 +137,21 @@
     out = {}
     for line in doc.split("\n"):
         stripped = line.strip()
-        for cls in ("RECORD-MISSING", "RECORD-MALFORMED"):
+        for cls in DOC_CLASSES:
             if stripped.startswith(cls) and cls not in out:
                 out[cls] = stripped
     return out
 
 
-def run_fixture(fixture, tool, scratch, work, extra=None):
-    cmd = ["python3", "-B", fixture] + list(extra or ["--tool", tool]) + ["--work", work]
-    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
+def run_fixture(lane, path, name, tool, scratch):
+    """Stage a worktree fixture (instrument bytes) into scratch, then run it against `tool`."""
+    dest = os.path.join(scratch, name)
+    with open(os.path.join(lane, path), encoding="utf-8") as handle:
+        src = handle.read()
+    with open(dest, "w", encoding="utf-8") as handle:
+        handle.write(src)
+    proc = subprocess.run(["python3", "-B", dest, "--tool", tool, "--work", scratch],
+                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                           check=False, env=child_env(scratch))
     match = re.search(r"SUMMARY cases=(\d+) pass=(\d+) fail=(\d+)", proc.stdout)
     if not match:
@@ -162,12 +167,14 @@
     ap.add_argument("--scratch")
     args = ap.parse_args(argv)
     root = args.root
+    # Instrument (fixture) bytes come from the working tree; audited tool bytes come from --rev.
+    lane = os.path.abspath(root)
     for flag, rev in (("--rev", args.rev), ("--base-rev", args.base_rev)):
         if not REV.match(rev) or not resolves(root, rev):
             sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s %s does not resolve\n" % (flag, rev))
             return 2
     tool_sha = hashlib.sha256((git_show(root, args.rev, CITATION) or "").encode()).hexdigest()[:12] + "/" + hashlib.sha256((git_show(root, args.rev, DRIFT) or "").encode()).hexdigest()[:12]
-    fixture_sha = hashlib.sha256(open(os.path.join(os.path.abspath(root), "tests/fixtures/r39-citation-rev.py"), encoding="utf-8").read().encode()).hexdigest()[:12]
+    fixture_sha = hashlib.sha256(open(os.path.join(lane, "tests/fixtures/r39-citation-rev.py"), encoding="utf-8").read().encode()).hexdigest()[:12]
     try:
         base_scratch = tempfile.mkdtemp(
             prefix="souji-r39-c2.", dir=args.scratch or os.environ.get("TMPDIR") or "/var/tmp")
@@ -238,12 +245,10 @@
         leg("L4", new_ok and not old_ok, detail + " new_maps=%s old_maps=%s" % (new_ok, old_ok))
 
         # L5 — the new fixture discriminates.
-        fix_src = open(os.path.join(lane_root_of(args), "tests/fixtures/r39-citation-rev.py"), encoding="utf-8").read()
-        fix = os.path.join(base_scratch, "r39-citation-rev.py")
-        with open(fix, "w", encoding="utf-8") as handle:
-            handle.write(fix_src)
-        new_f = run_fixture(fix, new_cit, base_scratch, base_scratch)
-        old_f = run_fixture(fix, old_cit, base_scratch, base_scratch)
+        new_f = run_fixture(lane, "tests/fixtures/r39-citation-rev.py", "r39-citation-rev.py",
+                            new_cit, base_scratch)
+        old_f = run_fixture(lane, "tests/fixtures/r39-citation-rev.py", "r39-citation-rev.py",
+                            old_cit, base_scratch)
         ok = (
             new_f is not None and new_f[0] == 8 and new_f[2] == 0 and new_f[3] == 0
             and old_f is not None and old_f[2] >= 2
@@ -253,15 +258,11 @@
         # L6 — consumers green, none harmed against base.
         consumer_ok = True
         details = []
-        for name, path, tool_key, flag in CONSUMERS:
-            src = open(os.path.join(lane_root_of(args), path), encoding="utf-8").read()
-            fixp = os.path.join(base_scratch, name + ".py")
-            with open(fixp, "w", encoding="utf-8") as handle:
-                handle.write(src)
+        for name, path, tool_key in CONSUMERS:
             new_tool = new_drift if tool_key == DRIFT else new_cit
             old_tool = old_drift if tool_key == DRIFT else old_cit
-            new_r = run_fixture(fixp, new_tool, base_scratch, base_scratch, extra=[flag, new_tool])
-            old_r = run_fixture(fixp, old_tool, base_scratch, base_scratch, extra=[flag, old_tool])
+            new_r = run_fixture(lane, path, name + ".py", new_tool, base_scratch)
+            old_r = run_fixture(lane, path, name + ".py", old_tool, base_scratch)
             if new_r is None or old_r is None:
                 consumer_ok = False
                 details.append("%s=NO-SUMMARY" % name)
```

## 5. Observations for the L1 (not defects in my scope)

### 5.1 `fixture_sha` is not reproducible from the frozen receipts — expected, worth stating

`fixture_sha` hashes the *worktree* bytes of `tests/fixtures/r39-citation-rev.py`. Measured shas:

```
$ git show b769bfb84a264d8b284c09bc211d99f39a3e9126:tests/fixtures/r39-citation-rev.py | sha256sum | cut -c1-12
c142c1bc28b8      <- c2-before.txt
$ git show bbd9b97:tests/fixtures/r39-citation-rev.py | sha256sum | cut -c1-12
7ab7c3d85a81      <- c2-after.txt
$ git show d4c17557b92fd98044e4c8f0ddc79c6d75701b15:tests/fixtures/r39-citation-rev.py | sha256sum | cut -c1-12   (== worktree == 5230a34)
e555d8281484
$ git show ed30b7f5b77939c9073348d810730bc4f355708d:tests/fixtures/r39-citation-rev.py
fatal: path 'tests/fixtures/r39-citation-rev.py' exists on disk, but not in 'ed30b7f5b77939c9073348d810730bc4f355708d'
```

So `c2-before.txt` records the freeze-commit instrument bytes and `c2-after.txt` the C2-landing
instrument bytes; a re-run today prints `e555d8281484` because the fixture was revised again by
`d4c1755`. Consequence for the base-arm control: today's base run prints
`LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)` where the receipt has `new=(8, 5, 3, 1)` — same
verdict (FAIL), different case split, because L5's "old" arm is now the revised instrument. The
audited-tool side is stable (`tool_sha=56866ea8f832/14e9c0f77d7e` matches the receipt exactly). If
the L1 wants the receipt to be re-runnable, the re-run needs the instrument pinned by rev rather
than read from the worktree — but that is a design change to a frozen predicate, not a YAGNI cut,
so it is reported, not proposed.

### 5.2 The `harm` field cannot fail a run on its own

Restated for the record: `harm > 0 ⇒ fail > 0` at both increment sites, so `harm=0` on a
`fail=0` summary is structural, and `harm=1` always co-occurs with a failing leg. §3.2/§3.3 build
on this.

## 6. Verdicts

| check | command | verdict |
|---|---|---|
| reviewed bytes are committed | `git status --porcelain` / `sha256sum` / `git log -- <file>` | PASS — `732b1e42…` at `5230a34` |
| base arm unchanged, original bytes | §1.2 | PASS — `legs=6 pass=2 fail=4 harm=0`, exit 1 |
| HEAD arm unchanged, original bytes | §1.3 | PASS — `legs=6 pass=6 fail=0 harm=0`, exit 0 |
| proposal at base arm | §1.4 | PASS — `diff -q` identical (legs, summary, exit code) |
| proposal at HEAD arm | §1.4 | PASS — `diff -q` identical |
| proposal on the harm-exercising arm | §1.4/§1.7 | PASS — identical, `harm=1` preserved |
| proposal compiles | §1.5 | PASS — `py_compile rc: 0` |
| §4 patch applies to the current bytes | §1.6 | PASS — `patch rc: 0`, patched sha256 == proposal sha256 `7217c9dd…` |
| F1–F5 keep | §2 | KEEP — all measured identical |
| harm constant / delete | §3.2 | REFUSED — measured `harm=1` → `harm=0` |
| drop `and harm == 0` | §3.3 | REFUSED — dead today, sole future guard |
| shared `stage()` helper | §3.4 | REFUSED — second convention, no net removal |
| lane bytes written by this seat | `git status --porcelain` | NONE — advisory only |

No leg verdict changes under the proposal, so nothing had to be refused on that ground; the
refusals in §3 are grounded in evidence loss and convention cost instead.

## 7. Scratch

Scratch root used: `/fast/scratch/hyaku/souji-r39/W1SimpC2/` (proposal `c2-min.py`, variant
`c2-constharm.py`, the `harm-demo.b8ylbjkc` fixture repo, and per-arm `TMPDIR` dirs). It is
removed after this report is written; the durable form of the proposal is the verbatim patch in
§4, so nothing in this report depends on a scratch path surviving.
