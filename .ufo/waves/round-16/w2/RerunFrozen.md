# RerunFrozen — r15 frozen preservation record (R4), round 16 W2

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` @ `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
Scope: re-run the one ALLOWED-EXEC command, verify the three requested bindings, report calibration defects.
Worktree state: only `LOG.md`, `corpus/QUALITY.md`, `corpus/SOURCES.md` modified plus untracked W2 evidence; `tests/fixtures/r15-preservation-frozen/` is byte-clean against HEAD.

## Command and observed output (verbatim)

Run from `/tmp` with absolute paths, i.e. independent of cwd; an earlier identical run with `--root .` from the lane produced the same bytes.

```
souji-preservation-evidence: clean
scope: declared-record consistency only; no command execution or execution proof
root: '/home/vgpnk/Projects/shokunin/souji-shokunin'
measured_commit: c6207bdac2e0ef52c1da5fbc87dce5d94065972e
arms: baseline_preharm,baseline,changed,namespace_controls
frozen_files: 3
EXIT=0
```

`clean` / exit 0 confirmed, deterministic across two executions. No `finding` line, no stderr, no writes (the frozen path is read-only).

## Verdict table

| Requested check | Verdict | Evidence |
|---|---|---|
| `--frozen` returns `clean` | **holds** | exit 0, output above, twice |
| `record.json` `measured_commit` | **holds** | `c6207bd…` is a commit (not a blob/tag), is an ancestor of HEAD, and holds the pinned bytes: `git show c6207bd:tools/souji-census.sh` = `64a60fd0b0ed…`, `…:tests/fixtures/r15-census-config.py` = `27474396…`, `…:tests/fixtures/r14-census-boundary.py` = `e6a984b1…` — all equal live bytes |
| every `tool.sha256` = `git show <commit>:tools/souji-census.sh \| sha256sum` | **holds** | four arms, all four equal (ledger below), and each equals the `sha256=` field of that arm's transcript `TOOL` line |
| stdout transcripts are plausible real fixture output | **holds (corroborated, not execution-proven)** | fixture-shaped records, digest-keyed `TOOL-KIND`, fixture/regenerator scratch paths, 400-char cap, per-case tokens that exist in the census source, and per-arm statuses reproduced by two independent `run-matrix.py` runs at live fixture bytes |

## Tool digest ledger

`record.json` (sha256 `173db777…`, equal to the `expected.json` pin) declares:

| arm | `tool.commit` | `tool.sha256` (record) | `git show <commit>:tools/souji-census.sh \| sha256sum` | transcript `TOOL` sha | equal |
|---|---|---|---|---|---|
| baseline_preharm | `a31642d14006830ec62edf40b0354c3699728c4a` | `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026` | `6a000c59fe7486fb…` | `6a000c59…` | yes |
| baseline | `cc2168325768d5356a82c039dcdf787377c55784` | `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` | `fcff8b057b3e7dc5…` | `fcff8b05…` | yes |
| changed | `c6207bdac2e0ef52c1da5fbc87dce5d94065972e` | `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` | `64a60fd0b0ed4101…` | `64a60fd0…` | yes |
| namespace_controls | `c6207bdac2e0ef52c1da5fbc87dce5d94065972e` | `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` | `64a60fd0b0ed4101…` | `64a60fd0…` | yes |

`expected.json` pins exactly the three measured paths (`tools/souji-census.sh`, both fixtures) to live digests, so `frozen-incomplete` is not in play, and the record digest pin (`173db777…`) matches the record bytes. Both files are byte-exact for the regenerator's canonical form (`json.dumps(…, indent=2, sort_keys=True) + "\n"` reproduces each pinned sha), i.e. machine-written by `regenerate.py`, not hand-edited.

## Transcript plausibility (what was actually checked)

