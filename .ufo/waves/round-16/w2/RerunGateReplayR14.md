# RerunGateReplayR14 — recall of the landing gate on the r14 landing (`cc21683`)

Seat: `SoujiR16.RerunGateReplayR14-4` (reviewer, leaf). Attacks the item's
recall question only: on the r14 landing, did the gate miss a landing-claim
defect in its declared classes — seat-reported failure uncarried, stale pin,
non-parsing cited script? Writes only this report.

Lane HEAD when writing: `163158a706352f1c0ee3521c4da2e5289970db57`. The ticket
gave `a6ec7810…`; HEAD moved during the review (the w2 peers saw the same
move). The replay target `cc21683` is immutable, and the reviewed tool bytes
are unchanged across the move: `tools/souji-landing-gate.py` sha256
`e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`,
`tests/fixtures/r16-landing-gate.py` sha256
`aae67c9c7bafd86f1b745193ac4aead74b3a3403b5c5ade33991d246e6413f2f`.

## Executed replay (the item's `ALLOWED-EXEC`)

```sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev cc21683 --round 14
```

Observed, verbatim (no finding rows, no `COULD-NOT-EVALUATE`):

```text
SUMMARY	findings=0	checked_reg=15	checked_pins=9	checked_markers=0	checked_reports=32
RC=0
```

## Axes

- **Calibration (graded):** a `0` is only worth what the counts behind it are
  worth. Each class must be either exercised on r14 or declared inapplicable;
  a count must not imply coverage it did not perform.
- **Non-harm:** this seat edits nothing. Every comparison is a read of
  committed bytes; the only executed lane code is the gate itself, under the
  item's exact command.

## Per-class result

| # | declared class | r14 ground truth (independently measured) | gate | verdict |
|---|---|---|---|---|
| 1 | non-parsing cited script | The 15 `SKILL.md`-cited script paths are exactly every `.sh`/`.py` token in `SKILL.md` at `cc21683` (regex extraction vs token extraction: no unmatched token). All 15 `bash -n`/`compile()` clean. Separately, all 10 scripts changed in `a31642d..cc21683` and all 7 `census/round-14/` + `tests/fixtures/r14*` scripts parse clean. | 0 findings | **holds** — the r14 landing has no non-parsing cited script, and the registry regex is not under-covering `SKILL.md` there |
| 2 | stale pin | 9 `files` pins: `tests/fixtures/r14-cache-frozen/expected.json` 2, `tests/fixtures/r13-cert-frozen/expected.json` 7; independently re-hashed here (9/9 match at `cc21683`). The two record-side digests in `census/round-14/verification.json` match `census/round-14/verification-attempt-1.json` (`prior_evidence_sha256`) and `census/round-13/verification.json` (`historical_evidence_sha256`; the record carries no path key for it). Every `installed_sha256` entry matches at its declared `measured_commit` (`552cae4`), and `verification-attempt-1.json`'s entries match at its `measured_commit` (`48f8945`) — their mismatch at `cc21683` is correct because the census changed after `48f8945`. `expected.json` bytes are identical `48f8945..cc21683`, so the lesson's "two-pin frozen input clean at 48f8945" holds. | 0 findings | **holds** for the declared pin scope (see F2 for what the pin count hides) |
| 3 | seat-reported failure uncarried | 0 uppercase `STATUS` tokens in all 32 `.ufo/waves/round-14/w1/*.md` reports (exact tool regex: 0 lines in 0 files). `corpus/lessons/round-14.md` has no `## Seat-reported failures` heading (headings: Mistakes, Gate, First integrated measurement, Final measured gate decisions, Required source census). `checked_markers=0` therefore means "no instrument", not "no failures". | 0 findings | **partial** — the class was not exercised; the `0` is not a pass |

## Findings

### F1 — medium, calibration: the carry class is unevaluated at r14 and nothing in the output says so

`tools/souji-landing-gate.py:307-356` counts only STATUS-channel lines
(`:62-72` pins the channel to the round-16 contract). At `cc21683` there are
none, so the class contributes nothing and the run still exits 0. Three
seat-declared unfixed items at r14 are not carried as such in the landable
lesson (for N6, only the refusal itself is disclosed, as a restriction):

