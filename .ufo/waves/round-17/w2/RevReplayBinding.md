STATUS: PARTIAL — every digest the replay record binds verifies byte-exact against ddb7347/5fa6017 blobs, but the records themselves are NOT committed, and the record schema omits the replay script's own sha256 and the Python version.

Scope: binding completeness of `census/round-17/seat-audit-replay.py` and its two records, judged for "a verifier can re-run and compare". All line refs at ddb7347 unless noted.

## Findings

### F1 HIGH — the records are not committed; the claim "committed records" is false at ddb7347
- `git -C . ls-tree --name-only ddb7347:census/round-17/` → only `gate-replays-expected.json gate-replays.py run-matrix.py seat-audit-replay.py transcript-manifest.py`.
- `git show ddb7347:census/round-17/seat-audit-r16-replay-base5fa6017.json` → `fatal: path … exists on disk, but not in 'ddb7347'` (same for -ddb7347.json).
- `git status --porcelain -- census/round-17/` → `?? census/round-17/seat-audit-r16-replay-base5fa6017.json`, `?? …-ddb7347.json` (untracked).
- Provenance of the on-disk copies is intact: `cmp /var/tmp/souji-r17-L1/sa-before.json census/round-17/seat-audit-r16-replay-base5fa6017.json` → BASE-COPY-IDENTICAL; same for sa-after/…-ddb7347.json → CHANGED-COPY-IDENTICAL. The tool's atomic-write output is what landed in census/, byte for byte (sha256 bd2e61df…, 6f00a5b6…).
- Smallest fix: L1 commits both records in the integration commit (`git add census/round-17/seat-audit-r16-replay-*.json`). Nothing in the repo binds the C2 numbers until then.

### F2 MEDIUM — record does not bind the replay script's own bytes
`seat-audit-replay.py:66-79` builds `rec`; `"tool": "seat-audit-replay.py"` is a literal name and `argv[0]` is the relative invocation path. Every input (auditor, both specs, manifest, manifest tool) is sha-bound, but the producer of the record is not: a verifier cannot prove a given record was written by the committed ddb7347 version (sha256 e3a89931…) rather than any other edit. Smallest fix, matching the existing `manifest_check.tool_sha256` precedent (`seat-audit-replay.py:87`): add `"tool_sha256": sha256_file(Path(__file__))` next to `"tool"`.

### F3 MEDIUM — no Python version/interpreter binding
The auditor is executed in-process via `importlib` (`seat-audit-replay.py:33-38`), so its behavior rides on the replay's interpreter; the manifest tool runs under `sys.executable` (`:83`). The record stores neither. Python here was 3.14.8 — recoverable today only by luck from the stray `tools/__pycache__/souji-seat-audit.cpython-314.pyc`, not from the record. Smallest fix: `"python": {"version": sys.version, "executable": sys.executable}` in `rec`.

### F4 LOW — no cwd, no timestamp
`transcripts_dir`, both `specs[].path`, and `argv` are cwd-relative (`census/round-16/transcripts`, `.ufo/waves/round-16/w1-spec.json`); the cwd itself is unrecorded (recoverable only via the absolute `lane` + convention). The two runs are unordered inside the records (fs mtimes 14:21 only). Smallest fix: `"cwd": os.getcwd()` and `"generated_utc": datetime.now(timezone.utc).isoformat()`.

### F5 LOW — re-run comparison must be field-wise, not whole-file; document it
A verifier re-running with a different `--output` gets a different `argv`, and the base auditor path `/var/tmp/souji-r17-L1/sa-base.py` is temp-only — whole-record byte equality is impossible by design. The comparison protocol is: re-run pinned inputs, compare `auditor.sha256`, `specs.*.sha256`, `manifest.sha256`, `manifest_check`, and `waves` (argv/output path excluded). A git-rev field for the auditor is optional: sha256 is the stronger identity and I recovered both revs from it (below). One sentence in the docstring or a census/round-17 README would fix the gap.

