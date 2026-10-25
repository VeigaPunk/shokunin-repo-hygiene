# CritC2Value — falsifying C2 (blob-bound receipts)

## Status

STATUS: FAIL — the claim's own kill rule fires under an executed counterexample against the
shipped runner: `verify` exits 0 on a receipt whose `tool_sha256` is **not** the committed blob
at the named revision. The mechanism is real and one env var from correct; the frozen counter is
also satisfiable without the runner existing. Both are named, repairable limits — not a tradeoff
the canonical judge must reject.

Verdict on the claim: **capability-with-named-limit**. Strongest single argument against it:
`tools/souji-receipt-run.py:83` reads the tool digest from the source repo while
`tools/souji-receipt-run.py:117-122` executes from a clone that need not carry the same object
substitutions, so the bytes hashed and the bytes run are two different object stores; `verify`
agrees with the receipt and the claim's kill rule is met.

## Evidence

Lane revision: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (`refs/heads/master`). Runner under
review: `tools/souji-receipt-run.py`, untracked, 218 lines, sha256 `8ba2761368ab8cf9…`.

**E1 — kill rule, end-to-end through the shipped tool.** Scratch repo at `/var/tmp`, one commit,
one `refs/replace` ref substituting the tool blob; then the real runner:

```
$ python3 tools/souji-receipt-run.py run --root /var/tmp/…/r --rev 1d479fc460cc9419bbaadd73a575d9db13ebd026 \
    --tool counter.py --out /var/tmp/…/r.receipt -- python3 counter.py
receipt=/var/tmp/…/r.receipt rev=1d479fc4… tool_sha256=0bf5569376f04986c3864566fa6f538cc57df2d32d0ec47d2e0763915e063159 rc=0 counts=assertions=1 …
run-exit=0
$ python3 tools/souji-receipt-run.py verify --root /var/tmp/…/r /var/tmp/…/r.receipt
verify=ok rev=1d479fc4… tool=counter.py tool_sha256=0bf55693…
verify-exit=0
$ GIT_NO_REPLACE_OBJECTS=1 git -C /var/tmp/…/r cat-file blob 1d479fc4…:counter.py | sha256sum
68ed0f536c6452e2cfacaa314ed2ca43574f633734453caa3291ee3d264bf7e2
```

Recorded digest `0bf55693…`, true committed blob `68ed0f53…`, `verify` exit 0. The recorded
stdout (`assertions=1 …`) came from the *real* tool, so the receipt mis-binds both digest and
output. `tools/souji-rev-pin.py:56-60` already sets `GIT_NO_REPLACE_OBJECTS`/`GIT_NO_LAZY_FETCH`;
the new runner's `git()` (lines 62-67) strips only `GIT_DIR`/`GIT_WORK_TREE`.

**E2 — verify does not prove execution.** A hand-written receipt (no `run`, no execution at all)
with the true tip digest verifies clean:

```
$ python3 tools/souji-receipt-run.py verify --root <lane> /var/tmp/…/handwritten.receipt
verify=ok rev=1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd tool=tools/souji-gate-check.py tool_sha256=d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d
exit=0
```

`verify` (lines 169-196) checks header order, digest agreement and `COUNTS_RE` presence only.

**E3 — verify ignores `rc`.** Same receipt with `rc=1` (a failed run) still verifies:
`verify=ok … exit=0`, receipt line `rc=1`. A claim's four receipts can all record failure.

**E4 — the required refusal demo does fire (fair credit).**

```
$ python3 tools/souji-receipt-run.py verify --root <lane> <receipt with tool_sha256=5b8025a8…>
RECEIPT-TOOL-DIGEST-MISMATCH	receipt 5b8025a83f16 != tree d5ed0805b10f at 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd
exit=2
```

**E5 — the frozen counter measures a text shape, not a binding.** In a fabricated tree with no
`tools/` directory at all, four files containing one identical meaningless digest:

```
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l
4
$ ls tools
ls: cannot access 'tools': No such file or directory
```

Adding a prose `.md` of the same shape raises it to 5; a real receipt with a trailing space/CRLF
is not counted at all. Live lane counter today: `0`.

**E6 — the runner refuses the write the counter requires.**

```
$ python3 tools/souji-receipt-run.py run --root <lane> --rev <tip> --tool tools/souji-gate-check.py \
    --out <lane>/census/round-23/records/x.receipt -- python3 tools/souji-gate-check.py
OUT-IN-REPO	the receipt must not be written inside the measured repo
exit=2
```

