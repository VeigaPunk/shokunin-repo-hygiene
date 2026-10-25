STATUS: PASS — D3 verified REAL against committed bytes at lane base `1208bfb`, with one clause mis-framed (the run and the cited digest agree; the staleness is report-vs-tip) and one clause understated (fail=10 is not reproducible at the base tool at all). The round's planned repair closes D3(a) and closes D3(b) only in a synthetic-absence form; D3(c) is outside the lane's write scope and needs the append-only substitute named in F5.

# RevD3 — routed defect D3 (r22 C2 after-run digest / missing before receipt)

Read-only seat. No lane write outside this file; no `git`/`jj` mutation; no install; no pacman
transaction; no `/proc` census; no operator-sweep contents. Scratch under
`/var/tmp/souji-r23-RevD3/` (removed before finishing). No LSP device is mounted in this session,
so caller/definition checks are direct reads plus executions, not semantic navigation.

## Evidence

**E1 — the digest chain, at lane base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`.**
`git rev-parse <rev>:tools/souji-gate-check.py` and `git cat-file blob <rev>:tools/... | sha256sum`:

```
a211e4d   4309d76930a1  d85c269624f4
4a6ee90   f26aa72855e3  5b8025a83f16
c9f1fe3   f26aa72855e3  5b8025a83f16
c1664fc   f26aa72855e3  5b8025a83f16
7bc458c   f26aa72855e3  5b8025a83f16
8680755   f26aa72855e3  5b8025a83f16
9fcc4f7   63ac63b8e481  d5ed0805b10f
dd8a6b7   63ac63b8e481  d5ed0805b10f
9301d98   63ac63b8e481  d5ed0805b10f
77d6595   63ac63b8e481  d5ed0805b10f
1208bfb   63ac63b8e481  d5ed0805b10f
```

So `5b8025a8…` **is** the sha256 of blob `f26aa728` — the tool that produced the after run.

**E2 — the lane's own two records disagree.** `census/round-22/attempt2/instrument-digests.txt:2`
reads `d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d  tools/souji-gate-check.py`
while the fleet report `.ufo/reports/round-22/souji.md:65` cites the digest as `5b8025a8…` and the
same report declares its tip `77d6595` (E1: tool at that tip is `d5ed0805`).

**E3 — the after figure survives the final tool.** Materialized `git archive 1208bfb` under
`/var/tmp/souji-r23-RevD3/lane` (`sha256sum tools/souji-gate-check.py` =
`d5ed0805b10f283f…`, `git hash-object` = `63ac63b8e481`), then the frozen argv:

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
              corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
REAL_RC=0
```
`--selftest` at the same bytes: `selftest=9/9`, `SELFTEST_RC=0`.

**E4 — no bound receipt anywhere.** Frozen C2 counter at the base:
`grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l` → `0`. Fleet side:
`grep -rln '^tool_sha256=' .ufo/` → no match. The only committed trace of the after run is
`.ufo/waves/round-22/attempt2/residual/evidence/counter.txt`, whose own header pins
`tools/souji-gate-check.py f26aa72855e38ee866689d3874e2b2ef8d63212a` and names
`last-observed tip 8680755` — i.e. pre-`9fcc4f7` bytes, no `rev=`/`rc=` receipt header.

**E5 — fail=10 is tool-version-specific.** Same argv, absent entries and absent verdicts, run
against the base tree with each committed tool version:

```
tool@a211e4d  entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=10
tool@4a6ee90  entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=2
tool@8680755  entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=2
tool@9fcc4f7  entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=2
```

**E6 — no durable rev holds the tool without the entries.** `git show --stat a211e4d` adds
`tools/souji-gate-check.py`, both entries, `quarantine-slice` and `slice-verdicts.tsv` together;
parent `4edb25d` has none of the four (`git cat-file -e` → absent). Scan of every rev in
`4edb25d..1208bfb` for tool-present-and-entries-absent: no match.

**E7 — closure mechanism exercised end to end** with the round's runner
(`tools/souji-receipt-run.py`, untracked, digest `8ba27613…` at run time):

```
run --rev 1208bfb… --tool tools/souji-gate-check.py --out /var/tmp/…/gate-check-after.tsv
  → tool_sha256=d5ed0805b10f283f… rc=0 counts=entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
verify …/gate-check-after.tsv
  → verify=ok rev=1208bfb… tool_sha256=d5ed0805b10f283f…            VERIFY_RC=0
verify on the same receipt with tool_sha256 swapped to 5b8025a8…
  → RECEIPT-TOOL-DIGEST-MISMATCH  receipt 5b8025a83f16 != tree d5ed0805b10f at 1208bfb…  RC=2
run --rev a211e4d… --tool tools/souji-gate-check.py --entries <absent paths> …
  → tool_sha256=d85c269624f4ade5… rc=1 counts=entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=10
verify …/gate-check-before.tsv → verify=ok  VERIFY_RC=0
```

## Findings

**F1 (real, mis-framed).** The spot-check's mechanism sentence — the after-run was measured with
`f26aa728` "while the report cited `5b8025a8…`" — describes a disagreement that does not exist:
`5b8025a8…` is the sha256 **of** blob `f26aa728` (E1). Run and report agree; the defect is
staleness against the tip the report itself names (`77d6595` → `d5ed0805`), and an in-lane
contradiction between `census/round-22/attempt2/instrument-digests.txt:2` and
`.ufo/reports/round-22/souji.md:65` (E2).

**F2 (severity correction).** D3 is a binding defect, not a value defect: the after counts
reproduce exactly at the base bytes with the base tool (E3). No number needs changing.