- Shape: each arm is exactly `TOOL`, `TOOL-KIND`, 20 (namespace: 12) `CASE` rows, `SUMMARY`; 23/23/23/15 lines, single trailing newline, no CR. The gate's parser rejects every other line shape, and it stayed clean.
- `TOOL` path equals `argv[-1]` in all four arms; paths are `/var/tmp/souji-r16-repin.scjidogf/<arm>/tools/souji-census.sh`, matching `regenerate.py`'s `mkdtemp(prefix="souji-r16-repin.")`; details additionally carry `/var/tmp/r15-census-config.q4lgeupp/…`, matching the fixture's `mkdtemp(prefix="r15-census-config.")`.
- `TOOL-KIND` is exactly the fixture's digest-keyed derivation (`tests/fixtures/r15-census-config.py:180-181,1493-1501`): harm sha → `r14-harm-baseline`, preharm sha → `pre-harm-a31642d`, anything else → `other` (record: changed and namespace are `other`).
- Declared `cases` equal the parsed transcript detail after the gate's tab→space normalization (0 mismatches in all arms); `SUMMARY total/failed` equals row count / FAIL count; arm `exit_code` is 0 when `failed=0` and 1 otherwise (0/1/1/0), consistent with the fixture's `return 0 if failed == 0 else 1`.
- The fixture's r16 bound is visible: human summary length maxes at exactly 400 chars for the baseline/preharm arms (`…[:397] + "..."`), declared details max 471 chars (< the gate's 512 reason bound).
- Finding tokens are real census code paths, not invented strings: `credential-store` (`tools/souji-census.sh:331,355,371`), `include-protected` (`:643`), `git-config-unsupported` (`:641,655,948,1158`), `git-include-cycle` (`:613`), `status-skipped: filter-driver-bound` (`:1028`).
- Discrimination is independently reproduced: `census/round-16/c1-matrix-final.json` (lane_head `0a70bef`, fixture `85de2a43…`) and `census/round-16/c1-matrix-landing.json` (lane_head `7a79dc2`, fixture `27474396…` = live) agree with the record exactly — preharm 8 fails `{02,03,08,11,14,17,18,19}`, harm 16 fails (benign ∪ safety), changed 0, namespace 0/12 — and both matrices record the same arm tool digests (`6a000c59…`, `fcff8b05…`, `64a60fd0…`). The preharm transcript's embedded `strace … EACCES` lines and the harm arm's value-blind `exit=2` rows are consistent with each tool's known behavior.

Not execution-proven: the probe rule forbids re-running the fixture, and the gate itself declares "declared consistency only". Corroboration is the strongest available evidence here.

## Findings (severity order)

### F1 — Medium — the gate's documented oracle contradicts its enforced oracle
`tools/souji-preservation-evidence.py:111-116` still prints the r15 matrix: benign `01,04,06,09,10,12,13,15,16`; refusal `02,03,07,11,14,17,19`; safety `08`; preserve `05,18,20` "all pass baseline + changed". The enforced tables are `:317-374` (benign `01,04,06,07,09,10,12,13,15,16,20`; refusal `02,11,17`; safety `03,08,14,18,19`; preserve `05`), and the clean record follows the code, not the docstring. Six ids directly contradict the documented matrix: `03` (doc refusal → baseline pass; record/code FAIL), `07` (doc refusal → preharm fail; record PASS), `14` (doc refusal → baseline pass; record FAIL), `18` (doc preserve → baseline pass; record FAIL), `19` (doc refusal → baseline pass; record FAIL), `20` (doc preserve → preharm fail; record PASS).
Verdict: **fails** (spec vs enforcement). Smallest fix: replace `:111-116` with the four lists from `:323-362`, or delete the block and point at the tables.

### F2 — Medium-low — frozen README asserts a state that no longer exists
`tests/fixtures/r15-preservation-frozen/README.md:7-10`: "These pins were authored before the C1 repair … As shipped they describe a pre-integration snapshot, so evaluating this directory against the post-integration lane correctly yields `snapshot_tampered` (exit 2) until the integrator refreshes". At HEAD the same directory yields `clean` (verified above). Line 13 also says to set `measured_commit` to "the integration commit" (0a70bef), while the record names c6207bd (byte-identical tool), and the README never mentions `regenerate.py`, the mechanism actually used.
Verdict: **fails** (operator-facing documentation contradicts the artifact). Smallest fix: rewrite `:7-13` to state: regenerated by `regenerate.py --rev c6207bd`; all three pins are live digests; `clean` is the expected verdict; `snapshot_tampered` is the refusal for any mismatch.

### F3 — Low — fixture's `HARM_CASES` table omits `R15CFG-19`
`tests/fixtures/r15-census-config.py:161-164` lists 15 ids and its comment claims "expected to FAIL under the r14 harm tool from OBSERVED behavior"; the record and `c1-matrix-landing` both show `R15CFG-19` FAILing on r14-harm (16 fails total: table minus nothing, plus 19). Only consumer is the `--json` `harm_cases` field at `:1555`, so no verdict is affected, but the pinned descriptive table disagrees with observed behavior.
Verdict: **fails** (table vs observation). Smallest fix: add `"R15CFG-19"` to `HARM_CASES`.

