# S59Scribe — round-59 lesson draft (source gate + r58 late-control mistake)

Draft only. `corpus/lessons/round-59.md` is a production file owned by L1
SoujiR59; this seat did not create, edit or overwrite it. The text below is a
proposal for L1's integration, written so that the source admit/reject decision
and the r58 late-control mistake are both carried without erasing any
inherited debt.

## Opened sources (Gate continuation) — draft wording

- **S286 admit** (C1 sourced evidence): https://docs.python.org/3/library/subprocess.html,
  accessed 2026-11-04, Python 3.15.2 documentation, `CompletedProcess.returncode`.
  Located quote (17 words): `Exit status of the child process. Typically, an
  exit status of 0 indicates that it ran successfully.` Child exit status is a
  separate attribute from captured stdout, so the assessment-gate selftest must
  assert rc alongside its findings. Capture and span receipt: `quotes.txt`.
- **S287 reject inference**, same URL, same access date, same version, the
  `subprocess.run` check paragraph. Located quote (19 words): `If check is
  true, and the process exits with a non-zero exit code, a CalledProcessError
  exception will be raised.` The `run()` signature on the same page defaults
  `check=False`, and the documented exception is conditioned on check being
  true, so the default asserts no exit status. Flip: compare
  `CompletedProcess.returncode` with an independently persisted expected rc.
  The official document is not rejected; the inference drawn from it is.
- Rows added A2/B0/C0. No existing status/recheck/used-by cell changed. The
  two rows share one URL under distinct scopes, so the census reports the
  same-URL/different-scope **W04** warning for each, as it already does for
  S261 on this page. W04 is a warning class, not a finding.

## Mistakes — draft rows

The r58 late-control mistake is carried forward and kept explicit, not
softened by r59's own clean chronology:

| class | evidence | captured-by | fix |
|---|---|---|---|
| scope: a verdict comparator registered as evidence-only | corpus/lessons/round-58-verifier-spotcheck.md routed defect 2; SKILL.md r58 assessment row; census/round-59/before.txt shows REGISTRY-KIND-MISMATCH EXIT1 | PROTOCOL Gate standard; outside closure | classify the historical comparator as gate, register its current self-invoking successor; the SAME frozen classification command is red at base, not just a prose assertion |
| vacuous: control commitment after predicate freeze cannot establish prefreeze discrimination | r58 outside spotcheck §C2 chronology; r58 freeze e7f64f3 before executable control1880343 | Q99 and round59 binding prerequisites | r59 controls actually executed and committed 74455b7209e04a2375c2084738a7b6fea59bf6d5 BEFORE declaration 19f44552378d333f401ff2f0864c4e8b9c59ab1f; unchanged/prose forgery/duplicate forgery red, correct-kind positive green; census/round-59/controls.json retains expected and actual rc/findings |
| quoting: a located-quote word count is asserted rather than counted | round-59 lesson records the S287 quote as 23 words; the sentence is 19 whitespace-separated words (token list in `.ufo/waves/round-59/w1/S59Scribe/quotes.txt`); r57 S279 quote-2 recorded 17, later established 19 | S59Scribe re-open and count against the pinned capture | count the quote with a command over the captured bytes and record the token list; a prose count is not a count |

The third row is new to this draft. It is a record-accuracy correction, not a
claim defect: the quoted sentence is verbatim and correct; only its stated
length was wrong. It is offered for L1 to accept, amend or drop.

## Preserved debts and boundaries — draft wording

Prior r56/r57 rejected-harmed and r58 rejected-honest-stop admissions remain
unchanged. Visibility-parser second-opener/code-span/escape/link/TAB and scale
defects; recorder dirty-tree/overwrite; capture row-set meta-test; historical
receipt binding; diagnostic escaping; receipt confinement atomicity/resource
intake all remain OPEN. Q117 pathname/raw-identity protections remain current.
Certification OFF; K5 HELD. Nothing removed, quarantined, signalled, rewritten
or certified safe to delete. No credential material opened.

The classification counter measures its single named row, not general registry
truth or execution authenticity. A truthful kind edit intentionally passes its
positive control; actual public comparator runs and selftest are separate
substance/conformance evidence. Any unexercised branch remains unproved. Frozen
counter, population and controls are not amended after scoring.

Source admission and rejection are the non-author closure's duty, not any seat
this lane dispatched. The source rows above are drafts sourced from one
official page opened live on 2026-11-04; they grant no capability, certify no
tool, and close no inherited debt.

## Note for the canonical judge

This seat is lane-dispatched. It reports source facts, a row-draft checker with
four negative controls, and two record discrepancies. It does not claim
non-author admission, does not claim the lane's gate implementation is
correct, and does not claim the frozen counter or the pre-freeze controls pass
— none of those were executed here.