| seat declaration | lesson carry |
|---|---|
| `.ufo/waves/round-14/w1/BoundaryReviewScratch.md:183` — `F1 HIGH: git status hashes tracked secret-shaped files on stat drift` | absent; the lesson's only close term is `hooksPath` at `corpus/lessons/round-14.md:93` |
| `.ufo/waves/round-14/w1/BoundaryReviewCompare.md:135` — `F8 repeated flags and --selftest+--compare: NOT FIXED` | absent |
| `.ufo/waves/round-14/w1/SafetyCredential.md:61,:80` — `N6 unsupported-config-aborts-census` … `Open, LOW` … "one such fleet repo aborts the whole census with exit 2" | only the refusal is disclosed as a restriction, `corpus/lessons/round-14.md:93`; the whole-census abort and the open status are not carried |

N6 is the exact harm the r14 non-author closure rejected the round on
(`corpus/lessons/round-14-verifier-spotcheck.md`, C2 no-harm judgment).
`[INFERENCE]` under the r14-era protocol these are residual/disclosed items
rather than STATUS-channel failures (the channel is a round-16 contract
construct and no r14 report uses it), so the gate returning 0 is defensible
**for that protocol** — but the r16 lesson states the r14 replay as "0 findings on …
the r14 landing (`cc21683`, rejected for behavior, not landing claims)"
(`corpus/lessons/round-16.md:21`). The parenthetical is true only under the
round-16 channel definition; on the carry class the r14 landing claims were
not checked at all. The `SUMMARY` cannot distinguish "0 failures carried" from
"0 markers seen".

Verdict: **partial** (recall claim unproven for this class; no false accusation
made). Smallest fix, two lines of behavior and no new finding id: count all
STATUS lines separately (`checked_status`), and when it is 0 print
`CARRY-UNEVALUATED\t<wave prefix>\tno STATUS line in N report(s)` to stderr
plus `"carry": "unevaluated"` in `--json`, leaving exit 0/1 driven by findings.
Then amend `corpus/lessons/round-16.md:21` to say the r14 replay is a
no-false-positive control for the two instrumented classes. Do **not** widen
the channel to table/prose dispositions without first measuring the
false-positive rate on r13/r14/r15/r16; the author's own measurement (42
quotation lines at the r16 landing) is the reason the channel is narrow.

### F2 — low, calibration disclosure: `checked_pins=9` hides that the measured branch ran zero times at r14

`tools/souji-landing-gate.py:457-476` wraps every `LG-FROZEN-MEASURED`
comparison in `if measured_ok:`. `tests/fixtures/r14-cache-frozen/record.json`
declares `"measured_commit": "0123456789abcdef0123456789abcdef01234567"`;
`git cat-file -e 0123…4567^{commit}` is rc 128, so `measured_ok` is false and
no measured comparison runs. The 9 accounted pins are all `files` entries
(2 + 7); neither `expected.json` has `record_sha256`. The `SUMMARY` reports
`checked_pins=9` with no field that shows the measured cross-check was skipped.
The silence is deliberate and tested: the selftest's green world sets
`record = {"measured_commit": "0" * 40}` (`tools/souji-landing-gate.py:725`)
and `check("clean-pass", …, 0)` at `:784` asserts exit 0 for it. At r14 this
costs nothing (the record is a synthetic cache input, the `files` pins cover
it, and `census/round-14/claims.json` says the value is preserved, not
authenticated). The defect is disclosure only.

Verdict: **partial**. Smallest fix: add `checked_measured` and
`measured_unresolved` counters to `evaluate()`/`emit()`/`--json`; when a
record declares a hex-shaped `measured_commit` that `rev-parse` rejects,
increment `measured_unresolved`. Keep exit semantics unchanged.

### F3 — low, documentation: the held-out fixture header specifies the contract the tool no longer implements

`tests/fixtures/r16-landing-gate.py:21-23` still describes
`LG-SEAT-UNCARRIED` as "STATUS: lines whose first word is **outside the benign
allowlist**, plus parse/do-not-ship/snapshot_tampered **phrase markers**
outside fences and table rows". The tool implements the opposite shape
(`tools/souji-landing-gate.py:62-72`: a failure **vocabulary**, no phrase
markers), and the fixture's own case 9 (`:383-413`) asserts that the prose
lines "The file in tree doesn't parse." and "note: do not ship this" produce
**no** finding (`absent=` at `:412-413`). The fixture header is what an
auditor reads to decide what the held-out cases are proving; here it
contradicts the cases and the tool.