**F3 (real, understated).** "No before (`fail=10`) receipt exists" is true (E4) and stronger than
stated: `fail=10` cannot be emitted by the base tool for any input — the documented absent-input
argv gives `fail=2`, the real argv gives `fail=0` (E5, E3). The historical figure belongs to
`tool@a211e4d` (`d85c2696…`).

**F4 (constraint the spot-check missed).** The historical before state — tool present, entries
absent — exists at no durable revision, because tool and inputs co-landed at `a211e4d` (E6).
A "before" receipt is therefore necessarily a *synthetic-absence* measurement at `a211e4d`, not a
recovery of the r22 pre-landing tree. Any receipt presenting `fail=10` under `d5ed0805` is false.

**F5 (judgment on the planned repair).** Round-23 prereg C2 (≥4 bound receipts, gate-check before
and after) closes D3 as follows: **D3(a)** closed by an after receipt bound to a rev whose tool
blob is `63ac63b8` with `rc=0` and `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0` — proven
achievable (E7). **D3(b)** closed only in the `a211e4d`/`d85c2696…`/synthetic-absence form (E7);
a receipt at the base tool must read `fail=2` and say so. **D3(c)** — replacing the stale digest in
`.ufo/reports/round-22/souji.md:65` — is **not achievable inside the lane**: that file is tracked
in the fleet repo `/home/vgpnk/Projects/shokunin` (not in the lane tree at `1208bfb`) and is filed
evidence; editing it is both a fleet write and a rewrite of filed bytes.

**F6 (operability gap in the round's own runner).** `tools/souji-receipt-run.py:108` refuses
`OUT-IN-REPO` (`--out` inside `--root`), while the frozen counter requires receipts under
`census/`. Every receipt must be produced outside the lane and copied in; the round must state the
copy is byte-identical (sha256 of the produced file equals the committed blob), else the binding
is asserted rather than shown. The file is untracked and was edited by a peer mid-review (digest
`359cc41…` at first read → `8ba27613…` at run time).

**F7 (minor, overstatement).** "No committed re-run" is not provable: `ResSliceVerdicts-gate-counter.txt`
was added at `dd8a6b7`, after the `9fcc4f7` tool change, and records
`entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0` with `EXIT=0` — but it binds neither `rev`
nor a tool digest, so it is unverifiable in both directions. The defensible statement is "no
*bound* re-run exists".

## Minimal repair that closes D3

- **R1 (D3-a).** New file `census/round-23/records/gate-check-after.tsv`, receipt v1:
  `rev=1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (or any later rev whose tool blob is still
  `63ac63b8`), `tool=tools/souji-gate-check.py`,
  `tool_sha256=d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d`,
  `cmd=` the frozen argv verbatim (including `--round-date 2026-10-25`), `rc=0`, stdout the single
  line `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`.
  Wording constraint: no `5b8025a8` token may appear in this receipt.
- **R2 (D3-b).** New file `census/round-23/records/gate-check-before.tsv`:
  `rev=a211e4d1bf6ea592670d16269f34e9f67f33e8b3`,
  `tool_sha256=d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00`, `rc=1`,
  stdout ending `entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=10`, plus one label line
  stating the entries and verdicts paths were absent at that rev and that no durable rev holds the
  tool without them (F4). Wording constraint: `fail=10` may appear **only** with `d85c2696…`; if
  the receipt binds `d5ed0805…` its counts must read `fail=2`.
- **R3 (D3-c, append-only).** Do not touch `.ufo/reports/round-22/souji.md`. Instead: (i) append a
  `LOG.md` block after the last line carrying the marker `superseded by` and naming both digests
  (`5b8025a8…` = blob `f26aa728`, tool through `8680755`, the tool that produced the after run;
  `d5ed0805…` = blob `63ac63b8`, tool from `9fcc4f7`) with the note that the report's line-65
  digest predates the tip it names; (ii) the same sentence in the round-23 fleet report
  (`.ufo/reports/round-23/souji.md`, a new file landed by `fleet-commit.sh`) and in
  `corpus/lessons/round-23.md`; (iii) optionally one row per rev in
  `census/round-23/records/tool-digest-history.tsv` so E1 is machine-checkable.

**Closure command.** `python3 tools/souji-receipt-run.py verify --root /home/vgpnk/Projects/shokunin/souji-shokunin census/round-23/records/gate-check-after.tsv` and the same for
`gate-check-before.tsv` (both must print `verify=ok`, rc 0), then
`grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l` → ≥4, and the R3 marker present in
`LOG.md`.

## Attack log

**A1 — frozen C2 counter and verifier cannot distinguish executed from typed (demonstrated).**
I wrote a receipt header binding `rev=1208bfb…`, `tool_sha256=d5ed0805…` (correct digest), `rc=1`,
stdout `entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=10` — a line the tool at that rev cannot
emit for that argv (E3: it emits `fail=0`). `verify` returned `verify=ok`, `FORGED_VERIFY_RC=0`.
The prereg's kill rule (digest mismatch) is not tripped. Reported as ATTACK, predicate untouched:
the frozen counter counts a header shape, and the frozen verifier checks the digest and the
presence of a counts line, not its reproducibility. A non-predicate mitigation the round may add:
a `recheck` verb that re-runs the receipt's own `cmd` at its own `rev` and diffs stdout, and a
round-level statement that `verify=ok` is not execution proof.

**A2 — the tempting dishonest repair.** Writing `fail=10` into a before receipt bound to
`d5ed0805…` passes A1's verifier and would satisfy the prereg's "gate-check before" slot while
being false. R2's wording constraint exists to forbid exactly this.
