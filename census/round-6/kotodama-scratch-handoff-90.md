# S90 — kotodama `.scratch` handoff (round 6, K1)

Seat S90, independent, read-only. Lane written: this file only.
Target: `/home/vgpnk/Projects/shokunin/kotodama-shokunin/.scratch`.
No deletion, no quarantine, no `git fetch/push/commit/branch/prune`, no ledger write, no secret-file open.

## Verdict

**NOT-SAFE. No removal. No prune. No quarantine.**

The directory is a live workspace of a dirty, unpushed lane. Size is not a receipt. The r5 label "16G" is already stale.

Receipt check against `tools/souji-verify.spec.md` (reasoned from commands below; `souji-verify.sh` was not pointed at this tree, because a digest walk would open secret-shaped names):

- `pushed`: no. `.scratch/` is gitignored.
- `moved-to-obsidian`: no. Ledger has a header and no matching row.
- `stale`: no. Top-level mtimes are from today; a live `mkdtemp` writer is creating `r26-o33-*` dirs; between 16:04 and 16:41 HEAD moved from `1ad491a` (ahead 47) to `b95fca1` (ahead 49), a round-27 declare commit.
- Owning lane dirty and unpushed: PROVINCE refusal. Verdict stays `NOT-SAFE` even for empty dirs and duplicate copies.

## Classification of record

Closed walk `2026-10-18T16:31:45-0300` → `2026-10-18T16:32:46-0300` (elapsed 60.91s).
Every file `os.walk` returned got exactly one class. `errors=0`. Unclassified remainder inside the walk: **0**.

| measure | value |
|---|---|
| files | 661234 |
| class-count sum | 661234 |
| dirs below `.scratch` | 108830 |
| empty dirs | 4215 |
| top-level entries | 320 |
| summed `st_size` (hardlinks counted per name) | 28467104711 (26.512 GiB) |
| unique inode bytes | 27529965392 (25.639 GiB) |
| hardlink-duplicate bytes | 937139319 |
| `.git` directories | 235 |
| header reads (`read` ≤ 200 bytes) | 625742 |
| secret-shaped files, not opened | 71 (31370 bytes) |
| symlinks, not followed | 165 |

Human `du -sh` labels during this census were 17G, then 19G, then 18G. Do not use them. Byte counts above are the measurement.

## Why the r5 "16G" figure moved

| instant | command | observed |
|---|---|---|
| 2026-10-18T15:18:23-03:00 | r5 seat-51: `du -sh kotodama-shokunin/.scratch` | `16G` (cited, not re-run) |
| 2026-10-18T15:52:28-03:00 | `du -sh --apparent-size <scratch>` | `17G` |
| 2026-10-18T15:57:04–15:57:39-03:00 | first full class walk | 535,606 files; summed 19,230,125,122; unique 18,292,985,803; 219 tops; class sum matched |
| 2026-10-18T16:29:11-03:00 | metadata recount | 659,072 files |
| 2026-10-18T16:31:45-0300–2026-10-18T16:32:46-0300 | walk of record | 661234 files; summed 28467104711; unique 27529965392; 320 tops |
| 2026-10-18T16:41:08-03:00 | recount + `du -sb` | 663,013 files; `du -sb` = 27,589,077,025 |
| 2026-10-18T16:45:31-03:00 | class pass, `mtime >=` walk end | 2,239 files classed (overlaps the walk where files were rewritten) |

Growth during this seat: +125,628 files (661,234 − 535,606) and +9,236,979,589 unique bytes between the 15:57 walk and the 16:32 walk. That is live writing, not a recount error. Both walks had class-sum = file-count and `errors=0`.

`to-verify`: `os.walk` does not revisit a directory. Files created in an already-visited directory during the 61s walk are absent from the 661,234. The 16:41 recount was +1,779 files versus the walk. That delta was not identified path-by-path. The 16:45 mtime pass classed 2,239 files with `mtime >= 16:32:46` (yaml 639, markdown 407, log 363, python 278, json 194, plain 114, empty 92, tsv 62, other 51, binary-nul 35, shell 2, git-internal 1, secrets-refusal-unread 1). That set overlaps the walk. It does not prove a disjoint list of the +1,779. The one secrets-refusal file in that mtime pass is `round-27/validation/links-selftest/outside-secret.txt`, 8 bytes, mode `0o644`, content unread. It is also in the walk's 71-path list.

## Byte composition

Most of the mass is repeated copies, not unique new content. Hardlinks save only 937139319 bytes, so the copies are independent files.

Paths containing `reports/supplement-opencode-1/scratch/`: 25715 files, 14786897116 bytes (13.771 GiB), in 13 top-level holders.
Live tree, same relative path, measured read-only: `du -sb kotodama-shokunin/reports/supplement-opencode-1/scratch` → `399644176`. `git check-ignore -v` → `.gitignore:5:/reports/supplement-opencode-1/scratch/`.

Holders that are exact integer multiples of 399,644,176:

| top | supplement bytes | × live |
|---|---:|---:|
| `x58` | 6394306816 | 16× exact |
| `x37` | 3197216012 | 8× + 62604 |
| `cold-run-4` | 799288352 | 2× exact |
| `x46` | 799288352 | 2× exact |
| `r23-run` | 399644176 | 1× exact |
| `audit4` | 399644176 | 1× exact |
| `r24-run` | 399644176 | 1× exact |
| `r25-o04` | 399644176 | 1× exact |
| `r25-o08` | 399644176 | 1× exact |
| `r25-run` | 399644176 | 1× exact |
| `r26-d05` | 399644176 | 1× exact |
| `r4c` | 399644176 | 1× exact |
| `r26-run` | 399644176 | 1× exact |

PDF magic (`%PDF`, first bytes): 1443 files, 12132124250 bytes (11.299 GiB). They sit inside those supplement copies. Headers were not parsed past 200 bytes. Filenames of the PDFs are not reproduced here.

The other large classes are cloned lane working trees (markdown, yaml, json, python, plain text) plus 1161316834 bytes of nested `.git` internals across 235 `.git` directories.

## Purpose class — every top-level entry

Rules, first match:

1. `secrets-refusal-unread` — the entry itself is one secret-shaped file.
2. `empty-live-temp` — name `r26-o33-*`, 0 files, 0 bytes. Live `mkdtemp` dirs.
3. `loose-empty-output` — one top-level file, 0 bytes.
4. `loose-session-output` — one top-level file, non-empty.
5. `supplement-corpus-copy` — any PDF bytes, or any bytes under `reports/supplement-opencode-1/scratch/`.
6. `nested-git-clone` — at least one `.git` directory, no supplement/PDF bytes.
7. `empty-dir` — 0 files and 0 bytes, other name.
8. `working-tree-copy-no-git` — markdown bytes > 1,000,000 and no `.git`.
9. `small-work-dir` — everything else.