### Hygiene — untracked, unignored pycache residue in tools/
`git check-ignore tools/__pycache__/` → rc 1 (not ignored); `tools/__pycache__/souji-seat-audit.cpython-314.pyc` (30 016 B, Oct 20 14:47) was created by the changed-run's in-process import. A careless `git add -A` at integration would commit it. Fix: delete it and add `__pycache__/` to .gitignore (or rely on L1's clean add list).

## Binding checks that PASS (each verified, not assumed)
Command set: `git show <rev>:<path> | sha256sum`, worktree `sha256sum`, `cmp`, `python3 -c` recount of record JSON.

| Record field | Record value | Ground truth | Result |
|---|---|---|---|
| auditor sha256 (base rec) | c9ff355c6bca…9bd3b3 | `git show 5fa6017:tools/souji-seat-audit.py` | match — base record really ran the true base auditor |
| auditor sha256 (changed rec) | 8268212db158…d5f54 | `git show ddb7347:tools/souji-seat-audit.py` | match |
| specs w1/w2 sha256 (both recs) | eb242e48… / 775a4c9c… | ddb7347 blobs `.ufo/waves/round-16/w{1,2}-spec.json` | both match |
| manifest sha256 + check | 4837d550…; exit 0, "check OK: 144 files verified" | ddb7347 blob `census/round-16/transcripts/MANIFEST.sha256` | match |
| manifest tool sha256 | 12e294b0… | ddb7347 blob `census/round-17/transcript-manifest.py` | match |
| lane / fleet | absolute `/home/vgpnk/Projects/shokunin/souji-shokunin` / `…/shokunin` | — | bound |
| argv | verbatim, both recs | — | bound |
| summaries vs rows | recounted from per-seat `violations` rows: base w1 1/19, w2 3/42; changed w1 1/20, w2 1/52 | record `summary` blocks and C2 claims | all four match exactly |
| transcript_count | 65 + 79 = 144 | MANIFEST entry count (145 tree files − MANIFEST itself) | match |
| row schema | `{args, class, line, severity, target, tool}` e.g. ConnReadmeIndex:180 V-WRITE-RELATIVE major in changed w2 | C2 adjudication | sufficient to re-derive seat claims |
| extra-file trust | `transcript-manifest.py:132-137` fails check on `on_disk − listed` ("extra:") | — | transcript_count cannot hide unlisted files |
| write safety | refuses existing `--output`; tempfile + `os.replace` in dest dir (`seat-audit-replay.py:57-59,120-129`) | — | holds |
| worktree == ddb7347 | `seat-audit-replay.py` e3a89931…, `souji-seat-audit.py` 8268212d… identical to committed blobs | — | the script I reviewed is the one committed |

## Verdict
PARTIAL — binding design is sound and every bound digest verifies, but (a) the records are uncommitted (F1), and (b) the schema omits the producer's own sha256 and the Python version (F2/F3), so a cold verifier cannot fully re-derive provenance from the repo alone today.

Smallest fix, all in `seat-audit-replay.py` `rec` literal (~4 lines) + L1 commit step:
```python
rec = {
    …
    "tool": "seat-audit-replay.py",
    "tool_sha256": sha256_file(Path(__file__)),
    "python": {"version": sys.version, "executable": sys.executable},
    "cwd": os.getcwd(),
    "generated_utc": datetime.now(timezone.utc).isoformat(),
```
(`from datetime import datetime, timezone` added), then: commit both records, delete `tools/__pycache__/`, and note the F5 field-wise comparison protocol. Regenerating the two records after the schema change is cheap and recommended so the committed records carry the new fields.

## Residual risk / verification gaps
- I did not re-execute the replay (records were produced by L1; re-running is allowed only under /var/tmp and would only re-derive what the row recount already confirmed).
- Whether the auditor's `run()` determinism holds across Python versions is untested (motivates F3's binding, not a defect found).
- `sa-base.py`'s content beyond its sha was not inspected further; its sha equality with the 5fa6017 blob is the operative fact.
