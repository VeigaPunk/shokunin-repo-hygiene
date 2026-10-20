# RerunMatrixLanding — wave 2 falsification of C1's counting command

STATUS: ok — C1's published totals and all 128 per-case verdicts reproduce exactly at
HEAD (0 verdict differences vs `census/round-16/c1-matrix-final.json`); no blocking
defect. Findings F1–F4 below are low-severity record/instrument defects; none
contradicts a claimed total or verdict.

Axis: operability. Attack: run the C1 counting command at the lane HEAD and compare
every arm's totals and per-case verdicts with `census/round-16/c1-matrix-final.json`
(and, because it exists and is now committed, with
`census/round-16/c1-matrix-landing.json`).

## Scope, identity, and method

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
- Lane HEAD was `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae` when the rerun was started;
  L1 committed `163158a` (lesson/sources/landing record) while this review was running.
  Matrix inputs are byte-identical at `7a79dc2`, `a6ec781`, and `163158a`:
  `tools/souji-census.sh` sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`,
  `tests/fixtures/r15-census-config.py` sha256 `2747439680…`,
  `tests/fixtures/r14-census-boundary.py` sha256 `e6a984b1…`,
  `census/round-16/run-matrix.py` sha256 `2815712b…`.
- Rerun (only permitted execution): `run-matrix.py --changed a6ec7810… --output
  /var/tmp/souji-r16-RerunMatrixLanding/m.json`. Exit 0 in 2m44.8s; record sha256
  `304c2ff664477d4646297225adc5682ae3fbd85500e3c517359b179ebd35daf3`;
  `invalid_suites: []`. Manifest: git 2.56.0, bash 5.3.20(1), Python 3.14.8,
  shellcheck 0.11.0, `fixtures_dirty: ""`, runner digest `2815712b…`.
- Records compared byte-for-byte and structurally:
  `c1-matrix-final.json` sha256 `61e56f6c…` (`lane_head` `0a70bef`, changed `0a70bef`),
  `c1-matrix-landing.json` sha256 `bdb24b76…` (`lane_head` `7a79dc2`, changed `"HEAD"`).
  The landing file now committed at HEAD `163158a` has exactly the compared bytes
  (`git show HEAD:census/round-16/c1-matrix-landing.json | sha256sum` = `bdb24b76…`).

## Headline result — fresh HEAD run

Console output of the rerun, verbatim:

```
pre-harm	6a000c59fe74	bash-n=0	sc=0	selftest=36/0fail	r15=20/8fail	r14=12/10fail
r14-harm	fcff8b057b3e	bash-n=0	sc=0	selftest=38/0fail	r15=20/16fail	r14=12/0fail
r15-baseline	dab4122c997d	bash-n=2	sc=1	selftest=None/Nonefail	r15=20/20fail	r14=12/12fail
changed	64a60fd0b0ed	bash-n=0	sc=0	selftest=38/0fail	r15=20/0fail	r14=12/0fail
```

| arm | rev | sha256[:12] | bash -n rc | shellcheck rc/findings | selftest checks/failed | r15 total/fail | r14 total/fail |
|---|---|---|---|---|---|---|---|
| changed | `a6ec7810…` | `64a60fd0b0ed` | 0 | 0 / 0 | 38 / 0 | 20 / 0 | 12 / 0 |
| pre-harm | `a31642d1…` | `6a000c59fe74` | 0 | 0 / 0 | 36 / 0 | 20 / 8 | 12 / 10 |
| r14-harm | `cc216832…` | `fcff8b057b3e` | 0 | 0 / 0 | 38 / 0 | 20 / 16 | 12 / 0 |
| r15-baseline | `b410186c…` | `dab4122c997d` | 2 | 1 / 4 | None / None (rc 2) | 20 / 20 | 12 / 12 |

This reproduces the wave-1 claim literally: changed 20/20 and 12/12, selftest 38/0,
bash -n and shellcheck clean; r15-baseline does not parse (bash -n rc 2 at tool line
1368) and fails 20/20 + 12/12; r14-harm fails 16/20 in the r15 suite and covers every
`HARM_CASES` id (15/15).

### Comparison against `c1-matrix-final.json`

- `rc`, `total`, `failed`, `valid` for all 8 suites (4 arms × 2 fixtures): **identical**.
- Per-case verdicts: **128/128 identical**; case-id sets identical in every arm/suite.
- Per-arm `sha256`, `bash_n.rc`, `shellcheck_warning` (`rc` and `findings`), `selftest`
  triplet: identical.
- Environment fields (`bash_version`, `git_version`, `python_version`,
  `shellcheck_version`, `runner_sha256`): identical.

### Differences that were found (and what they are)

- 15 case-`detail` strings per record pair differ; they are exactly the pre-harm arm's
  FAIL diagnostics: r15 `R15CFG-02,03,11,17,19` and r14
  `R14C2-01,02,03,04,05,06,09,10,11,12`. Every PASS detail is byte-identical. The
  differing bytes are strace PIDs, `/var/tmp/r15-census-config.*` /
  `/var/tmp/r14-census-boundary.*` mkdtemp names, and stack addresses; after masking
  those, 0 textual differences remain. The runner's 300-character cut
  (`run-matrix.py:53`) also lands at a different offset because PIDs/paths differ in
  length.
- `bash_n.stderr` for the r15-baseline arm carries the runner's own mkdtemp path
  (`run-matrix.py:94`), so it differs on every run.
- Record-level fields that legitimately differ: `lane_head` (`0a70bef` / `7a79dc2` /
  `a6ec781`), `changed` (`0a70bef` / `"HEAD"` / full rev), and
  `fixtures_sha256.r15-config` (`85de2a43…` in final vs `2747439680…` in landing and in
  the fresh run) — see F1.

No total, no failed count, and no verdict differs. The counting command passes the
assigned falsification at the level of its claim.

## Findings

### F1 — low — `c1-matrix-final.json` cannot substantiate the “r16-revised fixture” wording; the landing record can

- `c1-matrix-final.json` records `lane_head`/`changed` `0a70bef` and
  `fixtures_sha256.r15-config` = `85de2a43e9040752b16b116c3cbd56e84f6f6f82895c38f0ea459b8f159d1d87`
  (`census/round-16/c1-matrix-final.json:660-668`).
- The commit that contains that record, `7a79dc2` (and HEAD `163158a`), has the fixture
  at `2747439680…`: the fixture changed in `c6207bd`, one commit after the measurement.
  `git diff 0a70bef 7a79dc2 -- tests/fixtures/r15-census-config.py` is a single hunk
  capped at lines 1515-1521 of the fixture (human-readable summary truncated to 400
  characters), so the change is verdict-neutral — proven by 0/128 verdict differences
  between the two records and by the fresh run over the capped fixture.
- Consequence: the handoff sentence “measured … over the r16-revised
  `tests/fixtures/r15-census-config.py` … (`c1-matrix-final.json`; landing rerun …)”
  attributes the revised-fixture measurement to the one record whose own digest is the
  pre-cap fixture. The record is internally honest (`lane_head` names `0a70bef`); the
  citation is not.
- Smallest fix: cite `c1-matrix-landing.json` (now committed, `bdb24b76…`) for the
  revised-fixture claim, or regenerate `c1-matrix-final.json` at `7a79dc2`+.
- Verdict: **partial** (claim numbers unaffected; attribution wrong).

### F2 — low — the counting command cannot notice a fixture that shrinks or drifts

- `total`/`failed` come from the fixture's own `SUMMARY` line (`run-matrix.py:28,54-57`),
  and `valid` (`run-matrix.py:57-60`) only requires `len(cases) == total` plus a
  consistent FAIL count. There is no pinned expected total (20/12) and no cross-arm
  case-set equality check. A future fixture edit that deletes a case, or a fixture
  change that renames ids consistently, would read as a clean smaller pass.
- Today the risk is unrealised: all four arms report 20/12; the fixture's own id-set
  guard (`tests/fixtures/r15-census-config.py:1540-1546`) emits an extra
  `CASE\tid-set\tFAIL` line, which makes `len(cases) = total + 1` and forces the suite
  invalid → `run-matrix.py:137-139` exits 2 (verified by inspection of the guard and
  the runner's validity predicate; not executed).
- Smallest fix: pin `EXPECTED = {"r15-config": 20, "r14-namespace": 12}` into `valid`,
  and assert the case-key sets are equal across all four arms after the loop.
- Verdict: **holds today; hardening gap** (no live miscount).

### F3 — low — `shellcheck_warning.findings` is output-format dependent, not a count of findings

- `run-matrix.py:112-113` counts occurrences of `(warning)`/`(error)` in shellcheck's
  stdout. That token is part of shellcheck's default human format only. Observed on the
  extracted `b410186` tool: default invocation yields 4 markers; with inherited
  `SHELLCHECK_OPTS='-f gcc'` the same tool yields **0** markers while shellcheck's rc
  stays 1. The runner passes the caller's environment through, so a record can read
  `{"rc": 1, "findings": 0}` — which is what the current record would look like in
  that environment.
- No current record is affected (all four arms were measured with default format), and
  `rc` remains a sound signal; the claim “shellcheck clean” must be read off `rc`, not
  `findings`.
- Smallest fix: drop `findings`, or invoke `shellcheck -f gcc` and count `SC[0-9]{4}`,
  or pass a sanitised env (strip `SHELLCHECK_OPTS`).
- Verdict: **partial** (field can misreport; no observed miscount in the records).

### F4 — nit — `HARM_CASES` omits one case the harm arm is observed to fail

- `HARM_CASES` (`tests/fixtures/r15-census-config.py:161-165`) lists 15 ids and its
  header (`:156-160`) calls them “cases expected to FAIL under the r14 harm tool from
  OBSERVED behavior”.
- At HEAD the r14-harm arm fails 16/20: the 15 listed plus `R15CFG-19`, detail
  `store: contract: synthetic store path in output`, `observed_exit=2`,
  `observed_finding=path-protected:credential-store`. `R15CFG-19` is FAIL in all three
  records (final, landing, fresh) and in the frozen r15 preservation record measured at
  `c6207bd` (`tests/fixtures/r15-preservation-frozen/record.json`, arm `baseline`,
  `R15CFG-19` status `fail`).
- Consequence: the handoff claim “r14-harm fails every HARM_CASES id” is true (15/15),
  but the exported `harm_cases` list (`--json`, fixture `:1555`) understates the harm
  arm by one id, and the r16 note names only `03/07/14` while `18/20` were added at
  `0a70bef` without mention. A consumer building “must fail under harm” from
  `harm_cases` would not require `R15CFG-19` to fail.
- Smallest fix: add `"R15CFG-19"` to the set (or state that it is excluded because its
  harm is a store-path leak, not a refusal) and extend the r16 note to `03/07/14/18/20`.
- Verdict: **fails (documentation/table level, low severity)**.

### F5 — informational — records are not byte-reproducible; verdicts are

- Every rerun rewrites 15 detail strings (the pre-harm FAIL set above) and the
  r15-baseline `bash_n.stderr` mkdtemp path. Any future automated record diff must mask
  PIDs, `/var/tmp/<fixture>.<suffix>` paths and `0x…` addresses, and must not treat the
  300-char detail cut (`run-matrix.py:53`) as semantic. The verdict tuple
  (arm, suite, case, PASS/FAIL) is stable across all three records.
- Verdict: **holds** (with the normalisation rule above).

## What holds (verified, not inferred)

- The counting command's claim reproduces exactly at HEAD for all four arms: totals,
  failed counts, validity, 128 per-case verdicts, selftest triplets, bash -n rc, and
  shellcheck rc/findings.
- The landing record is now committed at HEAD (`163158a`) with the exact bytes compared
  (`bdb24b76…`); its `lane_head` (`7a79dc2`) predates HEAD only by the C2/R5 commit
  `a6ec781` and the docs commit `163158a`, neither of which touches a matrix input
  (`git diff --stat 7a79dc2 163158a -- tools/souji-census.sh
  tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py
  census/round-16/run-matrix.py` is empty). The record therefore remains valid at HEAD.
- Counting semantics fail closed: an extra `id-set` CASE line, a duplicated/short case
  set, a missing `SUMMARY`, or a fixture rc outside {0,1} all make `valid` false and
  make the run exit 2 (`run-matrix.py:57-60`, `131-139`), so a partial or hijacked
  suite cannot be reported as a clean count.
- r15 baseline non-parse is a genuine parse failure, not a fixture artefact: `bash -n`
  rc 2, `line 1368: syntax error near unexpected token '}'`, and the same arm's
  selftest fields are `None` rather than fabricated zeros.
- The r14-harm arm's failure set (16 ids) is identical in final, landing and fresh
  records and matches the independently regenerated frozen record at `c6207bd`.

## Residual risk / verification gaps

- F2 and F3 are instrument-hardening findings; I did not mutate the fixture or the
  environment to force a live miscount (the shellcheck format effect was demonstrated
  on a copy under `/var/tmp`, not through the runner).
- I did not adjudicate whether a PASS means what each case name claims (oracle
  strength); this lane only tests the counting command and its records.
- The matrix is now three-records deep (final at `0a70bef`, landing at `7a79dc2`, fresh
  at `a6ec781`) with identical verdicts; a fourth rerun after L1's docs commit would be
  redundant, and none was performed beyond the single permitted invocation.

Tooling installed or upgraded for this review: none.

## Commands

```bash
mkdir -p /var/tmp/souji-r16-RerunMatrixLanding && cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && ls -l census/round-16/c1-matrix-final.json census/round-16/c1-matrix-landing.json census/round-16/run-matrix.py && sha256sum census/round-16/c1-matrix-final.json census/round-16/c1-matrix-landing.json census/round-16/run-matrix.py tools/souji-census.sh
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
for n in ("final","landing"):
    d=json.load(open(f"census/round-16/c1-matrix-{n}.json"))
    print("==",n,d["lane_head"],d["changed"],d["fixtures_dirty"],d["invalid_suites"])
    for arm,v in d["arms"].items():
        print(" ",arm, v.get("rev"), v.get("sha256"))
        for k in ("bash_n","shellcheck_warning","selftest","r15-config","r14-namespace"):
            x=v.get(k)
            if isinstance(x,dict):
                print("   ",k,{kk:x[kk] for kk in x if kk not in ("cases","cases_detail")})
        print()
