# RevCheckerDiff — source review of the r16 preservation-checker hunks (round 16, W2)

Lane HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
`tools/souji-preservation-evidence.py` sha256
`5942f689a61a25884e52a8f1e377e4b41696bf1b920334a60a989beae1034b2a`, 2653 lines.
Scope: `git diff b410186..HEAD -- tools/souji-preservation-evidence.py`
(54 insertions / 39 deletions, nine hunks). Source review only; this seat has
no ALLOWED-EXEC, so nothing in the checker, the fixture, or the frozen snapshot
was executed here. All measurements below are source plus already-committed
JSON (`census/round-16/c1-matrix-{final,landing}.json`,
`tests/fixtures/r15-preservation-frozen/{record,expected}.json`).

## Axes

- **A1 — CASE grammar.** Does the relaxed `CASE_LINE_RE` parse every real
  fixture row without accepting malformed records, and does it stop rejecting
  the TAB-separated `observed_exit`/`observed_finding` fields?
- **A2 — detail equality.** Does `details_equal` compare the record's printable
  detail against the transcript faithfully, and is the one-sided TAB→space
  normalization sound?
- **A3 — class pins.** Do `CONFIG_BENIGN_IDS / CONFIG_REFUSAL_IDS /
  CONFIG_SAFETY_IDS / CONFIG_PRESERVE_PREHARM / CONFIG_HARM_FAILS` equal the
  per-arm statuses actually measured for the r16 fixture, on the bytes at HEAD?
- **A4 — token pins.** Is `CONFIG_TOKEN_IDS` exactly the changed-arm PASS set
  that carries a concrete `observed_finding`, and are both directions of the
  rule (token required / token must be `none`) enforced in the right channel?
- **A5 — self-description.** Do the file's own oracle documentation and its
  `--selftest` expectations still describe the code after the re-pin?

## Verdicts

| Axis | Verdict | Basis |
|---|---|---|
| A1 | **holds** | `CASE_LINE_RE` at 923 matches every real row; 60/60 config CASE rows in `record.json` carry a TAB inside the detail, which the old `[^\t]*` could not match (anchored `\Z`). New group `(.*)` is still anchored, no DOTALL, empty detail still allowed (needed by `weak-reason`, 2035). A tab-less CASE line still fails to parse → `stdout-parse` (1356-1358). |
| A2 | **holds** | Normalization is exactly the producer's rendering: `regenerate.py:64` (`m.group(3).replace("\t", " ")`) and `_arm` 1845-1848. A declared TAB is unreachable — `_validate_run` 1070-1074 rejects non-printable detail (`"\t".isprintable()` is False), so only the parsed side needs normalizing. Counted in `record.json`: **0 exact / 20 norm-only equal** rows per config arm; namespace rows are exact `ok`. |
| A3 | **holds** | Pins extracted from 323-357 equal the measured statuses in **both** matrices. preharm: PASS = 11 benign ∪ {05}, FAIL = 8 (02,03,08,11,14,17,18,19). harm: FAIL = benign ∪ safety = 16 rows exactly, PASS = 02,05,11,17. changed: 20/20 PASS. Universe = R15CFG-01..20, disjoint, no gaps. Moving **19** to safety is forced by the harm arm (19 FAIL); **20** to benign by preharm PASS + harm FAIL. |
| A4 | **holds** | Changed-arm PASS rows with a non-`none` token are exactly `{02,03,11,14,17,19}` in both matrices (02/11 `path-protected:include-protected`, 03 `config-unsupported:git-include-cycle`, 14 `status-skipped:filter-driver-bound`, 17 `path-protected:include-protected`, 19 `path-protected:credential-store`). Both directions enforce on the transcript (1493-1505) and `case-finding-mismatch` is level 1 (281) → exit 1. Per-arm consistency: preharm PASS 12 rows all `none`; harm PASS 02/11/17 tokened + 05 `none`; changed 6 tokened + 14 `none`. Confirmed directly from `record.json`'s own stdout. |
| A5 | **partial** | 47 selftest appends; `duplicate-id` recomputes as stated (see F4 for the one false clause); `finding-mismatch` count is `len(CONFIG_TOKEN_IDS)`=6. But the header oracle (109-120) and the `_default_detail` docstring (1815-1816) still describe the r15 shape. |

**No behavioral defect was found in the four functional hunks.** The findings
below are one stale contract doc and three calibration gaps in the controls
that pin the changed oracle; none of them alters a current verdict.