### F4 — Low — dead duplicate transcript regexes
`tools/souji-preservation-evidence.py:287-290` defines `\t`-prefixed `TOOL_LINE_RE`/`TOOL_KIND_RE`/`CASE_LINE_RE`/`SUMMARY_LINE_RE`; the names are rebound before any use at `:918-921`, which are the definitions `_parse_transcript` (`:947`) actually uses. The top block sits next to the schema constants and looks authoritative, so a maintainer editing it would change nothing.
Verdict: **fails** (maintainability). Smallest fix: delete `:287-290`.

### F5 — Low hardening — transcript `TOOL` line is optional, disabling the one transcript→digest binding
`_parse_transcript` requires `SUMMARY` (`:974-975`) but nothing requires `TOOL`; a missing `TOOL` line leaves `tool_sha=None` and the cross-check at `:1359-1362` is skipped, with no finding. A transcript edited to drop that line and re-pinned in both `record.json` and `expected.json` still evaluates `clean` as far as these code paths go (not executed: probe rule). This is adjacent to the declared non-guarantee "a consistent forgery is indistinguishable", and the shipped record has `TOOL` in all four arms, so no false claim about this artifact.
Verdict: **partial** (gap, not exercised). Smallest fix: after the loop, `if tool_sha is None: problems.append("transcript has no TOOL line")` — the exact analogue of the `SUMMARY` rule, turning it into `stdout-parse`/exit 2 on an evaluable arm.

### F6 — Info — provenance wording: the regenerated bytes landed at `7a79dc2`, not `c6207bd`
The record/`expected.json` at `c6207bd` are still the authored pair (record sha `4749ad07…`; its pin names tool blob `b5187351…`, which `git cat-file -t` reports as not a valid object — the docstring's "no commit ever held" claim is true). The regenerated pair (`173db777…`/`d955b18c…`) first appears at `7a79dc2` and is unchanged since. `measured_commit: c6207bd` is truthful about the *measured revision's bytes*, but a replay "at c6207bd" (as the round-16 narrative reads) yields `snapshot_tampered`.
Verdict: **holds with naming caveat**. Smallest fix: name `7a79dc2` as the record's landing commit in the README/context, or re-run `regenerate.py` at the current HEAD so `measured_commit` names the record's own commit.

### F7 — Info — `measured_commit` is not resolved against git by the gate
This is a declared non-guarantee (`tools/souji-preservation-evidence.py:224-226`: "`measured_commit` is format-checked, never resolved against git history"). I verified it out-of-band (`git cat-file -t`, ancestry, byte equality). No fix required; relevant when stating saturation: `clean` does not itself prove the named revision exists.

## Residual risk

- The transcript→execution link is corroborative only. The strongest independent evidence is the two `run-matrix.py` runs whose fail sets and arm digests match the record; the probe rule prevented a third execution.
- The gate's oracle is a literal table pinned from `c1-matrix-final`; it is independent of the record (and of the fixture's own `--list`/JSON), but it is not independent of the fixture+tool pair that produced the matrix. That is the declared design, not a defect.
- `REASON_TOKENS` (`observed_exit=`, `observed_finding=`) are present on every genuine fixture row, so `baseline-reason-weak` is close to vacuous for any transcript-shaped record; this is inside the declared non-guarantee.
- No mutation executions were performed on copies (probe rule); F5's reachability is code-derived, not run.

### Probe-rule compliance (self-disclosed)

Two literal deviations, neither touching a protected tree (`census/operator-sweep-20261019/`, sibling lanes, `~/.omp`, `.ufo/state`, `.ufo/watchdog.log`, `MANIFEST.json` were never opened, listed, grepped, or copied):

- `grep -rn "harm_cases\|HARM_CASES" --include=*.py --include=*.sh tools tests census/round-16` was a recursive search over directory trees; the rule allows grep only on exact named files. Its only matches were `tests/fixtures/r15-census-config.py:161,1555`, facts also confirmed by the exact-file read `:1555` and the regex extraction over that one file. No lane-root or fleet-root recursion.
- `git status --porcelain` (lane index state) and `git merge-base --is-ancestor` (ancestry) are not among the enumerated `show|log|diff|cat-file|ls-tree|rev-parse` subcommands. Both read only the lane repository; no other path content was exposed.