**E7 — the clone materializes operator-sweep contents.** Replicating the runner's exact clone and
checkout (lines 117-122) on a repo holding `census/operator-sweep-20261019/results/sweep.out`:

```
$ find <clone>/census/operator-sweep-20261019 -type f -printf '%P\n'
results/sweep.out
$ cat <clone>/census/operator-sweep-20261019/results/sweep.out
SECRET-SWEEP-CONTENT
```

The lane rev tree tracks 15 `census/operator-sweep-*` blobs; `git archive --format=tar <base>`
unscoped yields 16 such members, `git archive … -- <paths>` yields none.

**E8 — no self-test, no oracle.** `python3 tools/souji-receipt-run.py --selftest` →
argparse usage error, exit 2 (only `run`/`verify` subcommands, lines 198-207). `grep -rln
"receipt-run" tests/ census/ SKILL.md corpus/` → no hits.

## Findings

1. **Kill rule fires (E1).** Digest source ≠ executed bytes. Location: `tools/souji-receipt-run.py:62-67`
   (`git()` env), `:83-89` (`blob_sha_bytes` over `--root`), `:117-122` (clone/checkout).
2. **`verify` proves digest agreement, not execution (E2).** Any author who can run
   `git cat-file blob <rev>:<tool> | sha256sum` and type one `COUNTS_RE`-shaped line produces a
   receipt that verifies 0. Location: `tools/souji-receipt-run.py:169-196`.
3. **`rc` is recorded but never enforced (E3).** Line 135 writes `rc=`; `cmd_verify` never reads it.
   Four receipts proving the counter *failed* satisfy the target.
4. **The frozen counter is a grep for a string the author types (E5).** `>= 4` is reachable with
   four hand-written files and no runner (E2 shows `verify` would even accept them). The counter's
   exit status never consults `verify`, so the "each verifiable with verify" clause of the claim is
   a reviewer obligation, not a measured property. Location: `.ufo/waves/round-23/preregistration.txt`
   C2 counter line + the `verify` line beneath it.
5. **The runner cannot produce the counted artifact (E6).** `census/` is inside `--root`, so
   `OUT-IN-REPO` refuses; the committed receipt is therefore an unbound copy of a `/var/tmp`
   original — the same out-of-band placement class as D3. Location: `tools/souji-receipt-run.py:105-108`.
6. **Bound exposure (E7).** The runner's clone+checkout materializes operator-sweep paths under
   `/var/tmp`, and the prereg's own unscoped `git archive <rev>` would too. Contradicts the lane
   bound "no operator-sweep contents read or staged" and the prereg's "never writes the lane tree,
   never fetches" framing (a `--no-local` clone copies the whole object store, not one tree).
   Location: preregistration.txt C2 kill-rule paragraph; `tools/souji-receipt-run.py:117-122`.
