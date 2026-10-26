# r32 C2 T08: why changing tools/souji-evidence-cache.py turned two registered gates red

Seat SwarmRevenger33, 2026-10-26. Read-only over the lane; all execution inside
`/fast/scratch/hyaku/souji-r33/RevengeT08Revert/` (clone `c`, `TMPDIR` …/tmp), removed at the end.

Measured revision for every line pointer and every run below:
`2d9bca55a9f042a2c9ed60a797a8069e74c41f46` (the r33 preregistration commit). The six files that matter are
byte-identical at base `6017a482e7068d5afb7617640198fbb0fe743357` and at `2d9bca55`
(`git diff --stat 6017a48 2d9bca55 -- <paths>` prints nothing).

## 1. The invariant that was broken

The committed tool `tools/souji-evidence-cache.py` is **byte-pinned by historical evidence**: two registered gates
require the live worktree copy of that file to hash to `dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6`
(blob `82de0e07`, 75817 bytes), the digest r21/r22 recorded when they measured it.

| revision | blob | sha256 of the file | gates |
|---|---|---|---|
| `6017a48` base | `82de0e07239724ab4f6ac55da46f4e00ae22723f` | `dd279ba9…39d6` | green |
| `7a6667c` (r32 controls) | `82de0e07…` | `dd279ba9…39d6` | green |
| `98e5203` (r32 C2 landing) | `1578e419f5b6263480ef29de2643e9b4370768f6` | `6b826da2b65f9901f40b967fa296a164ef2bd0813aa474c0e8a5e760f65e7297` | **red** |
| `9da5e9a` (r32 attempt-2 revert) | `82de0e07…` | `dd279ba9…39d6` | green |
| `2d9bca55` (r33 prereg) | `82de0e07…` | `dd279ba9…39d6` | green |

The r32 landing changed 11 lines: the module docstring (`tools/souji-evidence-cache.py:33` base,
"isolated fixtures under `/var/tmp`"), `_selftest()`'s `mkdtemp(..., dir="/var/tmp")` at `:1295`, and the child
`env` literal `"TMPDIR": "/var/tmp"` at `:1311` (replaced by a conditional pass-through). Only the scratch root
moved; the CLI's verdict surface did not.

## 2. The exact mechanism (pin chain, top to bottom)

1. **Producer of the pinned digest.** `census/round-14/cache-demonstration.py:229`
   `state["sha256"] = sha256_file(path)` — the demo hashes the gate file it was handed
   (`--gate <ROOT>/tools/souji-evidence-cache.py`, wired at `census/round-21/run-acceptance.py:338`) and prints it
   in its JSON as `gate.sha256`. Its own `gate_digest_recorded_and_unchanged` check (`:934`) only asserts the file
   did not change *during that run*; it never compares to a historical value.
2. **The frozen payload.** `census/round-21/final-out-S1.json` is the r21 acceptance receipt (revision
   `ff425ab835614f38205426330b9cdb93fd267045`). Its 13th of 18 records, `clean-cache-demonstration`, holds:
   `"name"` at `:2515`, the raw `stdout` at `:3383` (its `stdout_sha256` at `:3384`), and inside that stdout the
   gate object — `sha256` at `:3155`, `matches_installed_default` at `:3160`, `sha256_after` at `:3165`,
   `gate_sha256_after` at `:3169`; the record's per-command input digest map is at `:3242`. All of them read
   `dd279ba9…39d6`.
3. **The oracle fixture.** `tests/fixtures/r22-result-oracle.json:3` names that receipt, `:4` pins its bytes
   (`source_receipt_sha256 = bc53a752…38fe`), `:5-6` pin `census/round-21/step-inventory.json`
   (`8b7b1cd8…1310`), `:7` pins the measured revision. `tests/fixtures/r22-result-oracle.py:31-35` recomputes both
   digests on every run and refuses with `R22-ORACLE-INPUT-TAMPERED` on any drift. The freeze is over the receipt's
   *bytes*, and those bytes carry the tool's digest.
