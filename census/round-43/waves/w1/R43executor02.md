# R43executor02

- Candidate: `.ufo/waves/round-43/w1/R43executor02/candidate.py` (copied from committed `f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:tools/souji-freeze-check.py` and partially adapted).
- Behavior implemented in candidate: first duplicate value is evaluated; keys after malformed headings are reported as C0 UNATTACHED-KEY; strict ASCII positive Round syntax rejects malformed values and suppresses dispatch scan; CRLF parsing via `splitlines()`.
- Exact commands run: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:tools/souji-freeze-check.py > /fast/scratch/hyaku/souji-r43/R43executor02/candidate.py` (success); `cp /fast/scratch/hyaku/souji-r43/R43executor02/candidate.py /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43executor02/candidate.py` (success). No score run; no observed SUMMARY.
- Verdict: INCOMPLETE / acceptance not met. Remaining: CONTROL-SYMLINK + refusal; FROZEN-EDITED for control and prereg text; selftest TMPDIR fallback and >=31 cases; score and report exact scoring output. Candidate SHA256 not measured after edits.
- Risk: this candidate has not been scored or otherwise run; do not install it as the operative checker.