| purpose | tops | files | bytes |
|---|---:|---:|---:|
| `supplement-corpus-copy` | 13 | 169729 | 17996680011 |
| `nested-git-clone` | 74 | 482677 | 10250366552 |
| `working-tree-copy-no-git` | 5 | 7792 | 188063924 |
| `small-work-dir` | 68 | 912 | 29777295 |
| `loose-session-output` | 111 | 111 | 2216921 |
| `secrets-refusal-unread` | 1 | 1 | 8 |
| `loose-empty-output` | 12 | 12 | 0 |
| `empty-live-temp` | 34 | 0 | 0 |
| `empty-dir` | 2 | 0 | 0 |
| **sum** | **320** | **661234** | **28467104711** |

Empty non-temp dirs (0 files): `o38`, `r27-d20` (each has one empty child dir). Still NOT-SAFE; the lane is live, and `r27-d20` appeared while round-27 was being admitted.

Working-tree copies with no `.git`: `r24-gates`, `r27-r4-src`, `coldrun-b-export`, `r25d`, `round-27`.

## File taxonomy — every file in the walk

Classifier: do not open a basename containing `credential`/`secret`/`password`/`passwd`/`token`, or `.env*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa*`, `id_ed25519*`, `id_ecdsa*`, `id_dsa*`. Do not follow symlinks. Inside a `.git` path component, class `git-internal` by path (no header). Size 0 → `empty-file`. Otherwise read at most 200 bytes and branch on magic, then extension / first byte.

`text-json` includes non-`.json` files whose first non-space byte is `{` or `[` (some `.out` gate dumps). That is a header rule, not a claim that the extension is `.json`.

| class | files | bytes |
|---|---:|---:|
| `binary-pdf` | 1443 | 12132124250 |
| `text-markdown` | 334786 | 5847607615 |
| `text-json` | 147279 | 2907952405 |
| `text-yaml` | 44980 | 2456485379 |
| `text-plain` | 32129 | 1693135404 |
| `text-python` | 34278 | 1449846066 |
| `git-internal` | 23301 | 1161316834 |
| `text-markup` | 3071 | 585289421 |
| `binary-jpeg` | 148 | 131372977 |
| `binary-nul` | 430 | 33023883 |
| `text-other` | 4881 | 25759053 |
| `text-log` | 17918 | 24381761 |
| `text-tsv` | 3249 | 12373133 |
| `text-shell` | 1113 | 5891242 |
| `binary-gzip` | 37 | 499167 |
| `secrets-refusal-unread` | 71 | 31370 |
| `symlink` | 165 | 14751 |
| `empty-file` | 11955 | 0 |
| **sum** | **661234** | **28467104711** |

Header evidence (first ≤70 sanitized bytes, one per class that was header-read):

- `binary-gzip` `r23-run/reports/supplement-opencode-1/scratch/round5-07/pageindex.json.gz` — `..........U.k..(......?._..O.........OWE.W...1.......?........2.....7.`
- `binary-jpeg` `r23-run/reports/supplement-opencode-1/scratch/round5-07/leaf_try_0684.jpg` — `......JFIF.............C................................... $.' ",#..(`
- `binary-nul` `r22-d07/pycache/usr/lib/python3.14/types.cpython-314.pyc` — `+.........yj.,..............................R.t...^.R.I.5...R.R...l.t;`
- `binary-pdf` `r23-run/reports/supplement-opencode-1/scratch/source-recheck-turkic/kincses2019.pdf` — `%PDF-1.4.%.....1 0 obj.<<./Type /Catalog./Version /1.4./Pages 2 0 R.>>`
- `text-json` `cites.json` — `[.{."path": "<SHORT-REF>",."loc": ":100",."sklines": [.121.].},.{."pat`
- `text-log` `d2check.out` — `/home/vgpnk/Projects/shokunin/kotodama-shokunin/examples/culture-d2/ty`
- `text-markdown` `r27-readme-before.md` — `# kotodama-shokunin corpus index..revision: 1.5 ... Round-20 reconcili`
- `text-markup` `r23-run/reports/supplement-opencode-1/scratch/source-recheck-turkic/gb.html` — `<!DOCTYPE html>.<html lang=en>.  <meta charset=utf-8>.  <meta name=vie`
- `text-other` `r22-d04/verify/.gitignore` — `.ufo/state/..ufo/watchdog.log.*.log.__pycache__/./reports/supplement-o`
- `text-plain` `x05-live-shas-d4.txt` — `e7ecd2045ef0e5f9823ce0a067d21b8221b2ceb5e8f5799736981a1c88fa50d3  exam`
- `text-python` `extract_cites.py` — `import re, os, json, sys..src = open('SKILL.md', encoding='utf-8').rea`
- `text-shell` `r27-wait-stable.sh` — `#!/bin/bash.# wait until the D4 packet + holds + all components agree `
- `text-tsv` `r22-d04/verify/reports/round-17/tests/frozen/MANIFEST.tsv` — `gate.gate_sha256.input.input_sha256.exit_code.finding_count.output.out`
- `text-yaml` `x54-baseline-packet.yml` — `name: "D4 culture drill ... round-17 design build (NON-CANON)".canon: `

## Secret-shaped paths (unread)

Walk of record: 71 files, 31370 bytes. Content not opened. Route paths to kagi; do not open them from this note.

Basename counts: `outside-secret.txt` × 69 (8 bytes each; path shape is `packet-links-selftest` / `links-selftest` fixtures inside clones, plus one loose file at the scratch root), `tokenize.cpython-314.pyc` × 1 (26,944 bytes), `token.cpython-314.pyc` × 1 (3,874 bytes).

The two `.pyc` hits are a name-rule over-match: the substring `token` fired on `r22-d07/pycache/usr/lib/python3.14/tokenize.cpython-314.pyc` and `token.cpython-314.pyc`. Path shape is a copied CPython stdlib bytecode cache. Content still unread. Not confirmed secrets.

