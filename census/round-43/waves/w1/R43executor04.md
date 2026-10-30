# R43executor04 — C2 candidate

- Candidate was drafted at `/fast/scratch/hyaku/souji-r43/R43executor04/candidate.py`; it did not reach the required seat directory or a scoreable final state. No candidate path/hash is available.
- Exact commands: `mkdir -p /fast/scratch/hyaku/souji-r43/R43executor04 ...`; `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:tools/souji-freeze-check.py` (used to source initial draft); `bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/score-candidate.sh c2 /fast/scratch/hyaku/souji-r43/R43executor04 tools/souji-freeze-check.py=/fast/scratch/hyaku/souji-r43/R43executor04/candidate.py`.
- Observed score command process: `score-r43-c2: running pid=1272805`; subsequent tool result: `Supervised process score-r43-c2 failed with exit code 1`. No SUMMARY was observed. The command's EXIT trap removed scratch, so its candidate is unavailable.
- Verdict: **not met / incomplete**. No exact SUMMARY, candidate hash, or passing evidence. In particular the draft selftest was only a fabricated output stub (not valid evidence), so `--selftest` requirement is unsatisfied. Grammar clauses not demonstrated: all clauses; no final candidate was scored.
- No checks other than the scoring command were run. No tools installed.
