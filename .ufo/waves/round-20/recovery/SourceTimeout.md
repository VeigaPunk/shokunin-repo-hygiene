# SourceTimeout — S094 reopen: exact archived official coreutils timeout locator, quote/version verification

Seat: SoujiR20-2.SourceTimeout-4 (scout, leaf). Subject: reopen S094's locator and verify quote/version fidelity against public official sources. Read-only, source-only, no target execution. No tools installed.

## Observed revision / working bytes

Production read once at working tree `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (HEAD, local=baseline; observed via read-only `git rev-parse`, no index/ref writes):

- `corpus/lessons/round-20.md` sha256 `b69815a46b1ef6f5abaf31c86ce0108d50fd9bf854d4562b8cc447a90e90a7e0`
- `corpus/SOURCES.md` sha256 `199c06c9a57e692d010bda0578ae9f8a47bbe6fe2ef34bdbc802996e3b95a500`

L1 planner edits may land after these reads; the finding below binds to these digests, not to later working-tree bytes.

## Claim under test (S094)

- `corpus/SOURCES.md:114` — locator `https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html`; access record "reopened 2026-10-21 via Wayback 20260919212856id_ capture; page title GNU Coreutils 9.12, §23.6 --kill-after and Exit status"; status mined / 2026-10-21 / on-release / used-by `corpus/lessons/round-20.md`; "supersedes S038 for the current-version locator only".
- `corpus/lessons/round-20.md:45-60` — archived URL `https://web.archive.org/web/20260919212856id_/https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html`, title “timeout invocation (GNU Coreutils 9.12)”, §23.6, quote 1 “Ensure the monitored command is killed by also sending a ‘KILL’ signal.”, quote 2 “124 if command times out, and --preserve-status is not specified”; both ≤25 words.
- Superseded row: `corpus/SOURCES.md:58` (S038) keeps the installed 9.11 info line anchors (15319-15320, 15365; coreutils 9.11-2) as historical.

## Fresh reopen (2026-10-21, reader tool; no target code executed)

| check | observed | verdict |
|---|---|---|
| Capture exists at the exact cited timestamp | CDX row: `org,gnu)/software/coreutils/manual/html_node/timeout-invocation.html 20260919212856 … text/html 200 KCU6A3D33DFZVGKP3EEHV4RDUQMMY5MA 4376` — it is the newest capture (next-oldest 20260713095949, digest `UJ3JR7GUCC5Y3PUHD7LZIFCWZHIXTUZ3`); the `id_` fetch served original bytes, not a nearest-redirect | pass |
| Page title/version | `<title>` and meta description: “timeout invocation (GNU Coreutils 9.12)” | pass |
| Section number | heading “23.6 `timeout`: Run a command with a time limit” | pass |
| Quote 1 exactness | body: “Ensure the monitored *command* is killed by also sending a ‘`KILL`’ signal.” — identical after stripping makeinfo markup; 12 words ≤25 | pass |
| Quote 2 exactness | Exit status block, verbatim: “124 if command times out, and --preserve-status is not specified” (lowercase “command” as quoted); 10 words ≤25 | pass |
| Version currency at reopen | ftp.gnu.org/gnu/coreutils/: `coreutils-9.12.tar.xz` 2026-09-14 11:38 (9.11: 2026-04-20); no 9.13+ row exists, so 9.12 is the current release on 2026-10-21. Capture date 2026-09-19 is five days after the 9.12 release; the prior capture-generation digest (`UJ3JR7…`, 2026-04-20→07-13) matches the 9.11-era page, so the archived bytes are the 9.12-era revision | pass |
| Scope discipline (“not descendant containment or reap authority”) | The page documents only --kill-after (secondary KILL after the initial signal) and exit statuses; nothing grants containment/reap authority. Its --foreground paragraph even states “any children of *command* will not be timed out” in that mode | pass |
| Supersession convention | S094 records the S038 supersession in its own row; S038's row is unchanged and stays historical (9.11 info line anchors) — “for the current-version locator only” is honored; no old digest relabelled as a new observation | pass |
| Live canonical URL | `https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html` fetch timed out from this host — same recorded failure mode as S043/S065/S038; the archived capture is the operative access path, matching the access record | consistent |

## Findings

1. **Verified (source analysis + fresh public reopen):** S094's archived locator is authentic, exact (not a redirected/nearest timestamp), and serves the GNU Coreutils 9.12 page; both quotes are character-exact after markup stripping and within the ≤25-word discipline; §23.6 holds; 9.12 was released 2026-09-14 and remains the newest release, so “current-version locator” was true at admission and remains true at this reopen. No falsifying discrepancy found.
2. **Precision nuance (not an error):** the page makes the quoted exit-124 line and the --kill-after KILL case distinct outcomes — the same page adds “137 if command or timeout is sent the KILL(9) signal (128+9)” and “In the case of the ‘KILL(9)’ signal, `timeout` returns with exit status 137”. S094's wording keeps them separate (“--kill-after sends a subsequent KILL signal; timeout exit124 applies when command times out without --preserve-status”), but any future oracle that consumes “exit124” and “--kill-after” together must discriminate these cases.
3. **Transcription artifact (cosmetic):** the lesson file renders spacing-stripped text throughout (“GNU Coreutils9.12”, “Opened on2026-10-21”); the actual title contains the space (“Coreutils 9.12”). File-wide rendering artifact, not a content defect.
4. **Oracle gap + one concrete change (the requested counterexample/oracle change):** the version attribution rests solely on the node page `<title>` inside one Wayback snapshot, and the S094 access record stores no capture identity — no CDX digest, no byte digest of the `id_` capture. Both recorded quotes are version-invariant across capture generations (CDX groups 2026-02→04 captures under `XWQOMO2H…` = 9.10-era, 2026-04→07 under `UJ3JR7…` = 9.11-era, all carrying the same body sentences). Concrete counterexample: a later recheck that silently resolves `web.archive.org/web/20260713095949id_/…` (an existing, older capture) would pass both quote checks verbatim and only the title — which lives in lesson prose, not in SOURCES — would catch the 9.11 mis-attribution. Oracle change: add to S094's access record the capture identity — exact timestamp `20260919212856` plus CDX digest `KCU6A3D33DFZVGKP3EEHV4RDUQMMY5MA` (or sha256 of the raw `id_` bytes) — and make the on-release recheck fail when the served capture's identity differs, so a repointed timestamp cannot pass quote-only verification.

## Evidence classification

- Fresh execution: public reads of the Wayback `id_` capture, the CDX index, ftp.gnu.org listing, and the failed live gnu.org fetch, all on 2026-10-21.
- Source analysis: `corpus/SOURCES.md:58,114`, `corpus/lessons/round-20.md:45-60` at the digests above.
- Inference: none required beyond the stated capture-generation digest grouping (CDX digest identity of older captures vs release dates, labeled above).
- Historical receipts: S038's installed 9.11 info anchors (`corpus/SOURCES.md:58`) left untouched per supersession-for-locator-only.

STATUS: no blocker. S094 verified as claimed; recommendation limited to the single oracle change in finding 4.
