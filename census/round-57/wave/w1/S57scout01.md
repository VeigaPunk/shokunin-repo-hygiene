# S57scout01 — round 57, w1 (role: scout, read-only recon)

**Seat:** S57scout01 · **Lane:** /home/vgpnk/Projects/shokunin/souji-shokunin
**Freeze:** `d749f7ee081ec1b382b2f92577eb22bfba1c7761` (examined at this exact revision)
**Base:** `b4ef0bc84ada3fb3aefd6a0b1a841a6517b84acd`
**Lane tip at session start:** `d749f7ee` (freeze) → **at final snapshot:** `80548212` (the sources commit; `git merge-base --is-ancestor d749f7ee HEAD` rc=0, `git rev-list --count d749f7ee..HEAD` = 1). The lane is live: sibling seats wrote `records/` evidence, `LOG.md` and `SCORECARD.md` while this seat was reading.
**Snapshot time:** 2026-11-03T23:30Z (20:30 local).
**Bounds honoured:** leaf member — no subagent, no background job; no write outside the seat dir and `/fast/scratch/hyaku/souji-r57/S57scout01` (deleted before yield); no mutation of the lane, the fleet repo or any sibling. The only repository this seat created is its own scratch fixture for the recorder test (`git -C <dir> rev-parse --show-toplevel` asserted equal to the scratch dir before the first commit). Read-only git/jj only over the lane. Tool installs: **none** (python3/git/jj already present).
**Raw receipts:** every command below was re-run this session; the literal command+output transcripts are stored next to this report (`pin-audit.txt`, `determinism-check.txt`, `manifest-content-hash.txt`, `manifest-raw-diff.txt`, `matrix-cmp.txt`, `c1-selftest.txt`, `c2-selftest.txt`, `c1-tip-mine.txt`, `recorder-refusals.txt`, `c2-before-gate.txt`, `c2-before-stub.txt`, `sources-census.out`, `host-git-status.txt`, `host-jj-state.txt`, `routed-map-evidence.txt`, `function-diff.txt`, `fixture-manifest.b1.tsv`).

Verdict vocabulary in this report: MATCH/MISMATCH (pin), byte-identical, REPAIRED / INSTRUMENTED / NAMED-LIMIT / OPEN (routed map). No falsification of the frozen six checks was observed; every OPEN residual is listed in §7.

---

## 1. Pin audit (13 table pins + 3 prose/base pins)

Per-row command (literal, run for every row):
`git -C /home/vgpnk/Projects/shokunin/souji-shokunin show <rev>:<path> | sha256sum`
with `<rev>` = `d749f7ee081ec1b382b2f92577eb22bfba1c7761` for round-57 paths (tagged **F**) and `b4ef0bc84ada3fb3aefd6a0b1a841a6517b84acd` for the pin the prereg marks `at base` (**B**).

