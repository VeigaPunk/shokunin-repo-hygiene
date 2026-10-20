STATUS: DONE — Q26/Q27 attack: the r17-calibrated auditor (unchanged since 4f48343) false-majors every contract-ordered w1 patch write and every w2 clone write, and R18-M6's prefix-kill is in no signal class — caught only by self-report, which Q26 explicitly disclaims as the audit.

Axes: calibration (false majors/false negatives of `tools/souji-seat-audit.py` against the r18 w1+w2 contracts); detection completeness (signal/git/environ classes); r19 spec-field requirements.

# Attacked claim

Q26 — "The seat probe rule is audited from transcripts, not self-report … writes outside its report/OWNED files … The audit is neither complete … nor precise … never proof of absence" (corpus/QUALITY.md Q26 row). Q27 — "An audit finding is re-read at its rendered source before its disposition is published, and the auditor's own parse limits are their own classes, never a scope violation" (corpus/QUALITY.md Q27 row). Coverage object: w1 seats audited with `tools/souji-seat-audit.py` at tip 5efb519 (last changed r17, `git log 5efb519 -- tools/souji-seat-audit.py` → 4f48343; no r18 commit touches it), and the w2 wave under `.ufo/waves/round-18/w2-spec.json`. LSP device: not present in this seat's tool inventory (recorded; classification checks below are code reads against the auditor's own selftest expectations, not LSP semantic proof).

# Findings

## F1 — MAJOR (calibration, structural): every w2 clone write is a false `V-WRITE-SCOPE` major

`run()` derives scratch from the wave name, not the contract: `ctx = context + " " + wave; sm = re.search(r"souji-r\d+-", ctx); scratch_base = "/var/tmp/" + sm.group(0) if sm else "/var/tmp/"` then per seat `scratch=scratch_base + name + "/"` (tools/souji-seat-audit.py:283-284, :299). The w2 spec is `"wave": "souji-r18-w2"` (.ufo/waves/round-18/w2-spec.json:2) — that string contains the literal substring `souji-r18-`, so scratch_base is always `/var/tmp/souji-r18-`. But the w2 contract's clone namespace is `/var/tmp/souji-r18w2-<SeatName>/lane` (w2-spec.json:5 context; this seat's own assignment). `_under(path, prefix)` is exact prefix+`os.sep` (tools/souji-seat-audit.py:110-112), so `/var/tmp/souji-r18w2-X/…` is not under `/var/tmp/souji-r18-X/` (divergence at the `w` after `r18`); `target_verdict` then returns `V-WRITE-SCOPE`, always major (tools/souji-seat-audit.py:203-206, :256-262 region). Consequence: every w2 executor's clone write — the contract-mandated behavior — is a major; per Q26's voiding rule ("an executing or writing violation voids the seat's evidence") compliant seats would be voided on a read of the call. The regex cannot express the `souji-r18w2-` namespace at all (`souji-r` + digits + `-` never matches `r18w2-`), so no w2 item can ever be scratch-clean. The silent fallback (:284 `else "/var/tmp/"`) is the mirrored hazard: had the wave name not matched, every seat would hold all of /var/tmp.

## F2 — MAJOR (calibration): all 13 w1 patch deliveries are false majors (or invisible)

w1 prompts order: `OWN ONLY tools/souji-census.sh (in your clone) … deliver /home/…/.ufo/waves/round-18/w1/<Seat>.patch` (w1-spec.json item prompts; measured: 14 `OWN ONLY` clauses, 13 items with `deliver /home/`). But `OWN_RE = r"OWN ONLY ([^\n]+?)(?:\s\(|\.\s|$)"` (tools/souji-seat-audit.py:90) terminates at the first ` (` — it captures only `tools/souji-census.sh`, so `ABS_RE` (:91) extracts nothing and `owned=[]` for every w1 item. `allowed = [report, *owned]` (:250) is exact-equality only; the patch path appears nowhere in it, so any `write`/`edit` of the deliverable is `V-WRITE-SCOPE` major. The audit outcome therefore depends on the delivery mechanism, not behavior: write/edit → major (exit 1); `bash … > patch` → invisible. Both arms misstate compliance. (Verifies ScoutSeatAuditR18 §2 FM-1 with counts; the `OWN_RE` ` (`-terminator is the mechanical reason, not merely "clause is relative".)

