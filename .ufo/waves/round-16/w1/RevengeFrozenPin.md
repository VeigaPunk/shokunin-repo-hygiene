# RevengeFrozenPin — provenance of `b51873514d1f…` (r16, w1)

Seat: revenger, leaf. Axes: calibration (primary), operability (secondary).
Scope: where the r15 frozen pin for `tools/souji-census.sh` came from. Read-only;
no tests, no fixture/census runs, no edits outside this report.

## Answer

`b5187351…` is **not a measurement of any committed `tools/souji-census.sh`
byte**, and it is not a git object at all. It entered the
repository as an authored constant in the frozen fixture written by
`SoujiR15.AdmissionChecker`, a seat that (a) declared it executed nothing and
(b) was scoped to two files that do not include the frozen directory. The value
was attached to commit `fc3a8d4` only because that was the commit the record
names as its measurement point; `fc3a8d4` never contained those bytes (its
`tools/souji-census.sh` is `fcff8b05…`, the r14 harm tool). The saved stdout is
not captured fixture output either: it prints a relative tool path while both
pinned fixtures resolve and print an absolute one. So the pin's provenance is
"declared", with no recoverable byte source, and the transcript that carries it
is unreproducible.

## Evidence chain (all observed)

### 1. The value is not a committed blob, and not even a git object

Distinct blobs ever committed for `tools/souji-census.sh` (every revision
returned by `git log --all --format=%H -- tools/souji-census.sh`, plus the
pre-harm reference):

| revision | context | sha256 of `git show <rev>:tools/souji-census.sh` |
|---|---|---|
| `b5db5cf` | r6 | `11bf9cdf8d4f75415b18e046aef0e96215b983f0d5b3ff7842301ff6ac65d381` |
| `43d5754` | r11 | `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026` |
| `a31642d` | r14 pre-harm (unmodified path) | `6a000c59…` (same) |
| `48f8945` | r14 intermediate | `fd234148f0c44bcd1edc6857388e08354eba0bc98a59b78e480adf5ab2c3028c` |
| `552cae4`, `cc21683`, **`fc3a8d4`** | r14 changed / r15 baseline / r15 learn | `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` |
| `b410186` | r15 landing ("acceptance unrun") | `dab4122c997db9b921e036ec8e2adf4c0e4743d8722ba9b2a28739bda9397810` |
| `cbf688ab` | r16 C1 repair (HEAD) | `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` |

`b51873514d1f6d34a5e3427bf30c95686a5d27b6ec9b8332034c3a3ba7868e02` is in none of
them, and it is not an object of any type in the object database:
`git cat-file -t b518735…` → `fatal: Not a valid object name`. It was therefore
never committed; it is also absent from the object database entirely (a
staged-but-uncommitted blob would normally still be present), so no authored
bytes of it survive.

Exactly two committed files carry the literal: `tests/fixtures/r15-preservation-frozen/expected.json`
(`:5`) and `record.json` (`:93`, `:482`, and inside the stdout text at `:82`,
`:471`). No seat report, claim, runner or checker source quotes it
(`git grep b518735` at `b410186` over `tests tools .ufo/waves census/round-13
census/round-14 census/round-15 corpus` → those two files only;
`tools/souji-preservation-evidence.py` and `tests/fixtures/r15-preservation-evidence.py`
contain no pin literal for the changed tool at all).

### 2. The commit binding is value-blind

- `record.json:7` — `"measured_commit": "fc3a8d49…"`.
- `record.json:92-93` — namespace tool `commit: fc3a8d49…`, `sha256: b5187351…`.
- `record.json:481-482` — changed tool `commit: fc3a8d49…`, `sha256: b5187351…`.