4. **The consumer line that compares live bytes to the pin.** `tests/fixtures/r22-result-oracle.py:87-91` calls
   `census/round-21/run-acceptance.py`'s `summarize_result(step, rc, stdout, stderr, oracle['revision'], ROOT)`
   with `ROOT = Path(__file__).resolve().parents[2]` (the live lane, `:17`) and the pinned stdout (`:68`). Inside:
   - `:503` `gate_sha = sha256_bytes(read_regular(root / "tools" / "souji-evidence-cache.py"))`
     — reads the **live worktree file** (regular, non-symlink: `read_regular`, `:217-220`), whole bytes;
   - `:522` `and isinstance(gate, dict) and gate.get("sha256") == gate_sha`
     — requires the payload's recorded digest to equal the live file's digest;
   - `:536` `matched = matched and demo_match and not stderr` — one false conjunct fails the vector.
   `positive/clean-cache-demonstration` and `positive/cache-transient-path-and-time` both `want: true`
   (`r22-result-oracle.py:97-100`), so a byte change anywhere in the tool flips both.
5. **The second gate.** `census/round-22/mutation-adequacy.py:28` grades the same oracle in memory.
   `:266` grades the pristine runner, `:269-274` grades 59 literal mutants of `run-acceptance.py` and records
   `killing_vectors`, `:276` `ok = code == 0 and pristine['fail'] == 0 and all(r['agrees'] for r in rows)`.
   Three mutants anchor on the comparison text itself (`:100`, `:121`, `:190`), so the consumer's pin cannot be
   removed without the mutant anchors disappearing (see §5).
6. **Nothing else pins it.** `git grep -l "souji-evidence-cache.py" 2d9bca55 -- tests/fixtures census` = 85 files;
   the ones that read the tool *at gate time* are the three above. `tests/fixtures/r14-evidence-cache.py`
   (G3) only invokes the tool as a CLI and asserts exits/finding ids — measured green on the r32 bytes (§4).
   `tests/fixtures/r20-input-binding.py` stubs `run_demonstration` (`:575`, `:682` paths) so it never hashes the
   gate. `tools/souji-landing-gate.py` contains no reference to this tool or to r22.
   The many `census/round-1x|2x|32` records that quote `dd279ba9…` are history, not consumers; only
   `census/round-21/final-out-S1.json` is read by a gate.

## 3. The red state, reproduced

Clone at `2d9bca55`, then
`git -C <lane> diff 7a6667c 98e5203 -- tools/souji-evidence-cache.py | git -C c apply` →
worktree tool sha256 `6b826da2…e7297` (byte-identical to the r32 landing blob), otherwise clean.

```
python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py
rc=1  total 258  pass 256  fail 2  finding R22-RESULT-CONTRACT
FAIL positive/clean-cache-demonstration        expected True observed False
FAIL positive/cache-transient-path-and-time    expected True observed False

python3 -B census/round-22/mutation-adequacy.py
rc=1  pristine {'exit': 1, 'pass': 256, 'fail': 2}
      summary {'mutants': 59, 'killed': 59, 'survived': 0,
               'disagreeing_with_expect': ['nonexact-keyin-get', 'failed-checks-to-eq',
                 'names-len-constant', 'phases-len-constant', 'baseline-guard-pass',
                 'checks-len-drop', 'caserows-len-drop']}
```

Same commands on the same clone before the patch (base bytes): G1 `rc=0 total 258 pass 258 fail 0`; G2 `rc=0
pristine {'exit': 0, 'pass': 258, 'fail': 0} summary {'mutants': 59, 'killed': 52, 'survived': 7,
'disagreeing_with_expect': []}`. The 7 "equivalent" mutants survive at base and are falsely killed at the r32
bytes: the two broken positive vectors fail for every mutant, so `killing_vectors` no longer discriminates.

Guard-rule note (for `census/round-33/c2-legs.tsv:13-20`): G1's **last digit-bearing line is identical in both
states** (`"total": 258`); only its exit code (0 → 1) separates green from red. G2 differs in both (`rc 0→1`,
`"survived": 7 → 0`). A comparator that looked only at G1's last line would read red as green.

