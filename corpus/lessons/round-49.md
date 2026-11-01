# Round 49 — the freeze-check selftest re-derivable on this host (the r48 routed fixture defect fixed, same-instrument red→green)

Fresh-start reading done first (round prompt §7): the last three rejected
closures (r43, r44, r45 — lessons + reports) were re-read and spot-checked
before anything was declared; the rulings-out are in the round report. The
r48 non-author closure routed three defects; all three are addressed: item 1
became claim C1 (calibration 7, the lowest non-retired axis), items 2 and 3
are lesson rows below. One claim, one axis; preregistration frozen at
445321aa61cfafb95b623a5fe1c0126c0a60186f (attempt 2 — see Mistakes row 2;
attempt 1 ebebc44c0ccd8941dd4cc1fc4dd71452ab9027fa is preserved as evidence,
never rewritten) before any claim receipt existed; the do-nothing control is
committed in the freeze commit (control-first). No wave was dispatched: this
host has no seat dispatch surface (standing L0 question; dispatched=0,
completed=0, dead=0; no WAVE-DONE claimed; nothing assumed answered).

## Gate

- S272 admitted: https://docs.python.org/3/library/functions.html (served
  /3/builtins/functions.html after one 301) opened live 2026-11-01 by this
  session (curl -sSL, HTTP 200, 330862 bytes, sha256 ece1c4b3…e00701a;
  capture census/round-49/sources/s272-python-open-located-quote.txt).
  Located quote (23 words, counted by command against the captured bytes —
  the count command is in the capture): "When writing output to the stream,
  if newline is None, any '\n' characters written are translated to the
  system default line separator, os.linesep." Context: open()'s
  newline-parameter description; the same page's encoding paragraph adds
  "For reading and writing raw bytes use binary mode and leave encoding
  unspecified." Grounds only the interpreter behavior — text-mode writes
  translate \n to the platform newline, binary mode does not translate —
  which is exactly the mechanism behind the r48 routed fixture defect. The
  page never names git blobs, freeze preregistrations, or this lane's
  instruments; which instruments are affected is the round's own sweep
  (census/round-49/records/fixture-hazard-sweep.txt), instrument-internal.
- Reject sample (r48-closure carry-in item 3), stated explicitly: this Gate
  opens exactly ONE new source (S272, the only candidate fetched, admitted)
  and lands ZERO new reject rows — there was no rejection decision to
  record; the sweep that shows the sample is the single-fetch inventory
  above. The reject-side sample is a standing-rejection re-open: S267
  (rejected r45: tuple equality cannot establish historical correction
  truth) was re-opened against the live
  https://docs.python.org/3/builtins/stdtypes.html (HTTP 200, 814236 bytes,
  receipt census/round-49/sources/s267-reopen-receipt.txt): the comparison
  sentence is verbatim on the live page, the page contains zero occurrences
  of "factual" and zero of "histor*", so the recorded rejection reason
  holds — S267 stays rejected, no row cell changed.
- S271 word-count erratum (r48-closure carry-in item 2): the r48 lesson and
  r48 report label the S271 located quote "17 words"; the verbatim quote —
  "cacheinfo is useful when the object is in the database but the file
  isn't available locally" — is 16 words. Count command:
  `python -B -c "s='cacheinfo is useful when the object is in the database but the file isn'+chr(39)+'t available locally'; print(len(s.split()))"`
  → 16. The ≤25-word bound held either way; the quote bytes never changed;
  the r48 lesson stays as filed (history is not rewritten). Lineage: r45's
  Gate carried the same class ("15 words" for a nine-word quote, corrected
  in its errata section) — second occurrence; both eras' quotes are now
  command-counted (S272's count command runs against the captured page
  bytes, per the r45 erratum practice).
- Census before→after: before
  `census/round-49/records/census-before.txt` (the r48 adapter form, rc 0,
  58 W04 duplicate-url warnings, rows 195, `shokunin-repo-hygiene ok`; the
  conf form's raw rc-2 `souji missing` verdict recorded inside — the
  documented host state, PROVINCE host correction). After: the end-of-round
  receipt lands with the round's end receipts, exit 0 required.