## Findings (by severity)

### F1 (medium, documentation) — header oracle still describes the r15 classes
`tools/souji-preservation-evidence.py:109-120` is the file's authoritative
description of the pinned oracle, and the r16 hunk at 323-364 made it false:

- 113 `benign (01,04,06,09,10,12,13,15,16)` — now 11 ids including **07, 20**.
- 114 `refusal (02,03,07,11,14,17,19)` — now **02,11,17**; 03 is safety, 07/20
  benign, 19 safety.
- 115 `safety (08)` — now **03,08,14,18,19**.
- 116 `preserve (05 pass / 18,20 fail preharm …)` — now only **05**; 18 is
  safety, 20 benign.
- 119-120 "A refusal PASS must carry …" — the token set now also includes the
  non-refusal degrade/skip rows **03,14,19**.

Evidence: identical text at `b410186` where it matched that commit's tables
(extracted literals: benign 9, refusal 7, safety 1, preserve 3); the r16 tables
at 323-364 differ. Note also that the checker's classes are now *behavioral*
(per-arm statuses) and intentionally diverge from the fixture's own
`CASE_CLASSES` (`tests/fixtures/r15-census-config.py:167-175`: 03 `degrade`,
18 `preserve`, 19 `refusal`, 20 `preserve`), so the header should not be read
as the fixture taxonomy.

Minimal patch (replace 109-120):

```
    CONFIG_BENIGN_IDS / CONFIG_REFUSAL_IDS / CONFIG_SAFETY_IDS /
    CONFIG_PRESERVE_PREHARM / CONFIG_TOKEN_IDS   the r15 config case universe

Expected per-case status is recomputed, never trusted (r16 pin):

    benign   (01,04,06,07,09,10,12,13,15,16,20): preharm pass, baseline FAIL, changed pass
    refusal  (02,11,17):                          preharm fail, baseline pass, changed pass
    safety   (03,08,14,18,19):                    preharm fail, baseline FAIL, changed pass
    preserve (05):                                pass on all three arms
    namespace (R14C2-01..12): pass on changed

A PASS whose id is in CONFIG_TOKEN_IDS (refusals plus the degrade/skip rows
03,14,19) must carry a non-"none" observed_finding token; every other PASS
must carry observed_finding=none, else `case-finding-mismatch`.
```

Optional same-theme edit outside this file: the fixture's 20-21 comment
("descriptive table for the independent admission checker") no longer matches
the checker's 18/19/20 classes; its labels are only emitted in `--json`, so
this is documentation only.

### F2 (medium, test control) — the `observed_finding=none` branch of the new token rule is untested
`_eval_arm:1497` rejects a token-id PASS when `finding_tok is None **or**
finding_tok == "none"`. The selftest at 2532-2536 feeds
`"ok observed_exit=0 observed_finding=none"` — **space**-separated, so 1493's
`\tobserved_finding=` never matches and `finding_tok` is `None`. The case
therefore exercises only the first disjunct. Dropping `or finding_tok ==
"none"` leaves 47/47 selftest cases, the external fixture's 8/8, and a clean
`--frozen` verdict all passing (no current input has a token-id PASS with a
present-but-`none` token), while a record whose 02/03/11/14/17/19 PASS claims
`observed_finding=none` would be admitted clean — the exact weak evidence
`CONFIG_TOKEN_IDS` was introduced to reject.

Minimal patch (2535) keeps the expected 6 findings but exercises the real
branch and the A2 normalization:

```
        detail_map = {cid: "ok\tobserved_exit=0\tobserved_finding=none"
                      for cid in sorted(CONFIG_TOKEN_IDS)}
```

(`_arm` 1847-1848 still stores the space form and `_transcript` keeps the TABs,
so `details_equal` continues to hold.)

### F3 (low, test control) — no control makes `details_equal` false
`details_equal` 1388-1392 is new code that is load-bearing for all 60 config
rows in the frozen record (A2), yet no check exercises its reject direction:
`grep` finds no test that mutates a declared `detail`; `structured-disagree`
(2144-2151) flips a **status**, and the two sub-checks share one finding id
(1393), so it cannot isolate the detail comparison. A no-op `details_equal`
(`all(...) -> True`) passes 47/47 and the external fixture's 8/8.

Minimal patch (insert after 2151):

