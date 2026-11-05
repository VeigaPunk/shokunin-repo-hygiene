# S62ExecCandidate — findings (round 62, w1, claim C1)

Delivered: `.ufo/waves/round-62/w1/S62ExecCandidate/` (candidate bytes, `candidate.patch`, `candidate.sha256`, `rows-candidate.txt`, `rows-base.txt`, `report.md`, r60 logs, receipts).

- Candidate patch sha256: `233bef014be55c841b8cda168c93b06254ae7c59f6a2d364d4309f574843992b`
- Candidate file sha256: `9fb55f356aa256475d08f4b82d7132b1ce200a30f0dc26fec17eae969df0ec9b`
- Diff: `tools/souji-receipt-write.py`, +18 / −0, single file.

r60 fixture: candidate `pass=8 fail=0` (rc 0), base `pass=8 fail=0` (rc 0); both controls rejected.

Rows (candidate): A accept (rc 0), B accept (rc 0), C refuse `lane worktree is dirty`, D/E/F/G refuse `RECEIPT-INDEX-FLAG-CONCEALED` (tags S, h, S, S).
Rows (base): A accept, B accept, C refuse, D/E/F accept (3 forgeries), G refuse `instrument differs`.

No deviation from the frozen design. Limits: index-tracked paths only; TOCTOU window between flag check and receipt write; counter's own scoring not run by this seat. Tools installed: none.

Integration: L1 applies `candidate.patch` (or copies `souji-receipt-write.candidate.py`) into `tools/souji-receipt-write.py` after WAVE-DONE.
