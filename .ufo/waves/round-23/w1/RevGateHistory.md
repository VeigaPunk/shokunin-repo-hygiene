# RevGateHistory — r22 gate-check (C2) digest history reconstruction

author: L1Souji23.RevGateHistory
date: 2026-10-25
scope: read-only; `git` read commands only; no writes outside this file

## Status

STATUS: PASS — the r22 gate-check history is fully reconstructed from committed bytes: every
recorded digest for `tools/souji-gate-check.py` is enumerated and bound to the revision where it
is actually true; the tool's sha256 at the lane base and at the current branch tip (identical
revisions) is `d5ed0805…`; and the residual seat's C1 line (`tool@c9f1fe3 x decl@f8f0b4a -> 
assertions=63 resolved=61 skipped=39 mismatches=2 rc=1`) and the report's `5b8025a8` digest are
BOTH true at the same revision (`c9f1fe3`/`f8f0b4a`/`8680755`), because git blob `f26aa728`
and sha256 `5b8025a8…` are two representations of the same tool bytes. The D3 "measured with
f26aa728 while the report cited 5b8025a8" mismatch is therefore a false dichotomy; the residual
truth in D3 is that the digest is stale at the report's named tip `77d6595` (the tool changed to
`63ac63b8`/`d5ed0805…` at `9fcc4f7`), and that no "before" receipt exists in any form.

## Evidence

### E1. Lane base and current tip are the same revision

```
$ git rev-parse HEAD                      -> 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd
$ git rev-parse 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd -> 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd
```

Branch master, ahead=0 behind=0 (preregistration). So (b)'s "base" and "tip" are one revision:
`1208bfb`.

### E2. Tool bytes per revision (blob sha1 = sha256 of file content)

| revision | tool blob (git sha1) | tool sha256 | note |
|---|---|---|---|
| a211e4d, 70af563, 2a130b4, 3216c19, 5ff5041, d6a75ba | 4309d76930a18891dd1d3446364c4c1dfecc275f | d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00 | first gate checker (a211e4d) |
| af73b8b, 5fdd5d5, ee1aef2, 4a6ee90, c9f1fe3, f8f0b4a, 8990ae4, c1664fc, 7bc458c, 8680755 | f26aa72855e38ee866689d3874e2b2ef8d63212a | 5b8025a83f16957cb2ff6aca0adecfc3a6a1ff796c3eed1d70018ecc339b3062 | hardened at af73b8b |
| 9fcc4f7, dd8a6b7, 9301d98, 77d6595, 1208bfb | 63ac63b8e48133afad8a0dd263f0fbe5d1abc5a6 | d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d | hardened at 9fcc4f7 (2-line diff) |

`git log --oneline -- tools/souji-gate-check.py`:
`9fcc4f7 round-22: gate-check reason/locator loopholes closed; entry reasons tightened`,
`af73b8b round-22: review-driven hardening of gate-check, entry reasons and row wording`,
`a211e4d round-22: declared-evidence audit tool, assimilation entries and gate checker`.

The worktree at `1208bfb` has the same bytes: sha256 `d5ed0805…` (14269 bytes), so the tool is
committed-clean at the tip. The `9fcc4f7` change is exactly:
`ROW_REASON_RE = re.compile(r"reason:\s*\S", re.I)` -> `r"reason:\s*[^\s—–-]\S*"` and
`locator_probe = SNAPSHOT_RE.sub("", line)` -> `QUOTE_RE.sub("", SNAPSHOT_RE.sub("", line))`.

### E3. Digest census — every recorded digest for the tool, with where it is true

| digest (recorded form) | recorded at | true at |
|---|---|---|
| d85c269624f4ade5… (sha256) | CritC2Counter.md:29 (HEAD d6a75ba); RevGate.md:19 (HEAD a211e4d); MutQuote.md:10,19,139; RevGate.md:13 table ("d85c2696…"); pre-dd8a6b7 instrument-digests.txt | a211e4d..d6a75ba |
| 5b8025a83f16957c… (sha256) | Sentinel.md:483 ("was d85c269624f4ade5…"), Sentinel.md:555 (sha256sum at ee1aef2); ResDeclaredEvidence.md:46; ResClaims-instrument-digests.txt:2; ResClaims-commands.txt:14,50 | af73b8b..8680755 |
| f26aa72855e38ee8… (blob sha1) | residual/evidence/counter.txt:6,14; residual/evidence/attacks.txt:3; ResGateCheck.md:35 | af73b8b..8680755 |
| d5ed0805b10f283f… (sha256) | census/round-22/attempt2/instrument-digests.txt:2 (committed at dd8a6b7); also at the worktree and base tip | 9fcc4f7..1208bfb |
| f2d18e8273d56467… (sha256, dirty) | CritC2Counter.md:37 ("differs from HEAD") | no committed revision (transient worktree between d6a75ba and af73b8b) |
| 66c7af71840470e9… (sha256) | ImplGateCheck.md:12; Sentinel.md:216 | of .ufo/waves/round-22/attempt2/w1/evidence/impl-gate/souji-gate-check.py — the staged copy, NOT `tools/` |

`2a130b47…` at RevGate.md:12 is a commit id (40-hex), not a digest. No `tool_sha256=` receipt
lines exist anywhere in `census/` (grep found none). The only receipts committed for the gate
check are the wrapper files `counter.txt`, `attacks.txt`, `ResGateCheck.md` (blob-identifier
form) and `instrument-digests.txt` (sha256 form, committed only after 9fcc4f7).

### E4. The after-run and the `f26aa728` = `5b8025a8` identity

`ResGateCheck.md:35` records the tool used for the real C2 run as `f26aa728…` and states it
was "the committed blob at every tip" of the four revs observed (`4a6ee90`, `c1664fc`,
`7bc458c`, `8680755`). The sha256 of that blob is exactly `5b8025a8…` (E2). Sentinel.md:555
independently measured `sha256sum tools/souji-gate-check.py` at `ee1aef2`:
`5b8025a83f16957cb2ff6aca0adecfc3a6a1ff796c3eed1d70018ecc339b3062`, and the same run returned
`entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0 rc=0`.

Verbatim quote (bytes opened this run, corpus/lessons/round-22-verifier-spotcheck.md:142):
"But the after run was measured with tool blob `f26aa728` (= `c9f1fe3`…`8680755`); the tool
changed at `9fcc4f7` to blob `63ac63b8` (`sha256 d5ed0805…`, the digest `instrument-digests.txt` records), and"

### E5. (c) The residual seat's C1 line and `5b8025a8` at one revision

The lane's own recorded C1 line is at `.ufo/waves/round-22/attempt2/residual/ResClaims.md:24`:
`f8f0b4a         assertions=63 resolved=61 skipped=39 mismatches=2   rc=1`, and the paired
`tool@c9f1fe3 x decl@f8f0b4a` form is in `residual/evidence/ResDeclaredEvidence-counts-matrix.txt`
(rows `tool@c9f1fe3 decl@f8f0b4a` is not in the matrix, but `tool@c9f1fe3 decl@8680755` and all
intermediate revs are; the C1 after-run was executed at `f8f0b4a` = the rev named in ResClaims.md:24).

Both `c9f1fe3` and `f8f0b4a` carry the SAME gate-check blob `f26aa728` = sha256 `5b8025a8…`
(E2). So a reader at `c9f1fe3` (or `f8f0b4a`, or `8680755`) sees both the tool bytes whose
sha256 is the report's `5b8025a8` AND the residual C1 line. The two statements are consistent:
they name different instruments (gate-check vs declared-evidence) but the digest in the report is
exactly the sha256 of the tool bytes used for the C2 after-run the report describes.

### E6. The "before" state has no receipt

Every recorded `fail=10` before-state is prose:
- LOG.md:1511-1512 "Gate counter tools/souji-gate-check.py: before entries=2 ok=0 slice_verdicts=0/8 fail=10 exit1; after entries=2 ok=2 slice_verdicts=8/8 fail=0 exit0; selftest 9/9."
- corpus/lessons/round-22.md:375 "Before (entries absent): `entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=10`, exit 1."
- fleet report `.ufo/reports/round-22/souji.md:71-72` "Before: `entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=10`, exit 1. After: `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, exit 0."

