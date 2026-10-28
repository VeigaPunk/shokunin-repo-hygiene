# R41reviewer04 — C3 coverage audit: c3-sites.tsv vs tools/souji-worktree-drift.py

Role: reviewer (leaf, no subagents). Lane freeze: `e2a74312af4233963e44e4dbb38838ece07b8bd2`.
Scope: read-only audit of the frozen population plus one candidate probe fixture under
`.ufo/waves/round-41/w1/R41reviewer04/`. No file under tests/, tools/, census/, corpus/ or any
tracked path was written. The lane was not mutated by any seat command.

## Pinned bytes (checked)

- `tools/souji-worktree-drift.py` sha256 `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6` (= `PRISTINE_SHA256`, c3-counter.py:49).
- `census/round-41/c3-sites.tsv` sha256 `be363c0de5d332dc4223bdf6ccf5f2035e6e38af9cc30735463b07b5d2e764ea` (= `SITES_SHA256`, c3-counter.py:48).
- `census/round-41/c3-counter.py` sha256 `9ef99e8f20805501c3944e4b598e3fd7b7ac3ea3914674fa46e6affdc1e537ca`.
- Environment: uid 1000 (not root), git 2.56.0, Python 3.14.8, /fast is xfs.

## 1. Site order and class labels

Command (read-only, enumerates the frozen counter's own regex `SITE_RE` over the pristine tool):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'PY'
import re,hashlib
src=open('tools/souji-worktree-drift.py',encoding='utf-8').read()
SITE_RE = re.compile(r'(?:Refusal\(\s*"|"REFUSAL )([A-Z]+(?:-[A-Z]+)*):')
for n,m in enumerate(SITE_RE.finditer(src),1):
    ln=src[:m.start(1)].count('\n')+1
    print("S%02d line %d %s"%(n,ln,m.group(1)))
print(hashlib.sha256(src.encode()).hexdigest())
PY
```

Output:

```
S01 line 136 RECORD-MALFORMED
S02 line 137 RECORD-MISSING
S03 line 140 RECORD-MALFORMED
S04 line 161 RECORD-MALFORMED
S05 line 173 RECORD-MALFORMED
S06 line 175 RECORD-EMPTY
S07 line 178 RECORD-MALFORMED
S08 line 180 RECORD-MALFORMED
S09 line 183 RECORD-MALFORMED
S10 line 271 JSON-NOT-REGULAR
S11 line 276 JSON-NOT-REGULAR
S12 line 286 USAGE
S13 line 300 RECORD-OUTSIDE-ROOT
S14 line 317 RECORD-OUTSIDE-ROOT
S15 line 341 JSON-IS-RECORD
S16 line 348 JSON-INSIDE-MEASURED-TREE
S17 line 425 JSON-HARDLINKED
S18 line 435 JSON-UNWRITABLE
S19 line 448 USAGE
b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6
```

Verdict on order and labels: the tsv rows S01..S19 match this sequence row for row (site, class),
and the line numbers are strictly increasing, so source order is the tsv order. The tsv's class
column agrees with each raise site. The site-regex check in the counter (`site_regex=ok`) confirms
the same.

A grep of every refusal emitter confirmed there is no 20th class site. Output of
`grep -n 'Refusal(\|REFUSAL\|sys.exit\|return 2' tools/souji-worktree-drift.py` lists the 19 raise
sites above, the class definition at line 92, the USAGE write at 448-449, and two non-site
pass-throughs: line 453 `sys.stderr.write("REFUSAL %s\n" % exc)` (the class is inside `exc`, no
literal, so no site) and line 454 `return 2`.

Docstring classes (tool lines 47-61): 10, equal to the 10 frozen classes. Probe ids: 21
(P01, P02a, P02b, P03..P09, P10a, P10b, P11..P19), as in the tsv.

## 2. Probe-to-site mapping (per-site evidence)

The probe battery built by me (candidate, section 3) runs each probe with a distinct refusal.
Pristine stderr, observed from my direct run (section 3, output A), shows which code line emitted each
class. Mapping by message text plus code path:

| Site | Line | Probe(s) | Pristine stderr observed (abridged) | Path |
|---|---|---|---|---|
| S01 | 136 | P01 | `RECORD-MALFORMED: .../absent.tsv is not a regular file` | open ENOENT |
| S02 | 137 | P02a, P02b | `RECORD-MISSING: [Errno 13] Permission denied` / `[Errno 40] Too many levels of symbolic links` | open EACCES / ELOOP |
| S03 | 140 | P03 | `RECORD-MALFORMED: .../dir.tsv is not a regular file` | fstat not S_ISREG |
| S04 | 161 | P04 | `RECORD-MALFORMED: line 2 duplicates good` | duplicate REPO |
| S05 | 173 | P05 | `RECORD-MALFORMED: line 2 does not match the census schema` | schema |
| S06 | 175 | P06 | `RECORD-EMPTY: no REPO rows` | no rows |
| S07 | 178 | P07 | `RECORD-MALFORMED: TOTAL repos=2 but 1 REPO rows` | total repos |
| S08 | 180 | P08 | `RECORD-MALFORMED: TOTAL regs=2 but REPO rows sum to 1` | total regs |
| S09 | 183 | P09 | `RECORD-MALFORMED: TOTAL prunable=1 but REPO rows sum to 0` | total prunable |
| S10 | 271 | P10a, P10b | `JSON-NOT-REGULAR: .../out.fifo is not a regular file` / `.../jdir is not a regular file` | open ENXIO / EISDIR |
| S11 | 276 | P11 | `JSON-NOT-REGULAR: /dev/null is not a regular file` | fstat char device |
| S12 | 286 | P12 | `USAGE: --root .../plain-file is not a directory` | root check |
| S13 | 300 | P13 | `RECORD-OUTSIDE-ROOT: ../sibling resolves outside .../root` | row path |
| S14 | 317 | P14 | `RECORD-OUTSIDE-ROOT: linked gitdir resolves outside .../root` | .git file gitdir |
| S15 | 341 | P15 | `JSON-IS-RECORD: .../self.tsv is the record file` | alias |
| S16 | 348 | P16 | `JSON-INSIDE-MEASURED-TREE: .../root/out.json is under .../root` | measured base |
| S17 | 425 | P17 | `JSON-HARDLINKED: .../outside/a.json has 2 links` | nlink > 1 |
| S18 | 435 | P18 | `JSON-UNWRITABLE: [Errno 13] Permission denied: 'out.json'` | open EACCES |
| S19 | 448 | P19 | `USAGE: --timeout must be >= 1` | timeout check |

Every probe's pristine run reaches exactly one site (the table is one-to-one per probe). Each
two-probe site (S02, S10) has both probes reaching the same line by two different errnos.

## 3. Candidate fixture and one-site mutation

Candidate: `.ufo/waves/round-41/w1/R41reviewer04/r41-refusal-sites.py`
(sha256 `7bf528543ced14f95e62a5f716be97a986b3d985160936ab4d07a64abbe54742`). Each probe builds a
hermetic fixture under `--work`, runs the tool, and PASSes only when rc == 2 and stderr begins with
`REFUSAL <exact class>:`. A probe runs only inside its own mkdtemp directory; the EACCES probes
restore permissions in `finally`. It is not a copy of the frozen stub; it has no fixed PASS lines.

### Output A: direct run of the candidate against the pristine tool

Command:

```
S=/fast/scratch/hyaku/souji-r41/R41reviewer04; mkdir -p "$S/direct-work"; cd "$S" && \
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41reviewer04/r41-refusal-sites.py \
  --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --work "$S/direct-work"; echo "EXIT=$?"
```

Output (verbatim, paths in scratch):

```
probe-P01=PASS rc=2 want=RECORD-MALFORMED stderr=REFUSAL RECORD-MALFORMED: .../absent.tsv is not a regular file
probe-P02a=PASS rc=2 want=RECORD-MISSING stderr=REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '.../locked.tsv'
probe-P02b=PASS rc=2 want=RECORD-MISSING stderr=REFUSAL RECORD-MISSING: [Errno 40] Too many levels of symbolic links: '.../loop.tsv'
probe-P03=PASS rc=2 want=RECORD-MALFORMED stderr=REFUSAL RECORD-MALFORMED: .../dir.tsv is not a regular file
probe-P04=PASS rc=2 want=RECORD-MALFORMED stderr=REFUSAL RECORD-MALFORMED: line 2 duplicates good
probe-P05=PASS rc=2 want=RECORD-MALFORMED stderr=REFUSAL RECORD-MALFORMED: line 2 does not match the census schema
probe-P06=PASS rc=2 want=RECORD-EMPTY stderr=REFUSAL RECORD-EMPTY: no REPO rows in .../empty.tsv
probe-P07=PASS rc=2 want=RECORD-MALFORMED stderr=REFUSAL RECORD-MALFORMED: TOTAL repos=2 but 1 REPO rows
probe-P08=PASS rc=2 want=RECORD-MALFORMED stderr=REFUSAL RECORD-MALFORMED: TOTAL regs=2 but REPO rows sum to 1
probe-P09=PASS rc=2 want=RECORD-MALFORMED stderr=REFUSAL RECORD-MALFORMED: TOTAL prunable=1 but REPO rows sum to 0
probe-P10a=PASS rc=2 want=JSON-NOT-REGULAR stderr=REFUSAL JSON-NOT-REGULAR: .../out.fifo is not a regular file
probe-P10b=PASS rc=2 want=JSON-NOT-REGULAR stderr=REFUSAL JSON-NOT-REGULAR: .../jdir is not a regular file
probe-P11=PASS rc=2 want=JSON-NOT-REGULAR stderr=REFUSAL JSON-NOT-REGULAR: /dev/null is not a regular file
probe-P12=PASS rc=2 want=USAGE stderr=REFUSAL USAGE: --root .../plain-file is not a directory
probe-P13=PASS rc=2 want=RECORD-OUTSIDE-ROOT stderr=REFUSAL RECORD-OUTSIDE-ROOT: ../sibling resolves outside .../root
probe-P14=PASS rc=2 want=RECORD-OUTSIDE-ROOT stderr=REFUSAL RECORD-OUTSIDE-ROOT: linked gitdir resolves outside .../root
probe-P15=PASS rc=2 want=JSON-IS-RECORD stderr=REFUSAL JSON-IS-RECORD: .../self.tsv is the record file
probe-P16=PASS rc=2 want=JSON-INSIDE-MEASURED-TREE stderr=REFUSAL JSON-INSIDE-MEASURED-TREE: .../root/out.json is under .../root
probe-P17=PASS rc=2 want=JSON-HARDLINKED stderr=REFUSAL JSON-HARDLINKED: .../outside/a.json has 2 links
probe-P18=PASS rc=2 want=JSON-UNWRITABLE stderr=REFUSAL JSON-UNWRITABLE: [Errno 13] Permission denied: 'out.json'
probe-P19=PASS rc=2 want=USAGE stderr=REFUSAL USAGE: --timeout must be >= 1
SUMMARY probes=21 pass=21 fail=0
EXIT=0
```

(Paths abridged with `...`; full lines are in the scratch run, which is deleted after this report.)

### Output B: frozen scorer on the candidate (advice; the L1 measures)

Command:

```
bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh c3 \
  /fast/scratch/hyaku/souji-r41/R41reviewer04 \
  tests/fixtures/r41-refusal-sites.py=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41reviewer04/r41-refusal-sites.py; echo "EXIT=$?"
```

Output (verbatim):

```
PRISTINE ok rc=0 probes=21 crash=False dup=False summary=(21, 21, 0)
SITE S01 RECORD-MALFORMED killed failing=P01 mapped=P01 rc=1
SITE S02 RECORD-MISSING killed failing=P02a,P02b mapped=P02a,P02b rc=1
SITE S03 RECORD-MALFORMED killed failing=P03 mapped=P03 rc=1
SITE S04 RECORD-MALFORMED killed failing=P04 mapped=P04 rc=1
SITE S05 RECORD-MALFORMED killed failing=P05 mapped=P05 rc=1
SITE S06 RECORD-EMPTY killed failing=P06 mapped=P06 rc=1
SITE S07 RECORD-MALFORMED killed failing=P07 mapped=P07 rc=1
SITE S08 RECORD-MALFORMED killed failing=P08 mapped=P08 rc=1
SITE S09 RECORD-MALFORMED killed failing=P09 mapped=P09 rc=1
SITE S10 JSON-NOT-REGULAR killed failing=P10a,P10b mapped=P10a,P10b rc=1
SITE S11 JSON-NOT-REGULAR killed failing=P11 mapped=P11 rc=1
SITE S12 USAGE killed failing=P12 mapped=P12 rc=1
SITE S13 RECORD-OUTSIDE-ROOT killed failing=P13 mapped=P13 rc=1
SITE S14 RECORD-OUTSIDE-ROOT killed failing=P14 mapped=P14 rc=1
SITE S15 JSON-IS-RECORD killed failing=P15 mapped=P15 rc=1
SITE S16 JSON-INSIDE-MEASURED-TREE killed failing=P16 mapped=P16 rc=1
SITE S17 JSON-HARDLINKED killed failing=P17 mapped=P17 rc=1
SITE S18 JSON-UNWRITABLE killed failing=P18 mapped=P18 rc=1
SITE S19 USAGE killed failing=P19 mapped=P19 rc=1
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=7bf528543ced
EXIT=0
```

Summary line for the frozen target (`SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10`) is met by this candidate. This is a seat score; the L1 measures.

## 4. Equivalent-mutant risk

Test performed: each one-site mutation (class label -> ZZ-MUTANT) killed exactly the mapped probe set
(Output B). No site is unreachable and no probe reaches a second site under the mutation. So no
equivalent mutant exists in the frozen population for the candidate. Named risks (each checked or
stated with evidence):

1. Shared class label, distinct sites (S01/S03; S04..S09): both pairs produce the same class and
   the same message text ("is not a regular file" at 136 and 140). They are separated by control
   flow (ENOENT at open vs non-regular fstat). A class-only assertion alone cannot tell them apart by
   text; the per-site mutation separates them (S01 kills only P01; S03 kills only P03). Risk: a fixture
   that asserts only the class and not the trigger would still kill both, which is correct under
   the counter's rule.
2. Two-probe sites (S02, S10): the counter requires both probes. A fixture that covers one errno
   only gives `misattributed` (failing set is a strict subset), not `killed`. The candidate covers both
   (P02a EACCES, P02b ELOOP; P10a ENXIO, P10b EISDIR).
3. Privilege-dependent sites (S02 via P02a, S18 via P18): as uid 0 the chmod 000 and the unwritable
   directory do not refuse, so the probe would FAIL on pristine (not silently pass). The counter
   refuses uid 0 outright (c3-counter.py:232-234, exit 2). Verified runnable here only as uid 1000.
4. Host dependency (S11 via P11): `/dev/null` must be a character device. If it were a regular
   file on some host, S11 would be unreachable; the probe then FAILs pristine (non-silent). P11 is
   therefore not fully hermetic; the fixture makes no other host-global assumption except git
   (P14).
5. Git dependency (S14 via P14): needs git to resolve a `.git` file whose gitdir lies outside
   root. Verified with git 2.56.0. A git failure during fixture setup makes P14 FAIL (non-silent).
6. Class-only mutation population: the counter mutates only the class token. A mutation that
   changes a site's text but keeps its class is outside the population (a named limit of C3, not a
   defect of this round's sites). Refusal raises not captured by SITE_RE (only literal
   `Refusal("...` and `"REFUSAL ...`) are absent by construction; grep confirms there are none.
7. Non-Refusal exits: uncaught exceptions (for example os.read EIO at line 144, git missing at
   line 115) exit 1 with a traceback and carry no class. They are not in the 19-site population and
   cannot be covered by a class-asserting probe. This is a named limit, not an equivalent mutant.
8. Line 453 `REFUSAL %s` reporter: pass-through of `exc`; mutating the class label there is
   impossible (no literal) and it is not a site. Not a risk.

## 5. Findings for the L1 (no edits made)

- F-R41rv04-1 (none blocking): the frozen population, the pinned tool and the counter agree.
  No defect found in c3-sites.tsv, c3-counter.py or tools/souji-worktree-drift.py for C3.
- F-R41rv04-2 (advice): the counter's SITE_RE only matches double-quoted literals (`Refusal("`,
  `"REFUSAL `). A future refusal written with single quotes or an f-string would silently drop out of
  the population (site_regex would then mismatch and the counter would fail, so this is loud, not
  silent). Not an issue at this pinned sha.

## Verdict

C3 coverage for the frozen population is reachable: the candidate probe battery kills 19 of 19
sites, each to exactly its mapped probe set, with pristine=ok, docclasses=10, 21 probes, no
misattribution. Equivalent-mutant risk: none found for the 19 sites; named limits are items 4-7 above.
This is the reviewer's seat evidence. The L1 must still measure through jj-lane.sh; I did not land
or commit anything.

## Tooling

No tool was installed or upgraded. Only the already-present git 2.56.0 and Python 3.14.8 were used.

## Cleanup

Scratch `/fast/scratch/hyaku/souji-r41/R41reviewer04/` is removed after this report was written
(see the final command in the seat's yield).
