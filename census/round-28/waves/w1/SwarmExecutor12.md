## Status
STATUS: PARTIAL — search-log draft delivered; L1 integration and C1/C2/C3 completion are outside this seat.

## Evidence
- Revision observed: lane HEAD `0c96332932e66bbaf9cf1c246091d3275a0ab612` (`round-28: frozen preregistration + before receipts + do-nothing controls`), branch `HEAD`; frozen base in preregistration is `3a2a80d0d18940a5e352ebc526da22a57dad83c4`.
- Opened frozen contract first: `census/round-28/records/preregistration.txt` lines 1–9; search-log requirement is scoped to two round-28 bounded searches.
- Live fetch command executed: `curl -fsSL -o {open,rename,fsync,git-fetch-zh-hans}.html <official URL>` in `/var/tmp/souji-r28-SwarmExecutor12/`, all rc 0. POSIX sha256: open `57b770918aa3e0c25186972675df8c96da119cf4b973335ed4487405e260dc3a`, rename `06671610134b0a52cdf4dcdaf382f72fef85ef51088b8a52b8679c7f03829318`, fsync `5c2975abbb2d65fcad92a4da5241f4f4001f0e5d8cf57f752d9486073ca49747`; all three match the W1 `snapshots/` copies (hash values observed in this run).
- Fetched zh-Hans snapshot sha256: `a7f4742d99fd515f1811a1abd830a61840939ebe3e12cf1e6792662181b574042`; output lengths: open 40401, rename 26407, fsync 10474, zh-Hans 156713 bytes.
- Located source output: open lines 101–104, 209–210; rename lines 82, 246–247; fsync lines 89–97; zh-Hans lines 1343, 3112–3117. Quotes are recorded in the draft.
- Observed `git --version` = `git version 2.56.0`; lane counts at observed revision: SOURCES rows 135, grounded F4 4. Workspace `git status` reported 26 entries, of which 11 are `.ufo/waves/`.
- Delivery: `census/round-28/records/searchlog-draft.md` (4509 bytes), with two prose PRISMA-inspired entries, identified/screened/included/excluded counts, stop rationales, URLs, snapshot digests, located quotes, and the S119 bounded negative sweep.

## Findings
1. **F4 source search:** official POSIX pages were fetched on 2026-10-25; the draft records 3 identified, 3 screened, 3 included, 0 excluded. Location: `census/round-28/records/searchlog-draft.md`, section 1. Evidence from opened bytes: Open Group Issue 8 header at `open.html` lines 25–26; atomic O_EXCL rule at lines 101–103; rename unaffected/atomic rules at `rename.html` lines 82 and 246–247; fsync durability/null implementation at `fsync.html` lines 89–97.
2. **S119 decision-time pin:** the captured official zh-Hans page reports git-fetch last updated 2.56.0 at line 1343 and the switch/default-on text at line 3117. This meets the documented pin/quote/version-alignment flip condition relative to observed host Git 2.56.0. The draft records 1 identified, 1 screened, 1 included, 0 excluded and ADMIT as the C2 seat's intended S215 decision. Location: `census/round-28/records/searchlog-draft.md`, section 2.
3. **No unrelated implementation performed:** no lane source, registry, staged package, index, jj state, wave receipt, or external repo was changed. No checks/build/tests were run.

## Attack log
None.

Report: `.ufo/waves/round-28/w1/SwarmExecutor12.md`