No file in `census/` records a before-run command, rc, stdout, or tool digest. `census/round-22/attempt2/` contains only `declared-evidence-before.tsv`, `declared-evidence-before-final.tsv`, `instrument-digests.txt`, `quarantine-slice`, `slice-verdicts.tsv`, `sources/` — none is a gate-check run receipt.

## Findings

1. **The D3 "tool blob f26aa728 vs report digest 5b8025a8" mismatch is a false dichotomy** —
   `f26aa728` is the git blob sha1 and `5b8025a8…` is the sha256 of the SAME bytes (true at
   `af73b8b`..`8680755`, E2/E4). The spot-check's D3 premise conflates two digest namespaces.
   The after-run WAS measured with the exact tool the report cites. Location: corpus/lessons/round-22-verifier-spotcheck.md:142; compare ResGateCheck.md:35 and Sentinel.md:555.

2. **The report's `5b8025a8` digest is accurate for the measured run but stale at the named tip**
   — the report (fleet `.ufo/reports/round-22/souji.md:64-65,172`) names measured revision
   `77d6595`, where the tool is `63ac63b8`/`d5ed0805…`. The digest is true at `8680755` and
   below, not at `77d6595`. So D3's residual truth is a STALE digest in the report, not a wrong
   digest. Location: fleet report lines 64-65 and 172; E2.