EOF
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
F=json.load(open("census/round-16/c1-matrix-final.json"))
L=json.load(open("census/round-16/c1-matrix-landing.json"))
for arm in F["arms"]:
    for suite in ("r15-config","r14-namespace"):
        fc=F["arms"][arm][suite]["cases"]; lc=L["arms"][arm][suite]["cases"]
        if fc==lc:
            print(f"{arm:12s} {suite:14s} cases IDENTICAL ({len(fc)})")
        else:
            print(f"{arm:12s} {suite:14s} DIFF")
            for k in sorted(set(fc)|set(lc)):
                a=fc.get(k); b=lc.get(k)
                if a!=b: print("   ",k,"\n     final:",a,"\n     land :",b)
EOF
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat 7a79dc2d6e282654b9379c391c4c6be985ccf92c a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae -- tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py census/round-16/run-matrix.py
echo "---log---"
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline 7a79dc2d6e282654b9379c391c4c6be985ccf92c..a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae
echo "---head fixture digests---"
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py --changed a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae --output /var/tmp/souji-r16-RerunMatrixLanding/m.json; echo "EXIT=$?"
```
(the above was first submitted `async`; the harness refused it with “Background job limit reached (100)” and it did not execute. The synchronous form below is what ran.)

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff 0a70bef 7a79dc2 -- tests/fixtures/r15-census-config.py | head -120; echo "=== case id sets ==="; for r in 0a70bef 7a79dc2; do echo "--$r"; git show "$r:tests/fixtures/r15-census-config.py" | grep -oE "R15CFG-[0-9]+" | sort -u | tr '\n' ' '; echo; done
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE "timeout|TIMEOUT|def run_case|subprocess.run" tests/fixtures/r15-census-config.py | head -40; echo ===; grep -nE "timeout|TIMEOUT" tests/fixtures/r14-census-boundary.py | head -20; echo ===; grep -n "CASE\|print(f\"SUMMARY" tests/fixtures/r15-census-config.py | head -5
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && time python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py --changed a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae --output /var/tmp/souji-r16-RerunMatrixLanding/m.json; echo "EXIT=$?"
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,re
M=json.load(open("/var/tmp/souji-r16-RerunMatrixLanding/m.json"))
F=json.load(open("census/round-16/c1-matrix-final.json"))
L=json.load(open("census/round-16/c1-matrix-landing.json"))
print("M manifest:", M["lane_head"], M["changed"], M["fixtures_sha256"], M["fixtures_dirty"], M["invalid_suites"], M["runner_sha256"][:12])
def norm(s):
    s=re.sub(r"/var/tmp/(r15-census-config|r14-census-boundary|souji-r16-matrix)\.[A-Za-z0-9_]+","<TMP>",s)
    s=re.sub(r"\b\d{6,7}\b","<PID>",s)
    s=re.sub(r"0x[0-9a-f]+","<ADDR>",s)
    return s
for other,name in ((F,"final"),(L,"landing")):
    diffs=0
    for arm in M["arms"]:
        for suite in ("r15-config","r14-namespace"):
            a,b=M["arms"][arm][suite],other["arms"][arm][suite]
            for f in ("rc","total","failed","valid"):
                if a[f]!=b[f]: print(f"  {name} FIELD {arm}/{suite}/{f}: mine={a[f]} {name}={b[f]}"); diffs+=1
            if set(a["cases"])!=set(b["cases"]): print(f"  {name} CASE-SET {arm}/{suite}"); diffs+=1
            for k in a["cases"]:
                if a["cases"][k]["verdict"]!=b["cases"][k]["verdict"]:
                    print(f"  {name} VERDICT {arm}/{suite}/{k}: mine={a['cases'][k]['verdict']} {name}={b['cases'][k]['verdict']}"); diffs+=1
                elif norm(a["cases"][k]["detail"])!=norm(b["cases"][k]["detail"]):
                    print(f"  {name} DETAIL {arm}/{suite}/{k}"); diffs+=1
        if M["arms"][arm]["selftest"]!=other["arms"][arm]["selftest"]:
            print(f"  {name} SELFTEST {arm}: mine={M['arms'][arm]['selftest']} {name}={other['arms'][arm]['selftest']}"); diffs+=1
        if M["arms"][arm]["sha256"]!=other["arms"][arm]["sha256"]:
            print(f"  {name} SHA {arm}"); diffs+=1
    print(f"{name}: {diffs} differences vs fresh HEAD run")
print("\nchanged r15 cases:", {k:v['verdict'] for k,v in M['arms']['changed']['r15-config']['cases'].items()})
print("changed r14 cases:", {k:v['verdict'] for k,v in M['arms']['changed']['r14-namespace']['cases'].items()})
print("\nr14-harm r15 fails:", sorted(k for k,v in M['arms']['r14-harm']['r15-config']['cases'].items() if v['verdict']=='FAIL'))
print("r14-harm r15 pass :", sorted(k for k,v in M['arms']['r14-harm']['r15-config']['cases'].items() if v['verdict']=='PASS'))
EOF
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "HARM_CASES\|CASE_CLASSES\|TOOL-KIND\|--tool\|args.tool\|tool_kind\|KIND" tests/fixtures/r15-census-config.py | head -60
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
M=json.load(open("/var/tmp/souji-r16-RerunMatrixLanding/m.json"))
F=json.load(open("census/round-16/c1-matrix-final.json"))
L=json.load(open("census/round-16/c1-matrix-landing.json"))
k="R14C2-04"
for n,d in (("final",F),("landing",L),("fresh",M)):
    print(n,":",repr(d["arms"]["pre-harm"]["r14-namespace"]["cases"][k]["detail"]))
print()
print("r14-harm R15CFG-19 detail:",repr(M["arms"]["r14-harm"]["r15-config"]["cases"]["R15CFG-19"]["detail"]))
print("r14-harm R15CFG-02 detail:",repr(M["arms"]["r14-harm"]["r15-config"]["cases"]["R15CFG-02"]["detail"]))
print("pre-harm r15 fails:", sorted(k for k,v in M["arms"]["pre-harm"]["r15-config"]["cases"].items() if v["verdict"]=="FAIL"))
EOF
echo "=== HARM_CASES history ==="
for r in b410186 cbf688a 0a70bef 7a79dc2 a6ec781; do echo "--$r"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show "$r:tests/fixtures/r15-census-config.py" | sed -n '/^HARM_CASES = frozenset({/,/^})/p' | tr -d ' \n'; echo; done
echo "=== consumers of harm_cases/HARM ==="
grep -rn "harm_cases\|HARM_CASES\|r15-census-config" /home/vgpnk/Projects/shokunin/souji-shokunin/tools/ /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-preservation-frozen/regenerate.py 2>/dev/null | head -30
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1018,1040p;955,970p;980,1000p' tests/fixtures/r15-census-config.py; echo "=== any raw out/err in problems ==="; grep -n "res\.out\|res\.err\|\.stdout\|\.stderr" tests/fixtures/r15-census-config.py | sed -n '1,60p'
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1560,1573p' tests/fixtures/r15-census-config.py; echo "=== r14 fixture summary/exit ==="; grep -n "SUMMARY\|return 1 if\|failed\b" tests/fixtures/r14-census-boundary.py | tail -15
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "problems.append\|problems +=\|def check\|def note\|stdout is not empty\|stdout\b" tests/fixtures/r15-census-config.py | head -50
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,re
M=json.load(open("/var/tmp/souji-r16-RerunMatrixLanding/m.json"))
F=json.load(open("census/round-16/c1-matrix-final.json"))
L=json.load(open("census/round-16/c1-matrix-landing.json"))
def norm(s):
    s=re.sub(r"/var/tmp/(r15-census-config|r14-census-boundary|souji-r16-matrix)\.[A-Za-z0-9_]+","<TMP>",s)
    s=re.sub(r"\b\d{4,7}\b","<N>",s)
    s=re.sub(r"0x[0-9a-f]+","<A>",s)
    return s
tot_diff=0
for name,d in (("final",F),("landing",L)):
    raw=0; normd=0; verdicts=0; fields=0
    for arm in M["arms"]:
        a,b=M["arms"][arm],d["arms"][arm]
        for f in ("sha256",):
            if a[f]!=b[f]: fields+=1
        if a["selftest"]!=b["selftest"]: fields+=1
        if a["bash_n"]["rc"]!=b["bash_n"]["rc"] or a["shellcheck_warning"]!=b["shellcheck_warning"]: fields+=1
        if a["bash_n"]["stderr"]!=b["bash_n"]["stderr"]: fields+=1
        for suite in ("r15-config","r14-namespace"):
            sa,sb=a[suite],b[suite]
            for f in ("rc","total","failed","valid"):
                if sa[f]!=sb[f]: fields+=1; print(name,arm,suite,f,sa[f],sb[f])
            for k in sorted(set(sa["cases"])|set(sb["cases"])):
                va=sa["cases"].get(k,{}).get("verdict"); vb=sb["cases"].get(k,{}).get("verdict")
                if va!=vb: verdicts+=1
                if sa["cases"][k]["detail"]!=sb["cases"][k]["detail"]:
                    raw+=1
                    if norm(sa["cases"][k]["detail"])!=norm(sb["cases"][k]["detail"]): normd+=1
    print(f"{name}: field-level differences={fields} verdict differences={verdicts} raw detail differences={raw} normalized detail differences={normd}")
    tot_diff+=fields+verdicts+normd
print("TOTAL semantic differences:",tot_diff)
for k in ("bash_version","git_version","python_version","shellcheck_version","runner_sha256"):
    print(k,"final=",F[k],"landing=",L[k],"fresh=",M[k])
EOF
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import ast,sys
src=open("tests/fixtures/r15-census-config.py").read()
tree=ast.parse(src)
for node in tree.body:
    if isinstance(node,ast.Assign):
        tgt=node.targets[0]
        if getattr(tgt,"id","") in ("EXPECTED_IDS","CASES","HARM_CASES","CASE_CLASSES"):
            try: val=ast.literal_eval(node.value)
            except Exception as e: print(tgt.id,"<not literal>"); continue
            print(tgt.id, len(val), sorted(val) if isinstance(val,(dict,set,frozenset)) else val)
EOF
echo "=== frozen + gate references to harm list ==="
grep -rn "R15CFG-19\|harm_cases\|HARM" tests/fixtures/r15-preservation-frozen/expected.json tests/fixtures/r15-preservation-frozen/record.json tools/souji-preservation-evidence.py 2>/dev/null | head -20
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open("tests/fixtures/r15-preservation-frozen/record.json"))
print(type(d), list(d)[:12] if isinstance(d,dict) else len(d))
EOF
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --format='%h %ci %s' -6; echo "=== fixture/tool digest per commit ==="; for r in cbf688a 0a70bef c6207bd 7a79dc2 a6ec781; do printf "%s fx=" "$r"; git show "$r:tests/fixtures/r15-census-config.py" | sha256sum | cut -c1-12; printf "    tool="; git show "$r:tools/souji-census.sh" | sha256sum | cut -c1-12; done
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open("tests/fixtures/r15-preservation-frozen/record.json"))
for k,v in d.items():
    print(k, type(v).__name__, (len(v) if hasattr(v,'__len__') else v))
runs=d["runs"]
print("runs sample type:", type(runs).__name__)
if isinstance(runs,dict):
    for k,v in runs.items():
        print(" arm",k,type(v).__name__, list(v)[:8] if isinstance(v,dict) else str(v)[:80])
EOF
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open("tests/fixtures/r15-preservation-frozen/record.json"))
for arm,v in d["runs"].items():
    cs=v["cases"]
    print("==",arm,"exit",v["exit_code"],"n",len(cs))
    print("  fails:",sorted(c["id"] for c in cs if c["status"]!="pass"))
    print("  R15CFG-19:",[c for c in cs if c["id"]=="R15CFG-19"])
EOF
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && mkdir -p /var/tmp/souji-r16-RerunMatrixLanding/sc && git show b410186:tools/souji-census.sh > /var/tmp/souji-r16-RerunMatrixLanding/sc/baseline.sh && chmod +x /var/tmp/souji-r16-RerunMatrixLanding/sc/baseline.sh && echo "--- default (as runner invokes) ---" && shellcheck -S warning /var/tmp/souji-r16-RerunMatrixLanding/sc/baseline.sh | head -8; echo "--- marker count default:"; shellcheck -S warning /var/tmp/souji-r16-RerunMatrixLanding/sc/baseline.sh | grep -cE '\(warning\)|\(error\)'; echo "--- -f gcc marker count:"; shellcheck -S warning -f gcc /var/tmp/souji-r16-RerunMatrixLanding/sc/baseline.sh | grep -cE '\(warning\)|\(error\)'; echo "--- -f gcc sample:"; shellcheck -S warning -f gcc /var/tmp/souji-r16-RerunMatrixLanding/sc/baseline.sh | head -3
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
M=json.load(open("/var/tmp/souji-r16-RerunMatrixLanding/m.json"))
F=json.load(open("census/round-16/c1-matrix-final.json"))
L=json.load(open("census/round-16/c1-matrix-landing.json"))
for name,d in (("final",F),("landing",L)):
    for arm in M["arms"]:
        a,b=M["arms"][arm],d["arms"][arm]
        for k in ("sha256","bash_n","shellcheck_warning","selftest"):
            if a[k]!=b[k]: print(name,arm,k,"differs:",a[k],"vs",b[k])
print("done")
EOF
echo "=== run-matrix numbered anchors ==="; grep -n "CASE_RE\|SUMMARY_RE\|SELFTEST_RE\|valid = \|r15-config\|invalid_suites\|record\[\"changed\"\]\|if out.exists\|mkdtemp\|git show\|def suite" census/round-16/run-matrix.py
echo "=== fixture anchors ==="; sed -n '156,167p' tests/fixtures/r15-census-config.py | cat -n
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "diff of matrix inputs 7a79dc2..a6ec781:"; git diff --stat 7a79dc2 a6ec781 -- tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py census/round-16/run-matrix.py; echo "exit=$?"; echo "--- worktree tool vs HEAD:"; sha256sum tools/souji-census.sh; git rev-parse HEAD:tools/souji-census.sh 2>/dev/null || git ls-tree HEAD tools/souji-census.sh; echo "--- landing record tracked?"; git ls-files --error-unmatch census/round-16/c1-matrix-landing.json 2>&1; echo "--- final record tracked?"; git ls-files --error-unmatch census/round-16/c1-matrix-final.json 2>&1
```

