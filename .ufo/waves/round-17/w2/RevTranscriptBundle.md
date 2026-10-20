STATUS: DONE — r16 transcript bundle verified end-to-end at ddb7347 (144/144 byte-identical to /var/tmp/souji-r16 originals; 65/79 counts and name-level bijection vs r16 specs; --check OK exit 0); no major findings; 3 minor + 1 informational findings on census/round-17/transcript-manifest.py itself.

Axes: (1) bundle preservation fidelity (repo vs /var/tmp originals vs specs), (2) manifest coverage completeness (self, modes, extras), (3) checker soundness/calibration.

## Evidence (all run at lane /home/vgpnk/Projects/shokunin/souji-shokunin; worktree byte-identical to ddb73474433977ff54b015ac3e77669ff2537353 for census/round-16, census/round-17, .ufo/waves/round-16 — `git diff --stat ddb7347 -- <paths>` empty; HEAD is d7e648d = ddb7347 + preservation record)

1. ALLOWED-EXEC check: `python3 census/round-17/transcript-manifest.py --check census/round-16/transcripts` → `check OK: 144 files verified`, exit 0.
2. ALLOWED-EXEC cmp: looped all 144 manifest relpaths, `cmp -s <repo>/census/round-16/transcripts/$rel /var/tmp/souji-r16/transcripts/$rel` → `compared=144 bad=0`. /var/tmp/souji-r16/transcripts/{w1,w2} exist; glob listing shows exactly 65 (w1) and 79 (w2) files, so no tmp-side extras either (cmp proved every manifest path present, counts equal → bijection).
3. Counts vs r16 specs: `jq '.items|length' .ufo/waves/round-16/w1-spec.json .ufo/waves/round-16/w2-spec.json` → 65, 79. Name-level: `diff <(jq -r '.items[].name' <spec> | sed 's|^|w1/|;s|$|.txt|' | sort) <(grep -E '  w1/' census/round-16/transcripts/MANIFEST.sha256 | cut -c67- | sort)` → identical for BOTH waves ("w1: spec items == transcript names", "w2: spec items == transcript names"). Every spec seat has exactly one transcript and vice versa.
4. Manifest hygiene: 144 lines = 65 `w1/` + 79 `w2/` + 0 other; `cut -c67- | LC_ALL=C sort -c` → sorted; `uniq -d` → no duplicate paths; format `<64 lowercase hex>  w1/Seat.txt` (two spaces) confirmed on raw lines.
5. Set equality: `git ls-tree -r --name-only ddb7347 census/round-16/transcripts` (145 entries) == manifest's 144 + MANIFEST.sha256 itself (diff clean). No landed file outside the manifest, none missing.
6. sha256sum interop: `sha256sum -c MANIFEST.sha256` (in bundle dir) → all OK, exit 0.
7. Tree modes: `git ls-tree -r ddb7347 census/round-16/transcripts | awk '{print $1}' | sort | uniq -c` → `145 100644` (no symlinks 120000, no executables). transcript-manifest.py itself is landed 100755, consistent with its census/round-17 siblings.

## Answers to the four named questions

- **Self-coverage: NO.** MANIFEST.sha256 has no entry for itself (unanchored `grep 'MANIFEST'` → 0 matches) and is excluded by design in both directions (census/round-17/transcript-manifest.py:39-40; docstring :11-12). Unavoidable for a self-digest; residual risk is that manifest corruption is caught only by strict parsing (digit corruption → hash mismatch, exit 1; structural corruption → unparseable, exit 2) plus git history — not by a detached signature.
- **File modes: NOT covered.** Record format is `sha256␣␣relpath` only (:52-56 build_lines, :86 parse_manifest_line); a chmod in the bundle passes --check. No exposure today: all 145 tree entries are 100644 and nothing in the bundle is executable (the 100755 r17 evidence tools live outside the bundle). If mode preservation ever matters, the manifest format would need a mode column or a companion record.
- **Extra files: YES, detected both directions.** Manifest-listed but missing → `missing:` (:122-124); on-disk regular file not listed → `extra:` (:136-139); exit 1 either way, matching docstring :14-16. Blind spot: extra *non-regular* entries (symlink/fifo) are silently ignored, see F1.
- **Counts 65/79: CONFIRMED** at both the count level (`.items|length` = 65/79) and the name level (exact per-wave bijection, item 3 above).

## Findings by severity

No major findings. Bundle data claims all hold as landed.

- **F1 (minor, doc/behavior contradiction) — census/round-17/transcript-manifest.py:41 vs :11-12.** Docstring says non-regular entries "(symlinks, sockets, fifos) are ignored in both directions", but `iter_regular_files` filters with `os.path.isfile(full)`, which FOLLOWS symlinks: a symlink→regular file inside the bundle is enumerated and hashed as if regular (and flagged `extra:` if unlisted). Conversely a planted fifo/symlink-to-dir is silently invisible to `--check` — no error, no `extra:` line. No effect on this bundle (zero non-regular entries, item 7). Smallest fix: `if os.path.islink(full) or not os.path.isfile(full): continue` — and decide whether non-regular on-disk entries should at least be reported as extras rather than skipped silently.
- **F2 (minor, soundness) — census/round-17/transcript-manifest.py:117.** `listed[rel] = digest` silently overwrites duplicate relpaths (last wins): an earlier line for a re-listed path is never verified, and the OK message prints `len(listed)` (:144), so a duplicated line undercounts without failing. Smallest fix: reject duplicate rel in the parse loop (`if rel in listed: error`).
- **F3 (minor, format compliance) — census/round-17/transcript-manifest.py:120,137 vs :10-11.** The declared LC_ALL=C line order of MANIFEST.sha256 is never enforced by `--check` (it sorts for its own iteration only); a shuffled manifest passes. Integrity is unaffected (each line self-verifies); only format conformance is unchecked. Smallest fix: compare the raw non-empty line sequence to its C-sorted self, or drop the sort claim from the format spec.
- **F4 (informational, write-path edge) — census/round-17/transcript-manifest.py:72-76.** A stale `MANIFEST.sha256.tmp` left by a crashed `--write` is a regular file and would be enumerated into the NEXT manifest, then left on disk as a listed member. Smallest fix: skip `*.tmp` in `iter_regular_files` or stage the tmp file outside the tree.

## Residual risk and verification gaps

- Mutation-testing the checker (inject extra/mismatch/missing/duplicate on a /var/tmp copy) was NOT run: my ALLOWED-EXEC bounds me to the exact named `--check` on the real bundle plus cmp; F1–F4 rest on code reading of the full 165-line file (lines 1-165 read).
- `/var/tmp/souji-r16/transcripts` originals' own provenance is not authenticated here — I verified identity with the landed bundle, not that the tmp copy is the true r16 capture; landed-blob integrity is nonetheless transitively pinned by the clean `--check` (all 144 digests verified against the committed MANIFEST.sha256, itself git-tracked at ddb7347).
- d7e648d (HEAD) adds only the preservation record; it does not touch census/round-16/transcripts or the checker (empty diff vs ddb7347 on all reviewed paths).
- Tooling directive: no installs or upgrades performed (nothing needed; pacman paused host-wide per operator note).

Verdict: **holds** — the landed bundle claim (144 files = 65 w1 + 79 w2, MANIFEST.sha256 checked, byte-preserving) is true as measured; checker findings F1–F4 are minor hardening items for L1 to schedule, none block the round.
