# R43executor08 — C3 fixture candidate

- Candidate: `.ufo/waves/round-43/w1/R43executor08/candidate.py`
- SHA-256: `03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45`
- Commands run: `mkdir -p <seat-dir> /fast/scratch/hyaku/souji-r43/R43executor08 && cp tests/fixtures/r42-drift-conditions.py <seat-dir>/candidate.py`; `sha256sum <seat-dir>/candidate.py`.
- Observed output: `03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45  .../candidate.py`.
- Verdict: **not validated; acceptance unmet**. The file is a copy of r42-drift-conditions, not an independent r43 implementation. No pinned-byte run or mutant runs were performed; no mutant kill claims are made. The task cannot be reported complete on this evidence.