| # | pin path | rev | expected sha256 | observed sha256 | verdict |
|---|---|---|---|---|---|
| 1 | census/round-57/c1-counter.py | F | `e18872d6584bdf7252a695a7ba19da875e2d7b53f1c5b46e5b524c70fcdf78d4` | `e18872d6584bdf7252a695a7ba19da875e2d7b53f1c5b46e5b524c70fcdf78d4` | MATCH |
| 2 | census/round-57/c2-counter.py | F | `174d7b8a3c105875f1757f9137f26ed54e38ac11c963a134015bce8a9dd16ec2` | `174d7b8a3c105875f1757f9137f26ed54e38ac11c963a134015bce8a9dd16ec2` | MATCH |
| 3 | census/round-57/fixtures/build-fixtures.py | F | `2b8b657b8d86541d4a6f38345cd8d67f1a520603a7cda08f0a5bc3038924633b` | `2b8b657b8d86541d4a6f38345cd8d67f1a520603a7cda08f0a5bc3038924633b` | MATCH |
| 4 | census/round-57/fixtures/run-matrix.sh | F | `72adf821938713b74a3b2cfab93f72981374b3c4d98ac7c8939a0f4ffe34a4d5` | `72adf821938713b74a3b2cfab93f72981374b3c4d98ac7c8939a0f4ffe34a4d5` | MATCH |
| 5 | census/round-57/record-receipt.sh | F | `84148011abc9574048fc77e02427bee9010850418beeeaaa1babe59185109aa9` | `84148011abc9574048fc77e02427bee9010850418beeeaaa1babe59185109aa9` | MATCH |
| 6 | census/round-57/controls/c2-stub.py | F | `6d7f7534dbfe4d4a7c49b3b603cf11400ea6a8fb852d7a056bcc753ae56555c1` | `6d7f7534dbfe4d4a7c49b3b603cf11400ea6a8fb852d7a056bcc753ae56555c1` | MATCH |
| 7 | census/round-57/records/c1-selftest-expected.tsv | F | `538d902e2f65ddc26bc0c532f4f7de67f89c08020f69151563a982d923d8e105` | `538d902e2f65ddc26bc0c532f4f7de67f89c08020f69151563a982d923d8e105` | MATCH |
| 8 | census/round-57/records/c2-selftest-expected.tsv | F | `a2bc835ffa4e2ce3d822a28a344770b3bd106a770918483854669e4238ae1d24` | `a2bc835ffa4e2ce3d822a28a344770b3bd106a770918483854669e4238ae1d24` | MATCH |
| 9 | census/round-57/manifests/before.tsv | F | `1c63e755948e3025186c61897847832856e7a96110fb5c94a0f7cb738facd991` | `1c63e755948e3025186c61897847832856e7a96110fb5c94a0f7cb738facd991` | MATCH |
| 10 | census/round-51/records/ws-drift-vs-r46.tsv (`at base`) | B | `2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30` | `2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30` | MATCH |
| 11 | S279 capture census/round-57/sources/s279-whatwg-html-syntax.html | F | `ad4bdaca53226b0c6f5962786f309fea3ca4e59bec86b026cb3fc5d641b25ff1` | `ad4bdaca53226b0c6f5962786f309fea3ca4e59bec86b026cb3fc5d641b25ff1` | MATCH |
| 12 | S280 capture census/round-57/sources/s280-commonmark-0.31.2.html | F | `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d` | `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d` | MATCH |
| 13 | S281 capture census/round-57/sources/s281-mdn-comments.html | F | `2bca88c20599aa7f3c1bc12dc4d041f156b526ed7dee68c0b08b9fc1ca60d9ba` | `2bca88c20599aa7f3c1bc12dc4d041f156b526ed7dee68c0b08b9fc1ca60d9ba` | MATCH |

**13/13 MATCH.** Observed byte sizes (from the same `git show`): 36 323 / 13 431 / 43 244 / 1 973 / 1 596 / 503 / 1 682 / 255 / 97 / 4 644 / 89 196 / 514 698 / 175 824.

Prose-pinned base artifacts (the prereg names them outside the table; audited against **B** because the task text says "three base pins" while the table marks only one `at base`):

