# R41critic04 — attack on the frozen C3 counter (census/round-41/c3-counter.py)

Seat: R41critic04 (critic, leaf). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Lane tip scored: e2a74312af4233963e44e4dbb38838ece07b8bd2 (`git status --porcelain` = 0 lines before and after). No file under tests/, tools/, census/, corpus/, SKILL.md or any tracked file was written. Candidates live only in `.ufo/waves/round-41/w1/R41critic04/`. Scratch `/fast/scratch/hyaku/souji-r41/R41critic04/` was removed after scoring. No package or tool was installed.

## Verdict

**The frozen C3 counter is defeated by a fixture that never runs the tool.** Three sniffing candidates (they read the tool bytes or the mutant path, and never probe) each reach `killed=19 survived=0 misattributed=0` with `pristine=ok`, which is the C3 target. The counter cannot tell a probing fixture from a sniffing one. A candidate that merely checks exit codes is caught (19 survived), so the counter does catch blind probes. It does not catch fixtures whose verdicts depend on label text or the mutant file name.

Under the preregistration selection rule ("all-target first, then smaller bytes"), the smallest sniffing candidate (`sniff-path.py`, 1287 bytes) would win the C3 landing over any honest fixture of comparable size. That is the consequence the L1 must see.

## Frozen instruments (sha256 checked)

- `census/round-41/c3-counter.py` = 9ef99e8f20805501c3944e4b598e3fd7b7ac3ea3914674fa46e6affdc1e537ca (matches prereg).
- `census/round-41/c3-sites.tsv` = be363c0de5d332dc4223bdf6ccf5f2035e6e38af9cc30735463b07b5d2e764ea (matches prereg).
- `tools/souji-worktree-drift.py` at e2a7431 = b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 (matches pin).
- Tool refusal exit code: 2 (observed: `python3 -B pristine.py --root W --record /nonexistent.tsv` → `REFUSAL RECORD-MALFORMED: ... is not a regular file`, RC=2).

## How the counter scores (code read; file:line in census/round-41/c3-counter.py)

- L16–21 (docstring): a site is killed only when the FAIL-probe set equals the frozen mapped set on a mutant whose site label is rewritten to `ZZ-MUTANT`.
- L102–105 `mutate`: rewrites only the class token of the nth `Refusal("CLASS:` / `"REFUSAL CLASS:` match.
- L108–128: the pristine check requires only that the fixture print exactly the 21 probe ids as PASS with exit 0. It never checks that the fixture executes the tool.
- L138–148: verdict uses the fixture's own PROBE lines, `failing == sorted(mapped)`, `mrc == 1`.
- L139 + L109 (`mpath = scratch/mut-<SID>.py`, `run_fixture(fixture, mpath, scratch)`): the mutant path encodes the site id.
- L86 `sid, cls, probes, _trigger = line.split(...)`: the trigger column is parsed and discarded. Nothing checks that a probe's trigger reaches its site.
- No check on the fixture's bytes (no pin, no provenance). `--selftest` was not run.

## Candidates written (seat dir)

| file | sha256 | trick |
|---|---|---|
| `sniff-label.py` | 844d306e3defc606626125cc45314aff33061bc910965ad333420190825075b8 | A: reads tool bytes, finds the `ZZ-MUTANT` label, prints FAIL for that site's frozen probe ids; never runs the tool |
| `sniff-path.py` | 919dfd34103ec32531ad88b901e2b7a3a4a99cffc5a8ff279db9fde26bf40f4e | B: reads the site id from the mutant path `mut-S<NN>.py`; never reads bytes or runs the tool |
| `sniff-classtable.py` | 1eb4c3f18656750f5c9e7681f13229abf03e548e9aa1eaa7257b9a1df37ea615 | C: compares each site's label in the tool bytes with the frozen class column; never names `ZZ-MUTANT`; never runs the tool |
| `rc-only-decoy.py` | 9fde9570faf6265c9fb7d7d8ca1d82ee29a096c9f9195b4051de9f4a3264a630 | D: really runs the tool on a refusal trigger for each of the 21 probes; PASS iff exit code is nonzero; never reads stderr or the class label |

All four print the 21 frozen probe ids. Sniffers A–C print FAIL only for the mapped ids of the site they identify, and never probe. D is a real-but-blind probe, written to test whether the counter catches probes that ignore labels.

## Commands run and observed output

Scoring (the only supported path), each run from `/fast/scratch/hyaku/souji-r41/R41critic04`, with `TMPDIR` set to that scratch dir:

```
bash .../census/round-41/score-candidate.sh c3 /fast/scratch/hyaku/souji-r41/R41critic04 tests/fixtures/r41-refusal-sites.py=$SEAT/<candidate>
```

**Trick A (`sniff-label.py`)** — no probing:
```
PRISTINE ok rc=0 probes=21 crash=False dup=False summary=(21, 21, 0)
SITE S01 RECORD-MALFORMED killed failing=P01 mapped=P01 rc=1
SITE S02 RECORD-MISSING killed failing=P02a,P02b mapped=P02a,P02b rc=1
... (all 19 sites: killed, failing == mapped, rc=1)
SITE S19 USAGE killed failing=P19 mapped=P19 rc=1
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=844d306e3def
EXIT=0
```

