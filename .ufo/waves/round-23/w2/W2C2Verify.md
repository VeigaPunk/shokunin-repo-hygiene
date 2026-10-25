# W2C2Verify — attack on C2's verify path (round 23, wave 2, falsify)

Seat: L1Souji23.W2C2Verify. Artifact under attack: C2's verifier, `tools/souji-receipt-run.py`
`verify` — the committed blob at lane tip `1026900`, sha256
`6bb623b8e8ce40028aee740ee40d600963d253e494048ce1ef121d5007d63e45` — exercised against the five
committed receipts in `census/round-23/records/*.tsv`. All commands below were run from
`/home/vgpnk/Projects/shokunin/souji-shokunin`; scratch is `/var/tmp/souji-r23-w2-C2Verify2/`
(an earlier scratch, `…C2Verify/`, was deleted before the byte-pinning re-run).

## Byte pinning (the lane moved during the attack)

Attacked bytes are the **committed** blob, not a working-tree copy: `tools/souji-receipt-run.py`
at lane tip `1026900`, sha256 `6bb623b8e8ce40028aee740ee40d600963d253e494048ce1ef121d5007d63e45`.
Mid-attack (05:44:32) a sibling seat (`W2FixReceipt`) modified the working-tree copy to
`2761290d…`; its diff touches only run-side lines (`command_refusal` now scans every token for a
denied subcommand, `--out` uses `realpath`) and neither `blob_sha_bytes` nor `cmd_verify`. Every
decisive experiment was therefore **re-run against the pinned blob** (extracted with
`git cat-file blob 1026900:tools/souji-receipt-run.py`) and reproduced unchanged:

```
$ python3 <pinned> verify --root <lane> <each of the five receipts>      → rc=0, rc=0, rc=0, rc=0, rc=0
$ python3 <pinned> verify --root <lane> <c3 relabelled to 1208bfb>       → verify=ok rc=0
$ python3 <pinned> verify --root <lane> <declared-evidence relabelled to a211e4d1>
    RECEIPT-TOOL-DIGEST-MISMATCH	receipt 65817d0d0d48 != tree 58ddbfef46e0 at a211e4d1…   rc=2
$ python3 <pinned> verify --root <lane> <agreement-after relabelled to jj @ 5e8b78bf> → verify=ok rc=0
$ python3 <pinned> verify --root <lane> <c3 with tool=tools/souji-record-agreement.py>
    RECEIPT-TOOL-DIGEST-MISMATCH	receipt d5ed0805b10f != tree 617f4c9618c0 at 4765250…   rc=2
$ python3 <pinned> verify --root <lane> <c3 with tool=tools/../tools/souji-gate-check.py>
    RECEIPT-TOOL-ABSENT	tools/../tools/souji-gate-check.py absent at 4765250…            rc=2
$ python3 <pinned> run --root <lane> --rev 5e8b78bf… --tool tools/souji-gate-check.py --out … -- …
    REV-NOT-DURABLE	5e8b78bf… is not reachable from refs/heads|tags|remotes            rc=2, no receipt
$ python3 <pinned> verify --root <lane> <agreement-after relabelled to 5e8b78bf>          rc=0
$ python3 <pinned> verify --root <replace-ref clone> <c3 with tool_sha256=564af484…>       → verify=ok rc=0
$ GIT_NO_REPLACE_OBJECTS=1 python3 <pinned> verify --root <replace-ref clone> <same>
    RECEIPT-TOOL-DIGEST-MISMATCH	receipt 564af4848bbc != tree d5ed0805b10f at 4765250…   rc=2
$ GIT_DIR=<empty repo> python3 <pinned> verify --root <lane> <c3>   → RECEIPT-TOOL-ABSENT  (false refusal)
```

Line numbers below are the **committed blob's** (`1026900`); the current working tree is shifted
+1 after line 97 (e.g. `blob_sha_bytes` is `:130` committed, `:131` working tree).

## VERDICT: `falsified` — narrow, executed, and fixable in two lines

The claim's second limb (`.ufo/waves/round-23/preregistration.txt`, C2) is stated unconditionally:

> a verifier that refuses a receipt whose recorded tool digest is not the committed blob at the
> named revision

and the round's kill rule is:

