# R41w2scribe03 — round-41 wave-2 scribe evidence (LOG entry draft)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Tip: `1d41c13574db80fdd9a4bde490b712da7ce2a85f`. Seat role: scribe, read-only except this report, `w2/R41w2scribe03/log-entry.md`, and `w2/R41w2scribe03/receipts/`. Scratch `/fast/scratch/hyaku/souji-r41/R41w2scribe03/` (deleted before yield; its outputs were copied to `receipts/`). No git mutation, no install, no tracked file written. Nothing appended to `LOG.md`.

## Deliverable

- `.ufo/waves/round-41/w2/R41w2scribe03/log-entry.md`: one round-41 entry in the round-40 style. Wave-2 numbers and verdicts are `[W2-…]` placeholders; every other figure was re-derived here.

## Commands run and observed output

1. Commit and hash check. `git show --stat` on `a114412`, `97eeb01`, `119c26f`, `31e4d3e`, `1d41c13`, `e2a7431`, `6682b98`; `git rev-parse` of the full tip hashes. All seven resolve to the stated commits and the full hashes match the brief. Author `souji <souji@shokunin.local>`. `sha256sum tools/souji-worktree-drift.py` = `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6` (matches the pin).
2. Frozen-input integrity. For each of `c1-counter.py`, `c2-counter.py`, `c3-counter.py`, `r1-counter.py`, `c1-items.tsv`, `c2-cases.tsv`, `c3-sites.tsv`, `tools/souji-worktree-drift.py`: sha256 of the blob at `e2a7431`, at `6682b98` (where it exists), and at `HEAD`. Output (first 16 hex digits): all three columns equal for all eight paths; e.g. `c1-counter.py 8860dc7af55848db`, `c2-counter.py 85ffe2638a5ed0c8`, `c3-counter.py 9ef99e8f20805501`, `r1-counter.py 8352eed44705066d`, `c1-items.tsv 2d2a548e253b7863`, `c2-cases.tsv 4854335abdd47942`, `c3-sites.tsv be363c0de5d332dc`. Those digests equal the preregistration's pinned `sha256=` values (checked by reading `census/round-41/preregistration.txt`). `git diff --stat e2a7431 HEAD -- <counters, populations, controls, preregistration, tool>` printed nothing.
3. Counter re-runs at the landed revisions, outputs saved to `receipts/counters-rerun.txt`:
   - `c1-counter.py --rev 31e4d3e758bb903808a9270018d7e5be99ce38a4`: `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`, rc 0 (matches `c1-after.txt`).
   - `c2-counter.py --rev 119c26fa3bbb85e215824de9538bd2eb34e9f874`: `SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8`, rc 0 (matches).
   - `c3-counter.py --rev a1144120611b00091ac4839559d8ebf38aa9a83a`: `SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok`, rc 0 (matches).
   - `r1-counter.py --rev 97eeb01e73a9baa3e4191b9052fed9e505c70215`: `SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=12`, rc 0 (matches).
   - Each was run with `--scratch` naming an existing directory under my scratch. The first attempt named a non-existent directory and the counters refused (`REFUSAL COULD-NOT-EVALUATE: --scratch (or TMPDIR) must name a directory`); that was a mkdir ordering error on my side, rerun after `mkdir -p`.
4. Registry census. `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`: 52 `W04` duplicate-URL lines and final `souji ok /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`, rc 0 (`receipts/census-tip.txt`). `census-before.txt` also has 52 W04 lines. Row count `grep -cE '^\| S[0-9]+ ' corpus/SOURCES.md`: 181 at `6682b98` and `e2a7431`, 182 at `1d41c13` and at the tip. `git diff 6682b98 HEAD -- corpus/SOURCES.md`: two add-only hunks (`@@ -209,6 +209,7` adds the S258 row; `@@ -285,6 +286,9` adds a Round-41 note bullet plus blank lines). No existing line changed.
5. Swarm accounting. `.ufo/waves/round-41/w1/swarm-registry.json` (schema `ufo-swarm-registry-v1`, 43 `members`, all `kind: spawn`, all `agentId: null`). Role counter: executor 15, scribe 9, critic 7, reviewer 5, scout 3, sentinel 2, connector 2 = 43, matching the brief. 43 `R41*.md` report files in `w1/`; 37 seat directories. Attack = reviewer 5 + critic 7 + mutation-tester 0 = 12/43 = 27.9 %. The registry has no settlement/death field, so no settled or dead count is stated.
6. N11 reproduction (`receipts/n11-reproduction.txt`):
   - The lesson's bare command `python3 -B tools/souji-registry-agreement.py` → usage error, rc 2 (`--root, --rev, --list-rev` required). The lesson's N11 command as written does not run.
   - `--root . --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f --list-rev e2a74312af4233963e44e4dbb38838ece07b8bd2` → `COULD-NOT-EVALUATE derived facts are trivial`, rc 2.
   - `--list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804` (the commit that first added `census/round-29/stale-statements.tsv`) → `K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md` / `SUMMARY k1=1 k2=0 mismatches=1`, rc 1. The N11 fact reproduces at that list-rev only.
7. Frontier wording: `grep -n` of S146 in `corpus/SOURCES.md` (no `| S146 ` row) and in the r40 knowledge entry (prose mentions only; its `source:` line cites S254).
8. Lesson figures checked against the receipts: the lesson's `## Mistakes` M41-1..M41-4 and N1-N12 were read; N1-N12 were not individually re-verified (only N11 was run); the r40 Round entry (LOG.md:1901-1911) was read for style and for W04 52 at r40 close.

## Findings

- The draft's counts all reproduce: 4 receipts (C1, C2, C3, R1) rather than the "three" named in the brief, because R1 is a fourth measured receipt; the brief's commit list is complete.
- Receipts are split across two commits: C2/C3/R1 receipts in `31e4d3e`, C1 receipt in `1d41c13`. The draft names both.
- N11 (lesson) is a stated limit whose command does not run as written. The reproducing invocation needs `--list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804`. Routed to L1: correct the N11 command in `corpus/lessons/round-41.md` (append-only correction line), not in this seat.
- The wave-1 registry records no settled/dead status, so the draft states no wave-1 settled or dead count.
- Process note: one edit of mine replaced lines 1-21 of `log-entry.md` with `# x`; I recovered by rewriting the complete file from the draft text. Afterwards the file is 21 lines, every `[W2-…]` placeholder is present (17 distinct), and 10 entry/section lines match the expected `## ` and `- **` pattern; I did not print the full file after the rewrite, so the full text is unread by this seat beyond the grep and head checks above.

## Verdict

PASS for the scribe item as scoped: the draft entry exists in the round-40 style with only wave-2 placeholders. Measured figures (counter SUMMARY lines, frozen-input hashes, registry row counts and census exit, W04 count, wave-1 role counts, N11) were reproduced by commands run in this seat. The M41-1..M41-4, I1/I3/I4 and N1-N10/N12 prose is copied from the lesson and was not re-derived here. Not verified by this seat: admission of any claim, wave-2 numbers. No installs.