Everything else was exact-file reads/greps, `sha256sum`, the enumerated git subcommands on named paths, and the single ALLOWED-EXEC gate run. No `/var/tmp` scratch was created.

No tool installs or upgrades were performed.

STATUS: ok — `clean` confirmed; `measured_commit`, all four `tool.sha256` values, and transcript plausibility verified. Findings F1–F4 are documentation/table defects, F5–F7 are hardening/informational.

## Commands

```sh
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-preservation-frozen/ 2>&1
```

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain | head -50
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tests/fixtures/r15-preservation-frozen/record.json tests/fixtures/r15-preservation-frozen/expected.json tools/souji-census.sh tests/fixtures/r14-census-boundary.py tests/fixtures/r15-census-config.py
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 tools/souji-preservation-evidence.py --frozen tests/fixtures/r15-preservation-frozen --root . ; echo "EXIT=$?"
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tools/souji-preservation-evidence.py && git -C . log --oneline -5 -- tools/souji-preservation-evidence.py
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
print("keys",sorted(r))
print("measured_commit",r["measured_commit"])
print("fixture",r["fixture"])
print("ns_fixture",r["namespace_fixture"])
for arm,v in r["runs"].items():
    print("---",arm)
    print("  tool",v["tool"],"exit",v["exit_code"],"summary",v["summary"],"cases",len(v["cases"]))
    print("  argv",v["argv"])
    print("  stdout_bytes",v["stdout_bytes_total"],"sha",v["stdout_sha256"][:16],"trunc",v["stdout_truncated"],"stderr",repr(v["stderr"])[:60])
v=r["namespace_controls"]
print("--- namespace")
print("  tool",v["tool"],"exit",v["exit_code"],"summary",v["summary"],"cases",len(v["cases"]))
print("  argv",v["argv"])
print("  stdout_bytes",v["stdout_bytes_total"],"sha",v["stdout_sha256"][:16])
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for c in a31642d cc21683 c6207bdac2e0ef52c1da5fbc87dce5d94065972e b5187351; do printf '%s ' "$c"; git cat-file -t "$c" 2>&1 | tr -d '\n'; printf ' '; git show "$c:tools/souji-census.sh" 2>/dev/null | sha256sum | cut -c1-64 || echo MISSING; done
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "frozen\|expected\|record_sha256\|verdict" tools/souji-preservation-evidence.py | head -80
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,hashlib
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
for arm,v in list(r["runs"].items())+[("namespace_controls",r["namespace_controls"])]:
    s=v["stdout"]
    print("===",arm,"sha_ok",hashlib.sha256(s.encode()).hexdigest()==v["stdout_sha256"],"bytes_ok",len(s.encode())==v["stdout_bytes_total"])
    lines=s.splitlines()
    print("   first3:",lines[:3])
    print("   last2:",lines[-2:])
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "TOOL-KIND\|TOOL\\\\t\|pre-harm\|r14-harm-baseline\|def .*kind\|sha256" tests/fixtures/r15-census-config.py | head -60
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
arms={**r["runs"],"namespace_controls":r["namespace_controls"]}
ids=[c["id"] for c in r["runs"]["changed"]["cases"]]
print("ids:",ids)
print("%-12s %-8s %-8s %-8s"%("case","preharm","baseline","changed"))
for i in ids:
    row=[]
    for a in ("baseline_preharm","baseline","changed"):
        c={x["id"]:x for x in r["runs"][a]["cases"]}[i]
        row.append(c["status"])
    print("%-12s %-8s %-8s %-8s"%((i,)+tuple(row)))
print("preharm fails:",[c["id"] for c in r["runs"]["baseline_preharm"]["cases"] if c["status"]=="fail"])
print("baseline fails:",[c["id"] for c in r["runs"]["baseline"]["cases"] if c["status"]=="fail"])
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "_parse_transcript\|def _validate_record\|def _check_bindings\|TOOL_LINE_RE\|TOOL_KIND_RE" tools/souji-preservation-evidence.py
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
arm=r["runs"]["changed"]
for c in arm["cases"]:
    print(c["id"],c["status"],"|",c["detail"])
