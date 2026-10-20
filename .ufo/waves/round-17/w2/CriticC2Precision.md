STATUS: DONE — C2's headline numbers are honest: they reproduce from the records, every changed row is accounted for, and the selftest really is severity-exact. Three things are wrong: the "held-out" label, the stated reason the relative header is allowed, and the lack of any held-out precision check. HeldOutBaseAuditor-2 executed my predictions and confirmed three new false majors (P1–P3, base `[]`) plus the pre-existing P5. P4 is an undisclosed fail-open that we disagree on. The replay record is bound but not committed. Verdict: **partial**.

# CriticC2Precision — round 17 w2 (critic, axis: calibration)

- **Scope:** C2 as landed. That means `tools/souji-seat-audit.py` at ddb7347 (blob sha256 `8268212d…`), `census/round-17/seat-audit-replay.py` (`e3a89931…`), and the two replay records.
- **Method:** every behavioural statement about the auditor is derived from the source. I was given no ALLOWED-EXEC, so I ran no lane tool. Predictions are phrased as falsifiers for L1, and I sent them to HeldOutBaseAuditor-2. File:line references are `git show ddb7347:<file>` line numbers.

**Execution confirmation (peer, not run by me).** SoujiR17-3.HeldOutBaseAuditor-2 imported the ddb7347 auditor and ran P1–P5 with lane=`/home/u/P/f/lane`, rep=`…/.ufo/waves/round-9/w1/S.md`, owned=[`lane/tools/x.py`], scratch=`/var/tmp/souji-r9-S/`. It reported:
- P1 → V-WRITE-RELATIVE major; base `[]`.
- P2 → V-WRITE-UNPARSED major; base `[]`.
- P3 → V-WRITE-RELATIVE major; base `[]`.
- P4 `[/v…` and `[/…` → `[]` on both base and ddb7347. The peer calls this "not a bug", because `:150-155` and the `scratch-trunc-header` case rely on scratch-prefix compatibility.
- P5 → V-WRITE-RELATIVE major; base was V-WRITE-SCOPE major.

So **P1–P3 are executed regressions** (false majors that did not exist in the base). Its candidate fix keeps 48/48 of the table and passes 13/13 probes; see `.ufo/waves/round-17/w2/HeldOutBaseAuditor.md` §5b.

My position on P4 stands as a **disclosure defect**, not an r16 count error:
- the code comment at `:150-152` says the prefix "resolves inside the one region seats may write freely";
- SeatAuditPrecision's Limits say "fail-open inside `/var/tmp` only";
- both are false for `/` and `/v`.

**Correction, after the peer measured it.** I said the peer's "unparsed fallback only when no header resolved" rule would hide real truncated targets. That is retracted. The peer built both variants on the same P1/P3/P5 changes and got the same results for each:
- 48/48 table cases and 15/15 probes;
- X1, `edit([<owned>#AB12] PUT 1.=1: + y [/home/u/P/f/other/…)` → V-WRITE-SCOPE major;
- X2, `…[souji-shokunin/…)` → V-WRITE-RELATIVE major.

The two rules behave identically on every measured input. The first-character rule (a tail is a header only if the character after `[` can be a path character) is kept only as the clearer way to write it.

Untested by either of us: fix 1's op-keyword rule for P3, and fix 3 (P4 narrowing).

## Axes
- **calibration** (judged): does each reported number mean what it says?
- Touched, not judged: recall (allowed rows that are not safe) and reproducibility (what the record binds).

## 1. The numbers: hold
Both records were read with jq.

| record | w1 major/minor | w2 major/minor |
|---|---|---|
| base | 1 / 19 | 3 / 42 |
| after | 1 / 20 | 1 / 52 |

- **After w2 minors** = 42 V-RECURSIVE (the same 42 rows as base) + 8 V-PROBE (ConnQuality2:48, ConnSkillRegistry2:47, ReopenS047:81, ReopenS049:70, ReopenS049:86, RerunSeatAudit:170, RevRegenerate:149, ScoutSafeDirectory:86) + 2 V-WRITE-UNPARSED.
- **After w1** = base + ConnLogConvention:52 V-PROBE, with SentinelCommandExec:118 renamed from UNKNOWN to UNPARSED.
- **Row diff, base → after:** no row disappeared. The only changes are those additions, that rename, and three reclassifications:
  - ConnReadmeIndex:180 SCOPE→RELATIVE, still major;
  - RerunGateReplayR14:225 and :226 major→UNPARSED minor.