```bash
cd /var/tmp/souji-r16-RerunMatrixLanding/sc && printf '#!/bin/bash\nx=1\necho $x\n' > warnonly.sh && echo "default:"; shellcheck -S warning warnonly.sh >/dev/null 2>&1; echo "  rc=$?"; shellcheck -S warning warnonly.sh | grep -cE '\(warning\)|\(error\)'; echo "with inherited SHELLCHECK_OPTS=-S error:"; SHELLCHECK_OPTS='-S error' shellcheck -S warning warnonly.sh >/dev/null 2>&1; echo "  rc=$?"; SHELLCHECK_OPTS='-f gcc' shellcheck -S warning /var/tmp/souji-r16-RerunMatrixLanding/sc/baseline.sh | grep -cE '\(warning\)|\(error\)'; echo "gcc-format marker count above (baseline has 4 errors)"
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --oneline -3 && echo "--- matrix inputs at HEAD:" && for p in tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py census/round-16/run-matrix.py; do printf "%s " "$p"; git show "HEAD:$p" | sha256sum | cut -c1-16; done; echo "--- landing/final record at HEAD:"; git show HEAD:census/round-16/c1-matrix-landing.json 2>&1 | sha256sum; sha256sum census/round-16/c1-matrix-landing.json census/round-16/c1-matrix-final.json; echo "--- diff a6ec781..HEAD inputs:"; git diff --stat a6ec781 HEAD -- tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py census/round-16/run-matrix.py census/round-16/c1-matrix-final.json census/round-16/c1-matrix-landing.json; echo "diff-exit=$?"
```