```
8	0o644	outside-secret.txt
3874	0o644	r22-d07/pycache/usr/lib/python3.14/token.cpython-314.pyc
26944	0o644	r22-d07/pycache/usr/lib/python3.14/tokenize.cpython-314.pyc
8	0o644	r22-o12-regression/closing/tmp/packet-links-selftest/outside-secret.txt
8	0o644	r22-o12-regression/initial/tmp/packet-links-selftest/outside-secret.txt
8	0o644	r22-o12-regression/integrated-candidate/tmp/packet-links-selftest/outside-secret.txt
8	0o644	r22-x04/tmp/checkpoint-a/packet-links-selftest/outside-secret.txt
8	0o644	r23-o11-o12-regression/closing/tmp/packet-links-selftest/outside-secret.txt
8	0o644	r23-o11-o12-regression/initial/tmp/packet-links-selftest/outside-secret.txt
8	0o644	r23-x04/tmp/checkpoint-a/packet-links-selftest/outside-secret.txt
8	0o644	r25-d05/clone/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-o04/vclone/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-o08/vclone/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-o16-o17-regression/closing/tmp/packet-links-selftest/outside-secret.txt
8	0o644	r25-o16-o17-regression/initial/tmp/packet-links-selftest/outside-secret.txt
8	0o644	r25-o18/c4/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-o18/c5/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-o18/clone/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-o18/clone2/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-o18/clone3/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-o18/f2/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-o18/f3/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-o18/f4/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-o18/final/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-run/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-x40/checkpoint-b/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-x40/checkpoint-c/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-x40/checkpoint-d/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-x40/checkpoint-e/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r25-x40/tmp/checkpoint-a/packet-links-selftest/outside-secret.txt
8	0o644	r25-x42/clone/repo/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r26-c47/clone/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r26-o37-o38-regression/closing/tmp/packet-links-selftest/outside-secret.txt
8	0o644	r26-o37-o38-regression/initial/tmp/packet-links-selftest/outside-secret.txt
8	0o644	r26-run/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	r26c/rv3/repo/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	r26c/rvclone/repo/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	r26c/rvclone2/repo/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	r27-o33-o36-regression/initial-unoverlaid/tmp/packet-links-selftest/outside-secret.txt
8	0o644	r27-o33-o36-regression/initial/tmp/packet-links-selftest/outside-secret.txt
8	0o644	r58/checkpoint-b/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	r58/checkpoint-c/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	r58/checkpoint-d/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	r58/checkpoint-e/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	r58/tmp/checkpoint-a/links-selftest/outside-secret.txt
8	0o644	round-26/validation/links-selftest/outside-secret.txt
8	0o644	round-27/validation/links-selftest/outside-secret.txt
8	0o644	x37/clone/repo/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	x37/final/repo/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	x37/neg/repo/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	x37/teeth/argot/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	x37/teeth/gate-input/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	x37/teeth/lessons/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	x37/teeth/v3/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	x37/verify/repo/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	x46/clone/.scratch/round-25/validation/links-selftest/outside-secret.txt
8	0o644	x52/checkpoint-b/.scratch/round-27/validation/links-selftest/outside-secret.txt
8	0o644	x52/checkpoint-c/.scratch/round-27/validation/links-selftest/outside-secret.txt
8	0o644	x52/checkpoint-d/.scratch/round-27/validation/links-selftest/outside-secret.txt
8	0o644	x52/checkpoint-e/.scratch/round-27/validation/links-selftest/outside-secret.txt
8	0o644	x52/tmp/checkpoint-a/links-selftest/outside-secret.txt
8	0o644	x52/tmp/checkpoint-d/links-selftest/outside-secret.txt
8	0o644	x56/clone/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	x56/clone2/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	x56/clone3/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	x56/clone4/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	x56/clone5/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	x56/final/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	x56/final2/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	x64/clone-run/.scratch/round-26/validation/links-selftest/outside-secret.txt
8	0o644	x64/clone-run2/.scratch/round-26/validation/links-selftest/outside-secret.txt
```

## Symlinks (not followed)

165 symlinks. `readlink` only. All targets absolute. Four distinct targets:

- 66 × `/home/vgpnk/Projects/shokunin/kotodama-shokunin/examples/culture-d3/components/04-language.json`
- 33 × `/home/vgpnk/Projects/shokunin/kotodama-shokunin/reports/supplement-opencode-1/scratch/round7-15/outside-target.json`
- 33 × `/home/vgpnk/Projects/shokunin/kotodama-shokunin/reports/supplement-opencode-1/scratch/round7-15/outside-target2.json`
- 33 × `/tmp/d3-outside-probe.json`

Targets were not read. Several point at the live kotodama repo and one at `/tmp/d3-outside-probe.json`. Deleting the links would still be a write, and would touch a live lane. NOT-SAFE.

## Live-lane evidence

```
$ git -C kotodama-shokunin status --porcelain=v1 -b --untracked-files=no
## main...origin/main [ahead 47]
 M examples/culture-d4/components/01-brief.yml
 M examples/culture-d4/components/04-lexicon.yml
 M examples/culture-d4/expected-holds.json
 M examples/culture-d4/packet.d4.typed.yml
 M examples/culture-d4/packet.d4.yml
 M examples/culture-d4/typed-labels.d4.yml
 M tools/gates/typed-pipelines.json
# observed 2026-10-18T15:52:28-03:00. Untracked files were suppressed by the flag.
```

```
$ git -C kotodama-shokunin rev-list --count origin/main..HEAD
49
$ git -C kotodama-shokunin rev-parse HEAD
b95fca1e40f32f7346937ab6426f9ccca60e319f
$ git -C kotodama-shokunin log --oneline -3 origin/main..HEAD
b95fca1 round-27: declare claims D/O/C (register law, pin sweep, register knowledge)
4f09c99 round-26: admit D/O/C — register stratum closes the r17 forecast; r5 pin chain (devin)
1ad491a round-26: declare claims D/O/C (register stratum, r25 remainders, open-question dispositions)
$ git -C kotodama-shokunin check-ignore -v .scratch
.gitignore:6:.scratch/	.scratch
# these four commands observed 2026-10-18T16:48:48-0300
```

Ahead moved 47 → 49 during this census. HEAD moved `1ad491a1a4b0aef9ebdc1861dfb8237727503825` (observed 16:04) → `b95fca1e40f32f7346937ab6426f9ccca60e319f`. The new tip's subject is `round-27: declare claims`. No fetch was run; the ahead count is against the existing `origin/main` ref.