- **"Misclassified 2→0" is fair.** Transcript lines `224:`/`225:` both end `⇒ error · 8 lines — Validation failed for tool "edit"`. The calls were rejected before dispatch, so no target was resolved or attempted. Word it as "rejected calls, target not rendered", not "false positive".
- **"True 2→2"** matches the non-author labels in CriticC2Overclaim (SrcGitNoLazyFetch:144, ConnReadmeIndex:180).
- **"20 severity-blind → 49 severity-exact" holds:**
  - 5fa6017 `:179` is `got = sorted({v["class"] for v in found})`, a set of class names;
  - ddb7347 `:331` is `sorted((class, severity))`, compared as a list, so the multiset is exact;
  - I counted the cases at `:267-325`: 48 plus wave-summary = 49.

## 2. The "held-out" label is false after the fact
`:310` says "H1–H8 held-out shapes". The critic wrote those lines before the code, and the executor then fitted the code until they passed. They are now regression pins. No evaluation on shapes the rule was not tuned on exists anywhere in C2. The new rules also create their own false positives (§4), and the selftest exercises none of them.

## 3. The relative-header divergence (`[tools/x.py#AB12]` → `[]`)
**Verdict on the r16 row:** LandingGate:100 is a true negative. Keeping it unflagged is correct for that row. Evidence:
- the w1 spec gives LandingGate `OWN ONLY /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py`;
- `stat /home/vgpnk/Projects/shokunin/tools` → absent;
- the seat then re-read the lane file to repair "the wrong range" (`LandingGate.txt` `104:`–`113:`).

**The stated mechanism is wrong.** The executor says the header "resolves under the lane root". But the session root was the fleet root, and the edit tool's own canonical name for the lane file is fleet-relative:
- `LandingGate.txt` `126:` `⇒ error … This edit anchors to lines 468 of souji-shokunin/tools/souji-landing-gate.py`;
- `PreservationRepin.txt` `180:`, the same form;
- of the 26 rendered header edits in the 144 transcripts: 13 are absolute headers and 12 use the `[souji-shokunin/…]` fleet-relative form. Exactly one is a lane-relative header, LandingGate:100.

So `[tools/…]` resolved through some mechanism other than a root. [INFERENCE] It is a tag/snapshot or suffix fallback inside the edit tool; this is unobserved.

**Effect on the auditor.** `target_verdict` (`:169-174`) tries the lane root first and allows the first hit. That hard-codes a root the session never had.

**Recall hole:** real but conditional, with zero observed r16 exposure. If the fallback resolves by tag or suffix, then a `[tools/souji-census.sh#T]` whose tag was minted on another repo's `tools/souji-census.sh` writes that repo and audits clean.

**The justification is outcome-driven.** SeatAuditPrecision.md:21 says flagging the row "would add a second w1 major… and break the declared w1 1→1 outcome". That is the overfit signature (a rule chosen to hit a count), even though this row's label is right on the evidence.

**Smallest fix:** a header that resolves only through the lane-root guess, and not at the fleet cwd, gets a **minor** class (e.g. `V-WRITE-HEADER-INFERRED`). Majors stay 1/1, the row stays visible for adjudication, and the docstring states that resolution is modelled.

## 4. Held-out counterexamples (source-derived; falsifiers for L1)
All four are new, and none is covered by a selftest case.

**P1 — false major: a correct fleet-relative bare write.**
- Line: `→ write(souji-shokunin/.ufo/waves/round-17/w2/S.md) ⇒ ok` (lane = …/souji-shokunin).
- Path through the code: `write_targets` → `(target, False, False)`, then `target_verdict` `:169` skips the root loop for bare targets, then `:175` returns V-WRITE-RELATIVE major.
- The path resolves at the contract's fleet root to exactly the report. The docstring (`:18-21`) and comment (`:166-167`) say a bare target "cannot reach an allowed lane path". That is false: this is the harness's own rendering form.
- Fix: resolve bare relatives at the fleet root only, and allow the target when the normalized result is allowed. ConnReadmeIndex:180, H1 and H2 stay major.