`fc3a8d49b52de26bef74418da96611aae34b958d` is a real commit ("round-15: learn
rejected-harmed config preservation and declare repairs", parent `cc21683`,
2026-10-20 05:28:44 -0300) and an ancestor of `b410186`. Its
`tools/souji-census.sh` hashes to `fcff8b05…`, i.e. **the same bytes the record's
own baseline arm measures and scores 10 FAIL / 20** (`record.json` `runs.baseline`,
summary `{failed: 10, total: 20}`). If `b5187351…` were the blob at `fc3a8d4`,
the two arms would be the same bytes with opposite verdicts. They are not the
same bytes, so the commit field names HEAD at authoring time, not the bytes it
claims to bind — precisely the hazard `CheckerBindings.md` F3 names ("commit
binding is recorded, not verified"; round-14 closed this class as value-blind).

### 3. The 20/20 "changed" transcript is not reproducible from the pinned fixtures

The record's saved stdout for the changed arm (`record.json:471`) and for the
namespace arm (`record.json:82`) begins:

```
TOOL	tools/souji-census.sh	sha256=b51873514d1f…
```

Both fixtures whose digests the record itself pins resolve the tool path and
print the **absolute** path:

- `tests/fixtures/r15-census-config.py` at `b410186` (pinned `6314d45d…`):
  `:1318-1322` `TOOL = … Path(args.tool) …` then `TOOL = TOOL.resolve()`;
  `:1350` `print(f"TOOL\t{TOOL}\tsha256={digest}")`.
- `tests/fixtures/r14-census-boundary.py` at `b410186` (pinned `e6a984b1…`):
  `:681-682` same construction and `TOOL.resolve()`; `:704` same print.

A genuine run with the recorded argv `--tool tools/souji-census.sh` would print
the resolved lane-absolute path. The record prints the raw argument, so the
saved text is at minimum hand-normalized and, given the author's own
no-execution declaration (below), has no capture provenance. This is
independent of any question about the digest: the transcript is inconsistent
with the fixture identity the record pins.

### 4. Who wrote it, and with what authority

- `AdmissionChecker.md:9` lists the three frozen files under "Files written".
- `AdmissionChecker.md:87`: "No installs performed; no runtime tests executed
  (source inspection only)."
- Its assignment (`.ufo/waves/round-15/w1-spec.json:28`) read: "Own ONLY
  `tools/souji-preservation-evidence.py` plus
  `tests/fixtures/r15-preservation-evidence.py`. … no runtime tests." The
  frozen directory was outside that OWN-ONLY list; `AdmissionRules.md:101`
  later claimed write scope `tests/fixtures/r15-*` (seat-authored, not authority).
- `AdmissionChecker.md:73`: "Frozen fixture ships pre-integration pins … This is
  fail-closed by design, not a defect."
- `README.md:7-18`: "These pins were authored before the C1 repair of
  `tools/souji-census.sh` landed. As shipped they describe a pre-integration
  snapshot …" and the refresh recipe: set `measured_commit`,
  `runs.changed.tool.commit`, `namespace_controls.tool.commit` to the
  integration commit; set the three digests "to the final file digests".

So the pin was authored for a file that **did not yet exist**, by a seat that
ran nothing, and bound to the then-HEAD commit. The other seats are ruled out as
sources by their own text: `ConfigRepair.md:4` ("No runtime checks … executed"),
`ConfigRepair.md:7-13` (the tree file "does NOT parse"; `bash -n` fails at line
1368), `RoundRunner.md:4` ("No commits, no execution, no tests"),
`FixtureCounts.md:4` (design-only; it proposes a 49-ID matrix, not the landed
20, and quotes no pin). `RoundRunner.md` designs a record "synthesized verbatim
from captured runs", but reports no execution, and its designed transcripts
would carry resolved absolute `TOOL` paths.

### 5. Why the gate could not catch it

`tools/souji-preservation-evidence.py` pins literals for the baseline
(`BASELINE_COMMIT` `:302`, `PREHARM_COMMIT` `:300`) and the namespace fixture
(`:306`) but holds **no literal for the changed tool**; per `AdmissionChecker.md`
it "consumes JSON + file hashes only" and never runs git. `--frozen` compares
the record's declared digests against files under `--root`; it cannot compare a
pin to `git cat-file blob <commit>:<path>`. The r15 closure independently
confirms the result at `corpus/lessons/round-15-verifier-spotcheck.md:56`:
the pin "matches no committed revision (cc21683/fc3a8d4 `fcff8b05…`, b410186
`dab4122c…`)", so a frozen run is `snapshot_tampered`, never the pinned `clean`;
`:125` is R4.

