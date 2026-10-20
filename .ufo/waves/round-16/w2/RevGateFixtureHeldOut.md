# RevGateFixtureHeldOut — R16 W2 falsification (source-only)

Artifact: `tests/fixtures/r16-landing-gate.py`
- 530 lines, sha256 `aae67c9c7bafd86f1b745193ac4aead74b3a3403b5c5ade33991d246e6413f2f`
- `git show a6ec781:tests/fixtures/r16-landing-gate.py` hashes identically; no diff vs HEAD.
- `python3 -m py_compile` clean.

Gate under test: `tools/souji-landing-gate.py`
- 1005 lines, sha256 `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`
- `git show a6ec781:tools/souji-landing-gate.py` hashes identically.

Method: source-only. This item carries no `ALLOWED-EXEC`, so I did not execute the fixture, the gate, or either selftest. Behavioural claims below that are not directly observed are marked **[INFERENCE]**; each follows deterministically from the cited lines.

## Q1 — are the held-out cases independent of the gate's own selftest? Verdict: HOLDS

Structural independence (not just "different names"):

1. **No shared code path in the fixture's construction.** The fixture never imports the gate; it executes it as a subprocess (`Gate.run`, fixture:146-161). Its repos come from its own `Repo` class (fixture:108-135), its own `SKILL_TMPL` (fixture:80-83), and inline `expected.json`/`record.json` literals. The gate's selftest builders (`_base_files`, `_frozen_world`, `_mkrepo`, `_write_file`) at gate:695-747 are not referenced anywhere in the fixture.
2. **Different synthetic world.** Selftest uses round 16 and `tests/fixtures/r9-frozen/`; the fixture uses round 77 (`ROUND = 77`, fixture:67, chosen to never collide with real wave dirs) and three different frozen-dir names. A regression that hard-codes either world fails the other.
3. **The fixture tests the process contract the selftest never touches.** The selftest calls `evaluate()` in-process and inspects `res["findings"]` (gate:766-779). The fixture asserts exit codes, TSV row shape (`ID\tpath\tdetail`), and `SUMMARY` text via the CLI (`evaluate`, fixture:176-193). Row-level `path` attribution is therefore testable only here.
4. **Nine of fourteen substantive cases are not copies of a selftest case** — two reuse a finding class with new defect constructs (unterminated `case`; `TabError`/module-level `return`), the rest add behaviour the selftest never exercises. Mapping (fixture case line → selftest analog → relation):

| fixture case | selftest analog | relation |
|---|---|---|
| `replay-b410186` (229) | none | held out: real lane history at an immutable rev |
| `unterminated-case` (248) | `nonparsing-cited-sh` | new defect construct (EOF inside `case`, not missing `fi`) |
| `py-compile-defects` (262) | `nonparsing-cited-py` | new classes: tab/space `IndentationError`, module-level `return` |
| `truncated-heredoc` (277) | none | held out: `bash -n` **rc 0 + stderr** path (see Q2 note) |
| `missing-reg-and-changed` / `uncited-nobase-invisible` (293,300) | 3 selftest cases | behavioural overlap; new repo shape + per-path `absent` |
| `pin-only-inside-frozen-dir` (333) | `pin-missing-file` | held out: **inverse** direction — root-prefixed key present only inside the frozen dir; selftest only tests a non-root key absent inside it |
| `pin-vs-measured-commit` (356) | `frozen-measured` | overlap class, new construction (pin matches REV, measured is an ancestor) |
| `marker-one-char-off` (378) | none | held out: near-miss carry (`journal`→`jouxrnal`) |
| `marker-rewordings` (406) | `fenced-and-table-ignored` | held out: decoration/colonless/heading/blockquote; fence+table now on **STATUS** lines |
| `carry-inside-html-comment` (427) | none | held out: `HTML_COMMENT_RE` is never exercised by the selftest |
| `open-marker-admitted-true` (443) | `open-admitted` | behavioural overlap |
| `missing-wave-dir` (453) | `no-wave-dir-exit2` | behavioural overlap |
| `clean-all-green` (485) | `clean-pass` | overlap in intent; adds `--base`, a dir-local pin key, and per-id absence for all seven ids |
| `vacuity-stub` (517) | none | held out: CLI-level silence check |

