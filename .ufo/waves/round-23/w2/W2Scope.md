# W2Scope — security review of the landed round-23 tip

Seat: L1Souji23.W2Scope (sentinel, wave 2, falsify). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Tip reviewed: `102690017115cb202f292828c90b72705f69bf09` (branch `master`; round commits `4765250`, `c0eeaa7`, `1026900`).
Base: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`. Certification OFF, K5 HELD; no credentials, no live `/proc`,
no operator-sweep contents read (names/counts only).

Reviewer footprint (disclosed): one `git status --porcelain` in the lane at the start of this seat, before the
index-write mechanism below was identified — it has the same effect as finding F2-1 and was not repeated.
Everything else read-only (`git show`/`ls-tree`/`grep`/`cmp`/`stat`, `python3 … verify`, refusal-only runner
calls). Scratch `/var/tmp/souji-r23-w2-W2Scope*` removed at the end.

Verdict summary:

| # | Question | Verdict |
|---|---|---|
| 1 | secret-shaped string in a committed receipt under `census/round-23/records/` | **survives** (0 hits; gaps disclosed) |
| 2 | round's command set writes outside the lane | **survives** on destination; **2 findings** on content and on an in-lane write |
| 3 | new file carries an absolute path that leaks operator state | **survives** (no new class; counts given) |
| 4 | K4 exemption file grants more than the one operator-owned path | **survives** (cannot widen; subtree breadth disclosed) |

---

## 1. Secrets in the committed receipts — survives

Counting command, using the runner's own frozen pattern set (`tools/souji-receipt-run.py:64-72`, eight
patterns) applied to every file in the records directory:

```
python3 - <<'EOF'   # REDACTIONS extracted from tools/souji-receipt-run.py, then re.finditer per line
... (script kept at /var/tmp/souji-r23-w2-W2Scope-secret.py during the seat; removed)
EOF
```

Output:

```
pattern_count= 8
files_scanned= 11 hits= 0
```

Files covered: `agreement-after.tsv`, `agreement-control-base.txt`, `agreement-control-base-worktree.txt`,
`declared-evidence-after.tsv`, `empty-slice`, `empty-verdicts`, `gate-check-at-first-landing.tsv`,
`gate-check-at-lane-base.tsv`, `gate-check-c3.tsv`, `refusal-stale-digest.txt`, `uncommitted-exemptions.tsv`.

Pattern liveness (the eight patterns do fire, they are not dead code):

```
'Authorization: Bearer abc123' -> 'Authorization: Bearer [REDACTED]'
'ghp_deadbeefdeadbeef'        -> '[REDACTED]'
'sk-proj-XYZ123'              -> '[REDACTED]'
'AKIAABCDEFGHIJKLMNOP'        -> '[REDACTED]'
'xoxb-123-456'                -> '[REDACTED]'
'https://user:pw@host/x'      -> 'https://[REDACTED]@host/x'
'--token=abc'                 -> '--token=[REDACTED]'
'password=hunter2'            -> 'password=[REDACTED]'
```

Gap sweep over the same 11 files (`eyJ…` JWT, `gho_`, `github_pat_`, `xapp-`, `passwd=`, `--password`,
`Authorization: Basic`, `AWS_SECRET`, `BEGIN … PRIVATE KEY`, `netrc`, `id_rsa`, `.ssh/`): **no hits**.

Disclosures (no action required for this round; the round must not claim more than this):

- **D1-1 (low).** `redact()` is a filter, not a cap. `tools/souji-receipt-run.py:193-209` captures the child's
  full stdout/stderr and writes it; there is no size cap or truncation marker (grep for
  `truncat|65536|64 * 1024` in that file: only line 258 matches, a digest compare). A command that prints its
  environment would put it into a receipt; only the eight shapes above would be masked. Wave-1
  `.ufo/waves/round-23/w1/SentinelScope.md:70` recommended a 64 KiB cap with an explicit marker; it is not
  implemented. Round action: **disclose** in `corpus/lessons/round-23.md` (or implement the cap next round).
- **D1-2 (low).** Five common secret shapes are not covered and were confirmed unmasked:
  `Authorization: Basic …`, `passwd=`, `github_pat_…`, a JWT (`eyJ…`), `AWS_SECRET_ACCESS_KEY=`. None occurs
  in the committed records, so nothing leaks today; the guarantee is narrower than "secret-free".
- **D1-3 (informational).** Four of the eleven files are not runner output and never passed `redact()`:
  `agreement-control-base.txt` (`receipt=plain-v1`), `agreement-control-base-worktree.txt` (no header),
  `refusal-stale-digest.txt` (hand-written 4-line summary), and the two comment-only files. They are clean
  (scanned above).

---

## 2. Does the round's command set write outside the lane? — survives on destination, 2 findings

Recorded command set (from `census/round-23/records/*.tsv` `cmd=` lines): `python3 tools/souji-record-agreement.py`,
`python3 tools/souji-gate-check.py`, `python3 tools/souji-declared-evidence.py`; plus the C3 census call
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
(`.ufo/waves/round-23/w1/ScoutRegistryCensus.md:28`). None of these commands passes an `--out`/`--json` path.

**Destination guards fire.** Live, refusal-only (no file created anywhere):

```
$ python3 tools/souji-receipt-run.py run --root . --rev 4765250… --tool tools/souji-gate-check.py --out /tmp/x.tsv -- true
OUT-UNDER-TMP	receipts go outside /tmp (Q4)                       exit=2
$ … --out /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-23/records/probe.tsv -- true
OUT-IN-REPO	the receipt must not be written inside the measured repo   exit=2
$ … --out /home/vgpnk/Projects/shokunin/kasegi-shokunin/probe.tsv -- true
OUT-SIBLING-LANE	a receipt is never written into another lane        exit=2
$ … --out /home/vgpnk/Projects/shokunin/.ufo/state/probe.tsv -- true
OUT-PROTECTED	/.ufo/state/ is operator or orchestrator runtime           exit=2
$ ls /tmp/x.tsv census/round-23/records/probe.tsv /home/vgpnk/Projects/shokunin/kasegi-shokunin/probe.tsv
ls: cannot access … (all three: No such file or directory)
```

**The only outside-lane destination actually used is `/var/tmp`**, which the prereg's C2 amendment authorises.
Proof of the landing path: the runner refuses `--out` inside the repo (`:157`), yet the committed receipts are
byte-identical to staged files in `/var/tmp/souji-r23-receipts/`:

```
IDENTICAL agreement-after.tsv | declared-evidence-after.tsv | gate-check-at-lane-base.tsv | gate-check-c3.tsv
DIFFERS   agreement-control-base.txt      (different arm, see below)
NO-COMMITTED-COUNTERPART gate-check-before.tsv (renamed at landing) | stale-digest-demo.tsv (see below)
```

Scratch cleanup holds: `tools/souji-receipt-run.py:166` `mkdtemp(dir="/var/tmp")`, `:196` `shutil.rmtree` in
`finally`; `ls -d /var/tmp/souji-receipt-*` → none. `tools/souji-gate-check.py:231` and
`tools/souji-declared-evidence.py:265` create `/var/tmp` scratch only in `selftest()` (gated at
`gate-check.py:302-305`, `declared-evidence.py:324-327`), and the recorded commands do not pass `--selftest`.
`sources-census.sh` writes only to stdout unless `--out` is given (`:94-95`); the recorded call passes none.

### F2-1 (medium) — the C1 instrument writes the lane's git index

`tools/souji-record-agreement.py:279-305` (`k4`) runs `git status --porcelain` at `:295` through the helper at
`:91-99`, whose environment strips only `GIT_DIR`/`GIT_WORK_TREE` and sets `core.fsmonitor=false`. It does **not**
set `GIT_OPTIONAL_LOCKS=0` — which the round's own runner does set for its child (`tools/souji-receipt-run.py:184`).
`git status` refreshes and rewrites `.git/index`.

Mechanism, in scratch: a plain `git status --porcelain` advanced `index-before=05:41:32.166` →
`index-after-plain-status=05:41:33.271`; with `GIT_OPTIONAL_LOCKS=0` the mtime did not move.

Instrument, on a `/var/tmp` clone of the lane at the tip with one untracked file added:

```
$ stat -c 'index-before=%y' "$S/clone/.git/index"
index-before=2026-10-25 05:45:41.654330236 -0300
$ python3 souji-record-agreement.py --root "$S/clone" --rev 102690017115cb202f292828c90b72705f69bf09
keys=4 records=4 occurrences=17 mismatches=8
$ stat -c 'index-after=%y' "$S/clone/.git/index"
index-after=2026-10-25 05:49:05.415238202 -0300
```

Impact: every C1 after-run (and every future receipt that re-runs this counter) takes a lock and rewrites the
lane's git index — contradicting the round's own "reads git objects only" wording (preregistration C1), the
hard bound "the lane's jj state / git index never touched", and the one-convention rule the round applied
correctly in `souji-receipt-run.py`. It is in-lane, not outside-lane; no content loss, but it makes a
"read-only" receipt false in its own repository, and a concurrent lane writer can see an index rewrite.
Smallest remediation: add `env["GIT_OPTIONAL_LOCKS"] = "0"` in `tools/souji-record-agreement.py:92-98` (one line),
then re-run and re-land the C1 receipts; or, if the round will not touch the tool again, disclose the write in
`corpus/lessons/round-23.md` and in the C1 receipt's limits.

### F2-2 (medium) — the clone stages tracked operator-sweep blobs outside the lane

`tools/souji-receipt-run.py:171-177` clones the whole revision (`git clone --no-local --no-checkout` then
`checkout --detach`), with no `--filter`/sparse. Replicating those exact lines in scratch:

```
$ git clone --quiet --no-local --no-checkout <lane> "$S/clone" && git -C "$S/clone" checkout --quiet --detach 1026900
$ find "$S/clone" -path '*operator-sweep*' -type f | wc -l
15
$ find "$S/clone/census" -maxdepth 1 -name 'operator-sweep-*' -printf '%f\n'
operator-sweep-20261018          (one directory; 15 tracked files, names not printed)
```

So each of the five receipt runs materialised 15 tracked `census/operator-sweep-20261018/*` blobs under
`/var/tmp` and deleted them in `finally`. The frozen bound says "no operator-sweep contents read or staged"
(`.ufo/waves/round-23/preregistration.txt:123`); the C2 amendment authorises materialising the revision but
never reconciles that with the bound. The **untracked operator-owned `census/operator-sweep-20261019/` is not
in the clone** (0 files matched) — the bound's actual target is untouched.

Wave 1 already found this as E7 and recommended a bounded clone
(`.ufo/waves/round-23/w1/CritC2Value.md:86-96,120-122,185`); the landed tool carries no `--filter`/sparse, so the
recommendation was not applied. Round action: **disclose** (bound text vs mechanism) or narrow the clone
(`--filter=blob:none --sparse` + a sparse-checkout excluding `census/operator-sweep-*`). Severity is limited
because those 15 blobs are already committed lane history; they are not the operator's untracked output.

### F2-3 (low) — receipt provenance is a copy step nothing records

`cmd_run` never records its own `--out`, and `verify` (`:239-260`) checks only the header shape, the tool digest
and the presence of a counts line — not that the committed bytes are what the runner wrote. The landed receipts
were therefore copied by hand from `/var/tmp` into `census/round-23/records/`. Consequences observed:

- `census/round-23/records/agreement-control-base.txt` is **not** the staged bytes: staged is the K4-on arm
  (20 mismatches, `/var/tmp/souji-r23-receipts/agreement-control-base.txt`), committed is a separate
  `--no-worktree` run (6 mismatches) with a hand-added `receipt=plain-v1` header. Both arms exist and agree with
  the tool's behaviour (the K4-on arm is committed as `agreement-control-base-worktree.txt`), so this is a
  provenance wart, not a contradiction.
- `census/round-23/records/refusal-stale-digest.txt` is a 4-line transcription, not the machine receipt; the
  staged receipt `/var/tmp/souji-r23-receipts/stale-digest-demo.tsv` reproduces it exactly:
  `python3 tools/souji-receipt-run.py verify --root . <that file>` →
  `RECEIPT-TOOL-DIGEST-MISMATCH	receipt 5b8025a83f16 != tree d5ed0805b10f at 1208bfb…`, `exit=2` — identical to
  the committed text. Honest transcription; the machine bytes were left in `/var/tmp`.
- The prereg already concedes the general limit ("the digest binds the bytes the command ran against, not the
  fact that the command ran"). Round action: **accept** the copy step, but say in the receipt format's limits
  that a landed receipt is not authenticated against the runner's write.

---

## 3. Absolute paths in new files — survives

Added-file set: `git diff --name-only --diff-filter=A 1208bfb..1026900` (75 files). Absolute-path hits, deduped:

```
147 /home/vgpnk/Projects/shokunin/souji-shokunin        (lane root)
 40 /home/vgpnk/Projects/shokunin                       (fleet root)
 19 /home/vgpnk/Projects/shokunin/scripts/sources-census.sh
  5 /home/vgpnk/Projects/shokuknow/merge/souji/         (staged inbound package)
  4 /home/vgpnk/Projects/shokuknow
  2 /home/vgpnk/.omp/agent/RULES.md                     (.ufo/waves/round-23/make-spec.py:59)
  2 /home/vgpnk/Projects/shokunin/.scratch/
  1 …/research/, …/LEARNING.md, …/AXES.md, …/{kotoba,kotodama,revenger}-shokunin, …/kama-shokunin/…
```

Every class is pre-existing in the committed tree at the base revision, so no new class of operator state is
published:

```
base /home/vgpnk/.omp files: 108    tip: 110
base shokuknow       files:  69     tip:  84
base files containing /home/vgpnk: 2130   tip: 2168
```

Negative checks over the 75 added files: no `/proc`, no `/home/vgpnk/.ssh`, no `id_rsa`/`netrc`, no dotfile
*contents*, no hostname, no `/etc/passwd`, no file name from inside `census/operator-sweep-20261019/` (only the
directory path, in the exemption row and in prose). `@shokunin.local` occurrences are the lane identity
(`souji@shokunin.local`) and the fixtures' `fixture@shokunin.local`, not operator data.

Verdict: the round adds absolute paths (fleet root, fleet script, staged package, agent-config path) but no
category the lane had not already committed 2130 times. Round action: **accept**; if the lane wants hygiene,
emit lane-relative paths from `.ufo/waves/round-23/make-spec.py` next round — not required now.

---

## 4. K4 exemption breadth — survives

`census/round-23/records/uncommitted-exemptions.tsv` has exactly one row (`cat -A` confirms one TAB and no
continuation):

```
census/operator-sweep-20261019/^Ioperator-owned untracked output (L0 souji | round-17); names only, contents never read, never staged, never deleted by this lane$
```

The code freezes the allowed set independently of the file — `tools/souji-record-agreement.py:60`
`K4_ALLOWED = frozenset({"census/operator-sweep-20261019/"})` — and refuses any other row at `:290-291` before
appending it to the exempt list (`:292`). So the data file **cannot** grant a second path.

Tested by widening the file in a `/var/tmp` clone (a real commit there, lane untouched):

```
$ (append row) corpus/README.md<TAB>lane work I want to hide
$ git commit -m widen-probe → newrev=809abf62b55ff4059ebb0951ce9e359050264cdf
$ python3 souji-record-agreement.py --root "$S/clone" --rev 809abf6…
MISMATCH	K4	corpus/README.md	exemption-not-allowed	not a frozen operator-owned path
keys=4 records=4 occurrences=17 mismatches=1
```

The refused row is not applied. The live evidence that the single allowed row works: `agreement-after.tsv`
at `4765250` reports only a K1 row, i.e. K4 was clean while `census/operator-sweep-20261019/` was untracked.

Disclosure (not a widening beyond the one operator-owned path, but state it): the match at `:303` is a **prefix**
match (`path.startswith(e)` for a row ending `/`), so the grant is the whole directory subtree, not one file, and
it also masks `M`/`D` states there. Demonstrated by dropping a new file inside the exempt directory in the clone:

```
$ echo probe > census/operator-sweep-20261019/injected-probe.txt
$ python3 souji-record-agreement.py --root "$S/clone" --rev 1026900…
keys=4 records=4 occurrences=17 mismatches=0        # the injected file is exempt
```

`git status` collapses untracked directories (`?? census/operator-sweep-20261019/`), so K4 cannot see inside it
either; `.ufo/waves/round-23/w1/ScoutInherited.md:124` counts 29 entries there today, and any future entry is
exempt too. Round action: **accept** — the operator-owned unit is the directory, and the frozen allowlist keeps
the exemption from growing — but record in the K4 note that the grant is subtree-wide and permanent.

---

## Adjacent observations, routed — not judged here

- `census/round-23/records/agreement-after.tsv` is a `receipt=v1` with `rc=1` and one `K1 value-disagree` row at
  `rev=4765250…`. C1's target is the round tip, and this receipt is not at the tip; the C1 seat owns whether the
  claim is met. Not scored here.
- `tools/souji-record-agreement.py:319-323` accepts any 40-hex `--rev` without checking existence; an
  unresolvable rev yields all-absent mismatches (fails closed toward `mismatches>0`), so it cannot manufacture
  agreement. Robustness note only.
- At the tip in a clean clone the counter reports `keys=4 records=4 occurrences=17 mismatches=0` (sub-tip
  observation from the item-4 test; the C1 seat must produce its own receipt at the tip).

## Bounds honoured

No git/jj mutation, no `rm`/`mv` in the lane, no signals, no installs, no credentials, no live `/proc`, no
operator-sweep contents read (names/counts only), no writes outside this report and `/var/tmp/souji-r23-w2-W2Scope*`
(removed). Scratch clones were made from the lane and committed only inside `/var/tmp`.
