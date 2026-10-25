## Status
STATUS: PARTIAL — exact after-census recipe delivered; final round acceptance checks remain unrun/unverified by this seat.

## Evidence
- Read first: `census/round-28/records/preregistration.txt`, lines 5–9 and 11–24; frozen C1/C2/C3 targets include F4=6, registry rows=138, landing findings=0, dirty waves=0, fixture cases=6/pass=6, and source-census validation rc=0.
- Read `corpus/QUALITY.md:141` and `:143`; Q57 command already points at `census/round-28/q57-sites.txt`, Q59 wording still contains `knowledge-registry` as criterion text.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → `0c96332932e66bbaf9cf1c246091d3275a0ab612` (observed workspace revision; preregistration base is `3a2a80d0d18940a5e352ebc526da22a57dad83c4`).
- `grep -cE '^ground: F4' corpus/knowledge/*.md | cut -d: -f2 | paste -sd+ | python3 -B -c 'import sys; print(sum(map(int,sys.stdin.read().strip().split("+"))))'` → `4` (substitute arithmetic because `bc` is not installed; requested exact `bc` recipe is preserved but not run successfully).
- `grep -cE '^\\|[[:space:]]*S[0-9]{3,}[[:space:]]*\\|' corpus/SOURCES.md` → `135`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain=v1 --untracked-files=all | awk '$2 ~ /^\\.ufo\\/waves\\// {n++} END{print "ufo_waves_lines=" n+0}'` → `ufo_waves_lines=169` (dirty state; no cleanup performed).
- `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh --help` printed usage/documentation; this was not validation. Recipe calls the script's documented `validate` mode.
- Written delivery: `census/round-28/records/after-recipe.md`.

## Findings
1. The exact six-command recipe with specified expected values is in `census/round-28/records/after-recipe.md`; expected outputs are explicitly targets, not asserted observations.
2. C2 counters observed here remain below target: F4=4 (fallback sum due to missing `bc`) and SOURCES rows=135. Current `corpus/README.md:42` includes two r28 paths, while `corpus/knowledge/` listing showed neither r28 entry at observation time.
3. C3 was not verified: the dirty-wave count was 169; `census/round-26/waves/` and `census/round-27/waves/` were absent at observation time; capture tool and fixture were absent at observation time. This report does not claim completion.
4. No source claims beyond local contract/repository state are made.

## Attack log
- None filed. The unavailable `bc` command is a tooling limitation, not an attack on the frozen counter; no predicate, target, or case set was changed.