Residual coupling (honest caveat, not a defect): both suites drive the same `evaluate()`/`check_*` implementation, so a bug in shared plumbing passes both. That is unavoidable for any test of this gate; it does not reduce the construction-level independence above.

Verified premise for the one case that depends on external tool semantics: `printf '#!/bin/sh\ncat <<EOF\nline one\nline two\n' | bash -n` → **rc=0** with `warning: here-document ... delimited by end-of-file` on stderr. So fixture case 4 (`truncated-heredoc`, 277-279) is genuinely the stderr-only path and is not a duplicate of case 2; the gate treats any stderr as a failure (gate:192-211), so the case is live.

## Q2 — is the vacuity guard real? Verdict: PARTIAL

What it does prove: a `.py` tool that exits 0 and prints nothing is classified `vacuous` (fixture:510-511) and the replay assertion triple fails against it (fixture:504-509), so the case's verdict is `PASS` (fixture:512). The guard is not decorative.

What it does **not** prove — the exit-code comparison dominates the verdict (static trace, **[INFERENCE]**):

- `evaluate(..., exp_rc=1, ...)` appends a failure at fixture:180-182 whenever `returncode != 1`. The stub exits 0, so `fails` is already non-empty and `ok is False` **before** either `need` loop can matter.
- Therefore `not ok` at fixture:512 is guaranteed by the rc assertion alone. If the `need` loop were disabled (e.g. `if False:` at fixture:183-185), or `has()` were made to always return True for the `need` path, the vacuity case would **still** print PASS. That is exactly the regression class a vacuity guard exists to catch.
- Concrete consequence: the five `absent`-free cases (3, 4, 10, 11, 12) would be satisfied by a gate that silently dropped one of their required findings once the `need` loop is dead, and this guard would not notice.

Smallest fix (two tokens, plus the docstring sentence at line 41): make the stub exit with the *expected* code so the only remaining failure source is the row content.

```diff
@@ fixture:41
- 3. vacuity guard: a --tool that exits 0 printing nothing must fail this
-    fixture (proven in-fixture by evaluating the same assertions against the
-    stub's empty output).
+ 3. vacuity guard: a --tool that prints nothing must fail this fixture's
+    replay assertions at the expected exit code (proven in-fixture by
+    evaluating the same assertions against the stub's empty output).
@@ fixture:501-511
         with open(stub, "w") as f:
-            f.write("import sys\nsys.exit(0)\n")
+            f.write("import sys\nsys.exit(1)\n")
         stub_proc = gate.run(LANE, REPLAY_REV, REPLAY_ROUND, tool=stub)
@@
-        vacuous = (stub_proc.returncode == 0
+        vacuous = (stub_proc.returncode == 1
                    and not stub_proc.stdout.strip())
```

(Equally acceptable and preserving the current sentence: keep the rc-0 stub and add a second `silent-tool.py` with `sys.exit(1)`, requiring both evaluations to fail. The rc-1-only version is the smaller change.)

## Findings (severity order)

### F1 [Moderate] Vacuity guard is exit-code-confounded — it cannot detect dead `need` assertions
`tests/fixtures/r16-landing-gate.py:502` (`sys.exit(0)`), `:510-512` (`vacuous`/`passed`), `:180-182` (rc dominates `fails`).
Counterexample: replace `evaluate`'s `need` loop with `pass`; the fixture still reports `CASE vacuity-stub PASS` and cases 3, 4, 10, 11, 12 still pass against the real gate, so nothing signals that required rows are no longer checked.
Fix: the diff in Q2 above (stub exits 1, `vacuous` tests rc 1). The case now PASSes only if the row checks actually reject empty output — with the stub, all three `need` checks fail; a dead `need` loop or a `has` that always matches makes `ok` True and reds the case. (A single dead needle among the three would still be masked, so the guard is a floor, not a proof of each assertion.)

