# S59Scribe — round-59 Gate draft (source admit/reject) for L1 integration

Draft only. Nothing in `corpus/`, `census/`, `SKILL.md`, `LOG.md`,
`SCORECARD.md` or `MANIFEST.json` was edited by this seat. The canonical
assignment remains the only instruction source; this file is a proposal for
L1 SoujiR59, who holds sole integration authority.

## Gate — source decisions, opened 2026-11-04

One official document opened: `https://docs.python.org/3/library/subprocess.html`
(Python 3.15.2 documentation; curl -sSL HTTP 200, no redirect, 208648 bytes,
sha256 `31f573c59a215fbad7e12dd81b41715f38b600eed240b84b9a42bd4e4a1685b1`;
capture `subprocess.html` in this delivery directory). Located quotes, token
lists and capture line spans: `quotes.txt`. Tool-reader evidence: the same URL
was additionally opened with the session's URL reader, which returns the
3.15.2 page text containing both quoted sentences.

| id | source | decision | located quote (words) | what the source supports / does not support |
|---|---|---|---|---|
| S286 | Python subprocess return codes — https://docs.python.org/3/library/subprocess.html | **ADMIT** (draft, tier A, status mined) | `Exit status of the child process. Typically, an exit status of 0 indicates that it ran successfully.` (17) | `CompletedProcess.returncode` is a child exit status distinct from captured stdout. It grounds the requirement that a public gate selftest assert the child's return code, not only its printed findings. It says nothing about whether any particular gate implementation is correct. |
| S287 | Python subprocess check default — https://docs.python.org/3/library/subprocess.html | **REJECT the inference** (draft, tier A, status rejected) | `If check is true, and the process exits with a non-zero exit code, a CalledProcessError exception will be raised.` (19) | The documented exception is conditioned on *check being true*, and the `subprocess.run` signature on the same page defaults `check=False`. So the default does not assert an exit status. REJECTED inference: "capturing stdout with the default check setting proves the child succeeded". Flip: compare `CompletedProcess.returncode` against an independently persisted expected rc. The official document itself is **not** rejected — only the inference drawn from it. |

Both rows cite the same URL under different scopes, so the fleet census emits
the same-URL/different-scope **W04** warning for each (as it already does for
S261, which cites this page under an env/stderr scope). W04 is a warning
class, not a finding.

## Executable substance for the row drafts

`verify-quotes.py` (stdlib only, read-only over the capture and the rows file)
checks each draft row against the captured page: quote verbatim in the
tag-stripped/entity-decoded/whitespace-collapsed capture; word count at or
below the 25-word ceiling; anchor label present on the page; exactly one shared
URL across the two rows; distinct scopes.

Honest arm — the two draft rows in `rows.tsv`:

```
ROW S286 words=17 verbatim=True
ROW S287 words=19 verbatim=True
SUMMARY checks=2 findings=0
```

Exit status 0. Four negative controls, each rejected with a named finding:

| control | mutation | observed |
|---|---|---|
| corrupt-quote | S286 quote reworded ("the CHILD") | rc=1 `FINDING QUOTE-NOT-VERBATIM S286` |
| over-long-quote | S286 quote replaced by 30 words | rc=1 `FINDING QUOTE-TOO-LONG S286 words=30` |
| same-scope | S287 scope set equal to S286's scope | rc=1 `FINDING SCOPES-NOT-DISTINCT …` |
| different-url | S287 URL changed to `os.html` | rc=1 `FINDING URLS-DIFFER …` |

These four are the only controls this seat ran. They test the row-draft
checker, not the lane's gate implementation and not the round's counter.

## What this seat did NOT establish

- That the r59 assessment gate implementation asserts rc correctly. No
  `assessment-gate.py` existed in `census/round-59/` at the time of this
  seat's read (the directory held `before.txt`, `c1-counter.py`,
  `controls-run.txt`, `controls.json`, `controls.py`, `population.tsv`,
  `preregistration.txt`, `sources-before.txt`). S286 grounds the requirement;
  it does not evidence any implementation.
- That the frozen counter or the pre-freeze controls pass. Not run here.
- Any admission verdict. The lane-dispatched seats cannot confer non-author
  admission; the outside spot-check remains the closure's duty.

## Inherited debts carried forward (unchanged by this seat)

Visibility-parser second-opener / code-span / escape / link / TAB and scale
defects; recorder dirty-tree and overwrite; capture row-set meta-test;
historical receipt bindings; diagnostic escaping; receipt-confinement
atomicity and resource-intake bounds. Certification OFF; K5 HELD; r46
mass-id-drift hold retained. Prior r56/r57 rejected-harmed and r58
rejected-honest-stop admissions are unchanged and are not retroactively
repaired. This seat closed none of these and opened none.

## Discrepancies reported to L1 (not applied by this seat)

1. **S287 word count.** The round-59 lesson in the lane working tree records
   the S287 located quote as 23 words. The quoted sentence is 19
   whitespace-separated words; the counted token list is in `quotes.txt`.
   Same defect class as r57's S279 quote-2 (recorded 17, later established 19).
2. **S287 scope wording.** The working-tree row's scope cell reads "rejected
   inference that capturing stdout with the default check setting proves child
   success" while its `teaches` cell states the check=False point. This seat's
   assigned scope is "rejected inference that check=False itself asserts
   success". The draft in `sources-rows-draft.md` uses the assigned wording;
   the two scopes remain distinct from S286 either way.