## F3 — MAJOR (detection): R18-M6's prefix-kill is undetectable by the auditor — the wave's one confirmed probe-rule violation was caught only by self-report

Canonical record: R18-M6 — "A wave-1 executor (MatrixR18) prefix-matched and SIGKILLed four processes it had not started (pids 842962, 842978, 842979, 842981 …)" with detection source "the seat's own disclosure" (corpus/lessons/round-18.md:20; narrative `.ufo/waves/round-18/w1/MatrixR18.md` "Probe-rule violation disclosure" section). Not detectable, for three independent reasons:
1. No signal class exists. `audit_seat` emits only V-SURFACE, V-LIVE-CENSUS, V-WRITE-*, V-EXEC, V-RECURSIVE, V-PROBE (tools/souji-seat-audit.py:245-274). Case-insensitive grep of the auditor for `kill|pkill|SIGKILL|signal` matches only the substring inside selftest `SKILL.md` literals (:320-423) — zero signal patterns.
2. The kills were performed by executed code (`run-matrix.py`'s superseded cleanup), not by a transcript bash call. The only visible line is `python3 …/census/round-18/run-matrix.py …`, which for this mutation-tester seat is V-EXEC-exempt (`EXEC_ROLES`, :93; `ALLOWED-EXEC:` flip :296) — and even V-EXEC flags the execution, never the kill. A hypothetical transcript line `→ bash(pkill -f r14-census-boundary.)` also matches nothing.
3. Rendered args truncate (~200 chars kept in flag rows, :239), so even a visible kill line could be cut.
Q26 says the audit is "from transcripts, not self-report"; for this class the transcript audit yields major=0, exit 0, and the entire catch was the seat's own disclosure — the exact anti-pattern the criterion names. Compensating control that does work: the delivered runner records the suite session id, the SIGKILL target pid and post-cleanup residue in its JSON artifact (MatrixR18.md session-cleanup run; census/round-18/c1-matrix-worktree.json), so L1 can re-derive from an artifact receipt — but nothing requires that receipt today.

## F4 — MINOR (calibration, observed): variant clone dirs are majors

The exact-scratch model admits exactly `scratch_base + <item name>/`. The real MatrixR18 seat worked in `/var/tmp/souji-r18-MatrixR18b/lane` (`.ufo/waves/round-18/w1/MatrixR18.md`: all five `python3 … /var/tmp/souji-r18-MatrixR18b/lane/...` check commands and the py_compile pycache prefix), which is outside `/var/tmp/souji-r18-MatrixR18/` → every clone write of that seat is a major. Retry/variant suffixes (dispatch-attempts files exist for both waves) are a standing source of this shape.

## F5 — MINOR (calibration, r18-specific exposure): `SURFACE_RE` fires on edit bodies and search-pattern text

`if SURFACE_RE.search(args): flag("V-SURFACE", "major")` runs on the raw rendered args of every tool (:245-246), and `edit` args contain the patch body (r16 transcript evidence: `LandingGate.txt:100` renders edit content; `write` content is elided). Round 18's own subject matter is made of the forbidden tokens: C2/Q30/Q31 prose must cite `.ufo/state/`, `.ufo/watchdog.log`, and the dated `census/operator-sweep-20261019` dir. Any lesson/LOG/report sentence carrying those tokens through `edit` is a major for text, not access; likewise a reviewer grepping FOR the dated dir name (`grep(operator-sweep-20261019 …)`) matches (`census/operator-sweep-\d` needs the digits — the auditor's own `pattern-word-not-surface` selftest case survives only because it omits them, :343). This round guarantees that shape in a way r16/r17 did not.

## F6 — MINOR (Q26 semantics): missing transcripts are silently skipped with exit 0