> a receipt whose verify exits 0 while its tool bytes at rev differ from the recorded digest kills
> the claim

**Executed counterexample: `verify` exits 0 while the tool bytes committed at the receipt's rev
differ from the recorded digest.** The cause is visible in the committed bytes: `cmd_verify` reads
the object through `blob_sha_bytes` (`tools/souji-receipt-run.py:130-133`, committed blob), which
shells out with a raw `subprocess.run` and **no** `GIT_NO_REPLACE_OBJECTS` / `GIT_NO_LAZY_FETCH` /
`GIT_DIR` strip, while the sibling helper `git()` (`:112`) and the runner's `run_env` (`:182`) both
set them. A
`refs/replace` entry therefore changes what the verifier hashes. This is the *same defect shape*
the wave-1 seat `CritC2Value` used against the runner; the remediation recorded at
`corpus/lessons/round-23.md:128` ("the runner now … sets GIT_NO_REPLACE_OBJECTS/GIT_NO_LAZY_FETCH")
was applied to `run` only — the verifier, which is the subject of the clause, was not hardened.

Scope, stated plainly: the falsification requires a repository carrying a `refs/replace` ref. The
lane currently has **zero** (`git replace -l | wc -l` → `0`), so the five committed receipts are
not compromised today, and every receipt/tool/rev edit inside the lane behaved correctly
(§P1–§P3). This is a falsification of the verifier's unconditional sentence, not of the receipt set.

### The counterexample (scratch clone only — the lane was never written)

```
$ git -c maintenance.auto=false clone --quiet --no-local <lane> /var/tmp/.../repl
$ cd /var/tmp/.../repl
$ ORIG=$(git rev-parse 4765250:tools/souji-gate-check.py)          # 63ac63b8…
$ NEW=$(git hash-object -w /var/tmp/.../tampered.py)               # d623b082…
$ git replace "$ORIG" "$NEW"
$ git cat-file blob 4765250:tools/souji-gate-check.py | sha256sum
564af4848bbce53067abfbf4c11415dd8f23fd3af022464ca76f76ee68ddc085  -      # verify's read
$ GIT_NO_REPLACE_OBJECTS=1 git cat-file blob 4765250:tools/souji-gate-check.py | sha256sum
d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d  -      # run's read
```

Receipt = `gate-check-c3.tsv` with `tool_sha256=` set to `564af484…` (the replacement, i.e. **not**
the committed blob):

```
$ python3 tools/souji-receipt-run.py verify --root /var/tmp/.../repl  .../replaced-digest.tsv
verify=ok rev=476525026cdb179f2d49441e1cb6c6f7316f3124 tool=tools/souji-gate-check.py tool_sha256=564af4848bbce53067abfbf4c11415dd8f23fd3af022464ca76f76ee68ddc085
rc=0
$ GIT_NO_REPLACE_OBJECTS=1 python3 tools/souji-receipt-run.py verify --root /var/tmp/.../repl .../replaced-digest.tsv
RECEIPT-TOOL-DIGEST-MISMATCH	receipt 564af4848bbc != tree d5ed0805b10f at 476525026cdb179f2d49441e1cb6c6f7316f3124
rc=2
```

The only difference between the two runs is the env var, so the mechanism is isolated: the
verifier's object read is replace-affected.

### The fix (proved on a patched scratch copy, lane untouched)

`tools/souji-receipt-run.py:130-133` (committed blob) — route the read through the same hardened
environment the file already builds at `:112` (or simply call `git()` and take `.stdout`):

```python
proc = subprocess.run([... "cat-file", "blob", f"{rev}:{path}"], capture_output=True,
                      env={**{k: v for k, v in os.environ.items()
                              if k not in ("GIT_DIR", "GIT_WORK_TREE")},
                           "GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1"})
```

Measured on the patched copy (`/var/tmp/.../fixed-receipt-run.py`):

