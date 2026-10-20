STATUS: DONE — regenerate.py computes the frozen verdict from the checker's own evaluation, refuses a non-clean record unless `--allow-nonclean`, and reproduces the committed expected.json at the measured rev.

Round 17, WAVE 1 (BUILD). Routed item: D6 third bullet / R16-M2.
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin (base 5fa6017ddcae9f6bd4412df44765f6360cb16294).
OWN ONLY file: `tests/fixtures/r15-preservation-frozen/regenerate.py` (modified). `expected.json` / `record.json` in the lane were **not** written by me (digests unchanged, see §4).

## 1. What the literal was and what it now is

Before: `regenerate.py:130` emitted `"verdict": "clean"` as a constant, so a record that the checker rejects would still be published with an admitting verdict — the pin was authored, never observed (spot-check `corpus/lessons/round-16-verifier-spotcheck.md:67,143`).

After (all in the assigned file, `git diff` 64 insertions / 3 deletions):

- `CHECKER = "tools/souji-preservation-evidence.py"` and `VERDICT_BY_STATUS = {0: "clean", 1: "failed", 2: "could-not-evaluate"}`, mirroring the checker's documented stable exit-code contract (`tools/souji-preservation-evidence.py:36-53`). The verdict is mapped from the exit code, never scraped from prose.
- `run_checker()` invokes the checker with `sys.executable` (the interpreter running the regenerator) and `cwd`-independent absolute paths.
- `evaluate_record(record_text)` runs `checker --root <LANE> --record <record_text>` — the same `evaluate()` entry point `--frozen` calls internally (`souji-preservation-evidence.py:1739-1749`), so the verdict is the checker's own frozen evaluation, not a reimplementation. It raises (exit 2 path) if the checker returns a code outside {0,1,2}.
- `main()` computes `verdict` **before** touching the output files:
  - verdict `clean` → writes `record.json`, then `expected.json` with `"verdict": verdict`;
  - verdict != `clean` and no `--allow-nonclean` → prints `regenerate: checker verdict is '<v>', not 'clean'; refusing to write record.json/expected.json (rerun with --allow-nonclean to record it)`, replays the checker's stdout to stderr, returns **3**; neither file is written;
  - `--allow-nonclean` → writes the computed verdict verbatim (never `clean`), announces `regenerate: --allow-nonclean accepted verdict='<v>'` on stderr, and the final summary line now ends `, verdict=<v>`.
- After writing, a **frozen re-check** runs `checker --frozen <HERE> --root <LANE>`; its exit status must map to the recorded verdict, else exit 2 with the checker's output. This makes the writer self-verifying against exactly the mode consumers use.
- Docstring updated: usage gains `[--allow-nonclean]`, the verdict-is-computed paragraph, and the exit-code list (`0` wrote; `2` usage/binding/tool failure; `3` non-clean refused).

Design note: the recursion `write expected.json → run --frozen` is avoided by evaluating the record through `--record` first. `--frozen` also refuses to report the observed verdict on mismatch (it converts to `could-not-evaluate`, `:1753-1759`), so it cannot be used to discover a verdict — `--record` is the only path that surfaces it, and it is the identical `evaluate()`.

## 2. Success path in a byte copy (ALLOWED-EXEC)

Copy: `rsync -a --exclude=.jj ./ /var/tmp/souji-r17-RegenerateVerdict/lane/` (no hardlinks; `.git` copied, `git -C <copy> rev-parse HEAD` → `5fa6017ddcae9f6bd4412df44765f6360cb16294`). Scratch removed afterwards.

```
cd /var/tmp/souji-r17-RegenerateVerdict/lane && python3 tests/fixtures/r15-preservation-frozen/regenerate.py --rev 5fa6017
regenerated at 5fa6017ddcae: baseline_preharm=8/20 fail, baseline=16/20 fail, changed=0/20 fail, namespace=0/12 fail, verdict=clean
REGEN_RC=0
```

The script's own post-write frozen re-check passed (it returns 2 on mismatch). Independent confirmation on the produced directory:

```
python3 lane/tools/souji-preservation-evidence.py --frozen lane/tests/fixtures/r15-preservation-frozen --root lane
souji-preservation-evidence: clean … frozen_files: 3
FROZEN_RC=0
python3 lane/tools/souji-preservation-evidence.py --root lane --record lane/tests/fixtures/r15-preservation-frozen/record.json
souji-preservation-evidence: clean
RECORD_RC=0
```

### Comparison with the committed expected.json

`diff -u` against `tests/fixtures/r15-preservation-frozen/expected.json` printed exactly one hunk:

```
-  "record_sha256": "173db77793bca747e9efad4150ea8a0dd2d9d4bdc0c17f30dc734bfe0e983599",
+  "record_sha256": "4f0e69686a23dfb7ce22a59266a90426c4a19cbf22bcdc900d96e10ccc4f8d93",
   "verdict": "clean"
```

`files` (all three pins, `64a60fd0…`/`27474396…`/`e6a984b1…`) and `record` are byte-identical; the computed verdict `clean` equals the committed literal. Only `record_sha256` moves, because it digests `record.json`.