```
        # declared detail disagrees with its own transcript row.
        root = _selftest_root(base, "structured-detail", lane)
        record = _record(root, changed_sha)
        record["runs"]["changed"]["cases"][0]["detail"] += " x"
        cases.append((
            "structured-detail",
            ["--root", str(root), "--record", json.dumps(record)],
            2, ["run-inconsistent"],
            ["souji-preservation-evidence: could-not-evaluate"],
        ))
```

### F4 (low, comment) — `duplicate-id` attributes the two `run-inconsistent` findings to the wrong cause
`2137-2138`: "the first (token-bearing) row wins and the duplicate shows as
declared/parsed disagreement." The first clause is correct (`setdefault`,
1377), which is why the extra `PASS ok` row cannot add
`case-finding-mismatch`. The second clause is false: both sides collapse the
id, so `statuses_equal` and `details_equal` are true; the two
`run-inconsistent` findings are the stale `stdout_sha256` (1337-1340) and
`stdout_bytes_total` (1341-1344), and `summary-mismatch` is the 21-row total
(1398-1400). Exact expected set: `case-duplicate` (1375) + 2×`run-inconsistent`
+ `summary-mismatch`.

Minimal patch:

```
            # r16: with TAB details parseable the duplicate row is parsed;
            # setdefault keeps the first (token-bearing) row, so the two
            # run-inconsistent findings are the stale stdout_sha256 and
            # stdout_bytes_total (1337-1344), not a declared/parsed mismatch.
```

### F5 (low, helper fidelity) — `_default_detail` claims a fixture shape it does not produce
1815-1823 now says "Fixture-shaped detail text … the real r15 fixture emits
TAB-separated …", but for the two ids the same hunk *added* to
`CONFIG_TOKEN_IDS` (03, 14) it emits `guard held … observed_exit=2 …
path-protected`, whereas the measured changed rows are `observed_exit=0` with
`config-unsupported:git-include-cycle` (03) and `status-skipped:filter-driver-bound`
(14) — see `c1-matrix-final.json` `changed.r15-config`. It also emits
`guard held … path-protected` for the namespace ids, while the digest-pinned
r14 fixture emits plain `ok` (record.json `namespace_controls`). The checker
never reads `observed_exit`, and the token check is skipped for namespaces
(1488-1492), so no verdict changes; only the selftest's synthesized evidence
is mislabeled.

Minimal patch (docstring only, no behavior):

```
def _default_detail(cid, status):
    """Synthetic detail text for selftest arms, not a fixture transcript:
    the checker validates only the observed_finding token class here and
    never cross-checks observed_exit."""
```