```bash
cd /var/tmp/souji-r16-RerunMatrixLanding/sc && printf '#!/bin/bash\nfor f in $(ls); do rm $f; done\n' > warn2.sh && echo "default marker/rc:"; shellcheck -S warning warn2.sh; echo "rc=$?"; echo "--- with SHELLCHECK_OPTS='-S error':"; SHELLCHECK_OPTS='-S error' shellcheck -S warning warn2.sh; echo "rc=$?"; echo "--- with SHELLCHECK_OPTS='-e SC2044,SC2086':"; SHELLCHECK_OPTS='-e SC2044,SC2086' shellcheck -S warning warn2.sh; echo "rc=$?"
```

```bash
cd /var/tmp/souji-r16-RerunMatrixLanding/sc && printf '#!/bin/bash\ncp $1 $2\n' > warn4.sh && echo "default (warning-only file):"; shellcheck -S warning warn4.sh; echo "rc=$?"; echo "--- inherited SHELLCHECK_OPTS=-e SC2086:"; SHELLCHECK_OPTS='-e SC2086' shellcheck -S warning warn4.sh; echo "rc=$?"; echo "--- inherited SHELLCHECK_OPTS=-f gcc on baseline (4 errors):"; SHELLCHECK_OPTS='-f gcc' shellcheck -S warning baseline.sh | grep -cE '\(warning\)|\(error\)'; echo "rc-of-shellcheck=$?"
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
M=json.load(open("/var/tmp/souji-r16-RerunMatrixLanding/m.json"))
for arm,v in M["arms"].items():
    print(arm, "|", v["rev"][:12], "|", v["sha256"][:12],
          "| bash-n rc", v["bash_n"]["rc"], "| sc rc/find", v["shellcheck_warning"]["rc"], v["shellcheck_warning"]["findings"],
          "| selftest", v["selftest"]["checks"], "/", v["selftest"]["failed"],
          "| r15", v["r15-config"]["total"], "/", v["r15-config"]["failed"],
          "| r14", v["r14-namespace"]["total"], "/", v["r14-namespace"]["failed"],
          "| valid", v["r15-config"]["valid"], v["r14-namespace"]["valid"])
EOF
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
F=json.load(open("census/round-16/c1-matrix-final.json"))
L=json.load(open("census/round-16/c1-matrix-landing.json"))
M=json.load(open("/var/tmp/souji-r16-RerunMatrixLanding/m.json"))
HARM={"R15CFG-01","R15CFG-03","R15CFG-04","R15CFG-06","R15CFG-07","R15CFG-08","R15CFG-09","R15CFG-10","R15CFG-12","R15CFG-13","R15CFG-14","R15CFG-15","R15CFG-16","R15CFG-18","R15CFG-20"}
for n,d in (("final",F),("landing",L),("fresh",M)):
    c=d["arms"]["r14-harm"]["r15-config"]["cases"]
    fails={k for k,v in c.items() if v["verdict"]=="FAIL"}
    print(n,"HARM covered:",len(HARM&fails),"/",len(HARM),"| 19:",c["R15CFG-19"]["verdict"],"| all fails:",len(fails))
print("final 19 detail:",F["arms"]["r14-harm"]["r15-config"]["cases"]["R15CFG-19"]["detail"])
EOF
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
M=json.load(open("/var/tmp/souji-r16-RerunMatrixLanding/m.json"))
F=json.load(open("census/round-16/c1-matrix-final.json"))
for arm in M["arms"]:
    for suite in ("r15-config","r14-namespace"):
        a,b=M["arms"][arm][suite]["cases"],F["arms"][arm][suite]["cases"]
        diff=[k for k in a if a[k]["detail"]!=b[k]["detail"]]
        if diff: print(arm,suite,len(diff),sorted(diff))
EOF
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in .ufo/waves/round-16/w1/RevMatrixRunner.md .ufo/waves/round-16/w1/MutateScanConfig.md .ufo/waves/round-16/w1/RevFixtureR16Edits.md; do echo "== $f"; grep -nE "^STATUS:|^# |^## " "$f" | head -12; done
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=46 && NR<=62 {printf "%d\t%s\n", NR, $0}' census/round-16/run-matrix.py; echo ---; awk 'NR>=156 && NR<=167 {printf "%d\t%s\n", NR, $0}' tests/fixtures/r15-census-config.py; echo ---; awk 'NR>=100 && NR<=121 {printf "%d\t%s\n", NR, $0}' census/round-16/run-matrix.py
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=122 && NR<=145 {printf "%d\t%s\n", NR, $0}' census/round-16/run-matrix.py; echo ---; awk 'NR>=1498 && NR<=1514 {printf "%d\t%s\n", NR, $0}' tests/fixtures/r15-census-config.py
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1530 && NR<=1552 {printf "%d\t%s\n", NR, $0}' tests/fixtures/r15-census-config.py
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=655 && NR<=672 {printf "%d\t%s\n", NR, $0}' census/round-16/c1-matrix-final.json
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '"lane_head"\|"changed"\|"fixtures_sha256"\|"r15-config"' census/round-16/c1-matrix-final.json | head -8; echo "---composite input diff 7a79dc2..163158a:"; git diff --stat 7a79dc2 163158a -- tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py census/round-16/run-matrix.py; echo "exit=$?"; echo "---report:"; ls -l .ufo/waves/round-16/w2/RerunMatrixLanding.md; grep -c "" .ufo/waves/round-16/w2/RerunMatrixLanding.md; echo "---my writes in status:"; git status --porcelain | grep -i "RerunMatrixLanding"
```

```bash
cd /var/tmp/souji-r16-RerunMatrixLanding/sc && SHELLCHECK_OPTS='-f gcc' shellcheck -S warning baseline.sh >/dev/null 2>&1; echo "gcc-mode shellcheck rc=$?"; shellcheck -S warning baseline.sh >/dev/null 2>&1; echo "default shellcheck rc=$?"
```

```bash
rm -rf /var/tmp/souji-r16-RerunMatrixLanding && ls -d /var/tmp/souji-r16-RerunMatrixLanding 2>&1; echo "---"; cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -l .ufo/waves/round-16/w2/RerunMatrixLanding.md && git status --porcelain -- .ufo/waves/round-16/w2/ | head
```