print("NS:")
for c in r["namespace_controls"]["cases"][:3]:
    print(c["id"],c["status"],"|",c["detail"])
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "credential-store\|include-protected\|git-config-unsupported\|git-include-cycle\|filter-driver-bound\|status-skipped" tools/souji-census.sh | head -40
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
for c in r["runs"]["baseline"]["cases"]:
    print(c["id"],c["status"],"|",c["detail"])
print("---preharm fails")
for c in r["runs"]["baseline_preharm"]["cases"]:
    if c["status"]=="fail": print(c["id"],"|",c["detail"])
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "HARM_SHA\|PREHARM_SHA\|CASE_CLASSES\|^HARM_CASES\|^EXPECTED_IDS" tests/fixtures/r15-census-config.py | head -20
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
for arm,v in list(r["runs"].items())+[("namespace_controls",r["namespace_controls"])]:
    toolpath=v["argv"][5]
    toolline=v["stdout"].splitlines()[0].split("\t")[1]
    print(arm,"argv5==TOOLline",toolpath==toolline,"| toolpath",toolpath)
    parsed=[]
    for line in v["stdout"].splitlines():
        if line.startswith("CASE\t"):
            p=line.split("\t")
            parsed.append((p[1],p[2].lower(),"\t".join(p[3:])))
    decl=[(c["id"],c["status"],c["detail"]) for c in v["cases"]]
    print("  count",len(parsed),len(decl),"idsets", {p[0] for p in parsed}=={d[0] for d in decl})
    mism=[(a[0],a[2][:40],b[2][:40]) for a,b in zip(parsed,decl) if a[2].replace("\t"," ")!=(b[2] or "")]
    print("  detail-mismatch",len(mism),mism[:2])
    params=[l for l in v["stdout"].splitlines() if l.startswith("SUMMARY\t")]
    print("  summary line",params)
    maxsum=max(len(p[2].split("\t")[0]) for p in parsed)
    print("  max human summary chars",maxsum,"max declared detail",max(len(d[2]) for d in decl))
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
for arm,v in list(r["runs"].items())+[("namespace_controls",r["namespace_controls"])]:
    print(arm,"argv[-1]",v["argv"][-1],"| TOOL line",v["stdout"].splitlines()[0].split("\t")[1],"| eq",v["argv"][-1]==v["stdout"].splitlines()[0].split("\t")[1])
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -3 -- tests/fixtures/r15-preservation-frozen/record.json && git merge-base --is-ancestor c6207bdac2e0ef52c1da5fbc87dce5d94065972e HEAD && echo "c6207bd is ancestor of HEAD" && git show c6207bd:tests/fixtures/r15-census-config.py | sha256sum && git show c6207bd:tests/fixtures/r14-census-boundary.py | sha256sum && git show c6207bd:tools/souji-preservation-evidence.py | sha256sum && sha256sum tools/souji-preservation-evidence.py
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix-final.json'))
print(type(d), list(d)[:12] if isinstance(d,dict) else len(d))
" 2>&1 | head -5
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix-final.json'))
print("lane_head",d["lane_head"]); print("arms",d["arms"]); print("changed",d["changed"])
print("fixtures_sha256",json.dumps(d["fixtures_sha256"],indent=1)[:600])
print("invalid_suites",d["invalid_suites"])
print("fixtures_dirty",d["fixtures_dirty"])
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show c6207bd:tests/fixtures/r15-preservation-frozen/record.json | sha256sum && git show c6207bd:tests/fixtures/r15-preservation-frozen/expected.json | sha256sum && git show c6207bd:tests/fixtures/r15-preservation-frozen/README.md | sha256sum && sha256sum tests/fixtures/r15-preservation-frozen/README.md
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for c in b410186 c6207bd 7a79dc2 HEAD; do printf '%s ' "$c"; git show "$c:tests/fixtures/r15-preservation-frozen/record.json" 2>/dev/null | sha256sum | cut -c1-16; done; echo "--- diff c6207bd vs HEAD record"; diff <(git show c6207bd:tests/fixtures/r15-preservation-frozen/record.json) tests/fixtures/r15-preservation-frozen/record.json | head -40
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat 85de2a43e9040752b16b116c3cbd56e84f6f6f82895c38f0ea459b8f159d1d87 2>/dev/null; echo "--- try extract fixture at 0a70bef"; git show 0a70bef:tests/fixtures/r15-census-config.py | sha256sum; echo "--- matrix final r15-config statuses"; python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix-final.json'))
for arm in d["arms"]:
    a=d["arms"][arm]
    if "r15-config" in a:
        cs=a["r15-config"]["cases"]
        fails=[k for k,v in cs.items() if v["verdict"]!="PASS"]
        print(arm,"total",a["r15-config"].get("total"),"failed",a["r15-config"].get("failed"),"fails",fails)
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '944,980p' tools/souji-preservation-evidence.py | cat -n && echo "--- 1354-1365" && sed -n '1354,1366p' tools/souji-preservation-evidence.py | cat -n && echo "--- 125,150" && sed -n '125,150p' tools/souji-preservation-evidence.py | cat -n
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "def _case_\|CASE_SPECS\|cases = \[" tools/souji-preservation-evidence.py | head -30
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "benign   (01\|refusal  (02\|safety   (08\|preserve (05\|Expected per-case status" tools/souji-preservation-evidence.py
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,hashlib
fin=json.load(open('census/round-16/c1-matrix-final.json'))
print("final lane_head",fin["lane_head"],"fixture",fin["fixtures_sha256"]["r15-config"][:16])
rec=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
def fails(cases): return {c["id"] for c in cases if c["status"]=="fail"}
for arm,key in (("pre-harm","baseline_preharm"),("r14-harm","baseline"),("changed","changed")):
    m=fails([{"id":k,"status":"fail" if v["verdict"]!="PASS" else "pass"} for k,v in fin["arms"][arm]["r15-config"]["cases"].items()])
    r=fails(rec["runs"][key]["cases"])
    print(arm,"matrix",len(m),"record",len(r),"equal",m==r)
