# S44mutationtester54 — C2 tmpdir mutation probe

Axes: calibration / operability / coverage. Assigned axis: operability.
Frozen revision: `d314fd6e85d62565344fa6c4b102f52f62297884`.

## Result

**KILLED by the C2 counter; SURVIVED the hidden audit alone.** Both pristine and restored baselines pass. No detector crash occurred. Admission remains outside non-author closure; this probe makes no certification or score claim.

The single private tool mutation at line 354 replaces:

```python
tmp = tempfile.mkdtemp(prefix="freeze-selftest-")
```

with:

```python
tmp = tempfile.mkdtemp(prefix="freeze-selftest-", dir=os.environ.get("TMPDIR"))
```

This plausible explicit-TMPDIR regression disables tempfile's missing-directory fallback. Expected detection: the counter's missing-TMPDIR selftest leg must report `tmpdir=RED`, exit 1; the hidden audit does not exercise selftest and should remain 10/10.

| Stage | C2 exit | C2 differing fields | Hidden audit exit / summary |
|---|---:|---|---|
| pristine | 0 | `selftest=ok tmpdir=ok` | 0 / `SUMMARY scenarios=10 pass=10 fail=0` |
| mutated | 1 | `selftest=ok tmpdir=RED` | 0 / `SUMMARY scenarios=10 pass=10 fail=0` |
| restored | 0 | `selftest=ok tmpdir=ok` | 0 / `SUMMARY scenarios=10 pass=10 fail=0` |

All three C2 runs retain:

```text
tool=present population=ok retention=ok hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED controls_ran=ok
```

Full pristine/restored counter output:

```text
SUMMARY tool=present population=ok retention=ok hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED controls_ran=ok selftest=ok tmpdir=ok
```

Mutated counter output:

```text
SUMMARY tool=present population=ok retention=ok hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED controls_ran=ok selftest=ok tmpdir=RED
```

A direct mutated-child run with missing TMPDIR exits 1, stdout empty, with `FileNotFoundError: [Errno 2] No such file or directory` from `tempfile.mkdtemp`. That is a **candidate crash correctly rejected by the counter**, not a crashing control/audit mistaken for successful discrimination. Full traceback is preserved in `mutated-child.json`.

## Exact invocation and isolation

All command arrays, stdout, stderr, exit codes and timings are in `pristine.json`, `mutated.json`, `restored.json`, and `mutated-child.json`. Each stage ran these two commands concurrently, cwd equal to the seat scratch:

```sh
O=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44mutationtester54
S=/fast/scratch/hyaku/souji-r44/S44mutationtester54
# STAGE was pristine, mutated, then restored; TMPDIR=$S for these commands.
python3 -B "$O/probe.py" "$STAGE"
python3 -B "$O/probe.py" --child "$O/audit.py" --tool "$S/tool.py" --work "$S/$STAGE-audit"
# Additional assigned-property diagnostic, mutated bytes only:
TMPDIR="$S/direct-missing-tmpdir" python3 -B "$O/probe.py" --child "$S/tool.py" --selftest
```

`probe.py` loads the byte-identical frozen counter and invokes its main with `--root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch $S/$STAGE`. Its one injection replaces the counter's TOOL blob result with private candidate bytes; all other blobs come from the frozen revision. No frozen counter/audit bytes were edited. Files were obtained with `git -C LANE show REV:PATH`.

The harness recursively guards fixture `git add`/`commit`: before every mutation, `git rev-parse --show-toplevel` must equal that fixture's directory. New fixture `git init` is restricted beneath the seat scratch. Python tempfile fallback is redirected to the existing seat scratch, preserving fallback availability without writing trees into /tmp. This harness condition is identical in all stages. Retention executes the lane's r43 counter; post-run byte comparisons show its counter and hidden audit match the frozen revision.

## Restoration evidence

Candidate SHA256 pristine/restored:
`f7f54e8f0a71aa952a66f53abb12dcd96f2805d8a8ef141c4b741a7865d87999`

Candidate SHA256 mutated:
`02b2a458668f10403f18531b592730ecd66369e5c729a00edd90c700ba398584`

Frozen C2 counter SHA256 before/after:
`0cb6ce80a23b460d1a03e0530ca2ef0866af773bdb7f5b88f6dc84bd0f525252`

Frozen C2 audit SHA256 before/after:
`50872b0da7a36d377ced9cf0e51579ef00f0f0ae402eebad8c579fce6e5e843e`

The tool's private bytes were restored in a `finally` block, restored detectors passed, and scratch was deleted. `restoration.json` records exact restoration, production byte equality to frozen blobs, and `scratch_removed=true`. Frozen originals and mutant candidate remain as evidence in this output directory. No production, sibling, git-index/jj, shared LOG or PATH-directory writes. Python 3.14.8; no installs/updates.

## Limitations and finding

One mutation only; no general adversarial robustness conclusion. Hidden-audit-only survival identifies its scope boundary, not a counter defect: missing TMPDIR is covered by the counter's independent operational leg. The injected candidate does not replace retention's historical frozen-tool blob. The temporary-storage fallback location was deliberately constrained by the seat scratch policy. No production change proposed or made.

Self-evaluation: accuracy 4 (instrumented rather than unwrapped counter); completeness 5 (pristine/mutated/restored, child crash evidence, cleanup); clarity 4 (harness details require reading probe.py); actionability 5 (exact receipt commands and candidate retained); conciseness 4 (isolation detail adds length). Overall 4.4/5. Improvement: a future approved standalone harness could reduce wrapper complexity; not part of this assigned probe. User agreement expected because every result links to raw receipts.