- NTFS exclusion set re-derived at base: exactly the six pinned paths
  (`census/round-49/records/ntfs-exclusion-check-base.txt`), matching the
  campaign record; tip re-check lands with the end receipts. Not widened.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| text-mode fixture writes for digest-bound bytes — a fixture writer that lets the platform newline translation choose the bytes cannot feed a literal LF digest off-POSIX (the r48 non-author closure routed defect 1; lineage r43 R43reviewer05 "its r42 CRLF case never actually writes CRLF") | at the r49 base the committed tool's selftest reads SELFTEST cases=41 pass=4 fail=37 EXIT=1 (census/round-49/controls/freeze-selftest-base-red.txt) and the frozen-form counter at the same rev reads selftest=FAIL (41, 4, 37) patches=0/3 (census/round-49/controls/c1-control-donothing-r2.txt); the pre-freeze sweep (census/round-49/records/fixture-hazard-sweep.txt) counts 49 selftest-bearing instruments, 27 with text-mode open sites, exactly ONE digest-bound writer in the tools layer — tools/souji-freeze-check.py; the frozen census counters (r41 c3, r42 c2, r43 c2/c3) carry the class as named limits (frozen bytes never edited; the r42 counter additionally cannot launch its child here — it invokes the "python3" name and this host has none) | the r48 non-author closure + this round's pre-freeze sweep | the fixture writer ported to binary mode (`open(fp, "wb")` + UTF-8 encode; the diff receipt census/round-49/records/tool-diff-base-to-fix.txt shows exactly that hunk plus its docstring line — verdict code byte-identical); raw selftest on the fixed bytes 41/41 EXIT=0 (records/freeze-selftest-fixed-green.txt); the new binary-clean counter census/round-49/c1-counter.py (no digest-bound fixture writes; launches the tool with sys.executable, no interpreter-name dependency) stands over the tool: red at base, green at the tip (patches=3/3 proves the repaired selftest still discriminates) |
| a receipt destined for a grammar-parsing field must meet that grammar — the attempt-1 freeze's Control receipt ended `COUNTER-EXIT=1`, the freeze-check's Control grammar requires the last non-blank line to be `EXIT=<nonzero>` | the freeze-check verdict run at the attempt-1 freeze itself read FINDING C1 CONTROL-NOT-RED … SUMMARY claims=1 findings=1 (census/round-49/records/freeze-check-at-freeze-attempt1.txt); attempt 1 ebebc44c… preserved as evidence, never rewritten; no after-data existed | the freeze-check verdict at the attempt-1 freeze — the instrument caught its own round's formatting defect at freeze time | freeze attempt 2 (445321aa…, preregistration-r2.txt): the control receipt re-taken with the same run shape and a grammar-correct final line (controls/c1-control-donothing-r2.txt), attempt-1 files byte-unchanged forever; the attempt-2 freeze reads claims=1 findings=0 exit 0 (records/freeze-check-at-freeze-r2.txt). Standing rule: run the freeze-check verdict against a freeze commit BEFORE building on it — attempt 1 was caught exactly by that run, and the supersede landed before any claim receipt (the r48 Amendment-1 ordering) |
| an exit code captured after a pipe records the pipe's last stage, not the instrument — the first raw-red receipt read "EXIT=0" under a failing selftest because `$?` followed `… --selftest | tail -3` | caught on this round's own receipt review, before landing; the receipt was re-taken with the instrument's stdout going to a file and `$?` taken unwrapped (controls/freeze-selftest-base-red.txt now ends EXIT=1, matching the counter's independent summary line); the flawed first take never left session scratch | this round's pre-landing receipt review | standing rule: receipts embed an instrument's exit code only as `cmd > file; rc=$?` — never after a pipe; where two receipts measure one verdict (raw + counter) their exits must agree, and this round's do (1 = 1) |

Fresh-start sweep (three rejected closures, re-checked this round): r43's
shape was preregistration-after-ready-handoff plus instruments that cannot
bind their tokens — ruled out by freezing at 445321aa (attempt 2) before any
claim receipt, with the counter digest-pinned in the prereg and the
do-nothing control committed in the freeze commit. r44's shape was a frozen
predicate honest work could not meet — ruled out by deriving the target from
a state the base already exhibits honestly (the selftest's own verdict on
committed bytes: red at base by the instrument's own reading, not by a
predicate the base cannot express) and from the r42 registry row's published
green semantics. r45's shape was the different-instrument limit (0-to-green
by swapping instruments) — ruled out structurally: the SAME r49 counter
measures both arms (it reads the base's committed tool bytes red and the
tip's committed tool bytes green; the instrument's bytes are identical in
both runs — only the world moves), and the repair direction is the r48
verifier's own routed fix to the lane's instrument, not a new instrument
invented to flip a verdict. The full ruling table is in the round report.

## Admission distinction

C1 is an instrument repair landing a calibration verdict: the lane's
standing self-assessment of its own freeze instrument (the r42 registry gate
`r42-freeze-check-selftest`) had no obtainable green on this host — the
registered gate could not match observed state; after the routed repair the
same gate's verdict is re-derived green here (41/41 raw; counter green with
patches=3/3, real/retro/retro_clean unchanged from base to tip). No new
capability row: the capability is the r48-era discipline applied to an
inherited instrument. Numeric axis scores unchanged (calibration 7,
operability 8, coverage 8): one repair does not saturate the axis, and no
new surface enters the province.