(The same copied string lives at `tests/fixtures/r15-preservation-evidence.py:104-111`;
that fixture is another seat's scope.)

### F6 (nit, pre-existing dead code the hunk leaves as a trap) — shadowed regex block
Lines **286-290** define `CASE_ID_RE`, `TOOL_LINE_RE`, `TOOL_KIND_RE`,
`CASE_LINE_RE`, `SUMMARY_LINE_RE`; the live definitions are **918-924**, so
287-290 are silently overwritten (the hunk's edit is to the live copy). The
dead `CASE_LINE_RE` at 289 requires a leading `\t` and would parse nothing.
`CASE_ID_RE` (286) and `BENIGN`/`REFUSAL` (1793-1794) are entirely unused —
all present at `b410186` too, so this is not an r16 regression, but the r16
author edited the same constant 630 lines below and should have deleted the
shadow copy. Minimal patch: delete 286-290 and 1793-1794 (verified: no other
references to `CASE_ID_RE`, `\bBENIGN\b`, or `\bREFUSAL\b`).

### F7 (nit, provenance) — pin comment cites a matrix measured on different fixture bytes
310-314 says the classes are "observed in census/round-16/c1-matrix-final.json"
and names the fixture "at 0a70bef". `c1-matrix-final.json` recorded fixture
sha256 `85de2a43…` (the 0a70bef blob); HEAD's fixture is `27474396…` (changed
in c6207bd to cap details). The pins still hold on HEAD's bytes — I re-derived
the same PASS/FAIL and token sets from `c1-matrix-landing.json`
(`fixtures_sha256` = `27474396…`) — but the citation should point at the
landing rerun (or both) so an auditor replays the matrix that measured the
shipped fixture.

## Residual risk / verification notes

- **`evaluate()` re-parse is last-wins.** 1573-1580 re-parses stdout and
  overwrites `_parsed` with a dict comprehension, while `_eval_arm` keeps the
  first occurrence (`setdefault`, 1377). With a duplicate id this can make
  `_arm_verdicts` judge the second row while the per-case check judged the
  first. Only reachable when `case-duplicate` (level 2) already forces
  `could-not-evaluate`, so the exit status cannot change; no test covers a
  duplicate whose second row is FAIL. Pre-existing, not part of the r16 hunk.
- **Empty declared detail is a documented opt-out** (`not detail`, 1389;
  `_validate_run` accepts `""`). A record may therefore leave declared details
  empty and the transcript is not compared; the token rule still reads the
  transcript (1493-1505), so the concrete-finding evidence is still enforced.
  This is the r15 `declared_consistency_only` stance, unchanged by r16.
- **Not run here (no ALLOWED-EXEC):** `--selftest`, `--frozen`, the external
  fixture, and the census matrix. The 47/47 and clean-frozen numbers are other
  seats' executions; this report does not independently confirm them.
- Frozen pin consistency checked read-only: `expected.json` `record_sha256`
  `173db777…` equals sha256(record.json); its three `files` pins equal HEAD's
  bytes (ns `e6a984b1…`, fixture `27474396…`, tool `64a60fd0…`); the record's
  `measured_commit`/`changed`/`namespace_controls` commits are all `c6207bd`,
  which satisfies `_check_bindings` 1270-1297 against the installed tool.

STATUS: ok

## Commands

File reads used the `read` tool (no shell). Shell commands, in order:

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain | head -50 && ls -la tools/ | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline --all -- tools/souji-preservation-evidence.py | head -20 && echo ---- && git diff --stat c6207bd~1 a6ec7810e9b5 -- tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-frozen/ 'tests/fixtures/r15-preservation*'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tools/souji-preservation-evidence.py && git diff --stat 58ace9f..a6ec7810e9b5 -- tools/ tests/fixtures/ | tail -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff b410186..a6ec7810e9b5 -- tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l tests/fixtures/r15-census-config.py && grep -n 'R15CFG-' tests/fixtures/r15-census-config.py | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix-final.json'))
print(type(d), list(d)[:20] if isinstance(d,dict) else len(d))
print(json.dumps(d, indent=1)[:3000])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '120,200p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'CONFIG_FIXTURE\|NAMESPACE_FIXTURE\|CONFIG_TOKEN_IDS\|CONFIG_REFUSAL_IDS\|CONFIG_SAFETY_IDS\|CONFIG_BENIGN_IDS\|CONFIG_PRESERVE' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '\bBENIGN\b\|\bREFUSAL\b\|HARM_CASES\|CASE_CLASSES' tools/souji-preservation-evidence.py tests/fixtures/r15-census-config.py tests/fixtures/r16-landing-gate.py 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '_default_detail\|detail_map' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-preservation-evidence.py | grep -n '\bBENIGN\b\|\bREFUSAL\b' ; echo "--- HEAD uses:"; grep -n 'BENIGN\|REFUSAL' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix-final.json'))
print("top keys:", list(d))
arms=d['arms']
print("arm keys:", list(arms))
for a,v in arms.items():
    print("==",a, list(v))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/c1-matrix-final.json'))
arms=d['arms']
for a in ('pre-harm','r14-harm','changed','r15-baseline'):
    v=arms[a]['r15-config']
    print("###",a,"rc=",v.get('rc'),"total",v.get('total'),"failed",v.get('failed'),"valid",v.get('valid'))
    for cid,row in v['cases'].items():
        print("  ",cid,row['verdict'],repr(row['detail']))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tools/souji-census.sh tests/fixtures/r15-preservation-frozen/record.json && python3 - <<'EOF'
import json,hashlib,pathlib
exp=json.load(open('tests/fixtures/r15-preservation-frozen/expected.json'))
print(json.dumps(exp,indent=1))
rec=pathlib.Path('tests/fixtures/r15-preservation-frozen/record.json').read_bytes()
print("record sha:", hashlib.sha256(rec).hexdigest())
for k,v in exp.get('files',{}).items():
    p=pathlib.Path(k)
    print(k, hashlib.sha256(p.read_bytes()).hexdigest()==v if p.exists() else 'MISSING')