**P2 — false major: a bracket inside the body of a bash patch.**
- Line: `→ edit(*** Begin Patch [<lane>/tools/x.py#AB12] PUT 1.=1: + if [ -n "$foo…) ⇒ ok`.
- `:118` finds the unclosed `[` after the last `]`. The fragment `-n "$foo` fails the character class, so `:126` gives `(None, True, True)` and `:207-210` makes it V-WRITE-UNPARSED **major**.
- C1/C3 are bash tools, so r17 executor transcripts are exposed. The r16 exposure is 0: all 7 unclosed tails in r16 are path-like.
- Fix: an open tail is a header only if the character after `[` is in the path class (headers never start with a space).

**P3 — false major: a markdown link in content.**
- Line: `→ edit([<rep>#AB12] PUT 1.=1: + see [README.md](x)) ⇒ ok`.
- `EDIT_HEADER_RE` (`:68`) matches `[README.md]` (it contains a `.`) as a header, which gives V-WRITE-RELATIVE major.
- This is a regression from the base, which audited only the first header.
- Fix: count a complete `[path#TAG]` / `[path]` as a header only when it is followed by `\s+(PUT|CUT|REM|MV)\b`. H6 still passes, because both headers in it are followed by `PUT`.

**P4 — recall fail-open beyond what the claim disclosed.**
- Truncated prefixes are allowed when `_norm(scratch).startswith(vis)` (`:153-154`). So `[/…`, `[/v…`, `[/var…` and `[/var/tmp/…` are all allowed.
- That contradicts the disclosed "fail-open inside `/var/tmp` only". `/v` is compatible with `/var/lib/…`, and `/` with everything.
- It also defeats the seat-scoped scratch rule (`scratch-other-seat`) whenever the header is truncated before the seat name.
- Live r16 rows on this branch:
  - `MutateDirtyFilters.txt` `90:` and `98:` render `[/v…)`;
  - `MutateSeatAudit.txt` `86:` renders `[/var/tmp/…)`;
  - `MutateScanConfig.txt` `83:` renders `[/var/tmp/souji-r…)`.
  - These four are probably benign, since the first header in each is the seat's own scratch, but they are allowed by prefix, not resolved.
- Fix: allow only when `vis` is under the scratch dir. Treat a scratch-compatible prefix that is not under it as a **minor** truncated-ambiguous row. Majors are unchanged and r16 minors rise by 4.

**P5 — false major (pre-existing at base, not a regression).** `write(xd://report_issue)` and `write(local://x.md)` give V-WRITE-RELATIVE major, because only `agent://` is exempted (`:144`). Fix: exempt any `scheme://` target that is not `file://`.

**Impact on the claim.** None of these touch the r16 major numbers. They do falsify "precision" as a property of the rule: P1, P2 and P3 will produce false majors on r17 transcripts. Recall for eval calls, shell writes and `sed -i` remains unmeasured, as disclosed.

## 5. Reproducibility: partial
**Bound and verified by me:**

| item | record value | check |
|---|---|---|
| after auditor | `8268212d…` | = ddb7347 blob |
| base auditor | `c9ff355c…` | = 5fa6017 blob |
| specs | `eb242e48…`, `775a4c9c…` | = committed w1/w2 spec blobs |
| manifest | `4837d550…` | — |
| manifest tool | `12e294b0…` | = ddb7347 blob |
| manifest check | `check OK: 144 files verified`, exit 0 | — |
| counts | 65/79 | — |

**Not bound or not landed:**
1. **The records are untracked.**
   - `git ls-files census/round-17` lists no `seat-audit-r16-replay-*.json`; neither ddb7347 nor d7e648d adds them.
   - The worktree files are `bd2e61df…` (base) and `6f00a5b6…` (ddb7347). Both have mtime 14:25:07.172, which is after ddb7347 (12:42).
   - The C2 text cites them as records, but they are not landed.
2. **The stored location does not match the record's own argv.** argv `--output` is `/var/tmp/souji-r17-L1/sa-{before,after}.json`, so the files were copied in afterwards. The record carries no digest of itself.
3. **The replay tool's own sha256 is missing** (`seat-audit-replay.py` `:73-84` records the auditor and manifest tool, not itself). Also missing: the Python version and the base auditor's commit (only the sha is recorded; I matched it to 5fa6017 by hand).
4. **Byte reproduction requires the identical `--output` path**, because argv is serialized into the body.
5. **Transcript-to-session authenticity is still unbound.** Line 1 of each transcript names `~/.omp/agent/sessions/…jsonl#TAG`, and that jsonl is not digested. CriticC2Overclaim F6.4 is unchanged.

**Fix:**
- commit both records;
- add `replay_tool_sha256`, `python_version`, and `auditor_git_rev` (or `"unbound"`) to the record;
- cite each record's sha256 in the C2 claim text.

