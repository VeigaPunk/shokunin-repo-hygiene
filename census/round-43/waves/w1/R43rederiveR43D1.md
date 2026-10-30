# R43rederiveR43D1 — independent committed-byte review

Axes: derived-count accuracy; receipt fidelity; independence from the frozen counter; reproducibility.

## Findings

No discrepancy found in required correction R43-D1. This review attacks C1's R43-D1 calibration evidence, not C2 or C3. The register's `rows=174` is independently supported; the stale receipt really prints `rows=173`.

Register inspected with `read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/c1-required.tsv`; relevant observed row:

```text
R43-D1	census/round-39/records/census-after.txt	rows	173	rows=174	0242085909fb6a4ee041c5443d76316ac6d59d4b	census-rows
```

## Exact commands and observations

Both commands ran read-only, concurrently, with cwd `/home/vgpnk/Projects/shokunin` and returned exit 0.

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0242085909fb6a4ee041c5443d76316ac6d59d4b:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
```

Observed stdout:

```text
174
```

Method: count exactly the committed Markdown lines whose first cell is an S identifier with at least three digits, using the assigned regular expression. This counts source rows, not receipt assertions.

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0242085909fb6a4ee041c5443d76316ac6d59d4b:census/round-39/records/census-after.txt
```

Observed stdout:

```text
# SOURCES census after — command: sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
census_rc=0
rows=173
W04=47
E11=0
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

## Verdict

| Check | Observed | Match |
|---|---|---|
| Derived value versus register R43-D1 | 174 versus `rows=174` | yes |
| Receipt line 3 versus registered stale value | `rows=173` versus 173 | yes |
| Derived count versus receipt assertion | 174 versus 173 | no; the asserted stale count is lower by one |

Recommendation: retain R43-D1's stated correction from 173 to 174. This is an evidence recommendation, not an admission or integration decision.

## Residual risk and verification gaps

Scope is R43-D1 only; R43-D2 and R43-D3 are not claimed verified. No counter code was read or executed. No runtime, candidate scoring, or broader test suite was invoked. The `read xd://lsp` prerequisite returned `No such tool: xd://lsp`; semantic references/definitions/diagnostics are unavailable, and the textual row count is not presented as semantic caller proof. The target is historical data, with no code changes or affected callers.

No scratch directory, clone, fixture, installation, or repository mutation was needed; no scratch cleanup remains. Only this assigned report was written.

Self-evaluation: accuracy 5 (committed-byte count and verbatim receipt); completeness 5 (D1 command, value, match, stale check); clarity 4 (full commands are long but reproducible); actionability 5 (explicit retain recommendation); conciseness 4 (receipt retained in full for line-3 evidence). Average 4.6. Improvement: shorten presentation only when full receipt evidence is unnecessary. User-agreement check: the verdict is limited to the assigned D1 evidence.