r=json.loads(rec)
print("record fixture sha:", r['fixture']['sha256'])
print("record ns sha:", r['namespace_fixture']['sha256'])
print("changed tool:", r['runs']['changed']['tool'])
maxlen=max((len(c['detail']),arm,c['id']) for arm,run in r['runs'].items() for c in run['cases'])
print("max declared detail len:", maxlen)
print("baseline max:", max((len(c['detail']),c['id']) for c in r['runs']['baseline']['cases']))
print("preharm max:", max((len(c['detail']),c['id']) for c in r['runs']['baseline_preharm']['cases']))
print("ns cases:", [(c['id'],c['status'],c['detail']) for c in r['namespace_controls']['cases']][:3], len(r['namespace_controls']['cases']))
print("stdout head:", repr(r['runs']['changed']['stdout'][:200]))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'frozen\|measured_commit\|expected' tools/souji-preservation-evidence.py | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
try:
    d=json.load(open('census/round-16/c1-matrix-landing.json'))
except Exception as e:
    print("no landing:", e); raise SystemExit
print(list(d))
arms=d['arms']
for a in ('pre-harm','r14-harm','changed'):
    v=arms[a]['r15-config']
    print("###",a,"rc",v.get('rc'),"failed",v.get('failed'),"total",v.get('total'))
    st={cid:row['verdict'] for cid,row in v['cases'].items()}
    toks={cid:row['detail'].split('\t')[-1] for cid,row in v['cases'].items()}
    print("  FAIL:",sorted(c for c,s in st.items() if s=='FAIL'))
    print("  tokens non-none:", sorted(c for c,t in toks.items() if t!='observed_finding=none'))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'observed_finding\|observed_exit' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=280 && NR<=300 {printf "%d:%s\n", NR, $0}' tools/souji-preservation-evidence.py | cat -A | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'TOOL_LINE_RE\|CASE_LINE_RE\|SUMMARY_LINE_RE\|TOOL_KIND_RE\|RECORD_PREFIXES' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for rev in 58ace9f b410186 c6207bd HEAD; do echo "== $rev"; git show $rev:tools/souji-preservation-evidence.py | grep -n 'CASE_LINE_RE\|TOOL_LINE_RE' ; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=910 && NR<=930 {printf "%d:%s\n", NR, $0}' tools/souji-preservation-evidence.py && echo ---- && sed -n '175,185p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^def \|^class ' tools/souji-preservation-evidence.py | awk -F'[ (:]' '{print $2}' | sort | uniq -c | sort -rn | head -20; echo "--- total defs:"; grep -c '^def ' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^def _parse_transcript\|^def _eval_arm\|^def _default_detail\|^def _arm(\|^def evaluate' tools/souji-preservation-evidence.py; echo ---; sed -n '640,700p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'CASE_ID_RE\|MAX_DETAIL_CHARS' tools/souji-preservation-evidence.py && python3 - <<'EOF'
import json
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
print("measured:", r['measured_commit'])
for arm in r['runs']: print(arm, r['runs'][arm]['tool'])
print("ns:", r['namespace_controls']['tool'], "exit", r['namespace_controls']['exit_code'], "summary", r['namespace_controls']['summary'])
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import re, pathlib
text=pathlib.Path('tools/souji-preservation-evidence.py').read_text()
def ids(name):
    m=re.search(r'^%s = \((.*?)^\)' % name, text, re.S|re.M)
    body=m.group(1)
    return re.findall(r'"(R15CFG-\d+)"', body)
ben=ids('CONFIG_BENIGN_IDS'); ref=ids('CONFIG_REFUSAL_IDS'); saf=ids('CONFIG_SAFETY_IDS')
tok=ids('CONFIG_TOKEN_IDS')
print("benign",len(ben),ben)
print("refusal",len(ref),ref)
print("safety",len(saf),saf)
allids=ben+ref+saf+['R15CFG-05']
from collections import Counter
c=Counter(allids)
print("dups:", {k:v for k,v in c.items() if v>1})
print("missing from 01..20:", sorted(set('R15CFG-%02d'%i for i in range(1,21))-set(allids)))
print("token ids:",len(tok),tok)
print("tok subset refusal+safety?", set(tok) <= set(ref)|set(saf))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
for f in ('census/round-16/c1-matrix-final.json','census/round-16/c1-matrix-landing.json'):
    d=json.load(open(f))
    print("==",f, "head", d.get('lane_head'))
    for a,v in d['arms'].items():
        print("  ",a, v.get('rev'), v.get('sha256'), "dirty?", v.get('r15-config',{}).get('valid'))
EOF
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tools/souji-preservation-evidence.py | grep -n 'CASE_ID_RE'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
for arm,run in r['runs'].items():
    parsed={}
    for l in run['stdout'].split('\n'):
        if l.startswith('CASE\t'):
            p=l.split('\t')
            parsed.setdefault(p[1], '\t'.join(p[3:]))
    exact=norm=0; bad=[]
    for c in run['cases']:
        pv=parsed.get(c['id'])
        if pv is None: bad.append((c['id'],'missing')); continue
        if pv==c['detail']: exact+=1
        elif pv.replace('\t',' ')==c['detail']: norm+=1
        else: bad.append((c['id'], 'differs', pv[:60], c['detail'][:60]))
    print(arm, "exact",exact,"norm-only",norm,"bad",bad[:3])
# namespace arm
ns=r['namespace_controls']
print("ns declared detail sample:", ns['cases'][0], "stdout:", repr(ns['stdout'].split('\n')[2]))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,re
r=json.load(open('tests/fixtures/r15-preservation-frozen/record.json'))
for arm,run in r['runs'].items():
    toks={}
    for l in run['stdout'].split('\n'):
        if l.startswith('CASE\t'):
            p=l.split('\t'); detail='\t'.join(p[3:])
            m=re.search(r'\tobserved_finding=([^\t]+)', detail)
            toks.setdefault(p[1], (p[2], m.group(1) if m else None))
    print("==",arm)
    non_none=sorted(c for c,(s,t) in toks.items() if s=='PASS' and t!='none')
    pass_none=sorted(c for c,(s,t) in toks.items() if s=='PASS' and t=='none')
    fail=[c for c,(s,t) in toks.items() if s=='FAIL']
    print("  PASS tokened:",non_none)
    print("  PASS none:",pass_none)
    print("  FAIL:",sorted(fail))
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'Expected per-case status\|benign   (\|refusal  (\|safety   (\|preserve (\|the r15 config case universe' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=100 && NR<=125 {printf "%d:%s\n", NR, $0}' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
for f in ('census/round-16/c1-matrix-final.json','census/round-16/c1-matrix-landing.json'):
    d=json.load(open(f))
    print("==",f)
    print(" fixtures_sha256:", d.get('fixtures_sha256'))
    print(" fixtures_dirty:", d.get('fixtures_dirty'))
    print(" runner:", d.get('runner_sha256'))
    print(" changed rev:", d['arms']['changed'].get('rev'))
EOF
sha256sum census/round-16/run-matrix.py tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for rev in 0a70bef 7a79dc2 c6207bd HEAD; do printf "%s " $rev; git show $rev:tests/fixtures/r15-census-config.py | sha256sum; done; echo ---; git log --oneline -- tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff 0a70bef 7a79dc2 -- tests/fixtures/r15-census-config.py | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk '/^def _selftest/{f=1} f&&/cases.append\(/{c++} f&&/for name, arguments, want_code/{print "appends:", c; f=0}' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'frozen-clean\|"frozen"\|--frozen' tools/souji-preservation-evidence.py | sed -n '1,30p'; echo ---; sed -n '2400,2480p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'detail\|CASE' tests/fixtures/r15-preservation-evidence.py | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '2375,2400p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1375 && NR<=1405 {printf "%d:%s\n", NR, $0}' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1478 && NR<=1512 {printf "%d:%s\n", NR, $0}' tools/souji-preservation-evidence.py; echo ----; awk 'NR>=1064 && NR<=1076 {printf "%d:%s\n", NR, $0}' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-preservation-evidence.py && wc -l tools/souji-preservation-evidence.py && awk 'NR>=307 && NR<=366 {printf "%d:%s\n", NR, $0}' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=2128 && NR<=2150 {printf "%d:%s\n", NR, $0}' tools/souji-preservation-evidence.py; echo ----; awk 'NR>=2528 && NR<=2548 {printf "%d:%s\n", NR, $0}' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1344 && NR<=1378 {printf "%d:%s\n", NR, $0}' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1326 && NR<=1344 {printf "%d:%s\n", NR, $0}' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '2183,2340p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'souji-preservation-evidence\|preservation' .ufo/waves/round-16/w2-spec.json | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la .ufo/waves/round-16/w2/ 2>/dev/null | head -30; echo ----; python3 -c "
import json
d=json.load(open('.ufo/waves/round-16/w2-spec.json'))
print(json.dumps(d,indent=1)[:5000])
"
```
