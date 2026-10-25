# CritC3Value — attack on C3 (receipt verify/run symmetry)

## Status
STATUS: PARTIAL — the draft keeps regress=5/5, and the durability refusal is a real, symmetric gain. But the `tool=`-in-argv rule exists only in `verify`, so it opens a new asymmetry: `run` exits 0 on four receipt shapes that `verify` then refuses. The fixture's single clean case c cannot detect this. The rule is also weak against a tool that is named in argv but never executed.

Candidate attacked: the uncommitted working-tree `tools/souji-receipt-run.py` (sha256 prefix 17a6d985b9e2), which is the draft `.ufo/waves/round-24/w1/souji-receipt-run.py` (cbe96d734e54) plus a wider `COUNTS_RE`. Base: `git show f9db218:tools/souji-receipt-run.py` (e13d0c8352c9). Both were snapshotted into /var/tmp before scoring, because the working tree changed mid-probe. Tools: git 2.56.0, Python 3.14.8, jj 0.45.1. Nothing installed.

## Evidence
- Regression set, at lane HEAD f9db2181647d91470a724a12d626bd6106805076, run with `python3 -B <tool> verify --root . census/round-23/records/<5>.tsv` under both base and draft: all 5 return `verify=ok`, rc=0.
  - Every rev lies on `refs/heads/master refs/remotes/origin/HEAD refs/remotes/origin/master` (`for-each-ref --contains`), and `merge-base --is-ancestor <rev> master` says yes for each.
  - Every `tool=` is an exact argv element of its `cmd=` (`python3 tools/…` or `python3 -B tools/…`).
- `git grep -l '^receipt=v1' HEAD` (tracked files only; operator-sweep is untracked and was not read) finds 9 files. Beyond the 5 above:
  - `.ufo/waves/round-23/records/stale-digest-demo.tsv` is refused `RECEIPT-TOOL-DIGEST-MISMATCH` by both base and draft. That is its intended demo outcome, unchanged.
  - Three `.ufo/waves/round-23/w2/*.md` files quote a receipt inline; they are not receipt files.
- `git rev-list --all --not --branches --tags --remotes | wc -l` → `315`. Commits reachable only via `refs/jj/*` are routine in this lane.
- Synthetic probes in `/var/tmp/souji-r24-CritC3Value/` (`probe.sh`, `probe2.sh`; receipts written by the draft `run`, rc 0 each). Verdicts:

| case | recorded cmd / situation | base verify | draft verify |
|---|---|---|---|
| clean | `python3 -B tools/x.py` | ok | ok |
| dot | `python3 ./tools/x.py` (same rev bytes executed) | ok | TOOL-NOT-IN-ARGV |
| abs | `python3 <src-worktree>/tools/x.py`; stdout `keys=7` from worktree bytes, digest from rev bytes (`keys=1`) | **ok** | TOOL-NOT-IN-ARGV |
| file | `python3 tools/y.py --file tools/x.py`; stdout `keys=9` from y | ok | **ok** |
| redact | `python3 tools/x.py 'password=a$b'` → recorded `'password=[REDACTED]` (closing quote eaten, shlex "No closing quotation") | ok | TOOL-NOT-IN-ARGV |
| skname | tool `tools/disk-census.py` → recorded `tools/di[REDACTED]` (`sk-` pattern) | ok | TOOL-NOT-IN-ARGV |
| bashc | `bash -c 'python3 tools/x.py'` | ok | TOOL-NOT-IN-ARGV |
| treerev | hand-made receipt with `rev=<tree oid>` | **ok** | REV-NOT-DURABLE (`for-each-ref` rc=129 "is a tree, not a commit") |
| git amend of the unpushed receipt commit | old commit present, reflog only | ok | REV-NOT-DURABLE; `run` at old rev → REV-NOT-DURABLE |
| `jj describe` of the bookmarked commit (colocated) | old commit only under `refs/jj/keep/*` | ok | REV-NOT-DURABLE |
| re-tag old commit after amend | `git tag keep <rev>` | ok | ok |
| after `reflog expire` + `gc --prune=now` | object gone | TOOL-ABSENT | TOOL-ABSENT |
| verifier: `clone --no-local` / `--depth 1` / `--depth 1 --no-single-branch` | rev present with a ref | ok | ok |
| verifier: `--single-branch` clone lacking a side-branch rev | object absent | TOOL-ABSENT | TOOL-ABSENT |
| same clone after `git fetch origin <sha>` | object present, no ref | ok | REV-NOT-DURABLE |

- Program-position predicate check (a stricter rule than exact argv match; scratch python): all 5 regression receipts pass it, plus `clean`, `dot`, `siderev` and `treerev`. It refuses `file`, `abs`, `bashc`, `redact` and `skname`.