## Verdict
- **Numbers (w2 3→1, misclassified 2→0, true 2→2, 20→49 severity-exact):** hold.
- **"Held-out" H1–H8:** fails. They are training pins.
- **Relative-header `[]`:** the row is right but the stated reason is wrong. It is a conditional recall hole that the docstring hides; fix it with a minor class.
- **Precision as a general property:** partial. P1, P2 and P3 are new false-major paths and P4 is an undisclosed fail-open.
- **Replay record:** partial. The digests are bound but the records are not landed and not self-identifying.

## Smallest safe correction (in priority order, none changes r16 majors)
1. Fix P2 (`:118-126`, the open-tail character check) and P3 (`:68`, an op keyword must follow the header). Fix P1 (`:166-175`, resolve bare relatives at the fleet root). Add selftest cases P1–P5 with exact `(class, severity)`.
2. Give lane-root-only header resolution a minor class, and correct the docstring and SeatAuditPrecision's mechanism sentence.
3. Narrow the P4 prefix rule to `_under(vis, scratch)`; anything else that is scratch-compatible becomes minor. Update the Limits text. **Prerequisite:** the pinned `scratch-trunc-header` case (`:325`, `[/var/tmp/souji-r…` → `[]`) contradicts this rule, because that string is a lexical prefix and not inside the scratch dir. Change that case's expectation to the minor class first; this is a table decision, not a code bug. If L1 keeps the case, fix 3 shrinks to correcting the comment at `:150-152` and the Limits text.
4. Commit the replay records, extend them with the tool sha, Python version and auditor rev, and relabel `:310` as "critic-authored regression shapes".

## Commands run
- `git -C <lane> show ddb7347:tools/souji-seat-audit.py | cat -n`; `show --stat ddb7347`; `show --stat d7e648d`; `log --oneline -5`; `ls-tree --name-only -r HEAD census/round-17/`; `rev-parse HEAD` → d7e648d5….
- `git show ddb7347:census/round-17/seat-audit-replay.py | cat -n`.
- `git show 5fa6017:tools/souji-seat-audit.py | cat -n | sed -n 170,240p`.
- `sha256sum` on the auditor, the replay tool, the manifest tool, the manifest, both specs and both records (worktree and `git show` blobs); outputs as cited in §5. `git ls-files census/round-17 .ufo/waves/round-16/w{1,2}-spec.json` (specs are tracked; the records are not).
- `stat` on fleet `tools`, `tools/souji-landing-gate.py`, `tools/souji-seat-audit.py` and `SKILL.md` (all absent); fleet `.ufo/waves/round-16` (exists, no `w2`); fleet `.ufo/waves/round-17`; both lane records; `c1-matrix.json` (absent).
- `read` with jq on the two records (headers and all violation rows) and on `.ufo/waves/round-16/w1-spec.json`: the scratch token is present, there are 65 items, and LandingGate is OWN ONLY …/tools/souji-landing-gate.py.
- Exact transcript reads via `git show ddb7347:census/round-16/transcripts/<file> | cut | cat -n | sed -n`:
  - LandingGate 1-5, 60-128;
  - MutateDirtyFilters 84-100;
  - MutateSeatAudit 80-96;
  - PreservationRepin 174-183;
  - MutateScanConfig 78-85;
  - RerunGateReplayR14 222-234.
- **Probe-rule disclosures.** Each of the following was a `read` of exact files or a non-recursive operation, but the auditor cannot see it:
  - One `grep` over the 144 transcript files, issued from `eval(py)` via `tool.grep`. Pattern `→ (edit|ast_edit)\(.*\[`. The path was the `;`-joined exact list of the 144 names from `MANIFEST.sha256`, not a directory.
  - Header forms were classified in the same kernel. Result: 26 header-edit rows; 13 absolute headers, 12 fleet-relative, and 5 other bracket tokens. Of those 5, only `tools/souji-landing-gate.py` is a path; the rest are `OBS`, `^/\s` ×2, and one parse artefact. There were 7 unclosed tails, all path-like.
  - `awk`, `tr`, `cut` and `sed -n` were used on `git show` output.
- **Peer message:** P1–P5 lines sent to SoujiR17-3.HeldOutBaseAuditor-2 so they can be executed. No reply was awaited.
- **Not done:** no lane tool runs, no jj, no git writes, and no writes except this report. Installs: none.