### Documented differences in record.json (159 diff lines, all attributable)

Deep comparison modulo `souji-r16-repin.<suffix>` (the script's own scratch dir names) leaves:

1. `measured_commit` `c6207bd…` → `5fa6017…`; `runs.changed.tool.commit` and `namespace_controls.tool.commit` likewise. The committed record was measured at `c6207bd`; regenerating at 5fa6017 must record 5fa6017 (and `expected.json` pins are unchanged because `souji-census.sh` and both fixtures are byte-equal at both revs).
2. `argv` paths and each arm's `stdout`/`stdout_sha256`/`stdout_bytes_total` for `baseline`, `changed`, `namespace_controls`: the scratch directory name (`souji-r16-repin.<8 chars>`) is embedded by `run_arm`. `stdout_bytes_total` for `baseline_preharm` moved 4255→4254 for the same reason.
3. `runs.baseline_preharm` `cases[*].detail` and `stdout` for FAIL rows: the fixture embeds the trace PID and the fixture's own `r15-census-config.<suffix>` scratch name (`… access: strace store access: 598662 access("/var/tmp/r15-census-config.s8n_rh15/…")`). Case **ids and statuses are identical** across all four arms.
4. Nothing else. Byte-identity of `record.json` across regenerations is therefore impossible by construction (fixture-embedded PID and mktemp suffix); it is not caused by this change. `expected.json` is reproducible byte-for-byte at a fixed rev apart from `record_sha256`.

## 3. Falsifier: non-clean verdict refuses to publish

Second copy (`lane2`) with one literal in the checker's copy flipped (`PREHARM_SHA256 = "0a000c59…"`), then `--rev 5fa6017`:

```
regenerate: checker verdict is 'could-not-evaluate', not 'clean'; refusing to write record.json/expected.json (rerun with --allow-nonclean to record it)
souji-preservation-evidence: could-not-evaluate
finding pinned-mismatch: runs.baseline_preharm.tool.sha256=6a000c59… is not the pinned 0a000c59…
REFUSE_RC=3
```

`record.json` and `expected.json` retained their pre-run digests (`173db777…`, `d955b18c…` = the `.orig` copies), i.e. **nothing was written**. The script also correctly propagated the checker's own finding text, so the refusal is auditable.

Recording override (`--allow-nonclean`), same copy:

```
regenerate: --allow-nonclean accepted verdict='could-not-evaluate'
regenerated at 5fa6017ddcae: … verdict=could-not-evaluate
ALLOW_RC=0
{ "files": {…unchanged pins…}, "record": "record.json",
  "record_sha256": "c45001e6…", "verdict": "could-not-evaluate" }
```

The non-clean verdict is recorded verbatim; the post-write `--frozen` re-check accepted it (exit 0 requires the frozen status to match the recorded verdict, `:1753-1761`). No `clean` was ever written by a non-clean run.

An earlier `lane2` attempt also proved the pre-existing binding guard still fires first and independently: after a sibling edited `tools/souji-census.sh` mid-wave, `--rev 5fa6017` returned rc 2 with `regenerate: tools/souji-census.sh differs between 5fa6017ddcae and the worktree`. I restored the rev's bytes **in the copy only** to isolate the verdict path.

## 4. Lane state

`python3 -m py_compile tests/fixtures/r15-preservation-frozen/regenerate.py` → COMPILED (the `__pycache__` it created was deleted).

```
git status --porcelain tests/fixtures/r15-preservation-frozen
 M tests/fixtures/r15-preservation-frozen/regenerate.py
sha256sum tests/fixtures/r15-preservation-frozen/{expected.json,record.json}
d955b18c…  expected.json      (untouched)
173db777…  record.json        (untouched)
```

No production caller is affected: the only `regenerate.py` references in `tools/`, `tests/`, docs and corpus are self-documentation (`SKILL.md:150`, `LOG.md:875`, `corpus/lessons/round-16*.md`); no script invokes it, and no code depends on its stdout format or exit codes beyond `0`.

## 5. Verdict and residual risks

- **Holds** for the assigned claim: verdict is computed by the checker's own evaluation; non-clean refuses (exit 3, no writes); `--allow-nonclean` records the observed verdict and is announced; the clean path reproduces the committed pins and the committed `"verdict": "clean"` at the rev that produced those pins.
- Residual: `record.json` cannot be byte-identical across runs (fixture-embedded PID + mktemp suffix in `argv`/`stdout`/`detail`). If L1 wants a deterministic record, the fixture must normalise those strings; out of this assignment's scope and file.
- Residual: the post-write frozen re-check failing exits 2 **after** files were written (message says `files left written`). The mandated refusal is pre-write, and this path only fires if the committed pins are inconsistent with the just-written record, i.e. never in the success path.
- Disclosed: `run_checker` uses `sys.executable`; the arms still spawn the literal `python3` (`run_arm`). Both are the same interpreter in practice; not normalised here.
- Tooling: no installs or upgrades (none needed); scratch under `/var/tmp/souji-r17-RegenerateVerdict` deleted; no `jj` and no git write command was run in any repo.