## Findings
1. **KEPT: durability refusal.** Draft `verify` now refuses exactly what `run` refuses (tools/souji-receipt-run.py:288). The draft docstring calls it "the same durable-ref predicate `run` refuses on". Amend and `jj describe` make the receipt commit non-durable, and then both `run` and `verify` refuse it. That is genuine symmetry, not a new false refusal. The window is recoverable: a tag restores `ok`. After gc both versions already returned TOOL-ABSENT. Shallow and full clones are unaffected.
2. **KEPT, bonus: tree-id rev.** Base `verify` accepted `rev=<tree oid>`, because `cat-file blob <tree>:<path>` resolves while `run` demands a commit. The draft refuses it, but only incidentally: `for-each-ref --contains` errors out. The refusal code says NOT-DURABLE rather than "not a commit".
3. **KEPT: absolute-path binding gain.** In the `abs` case the receipt's digest came from the rev's bytes but its output came from different (worktree) bytes. Base verified it; the draft refuses. This is the real value of the `tool=` check.
4. **HARMED (operability, symmetry): `run` and `verify` disagree on the argv check.** `run` (no argv predicate; `cmd=` built at :230) wrote `dot`, `abs`, `bashc`, `redact` and `skname` with exit 0. Draft `verify` (:291–294) refuses every one of them. Prereg case c says "a receipt produced by `run` in a synthetic repo -> verify exit 0." It covers one shape, so this inverted asymmetry is invisible to the counter.
   - `dot` is a pure false refusal: the same bytes ran.
5. **HARMED (latent false refusal): redaction runs after `shlex.join`.**
   - `password=`, `--token=` and URL redactions can swallow the closing quote. `shlex.split` then fails, and the draft maps that to `argv = []`, so it reports TOOL-NOT-IN-ARGV instead of MALFORMED.
   - The `sk-` pattern rewrites tool paths containing `sk-` (e.g. `disk-`). The `tool=` header is never redacted, so it can never match.
   - No current lane tool name matches a redaction pattern (`git ls-tree … tools`), so this is latent, not present.
6. **WEAK: the exact match accepts a named-but-unexecuted tool.** `python3 tools/y.py --file tools/x.py` verifies ok, with y's output bound to x's digest. Structurally, `cmd=` is self-reported text, so `verify` cannot prove what ran. The binding can only be enforced in `run`, on the real argv, before execution.
7. **Tradeoff, not defect: durability depends on the verifier's environment.** A verifier that fetched a durable-at-origin rev by sha (no ref) gets REV-NOT-DURABLE. Any local `git branch`/`tag` makes any present commit "durable", so the predicate means "survives gc here", not "published". With 315 jj-only commits in the lane, a pre-push `jj squash`/`describe` of a commit that an r24 receipt names will flip that receipt to refused [INFERENCE: no r24 receipt exists yet to test]. Rule: tag or push the receipt rev before any rewrite, or re-run.
8. Outside C3 counters, as an observation only: the working tree also widens `COUNTS_RE` (adding `cases=\d+ pass=\d+` and others). That widens what `verify` accepts. None of the five regression receipts depend on it.

## Attack log
- Counterexample A (asymmetry): `run --tool tools/x.py -- python3 ./tools/x.py` → rc 0, receipt written; draft `verify` → `RECEIPT-TOOL-NOT-IN-ARGV`. Impacted axis: operability (a C3 regression in the claim's own symmetry terms). Smallest safe correction:
  1. In `cmd_run`, before the clone, refuse `TOOL-NOT-IN-ARGV` with the same predicate on the raw `args.command`.
  2. Compare relative elements via `os.path.normpath`; never accept an absolute element.
  3. In `verify`, use the same helper.
  4. This keeps case b refused and regress 5/5. The program-position check above keeps 5/5 as well.
- Counterexample B (redaction): `'password=a$b'` / `tools/disk-census.py`. Correction:
  1. Build `cmd=` as `shlex.join([redact(a) for a in argv])`, so quoting stays balanced.
  2. In `run`, refuse when `redact(tool) != tool`.
  3. In `verify`, map a `shlex` ValueError to `RECEIPT-MALFORMED`, not NOT-IN-ARGV.
- Counterexample C (weakness): `--file tools/x.py`. Optional hardening: `tool` must be `argv[0]`, or the first non-dash element after a `python3`/`python`/`bash`/`sh` interpreter. This is measured to keep all 5 regression receipts. Note that interpreter flags taking a value (e.g. `-X dev`) would need an allowlist.
- Counterexample D (rewrite, shallow, missing ref): the false refusal is real only for "object present, no durable ref". It is shared with `run`, and fixed by a tag. **Keep.** Optionally add "commit is not a commit/tree?" and "tag or re-run" hints to the detail text.

**Kept:** durability in verify (1); tree-id closure (2); absolute-path binding refusal (3); regress 5/5; refusals 2/2 reachable.
**Harmed:** run/verify argv asymmetry, including the `./` false refusal (4); latent redaction false refusals (5); weak exact-match binding (6, not harmed vs base, but not a gain either).

Scratch `/var/tmp/souji-r24-CritC3Value/` removed after the run.