```
$ python3 .../fixed-receipt-run.py verify --root /var/tmp/.../repl .../replaced-digest.tsv
RECEIPT-TOOL-DIGEST-MISMATCH	receipt 564af4848bbc != tree d5ed0805b10f at 476525026cdb179f2d49441e1cb6c6f7316f3124
rc=2
$ GIT_DIR=/var/tmp/.../emptyrepo python3 .../fixed-receipt-run.py verify --root <lane> .../gate-check-c3.tsv
verify=ok … rc=0            # ambient GIT_DIR no longer spoofs the read (see F4)
$ for f in <the five receipts>; do python3 .../fixed-receipt-run.py verify --root <lane> "$f"; done
agreement-after.tsv rc=0 | declared-evidence-after.tsv rc=0 | gate-check-at-first-landing.tsv rc=0
gate-check-at-lane-base.tsv rc=0 | gate-check-c3.tsv rc=0
```

The fix is behavior-neutral for the landed receipt set and makes the claim's sentence true as
written. **Action: fix** (land the two-line hardening, re-run the five, record the output), and
extend `tests/fixtures/r23-receipt-run.py` with a case-9 that creates a `refs/replace` ref and
expects `RECEIPT-TOOL-DIGEST-MISMATCH` — the fixture's 8/8 never exercises this
(`tests/fixtures/r23-receipt-run.py:18-19`: case 3 mutates the tool in a *new* commit, which is a
different axis). If the round prefers not to change code this late, the alternative is to amend
`SCORECARD.md:92` from "refuses a digest that is not the committed blob" to "refuses a digest that
is not the blob reachable as `rev:tool` in a replace-free repository" and file the gap as residual —
but the frozen claim is unconditional, so amending the doc leaves the claim itself unverified.

## What was asked: which refusals fire, which do not, does any edited receipt still verify

### P1 — the five committed receipts, unedited: 5/5 verify

```
$ python3 tools/souji-receipt-run.py verify --root . census/round-23/records/<r>.tsv
declared-evidence-after.tsv      rc=0  verify=ok rev=9301d98c… tool=tools/souji-declared-evidence.py  tool_sha256=65817d0d…
agreement-after.tsv              rc=0  verify=ok rev=4765250…  tool=tools/souji-record-agreement.py    tool_sha256=617f4c96…
gate-check-at-lane-base.tsv      rc=0  verify=ok rev=1208bfb…  tool=tools/souji-gate-check.py          tool_sha256=d5ed0805…
gate-check-at-first-landing.tsv  rc=0  verify=ok rev=a211e4d1…  tool=tools/souji-gate-check.py          tool_sha256=d85c2696…
gate-check-c3.tsv                rc=0  verify=ok rev=4765250…  tool=tools/souji-gate-check.py          tool_sha256=d5ed0805…
```

Same result with the prereg's literal command (no `--root`, cwd = lane): all five `rc=0`.
C2 counter `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l` → `5` (target ≥4); at the lane
base the same counter over `1208bfb` is `0` (do-nothing control holds).

### P0 — the prereg's mandated refusal demonstration fires

```
$ python3 tools/souji-receipt-run.py verify --root . <receipt with tool_sha256=5b8025a8…>
RECEIPT-TOOL-DIGEST-MISMATCH	receipt 5b8025a80000 != tree d5ed0805b10f at 476525026cdb179f2d49441e1cb6c6f7316f3124
rc=2
```

### P2 — `rev=` edited to a different committed revision: 18 of 30 verify, 12 refuse

Candidate revs: `1208bfb` (lane base), `a211e4d1` (first landing), `4765250`, `c0eeaa7`,
`1026900` (tip), `9301d98c` (r22 tip), `5e8b78bf` (jj `@`, not durable). Every receipt's own rev
excluded.

| receipt | passes | refuses |
|---|---|---|
| agreement-after | c0eeaa7, 1026900, **5e8b78bf** | 1208bfb, a211e4d1, 9301d98c → `RECEIPT-TOOL-ABSENT` (tool absent at those revs) |
| declared-evidence-after | 1208bfb, 4765250, c0eeaa7, 1026900, **5e8b78bf** | a211e4d1 → `RECEIPT-TOOL-DIGEST-MISMATCH 65817d0d != 58ddbfef` |
| gate-check-at-first-landing | — | all six → `RECEIPT-TOOL-DIGEST-MISMATCH d85c2696 != d5ed0805` |
| gate-check-at-lane-base | 4765250, c0eeaa7, 1026900, 9301d98c, **5e8b78bf** | a211e4d1 → `DIGEST-MISMATCH` |
| gate-check-c3 | 1208bfb, c0eeaa7, 1026900, 9301d98c, **5e8b78bf** | a211e4d1 → `DIGEST-MISMATCH` |