**Trick B (`sniff-path.py`)** — no probing, reads only the mutant path:
```
PRISTINE ok rc=0 probes=21 crash=False dup=False summary=(21, 21, 0)
SITE S01 ... killed failing=P01 mapped=P01 rc=1
SITE S02 ... killed failing=P02a,P02b mapped=P02a,P02b rc=1
... (all 19 killed)
SITE S19 USAGE killed failing=P19 mapped=P19 rc=1
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=919dfd34103e
EXIT=0
```

**Trick C (`sniff-classtable.py`)** — no probing, no `ZZ-MUTANT` literal:
```
PRISTINE ok rc=0 probes=21 crash=False dup=False summary=(21, 21, 0)
SITE S01 ... killed ... (all 19 killed, failing == mapped)
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=1eb4c3f18656
EXIT=0
```

**Trick D (`rc-only-decoy.py`)** — real runs, exit-code-only verdict:
- First attempt (verdict `rc == 1`) was a fixture error on my side, not a counter result: the tool refuses with exit 2, so the pristine check failed with `PRISTINE FAIL rc=1 probes=21 crash=False dup=False summary=(21, 1, 20)` and `SUMMARY ... pristine=FAIL killed=0 survived=19`. I corrected the verdict to "nonzero exit" and rescored.
- Corrected run:
```
PRISTINE ok rc=0 probes=21 crash=False dup=False summary=(21, 21, 0)
SITE S01 RECORD-MALFORMED survived failing=- mapped=P01 rc=0
... (all 19 survived)
SITE S19 USAGE survived failing=- mapped=P19 rc=0
SUMMARY sites=19 probes=21 pristine=ok killed=0 survived=19 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=9fde9570faf6
EXIT=1
```

**Control (frozen, reproduced):** `bash score-candidate.sh c3 ... tests/fixtures/r41-refusal-sites.py=census/round-41/controls/c3-stub-fixture.py` →
`SUMMARY sites=19 probes=21 pristine=ok killed=0 survived=19 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=6ed213bd68cc` (same as the recorded control in controls/c3-control.txt).

Not run: `c3-counter.py --selftest`; no honest (probing) C3 fixture was built here.

## Question answers

1. **Does the counter catch a mutation-sniffing fixture?** No. Tricks A, B and C each score `killed=19 survived=0 misattributed=0 pristine=ok`, which meets the target. Each never invokes the tool.
   - A reads the `ZZ-MUTANT` label: the counter's own mutation token is visible in the bytes.
   - B reads the site id from the scratch path `mut-S<NN>.py` (counter L109/L139): the mutant filename encodes the answer.
   - C checks each label against the frozen class column. This needs no mutation token and is the purest form of "the counter checks only class labels."
2. **Can a probe pass pristine yet be unrelated to its site?** Yes, if its verdict depends on label text rather than on running the trigger (A, B, C above). A behavioural probe that reaches a different site is generally caught by the counter's failing-set equality (L139–148); I did not run such a case, so that point rests on code reading [INFERENCE].
3. **Does the counter catch a blind probe?** Yes: trick D scores `survived=19` (`killed=0`), because a label rewrite leaves the exit code unchanged. This is the one mutation class the counter does handle.
4. **Does the pristine check constrain the fixture?** Only that it prints PASS for the 21 ids and exits 0. A fixture that prints PASS without probing satisfies it (the sniffers pass pristine with `pristine=ok`).

## Named limits for the L1 (findings, not edits; the counter and tool are frozen)

- **L-C3-1 (sniffing):** the counter does not require the fixture to execute the tool. A fixture that reads the mutant bytes or path passes the target. Evidence: trick A/B/C scores above.
- **L-C3-2 (mutant path leaks the site):** the scratch name `mut-S<NN>.py` is the site id. Evidence: trick B.
- **L-C3-3 (trigger column unused):** `parse_sites` (L86) discards `_trigger`. Nothing checks that a probe's trigger reaches the site it is mapped to; only label-driven failing sets are checked.
- **L-C3-4 (no fixture provenance):** the fixture bytes are not pinned and not inspected. Its sha is only reported.
- **Consequence:** under the prereg's selection rule, a sniffing fixture is an all-target candidate and can win the C3 landing on size. Any "C3 met" claim from this counter alone is not evidence of coverage.
- **Smallest safe correction (for the L1 to decide, not applied here):** have the counter wrap `--tool` in an execution-counting shim, so each kill requires at least one run of the mutated site's line; or randomise the mutant filename and use per-run unique label tokens instead of `ZZ-MUTANT`, which closes trick B and A but not C. No single change closes all sniffing routes, because a fixture can always read the tool file as the same uid.

## Tooling

No tools installed or upgraded. Python 3.14.8 (existing). uid 1000 (not root).