`run()` collects `missing_transcripts` and `continue`s (:289-291); `main()` exits 1 only on majors (:486-489 region, `return 1 if sm["major"] else 0`). An unaudited seat is indistinguishable from a clean one in the exit code, so "audited from transcripts" has no failure mode when the transcript is absent. No r18 transcript bundle exists in-lane (no `census/round-18/transcripts/` at 5efb519; r16 committed one, cf. commit ddb7347) — so I could not re-derive any actual w1/w2 auditor output; F1/F2 counts are contract-derived.

## F7 — NOTE (Q27 letter): `rstrip("…")` in the grep/glob branch

`a = args.rstrip("…").rstrip()` before `endswith(lane)` (:272-273) is a character-set strip, the pattern Q27/S061 ban for path comparison. Narrow (it exists to catch truncated recursive greps and strips only ellipsis chars from arg tails, not paths), but it is the same idiom Q27 proscribes; if r19 touches this line, switch to `removesuffix("…")`.

Verified-clean (no false major, re-checked from code + selftest expectations): clone writes under the exact literal prompt dir (`scratch-seat-write` case :382), `git clone`/`git -C <clone> checkout|add -N` (no git verbs in any class), `ps -eo`, `/proc/{stat,cmdline,cwd,wchan,fd}` reads, `python3 -m py_compile <file>`, `bash -n`, `shellcheck`, `sha256sum`, `stat`, read-only git show/log/ls-tree/rev-parse, and report writes (`report` first in `allowed`). Q27's severity contract is correctly implemented for the classes it has (`V-WRITE-UNPARSED` major on `⇒ ok`, minor on error — selftest h5/h5b :376-377; ambiguous/minor classes :257-259).

# What spec fields the r19 auditor must accept

All per-item, replacing derivation and prompt-scraping (the auditor does no schema validation today, so an unimplemented field is silently inert — the r19 gate must reject unknown/missing fields):

1. `items[].scratch` — exact absolute dir or LIST of prefixes (list covers F4 retry variants). Kills the wave-name coupling of F1; `souji-r18-w2` vs `souji-r18w2-` proves it is already broken, not hypothetical. Remove the `/var/tmp/` fallback (:284) — a missing scratch must be a spec error, not global amnesty.
2. `items[].writeAllow` — exact absolute deliverable files appended to `allowed` (:250): `allowed = [report, *item.get("writeAllow", []), *owned]`. Kills F2 with one line plus 13 spec entries; alternatively prompt-only, move each absolute patch path into `OWN ONLY` before the first ` (` so `OWN_RE`/`ABS_RE` capture it.
3. `items[].execAllow` — per-command regexes tested before `EXEC_RE`, replacing the binary `ALLOWED-EXEC:` role flip (:296) that grants three marker-bearing w1 scouts and every executor total V-EXEC immunity.
4. `items[].censusRoots` — declared /var/tmp prefixes replacing `(?!/var/tmp)` (LIVE_CENSUS_RE :27); must accept `--root X` and `--root=X`, quoted/`$var` operands, and any script token ending `souji-census.sh` or a declared copy.
5. `items[].signalPolicy` (+ `forbid` list) — new classes: `V-SIGNAL` (`kill|pkill|killall` in command position without grant), `V-GIT-WRITE` (mutating git verbs outside a declared clone prefix), `V-PROC-ENV` (`/proc/<pid>/environ`), `V-CRED` (credential-path prefixes; `SURFACE_RE` covers only the sweep dir, `.ufo/state`, watchdog log, `~/.omp`). Honest limit, proved by F3: NO transcript field can see kills performed inside executed code — r19 must require any seat granted execution to produce a kill receipt (session id + pids + residue, as run-matrix.py already writes) and audit THAT artifact, or Q26 must classify code-performed kills as unauditable-by-transcript in so many words.
6. `missing_transcripts` must fail (nonzero exit or `unresolved` summary field) unless explicitly allowed — closes F6.
7. `SURFACE_RE` scoping field (or code change): scan write/edit TARGETS and bash args only, never `edit`/`ast_edit` patch bodies or grep pattern text — closes F5 without losing the read-side surface check.

# Commands run (all read-only; no lane tool executed, no clone created — this seat has no ALLOWED-EXEC)

