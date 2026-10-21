STATUS: DONE — no committed round-18 gate receipt binds 8be6523; the retained final receipt binds 74f9adb.

# Findings

Axis: calibration 7 (lowest non-retired). Round-19 preregistration identifies D1 as receipt binding (`.ufo/waves/round-19/preregistration.txt:66-70`).

- **No r18 receipt for 8be6523.** The final r18 gate command explicitly measured `74f9adb489fcf1393bbd479425acf5545ded9908` against base `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` and wrote `census/round-18/gate-pointers-after-final.json` (`corpus/lessons/round-18.md:73`). Its committed JSON says `resolved_rev=74f9…`, `resolved_base=b576…`, `exit=0`, `findings=[]`, `error=null`, and records the full summary (`census/round-18/gate-pointers-after-final.json:2-4,25-40`). The other committed gate-pointer receipts bind `5efb519…` (`census/round-18/gate-pointers-after-5efb519.json:25-39`) and `b576341…` (`census/round-18/gate-pointers-before-finalgrammar-b576341.json:81-95`), not 8be. A targeted search of `census/round-18/` found no `8be6523` occurrence.
- The closure's `after=8be6523` is review/landing identity, not a gate measurement: it says it did not execute the gate (`corpus/lessons/round-18-verifier-spotcheck.md:22-24,74`) and its measured after receipt is `74f9adb…` (`:78-79`). The identical gate-source digest at 4800fd7, 74f9adb and 8be6523 (`:81`) proves code identity only, not an execution against the 8be tree. I also measured the source digest: r18's gate at 8be is `f0f7bf2f836b52eebe2d58b1ee1fc2b6bd74096083cd736fdc2fecc7dfae67df`; current r19 worktree gate is `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd`. Do not use the current r19 executable while describing the result as an r18-gate recheck.
- **Receipt shape and location.** Save the gate's unaltered `--json` result at `census/round-19/gate-pointers-recheck-8be6523.json`. The generated JSON includes `exit`, `findings`, `summary`, `resolved_rev`, `resolved_base`, `error`, and (for round 18+) `fleet`; the summary includes pointer counts `checked_ptrs`, `ptr_exempt`, and `ptr_fleet` (`tools/souji-landing-gate.py:38-42,1147-1197`). A successful clean receipt must show the full `resolved_rev` equal to 8be65236a4b61fffe9c0d05d30043650848c0a60, the intended full base, `exit=0`, empty `findings`, `error=null`, and the complete summary/fleet classification. The JSON does not carry argv or executable digest; record the exact command and gate digest alongside its pointer in the round report. `--json` refuses an existing output, so use a fresh filename (`tools/souji-landing-gate.py:1168-1197`).

Recommended invocation, from the lane root, using the exact r18 gate copied from 8be6523 (verify its SHA-256 is the `f0f7…` digest above):

```sh
python3 /var/tmp/souji-r19-ScoutD1Receipt/landing-gate-8be6523.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 8be65236a4b61fffe9c0d05d30043650848c0a60 \
  --base b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 \
  --round 18 \
  --fleet-root /home/vgpnk/Projects/shokunin \
  --json census/round-19/gate-pointers-recheck-8be6523.json
```

The named script must first be materialized from `git show 8be6523:tools/souji-landing-gate.py`; this invocation is a prescription, **not run evidence**. If 8be6523 cannot be re-measured, keep the 74f9adb result labeled only for 74f9adb, state that the 8be6523 gate result is unavailable/unverified, and withdraw or narrow the recheck claim. Do not copy the old JSON, edit `resolved_rev`, or infer a recheck from an unchanged gate digest.

# Evidence

- `corpus/lessons/round-18.md:73` — exact final r18 gate invocation and output path.
- `census/round-18/gate-pointers-after-final.json:2-4,25-40` — observed final receipt and its actual bound revision.
- `census/round-18/gate-pointers-after-5efb519.json:25-39`; `census/round-18/gate-pointers-before-finalgrammar-b576341.json:81-95` — other committed revision bindings.
- `corpus/lessons/round-18-verifier-spotcheck.md:22-24,74,78-81` — closure review tip, non-execution disclosure, measured receipt revision, and gate-source digest comparison.
- `tools/souji-landing-gate.py:38-42,1147-1197` — JSON and revision-binding output contract.

# Commands run

- Targeted source searches for `8be6523`, gate receipts, and D1 across `census/round-18/`, r18 lessons/closure, and the r19 preregistration; no exact `8be6523` hit in `census/round-18/`.
- Read-only `git show 8be6523:<receipt> | jq …` for the committed final, intermediate, and baseline gate-pointer JSON files; observed resolved revisions 74f9adb, 5efb519, and b576341 respectively.
- `git show 8be6523:tools/souji-landing-gate.py | sha256sum` and `sha256sum tools/souji-landing-gate.py`; observed r18 and current r19 digests above.
- No gate invocation, build, or test was run. No LSP device/server is exposed in this session; searches were used for literal discovery only, and conclusions are based on direct source and committed JSON reads.

# Contract compliance

- Wrote only this assigned report; no subagents, repository mutations, tool installs, network access, live census, or scratch files. No gate check is represented as executed.