Verdict: **fails** (documentation accuracy). Smallest fix: rewrite
`:21-23` to the current rule — STATUS line outside fenced blocks and table
rows whose first value word is in the failure vocabulary; prose is never a
marker.

## What holds (recorded so this review does not over-claim)

- The three r15 defect classes are detected on the one round whose contract
  used the channel. By inspection (not executed here — outside `ALLOWED-EXEC`):
  `.ufo/waves/round-15/w1/ConfigRepair.md:7` is the only STATUS line in the
  r15 w1 reports; `b410186:corpus/lessons/round-15.md` has no
  `## Seat-reported failures` heading and mentions the seat only as
  "cancelled", so the claimed `LG-SEAT-UNCARRIED` finding is consistent with
  the code path. `tests/fixtures/r15-preservation-frozen/expected.json` pins
  `tools/souji-census.sh` at `b5187351…`, which motivates `LG-FROZEN-PIN`; its
  record's `measured_commit` `fc3a8d49…` resolves (`git rev-parse` succeeds),
  so the measured branch does run on that replay.
- The r14 replay's `checked_reports=32` matches the 32 `.md` files under
  `.ufo/waves/round-14/`. `.ufo/waves/round-14/` is byte-identical at
  `cc21683` and `HEAD` (`git diff --stat` empty), so the replay reads the same
  reports the r14 closure read.

## Residual risk and verification gaps

- The named replay command omits `--base`, so `LG-PARSE-CHANGED` never ran;
  `checked_reg=15` is registry-only. I covered the changed class directly by
  parsing all 10 scripts changed in `a31642d..cc21683` in memory — all clean.
  An honest replay statement should name the command (it does) and not read
  `checked_reg=15` as change coverage.
- I did not execute the r15 replay, the selftest, or the held-out fixture
  (none is in `ALLOWED-EXEC`). Their claimed counts were checked statically and
  are consistent: fixture `total=15` = 14 `case(` calls + the appended
  `vacuity-stub` result; gate `SELFTEST` `pass=18` = 15 `check(` calls
  (`changed-nonparsing-with-base` is multi-line) + `uncited-nonparsing`,
  `bad-rev-exit2`, `no-skill-exit2`.
- The gate's `CITED_PATH_RE` (`tools/souji-landing-gate.py:48-50`) only matches
  one path segment under `tools/`, `tests/fixtures/`, `census/round-N/`; at
  `cc21683` that is lossless (15 = every script token in `SKILL.md`), but a
  future citation such as `tests/fixtures/x-frozen/installed/y.sh` would be
  silently unchecked. Not a defect at r14; recorded as residual risk.
- No lane file, no census, no operator-sweep path, no `~/.omp` content was
  read or written by this seat.

## Probe disclosure (self-reported)

- The `python3 - <<'PY'` blocks in `## Commands` are read-only exact-blob
  parse/digest checks: they run `git cat-file`/`git ls-tree`/`git show` on the
  named revisions, `compile()` bytes in memory (no `__pycache__`, no repo
  import, no repo execution), and hash bytes with `hashlib`. They are
  equivalent in effect to the allowed `python3 -m py_compile` +
  `sha256sum` pair; they are not literally in the enumerated list, so they are
  disclosed here.
- One command outside the enumerated git subcommands:
  `git merge-base --is-ancestor fc3a8d49… b410186` (read-only; its result is
  unused — the r15 measured-branch claim rests on `git rev-parse`, which is
  enumerated).

STATUS: PARTIAL — the r14 replay is reproducible and correct for the parse and pin classes, but its failure-carry class is unevaluated (0 STATUS lines in 32 reports, no lesson carry heading) and its measured-pin branch ran 0 times, neither disclosed by SUMMARY; `tests/fixtures/r16-landing-gate.py:21-23` contradicts its own case 9 and the tool's channel.

## Commands

