# F5Enumeration — calibration review

STATUS: OPEN — the F5 enumeration exclusions are not stated consistently across the required authorities: SKILL retains the r19 wording without the exclusions, and Q42 makes exclusion categorical where PROVINCE and the knowledge entry phrase it as possible. L1 should harmonize these claims against implementation evidence before treating the Q42 correction as complete.

## Finding

### Major — F5 exclusion contract is not synchronized across PROVINCE, SKILL and Q42

The current F5 precision paragraph in `PROVINCE.md:147-151` describes eligible readable own-uid candidates and says self/descendants and unreadable/racing entries **can be excluded**. The corresponding `corpus/README.md:319-324` says they **may be excluded**; the appended knowledge correction `corpus/knowledge/process-residue-observations.md:117-122` likewise says self/descendants **can be excluded** and unreadable/racing data are skipped, with no exhaustive-coverage promise. In contrast, `corpus/QUALITY.md:101` (Q42) says the process set is bounded to readable eligible own-uid processes, **excluding** self/descendants and **skipping** unreadable/racing data, without the permissive qualification.

The required SKILL authority remains the older r19 bullet at `SKILL.md:129-134`: it describes own-uid deleted-cwd / vanished-scratch argv/fd findings, says the census never signals and redacts secret-shaped argv, and links the old entry, but does not state the readable/eligible bound, self/descendant exclusions, unreadable/race skips, or non-exhaustive coverage. The adjacent `SKILL.md:136-141` descendant language is about repository-content reader containment, not F5 process enumeration. Thus a consumer reading SKILL gets neither Q42's exclusion contract nor PROVINCE's explicit limit; Q42 also reads as a guarantee stronger than PROVINCE/README/entry.

**One falsifiable oracle change:** add one Q42 documentation-consistency case with a synthetic own-uid enumeration containing the census process, one descendant, one unreadable per-process record, and one PID that disappears between `/proc` listing and record reads. Require the same explicit clause in SKILL, PROVINCE, Q42, README and the knowledge correction: enumeration is limited to eligible readable own-uid candidates; self/descendants may be excluded; unreadable/racing entries may be skipped; output is not exhaustive. The current SKILL wording and the current categorical Q42 wording must fail that case. This is a text-contract check only; it does not claim what the implementation does.

## Observation boundary and residual risk

- `HEAD` observed: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. The six prescribed code files were marked modified in the worktree. Their SHA-256 working-byte observations before their one content read were:
  - `tools/souji-seat-audit.py` — `08a006657357e94d9153a6279c723340d7b586aa806c2355ec206253f09133c6`
  - `tools/souji-rev-pin.py` — `869d399ca1ec2868e9c794e438298a9dfd844eed76e5d477fa38b710f170e49d`
  - `census/round-13/run-verification.py` — `945cf6ecd5f4472c2556eb6f0b26e0a42193268a158cf3a0a8d776c00ef1d0cc`
  - `census/round-14/run-verification.py` — `bde95f972e09de393d32b1aa840bc2282f1677c147399ae7ed24c6558f525f73`
  - `census/round-14/run-targeted.py` — `a0c08e1252df3b7c20cab6eaecaa8222c7eed5f39ba19188eca2da031c5fd3f2`
  - `census/round-14/cache-demonstration.py` — `706200486d0938322a773116ae01377f3a56ec82443415e0d1956cd126c95bd6`
- The source review was read-only. I did not read or execute `tools/souji-proc-census.sh` or its fixture: they are outside this item’s permitted read set. Therefore this finding is a documentation-contract contradiction, not evidence that the implementation includes or omits any particular PID, skips a particular error, or behaves atomically. The behavior asserted by Q42 remains to be established from permitted implementation evidence by the integrator.
- LSP was unavailable: `xd://lsp` returned “No such tool” and the mounted tool list contains no LSP device. Literal grep was used only to locate bounded passages; findings above are grounded in the read text and exact file:line citations, not grep output. No tests, builds, linters, formatters, smokes, target-code execution, or tool installations were performed.