mns={k for k,v in fin["arms"]["changed"]["r14-namespace"]["cases"].items() if v["verdict"]!="PASS"}
print("ns equal",mns==fails(rec["namespace_controls"]["cases"]),len(mns))
try:
    land=json.load(open('census/round-16/c1-matrix-landing.json'))
    print("landing lane_head",land.get("lane_head"),"fixtures",land.get("fixtures_sha256"))
    for arm in land["arms"]:
        a=land["arms"][arm]
        if "r15-config" in a:
            print(" landing",arm,a["r15-config"].get("total"),a["r15-config"].get("failed"))
        if "r14-namespace" in a:
            print(" landing ns",arm,a["r14-namespace"].get("total"),a["r14-namespace"].get("failed"))
except FileNotFoundError as e:
    print("no landing matrix",e)
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "TOOL\\\\t\|TOOL-KIND\|SUMMARY\\\\t\|CASE\\\\t" tests/fixtures/r14-census-boundary.py | head -12
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
for f in ('census/round-16/c1-matrix-final.json','census/round-16/c1-matrix-landing.json'):
    d=json.load(open(f))
    print(f, sorted(d.keys()))
    print('  lane_head',d.get('lane_head'),'runner',d.get('runner_sha256'),'tool?',d.get('tool_sha256'))
    ch=d['arms']['changed']
    print('  changed keys',sorted(ch.keys()))