### F2 [Moderate] Fixture's contract header states the **superseded** failure-channel rule, contradicting its own case 9 and the gate
`tests/fixtures/r16-landing-gate.py:22-23`: "…whose first word is outside the benign allowlist, plus parse/do-not-ship/snapshot_tampered phrase markers…". The gate implements the opposite, narrower rule: first value word ∈ `FAILURE_STATUS_WORDS` (gate:71-78, matched at gate:270), and phrase markers were explicitly **dropped** (gate:62-70: "any non-benign first word … free-text phrase markers … all quotations of the round-15 failure"). Case 9 asserts the drop: SeatC "The file in tree doesn't parse." and SeatD "note: do not ship this" must produce no finding (fixture:394-395, 412-415). Read literally, the header says those two must fire.
Second-order defect: **no assertion distinguishes the two rules.** The only negative control is the clean case (`absent` on all ids, fixture:488-494), and its benign STATUS lines use `ok`/`none`/`clean`/`done`/`pass`, which any allowlist draft would also treat as benign; the replay case (fixture:229-235) has no `absent` list, so extra `LG-SEAT-UNCARRIED` rows there would not fail it. The vocabulary boundary is therefore unpinned **[INFERENCE]**.
Fix:
```diff
@@ fixture:22-23
-word is outside the benign allowlist, plus parse/do-not-ship/snapshot_tampered
-phrase markers outside ``` fences and table rows, not carried verbatim under
+word is in the pinned failure vocabulary (incomplete/fail/blocked/broken/
+partial/... — not a benign-allowlist complement) outside ``` fences and table
+rows, not carried verbatim under
```
Optionally change line 38 to "reworded/decorated STATUS and phrase markers that must **not** fire" so the case list cannot be misread. To pin the boundary, add one line to the clean repo (fixture:464): `"Notes.md": "# notes\n\nSTATUS: none\n\nSTATUS: defect — diagnostic note\n"` — `defect` is outside the closed vocabulary, so the clean case (`findings=0`) now forces the vocabulary rule and reds out under the header's old rule.

### F3 [Moderate] `has()` is disjunctive, so composite `need` tuples assert less than they read; one needle is inert
`tests/fixtures/r16-landing-gate.py:171` (`any(a in ln for a in alts)`), used by `need` at `:183-185`.
Two affected `need` entries:
- `:232-233` `("LG-FROZEN-PIN", ("tools/souji-census.sh", "r15-preservation-frozen"))` passes on a row that mentions only the census path. It does not prove the finding is attributed to `tests/fixtures/r15-preservation-frozen/expected.json`, which the comment at fixture:31-32 claims.
- `:445-446` `("LG-OPEN-ADMITTED", ("SeatA", "round-77", "Seat-reported"))` passes on the path alone (`.ufo/waves/round-77/w1/SeatA.md` contains "SeatA" and "round-77"). "Seat-reported" never appears in the finding: gate:341 emits `line N: <marker>` and gate:353 appends `carried open while lesson declares admitted: true`, and the row's path is `.ufo/waves/round-77/w1/SeatA.md`. The third needle is therefore unsatisfiable and currently masked by `any` **[INFERENCE]**.
Note: `absent` genuinely *needs* disjunction ("no row mentions ok.sh **or** ok.py"), so the fix must be scoped to `need`, not applied to `has` globally.
Fix:
```diff
@@ fixture:168-173
-def has(rows, fid, *alts):
+def has(rows, fid, *alts, match_all=False):
     for ln in rows:
         head = ln.split("\t", 1)[0]
-        if head == fid and any(a in ln for a in alts):
-            return True
+        if head == fid:
+            pick = all if match_all else any
+            if pick(a in ln for a in alts):
+                return True
     return False
@@ fixture:183-185
     for fid, alts in need:
-        if not has(rows, fid, *alts):
+        if not has(rows, fid, *alts, match_all=True):
             fails.append("missing %s ~ %s" % (fid, "/".join(alts)))
@@ fixture:445-446
              need=[("LG-OPEN-ADMITTED",
-                    ("SeatA", "round-%d" % ROUND, "Seat-reported"))])
+                    ("SeatA", "round-%d" % ROUND, "admitted: true"))])
```
The replay PIN tuple (232-233) already has both needles in the same row (path = `tests/fixtures/r15-preservation-frozen/expected.json`, detail = `files[tools/souji-census.sh] …`), so it stays green under conjunctions; the case-11 tuple stays green because gate:353 supplies "admitted: true".