## 4. Isolation experiments (each one run, not inferred)

| # | change in the clone (nothing else) | result |
|---|---|---|
| a | restore base tool bytes (`git checkout --`) | G1 rc0 258/258, G2 rc0 pristine fail 0, 52/7 — the **revert is green** |
| b | r32 bytes, then **one-word docstring edit only** (`under`→`beneath`, sha `d5a516b6…`) | G1 rc1, same two vectors fail, `R22-RESULT-CONTRACT` — the pin is over **bytes**, not behaviour |
| c | r32 bytes; in memory only, replace `payload["gate"]["sha256"]` with the live sha and re-grade the pinned stdout (`summarize_result`) | `as-pinned matched = False`; `replaced -> matched = True`, all other 33 checks and the 4 cases already matched — the **only** failing conjunct is `:522` |
| d | r32 bytes; `tests/fixtures/r14-evidence-cache.py` (G3) | rc0, `fixture: 22/22 checks passed` — G3 has no byte pin |

So the r32 harm is exactly one conjunct over one file's bytes, and it is not a behaviour change.

## 5. Legitimate repair paths under Q73

Q73 (`corpus/QUALITY.md:178`): a digest pin of a live tool inside historical evidence "is either regenerated with
its own committed script at the candidate, or the tool edit is reverted"; historical evidence is never rewritten by
hand; and every registered gate must be green at the candidate where it was green at base.

| path | Q73 status | evidence |
|---|---|---|
| **P1 revert the tool edit** | legitimate, named by Q73 | run (a) above: G1 258/258, G2 52/7; this is what `9da5e9a` did (blob back to `82de0e07`, sha `dd279ba9…`), and its own receipt states the cause: `census/round-32/records/a2-repairs.txt:30-38` ("compares the live tool's sha256 with the frozen cache-demo payload"). |
| **P2 regenerate the pin with its own committed script at the candidate** | **unavailable for this pin** | sweep: no script writes `tests/fixtures/r22-result-oracle.json` — `git grep -n "r22-result-oracle.json" 2d9bca55 -- '*.py' '*.sh'` returns one line, `census/round-22/mutation-adequacy.py:12`, a `--oracle FILE` *input* option. The only committed regenerator in the tree is `tests/fixtures/r15-preservation-frozen/regenerate.py` (docstring `:2`: "Regenerate the r15-preservation-frozen record from real runs (round 16, R4)."), which re-pins `tools/souji-census.sh`, a different tool. `census/round-21/run-acceptance.py` (`--output`) only *creates a new exclusive* receipt for a `--rev` it replays (`output_path` refuses an existing file) and its receipt bytes are themselves pinned by the oracle (`r22-result-oracle.py:31-35`), so re-running r21 cannot re-pin the existing receipt without also rewriting the oracle and its 258 expected decisions. That is hand-rewriting, not regeneration. |
| **P3 hand-edit the pinned stdout / gate sha** | forbidden by Q73; also self-detecting *only* if half-done | editing `final-out-S1.json` alone trips `R22-ORACLE-INPUT-TAMPERED` (rc 2) at `r22-result-oracle.py:34-35`. Editing receipt **and** the oracle's `source_receipt_sha256` (and the three case `stdout` strings that carry the same digest, oracle `:4955,:4962,:4969`) makes both gates green — see §6, Attack. |
| **P4 weaken the consumer (drop `run-acceptance.py:522`)** | blocked structurally | with `:522` reduced to `and isinstance(gate, dict)`, G2 prints `r22-mutation-adequacy: could-not-evaluate: anchor count 0: 'and isinstance(gate, dict) and gate.get'` and exits **2** (`mutation-adequacy.py:261-265`), because the killed/equivalent mutants anchor on that exact text. |

Consequence inside Q73's own text: for this pin P2 does not exist at the prereg commit, so **P1 is the only
Q73-clean repair**.

## 6. Attack log — ATTACK-T08-PIN-MOVABLE (reproduced; no amendment proposed)

The pin is movable without touching the tool, and nothing at gate time detects the move. Reproduced in the scratch
clone with the r32 tool bytes (`6b826da2…`) still in place:

1. rewrite the digest inside the one `clean-cache-demonstration` record of `census/round-21/final-out-S1.json`
   (`dd279ba9…` → `6b826da2…`): new receipt sha256 `dc13b8d938ac0d08…`;
2. set `tests/fixtures/r22-result-oracle.json`'s `source_receipt_sha256` to that;
3. replace the same digest in the three oracle case `stdout` fields (`:4955,:4962,:4969`) that fabricate
   missing-key payloads.

Result: G1 `rc=0 total 258 pass 258 fail 0 finding None`; G2 `rc=0 pristine {exit 0, pass 258, fail 0}
summary {mutants 59, killed 52, survived 7, disagreeing []}` — identical readings to base, with the tool's bytes
changed. The only trace is the receipt field `oracle_sha256` (`750946f4…` vs the committed `970b7362…`), and nothing
compares that field to a committed value: `git grep 970b7362 2d9bca55` hits only round-22 receipts that *print* it,
one round-22 lesson, and the r26 assimilation `manifest.sha256` of an exported snapshot — no gate, no pin.
Q73 forbids this in words; it is not mechanically detected. Reported, not repaired (frozen predicate untouched).

## 7. Consequence for this round's C2 (feasibility risk, reported not amended)

`census/round-33/c2-legs.tsv` makes O1 `python3 -B tools/souji-evidence-cache.py --selftest` under a read-only
`/tmp,/var/tmp,/dev/shm`, and G1/G2 (`:29-30`) no-harm guards: a guard must print the base run's exit code and last
digit-bearing line, and a FAIL is `harm`. Repairing O1 (scratch root from `TMPDIR`, Q71) *necessarily* changes the
tool's bytes — that is the whole repair — so G1 and G2 cannot stay green while O1 passes unless the r22 pin is
regenerated by a committed script for that pin, and §5-P2 shows no such script exists at the prereg commit.
The reproduced states are: O1 repair + base pin → G1 rc1/2 vectors, G2 rc1/7 disagreements; revert → both green,
O1 back to its base FAIL. [INFERENCE] A regenerator written *this* round would not be "its own committed script";
the L1 owns that reading and any stricter-only handling.

Also measurable from the same runs: the guard rule's last-line discriminator is inert for G1 (§3), so the L1's
reading of `pass=5 fail=0 harm=0` should key on exit codes, which do differ.

## 8. Confidence

- Mechanism, red state, revert state, docstring sensitivity, single-conjunct isolation, G3 no-pin, G2 anchor
  refusal, pin-movability: **measured in this run**, high confidence.
- r32 intent (whether the C2 executor knew about the pin): no committed evidence either way; the r32 receipt
  `a2-repairs.txt:30-38` records the discovery after the fact. **Not asserted.**
- The Q73 reading that a r33-authored regenerator would not qualify: **[INFERENCE]**, flagged for the L1.

## 9. Receipts (commands as run; cwd = scratch clone `c` unless stated)

```
mkdir -p /fast/scratch/hyaku/souji-r33/RevengeT08Revert/tmp
git clone -q --no-local <lane> /fast/scratch/hyaku/souji-r33/RevengeT08Revert/c && git -C c remote remove origin
git -C c rev-parse --show-toplevel   -> /fast/scratch/hyaku/souji-r33/RevengeT08Revert/c
git -C c checkout -q 2d9bca55a9f042a2c9ed60a797a8069e74c41f46
git -C <lane> diff 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1 98e5203d45b4e419a9e72801733d93303acc7ebd -- tools/souji-evidence-cache.py | git -C c apply
python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py   # §3, §4
python3 -B census/round-22/mutation-adequacy.py                                            # §3, §4
python3 -B - <<'PY'  … summarize_result on the pinned stdout, in-memory gate.sha256 swap   # §4c
python3 -B - <<'PY'  … receipt+oracle forgery, gates re-run                                 # §6
```

Scratch removed after these runs. No lane file, index or jj state was written; every `git -C <lane>` call in this
seat was `log/show/diff/rev-parse/grep/ls-tree/cat-file/status`.