Totals: 18 `verify=ok`, 9 `RECEIPT-TOOL-DIGEST-MISMATCH`, 3 `RECEIPT-TOOL-ABSENT`. **In no case did
an edited `rev=` produce a pass whose recorded digest differs from the blob at the new rev** — the
claim's stated contract held on this axis. The passes are exactly the revs where the tool blob is
byte-identical (gate-check `d5ed0805` at 1208bfb/4765250/c0eeaa7/1026900/9301d98c/5e8b78bf;
declared-evidence `65817d0d` at all but a211e4d1).

Consequence — **a relabeled receipt can verify while its recorded output is false at the new rev**.
`gate-check-c3` relabeled to `1208bfb` returns `verify=ok`, but its own recorded `cmd` at that rev
fails, because the round-23 paths it names do not exist there:

```
$ git cat-file -e 1208bfb4:census/round-23/records/empty-slice   → ABSENT
$ git cat-file -e 1208bfb4:corpus/knowledge/repo-size-census-readonly.md → ABSENT
$ <in a clone at 1208bfb> python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/repo-size-census-readonly.md corpus/knowledge/count-objects-garbage-readings-r25.md \
    --snapshot-dir census/round-23/sources --slice census/round-23/records/empty-slice \
    --slice-verdicts census/round-23/records/empty-verdicts
FAIL corpus/knowledge/repo-size-census-readonly.md entry-missing: …
FAIL corpus/knowledge/count-objects-garbage-readings-r25.md entry-missing: …
FAIL slice slice-missing
entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=3
rc=1
$ <same cmd at 4765250>  entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0 ; rc=0
```