### F4 [Minor] Case 6 under-pins its finding *set*: the gate emits two ids for the pin, and the case blesses either answer
`tests/fixtures/r16-landing-gate.py:330-336` says "this must be LG-FROZEN-PIN", but `absent` only denies `notes.txt`. Static trace **[INFERENCE]**: `record.json` sets `measured_commit = c1` (fixture:317), and at `c1` the root-relative path `tools/pinned.sh` does not exist (the blob lives only inside the frozen dir, fixture:314); gate:457-489 walks every `files` key at `measured_commit` and therefore also emits `LG-FROZEN-MEASURED files[tools/pinned.sh] absent at measured_commit <c1>`. Two findings, exit 1 — the case passes.
Fix, if both findings are intended (matches today's gate):
```diff
@@ fixture:335-336
-             need=[("LG-FROZEN-PIN", ("tools/pinned.sh",))],
+             need=[("LG-FROZEN-PIN", ("tools/pinned.sh",)),
+                   ("LG-FROZEN-MEASURED", ("tools/pinned.sh",))],
              absent=[("LG-FROZEN-PIN", ("notes.txt",))])
```
If one finding per unsatisfiable pin is intended instead, replace the added `need` with `absent=[("LG-FROZEN-MEASURED", ("tools/pinned.sh",))]` **and** add dedupe in `check_frozen_pins`; that option requires a gate change.

### F5 [Minor] `SUMMARY` counters are never validated
Only `findings=0` (fixture:487) and the bare presence of `checked_reports=` (fixture:235) are asserted; `checked_reg`, `checked_pins`, and `checked_markers` could print any value in every case. The clean repo makes two of them deterministic from the fixture's own tree (two wave `*.md` reports at fixture:462-465; one failure-channel marker, SeatA's `INCOMPLETE`; `Notes.md` is benign).
Fix (requires F3's all-match `need`, otherwise OR weakens it):
```diff
@@ fixture:487
-             need=[("SUMMARY", ("findings=0",))],
+             need=[("SUMMARY", ("findings=0", "checked_reports=2",
+                                "checked_markers=1"))],
```
Leave `checked_reg`/`checked_pins` unpinned on purpose: their values depend on counting policy (base-diff arm and the measured-commit loop), not solely on the fixture's tree.

### F6 [Minor] Case 8 comment claims a resolvability check the gate does not perform
`tests/fixtures/r16-landing-gate.py:372` — "a resolved@ disposition pointing at a real ancestor commit". The gate only pattern-matches the token: `CARRY_TOKEN_RE = … resolved@[0-9a-f]{7,}` (gate:83) at gate:338; there is no `rev-parse`/ancestry test in `check_carry` (gate:307-356). A lesson line ending `resolved@deadbee` would be accepted exactly the same.
Fix (comment only; the contract documents shape, not resolvability):
```diff
@@ fixture:372
-        # a resolved@ disposition pointing at a real ancestor commit.
+        # a resolved@<7+ hex> disposition; the gate checks the token shape
+        # only (tools/souji-landing-gate.py:83) and does not resolve it.
```
If resolvability *should* be part of the contract, that is a gate change plus a new seat/lesson pair with an unresolvable 7-hex token; do not encode it in this fixture unilaterally.

### F7 [Minor] Prerequisite rejects a linked worktree (`.git` file)
`tests/fixtures/r16-landing-gate.py:207-208` treats `os.path.isdir(LANE/.git)` as the definition of "git worktree". In a linked worktree or submodule `.git` is a file; the fixture then reports `PREREQ FAIL — lane root is not a git worktree` and exits 2, i.e. "could not evaluate" rather than running. `.git` is a directory in this clone today, so this is latent, but the lane is explicitly worktree-oriented tooling.
Fix:
```diff
@@ fixture:207-208
-    if not os.path.isdir(os.path.join(LANE, ".git")):
+    if subprocess.run(["git", "-C", LANE, "rev-parse", "--git-dir"],
+                      stdout=subprocess.DEVNULL,
+                      stderr=subprocess.DEVNULL).returncode != 0:
         prereq.append("lane root is not a git worktree: %s" % LANE)
```

### F8 [Minor] A contract clause is unprotected: verbatim carry *without* an `open`/`resolved@` token
Header (fixture:23-25) and gate:338 both require the lesson line to carry a disposition token. No case in either suite exercises a verbatim carry that lacks one: selftest `carried-open`/`carried-resolved` both have tokens; fixture case 8's lesson line has `— open` but differs from the seat line by a character; case 13 uses `resolved@`. Deleting `and CARRY_TOKEN_RE.search(nl)` at gate:338 leaves **both** suites green **[INFERENCE]** from the case inventory.
Fix — add after fixture:381:
```python
        # --- Case 8b: verbatim carry without a disposition token ------------
        r = Repo(scratch, "notoken")
        r.write("SKILL.md", SKILL_TMPL.format(cited="tools/ok.sh"))
        r.write("tools/ok.sh", "#!/bin/sh\necho ok\n")
        r.waves({"SeatA.md":
                 "# seat\n\nSTATUS: INCOMPLETE — copied without disposition\n"})
        r.lesson(["STATUS: INCOMPLETE — copied without disposition"])
        rev = r.commit("carry without token")
        case("carry-verbatim-no-token",
             gate.run(r.path, rev, ROUND), 1,
             need=[("LG-SEAT-UNCARRIED", ("SeatA",))])
```

## Residual risk and verification gaps

- **Not executed.** No `ALLOWED-EXEC` on this item; the fixture, the gate, both selftests, and the replay were not run. `15/15` and `18/18` are unverified by me and are **not** recorded in `census/round-16/c1-matrix-landing.json` (that file records the census arms only). Every behavioural claim above is a static trace of cited lines.
- Both suites drive one implementation, so shared-plumbing bugs are structurally invisible to the pair. The fixture does not add an independent oracle for `evaluate()`; it adds independent constructions.
- CLI exit-2 paths other than missing wave dir are untested externally: `bad-rev` and `no-skill` exist only in the selftest, at `evaluate()` level (gate:941-966), not through `main`/`emit`. The `--json` path and its refuse-overwrite rule (gate:611-614) are untested by either suite.
- The replay is pinned to immutable `b410186` (round 15) and to `tools/souji-census.sh` / `tests/fixtures/r15-preservation-frozen`; it is sound today (`git show b410186:…/expected.json` pins `tools/souji-census.sh` at `b51873…`; `ConfigRepair.md` line 7 is `## STATUS: INCOMPLETE — file has an unresolved syntax error`) but couples the fixture to lane history by design.
- Fixture scratch lives under `/var/tmp` and is removed by `finally` (fixture:521-522); a hard kill leaves the directory behind. Cosmetic.
- Gate-side robustness note (not this fixture's defect): the fixture hardens its own git calls with `GIT_CONFIG_NOSYSTEM`/`HOME` (fixture:69-78), but the gate's own `git` calls inherit the ambient environment (gate:116-130) and do not neutralize global config/hooks the way `tools/souji-census.sh` does. A hostile global config is out of scope for this item but would sit outside this fixture's net.

STATUS: ok
Verdicts: Q1 independence = holds; Q2 vacuity guard = partial (exit-code-confounded; fix is two tokens). No blocker; eight advisory findings, none of which changes the fixture's current pass/fail outcome.

## Commands

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain | head -50 && ls tests/fixtures/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tests/fixtures/r16-landing-gate.py tools/souji-landing-gate.py && sha256sum tests/fixtures/r16-landing-gate.py tools/souji-landing-gate.py tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "def \|selftest\|SELFTEST\|argparse\|add_argument" tools/souji-landing-gate.py | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -8 -- tests/fixtures/r16-landing-gate.py tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "benign allowlist\|phrase markers\|def has\|any(a in ln\|vacuity\|empty-tool\|stub_proc\|vacuous\|results.append\|def evaluate\|need/absent" tests/fixtures/r16-landing-gate.py
printf '#!/bin/sh\ncat <<EOF\nline one\nline two\n' | bash -n; echo "rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -m py_compile tests/fixtures/r16-landing-gate.py && echo COMPILE_OK; test -d .git && echo "git=dir" || echo "git=file"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json
spec=json.load(open('.ufo/waves/round-16/w2-spec.json'))
def walk(o,p=''):
    if isinstance(o,dict):
        s=json.dumps(o)
        if 'RevGateFixtureHeldOut' in s:
            for k,v in o.items():
                if 'RevGateFixtureHeldOut' in json.dumps(v):
                    print(p+'/'+k)
                    walk(v,p+'/'+k)
                elif isinstance(v,(dict,list)):
                    pass
            if 'RevGateFixtureHeldOut' in json.dumps(o) and not any(isinstance(v,(dict,list)) for v in o.values()):
                print(p, json.dumps(o, indent=1)[:2000])
    elif isinstance(o,list):
        for i,v in enumerate(o):
            walk(v,p+'/%d'%i)
walk(spec)
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show a6ec781:tests/fixtures/r16-landing-gate.py | sha256sum && git show a6ec781:tools/souji-landing-gate.py | sha256sum && git diff --stat HEAD -- tests/fixtures/r16-landing-gate.py tools/souji-landing-gate.py; echo "diff_rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
s=json.load(open('.ufo/waves/round-16/w2-spec.json'))
it=s['items'][37]
print(it.get('name'))
print('---')
for k,v in it.items():
    if k!='name': print(k+':', v)
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '14,48p;164,190p' tests/fixtures/r16-landing-gate.py | cat -n | head -70
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "pin-only-inside-frozen-dir\|pin-vs-measured-commit\|one-char-off\|real ancestor\|marker-one-char-off\|open-marker-admitted-true\|clean-all-green\|resolved@%s\|absent=\[\|need=\[" tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
for p in ['census/round-16/c1-matrix-landing.json','census/round-16/c1-matrix-final.json']:
    try: d=json.load(open(p))
    except Exception as e: print(p,'ERR',e); continue
    s=json.dumps(d)
    import re
    print(p, 'len', len(s))
    def walk(o,path=''):
        if isinstance(o,dict):
            for k,v in o.items(): walk(v,path+'/'+str(k))
        elif isinstance(o,list):
            for i,v in enumerate(o): walk(v,path+'/%d'%i)
        else:
            if isinstance(o,str) and 'r16-landing-gate' in o: print(path,'=',o[:200])
            if isinstance(o,(int,float)) and ('fixture' in path.lower() or 'held' in path.lower()): print(path,'=',o)
    walk(d)
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log -1 --format='%H %s' b410186 && echo '--- expected.json ---' && git show b410186:tests/fixtures/r15-preservation-frozen/expected.json && echo '--- ConfigRepair 1-9 ---' && git show b410186:.ufo/waves/round-15/w1/ConfigRepair.md | sed -n '1,9p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix-landing.json'))
print(type(d), list(d)[:20] if isinstance(d,dict) else len(d))
print(json.dumps(d, indent=1)[:2500])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "isdir(os.path.join(LANE\|lane root is not a git worktree\|r15-preservation-frozen\|ConfigRepair.md\|checked_reports=" tests/fixtures/r16-landing-gate.py; echo '--- gate ---'; grep -n "CARRY_TOKEN_RE\|absent at measured_commit\|carried open while" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "STATUS_PREFIX_RE\|FAILURE_STATUS_WORDS\|^    {$" tools/souji-landing-gate.py | sed -n '1,6p'; sed -n '56,74p' tools/souji-landing-gate.py | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -B2 -A3 "real ancestor" tests/fixtures/r16-landing-gate.py; echo ---; grep -n "Notes.md" tests/fixtures/r16-landing-gate.py; echo ---; sed -n '484,490p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^        # --- Case\|^        case("\|^        results.append(("vacuity' tests/fixtures/r16-landing-gate.py
```
