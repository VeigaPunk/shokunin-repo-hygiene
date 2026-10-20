# GateReplayFrozen — D6: freeze the r16 gate replays

STATUS: DONE — runner + frozen expected verdicts landed; all 5 replays
reproduce under the committed `5fa6017` gate and the current WORKTREE gate;
expected agrees with prose on every count including the disputed 29.

OWN ONLY files written:

- `census/round-17/gate-replays.py` (new, 13972 bytes)
- `census/round-17/gate-replays-expected.json` (new, 5311 bytes)

## Observed replay table (gate `e7d2439d97ef…` = `5fa6017:tools/souji-landing-gate.py`, == WORKTREE bytes at run time)

| name | rev | round | exit | findings | checked (reg/pins/markers/reports) | match |
|---|---|---|---|---|---|---|
| r15-landing | `b410186` → `b410186cea…` | 15 | 1 | 5 | 18/16/1/64 | True |
| r13-admitted | `a31642d` → `a31642d14…` | 13 | 0 | 0 | 10/7/0/32 | True |
| r14-landing | `cc21683` → `cc21683257…` | 14 | 0 | 0 | 15/9/0/32 | True |
| r16-landing | `6ff91f5` → `6ff91f534e…` | 16 | 0 | 0 | 21/16/30/141 | True |
| r16-precarry | `79bbe7a` → `79bbe7a621…` | 16 | 1 | 29 | 21/16/30/141 | True |

Gate `--selftest` on the extracted `5fa6017` bytes: `SELFTEST pass=18 fail=0`, rc 0.

## vs the prose claims (recorded, not fitted)

- `b410186` → 5 findings with ids LG-PARSE-REG (`tools/souji-census.sh`),
  LG-FROZEN-PIN + **2× LG-FROZEN-MEASURED** (same path
  `tests/fixtures/r15-preservation-frozen/expected.json`, distinguished only
  in `detail`), LG-SEAT-UNCARRIED (`.ufo/waves/round-15/w1/ConfigRepair.md`).
  The (id, path) multiset preserves the 2× multiplicity; agrees with prose.
- `a31642d`/`cc21683`/`6ff91f5` → exit 0, 0 findings; agrees. r16-landing
  summary (21/16/30/141) is byte-identical to committed
  `census/round-16/gate-landing.json`.
- `79bbe7a` → exit 1, **29** LG-SEAT-UNCARRIED (one per w2 report file);
  agrees with the closure's re-derivation (30 markers, 29 uncarried).
  `LOG.md:902` says "28" — observed is 29, so the LOG figure is wrong
  (already routed as D3 by the r16 closure).
- Every observed set agreed with prose; nothing was fitted. If a future
  run diverges, the runner prints `missing:`/`extra:` (id, path) rows and
  exits 1.

## Runner semantics

- `--gate-rev` (default `WORKTREE`) selects gate bytes:
  `git show <rev>:tools/souji-landing-gate.py`, sha256 recorded;
  `WORKTREE` reads the file. Replay revs resolved via `rev-parse --verify`.
- Each replay runs `<gate> --root LANE --rev R --round N --json <tmp>`;
  the output record holds resolved rev, process rc, payload exit, error,
  sorted (id, path) multiset, summary counts, stdout lines, stderr tail.
- Compare mode: exit 0 all match, 1 divergence, 2 usage/IO error.
  `--output` refuses overwrite (verified: rc 2).
- `--write-expected PATH` re-derives the frozen file (refuses overwrite);
  that is how the committed expected was produced, under `--gate-rev 5fa6017`.
- `--selftest` appends the gate's own selftest result to the record.
- `--scratch DIR` relocates the runner's own temp dir (default `/var/tmp`);
  the gate's internal `bash -n` snapshot and selftest repos hardcode
  `/var/tmp` in the gate itself.
- No `--base` on any replay: the originals omitted it, so LG-PARSE-CHANGED
  stays out of scope (disclosed in r16 `RerunGateReplayR15.md:74`).

## Residual risk

- Expected compares exit + (id, path) multiset only; `detail` strings carry
  a per-run `/var/tmp` snapdir token (r16 finding, unfixed) so they are
  recorded in the run record but not frozen.
- `gate_sha256` is recorded per run and `expected.gate_sha256_match`
  reported; a gate that changes verdicts will fail comparison as intended.

## Commands run

```sh
python3 -m py_compile census/round-17/gate-replays.py   # OK
git -C <lane> show 5fa6017:tools/souji-landing-gate.py  # read-only (header, evaluate, emit, carry, main)
git -C <lane> show -s --format='%h %s' <revs>; git status --porcelain; git diff HEAD -- tools/souji-landing-gate.py  # read-only
python3 census/round-17/gate-replays.py --gate-rev 5fa6017 --scratch /var/tmp/souji-r17-GateReplayFrozen/scratch --selftest --write-expected /var/tmp/souji-r17-GateReplayFrozen/gate-replays-expected.json   # RC=0
python3 census/round-17/gate-replays.py --gate-rev 5fa6017 --scratch … --selftest --output /var/tmp/souji-r17-GateReplayFrozen/run-5fa6017.json   # RC=0, match=True, selftest 18/0
python3 census/round-17/gate-replays.py --gate-rev WORKTREE --scratch … --output /var/tmp/souji-r17-GateReplayFrozen/run-worktree.json   # RC=0, match=True
python3 census/round-17/gate-replays.py --gate-rev 5fa6017 --scratch … --output <existing>   # RC=2, refused overwrite
```

Probe disclosure: gate invocations themselves write `/var/tmp` snapshots
(`souji-landing-gate-*`, selftest repos) outside my scratch dir — hardcoded
in the gate, allowed by the ticket's own exec command. Runner scratch and
all `--json` files were under `/var/tmp/souji-r17-GateReplayFrozen/`;
directory deleted after the runs (per-run `run-*.json` contents are
summarized in the table above). The `.pyc` from `py_compile` under
`census/round-17/__pycache__/` was removed.

Tool installs/updates: none.