7. **Duplicate authority for Q37.** `durable_rev` (lines 74-80) reimplements
   `tools/souji-rev-pin.py:resolve_durable` instead of calling it, so the tested refusal set
   (`HEAD`, branch, short id, path escape, no measured paths — rev-pin's 11-case selftest) is not
   inherited. `corpus/QUALITY.md:91` names `tools/souji-rev-pin.py` as the Q37 mechanism.
8. **`verify` does not check durability.** Any 40-hex rev that still resolves is accepted, including
   a keep-only or otherwise non-durable commit — the exact Q37 class the claim says it closes.
   Location: `tools/souji-receipt-run.py:169-186`.
9. **Q40 has no control.** `corpus/QUALITY.md:99` requires caller-level dirty-helper/wrapper/
   frozen-input/added-input controls for a new producer; the runner ships with no `--selftest` and
   no fixture (E8), so it cannot be entered as a `gate` row in the registry at all.
10. **Q41 scope.** C2 claims to close D3, but D3's third clause ("replace the stale `5b8025a8…`
    digest in the report") edits filed r22 evidence; `corpus/QUALITY.md:100` requires an append-only
    named replacement index, not an edit. C2's receipt work does not cover it and should not claim it.

## Answers to the three assigned questions

**(1) Existing mechanism — yes, twice, so the delta is narrower than claimed.** `tools/souji-rev-pin.py`
is a *pre-write* gate (rev durability + working-tree byte equality, prints only the revision; it
writes no record). The *post-write* direction already exists: `census/round-21/run-acceptance.py:560-563`
derives bytes at a recorded commit and refuses on digest disagreement —

> `raise Refusal("historical agreement artifact does not match recorded digest: " + kind)`

— and `census/round-19/verify-agreement-pin.py:69-100` already stores `{path, sha256, measured_commit}`
per tool and refuses on mismatch. Genuine delta: a flat receipt carrying `cmd`/`rc`/`stdout`, and
rev→blob derivation *inside* the verifier rather than by a trusting caller. `census/round-22/attempt2/instrument-digests.txt`
is the D3 defect itself, not a mechanism — its own bytes say the revision is elsewhere:

> `round=22 attempt=2 date=2026-10-25 note=tool digests only; the measured revision is named in SCORECARD.md and the round report`

and `grep -rn "instrument-digests"` finds no code reading it. The gap is real; the new runner
partly duplicates r21/r19 rather than extending them.

**(2) Real capability measure or typed string?** A typed string (E5). A fake-green author writes
four `census/**` files with `tool_sha256=<64 hex>` plus one `COUNTS_RE` line, runs nothing (E2
confirms `verify` returns 0 on exactly that), and the counter reads 4. `verify` stops neither the
forgery nor a `rc=1` receipt, and the counter never calls it.

**(3) Quality rules.** Q4: the receipt is written outside `/tmp` and outside the repo, and scratch
is under `/var/tmp` with cleanup — Q4-clean in form, but the unscoped clone defeats the adjacent
bound (finding 6). Q37: `run` is correct, `verify` is not (finding 8), and the rule is re-implemented
(finding 7). Q40: unmet — no oracle, and the hashed bytes are not the run bytes (findings 1, 9).
Q41: no rewrite of filed evidence, but the D3 claim overreaches (finding 10).

## Impacted axes

- **calibration (7)** — a `verify=ok` on a mis-bound receipt is a record-agreement green on a false
  binding; this is the axis C2 is supposed to protect and, as written, the one it can harm.
- **operability (8)** — counter gameability (4) and the out-of-band copy (5) reduce the receipt to
  documentation unless the pairing is measured.
- **coverage (8)** — unaffected by the receipt work; the operator-sweep materialization (6) is a
  bound exposure, not coverage credit.

## Smallest safe correction (do not edit the frozen predicate)

1. Add rev-pin's env to the runner (`GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1`,
   `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_OPTIONAL_LOCKS=0`) **and** compute
   `tool_sha256` from the same tree that is executed (the clone), so digest and run bytes share one
   object store. Re-run E1; it must then exit 2.
2. Scope the measured tree by pathspec (`git archive <rev> -- <tool> <inputs>`, or a
   `--filter=blob:none --sparse` clone with scoped sparse-checkout) so `census/operator-sweep-*`
   never materializes.
3. Replace `durable_rev` with `resolve_durable(..., tree_check=False)` from `tools/souji-rev-pin.py`,
   in both `run` and `verify`.
4. `verify`: refuse `rc != 0` and a non-durable `rev`. Keep the frozen counter as written, but report
   beside it the per-receipt `verify` exit so the count and the binding are both visible.
5. Add `--selftest` plus a Q40 fixture (dirty-helper, substituted-blob, `rc=1`, forged-receipt,
   non-durable-rev cases) before any registry row is claimed.
6. Let the receipt be written into `census/` by the landing helper and record the copy in the same
   commit, so the counted file's provenance is bound rather than out of band.

## Attack log

- **A1 (decisive)** replace-object substitution, end-to-end through `run`+`verify`: exit 0 while the
  true committed blob differs (E1). Meets the claim's kill rule verbatim.
- **A2** hand-written receipt, zero execution: `verify=ok` (E2).
- **A3** `rc=1` receipt: `verify=ok` (E3).
- **A4** four fabricated `census/` files, no `tools/`: counter = 4 (E5); counter = 5 with a prose
  file; a CRLF receipt is not counted.
- **A5** `--out` inside the lane: `OUT-IN-REPO` (E6) — the runner cannot create the counted artifact.
- **A6** replicated clone/checkout: operator-sweep file readable under `/var/tmp` (E7).
- **A7** `--selftest`: argparse exit 2; no fixture references the tool (E8).
- **Not executed / inference:** whether the lane repo currently carries any `refs/replace` ref
  (not checked; E1 needs one to be present, and `git replace` is a write). The lane-bound exposure
  in finding 6 is [INFERENCE] from the replicated clone plus `git archive` member counts, not from a
  lane clone — I did not clone the lane.

Tooling: no installs or upgrades performed (no pacman transactions attempted). Scratch tree
`/var/tmp/souji-r23-CritC2Value/` removed; no lane file written except this report.