```
$ git -C kotodama-shokunin status --porcelain=v1 -b
## main...origin/main [ahead 49]
 M corpus/README.md
 M examples/culture-d4/components/01-brief.yml
 M examples/culture-d4/expected-holds.json
 M examples/culture-d4/packet.d4.typed.yml
 M examples/culture-d4/packet.d4.yml
 M examples/culture-d4/typed-labels.d4.yml
 M tools/exercise-handoff-e2e.py
 M tools/gates/argot-derivation-gate.py
 M tools/gates/typed-pipelines.json
?? corpus/knowledge/linguistics/register-strata-attestation.md
?? corpus/lessons/round-27.md
?? examples/culture-d4/components/13-register-law.yml
?? reports/round-27/adjacency.md
?? reports/round-27/argot/
?? reports/round-27/audit/
?? reports/round-27/availability.json
?? reports/round-27/entry/
?? reports/round-27/fragment-index-x56.md
?? reports/round-27/gate-tests/
?? reports/round-27/law/
?? reports/round-27/pinsweep/
?? reports/round-27/readme/
?? reports/round-27/report-draft.md
?? reports/round-27/rerun.json
?? reports/round-27/run-validation.py
?? reports/round-27/scope.md
?? reports/round-27/scribe/
?? reports/round-27/validation.json
```

Ledger:

```
$ wc -l souji-shokunin/corpus/knowledge/obsidian-ledger.tsv
1
$ head -c 200 souji-shokunin/corpus/knowledge/obsidian-ledger.tsv
source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote
$ rg -n -F 'kotodama-shokunin/.scratch' souji-shokunin/corpus/knowledge/obsidian-ledger.tsv
LEDGER_NO_MATCH
```

Live writer, not a stale empty:

```
$ rg -n 'mkdtemp\(prefix="r26-o33-"' kotodama-shokunin/reports/round-26/remainders/pin-repoint-check.py
117:    temp = Path(tempfile.mkdtemp(prefix="r26-o33-", dir=str(ROOT / ".scratch")))
```

That line is why 34 top-level `r26-o33-*` directories were empty at walk time (18 at 15:57, 24 at 16:04, 34 in the walk of record). They are process temps. Do not delete them because they are empty.

A reference sweep `rg -l -g '!.scratch/**' -g '!.git/**' '\.scratch' kotodama-shokunin` returned matches in `SCORECARD.md`, `LOG.md`, `corpus/lessons/`, and `reports/round-26/` (output capped at 40 paths; the sweep is not exhaustive). Stale-receipt refs=0 is not established. Decisive failure is the mkdtemp line plus mtimes from today, not the capped sweep.

## What the parent must not do

- Do not remove, prune, or quarantine anything under `kotodama-shokunin/.scratch`.
- Do not treat 16G / 17G / 25.639 GiB as a removal receipt. r1 was 1.9G (r5 seat-51 citation, not re-measured here), r5 was 16G at 15:18, this seat's unique-inode figure at 16:32 is 27,529,965,392 bytes (25.639 GiB).
- Do not open the secret-shaped paths. Two `.pyc` names are likely over-matches; still unread.
- Do not follow the absolute symlinks into the live repo or `/tmp`.
- Do not "clean" the live `reports/supplement-opencode-1/scratch` either. It is outside this tree, gitignored, and owned by a dirty unpushed lane. Out of this seat's write scope.

## If an operator later asks for a cleanup plan

Not authorized now. When the lane is quiet (no dirty tracked files, no unpushed commits the operator still needs, no `r26-o33-*` mkdtemp writer, scratch file count stable across two counts), the byte win is the repeated supplement copies inside scratch clones, then the repeated working-tree clones. Re-run the walk. Do not reuse these counts. Empty `r26-o33-*` dirs are eligible only after the writer is gone and a second look shows they stayed empty — still a receipt decision, not a size decision.

## Top-level table (320/320)

Sorted by summed bytes, then name. `supp_bytes` is the subset under `reports/supplement-opencode-1/scratch/`.

