# R43executor09 — C3 tool candidate

Verdict: candidate implements N10 refusal for an existing leaf symlink at `--json`; both specified prior fixture runs passed, all frozen anchors remain exactly once, and the direct probe returned the required refusal/exit 2. Evidence below is from the candidate and frozen lane instruments; no lane source was modified.

Candidate: `.ufo/waves/round-43/w1/R43executor09/candidate.py`
SHA-256: `ff26f3da23b34f072fe22ce0aef3e73c197cfa6efd5b742a028c21bbfe9bf097`

Exact evidence command (anchor audit):
```sh
python3 -B -c 'import ast, pathlib, collections; p=pathlib.Path("/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/c3-counter.py"); t=ast.parse(p.read_text()); ns={}; exec(compile(t,str(p),"exec"),ns); b=pathlib.Path("/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43executor09/candidate.py").read_text(); anchors=[m[1] for m in ns["MUTANTS"]]+[e[1] for e in ns["EQUIV"]]; counts=[b.count(x) for x in anchors]; print("anchors total=%d exact_once=%s min=%d max=%d"%(len(anchors),all(n==1 for n in counts),min(counts),max(counts)))'
```
Observed: `anchors total=22 exact_once=True min=1 max=1`.

Two prior fixture commands and observed results:
```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r42-drift-conditions.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43executor09/candidate.py --work /fast/scratch/hyaku/souji-r43/R43executor09/work
```
Observed: `SUMMARY cases=13 pass=13 fail=0` (all 13 case lines PASS).
```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r41-refusal-sites.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43executor09/candidate.py --work /fast/scratch/hyaku/souji-r43/R43executor09/work
```
Observed: `SUMMARY probes=21 pass=21 fail=0` (all 21 probe lines PASS).

Refusal probe setup/command: under `/fast/scratch/hyaku/souji-r43/R43executor09`, made an empty `root/repo`, a record containing `REPO<TAB>repo<TAB>regs=1<TAB>prunable=0` and matching `TOTAL`, and `json-link` symlinked to `target.json`; then ran:
```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43executor09/candidate.py --root /fast/scratch/hyaku/souji-r43/R43executor09/root --record /fast/scratch/hyaku/souji-r43/R43executor09/record.tsv --json /fast/scratch/hyaku/souji-r43/R43executor09/json-link
```
Observed stderr: `REFUSAL JSON-TARGET-SYMLINK: /fast/scratch/hyaku/souji-r43/R43executor09/json-link is a symlink`; observed exit: `2`.

Risks/limits: only the two prior fixtures listed above were exercised here; this report does not claim the full C3 counter target or all nine prior fixtures. No tools were installed. Scratch was removed after the probe.