3. **The committed `instrument-digests.txt` is bound to the tip and is NOT stale** — committed at
   `dd8a6b7` (after 9fcc4f7), it records `d5ed0805…`, matching `9fcc4f7`..`1208bfb` and the
   worktree. The round's own digest file was already corrected; only the fleet report kept the
   old digest. Location: census/round-22/attempt2/instrument-digests.txt:2; git log for the file.

4. **No "before" receipt exists in any form** — the `fail=10` state exists only as prose in
   LOG.md, the lesson, and the report (E6). This half of D3 stands un-repaired.

5. **`f2d18e82…` is a transient dirty-worktree sha256** — recorded by CritC2Counter.md:37 while
   HEAD was `d6a75ba` and four paths were modified; it corresponds to no committed revision and
   is not a digest of any committed tool. Location: .ufo/waves/round-22/attempt2/w1/CritC2Counter.md:37.

6. **The 9fcc4f7 hardening is a 2-line regex change** (E2) — the same arguments, entries, and
   verdicts were re-derivable under both tool versions; the C2 outcome (2/2 ok, 8/8) is
   recorded only under the pre-hardening tool (ResGateCheck.md:65-73), never re-run under
   `63ac63b8` in committed bytes.

7. **The gate-check tool digest history is fully monotone**: `d85c2696` (a211e4d..d6a75ba) ->
   `5b8025a8` (af73b8b..8680755) -> `d5ed0805` (9fcc4f7..1208bfb), with exactly three sha256
   values over the whole r22 lifespan. No digest in the census is unbound; two are stale
   relative to the revision they are quoted against (the report's `5b8025a8` vs `77d6595`; and
   all pre-af73b8b `d85c2696` citations vs the revs where they appear, which are all correct).

## Attack log

- ATTACK 1: D3's premise ("after run measured with tool blob f26aa728 while the report cited
  5b8025a8…") is internally inconsistent — f26aa728 and 5b8025a8 are one content in two
  encodings (E2/E4). The spot-check's D3 as written cannot be closed by changing the report's
  digest to d5ed0805; the report's digest was true for the run it describes. The only honest
  closure re-runs the counter under the tip tool (63ac63b8) and commits both before and after
  receipts, as the r23 plan already does.
- ATTACK 2: the report's stale digest is a fleet-root file (`.ufo/reports/round-22/souji.md`),
  outside the lane's write scope; the lane can only correct its own records (SCORECARD,
  instrument-digests.txt) and note the fleet-side staleness.
- ATTACK 3: "no before receipt existed" is TRUE, and remains true after this reconstruction; the
  r23 C2 after-target of >=4 receipts includes a gate-check before receipt that still does not
  exist anywhere.

## Sources

- `git` objects at `/home/vgpnk/Projects/shokunin/souji-shokunin` (read-only commands only).
- corpus/lessons/round-22-verifier-spotcheck.md:113,142 (verbatim quote above).
- .ufo/waves/round-22/attempt2/residual/ResClaims.md:24; ResGateCheck.md:35,45,65-73;
  ResDeclaredEvidence-counts-matrix.txt; counter.txt:6,14; attacks.txt:3.
- .ufo/waves/round-22/attempt2/w1/evidence/Sentinel.md:216,483,555;
  w1/CritC2Counter.md:29,37; w1/evidence/RevGate.md:12-19; w1/MutQuote.md:10.
- census/round-22/attempt2/instrument-digests.txt:1-3; LOG.md:1511-1513;
  corpus/lessons/round-22.md:375; fleet .ufo/reports/round-22/souji.md:64-65,71-72,172.
