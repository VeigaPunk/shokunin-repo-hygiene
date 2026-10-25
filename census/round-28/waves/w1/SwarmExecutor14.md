## Status
STATUS: PASS — Exec-C3RunCapture ran tools/souji-wave-evidence-capture.sh for rounds 26 and 27 (both exit 0, tool-internal captured+verified), receipts exist, both manifests verify with `sha256sum -c` rc=0, file counts pasted. One defect found and reported (not synthesized/fixed per item): round-26 manifest has 2 entries unverifiable by `sha256sum -c` because source filenames contain newlines; round-27 clean.

## Evidence
- `bash tools/souji-wave-evidence-capture.sh /home/vgpnk/Projects/shokunin/souji-shokunin 26` → `captured+verified: .../.ufo/waves/round-26 -> .../census/round-26/waves`, exit=0.
- `bash tools/souji-wave-evidence-capture.sh /home/vgpnk/Projects/shokunin/souji-shokunin 27` → `captured+verified: .../.ufo/waves/round-27 -> .../census/round-27/waves`, exit=0.
- Receipt paths:
  - `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-26/waves/manifest.sha256` (+ `summary.tsv`)
  - `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-27/waves/manifest.sha256` (+ `summary.tsv`)
- Verification (run from each receipt dir):
  - `cd census/round-26/waves && sha256sum -c manifest.sha256` → rc=0; 1380 lines OK; `sha256sum: WARNING: 2 line(s) are improperly formatted`.
  - `cd census/round-27/waves && sha256sum -c manifest.sha256` → rc=0; 124 lines OK; no warnings.
- File counts:
  - `find census/round-26/waves -type f | wc -l` → 1385
  - `find census/round-27/waves -type f | wc -l` → 125
- Tool self-verification: `bash tools/souji-wave-evidence-capture.sh <lane> 26 --verify` → `captured+verified`, exit=0; same for 27.
- Repro (scratch, `/var/tmp/souji-r28-SwarmExecutor14`, removed after): source with one regular file named `first\nsecond.md` (real LF) → captured manifest line is `\73cb3858a687a8494ca3323053016282f3dad39d42cf62ca4e79dda2aac7d9ac  ./first\nsecond.md` (backslash inserted before the hex; LF rendered as literal `\n`).

## Findings
1. Round-26 receipt: manifest contains 2 entries whose hash tokens are corrupted (leading `\` before the hex) and whose paths render the newline as literal `\n`; `sha256sum -c` therefore cannot verify them (WARNING "2 line(s) are improperly formatted"; rc stays 0). Root cause: source filenames contain real newlines — `.../vadv54-run/r/nl/first<LF>second.md` and `.../vadv54-run/r/scratch/.scratch/old<LF>name.log` (present identically in `.ufo/waves/round-26/` and in `census/round-26/waves/`, so the byte-exact copy itself is faithful). Reproduced deterministically against the tool on a minimal fixture — defect belongs to `tools/souji-wave-evidence-capture.sh` (Exec-C3CaptureTool deliverable), not to the run. The tool's internal verification passes because it byte-compares the recomputed manifest to the same corrupted bytes.
2. Round-26 receipt counting: 1385 regular files (incl. manifest.sha256 + summary.tsv) = 1380 cleanly-verified entries + 2 manifest-corrupted entries + symlinks excluded by the frozen `find -type f` convention (verified `stat -c %F` on sampled omitted names: all symbolic links).
3. Round-27 receipt: fully clean — 125 regular files, 124/124 entries verify OK, no warnings.
4. No tooling installed (none needed; no pacman/uv/npx transactions). No git/jj mutation performed; read-only git status/log only.

## Attack log
No attack items assigned to this seat (`[INFERENCE]` — item Exec-C3RunCapture is an execution item, not an attack). Finding 1 is reported as a defect for the L1/reviewer (Rev-C3Receipts, Mut-C3) assessment.