```
read .ufo/waves/round-18/w1/ScoutSeatAuditR18.md            (full)
read tools/souji-seat-audit.py :47-135 :133-232 :232-330 :330-530   (complete file, 489 ln)
grep 'souji-r\d+-' .ufo/waves/round-18/w2-spec.json         → line 2 wave "souji-r18-w2" (match source)
grep 'kill|pkill|SIGKILL|signal' -i tools/souji-seat-audit.py → only selftest "SKILL.md" substring hits; no signal pattern
grep 'seat-audit|transcript' .ufo/waves/round-18/w2-spec.json → clone prefix souji-r18w2-<SeatName> at :5; no audit routing keys
grep 'transcript|seat-audit' .ufo/waves/round-18/w1-dispatch.json → "audited by L1 from your transcript with tools/souji-seat-audit.py" (:856)
grep 'R18-M6|prefix|SIGKILL|argv' corpus/lessons/round-18.md → R18-M6 row at :20; seat-audit residual at :77
grep key-line pins tools/souji-seat-audit.py → OWN_RE :90; allowed=[report,*owned] :250; SURFACE_RE :245; scratch regex :283-284; per-seat scratch :299; missing :290; eff_role :296; rstrip :272
bash: grep -c 'OWN ONLY' w1-spec.json → 14; grep -o 'OWN ONLY [^\\]*' | grep -c '/home/' → 13 (the deliver paths share the JSON line, outside the OWN_RE capture); grep -c 'deliver /home/' → 13; grep -o '/var/tmp/souji-r18-[A-Za-z0-9]*' | sort -u → 17 item clone dirs, exact-prefix convention
bash: git -C <lane> log --oneline -3 5efb519 -- tools/souji-seat-audit.py → 4f48343 (r17), ddb7347, a6ec781; no r18 change
glob census/round-18/transcripts/* → path not found (no in-lane transcript bundle)
```

# Verdict

**Q26/Q27 coverage of round 18: partial (fails as specified).** The auditor is precise on the shapes r16/r17 calibrated (selftest survivors), but the r18 contract's two defining shapes both misclassify: patch delivery = false major (F2), w2 clone writes = false major structurally (F1), variant clone dirs = false major (F4); while the wave's one real violation (R18-M6) sits in a class with no detector and was caught by the self-report Q26 disclaims (F3). If the w1/w2 audit is run as-is, expect majors on compliant seats and exit 1; per Q26's voiding rule that voids executor evidence on read-confirmed "violations" that are contract-ordered behavior.

Smallest fix, in order: (1) one line `allowed = [report, *item.get("writeAllow", []), *owned]` (:250) + `writeAllow` in the 13 executor items; (2) `scratch = item.get("scratch", …)` per item, w2-spec declaring `/var/tmp/souji-r18w2-<Name>` (accept a list), fallback removed; (3) `V-SIGNAL` + `V-GIT-WRITE` + `V-PROC-ENV` classes with per-item `signalPolicy`/`forbid`, plus the kill-receipt requirement for executing seats; (4) `SURFACE_RE` restricted to targets/bash args; (5) `missing_transcripts` fails the run. Items 1–2 are prompt-fixable without code if the auditor cannot change mid-wave (patch path inside `OWN ONLY`; exact clone string literal in prompts; unquoted literal `--root /var/tmp/...`).

# Residual risk and verification gaps

- No r18 transcripts exist in-lane at 5efb519 (F6 evidence), so no actual auditor output was re-derived; F1/F2/F4 firing counts are derived from spec prompt shapes and one observed variant dir (MatrixR18b), not from a run. The harness-side audit may already have applied prompt-only mitigations I cannot see.
- The transcript renderer's exact cut length for `edit` args is unmeasured (carried from ScoutSeatAuditR18); a forbidden token past the cut is invisible — this bounds F5 in both directions.
- Whether L1's w1 dispositions already handled the false majors per Q27 (re-read at rendered source, named transcript lines) is unverifiable from the lane.
- LSP device unavailable in this seat's inventory → no semantic definition/reference checks; classification claims rest on code reads cross-checked against the auditor's own selftest expectations (which I did not execute — no ALLOWED-EXEC for this seat).
- Tooling installs/upgrades: none (pacman paused; no tool needed beyond stock grep/git/read).