So `verify=ok` proves the *tool bytes* at rev, not that the receipt was produced there. That is
**not** a breach of C2 as frozen (the claim binds tool sha256, not the tree), but it is the exact
r22-D3 defect shape the claim says it closes, one level up. **Action: disclose** in
`SCORECARD.md:92` and the report ("a receipt's `rev=` may be relabeled to any rev with identical
tool bytes and still verify; the measured tree is not bound"), or bind it — add `tree=<40 hex>` to
the receipt v1 header and compare in `cmd_verify`. Do not let the SCORECARD imply `verify=ok`
means the counts are true at the rev.

### P3 — `tool=` edited to a different path: 0 of 40 non-identity edits verify

Nine substitutions per receipt: the three sibling tools, an absent path, `tools`, a `..` traversal,
`/etc/passwd`, and a trailing-space variant.

```
sibling tool at same rev        → RECEIPT-TOOL-DIGEST-MISMATCH  (e.g. receipt 617f4c96 != tree d5ed0805)
absent / directory / .. / abs   → RECEIPT-TOOL-ABSENT           (git refuses the path shape; no escape)
trailing-space path             → RECEIPT-TOOL-ABSENT
own path (identity, control)    → verify=ok
```

No bypass exists via a duplicate-content path: at `4765250` each tool's sha256 matches exactly one
path in the tree (checked all 3,964 blobs), so `tool=` cannot be redirected to a twin. **This axis
of the claim holds cleanly.**

### P4 — `verify` accepts a revision that `run` refuses (durability asymmetry)

```
$ python3 tools/souji-receipt-run.py run --root . --rev 5e8b78bf396e3e6c4b30ad9bed76874deb03b4e7 \
    --tool tools/souji-gate-check.py --out /var/tmp/.../never.tsv -- python3 tools/souji-gate-check.py --help
REV-NOT-DURABLE	5e8b78bf396e3e6c4b30ad9bed76874deb03b4e7 is not reachable from refs/heads|tags|remotes
rc=2      (no receipt written)

$ python3 tools/souji-receipt-run.py verify --root . .../gate-check-c3--5e8b78bf.tsv
verify=ok rev=5e8b78bf396e3e6c4b30ad9bed76874deb03b4e7 tool=tools/souji-gate-check.py tool_sha256=d5ed0805…
rc=0
```

`5e8b78bf` is the jj working-copy commit (`git for-each-ref --contains 5e8b78bf … refs/heads
refs/tags refs/remotes` → empty). `cmd_verify` never calls `durable_rev` (`:123`), so the Q37 rule
("refs/jj/* never counts") is enforced on the write side and not on the read side. All five
landed receipts name durable revs, so adding the check is behavior-neutral for them. **Action: fix**
(`if not durable_rev(root, rev): return refuse("RECEIPT-REV-NOT-DURABLE", …)` before the digest
compare) **or disclose** in `SCORECARD.md:92`.

### P5 — text edits that verify anyway

```
cmd= rewritten to a different tool      → rc=0
rc=0 → rc=7                             → rc=0
utc= rewritten to 1999-01-01            → rc=0
stdout counts → entries=99 ok=99 …      → rc=0
counts line moved into the stderr fence → rc=0
header rev/tool order swapped           → RECEIPT-MALFORMED, rc=2
```

The first four are the pre-disclosed limit ("the receipt records text … the digest binds the bytes
the command ran against, not the fact that the command ran") — **accept**. The fifth is a smaller,
separate gap: `parse_receipt` stores `_body` from the stdout fence onward (`:234`) and the counts
check searches that whole body (`:258`), so a receipt with an empty stdout fence verifies.
**Action: disclose or tighten** (search only `lines[idx+1:stderr_idx]`).

### P6 — the `--tool` digest does not bind the executed program

```
$ python3 tools/souji-receipt-run.py run --root . --rev 4765250… --tool tools/souji-gate-check.py \
    --out .../decoupled.tsv -- python3 tools/souji-record-agreement.py --rev 4765250…
receipt=… tool_sha256=d5ed0805… rc=1 counts=keys=4 records=4 occurrences=18 mismatches=1
$ python3 tools/souji-receipt-run.py verify --root . .../decoupled.tsv
verify=ok … rc=0
```

A receipt naming `tool=tools/souji-gate-check.py` while its `cmd=` ran
`tools/souji-record-agreement.py` verifies. `run` takes the digest of `--tool`'s path
(`:185-189`), and nothing ties `--tool` to `argv`. `SCORECARD.md:92` and
`report-draft.md:25` say "tool sha256 of the bytes the command ran against" — false as written.
**Action: fix the sentence** to "tool sha256 of the blob at `--tool` at `rev`" (and, if wanted,
refuse when `os.path.basename(argv[-1])`/the script operand is not `--tool`), or disclose.

### P7 — minor: a nonexistent revision is reported as tool absence

```
$ verify <receipt with rev=000…0>
RECEIPT-TOOL-ABSENT	tools/souji-gate-check.py absent at 0000000000000000000000000000000000000000
```

Refusal fires, but the code misattributes the cause (a rev that does not exist is not a tool
problem). **Action: accept** (cosmetic), or add `RECEIPT-REV-ABSENT` after the durability fix.

## Findings by severity

| # | severity | file:line | finding | action |
|---|---|---|---|---|
| F1 | **HIGH** | `tools/souji-receipt-run.py:130-133` (used at `:252`) | verify's object read is not replace-hardened (no `GIT_NO_REPLACE_OBJECTS`/`GIT_NO_LAZY_FETCH`, inherits ambient `GIT_DIR`), unlike `git()` `:112` and `run_env` `:182`; a `refs/replace` ref makes verify accept a digest that is not the committed blob → claim's kill rule fires by its letter | **fix** (2 lines, proof above) + fixture case 9 |
| F2 | HIGH (evidence) | `tools/souji-receipt-run.py:238-261`; `SCORECARD.md:92` | `rev=` can be relabeled to any rev with identical tool bytes and still verify — 18/30 passes, one provably false at the new rev (`gate-check-c3` @ `1208bfb`: `fail=3` when actually run) | **disclose** (or bind `tree=`) |
| F3 | MEDIUM | `tools/souji-receipt-run.py:249-252`; `:123` | verify never calls `durable_rev`; a jj working-copy rev (`5e8b78bf`) verifies while `run` refuses `REV-NOT-DURABLE` | **fix** or disclose |
| F4 | MEDIUM | `SCORECARD.md:92`, `.ufo/waves/round-23/report-draft.md:25` | "tool sha256 of the bytes the command ran against" overstates: the digest binds `--tool`'s blob, not the executed program (P6) | **fix sentence** |
| F5 | LOW | `tools/souji-receipt-run.py:234,258` | `RECEIPT-COUNTS-ABSENT` searches stdout+stderr, so an empty stdout fence verifies | **disclose** or tighten |
| F6 | LOW | `tools/souji-receipt-run.py:252` | nonexistent rev reported as `RECEIPT-TOOL-ABSENT` | accept |
| F7 | — | prereg C2 "Named limits" | `cmd`/`rc`/`utc`/`stdout` edits pass verify | **accept** (pre-disclosed) |
| F8 | — | `corpus/lessons/round-23.md:128` | the wave-1 remediation text implies the whole runner is replace-hardened; true of `run`, false of `verify` | amend with F1's fix |

Adjacent, out of my artifact: `census/round-23/records/agreement-after.tsv` records `rc=1` and
`keys=4 records=4 occurrences=18 mismatches=1` (K1 `value-disagree` at `SCORECARD.md:14`). That
receipt verifies correctly, but C1's target is `M_after = 0`; the C1 seat owns that. Flagged only
so it is not lost — the C2 receipt set is internally honest about it.

## Residual risk

- `verify` proves exactly one thing: the recorded `tool_sha256` equals sha256 of `rev:tool` as git
  reads it in a replace-free repo. It does not prove the counts were produced at that rev, by that
  tool, or that the command ran. All evidential weight of the five receipts therefore rests on the
  `run` path, which `verify` cannot re-check. The round's docs say "not a proof of execution"; they
  do not say "not a proof of the measured tree", which is the gap F2 asks to disclose.
- `blob_sha_bytes` also lacks `GIT_NO_LAZY_FETCH`, so on a promisor/partial clone the verifier
  could trigger a lazy fetch from `origin` — a read-side network effect the runner forbids for
  `run` ("never fetches from a remote"). **[INFERENCE]** — not executed; cited from
  `tools/souji-receipt-run.py:130-133` vs `:112`. The F1 patch closes it too.
- The five receipts are not compromised today (`git replace -l` → 0; every `rev=` durable; 5/5
  `verify=ok`).

## Verification gaps (what I did not run)

- No promisor/partial-clone experiment (F1 residual, marked inference).
- No concurrent-writer / race test; no test of `run`'s scratch clone under a full `/var/tmp`.
- I did not re-execute `run` for all five receipts (that would rewrite them); only `verify`, plus
  one `run` for the decoupling probe (P6) and one for the durability refusal (P4), both with
  `--out` under `/var/tmp`.

## Bounds

Read-only against the lane: no git/jj mutation, no `rm`/`mv`, no signals, no installs (none
needed — `python3` and `git` were already present). All edits were made to copies under
`/var/tmp/souji-r23-w2-C2Verify/` and `/var/tmp/souji-r23-w2-C2Verify2/`; the clones there were
made with `GIT_OPTIONAL_LOCKS=0` from the lane and written only inside `/var/tmp`. Both scratch
directories were removed before finishing.

The only file this seat wrote is this report. The lane's `git status --porcelain` **changed during
the attack**, but not by this seat: at 05:33 it showed `?? .ufo/waves/round-23/report-draft.md` and
`?? census/operator-sweep-20261019/`; by 05:47 it also showed five modified tracked files
(`census/round-23/records/refusal-stale-digest.txt`, `corpus/lessons/round-23.md`,
`tests/fixtures/r23-locator-heading.py`, `tests/fixtures/r23-record-agreement.py`,
`tools/souji-receipt-run.py`) and a dozen sibling wave-2 reports, from concurrent seats. I did not
revert, stage, or touch any of them. The `tools/souji-receipt-run.py` modification is exactly why
§"Byte pinning" exists: the report's evidence is pinned to the committed blob `6bb623b8`, not to a
moving working-tree file. The full 30-cell rev matrix and 45-cell tool matrix ran while `sha256sum
tools/souji-receipt-run.py` still reported `6bb623b8` (checked at 05:35, before the 05:44:32
sibling edit); every decisive cell was then re-run against the pinned blob and reproduced
unchanged.