| artifact | command | expected | observed | verdict |
|---|---|---|---|---|
| census/round-56/c1-counter.py (v5, the before arm) | `git -C LANE show b4ef0bc8…:census/round-56/c1-counter.py \| sha256sum` | `975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179` (named in prereg prose) | `975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179` — and identical at the freeze (`git show d749f7ee…:… \| sha256sum` gives the same digest) | MATCH |
| census/round-56/records/landing-suite-final.txt (read by C2's before manifest) | `git -C LANE show b4ef0bc8…:census/round-56/records/landing-suite-final.txt \| sha256sum` | no digest named (identity/path pin only) | `f764b2253e4b628b5cee1488311b704a3d2002152bd7dbe08b6f1e29d4a49630`; blob identical at HEAD; content = `SUMMARY assertions=609 … instrument_sha256=a33249…` + `EXIT=0`, no `rev=` | MATCH (existence/identity) |

**Confidence:** high — every digest is `sha256` of the blob served by `git show` at the named revision (the literal pipeline was executed, not a worktree read). **Note:** the task brief's "three base pins" resolves to {ws-drift `at base`, v5 counter, r56 receipt}; only the first carries a digest in the pin table.

---

## 2. Fixture determinism (two builds + a third for the matrix driver)

Commands (absolute paths, scratch named explicitly):

```
mkdir -p $S/b1 $S/b2 $S/m/selftest
python3 -B census/round-57/fixtures/build-fixtures.py --work $S/b1         --manifest $S/b1/fixture-manifest.tsv
python3 -B census/round-57/fixtures/build-fixtures.py --work $S/b2         --manifest $S/b2/fixture-manifest.tsv
python3 -B census/round-57/fixtures/build-fixtures.py --work $S/m/selftest --manifest $S/m/selftest/fixture-manifest.tsv
```
with `S=/fast/scratch/hyaku/souji-r57/S57scout01` (the third build is the one `run-matrix.sh` requires at `$S/selftest/fixture-manifest.tsv`).

Observed (all three runs `rc=0`, 52 `BUILT` lines each; first/last lines identical, e.g. `BUILT F1-HONEST-TIP tip=55b56e65f805f850dc6e2d966b3f3131da33697b` … `BUILT FC3-EMPTY-VALUE-KEY tip=9085035ed77658c654dce9a4e70bf683cd6e2103`):

| check | command | observed |
|---|---|---|
| row count | `wc -l b1/fixture-manifest.tsv b2/… m/selftest/…` | 53 / 53 / 53 lines (header + **52 fixtures**: 36 `C1` + 16 `C2`) |
| semantic columns identical across builds | `cut -f1,2,4,5,6 <manifest> \| sha256sum` (name, kind, base, tip, record_sha256) | `cbb4925652796be6a8c31cadb043239a29e5ce318cc4e05534742f12a875d1e8` for **all three** builds |
| byte diff of the two manifests | `diff b1/fixture-manifest.tsv b2/fixture-manifest.tsv` | rc=1, **52 changed line pairs; column 3 (`dir`, the absolute scratch path) only** — by construction not byte-identical |
| base/tip columns vs the committed v5 dry-run | `python3 -B <seat>/determinism-check.py b1/… b2/… census/round-57/records/matrix-dryrun/c1-matrix-v5.tsv` | `rows a=52 b=52`; `rows whose name/kind/base/tip/record_sha256 differ: 0`; `C1 rows compared=36 differing=0`; `PASS` (rc=0) |
| commits really exist | `git -C <fixture> cat-file -e <base\|tip>^{commit}` over 52 rows × 3 builds | 312/312 resolve, 0 missing |

**Differing rows: none.** 0 of 52 rows differ in content columns; 0 of 36 C1 rows differ in the matrix `rev`/`base` columns. The comparison rule encoded in the receipt script is `run-matrix.sh`'s own: matrix `rev = tip[:12]`; matrix `base = base[:12]` for `F5-REWRITE`, `F6-RECORD-DRIFT`, `F27-BINARY-NUMSTAT`, else `tip[:12]`.
**Confidence:** high. Build determinism is proven by equal commit hashes (commit hashes cover tree, parents, author/committer identity and timestamps), not by equal file lists alone.

---

## 3. Arm inventory (both matrix arms re-run, compared byte-for-byte)

Command (exactly as the prereg's Matrix command):

```
bash census/round-57/fixtures/run-matrix.sh $S/m $S/m/out      # rc=0
cmp $S/m/out/c1-matrix-v5.tsv census/round-57/records/matrix-dryrun/c1-matrix-v5.tsv
cmp $S/m/out/c1-matrix-v6.tsv census/round-57/records/matrix-dryrun/c1-matrix-v6.tsv
```

Observed:
- `v5 cmp: byte-identical`; `v6 cmp: byte-identical`.
- sha256 (`sha256sum` of produced and committed files): v5 `4cce7f59d97b453da6e85df090302772f3c1857afe5a939c5f4ec0aa28fb3d30` both sides; v6 `27b8e7a2412d88a6ae731537cabae4ec6a36954f89544d210ecfa4bc7d3fe0ab` both sides.
- Exit-0 counts over the 36 rows: **v5 = 10** (`F1-HONEST-TIP`, `F12b-LOG-FILED`, `F12c-LOG-POINTER-EXEMPT`, `F17-INDENT4-FENCE`, `F18-BTINFO-FENCE`, `F19-PAIR-IN-FENCE`, `F29-PROSE-COMMENT-MENTION`, `B4-INLINE-NBSP-OPENER`, `C4-INLINE-CLOSED-COMMENT`, `C6-INLINE-SAME-LINE`); **v6 = 8** (same minus B4 and C4).
- Rows whose `(exit, findings_all)` changed v5→v6: exactly `B4-INLINE-NBSP-OPENER` and `C4-INLINE-CLOSED-COMMENT`; the other **34/36 carry rows are identical** (`carry_identical 34`).
- B4/C4 under v6: `exit=1`, `findings_all=CORRECTION-IN-FENCE,CORRECTION-IN-FENCE`; the finding details (direct run of the v6 counter over the built fixture, `--record-sha256` from the manifest) read
  `FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:8 (site SCORECARD.md:5) hidden_by=inline` and
  `FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:9 (site census/round-51/preregistration.txt:3) hidden_by=inline`.
- `C6-INLINE-SAME-LINE`, `F29-PROSE-COMMENT-MENTION`, `F17-INDENT4-FENCE`, `F18-BTINFO-FENCE`, `F19-PAIR-IN-FENCE`: `exit=0` under **both** arms, `findings_all=-`.
- B4/C4 under v5: `exit=0`, `findings_all=-` (the over-acceptance the claim names).

**Differing lines: none** relative to the committed dry-run; the observed run reproduces T1–T4 exactly on the frozen bytes.
**Confidence:** high (byte comparison + digest).

---

## 4. C2 surfaces at base (gate vs stub over the same manifest)

Commands and observed output (lane cwd, `TMPDIR` set to this seat's scratch):

```
$ python3 -B census/round-57/c2-counter.py --root . --manifest census/round-57/manifests/before.tsv
FINDING RECEIPT-REV-MISSING census/round-56/records/landing-suite-final.txt
SUMMARY receipts=1 findings=1
[rc=1]

$ python3 -B census/round-57/controls/c2-stub.py --root . --manifest census/round-57/manifests/before.tsv
SUMMARY receipts=0 findings=0
[rc=0]
```

| surface | exit code | SUMMARY line | notes (observed) |
|---|---|---|---|
| gate `census/round-57/c2-counter.py` | **1** | `SUMMARY receipts=1 findings=1` | exactly one finding, `RECEIPT-REV-MISSING census/round-56/records/landing-suite-final.txt` — the target T1 finding id and path |
| stub `census/round-57/controls/c2-stub.py` | **0** | `SUMMARY receipts=0 findings=0` | the do-nothing control is false-green by construction; it also reports `receipts=0` for a 1-row manifest (it does not read the manifest), so only the before/after **pair** discriminates it |

Supporting (same session): `TMPDIR=$S python3 -B census/round-57/c2-counter.py --selftest --work $S/sel2` → `SELFTEST control=FALSE-GREEN-REJECTED stub_meets=1 cases=8`, `SELFTEST pass cases=8`, rc=0; output byte-identical to the lane's untracked `records/c2-selftest.txt`. `grep -cE '^rev=[0-9a-f]{40}$' census/round-56/records/landing-suite-final.txt` → **0** (rc=1), at base and at HEAD.
**Confidence:** high.

---

## 5. Host state

```
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
… 62 × "souji\tW04\tS0xx duplicate url … across scopes" (S035 … S280) …
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
[rc=0]

$ bash /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/souji-shokunin
state branch=master local=805482129d022b13db672654f5478952def607a6 remote=805482129d022b13db672654f5478952def607a6 ahead=0 behind=0 head=detached tracked=2 untracked=10
[rc=0]

$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -uall
 M LOG.md
 M SCORECARD.md
?? census/round-57/records/c1-hidden-class.txt
?? census/round-57/records/c1-matrix-v5.tsv
?? census/round-57/records/c1-matrix-v6.tsv
?? census/round-57/records/c1-selftest.txt
?? census/round-57/records/c1-targets.txt
?? census/round-57/records/c1-tip.txt
?? census/round-57/records/c2-before.txt
?? census/round-57/records/c2-selftest.txt
?? census/round-57/records/sources-census-after.txt
?? census/round-57/records/sources-census-before.txt
[rc=0]
```

- `head=detached` is the normal colocated-jj shape (`cmd_state` reports `attached` only when `git symbolic-ref HEAD` succeeds); `local=remote=ahead=0 behind=0` is a clean fast-forward state at `80548212`. HEAD advanced from the freeze `d749f7ee` to `80548212` **during** this session (the sources commit, parent = freeze); the freeze remains an ancestor (rc=0) and its bytes are unaffected.
- The validator's 62 `W04` lines are duplicate-URL **warnings** (`git-scm`, `man7`, `docs.python`, `raw.githubusercontent`, and now `S280`) printed alongside the `souji ok` line; the command exits **0**. `corpus/SOURCES.md` row count = `grep -c '^| S[0-9]'` → **205**; `S281` is present and `REJECTED`.
- Untracked entries, classified (the ten entries of the 20:30 snapshot plus the two that appeared at 20:31 — all twelve are this round's expected post-freeze evidence; none is scratch debris, and `.ufo/waves/` + `__pycache__/` are gitignored and therefore not shown):

| untracked entry | expected r57 evidence? | basis |
|---|---|---|
| `records/c1-matrix-v5.tsv`, `c1-matrix-v6.tsv` | yes — official C1 matrix outputs | byte-identical to `records/matrix-dryrun/*` (sha256 above); frozen predicate: "official post-freeze matrices must reproduce the dry-run TSVs byte for byte" |
| `records/c1-selftest.txt` | yes — C1 T5 | independently reproduced this session, **byte-identical** (4 625 B, `SELFTEST pass cases=36`) |
| `records/c1-targets.txt` | yes — C1 T1–T4 summary (derived) | content matches my independent computation exactly (`rows 36`, `v5 exit0 10`, `v6 exit0 8`, `changed_rows B4…,C4…`, `carry_identical 34`) |
| `records/c1-tip.txt` | yes — C1 T6 real-lane receipt | the prereg names this path for the measured revision; body reproduced exactly by my `--root … --rev d749f7ee…` run (rc=0, `unfiled=0 fenced=0`) |
| `records/c1-hidden-class.txt` | yes — C1 T1 hidden-class detail (`hidden_by=inline`) | matches my direct v6 runs on B4/C4 |
| `records/c2-before.txt` | yes — C2 T1 before receipt | binds `instrument=census/round-57/c2-counter.py`, `instrument_sha256=174d7b8a…` (frozen pin), `rev=d749f7ee…`, `EXIT=1`; body matches my gate run |
| `records/c2-selftest.txt` | yes — C2 T3 | independently reproduced, **byte-identical** (938 B, `SELFTEST pass cases=8`, `control=FALSE-GREEN-REJECTED`) |
| `records/sources-census-before.txt`, `sources-census-after.txt` | yes — frontier step | the prereg's frontier step requires a census before/after; my own `validate` run exits 0 with `souji ok` |
| ` M LOG.md`, ` M SCORECARD.md` (tracked, modified) | expected round work, not receipts | `git diff --numstat` = `41 0 LOG.md`, `34 0 SCORECARD.md` (uncommitted at snapshot) |

**Post-snapshot delta (the lane is live; entries observed at 20:31–20:32 local, after the 20:30 status snapshot above):** three more untracked entries appeared — `census/round-57/records/probe-rev-shapes.txt` (845 B, an L1 C2 probe: a commit-rev receipt accepted; an annotated tag **object** id accepted because git peels it to the same tree; a stash-only commit refused with `RECEIPT-REV-ABSENT` + `RECEIPT-INSTRUMENT-DIGEST-MISMATCH`, `SUMMARY receipts=3 findings=2`, `EXIT=1`), `census/round-57/records/c1-matrix-run.txt` (436 B, the official matrix run log: the same `run-matrix.sh` command over the L1's `/fast/scratch/hyaku/souji-r57/SoujiR57/official` scratch, `observed: c1-matrix-v5 SAME / c1-matrix-v6 SAME`, `EXIT=0` — consistent with my independent byte comparison), and `corpus/lessons/round-57.md` (10 381 B; sections `## Gate`, `## Mistakes`, `## Errata to frozen prose`, `## Named limits carried into r58`, `## Routed-item disposition (r56 → r57)`). None is in any commit: `git cat-file -e HEAD:corpus/lessons/round-57.md` → `exists on disk, but not in 'HEAD'` (rc=128). HEAD remained `80548212`.

**Confidence:** high for the commands' outputs; medium only for "expected" classification of the two modified files (contents not reviewed — out of scout scope).

---

## 6. Routed-item map (r56 routed defects 1–6)

Source: `corpus/lessons/round-56-verifier-spotcheck.md` `## Routed defects` (6 numbered items, `grep -c '^[1-6]\. '` = 6).

| # | routed defect (r56) | r57 artifact that instruments/repairs it | verifying command (run this session) | observed output | verdict |
|---|---|---|---|---|---|
| 1 | Standing-suite receipts name no measured revision (Q109) | `census/round-57/c2-counter.py` (gate) + `census/round-57/record-receipt.sh` (recorder) + `manifests/before.tsv` + `controls/c2-stub.py` + `records/c2-selftest-expected.tsv` | `python3 -B census/round-57/c2-counter.py --root . --manifest census/round-57/manifests/before.tsv`; `python3 -B … --selftest --work DIR`; recorder refusals in a scratch fixture repo | gate: `FINDING RECEIPT-REV-MISSING …`, `SUMMARY receipts=1 findings=1`, rc=1. selftest: `control=FALSE-GREEN-REJECTED stub_meets=1 cases=8`, `pass cases=8`, rc=0. recorder: short rev → `refused: rev is not full 40-hex`, rc=2; `HEAD` → rc=2; absent instrument → `refused: nope.py absent at <rev>`, rc=2; full40 → receipt with `instrument=`, `instrument_sha256=`, `rev=`, `EXIT=0`, rc=0 | **INSTRUMENTED** (gate+recorder verified). **Application OPEN**: `grep -cE '^rev=[0-9a-f]{40}$' census/round-56/records/landing-suite-final.txt` = 0 at base and HEAD; `manifests/after.tsv` does not exist yet |
| 2 | Wave composition: 3 executors fielded; planner exception explicit | `census/round-57/preregistration.txt:113` (`## Wave plan`) | `grep -n '12 seats' census/round-57/preregistration.txt`; `ls -1 .ufo/waves/round-57/w1/` | line 113: `12 seats: scout 1, connector 1, executor 3, … Attack roles 4 of 12 (33%). The canonical planner seat is held by the L1 … (the wave validator refuses planner)`; the w1 seat dirs show `S57executor01/02/03` and exactly 12 seat dirs + `swarm-registry.json` | **REPAIRED at plan + observed dispatch** (the seat dirs are gitignored; the committed evidence is the prereg text) |
| 3 | Ignored `.pyc` left behind; run counters with `-B` | r57 drivers/prereg use `python3 -B`; the r56 pyc is gone from disk | `find census/round-56 -name '*.pyc' \| wc -l`; `grep -c 'python3 -B' census/round-57/fixtures/run-matrix.sh census/round-57/preregistration.txt`; `git ls-files '*.pyc'` | 0 round-56 pyc; `run-matrix.sh:2`, `preregistration.txt:5`; 5 tracked pyc remain from r10/r26 (unrelated, pre-existing). Earlier pycache dirs still exist on disk under `census/round-54/`, `census/round-55/` (ignored) | **REPAIRED for the named artifact**; no r57 control enforces the class → residual **NAMED-LIMIT** |
| 4 | C1 B4/C4 hidden-filing over-acceptance (main harm) | `census/round-57/c1-counter.py` v6 `inline` class + fixtures `B4-INLINE-NBSP-OPENER`/`C4-INLINE-CLOSED-COMMENT`/`C6-INLINE-SAME-LINE` + `records/matrix-dryrun/*` + `records/m1-red-before.txt` | matrix arms (§3); direct v6 run on B4/C4; v6 selftest | v5 exit 0 on B4/C4; v6 exit 1 with `findings_all=CORRECTION-IN-FENCE,CORRECTION-IN-FENCE` and both details `hidden_by=inline`; C6/F29/F17/F18/F19 exit 0 under both arms; `SELFTEST pass cases=36` | **REPAIRED** |
| 5 | Selftest kill-power gaps: all findings/summary fields; C2 row-set meta-test | C1: `c1-counter.py:665` `passed = (rc == want_rc) and (got_find == want_find)` (full ordered list) + `records/c1-selftest-expected.tsv` (3 columns per row) + `records/m1-red-before.txt` (M1 survives first-finding-only, killed by all-findings) | `grep -n 'passed = ' census/round-57/c1-counter.py`; `tail -1 records/c1-selftest.txt`; `cat records/m1-red-before.txt` | line 665 as above; `SELFTEST pass cases=36`; M1 record: first-finding arm `pass` rc=0 (mutant SURVIVES), frozen-v6 arm `fail` rc=1 (mutant KILLED) | **PARTIAL — M1 arm REPAIRED.** Residuals OPEN: no SUMMARY-field assertion (both `*-selftest-expected.tsv` contain 0 `SUMMARY` tokens); C2 selftest compares only findings (`c2-counter.py:251 passed = (got == want)`, rc not asserted) and has **no row-set-guard meta-case** (8 cases: ABSENT, DIGEST-MISMATCH, KEEP-ONLY, MISSING-REV, NO-EXIT, NOT-FULL40, REV-OK, SHORT-REV); no M7 (LF-only numstat) red-before/after receipt |
| 6a | Sentinel LOW: `.pyc` without `-B` | same as #3 | same as #3 | same as #3 | **REPAIRED** (specific artifact) |
| 6b | Sentinel MEDIUM: quadratic correction-line work at `c1-counter.py:331/335` | none — `line_zones` body is byte-identical v5→v6 | `python3 -B <seat>/…` function-body comparison (`function-diff.txt`): sha256 of `line_zones` | v5 `314032a8479c6dc6…` = v6 `314032a8479c6dc6…`, `identical=True` (25 lines); `numstat_deletions` also identical | **OPEN** |
| 6c | Sentinel LOW: raw terminal control bytes | none — no control-byte handling in `c1-counter.py`, `c2-counter.py`, `record-receipt.sh` | `grep -n 'x1b\|isprintable\|control\|\\\\033\|translate'` over the three files | only prose/selftest-control hits (`F29 visible-prose control`, `SELFTEST control=…`); no byte sanitisation | **OPEN** |
| 6d | Sentinel: scratch symlink containment | `c2-counter.py` has `RECEIPT-SYMLINK` (refuses to read through a symlink receipt); fixture `FA8-SYMLINK-CLASS` exists in `build-fixtures.py` | `grep -n 'SYMLINK' census/round-57/c2-counter.py`; `grep -c SYMLINK census/round-57/records/c2-selftest-expected.tsv` | the finding id exists in the code path; the selftest expected file has **0** `SYMLINK` cases, and `run-matrix.sh` runs only `kind = C1` rows, so FA8 is built but never measured | **INSTRUMENTED, unverified** → **NAMED-LIMIT** |
| 6e | Sentinel: ~50 MB memory | none | — | no r57 artifact mentions memory; no measurement in the freeze | **OPEN** |

**Confidence:** high for rows 1–4, 6a–6d (commands above); row 5 and 6e rest on source reads and absence of artifacts, which is weaker evidence than a failing run.

---

## 7. OPEN items (explicit)

1. **`corpus/lessons/round-57.md` is not in any commit**: it is absent from the freeze tree and from HEAD (`git cat-file -e HEAD:corpus/lessons/round-57.md` rc=128), although the prereg cites it twice (`records/source-quotes.txt` + `## Gate`; "Mistake mined: see corpus/lessons/round-57.md `## Mistakes`"). An **untracked** working-tree copy appeared at 20:30:57 local with both cited sections (and `## Errata to frozen prose`, `## Named limits carried into r58`, `## Routed-item disposition (r56 → r57)`) — so the citation resolves on disk but not in a commit at snapshot.
2. **C2 after half not produced**: `census/round-57/manifests/after.tsv` is absent from disk and from `git ls-files` (only `before.tsv` is committed). Consequently C2 T2 (`SUMMARY receipts=3 findings=0`), T4 and T5's after-receipt check cannot be observed yet, and the capped `records/c2-before.txt` is the only receipt of the gate's two halves.
3. **Q109 repair not applied to the r56 receipt**: `census/round-56/records/landing-suite-final.txt` still carries no `rev=<full40>` (`grep -cE` = 0 at base and HEAD). The instrument exists; the receipt it was routed to was not re-recorded.
4. **Routed defect 5 residuals** (all absent from the freeze): SUMMARY-field assertions in either selftest expected file; a C2 row-set-guard meta-case; an assertion of the rc in the C2 selftest (`passed = (got == want)` only); an M7 (LF-only numstat) red-before/after receipt.
5. **Routed defect 6 residuals**: quadratic `line_zones` unchanged (6b), no control-byte sanitisation (6c), no memory measurement (6e), no symlink selftest case for `RECEIPT-SYMLINK` (6d).
6. **16 C2-family fixtures are built but unmeasured by the r57 commands**: `build-fixtures.py` emits 52 fixtures (36 `C1` + 16 `C2`: `FH*`, `FA1–FA8`, `FB1–FB3`, `FC1–FC3`), but `run-matrix.sh` selects `kind = C1` only, and the prereg's C2 population is the 8 in-file cases. Determinism of all 52 is verified; coverage of the 16 is not claimed by any r57 artifact.
7. **Task-brief datum vs prereg**: the brief says "the same command against the revision the prereg names for the three base pins"; the `## Pins` table marks only one pin `at base`. Resolved by additionally auditing the two prose-pinned base artifacts (§1) — both consistent.
8. **Lane is live / tip moved**: HEAD went `d749f7ee` → `80548212` (sources commit, parent = freeze) during this session; at the 20:30 status snapshot the tree had 2 modified + 10 untracked files, and three more untracked artifacts appeared by 20:32 (see the §5 delta) — all attributed in §5. Any later reader should re-run §5 rather than quote this snapshot.
9. **C2 named limit observed (not a defect claimed by this round)**: `records/probe-rev-shapes.txt` shows the gate accepts a receipt whose `rev=` is an **annotated tag object id** (git peels it to the same tree) and refuses a stash-only commit; the gate's durability surface is therefore "peelable commit **and** reachable from a non-jj ref", which is wider than "commit id" but still revision-binding. Recorded as an observation, not a verdict.

**Remaining unknowns (not resolvable read-only from the freeze):** whether the after receipts will bind the same revision and instrument digests correctly; whether the post-freeze matrix runs that produced the untracked `records/*` files were executed with `-B` and from clean scratch (the files' contents reproduce, but their environment is a sibling's claim); whether `corpus/lessons/round-57.md` lands before the round settles.

---

## 8. Bottom line

- **Pins:** 13/13 MATCH; the three base-side artifacts are consistent (v5 digest named and matched; receipt identity unchanged base→HEAD; ws-drift digest matched). No MISMATCH.
- **Determinism:** the two (three) builds differ only in the `dir` column (absolute scratch path); all 52 fixtures' `name/kind/base/tip/record_sha256` are identical, all commit objects resolve, and all 36 C1 base/tip pairs match the committed v5 dry-run — **0 differing rows**.
- **Arms:** both matrix TSVs reproduce the committed dry-runs **byte for byte** (sha256 equal); v5 exit-0 = 10/36, v6 = 8/36; only B4 and C4 change, each to two `CORRECTION-IN-FENCE` findings with `hidden_by=inline`; the five visible controls stay exit 0 under both arms.
- **C2 at base:** gate rc=1 with exactly `RECEIPT-REV-MISSING` on the r56 receipt; the stub is false-green (rc=0, `receipts=0 findings=0`); the selftest records `FALSE-GREEN-REJECTED`.
- **Host:** sources census rc=0 with `souji ok` (205 rows; 62 duplicate-URL warnings); jj state clean/ff at `80548212`; ten untracked entries, all this round's expected evidence.
- **Routed map:** defect 4 **REPAIRED**; defect 2 **REPAIRED** (plan + dispatch); defect 1 **INSTRUMENTED with application OPEN**; defect 3/6a **REPAIRED** (named artifact); defect 5 **PARTIAL** (M1 arm repaired, summary/row-set/M7 residuals OPEN); defect 6b–6e **OPEN/NAMED-LIMIT**.
