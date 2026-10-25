## Status

STATUS: PARTIAL — no step in the round-26 work plan writes outside the hard bound, but the bound text names a non-existent path, the frozen receipt instrumentation is not runnable as written and does not verify, the C3 fixture case set was cut 12->11 without an amendment, and the C2 gate's scratch path is already occupied.

Bound verdict per step (plan = `.ufo/waves/round-26/w1-spec.json`, 87 items, md5 `9419c33030b0179a128d09b7ad4bed6d`, read this run; lane HEAD `ba8b54b85814dd980aa96050fe111c7cbfd4956a`, 2026-10-25T17:33:43Z):

- (a) shukuknow writes: **NO.** All 18 occurrences of the source path across the 87 prompts are reads (`ScoutStagedEntries`, `ScoutRegroundOwnwork`, `ExecRenumberMap`, `MutC2Rows`, `SonicRowSchema`, `SonicReadmeRows`, `ScoutAssimRegister`). Two state the rule verbatim: "Read-only; never write into /home/vgpnk/Projects/shokuknow." No `git -C`, `cd`, `mkdir`, `cp` or redirect against that tree exists in any prompt. C2's kill rule also names it: "appended; any byte written into /home/vgpnk/Projects/shokuknow." (preregistration.txt:136). Compliant — subject to A1.
- (b) mirror gate: **PARTIAL.** The gate does use `--file` on a `/var/tmp` copy (`/var/tmp/souji-r26-mirror/corpus/SOURCES.md`), but the prereg's own gate text names a lane-internal `<mirror>` instead, and `--file` is sanctioned by the instrument's header, not by CORPUS.md. Details in findings 4-5; the frozen path currently refuses to build (finding 5).
- (c) counter reads of `census/operator-sweep-*` or `.scratch/`: **NO.** Source inspection of `census/round-26/c1-counter.sh` (SCORECARD.md only), `c2-counter.sh` (`corpus/knowledge/*.md`, `corpus/SOURCES.md` only), `c3-counter.sh`, and of the three tools the K-commands invoke (`souji-axis-check.py`, `souji-gate-check.py`, `souji-coverage-agreement.py`): no reference to `.scratch`, `operator-sweep` or `/proc`. `tools/souji-receipt-run.py:205` refuses `--out` under `/.ufo/state/`, `/.tower/`, `/.scratch/`, `/MANIFEST.json`, and lines 228-230 write `!/census/operator-sweep-*` into the receipt clone's sparse-checkout. K3's read set is `shokunin.conf` plus the selected lane's `SOURCES.md` (`scripts/sources-census.sh:708-720`), not sibling corpora. Compliant — subject to finding 7.
- (d) own-work re-grounding: **PASS (read-only reads are inside the bound).** `ScoutRegroundOwnwork` reads three files under `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/` and records sha256; the follow-on is a fresh synthetic repo in `/var/tmp/souji-r26-ScoutRegroundOwnwork/` running `git worktree prune --dry-run`, which is fixture *logic*, not the campaign fixture. Residual risk in A5.

No scratch was created by this seat; nothing was installed; no fleet, sibling-lane, jj, git-index, `.scratch/`, `.ufo/state/` or `census/operator-sweep-*` content was read or touched. The only execution against fleet code was the read-only K3 command quoted below.

## Evidence

Lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`; HEAD advanced during this sweep (`d6c13b0` -> `07f83e6` -> `ba8b54b`) — the plan artifacts `w1-spec.json`/`w1-dispatch.json` are unchanged since 14:15 (md5 above), so the prompts audited are the frozen ones.

(a) every source-repo mention, extracted from the prompts:
```
$ python3 -B -c '... re.finditer over items[].prompt ...' 
ScoutStagedEntries / ScoutRegroundOwnwork / ExecRenumberMap / MutC2Rows /
SonicRowSchema / SonicReadmeRows / ScoutAssimRegister  -> reads only
$ python3 -B - <<'PY'  # write/exec pattern hunt over the same prompts
pat = (git -C <src> | cd <src> | mkdir ... <src> | cp ... <src> | > ... <src>)
PY
(no output)
```

(b) CORPUS.md is silent on the mechanism:
```
$ grep -cin 'mirror\|var/tmp\|read-only\|validate' CORPUS.md
0
$ grep -n 'use --file' scripts/sources-census.sh
15:#                     use --file or an explicit directory for a specific registry.
$ grep -n 'Read-only: parses' scripts/sources-census.sh
6:# Read-only: parses shokunin.conf LANES rows textually (never sources the conf),
```
The `--file` branch (`sources-census.sh:497-504`) requires no `shokunin.conf`, resolves `used-by` against `dirname(file)/..`, and writes nothing unless `--out` is passed (line 699). No plan step passes `--out`.

(c) K3 executed read-only from the fleet root, at the live lane tree:
```
$ bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
... (W-codes only) ...
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
exit=0
```
`census/operator-sweep-20261018/` IS tracked at HEAD; `census/operator-sweep-20261019/` is untracked and appears in no rev-bound command's input.

Contract-integrity checks:
```
$ python3 -B tools/souji-receipt-run.py run --help
usage: ... run [-h] [--root ROOT] --rev REV --tool TOOL --out OUT ...
$ python3 -B tools/souji-receipt-run.py verify census/round-26/records/c1-before.tsv
RECEIPT-COUNTS-ABSENT	no stdout line starts with a counts line          (exit 2)
$ python3 -B tools/souji-receipt-run.py verify census/round-26/records/c2-before.tsv
RECEIPT-COUNTS-ABSENT	no stdout line starts with a counts line          (exit 2)
$ grep -c 'dict(id=' tests/fixtures/r26-axis-check.py
11
$ grep -n 'TemporaryDirectory' tests/fixtures/r26-axis-check.py
205:    with tempfile.TemporaryDirectory(prefix="souji-r26-axischeck.") as td:
$ echo "TMPDIR=${TMPDIR:-<unset>}"
TMPDIR=<unset>
$ git show 89e0fce:census/round-26/c3-counter.sh | sha256sum
7d40f5d8e32c5c9ab8b5485eaccff408355286c4a1ad1c90dac92b34ef34835d
$ git show d2e6253:census/round-26/c3-counter.sh | sha256sum
b60bcede775e6bf23ee2c4422b9feec3119134522a4534cb524ac8e3fcd7b656
```

## Findings

1. **Bound text protects a path that does not exist** (source: `/home/vgpnk/Projects/shokunin` root; ticket HARD BOUND and `w1-spec.json` item `SentBounds`). `/home/vgpnk/Projects/shukuknow` does not exist (`ls -d`: "No such file or directory"); the real source is `/home/vgpnk/Projects/shokuknow` (`/home/vgpnk/Projects/shokuknow/merge/souji/`, 18 hits in the spec prompts and 2 in the prereg, spelled `shokuknow`). A literal reading of the bound therefore protects nothing, and a seat that wrote `shokuknow` while claiming the `shukuknow` clause would satisfy the letter. C2's kill rule (`preregistration.txt:136`) names the correct path, so the claim is instrumented correctly; the ticket/bound wording is not. Smallest remediation: the bound and every prompt must say `/home/vgpnk/Projects/shokuknow`.

2. **The frozen receipt command is not executable as written** (`preregistration.txt:61`; C2 and C3 name their receipts without any argv at all, `:141-144`). The contract freezes "run --root . --rev 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd --label census/round-26/c1-counter.sh", but the instrument has no `--label`, and `--tool` and `--out` are `required=True` (`tools/souji-receipt-run.py:349-353`, `run --help` above). Every receipt in `census/round-26/records/` was therefore produced by an argv the contract does not name. Smallest remediation: amend the receipt argv to `--tool <counter> --out /var/tmp/...` (stricter/clarifying, logged) or make `--label` an alias.

3. **Red receipts are not bound to the declared base revision.** `c1-before.tsv` records `rev=12fd90bc…` (the freeze commit) where the contract names `0eca7c8a…`; `c2-before.tsv` and `c3-before.tsv` record `rev=89e0fcee…` (the amendment-1 commit). The values are still base-correct: `git diff --stat 0eca7c8 12fd90b -- SCORECARD.md` is empty and `git diff --stat 0eca7c8 89e0fce -- corpus/` is empty. But the receipt binds a different commit than the claim asserts, so the "base literals re-derived at 0eca7c8" assertion is proved indirectly, not by the receipt.

4. **Neither red receipt verifies, and the contract demands `verify=ok`** (`preregistration.txt:65` and `:144`, "each `verify=ok`"). Both `verify` runs exit 2 `RECEIPT-COUNTS-ABSENT`. `souji-receipt-run.py:67-77` accepts only a closed set of count shapes (`grounded=… mapped=…`, `cases=… pass=…`, `entries=… ok=…`, …); `markers=2` / `headings=…` / `grounded_f1=0` / `axis_check_exit=0` match none, so these receipts can never reach `verify=ok` as frozen. (The C2 K4 receipt, whose stdout starts `grounded=7 mapped=7`, would verify.) Smallest remediation: counters emit one accepted shape, or the contract drops the `verify=ok` demand for counter receipts and states the substitute check.

5. **C2 scratch-mirror path mismatch plus a live collision** (`preregistration.txt:124-129` vs `w1-spec.json` item `ExecScratchMirror`). The prereg names `.ufo/waves/round-26/assimilation/validate/` as `<mirror>`; the plan and `mirror-build.py:66` use `/var/tmp/souji-r26-mirror`. Both are inside the bound, but the `/var/tmp` name is not seat-scoped, and it is already occupied: `/var/tmp/souji-r26-mirror/` holds an unmarked copy of `corpus/ tools/ tests/` plus `validate.out` from another seat. `mirror-build.py:263-264` refuses a non-empty dest without its marker, so the frozen gate path currently cannot build. Smallest remediation: run the gate with a seat-scoped `--dest /var/tmp/souji-r26-C2-mirror`, and have the prereg name the path that is actually used.

6. **C3 case set was cut from 12 to 11 after freeze, with no amendment** (`preregistration.txt:180-199` vs `tests/fixtures/r26-axis-check.py:73-171`). The contract requires "last stdout line: `cases=12 pass=12 control=FALSE-GREEN-REJECTED`;" and lists 12 frozen cases including the r25-C2-replica discriminator as case 1. The committed fixture defines 11 cases, and its case 1 is "axis not owned" (R1), not the replica discriminator. Amendments 1 and 2 cover C2 literals and C1 spans only. `census/round-26/records/c3-control.tsv` confirms the shape (`cases=11 pass=4`). K2's frozen literal is unreachable at HEAD, so `cases=11 pass=11` cannot be scored as the frozen counter.

7. **C3 fixture cases run in `/tmp`, contradicting the claim's own kill rule** (`preregistration.txt:191` "Cases run in isolated /var/tmp scratch only.", and the kill rule "any fixture case lacking an isolated /var/tmp world"). `tests/fixtures/r26-axis-check.py:205` calls `tempfile.TemporaryDirectory(prefix="souji-r26-axischeck.")` with no `dir=`, and `TMPDIR` is unset, so every case world resolves to `/tmp` — also outside the seat scratch root. Smallest remediation: pass `dir="/var/tmp"` (or a `souji-r26-<seat>` subdir) at line 205.

8. **The frozen C3 counter was mutated after freeze.** `census/round-26/c3-counter.sh` hashed `7d40f5d8…` at `89e0fce` (the red arm's rev) and `b60bcede…` from `d2e6253` (the green arm's rev); the diff adds a `--stub` branch. `c1-counter.sh` and `c2-counter.sh` are byte-stable (their receipt hashes match the worktree). The change is additive and the no-argument behaviour is identical, but the red and green receipts bind different instrument bytes, and no amendment records the edit.

9. **Lane worktree carries bound material and build debris, uncommitted** (`git status --porcelain` at `ba8b54b`, 51 entries). `?? census/operator-sweep-20261019/` sits inside the lane at the exact path the bound says must never have its contents read; `?? tools/__pycache__/`, `?? tests/fixtures/__pycache__/` show lane Python was run without `-B`. Any `git add -A` or jj snapshot by the integrator would commit both. Smallest remediation: the integrator stages explicit paths only; seats keep running `python3 -B`.

10. **C2's required after-receipts are absent at the audited rev.** `git ls-tree --name-only HEAD census/round-26/records/` lists `c1-before c1-after c2-before c2-after c2-k4-base c3-before c3-after c3-control empty-slice empty-verdicts`. The contract also requires `c2-k4-after.tsv` and `c2-gate.tsv` (`preregistration.txt:139-144`); neither exists, so K2's and K4's after-values have no receipt in the required set. `c3-control.tsv` is committed but is not in the frozen receipt list.

## Attack log

- **A1 (bound-scope typo, Medium).** Cite `/home/vgpnk/Projects/shokuknow` as the protected source while the bound's protected path is the non-existent `shukuknow`. A seat could legitimately claim "no bytes written to shukuknow" after writing the campaign repo. Blocked only by C2's kill rule spelling it correctly (finding 1). Not executed.
- **A2 (unverifiable green, Medium).** `verify` exits 2 on every counter receipt (finding 4), so "green-after, receipts committed, verify=ok" is a property no independent seat can re-check from the committed bytes. The claim's evidence chain reduces to trusting the L1's own run.
- **A3 (silent case-set shrink, High for calibration).** Frozen 12 -> implemented 11 (finding 6) changes the falsification surface after freeze. K2's literal is then unreachable, and a passing "11/11" would be reported against a counter that can no longer produce `cases=12 pass=12`. This is the K5-freeze failure mode the lane's own amendment rules forbid.
- **A4 (kill-rule blindness via /tmp, Medium).** With case worlds in `/tmp` (finding 7), the "isolated /var/tmp world" kill arm is satisfied by text alone; a case that leaked state between cases would leave no `/var/tmp` evidence and would still report 11/11.
- **A5 (fixture-execution ambiguity, Low).** `ScoutRegroundOwnwork` says "re-run ONE case of the fixture logic" — the follow-on body is a synthetic `/var/tmp` repo, but a seat reading it as "run the fixture" would execute a campaign tool inside `/home/vgpnk/Projects/shokuknow`, which the bound forbids by the letter. The fixture itself writes only `/var/tmp/souji-r23-*` (`mktemp -d` at line 47, EXIT trap at line 53), so the write bound would survive; the execute bound would not.