```
bytes	files	dirs	git_dirs	secrets	supp_bytes	purpose	dominant_class	name
8082376254	89392	14771	4	0	6394306816	supplement-corpus-copy	binary-pdf	x58
3576323986	22589	4112	8	8	3197216012	supplement-corpus-copy	binary-pdf	x37
1747466161	86845	12634	42	5	0	nested-git-clone	text-markdown	r58
1301330055	64444	9053	10	2	0	nested-git-clone	text-markdown	x64
922662282	7571	1183	1	1	799288352	supplement-corpus-copy	binary-pdf	x46
877931019	5369	835	0	0	799288352	supplement-corpus-copy	binary-pdf	cold-run-4
840819686	42237	6182	21	5	0	nested-git-clone	text-markdown	r25-x40
706429237	12752	1850	6	0	399644176	supplement-corpus-copy	binary-pdf	r23-run
568885341	7713	1527	3	1	399644176	supplement-corpus-copy	binary-pdf	r26-run
556651745	6994	1193	3	1	399644176	supplement-corpus-copy	binary-pdf	r25-o08
479614163	19382	3464	9	9	0	nested-git-clone	text-markdown	r25-o18
461582257	3197	641	1	0	399644176	supplement-corpus-copy	binary-pdf	r4c
454007626	2901	554	1	1	399644176	supplement-corpus-copy	binary-pdf	r25-run
452990910	2866	539	1	1	399644176	supplement-corpus-copy	binary-pdf	r25-o04
450897169	2772	486	1	0	399644176	supplement-corpus-copy	binary-pdf	r24-run
444100671	2884	463	0	0	399644176	supplement-corpus-copy	binary-pdf	r26-d05
441841514	2729	528	0	0	399644176	supplement-corpus-copy	binary-pdf	audit4
403314574	19705	3196	9	7	0	nested-git-clone	text-markdown	x56
370802167	19027	2675	10	1	0	nested-git-clone	text-markdown	r23-x04
304373305	14318	2887	6	0	0	nested-git-clone	text-markdown	round-23
246639266	11785	2035	5	6	0	nested-git-clone	text-markdown	x52
230885357	11729	1646	6	0	0	nested-git-clone	text-markdown	r23-x10-post-PgX4qG59
225380932	9381	1871	4	3	0	nested-git-clone	text-markdown	r26c
187069131	8918	1347	4	0	0	nested-git-clone	text-markdown	x59
163887242	6805	1297	3	1	0	nested-git-clone	text-markdown	round-26
145099379	6680	1302	3	2	0	nested-git-clone	text-markdown	r22-d07
139352043	6807	1119	3	2	0	nested-git-clone	text-markdown	r26-o37-o38-regression
111419236	4611	843	2	0	0	nested-git-clone	text-markdown	r26-x55-probe
109422125	5815	875	3	3	0	nested-git-clone	text-markdown	r22-o12-regression
108235504	4513	829	2	0	0	nested-git-clone	text-markdown	r26c51
100216632	4435	740	2	0	0	nested-git-clone	text-markdown	x61
99914940	4868	852	2	2	0	nested-git-clone	text-markdown	r27-o33-o36-regression
87815072	4031	793	2	0	0	nested-git-clone	text-markdown	r22-o11-replay.cWR49r
87378221	4343	684	2	2	0	nested-git-clone	text-markdown	r25-o16-o17-regression
84708986	4234	594	2	0	0	nested-git-clone	text-markdown	x60
82769507	4157	640	2	2	0	nested-git-clone	text-markdown	r23-o11-o12-regression
81382142	2956	1032	0	0	0	working-tree-copy-no-git	text-yaml	r24-gates
74427767	3671	496	2	0	0	nested-git-clone	text-markdown	round-22-tie-break
60205884	2612	531	1	0	0	nested-git-clone	text-markdown	r27-d13
56303467	2300	429	1	0	0	nested-git-clone	text-markdown	r26-o39-tw
55661048	2306	430	1	0	0	nested-git-clone	text-markdown	r26-o39-tw3
55646261	2306	430	1	0	0	nested-git-clone	text-markdown	r26-o39-tw4
55560023	2291	422	1	0	0	nested-git-clone	text-markdown	r26-o29-vc
55557082	2291	422	1	0	0	nested-git-clone	text-markdown	r26-o39-tw2
55536743	2287	422	1	0	0	nested-git-clone	text-markdown	r26-o29-clone
55536422	2303	428	1	0	0	nested-git-clone	text-markdown	r26-o29-live
55501084	2288	420	1	0	0	nested-git-clone	text-markdown	r26-o39-clone2
55439832	2289	420	1	0	0	nested-git-clone	text-markdown	r26-o39-ctl
55439832	2289	420	1	0	0	nested-git-clone	text-markdown	r26-o39-ctl2
55439832	2289	420	1	0	0	nested-git-clone	text-markdown	r26-o39-ctl4
55435397	2288	420	1	0	0	nested-git-clone	text-markdown	r26-o29-c2
55435397	2288	420	1	0	0	nested-git-clone	text-markdown	r26-o29-c4
55435397	2288	420	1	0	0	nested-git-clone	text-markdown	r26-o39-clone
55435397	2288	420	1	0	0	nested-git-clone	text-markdown	r26-o39-ctl3
55425045	2289	420	1	0	0	nested-git-clone	text-markdown	r26-o39-ctl5
55420610	2288	420	1	0	0	nested-git-clone	text-markdown	r26-o39-fr
54541384	2191	392	1	1	0	nested-git-clone	text-markdown	r25-x42
54343399	2274	424	1	0	0	nested-git-clone	text-markdown	r26-o29-final
54173026	2284	462	1	1	0	nested-git-clone	text-markdown	r26-c47
54115119	2254	412	1	0	0	nested-git-clone	text-markdown	r26-o29-c3
53800914	2171	389	1	1	0	nested-git-clone	text-markdown	r25-d05
53512458	2217	411	1	0	0	nested-git-clone	text-markdown	r26-o29-final-frozen
53411433	2202	403	1	0	0	nested-git-clone	text-markdown	r26-o29-base
53411433	2202	403	1	0	0	nested-git-clone	text-markdown	r26-o29-frozen
53262558	2138	340	1	0	0	nested-git-clone	text-markdown	r25-x48
49360918	2309	366	1	0	0	nested-git-clone	text-markdown	x64cold
47456440	2162	421	1	0	0	nested-git-clone	text-markdown	r22-d04
47101649	2246	336	1	0	0	nested-git-clone	text-markdown	x55
47058008	2145	421	1	0	0	nested-git-clone	text-markdown	r22-declared-in-r2-whpgj6nt
47002581	2146	419	1	0	0	nested-git-clone	text-markdown	r22-o07-8iaicnio
46836754	2141	420	1	0	0	nested-git-clone	text-markdown	r22-declared-in-final-dj9n7392
46831826	2142	420	1	0	0	nested-git-clone	text-markdown	r22-declared-in.GXeE3A
46689479	2140	423	1	0	0	nested-git-clone	text-markdown	r22-o11-replay.JXu4SU
46689479	2140	423	1	0	0	nested-git-clone	text-markdown	r22-o11-replay.T75tzH
46689479	2140	423	1	0	0	nested-git-clone	text-markdown	r22-o11-replay.U03WLl
46689479	2140	423	1	0	0	nested-git-clone	text-markdown	r22-o11-replay.rHIdab
46598718	2137	418	1	0	0	nested-git-clone	text-markdown	r22-o10-snapshot.iTM6Nv
46595076	2136	418	1	0	0	nested-git-clone	text-markdown	r22-o10-snapshot.5YrOYy
46595076	2136	418	1	0	0	nested-git-clone	text-markdown	r22-o10-snapshot.5m7dYy
46595076	2136	418	1	0	0	nested-git-clone	text-markdown	r22-o10-snapshot.MhMXqN
46595076	2136	418	1	0	0	nested-git-clone	text-markdown	r22-o10-snapshot.PLSFoI
42575885	2062	354	1	0	0	nested-git-clone	text-markdown	r22-x03-final-dyisxutg
41703275	2063	279	0	0	0	working-tree-copy-no-git	text-markdown	r27-r4-src
41268471	2037	285	1	0	0	nested-git-clone	text-markdown	r25-o11-clone2
41155939	2035	283	1	0	0	nested-git-clone	text-markdown	r25-o11-clone
40430153	2015	279	1	0	0	nested-git-clone	text-markdown	r23-x10-Qj1pU4sJ
40000652	1964	271	1	0	0	nested-git-clone	text-markdown	r23-wording
39296589	1960	260	0	0	0	working-tree-copy-no-git	text-markdown	coldrun-b-export
36431417	1938	321	1	1	0	nested-git-clone	text-markdown	r22-x04
35790993	1840	282	1	0	0	nested-git-clone	text-markdown	r22-x03-irb57h5p
12971264	448	142	0	0	0	working-tree-copy-no-git	text-yaml	r25d
12710654	365	190	0	1	0	working-tree-copy-no-git	text-yaml	round-27
6609378	9	1	0	0	0	small-work-dir	text-json	o37
5607716	141	1	0	0	0	small-work-dir	text-yaml	r25-d15
2452241	20	1	0	0	0	small-work-dir	text-json	r26-o39
1438911	37	9	0	0	0	small-work-dir	text-yaml	r27-d
1317649	32	6	0	0	0	small-work-dir	text-python	x18-wart-mirror
957401	10	1	0	0	0	small-work-dir	text-yaml	o18-probe
843799	8	6	0	0	0	small-work-dir	text-yaml	r27-law
842489	49	2	0	0	0	small-work-dir	text-yaml	r25-o1
804293	18	1	0	0	0	small-work-dir	text-yaml	r26-d-reg
781162	21	1	0	0	0	small-work-dir	text-yaml	x38
647809	35	1	0	0	0	small-work-dir	text-json	logs
616827	16	7	0	0	0	small-work-dir	text-python	dbg3-dy_qq80q
605811	16	7	0	0	0	small-work-dir	text-python	dbg-s7guk5en
602541	14	7	0	0	0	small-work-dir	text-python	dbg2-poq02xlp
564855	1	0	0	0	0	loose-session-output	text-json	inventory.json
523212	1	0	0	0	0	loose-session-output	text-json	x63-full-corpus.json
482478	37	3	0	0	0	small-work-dir	text-yaml	r26d
451745	5	1	0	0	0	small-work-dir	text-yaml	r27-d17
451663	17	3	0	0	0	small-work-dir	text-yaml	r25-x47
386432	12	2	0	0	0	small-work-dir	text-json	r27-x49
363166	7	1	0	0	0	small-work-dir	text-yaml	r27-d18
347967	16	2	0	0	0	small-work-dir	text-yaml	r25-d11
341855	9	1	0	0	0	small-work-dir	text-yaml	r25-d21
297160	11	2	0	0	0	small-work-dir	text-json	x62
276312	11	2	0	0	0	small-work-dir	text-json	r26-o29
272042	38	6	0	0	0	small-work-dir	text-yaml	r26-d13
257358	15	1	0	0	0	small-work-dir	text-json	r26-c53c54
203384	85	3	0	0	0	small-work-dir	text-yaml	r26-d21
173746	5	1	0	0	0	small-work-dir	text-yaml	r27-d19
164636	1	0	0	0	0	loose-session-output	text-json	r27-c-corpus-audit.json
158578	1	0	0	0	0	loose-session-output	text-json	sibling-entry-audit.json
153179	10	1	0	0	0	small-work-dir	text-json	x53
130302	1	0	0	0	0	loose-session-output	text-json	x63-control-r19entries.json
122763	20	2	0	0	0	small-work-dir	text-json	x41
119868	1	0	0	0	0	loose-session-output	text-json	r27-runner.json
117587	17	1	0	0	0	small-work-dir	text-markdown	r26-c51
106786	18	2	0	0	0	small-work-dir	text-yaml	r26-d17-d20
98880	1	0	0	0	0	loose-session-output	text-markdown	r27-readme-before.md
96851	23	3	0	0	0	small-work-dir	text-json	r23-o05
95037	1	1	0	0	0	small-work-dir	text-yaml	r24-o3
87656	25	1	0	0	0	small-work-dir	text-log	x50
85259	8	1	0	0	0	small-work-dir	text-yaml	x43
84352	2	4	0	0	0	small-work-dir	text-yaml	round-25
82859	1	0	0	0	0	loose-session-output	text-yaml	x54-baseline-packet.yml
69013	8	1	0	0	0	small-work-dir	text-json	x54
53379	7	1	0	0	0	small-work-dir	text-python	x44
44192	2	1	0	0	0	small-work-dir	text-markdown	r25-c
42565	5	1	0	0	0	small-work-dir	text-json	audit3
38196	1	0	0	0	0	loose-session-output	text-plain	cited_dump.txt
36078	6	1	0	0	0	small-work-dir	text-json	r24-box2b
32215	3	1	0	0	0	small-work-dir	text-python	x07
29293	1	0	0	0	0	loose-session-output	text-json	r27d-battery.out
29292	1	0	0	0	0	loose-session-output	text-json	battery.out
28285	3	1	0	0	0	small-work-dir	text-markdown	x45
26414	1	0	0	0	0	loose-session-output	text-json	x63-baseline-linguistics.json
25863	6	1	0	0	0	small-work-dir	text-json	x51
23159	6	1	0	0	0	small-work-dir	text-python	x08
22846	1	0	0	0	0	loose-session-output	text-json	r27d-census.json
13786	1	0	0	0	0	loose-session-output	text-json	battery-br.out
12125	1	0	0	0	0	loose-session-output	text-json	r26-o29-r25-r4-checker-receipt.json
12113	1	0	0	0	0	loose-session-output	text-json	r25-check.json
12075	1	0	0	0	0	loose-session-output	text-json	cites.json
11688	4	1	0	0	0	small-work-dir	text-json	x57
10588	5	1	0	0	0	small-work-dir	text-log	r27-o39
9945	1	0	0	0	0	loose-session-output	text-log	d2tl-selftest.out
7360	1	0	0	0	0	loose-session-output	text-json	r26-o29-r23-wording-checker-receipt.json
6305	1	0	0	0	0	loose-session-output	text-json	r24-selftest.json
6238	1	0	0	0	0	loose-session-output	text-python	r27-repin-baselines.py
6209	1	0	0	0	0	loose-session-output	text-json	x64-entry.json
6209	1	0	0	0	0	loose-session-output	text-json	x64-final.json
6069	1	0	0	0	0	loose-session-output	text-json	r25-self.json
5541	1	0	0	0	0	loose-session-output	text-json	cecs.out
5277	1	0	0	0	0	loose-session-output	text-json	x63-entry.json
5197	1	0	0	0	0	loose-session-output	text-json	r25-o11-lines.json
5050	1	1	0	0	0	small-work-dir	binary-nul	__pycache__
4913	1	1	0	0	0	small-work-dir	text-json	x63
4727	1	0	0	0	0	loose-session-output	text-json	x39-watchlog.json
4510	1	0	0	0	0	loose-session-output	text-python	x39-watch.py
4372	1	0	0	0	0	loose-session-output	text-json	r58-commands.json
4372	1	0	0	0	0	loose-session-output	text-json	x52-commands.json
4304	1	0	0	0	0	loose-session-output	text-log	d4-gate.out
4304	1	0	0	0	0	loose-session-output	text-log	r25-derived-in.out
4304	1	0	0	0	0	loose-session-output	text-log	x38-typed.out
4205	1	0	0	0	0	loose-session-output	text-python	r27-freeze-d4legs.py
3279	1	0	0	0	0	loose-session-output	text-log	prov.out
3182	1	0	0	0	0	loose-session-output	text-json	r25-x40-commands.json
3056	1	1	0	0	0	small-work-dir	text-json	x05-tamper
3006	1	0	0	0	0	loose-session-output	text-python	r27-lib.py
2855	1	0	0	0	0	loose-session-output	text-log	ng.out
2855	1	0	0	0	0	loose-session-output	text-log	r25d-naming.out
2855	1	0	0	0	0	loose-session-output	text-log	r27d-ncg.out
2677	1	0	0	0	0	loose-session-output	text-log	r25-d2-source.out
2652	1	0	0	0	0	loose-session-output	text-python	r27d-syl6.py
2604	1	0	0	0	0	loose-session-output	text-log	r25-d2-derived.out
2232	1	0	0	0	0	loose-session-output	text-plain	x05-repin-receipt-check.txt
2200	1	0	0	0	0	loose-session-output	text-python	r27d-syl.py
2198	1	0	0	0	0	loose-session-output	text-log	d4-legacy-gate.out
2198	1	0	0	0	0	loose-session-output	text-log	r25-source-in.out
2198	1	0	0	0	0	loose-session-output	text-log	r25d-tpg.out
2198	1	0	0	0	0	loose-session-output	text-log	tpg.out
2198	1	0	0	0	0	loose-session-output	text-log	x38-source.out
2193	1	0	0	0	0	loose-session-output	text-log	replay-r3.out
2057	1	0	0	0	0	loose-session-output	text-python	r27d-syl2.py
2004	1	0	0	0	0	loose-session-output	text-plain	r27d-replay.txt
1948	1	0	0	0	0	loose-session-output	text-python	r27d-syl4.py
1894	1	0	0	0	0	loose-session-output	text-python	r27d-syl5.py
1884	1	0	0	0	0	loose-session-output	text-python	r27d-syl3.py
1869	1	0	0	0	0	loose-session-output	text-log	sai-st.out
1417	1	0	0	0	0	loose-session-output	text-python	dump_cited.py
1371	1	0	0	0	0	loose-session-output	text-json	x39-snapshot-1.json
1323	1	0	0	0	0	loose-session-output	text-python	resolve_cites.py
1305	1	0	0	0	0	loose-session-output	text-log	r27d-ag-fix.out
1086	1	0	0	0	0	loose-session-output	text-log	replay-r22.out
1073	1	0	0	0	0	loose-session-output	text-python	extract_cites.py
1029	1	0	0	0	0	loose-session-output	text-plain	x63-baseline-linguistics.txt
984	1	0	0	0	0	loose-session-output	text-python	r27d-census.py
887	1	0	0	0	0	loose-session-output	text-python	r27-c-insert.py
884	1	0	0	0	0	loose-session-output	text-json	r27-c-readme-sweep.json
790	1	0	0	0	0	loose-session-output	text-log	ag2.out
783	1	0	0	0	0	loose-session-output	text-python	r25d-census.py
733	1	0	0	0	0	loose-session-output	text-shell	r27-wait-stable.sh
724	1	0	0	0	0	loose-session-output	text-plain	x05-table-sweep.txt
697	1	0	0	0	0	loose-session-output	text-plain	x05-live-shas-d4.txt
679	1	0	0	0	0	loose-session-output	text-plain	x05-live-shas-d2.txt
654	1	0	0	0	0	loose-session-output	text-log	phon-d2.out
566	1	0	0	0	0	loose-session-output	text-log	r27d-tp-src.out
566	1	0	0	0	0	loose-session-output	text-log	r27d-tp-typ.out
458	1	0	0	0	0	loose-session-output	text-log	naming.out
423	1	0	0	0	0	loose-session-output	text-json	x64-control-empty.json
402	1	0	0	0	0	loose-session-output	text-log	d3st.out
343	1	0	0	0	0	loose-session-output	text-log	hpst.out
282	1	0	0	0	0	loose-session-output	text-log	nmst.out
276	1	0	0	0	0	loose-session-output	text-log	r27d-ag-typ.out
270	1	0	0	0	0	loose-session-output	text-log	r27d-ag-src.out
268	1	0	0	0	0	loose-session-output	text-log	costume.out
247	2	2	0	0	0	small-work-dir	text-markdown	tmp0vxigyq7
247	2	2	0	0	0	small-work-dir	text-markdown	tmp4m4hztzf
247	2	2	0	0	0	small-work-dir	text-markdown	tmp65fngt8p
247	2	2	0	0	0	small-work-dir	text-markdown	tmp8bcrf9yg
247	2	2	0	0	0	small-work-dir	text-markdown	tmp8bynwzpr
247	2	2	0	0	0	small-work-dir	text-markdown	tmp8im1bcu6
247	2	2	0	0	0	small-work-dir	text-markdown	tmp9j22uo50
247	2	2	0	0	0	small-work-dir	text-markdown	tmpamaovz4g
247	2	2	0	0	0	small-work-dir	text-markdown	tmpaprnjg92
247	2	2	0	0	0	small-work-dir	text-markdown	tmpbg5n0ieb
247	2	2	0	0	0	small-work-dir	text-markdown	tmpc6cm9qey
247	2	2	0	0	0	small-work-dir	text-markdown	tmpdvn9wye5
247	2	2	0	0	0	small-work-dir	text-markdown	tmpiqijk7v2
247	2	2	0	0	0	small-work-dir	text-markdown	tmpkfgutwsv
247	2	2	0	0	0	small-work-dir	text-markdown	tmpl364j3k1
247	2	2	0	0	0	small-work-dir	text-markdown	tmpnrg1jso0
247	2	2	0	0	0	small-work-dir	text-markdown	tmpq3orwncl
247	2	2	0	0	0	small-work-dir	text-markdown	tmptegfs8id
244	1	0	0	0	0	loose-session-output	text-log	phon.out
225	1	0	0	0	0	loose-session-output	text-log	d2st.out
218	1	0	0	0	0	loose-session-output	text-plain	x05-v2-07-check.txt
173	1	0	0	0	0	loose-session-output	text-log	ag-st.out
129	1	0	0	0	0	loose-session-output	text-log	d2check.out
116	1	0	0	0	0	loose-session-output	text-json	coupling-frozen.out
116	1	0	0	0	0	loose-session-output	text-json	coupling.out
108	1	0	0	0	0	loose-session-output	text-log	d3check.out
105	1	0	0	0	0	loose-session-output	text-log	pu-selftest.out
87	1	0	0	0	0	loose-session-output	text-log	craft.out
83	1	0	0	0	0	loose-session-output	text-log	d4check.out
82	1	0	0	0	0	loose-session-output	text-log	d2check2.out
82	1	0	0	0	0	loose-session-output	text-log	x1.out
81	1	0	0	0	0	loose-session-output	text-log	d2tl-check.out
81	1	0	0	0	0	loose-session-output	text-log	r25d-d4tl.out
81	1	0	0	0	0	loose-session-output	text-log	r27d-d4-typed-labels-check-gate.out
81	1	0	0	0	0	loose-session-output	text-log	r27d-tl.out
81	1	0	0	0	0	loose-session-output	text-log	x2.out
75	1	0	0	0	0	loose-session-output	text-log	craftst.out
73	1	0	0	0	0	loose-session-output	text-log	r25d-d4ac.out
73	1	0	0	0	0	loose-session-output	text-log	r27d-as.out
73	1	0	0	0	0	loose-session-output	text-log	r27d-d4-assembly-check-gate.out
55	1	0	0	0	0	loose-session-output	text-log	d3handoff.out
55	1	0	0	0	0	loose-session-output	text-log	handoff.out
31	1	0	0	0	0	loose-session-output	text-plain	r23-x10-postdir.txt
26	1	0	0	0	0	loose-session-output	text-plain	r23-x10-workdir.txt
8	1	0	0	1	0	secrets-refusal-unread	secrets-refusal-unread	outside-secret.txt
0	1	0	0	0	0	loose-empty-output	empty-file	cost-d2.out
0	1	0	0	0	0	loose-empty-output	empty-file	d2selftest.err
0	1	0	0	0	0	loose-empty-output	empty-file	inventory.err
0	1	0	0	0	0	loose-empty-output	empty-file	lex-audit.err
0	1	0	0	0	0	loose-empty-output	empty-file	lex-audit.out
0	1	0	0	0	0	loose-empty-output	empty-file	lex-d2.out
0	1	0	0	0	0	loose-empty-output	empty-file	myth-d2.out
0	0	1	0	0	0	empty-dir	none	o38
0	1	0	0	0	0	loose-empty-output	empty-file	r25-check.err
0	0	1	0	0	0	empty-live-temp	none	r26-o33-1e0jqkz9
0	0	1	0	0	0	empty-live-temp	none	r26-o33-1lvq6it6
0	0	1	0	0	0	empty-live-temp	none	r26-o33-733kn903
0	0	1	0	0	0	empty-live-temp	none	r26-o33-761f7ggr
0	0	1	0	0	0	empty-live-temp	none	r26-o33-939j88jb
0	0	1	0	0	0	empty-live-temp	none	r26-o33-9a12_k_e
0	0	1	0	0	0	empty-live-temp	none	r26-o33-_g0iasi6
0	0	1	0	0	0	empty-live-temp	none	r26-o33-a51v8sda
0	0	1	0	0	0	empty-live-temp	none	r26-o33-bc9yc8nc
0	0	1	0	0	0	empty-live-temp	none	r26-o33-bzw9m57v
0	0	1	0	0	0	empty-live-temp	none	r26-o33-d8o7154r
0	0	1	0	0	0	empty-live-temp	none	r26-o33-drg7_jrg
0	0	1	0	0	0	empty-live-temp	none	r26-o33-e4wv80dz
0	0	1	0	0	0	empty-live-temp	none	r26-o33-ez0hf36m
0	0	1	0	0	0	empty-live-temp	none	r26-o33-hbzzhns4
0	0	1	0	0	0	empty-live-temp	none	r26-o33-hxzepgnj
0	0	1	0	0	0	empty-live-temp	none	r26-o33-i1chwaw4
0	0	1	0	0	0	empty-live-temp	none	r26-o33-ixvsnksr
0	0	1	0	0	0	empty-live-temp	none	r26-o33-jlkxklhi
0	0	1	0	0	0	empty-live-temp	none	r26-o33-nrhzce_s
0	0	1	0	0	0	empty-live-temp	none	r26-o33-o3h3tj6x
0	0	1	0	0	0	empty-live-temp	none	r26-o33-pxq255ur
0	0	1	0	0	0	empty-live-temp	none	r26-o33-r0q24tn2
0	0	1	0	0	0	empty-live-temp	none	r26-o33-r8674dtm
0	0	1	0	0	0	empty-live-temp	none	r26-o33-rtckpl1s
0	0	1	0	0	0	empty-live-temp	none	r26-o33-sx7nwnzg
0	0	1	0	0	0	empty-live-temp	none	r26-o33-t831tfzd
0	0	1	0	0	0	empty-live-temp	none	r26-o33-tboc8lv3
0	0	1	0	0	0	empty-live-temp	none	r26-o33-wwbbu1b3
0	0	1	0	0	0	empty-live-temp	none	r26-o33-xh4kj4nd
0	0	1	0	0	0	empty-live-temp	none	r26-o33-xjn9ujpo
0	0	1	0	0	0	empty-live-temp	none	r26-o33-xunsy59y
0	0	1	0	0	0	empty-live-temp	none	r26-o33-yrker5wc
0	0	1	0	0	0	empty-live-temp	none	r26-o33-yucm7464
0	0	1	0	0	0	empty-dir	none	r27-d20
0	1	0	0	0	0	loose-empty-output	empty-file	sibling.err
0	1	0	0	0	0	loose-empty-output	empty-file	tpg.err
0	1	0	0	0	0	loose-empty-output	empty-file	x63-baseline.err
0	1	0	0	0	0	loose-empty-output	empty-file	x63-full-corpus.err
```

## Method limits

- Read-only. No file under kotodama was modified. This file is the only souji write.
- Header cap 200 bytes. Git internals classed by path, not by magic.
- Secret-shaped basenames not opened, including the likely `token` over-match.
- Symlinks not followed.
- The tree mutated before, during, and after the walk. The closed claim is the walk window, plus the separate mtime pass. It is not a stable inventory of a frozen tree.
- `souji-verify.sh` / `souji-vault-verify.sh` were not executed against this tree, so they could not read `outside-secret.txt`. The receipt conclusion is from the spec plus the commands in this note.
- Nested clone `.git` dirs were not queried (`git log` / `status` inside each clone). They are classed as scratch clones of a live lane, which is enough for NOT-SAFE. Per-clone cleanliness is `to-verify` and would not authorize removal while the parent lane is dirty.