## Reconstruction (labelled)

1. [observed] AdmissionChecker authored `record.json`/`expected.json`/`README.md`
   before the tool repair landed, declaring `measured_commit`/`tool.commit` as
   the then-HEAD `fc3a8d4`, and a changed digest `b5187351…`.
2. [INFERENCE, high] It typed/derived the digest while the changed artifact did
   not exist (README's own "authored before … landed"). The only two
   possibilities — a digest of an uncommitted scratch candidate, or an invented
   value — are indistinguishable from committed evidence and equally fatal,
   because nothing in the record ties the value to bytes. Do not claim which.
3. [observed] The 20/20 changed transcript is hand-normalized at minimum
   (relative `TOOL` vs. the pinned fixtures' resolved absolute `TOOL`), and its
   author declares no execution.
4. [observed] The candidate landed broken: `b410186` carries `dab4122c…`, which
   `ConfigRepair.md:7-13` and the closure `:7` say does not parse. The digest's
   alleged artifact was thus superseded twice (`dab4122c…`, then `fed43c71…` at
   `cbf688ab`) without the pin ever being re-derived.
5. [observed] The pin is unchanged at `cbf688ab` (`expected.json:5`,
   `record.json:93,482`), so R4 is still open. The r16 `PreservationRepin` seat
   owns the frozen dir (`.ufo/waves/round-16/w1-spec.json:26`).

## Divergences and the trap in the refresh recipe

- **D1 (calibration, R4):** pin ≠ any committed byte; frozen `clean` is
  unreachable and was never reachable at `b410186`.
- **D2 (calibration):** commit binding is a label, not a proof — `fc3a8d4` holds
  the harm bytes, and the record's own baseline arm says so.
- **D3 (calibration):** changed/namespace transcripts contradict the pinned
  fixture identity (path normalization) and the changed arm contradicts the
  baseline arm measured on the same commit.
- **D4 (process):** the fixture was authored outside the seat's OWN-ONLY scope
  and without execution.
- **D5 (calibration, the laundering path):** `README.md:12-18` instructs a
  digest-only re-pin. Following it overwrites `runs.changed.tool.sha256` and
  `files["tools/souji-census.sh"]` with the new file digest while **keeping the
  authored 20/20 transcript**, i.e. it pairs transcript-of-X with digest-Y and
  would turn R4 into a `clean` verdict without ever reproducing the run. A
  re-pin must be a re-measurement: re-run the matrix at the integration commit,
  re-capture each arm's stdout, and set `measured_commit` to a commit whose
  `git cat-file blob <rev>:tools/souji-census.sh` equals the pinned digest
  (for `cbf688ab`: `fed43c71…`). If any arm cannot be re-captured, the honest
  state is a non-`clean` verdict with the arm marked unattested — not `clean`.

## Input for the mistake row (calibration)

> A frozen pin was authored before its artifact existed, bound to a commit that
> never held those bytes, and never re-derived; the QA gate could not see it
> because commit binding was recorded rather than verified, and the published
> re-pin recipe refreshed digests while preserving a transcript produced by
> other (or no) bytes.

Rule that should block it next time: a pin may name a commit only after
`git cat-file blob <commit>:<path>` equals the pin; a saved transcript may be
admitted only if re-derivable from the pinned fixture digest and argv
(including path-normalization semantics); re-pinning is re-running and
re-capturing, never a digest-only rewrite.

## Confidence

High on every observed fact (digests, line numbers, declarations, transcript
inconsistency). The specific numeric origin of `b5187351…` (scratch candidate vs.
invented value) is **unrecoverable from committed evidence** and is not
asserted; the calibration finding does not depend on which it was.

STATUS: `b5187351…` is unattested — no committed blob, no odb object, no reproducible transcript; frozen verdict `clean` is unreachable at `b410186` and the pin is still unrepaired at `cbf688ab`.

## Commands

Every shell command run by this seat, in order:

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r b410186 -- tests/fixtures/r15-preservation-frozen/ && echo '---EXPECTED---' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r15-preservation-frozen/expected.json && echo '---RECORD---' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r15-preservation-frozen/record.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '---README---' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r15-preservation-frozen/README.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== blob at fc3a8d49 ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse fc3a8d49^{commit} 2>&1; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show fc3a8d49:tools/souji-census.sh 2>&1 | sha256sum; echo '=== blob at b410186 ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tools/souji-census.sh | sha256sum; echo '=== blob at cc21683 ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cc21683:tools/souji-census.sh | sha256sum; echo '=== blob at cbf688ab ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab:tools/souji-census.sh | sha256sum; echo '=== blob at a31642d ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show a31642d:tools/souji-census.sh | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== all revisions touching tools/souji-census.sh ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline --all -- tools/souji-census.sh | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== is b518735 an object in odb? ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t b51873514d1f6d34a5e3427bf30c95686a5d27b6ec9b8332034c3a3ba7868e02 2>&1; echo '=== is fc3a8d49 a commit? ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t fc3a8d49 2>&1; echo '=== fixture hashes at b410186 ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r15-census-config.py | sha256sum; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r14-census-boundary.py | sha256sum; echo '=== record.json hash at b410186 ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r15-preservation-frozen/record.json | sha256sum; echo '=== expected.json hash at b410186 ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r15-preservation-frozen/expected.json | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== CheckerBindings.md ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1/CheckerBindings.md 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== CheckerGreen.md ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1/CheckerGreen.md 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== fc3a8d49 identity ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --no-patch --format='%H%n%P%n%ad%n%s' fc3a8d49; echo '=== ancestry ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin merge-base --is-ancestor fc3a8d49 b410186 && echo 'fc3a8d49 IS ancestor of b410186'; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline cc21683..b410186 | head -20; echo '=== HEAD ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== FixtureCounts.md ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1/FixtureCounts.md 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== r15 wave tree ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only b410186 .ufo/waves/round-15/ .ufo/waves/round-16/ census/round-15/ 2>&1 | head -60; echo '=== log -S literal across named paths ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --all --oneline -S'b518735' -- tools tests .ufo/waves census 2>&1 | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== pin mentions across r15 campaign reports (revision-scoped) ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n 'b518735' b410186 -- .ufo/waves/round-15 census/round-15 2>&1 | head -40; echo '=== who owns the frozen fixture path in assignments ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n 'r15-preservation-frozen' b410186 -- .ufo/waves/round-15 2>&1 | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== ConfigRepair.md ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1/ConfigRepair.md 2>&1 | head -120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== AdmissionChecker.md ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1/AdmissionChecker.md 2>&1 | head -110
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== r16 HEAD tree for frozen dir + checker ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cbf688ab -- tests/fixtures/r15-preservation-frozen tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-evidence.py 2>&1; echo '=== expected.json at HEAD ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab:tests/fixtures/r15-preservation-frozen/expected.json; echo '=== record.json at HEAD: identity fields ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab:tests/fixtures/r15-preservation-frozen/record.json | grep -nE 'measured_commit|sha256|commit' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== census/round-15 tree ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only b410186 census/round-15/ 2>&1; echo '=== claims.json ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:census/round-15/claims.json 2>&1 | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== census.sh digests quoted in r15 reports ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -nE '(souji-census\.sh|changed)[^0-9a-f]{0,40}[0-9a-f]{64}' b410186 -- .ufo/waves/round-15/w1 2>&1 | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== references to verification.json / all-pass / record ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -nE 'verification\.json|20/20|all-pass|all pass|record\.json' b410186 -- .ufo/waves/round-15/w1 census/round-15 2>&1 | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== RoundRunner.md ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1/RoundRunner.md 2>&1 | head -90; echo; echo '=== ConfigFixture.md head ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1/ConfigFixture.md 2>&1 | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for rev in $(git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --all --format=%H -- tools/souji-census.sh); do printf '%s  %s\n' "$(git -C /home/vgpnk/Projects/shokunin/souji-shokunin show $rev:tools/souji-census.sh | sha256sum | cut -d' ' -f1)" "$rev"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== closure R4 wording ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n -B3 -A6 'frozen\|b518735\|no committed' b410186 -- corpus/lessons/round-15-verifier-spotcheck.md 2>&1 | head -80; echo '=== r16 campaign files ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cbf688ab -- .ufo/waves/round-16 2>&1 | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== TOOL emission in r15 fixture ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n 'TOOL' cbf688ab -- tests/fixtures/r15-census-config.py | head -30; echo '=== argv / abspath handling ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n 'abspath\|resolve()\|realpath\|args.tool' cbf688ab -- tests/fixtures/r15-census-config.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== closure file exists? ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cbf688ab -- corpus/lessons/ 2>&1 | grep -E 'round-1[45]' ; echo '=== round-16 dir ==='; ls -1 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/ 2>&1; ls -1 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ 2>&1 | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== r15 fixture at b410186 (pinned 6314d45d) ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r15-census-config.py | grep -n 'TOOL.resolve\|print(f"TOOL\|Path(args.tool)\|args.tool' | head -20; echo '=== r14 fixture at b410186 (pinned e6a984b1) ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r14-census-boundary.py | grep -n 'TOOL.resolve\|print(f"TOOL\|Path(args.tool)\|args.tool\|abspath' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== closure round-15 verifier spotcheck: frozen-pin lines ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab:corpus/lessons/round-15-verifier-spotcheck.md 2>&1 | grep -n -i 'frozen\|pin\|b518\|committed' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== record.json key line numbers ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r15-preservation-frozen/record.json | cat -n | grep -nE '"(measured_commit|commit|sha256|path|status)"' | head -30; echo '=== AdmissionChecker no-runtime + pre-integration lines ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1/AdmissionChecker.md | cat -n | grep -nE 'No installs|runtime tests|pre-integration|Files written' ; echo '=== ConfigRepair parse lines ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1/ConfigRepair.md | cat -n | sed -n '1,16p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== README numbered ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r15-preservation-frozen/README.md | cat -n; echo '=== expected.json numbered ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tests/fixtures/r15-preservation-frozen/expected.json | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== r15 w1-spec: frozen/pin sections ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1-spec.json | grep -n -i 'frozen\|pin\|pre-integration\|placeholder' | head -30; echo '=== r15 assignments: AdmissionChecker entry ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1-assignments.json | grep -n -i -A4 -B2 'preservation-frozen\|AdmissionChecker' | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== r16 dispatch R4 ===' && grep -n -i -A6 -B3 'R4\|frozen' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1-dispatch.json 2>&1 | head -60; echo '=== r16 spec R4 ==='; grep -n -i -A8 -B3 'R4\|frozen pin\|re-pin' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1-spec.json 2>&1 | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== literal b518735 in checker source? ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n 'b518735\|4749ad07\|6314d45d' b410186 -- tools/souji-preservation-evidence.py tests/fixtures/r15-preservation-evidence.py 2>&1 | head -20; echo '=== pin/const tables in checker ==='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -nE '^(CHANGED|BASELINE|PREHARM|NAMESPACE|PIN|[A-Z_]+SHA)[A-Z_]* *=' b410186 -- tools/souji-preservation-evidence.py 2>&1 | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== AdmissionChecker spec item ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1-spec.json | grep -n -A6 '"name": "AdmissionChecker"' | cut -c1-3000
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== all committed carriers of b518735 (named scopes) ===' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -l 'b518735' b410186 -- tests tools .ufo/waves census/round-13 census/round-14 census/round-15 corpus 2>&1
```

Non-shell reads: `read` of `.ufo/waves/round-15/w1-spec.json` lines 28 (display and raw) to recover the AdmissionChecker prompt; all other evidence came from the commands above. No test, fixture, census, checker or fixture run was executed; no tools installed; no operator-sweep path opened, listed or grepped.
