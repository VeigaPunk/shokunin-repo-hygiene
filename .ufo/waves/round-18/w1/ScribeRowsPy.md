STATUS: DONE — one SOURCES row (S064) drafted for the C1 fixture session fix from the Python subprocess docs, with two located quotes; no existing row changed.

# ScribeRowsPy — round 18, wave 1 (operability, C1)

Scope: draft one SOURCES row for the C1 fixture session fix (`start_new_session=True` plus `os.killpg` on timeout). Not landed: SOURCES.md is not edited by this seat (L1 integrates).

## Access record

- URL: https://docs.python.org/3/library/subprocess.html
- Accessed: 2026-10-20 (live read, `read` tool, text/html)
- Served as: "subprocess — Subprocess management — Python 3.15.0 documentation" (no last-updated line in the served text)
- Host Python is 3.14 (per S050); the quoted behaviour is documented since 3.2 (`start_new_session`) and is POSIX-only (`Availability: POSIX`, page line 516).
- Located lines in the served text: `start_new_session` at :513-514, "Changed in version 3.2" at :518; `Popen.communicate` timeout at :747-749; `subprocess.run` timeout wording at the `timeout` paragraph (run section).

## Located quotes (verbatim; markdown emphasis markers removed)

1. (22 words, primary for the session fix) — "If start_new_session is true the setsid() system call will be made in the child process prior to the execution of the subprocess."
   Word count: 22. Source location: Popen § start_new_session, lines 513-514.
2. (16 words, the reason the fixture must kill its own child) — "The child process is not killed if the timeout expires, so in order to cleanup properly"
   Word count: 16. Source location: Popen.communicate § timeout, lines 747-749. The full sentence continues "a well-behaved application should kill the child process and finish communication:", which is outside the 25-word cap and not quoted.

## Draft SOURCES row (for L1 to paste into the Registry)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S064 | Python subprocess documentation — https://docs.python.org/3/library/subprocess.html | docs | A | `start_new_session` (POSIX: `setsid()` in the child) and the timeout contract of `Popen.communicate`; not a claim about process-group kill semantics, which the page does not state | Python 3.15.0 online documentation opened 2026-10-20; § Popen `start_new_session` :513-514, Availability POSIX :516; § Popen.communicate `timeout` :747-749 | `start_new_session=True` makes the child call `setsid()` before exec (POSIX only), so a fixture can own the child's session; `Popen.communicate(timeout=…)` does not kill the child, so a fixture that times out must kill it itself | mined | 2026-10-20 | on-release | — (L1 adds corpus/lessons/round-18.md when the round-18 lesson lands) |

## Scope limits (what the row does not ground)

- The docs do not say that `setsid()` makes the child a process-group leader, nor that `os.killpg(pid, …)` reaches every descendant. The `os.killpg` mechanism is therefore NOT grounded by S064; any C1 claim that the group kill reaches grandchildren needs a separate POSIX/`setsid(2)` source or an executed fixture arm. [INFERENCE] until then.
- `subprocess.run(..., timeout=…)` is documented as "the child process will be killed and waited for"; the page does not say whether that kill reaches descendants. The fixture's own `killpg` is therefore still required; S064 does not show `run()` covers the case.
- Quotes were opened once by this seat. The round-17 convention re-opens each quote with a second seat; L1 should run that reopen before landing (the seat that opens a row must not be the one that verifies it).

## Frontier note

No other row opened. The `subprocess` page was the only source opened in this seat; no executed checks were run; no files were written other than this report.

## Tool installs/updates

None. Read-only web read via the `read` tool.

## Checks L1 should run

- `python3 tools/souji-landing-gate.py` (or the round-18 sources census) to confirm the S064 row's anchor syntax and the used-by path once the round-18 lesson exists.
- Second-seat reopen of https://docs.python.org/3/library/subprocess.html:513-514 and :747-749 to confirm both quotes verbatim.
