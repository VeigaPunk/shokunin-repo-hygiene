# S66MutKill — round-66 kill-power on the C1 matrix and M-ENV

Candidate: `.ufo/waves/round-66/w1/S66ExecWriter/candidate/souji-receipt-write.py`
sha256 `a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc` — matches the CANDIDATE-READY marker (checked before any mutant was built). Marker appeared after 2 polls.

## Kill rate

**4 of 8 mutants killed (50%).** Killed: K1, K2, K5, K8. Survived: K3, K4, K6, K7. All 8 compiled; none were compile-fail. K0 is the control, not counted.

## Per-mutant results (frozen C1 counter, base 045e1034, `--rev <mutant commit>`)

| K | mutant | new_forgeries | class_mismatches | EXIT | verdict |
|---|---|---|---|---|---|
| K1 | remove RECEIPT-ENV-CONFIG-SET gate | 0 | 2 | 1 | killed (E1, E2 refused without the class token) |
| K2 | remove RECEIPT-ENV-REDIRECT-SET gate | 3 | 3 | 1 | killed (E4, E5, E6 accepted) |
| K3 | remove `-c core.excludesFile=` pin | 0 | 0 | 0 | **survived** |
| K4 | remove GIT_CONFIG_GLOBAL=devnull | 0 | 0 | 0 | **survived** |
| K5 | mode mask `0o7777` -> `0o777` | 2 | 2 | 1 | killed (MOD2, MOD3 accepted) |
| K6 | remove GIT_NO_REPLACE_OBJECTS=1 | 0 | 0 | 0 | **survived** |
| K7 | remove GIT_CONFIG_NOSYSTEM=1 | 0 | 0 | 0 | **survived** |
| K8 | M-ENV (frozen c2-mutate recipe) | 2 | 2 | 1 | killed (N3, P13 accepted) |
| K0 | control: base writer in new slot | 8 | 8 | 1 | matches frozen do-nothing control `new_forgeries=8 class_mismatches=8 EXIT=1` |

Each mutant was a single change off the candidate bytes; `diff` against the candidate showed 1–5 changed lines per mutant (K8 three lines removed). Anchors were asserted to occur exactly once before each edit.

## Survivor list (findings)

- **K3, K4, K6, K7 survive.** Every one of them removes a pin the frozen C1 matrix does not exercise:
  - K3 (`core.excludesFile` pin) and K4 (`GIT_CONFIG_GLOBAL` pin) only change behaviour when a host/global or repo-local excludes file hides untracked content. The frozen matrix has no such row. The repo-local case is named limit L1 (outside C1), and L2 names the host-config behaviour change. [INFERENCE from row names and the counter's case specs; I did not audit each fixture.]
  - K6 (`GIT_NO_REPLACE_OBJECTS`) and K7 (`GIT_CONFIG_NOSYSTEM`) need a replace ref or a system config file. No matrix row creates one. [INFERENCE, same basis.]
  - Conclusion: the C1 claim as frozen cannot distinguish these pins from their absence. This is a coverage finding. I did not change the contract.
- Survival of K3 is expected under the named limit L1 and is recorded as such; it is not a claim that the pin is unnecessary.

## K8 (M-ENV) detail

- `c2-mutate.py --writer <candidate> --out <mutant>`: exit 0, `MUTANT M-ENV written ... removed_lines=3`. The anchor occurred once and the needle was in the deleted block. No refusal.
- C1 on K8: `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=2 new_honest=5 class_mismatches=2 regress=PASS`, EXIT=1. Rows N3 and P13 accepted with no class.
- C2 round-66 counter (`--tsv-rev 4576f101…`, `--rev 9b69c85f…`): `SUMMARY rows=5 findings=2 verdict=FAIL`, EXIT=1. Findings: `SCOPE-OVERREACH s2` (claim closed_full needs marker `env`; writer lacks it — `env=0`), and `GOVERNED-STATEMENT-UNRESOLVED s5`.
- C2 round-65 counter (`--tsv-rev 2761f0aa…`, same rev): `SUMMARY rows=4 findings=0 verdict=PASS`, EXIT=0. This reproduces round-65 M10: the mutant is scored live.
- Mechanism of the round-65 miss: the round-65 `EMISSION_TOKENS` contains bare `return` (line 88 of census/round-65/c2-counter.py). In the writer's own self-test code, `r.returncode` on lines that also carry the literal `RECEIPT-INDEX-ENV-SET` (for example line 1152 of the mutant: `if r.returncode != 2 ... "RECEIPT-INDEX-ENV-SET" not in r.stderr`) therefore counts as a refusal-emitting line. The round-66 repair (`RETURN_LITERAL`, a `return` followed by a string literal) does not match `returncode`, so the mutant scores `env=0`. The repair works on this mutant.
- **Caveat (caller must read):** the mutant commit is built on base 045e1034, so the SKILL.md read by both C2 counters is the BASE SKILL.md, not the candidate SKILL.md. I did not commit the lane's SKILL.md bytes. Part of the round-66 `findings=2` is therefore the `s5 GOVERNED-STATEMENT-UNRESOLVED` artefact (s5 wording absent from base SKILL.md). The M-ENV kill itself is the `s2` finding, driven by `env=0` from the writer bytes. Rerun against a commit carrying the candidate SKILL.md before reading s5 as evidence.

## Not measured / limits of this report

- I did not run the frozen C1 counter on the **unmutated candidate**; that is the L1's measurement.
- One M-ENV mutant only (named limit L5). The kill rate above covers the seven writer-pin/mode mutants plus M-ENV, not a full battery.
- Mutant commits existed only in scratch clones (identity `S66Seat <s66seat@example.invalid>`, never pushed). The clones and work dirs were removed (`rm -rf` of the scratch root; verified gone). Mutant bytes and SHA-256 are kept in `mutants/`.
- Lane was read-only for this seat: no git mutation in the lane.

## Tooling

No tool installed or upgraded. Used the host's Python 3.14.8 and git 2.56.0 as found. pacman was not touched.

## Host facts

Nothing required from sysctl or from host state. No bwrap or user-namespace use.