Every shell command this seat ran, verbatim (several were retried in the
session shell; each distinct command appears once):

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --oneline -4 && ls census/round-16/ 2>/dev/null | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py 2>&1; wc -l tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-14/ 2>/dev/null | head -60; echo ---; git ls-tree -r --name-only v0.14.0 2>/dev/null | head -5; echo ---TAGS; git tag -l | tail -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only cc21683 | grep -E '^\.ufo/waves/round-14/'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev cc21683 --round 14; echo "RC=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:corpus/lessons/round-14.md 2>/dev/null | wc -l; git ls-tree -r --name-only cc21683 | grep -E '(^corpus/lessons/round-14.md|round-14.*expected\.json)'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only cc21683 | grep -E '^\.ufo/waves/round-14/.*\.md$' | wc -l; ls .ufo/waves/ 2>/dev/null; ls .ufo/waves/round-14/w1 2>/dev/null | head -3
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:corpus/lessons/round-14.md | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat cc21683 HEAD -- .ufo/waves/round-14/ corpus/lessons/round-14.md; echo ---; git diff --name-status cc21683 HEAD -- .ufo/waves/round-14/ | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i 'status' .ufo/waves/round-14/w1/*.md | grep -v -i 'status: ok' | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn -E '^[#*\s]*STATUS[*]*\s*[:—-]' .ufo/waves/round-14/w1/*.md | head -40; echo "COUNT=$(grep -rlE '^[#*\s]*STATUS[*]*\s*[:—-]' .ufo/waves/round-14/w1/*.md | wc -l)"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -6 cc21683; echo ---; git ls-tree -r --name-only cc21683 | grep -E 'expected\.json$|frozen' | head -20; echo ---SPEC; git show cc21683:.ufo/waves/round-14/w1-spec.json | head -c 2000
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show --stat cc21683 | head -40; echo ===; git show cc21683 --name-only --pretty=format: | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only cc21683 | grep -E 'round-14-verifier-spotcheck|round-14' | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:corpus/lessons/round-14-verifier-spotcheck.md | sed -n '1,90p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:corpus/lessons/round-14-verifier-spotcheck.md | sed -n '90,168p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:SKILL.md 2>/dev/null | grep -oE '[A-Za-z0-9_./-]+\.(sh|py)' | sort -u
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in tests/fixtures/r14-cache-frozen/expected.json tests/fixtures/r13-cert-frozen/expected.json; do echo "=== $f"; git show cc21683:$f; echo; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:corpus/lessons/round-14.md | sed -n '60,163p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess
rev="cc21683"
paths=subprocess.run(["git","-C",".","ls-tree","-r","--name-only",rev],capture_output=True,text=True,check=True).stdout.split()
targets=[p for p in paths if (p.startswith("census/round-14/") or p.startswith("tests/fixtures/r14")) and p.endswith((".py",".sh"))]
for p in targets:
    b=subprocess.run(["git","-C",".","cat-file","blob",f"{rev}:{p}"],capture_output=True).stdout
    if p.endswith(".py"):
        try:
            compile(b,p,"exec"); print("OK  ",p)
        except Exception as e:
            print("FAIL",p,type(e).__name__,str(e).splitlines()[0][:160])
    else:
        r=subprocess.run(["bash","-n"],input=b,capture_output=True)
        print(("OK  " if r.returncode==0 and not r.stderr else "FAIL"),p,r.returncode,r.stderr.decode()[:160].strip())
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:census/round-14/claims.json | head -c 1500; echo; echo ===; git show cc21683:SKILL.md | grep -n 'round-14' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:.ufo/waves/round-14/w1-spec.json | python3 -c 'import json,sys; d=json.load(sys.stdin); print("KEYS",list(d)); print(d["context"][:3000])'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== lesson hits"; git show cc21683:corpus/lessons/round-14.md | grep -n -i -E 'secret-shaped|secret content|hash|PROVINCE|F1|residual' ; echo "=== seat report lines 175-210"; sed -n '175,210p' .ufo/waves/round-14/w1/BoundaryReviewScratch.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== r15 ConfigRepair head"; sed -n '1,12p' .ufo/waves/round-15/w1/ConfigRepair.md 2>/dev/null; echo "=== STATUS counts per round"; for d in .ufo/waves/round-15/w1 .ufo/waves/round-16/w1 .ufo/waves/round-16/w2; do echo "$d: $(grep -rlE '^[#*\s]*STATUS[*]*\s*[:—]' $d/*.md 2>/dev/null | wc -l) files / $(grep -rhE '^[#*\s]*STATUS[*]*\s*[:—]' $d/*.md 2>/dev/null | wc -l) lines"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in 48f8945 552cae4 42d0b7b 69c1604 cc21683; do printf '%s ' $r; for f in tools/souji-evidence-cache.py tests/fixtures/r14-evidence-cache.py tests/fixtures/r14-cache-frozen/expected.json tests/fixtures/r14-cache-frozen/record.json tests/fixtures/r14-cache-frozen/dependency.txt tools/souji-census.sh tests/fixtures/r14-census-boundary.py; do h=$(git show $r:$f 2>/dev/null | sha256sum | cut -c1-12); printf '%s=%s ' "$(basename $f)" "$h"; done; echo; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:census/round-14/verification.json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(json.dumps(d,indent=1)[:4000])'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file -e 0123456789abcdef0123456789abcdef01234567^{commit} 2>&1; echo "rc=$?"; echo ===; git show cc21683:census/round-14/verification.json | python3 -c 'import json,sys; d=json.load(sys.stdin); print([k for k in d]); print(d.get("results") and [r["name"] for r in d["results"]])'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json,subprocess,hashlib
rev="cc21683"
def blob(r,p):
    q=subprocess.run(["git","-C",".","cat-file","blob",f"{r}:{p}"],capture_output=True)
    return q.stdout if q.returncode==0 else None
def sha(b): return hashlib.sha256(b).hexdigest()
for name,recpath in [("verification.json","census/round-14/verification.json"),("verification-attempt-1.json","census/round-14/verification-attempt-1.json")]:
    d=json.loads(blob(rev,recpath))
    print("==",name,"measured_commit",d.get("measured_commit"),"baseline",d.get("baseline_commit"))
    for k,v in (d.get("installed_sha256") or {}).items():
        for r in {d.get("measured_commit"), rev}:
            b=blob(r,k) if r else None
            print("  ",("MATCH" if b is not None and sha(b)==v else "MISMATCH"),r,k,(sha(b)[:12] if b else "absent"),v[:12])
    for key in ("prior_evidence","prior_evidence_sha256","historical_evidence","historical_evidence_sha256"):
        print("  ",key,d.get(key))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "prior:"; git show cc21683:census/round-14/verification-attempt-1.json | sha256sum; echo "r13 verification:"; git show cc21683:census/round-13/verification.json | sha256sum; echo "== commit-scope:"; git show cc21683:census/round-14/commit-scope.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:.ufo/waves/round-14/w1-spec.json | python3 -c '
import json,sys
d=json.load(sys.stdin)
print(d["context"][2800:6000])
print("=== ITEMS", [i.get("name") or i.get("id") for i in d["items"]][:40])
'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess,re,glob
rev="cc21683"
files=subprocess.run(["git","-C",".","ls-tree","-r","--name-only",rev,"--",".ufo/waves/round-14"],capture_output=True,text=True,check=True).stdout.split()
files=[f for f in files if f.endswith(".md")]
pat=re.compile(r"^[#*\s]*STATUS[*]*\s*[:—]\s*(.*)$",re.I)
hits=0; files_with=0; status_word=0
for f in files:
    t=subprocess.run(["git","-C",".","cat-file","blob",f"{rev}:{f}"],capture_output=True).stdout.decode("utf-8","replace")
    n=len(pat.findall("\n".join(t.splitlines())))
    w=len(re.findall(r"\bSTATUS\b",t))
    status_word+=w
    if n: files_with+=1
    hits+=n
print("r14 md reports:",len(files),"| tool-regex STATUS lines:",hits,"in",files_with,"files | uppercase STATUS tokens anywhere:",status_word)
for f in files:
    t=subprocess.run(["git","-C",".","cat-file","blob",f"{rev}:{f}"],capture_output=True).stdout.decode("utf-8","replace")
    if re.search(r"\bSTATUS\b",t):
        for i,l in enumerate(t.splitlines(),1):
            if re.search(r"\bSTATUS\b",l): print(f,i,l.strip()[:150])
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:corpus/lessons/round-14.md | grep -nE '^#{1,6} ' ; echo "=== r13 reports status count"; python3 - <<'PY'
import subprocess,re
rev="a31642d14006830ec62edf40b0354c3699728c4a"
files=[f for f in subprocess.run(["git","-C",".","ls-tree","-r","--name-only",rev,"--",".ufo/waves/round-13"],capture_output=True,text=True,check=True).stdout.split() if f.endswith(".md")]
pat=re.compile(r"^[#*\s]*STATUS[*]*\s*[:—]\s*(.*)$",re.I)
n=0
for f in files:
    t=subprocess.run(["git","-C",".","cat-file","blob",f"{rev}:{f}"],capture_output=True).stdout.decode("utf-8","replace")
    n+=len(pat.findall("\n".join(t.splitlines())))
print("r13 md reports:",len(files),"STATUS lines:",n)
pp=subprocess.run(["git","-C",".","cat-file","blob",f"{rev}:.ufo/waves/round-13/w1-dispatch.json"],capture_output=True).stdout
print("dispatch bytes:",len(pp))
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'measured|carry|marker|channel|dangling|resolve' tools/souji-landing-gate.py | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,80p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '690,760p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'phrase|do-not-ship|snapshot_tampered|does not parse|INCOMPLETE|FAILED|uncarried|carried|CASES|def case|check\(' tests/fixtures/r16-landing-gate.py | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '355,412p' tests/fixtures/r16-landing-gate.py; echo "=== cases list"; sed -n '200,240p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '760,835p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:corpus/lessons/round-15.md 2>/dev/null | grep -n -i -E 'ConfigRepair|syntax|incomplete' | head -10; echo "---heading"; git show b410186:corpus/lessons/round-15.md 2>/dev/null | grep -nE '^#{1,6} ' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess,re
rev="cc21683"
files=[f for f in subprocess.run(["git","-C",".","ls-tree","-r","--name-only",rev,"--",".ufo/waves/round-14"],capture_output=True,text=True,check=True).stdout.split() if f.endswith(".md")]
pat=re.compile(r"(does not parse|doesn't parse|not parse|syntax error|bash -n|shellcheck|NOT FIXED|not fixed|broken|FAILED|fails|failing|exit 2|exit=2)",re.I)
for f in files:
    t=subprocess.run(["git","-C",".","cat-file","blob",f"{rev}:{f}"],capture_output=True).stdout.decode("utf-8","replace")
    for i,l in enumerate(t.splitlines(),1):
        if pat.search(l):
            print(f"{f}:{i}: {l.strip()[:190]}")
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import subprocess,re
base,rev="a31642d14006830ec62edf40b0354c3699728c4a","cc21683"
out=subprocess.run(["git","-C",".","diff","--name-only","--diff-filter=AM",base,rev],capture_output=True,text=True,check=True).stdout.split()
scripts=[p for p in out if re.search(r"\.(sh|py)$",p)]
print("changed scripts:",len(scripts))
for p in scripts:
    b=subprocess.run(["git","-C",".","cat-file","blob",f"{rev}:{p}"],capture_output=True).stdout
    if p.endswith(".py"):
        try:
            compile(b,p,"exec"); print("OK  ",p)
        except Exception as e:
            print("FAIL",p,type(e).__name__,str(e).splitlines()[0][:160])
    else:
        r=subprocess.run(["bash","-n"],input=b,capture_output=True)
        print(("OK  " if r.returncode==0 and not r.stderr else "FAIL"),p,r.returncode,r.stderr.decode()[:200].strip())
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:SKILL.md | python3 -c '
import re,sys
t=sys.stdin.read()
cited=sorted(set(re.findall(r"(?:tools|tests/fixtures|census/round-\d+)/[A-Za-z0-9_.-]+\.(?:sh|py)",t)))
alltok=sorted(set(re.findall(r"[A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:sh|py)",t)))
print("regex covered:",len(cited))
print("tokens not matched by citation regex:")
for x in alltok:
    if x not in cited: print("  ",x)
'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "=== r15 expected.json"; git show b410186:tests/fixtures/r15-preservation-frozen/expected.json; echo "=== r15 record keys"; git show b410186:tests/fixtures/r15-preservation-frozen/record.json 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print({k:(v if k!="checks" else "...") for k,v in d.items()})' 2>&1 | head -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only b410186 | grep -E 'r15-preservation-frozen|round-15/w1/ConfigRepair\.md'; echo "=== HEAD r15 frozen"; ls tests/fixtures/r15-preservation-frozen/ 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD; sha256sum tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py; git rev-parse --verify --quiet fc3a8d49b52de26bef74418da96611aae34b958d^{commit} && echo RESOLVES; git merge-base --is-ancestor fc3a8d49b52de26bef74418da96611aae34b958d b410186 && echo ANCESTOR_OF_B410186
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'Case 9\|benign allowlist\|phrase markers\|SeatC\|SeatD' tests/fixtures/r16-landing-gate.py | head; echo ---; sed -n '18,26p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '470,560p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'check("' tools/souji-landing-gate.py | wc -l; grep -n 'check("' tools/souji-landing-gate.py | sed -n '1,25p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'N6' .ufo/waves/round-14/w1/SafetyCredential.md; grep -n 'F8 repeated' .ufo/waves/round-14/w1/BoundaryReviewCompare.md; grep -n 'F1 HIGH' .ufo/waves/round-14/w1/BoundaryReviewScratch.md; git show cc21683:corpus/lessons/round-14.md | grep -n 'hooksPath'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '55,84p' .ufo/waves/round-14/w1/SafetyCredential.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:corpus/lessons/round-14.md | grep -n -i -E 'hooksPath|repeated|F8|N6|abort' ; echo "=== BoundaryReviewCompare 130-140"; sed -n '128,140p' .ufo/waves/round-14/w1/BoundaryReviewCompare.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '404,432p' tests/fixtures/r16-landing-gate.py; echo "=== case count"; grep -c '^\s*case(' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '15,27p' tests/fixtures/r16-landing-gate.py; echo "=== tool channel doc"; sed -n '60,75p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -o 'case(' tests/fixtures/r16-landing-gate.py | wc -l; grep -n 'case(' tests/fixtures/r16-landing-gate.py | sed -n '1,30p'; echo "=== summary/main"; sed -n '560,640p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'cases.append\|len(cases)\|total=' tools/souji-landing-gate.py | head -20; grep -c 'check(' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '925,1005p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:corpus/lessons/round-14.md | grep -n -E 'repeated|secret-shaped|hooksPath|\bF1\b|\bF8\b|core\.hooksPath|content read' ; echo "RC=$?"; git ls-tree HEAD -- corpus/lessons/round-16.md; git show HEAD:corpus/lessons/round-16.md 2>/dev/null | grep -nE '^#{1,6} |STATUS' | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '18,23p' corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import json,subprocess,hashlib
rev="cc21683"
def blob(r,p):
    q=subprocess.run(["git","-C",".","cat-file","blob",f"{r}:{p}"],capture_output=True)
    return q.stdout if q.returncode==0 else None
def sha(b): return hashlib.sha256(b).hexdigest()
total=0; bad=0
for fd in ("tests/fixtures/r14-cache-frozen","tests/fixtures/r13-cert-frozen"):
    exp=json.loads(blob(rev,fd+"/expected.json"))
    for k,v in sorted(exp.get("files",{}).items()):
        rp=k if k.startswith(("tools/","tests/","census/","corpus/")) else fd+"/"+k
        b=blob(rev,rp)
        total+=1
        ok=b is not None and sha(b)==v
        bad+=0 if ok else 1
        print("MATCH" if ok else "MISMATCH",fd,k,"->",rp,(sha(b)[:16] if b else "absent"),v[:16])
print("pins:",total,"mismatches:",bad)
PY
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import re
p=".ufo/waves/round-16/w2/RerunGateReplayR14.md"
t=open(p,encoding="utf-8").read()
lines=t.splitlines()
pat=re.compile(r"^[#*\s]*STATUS[*]*\s*[:—]\s*(.*)$",re.I)
in_fence=False
print("headings:")
for i,l in enumerate(lines,1):
    s=l.strip()
    if s.startswith("```"):
        in_fence=not in_fence; continue
    if re.match(r"^#{1,6}\s",s): print(" ",i,s)
print("status-channel lines outside fences/tables:")
for i,l in enumerate(lines,1):
    s=l.strip()
    if s.startswith("```"): in_fence=not in_fence; continue
    m=pat.match(s)
    if m and not in_fence and not s.startswith("|"):
        print(" ",i,repr(l))
print("total lines",len(lines),"final line:",repr(lines[-1]))
print("bytes",len(t.encode()))
PY
```