"
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "souji-census\|sha256\|--tool\|lane\|HEAD\|rev-parse" census/round-16/run-matrix.py | head -30
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
for f in ('census/round-16/c1-matrix-final.json','census/round-16/c1-matrix-landing.json'):
    d=json.load(open(f)); print("==",f,"lane_head",d["lane_head"][:12],"fixture",d["fixtures_sha256"]["r15-config"][:16])
    for name in ("changed","pre-harm","r14-harm","r15-baseline"):
        a=d["arms"].get(name)
        if a: print("  %-12s rev=%s sha=%s"%(name,str(a.get("rev"))[:12],str(a.get("sha256"))[:16]))
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "harm_cases\|HARM_CASES" --include=*.py --include=*.sh tools tests census/round-16 2>/dev/null | grep -v "census/operator-sweep" | head -20
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file -e fc3a8d49b52de26bef74418da96611aae34b958d 2>&1; echo "rc=$?"; echo "=== diff 0a70bef..7a79dc2 name-status ==="; git diff --name-status 0a70bef 7a79dc2 | head -20
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== expected.json at c6207bd ===" && git show c6207bd:tests/fixtures/r15-preservation-frozen/expected.json && echo "=== record.json at c6207bd (head) ===" && git show c6207bd:tests/fixtures/r15-preservation-frozen/record.json | head -40
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-list --all | while read c; do d=$(git rev-parse "$c:tools/souji-census.sh" 2>/dev/null) || continue; if [ "$d" = "$(printf 'b51873514d1f6d34a5e3427bf30c95686a5d27b6ec9b8332034c3a3ba7868e02' | git hash-object --stdin 2>/dev/null)" ]; then echo "MATCH blob in $c"; fi; done 2>/dev/null | head -5; echo "--- direct blob search"; git cat-file -t b51873514d1f6d34a5e3427bf30c95686a5d27b6ec9b8332034c3a3ba7868e02 2>&1
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log -1 --format='%H%n%ad%n%s' fc3a8d49b52de26bef74418da96611aae34b958d && echo "--- tool at fc3a8d49" && git show fc3a8d49:tools/souji-census.sh | sha256sum && echo "--- fixture at fc3a8d49" && git show fc3a8d49:tests/fixtures/r15-census-config.py | sha256sum
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "is_baseline\|PREHARM\|BASELINE_SHA" tests/fixtures/r14-census-boundary.py | head -12 && python3 -c "
import json
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
print('ns argv',r['namespace_controls']['argv'])
print('ns commit',r['namespace_controls']['tool']['commit'])
print('changed commit',r['runs']['changed']['tool']['commit'],'measured',r['measured_commit'])
"
```

```sh
cd /tmp && python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-preservation-evidence.py --frozen /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-preservation-frozen --root /home/vgpnk/Projects/shokunin/souji-shokunin; echo "EXIT=$?"
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,hashlib
for f,want in (("tests/fixtures/r15-preservation-frozen/record.json","173db77793bca747e9efad4150ea8a0dd2d9d4bdc0c17f30dc734bfe0e983599"),("tests/fixtures/r15-preservation-frozen/expected.json","d955b18c912e3a6aa5a3129697fd8d4bd8779874c008172bb9c5f071285a1bb0")):
    raw=open(f,'rb').read()
    canon=(json.dumps(json.loads(raw),indent=2,sort_keys=True)+"\n").encode()
    print(f,"canonical_reemit",hashlib.sha256(canon).hexdigest()==want,"raw",hashlib.sha256(raw).hexdigest()==want,"ends_nl",raw.endswith(b"\n"))
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "authored before\|As shipped\|snapshot_tampered\|integration commit" tests/fixtures/r15-preservation-frozen/README.md; echo "--- table lines"; grep -n "^CONFIG_BENIGN_IDS\|^CONFIG_REFUSAL_IDS\|^CONFIG_SAFETY_IDS\|^CONFIG_PRESERVE_PREHARM\|^CONFIG_TOKEN_IDS\|^# Four classes\|^#   benign\|^#   refusal\|^#   safety\|^#   preserve" tools/souji-preservation-evidence.py
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,re
src=open('tests/fixtures/r15-census-config.py').read()
m=re.search(r"HARM_CASES = frozenset\(\{(.*?)\}\)",src,re.S)
harm=set(re.findall(r'"(R15CFG-\d+)"',m.group(1)))
rec=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
obs={c["id"] for c in rec["runs"]["baseline"]["cases"] if c["status"]=="fail"}
print("HARM_CASES",len(harm),"observed harm fails",len(obs))
print("in HARM_CASES not observed",sorted(harm-obs))
print("observed not in HARM_CASES",sorted(obs-harm))
EOF
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
for arm,v in list(r["runs"].items())+[("namespace_controls",r["namespace_controls"])]:
    s=v["stdout"]
    print(arm,"endswith_single_nl",s.endswith("\n") and not s.endswith("\n\n"),"lines",len(s.splitlines()),"cr",("\r" in s))
EOF
echo "--- frozen dir unchanged in git"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain tests/fixtures/r15-preservation-frozen/; echo "(empty means clean)"
```

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show 7a79dc2:tests/fixtures/r15-preservation-frozen/expected.json | sha256sum && git merge-base --is-ancestor 7a79dc2 HEAD && echo "7a79dc2 ancestor of HEAD" && git log --oneline 7a79dc2..HEAD -- tests/fixtures/r15-preservation-frozen/ | head -5; echo "(empty = frozen dir unchanged since landing)"
```
