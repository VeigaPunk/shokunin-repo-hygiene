# S44executor34 — C3 output-envelope probe

Axes: calibration / operability / coverage. This probe covers C3 coverage: output-envelope refusal and a normal JSON-output success path.

## Method

Read the r44 preregistration and `census/round-44/c3-counter.py`; the latter specifies the governed cutover as outright refusal of a `--json` leaf symlink with `JSON-TARGET-SYMLINK`, versus the historical behavior that resolved/wrote through it. Read the tool contract in `tools/souji-worktree-drift.py` and `tests/fixtures/r38-drift-write-envelope.py` (legacy envelope fixture). Built isolated repositories under `/fast/scratch/hyaku/souji-r44/S44executor34/`: each root contains one initialized local Git repository, with a consistent two-line record; a JSON symlink points to an outside sentinel. The tool bytes were independently read from the named Git revisions (not from the working tree).

Exact probe command:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44executor34/probe.py
```

The driver tests both `--json <symlink>` and `--json <new-regular-file>` against each tool. Full stdout, stderr, exit statuses, JSON content, sentinel hashes and SHA-256 of both tool blobs are retained in `receipts.json`.

## Observed findings

| Revision | Tool SHA-256 | Symlink attempt | Sentinel unchanged? | Regular JSON output |
|---|---|---|---|---|
| Base `55d7af6f5a22340f7a3de1c386e514ababfaa75f` | `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6` | rc 0; empty stderr; `SUMMARY ... drift_rows=0 unreachable=0` | **No**; hash changed from `f320c3fcd16768f2305034fc7b95aa34a433fdd858e17852c6d989e9a7158aa2` to `2d5c326a56f86e825d03e2ea37353eaf260891b147c625508a81c9ba08b2b4d5` | rc 0; JSON file created, valid summary and empty drift list |
| Frozen `d314fd6e85d62565344fa6c4b102f52f62297884` | `4d6bb64312e1cb52863d4d3b95f32503b6ff8d8189680d940b280ffcd21c490d` | rc 2; stderr `REFUSAL JSON-TARGET-SYMLINK: .../result.json names a symlink`; no stdout | **Yes**; hash remains `f320c3fcd16768f2305034fc7b95aa34a433fdd858e17852c6d989e9a7158aa2` | rc 0; JSON file created, valid summary and empty drift list |

## Conclusion and limits

The frozen cutover changes this exact case: the base follows the symlink and overwrites its outside target; the frozen tool refuses before writing and preserves the target. The normal, non-symlink JSON output succeeds in both revisions, so refusal is scoped to the dangerous leaf link rather than disabling JSON output. This is a focused independent invocation, not a run of the r38 fixture or the C3 counter; it does not establish the complete battery, race resistance, or any broader admission/certification claim. No tool installs/updates were needed.

## Files / cleanup

- `probe.py` — isolated probe driver.
- `receipts.json` — full captured evidence.
- Scratch trees used for the probe were removed before handoff; no production, frozen counter, sibling output, shared bookkeeping, or Git/JJ state was changed.
