author: hyaku closure (non-author integrator, @m_opus)

# Round 19 — non-author closure and verifier spot-check

## Decision and scope

**Status: ok; admitted: false; verdict: rejected-harmed.** This is a real, landed round, not a completion marker. The carry improvement and the F5 observation entry have useful, checkable evidence. They do not cancel the auditor's newly overbroad authorization or the counter-command contraction. C1's broad exact-authorization claim and C2's broad measured-byte guarantee do not verify. No claim is exploratory; `unprovable-but-better` is not a substitute for missing measured evidence.

Reviewed baseline `3ab2c81479f5004c8bc91946eea482caec45408f` and final author/evidence tip `e6df080a60cae997bfcd387738a87aa449c85484`. The original fleet report is `cf557a61f6b88916086ba3bcddb27088e4e69836`; its twenty append-only errata end at `ac035c0074ca5ee07944cd62f61287f00fed6468`.

This closure ran only committed-byte measurements, read-only repository checks, public source reopens, and the prescribed source-census validator. It did **not** run a lane gate, acceptance runner, fixture, selftest, process census, signal, cleanup or reap. No private configuration, secret value, vault, host/service/package/boot/compositor surface was opened. `census/operator-sweep-20261019/` was neither opened nor traversed and is not unfinished lane work. No tools were installed or updated. Five read-only reviewer seats covered carry, auditor, revision bindings, F5 sources and conformance; this integrator performed the plain measurements below independently and adjudicates the whole-round verdict.

Driver digest copied from the closure dispatch's mutable-log extract:

- `2026-10-21T00:38:34-03:00 launch souji round=19 pgid=2971251 driver=hyaku-inline attempt=1`
- `2026-10-21T04:52:12-03:00 complete souji round=19; hyaku-inline attempt=1`

## Step-1 conformance

| check | command / committed evidence | observed | judgment |
|---|---|---|---|
| Report authorship and durability | fleet `git log --follow --format='%an %H' -- .ufo/reports/round-19/souji.md`; adjacent report blobs compared as byte prefixes | 21 versions, all `souji-shokunin`; original and latest hashes above; all 20 transitions preserve filed bytes; twenty Erratum headings | pass |
| Report substance and SHONEN | report Work/Landed/Measurements/Sources/Trends/SHONEN sections | real work and resolvable commits; four `[~]` lines | `ok`, not a marker; no promotion marks written |
| Cited lane commits | `git cat-file` and `git merge-base --is-ancestor <hash> refs/heads/master` | reviewer resolved 27 unique cited lane commits, zero non-ancestors | pass |
| Pushed author tip | `scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/souji-shokunin` | branch master; local=remote=`e6df080a60cae997bfcd387738a87aa449c85484`; ahead=0, behind=0, detached HEAD, tracked=0, untracked=1 | pass |
| Leftovers | `GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain` | only `?? census/operator-sweep-20261019/` | inherited operator-owned exception, untouched; not author debt |
| Prompt fidelity | committed rendered template prefix vs `.ufo/prompts/souji-round-19.md` | sections 1–5 match rendered template; §6 supplies lane-write scope, report-last ordering and pushed-hash citation | actual dispatch passes; reusable-template omissions routed below |
| LOG append-only | compare `git show <base>:LOG.md` and `git show <tip>:LOG.md` as bytes | final begins with the entire baseline blob; +6,586 bytes. Baseline lacked final LF, explaining numstat's apparent one-line deletion | pass; no historical rewrite inferred |
| SCORECARD no-trade review | `git diff <base> <tip> -- SCORECARD.md` and scoped reads | coverage 8, calibration 7, operability 8 remain legacy-unmapped; four capability rows added; numerical scores do not prove no harm | harms below prevent admission |

SHONEN is not certified fully checkable: exact authorization, provenance completeness, runnable copied commands and F5 wording remain open. Promotion remains operator-owned.

## Plain measurement method

All `git` commands in this lesson use `git -C /home/vgpnk/Projects/shokunin/souji-shokunin`. `base` and `tip` mean the two full reviewed hashes above. Plain Python analysis used `subprocess.check_output(['git','-C',lane,'show',rev+':'+path])`, `json.loads`, `ast.parse` without importing target code, and `hashlib.sha256`. It never executed a target module.

For SOURCES, split only lines matching `^\|\s*S\d{3,}\s*\|` into their eleven cells. For knowledge, enumerate committed `corpus/knowledge/*.md`, require the initial `source:`, `verified-at:`, `recheck:` trio, and exclude the entry with `## Admission status — HELD`. For audits, sum `.seats[].calls` and count `.seats[].violations[]` by `severity` and `class`, rather than trusting only the supplied summary.

## Per-claim verification

### C1 calibration — carry evidence verifies; broad auditor claim fails and introduces harm

| measurement | plain command / evidence | observed |
|---|---|---|
| Carry selftest size | AST of committed `tools/souji-landing-gate.py` `run_selftest`; expand literal case loops | baseline 52 syntactic `check` sites +3 loop repetitions +6 manual cases = **61**; final 56+3+6 = **65**. Initial intermediate arithmetic omitted the loop expansion; 58/62 is superseded, not a runtime result. |
| Carry behavior receipts | baseline `census/round-18/final-verification-4800fd7.json`; final `census/round-19/final-verification-bbeb73b-fixed.json` | baseline `SELFTEST pass=61 fail=0`; final 65/0; carry fixture **4/0**, `base_discriminating=2`. Both recorded base mismatches are present. |
| Invariants | committed `carry-invariants.txt` and unchanged probe source | **400** paragraphs, **562** boundary cuts, **842** mid-line cuts, **0** violations; receipt evidence, not rerun |
| Auditor receipts | final fixed acceptance record and `c1-audit.txt` | baseline 66/0 is supported by the r18 `RevSkillRegistryNumbers.md:32` run and unchanged baseline source; final selftest **73/0**, fixture **7/0**, three base discriminators. The initial five-case fixture receipt is superseded by the seven-case result. |
| Re-audit row counts | `json.loads(git show tip:census/round-{18,19}/...seat-audit...json)`; sum calls and violation rows | W1 **4,132 calls /91 seats**, major **139→134**, minor18; W2 **2,859 calls /79 seats**, major **92→92**, minor16. W1 removes 7 scope +1 relative-write rows and adds 3 `V-SIGNAL` rows. |
| Re-audit class decomposition | same committed row count | W1 scope119→112, relative13→12, V-SIGNAL0→3; other classes unchanged. These are classifier rows, not three independently adjudicated historical violations. |

Carry scope and actual frozen denominators:

| replay | revision | exit / findings | reports / markers / STATUS lines |
|---|---|---|---|
| r13-admitted | `a31642d14006830ec62edf40b0354c3699728c4a` | 0 /0 | 32 /0 /1 |
| r14-landing | `cc2168325768d5356a82c039dcdf787377c55784` | 0 /0 | 32 /0 /0 |
| r15-landing | `b410186cea626a67c92396ac58fbd57fb86876ac` | 1 /5 | 64 /1 /17 |
| r16-landing | `6ff91f534eece9adde5f667cb7dad400c145351b` | 0 /0 | 141 /30 /146 |
| r16-precarry | `79bbe7a62199260694943ec7186fef6ebff9d41a` | 1 /29 | 141 /30 /146 |

`census/round-19/gate-replays-final-bbeb73b.json` contains exactly these five semantic exit/finding-multiset matches. Its gate is labeled WORKTREE with a digest matching the committed final gate. `gate_sha256_match=false` means the gate differs from the historical expected gate digest; it is **not** byte-identical replay or a clean verdict for the red historical arms. Strict wrap parsing starts at round18. The seven known r16 cuts are not repaired or retro-certified by preserving r16's old result.

The strict r18 receipt `gate-r18-strict-fleet.json` resolves baseline `3ab2c814…`, exit0, **175 reports /172 STATUS lines /10 markers**, 487 pointer tokens, 33 registry rows, 13 pins, 3 measured records, 4 exemptions and 3 fleet pointers. `gate-at-commitB.json` instead binds `63bb8878bace9f814c1d94a8c7932b37da1259c8`, exit0, the same 175/172/10 denominator, 534 pointer tokens and 39 registry rows. Neither receipt grades the final e6df080 tree.

**Why C1 does not verify as declared:** final `tools/souji-seat-audit.py:274–277` unconditionally grants all five same-stem `.patch/.py/.json/.tsv/.txt` artifacts. The actual w1/w1b contract permits ONE sibling artifact **only if the item explicitly asks for its exact name**. The new allowance therefore clears shapes the contract did not authorize; exact spelling of the stem is insufficient. This is a static predicate/contract contradiction, not a claim that a seat exploited it. It is a calibration harm relative to the baseline's stricter allowed set. Useful carry improvements cannot trade it away.

Additionally, `run():309–326` derives scratch from `souji-r\d+-`, dropping the W2 slot spelling `souji-r19w2-<Name>`; slot-qualified authorized paths can remain false majors. The signal matcher now includes `os.killpg/killpg`, but the committed seven-case fixture has no specific killpg case; the report's direct probe is a narrower author observation. Visible `sudo kill` shapes remain outside the shell regex; `kill -0` and quoted Python/search-text matches are precision risks, not observed new false-positive incidents. Spec validation, lexical symlink limits and exact `OWN ONLY` exceptions remain external/bounded assumptions.

**Transcript binding:** the committed r18 manifest has **170** entries (91 W1+79 W2); independent SHA-256 comparison against every committed listed blob yields **0 mismatches**. Spec, result and transcript seat-name sets agree and both re-audits report missing=[]. However, the re-audit JSONs bind no auditor/spec/manifest/transcript digests. Set membership and recorded totals verify; exact input-byte/run provenance remains unprovable. Final acceptance binds the auditor code, not retroactively the re-audit invocation. JSON field names `args` and `target` are schema names, not evidence of private values. The code stores raw/truncated arguments rather than promising redaction; the input transcript secret scan does not prove derived-output redaction. No argument values are copied into this lesson, and no secret leak is asserted.

### C2 operability — real narrow guard, incomplete binding and bounded regression

Plain AST extraction of the committed lists gives **12** r13 measured paths, **8** r14 measured paths and **6** cache-demo measured paths. Static source and receipts support a real lowercase full-40-hex/durable-ref guard, excluding refs/jj roots, and `git diff --quiet <rev> -- <listed paths>` before writing runner records. Both count consumers read committed data with `tree_check=False`, intentionally permitting historical revisions; that is not a worktree-equality assertion.

`c2-smoke.txt` records helper11/0 and fixture13/0 with six base discriminators; both counter default-HEAD refusals exit2, and the r13 runner refuses a dirty listed path with exit2 and NO_OUTPUT. The final acceptance records both count commands using the full bbeb73b hash and the cache demonstration succeeding on clean bytes. These receipts verify only those entry points and cases.

The broad measured-byte claim remains **unprovable**:

- Both runner path lists omit `tools/souji-rev-pin.py`, although they dynamically load it.
- r14 omits `run-targeted.py`; that wrapper calls the resolver, executes and stamps a record without checking its own bytes.
- r14 executes `tests/fixtures/r14-cache-frozen`, but its three tracked dependency/expected/record files are outside the measured list and before/after digest set.
- r13 computes source/admission fields from worktree `corpus/SOURCES.md` and `corpus/knowledge` at lines455–469, outside its twelve paths. A blanket claim about every measured field therefore exceeds the binding boundary.
- The five fixture WIRING cases are static checks, not caller-level dirty/refusal runs. The acceptance runs neither full runner nor `run-targeted.py`. The r14 `import sys` repair removes the obvious error-handler NameError, but the committed C2 smoke and final acceptance contain no direct r14/targeted refusal receipt.

**Bounded operability harm:** the strict resolver refuses the still-published abbreviated commands. `LOG.md:591–594` and r13 `counts.json` use `31984f4`/`6f8ee0f`; `LOG.md:695–698` and README examples use `a31642d`/`552cae4`. My plain LOG regex found two explicit `count-claims.py <short-id>` tokens (the other arm is expressed as “same command”); both are shorter than40 and rejected by the committed COMMIT_RE. r14's saved JSON uses full hashes, but the displayed commands still contract. Erratum11 acknowledges this; disclosure does not migrate the affected replay instructions or erase the no-trade rule. Keep the intended durable/full-ID safety rule; migrate the documented callers with append-only historical corrections rather than silently restoring unsafe stamps.

The helper also inherits ambient repository-selection variables from `os.environ`. **[INFERENCE]** `GIT_DIR/GIT_WORK_TREE` can make the selected repository differ from the supplied root; no such behavior was exercised here. Route this as a bounded follow-on review, not as an observed failure.

### C3 coverage — measured improvement for the list-only observation surface

Independent committed-tree census agrees with admitted-marked markdown **6→7**: 7→8 markdown files, one HELD entry at each revision, and the TSV ledger excluded. The only new knowledge path is `corpus/knowledge/process-residue-observations.md`, with the provenance trio, recheck paths, SKILL rule, README Core row and appended PROVINCE refinement. The process-census implementation is byte-identical at baseline/final, SHA-256 `37c3316a1fd8cdda18cbefdc7692d3d3f388e5783e8fe19085f5d932a8ceba64`; zero `environ` identifiers occur in that code. C3 counts do not depend on executing either migrated counter.

| registry measurement | baseline | final |
|---|---|---|
| rows | 78 | 88 |
| A/B/C | 74/3/1 | 84/3/1 |
| mined/queued/rejected | 59/15/4 | 69/15/4 |
| malformed eleven-cell rows | 0 | 0 |
| SOURCES SHA-256 | `74c5e01ec6f5f1b3108d2b418dfaa970b92d3f6467ce58e067702dd745170f26` | `436b015c79386b0931641ffe01f4af4c416163e33f8ceed4fd1061a5da72ecff` |

The report's original78→85 and mined59→66 are correct **at005f3d3**. S086–S088 subsequently add three superseding rows, not three additional knowledge entries. Erratum19 and committed `source-census.json` correctly record final88; no stale85 value is substituted for the final denominator here.

This verifies C3's narrow observation coverage, **not** a complete process enumeration, secret-free read, universally redacted output, liveness proof, cross-UID ownership grant or permission to reap. The entry's broad per-process wording omits self/descendant exclusions and unreadable/racing-data skips. Its appended read-set correction names uptime/boot_id/proc listing, but Q32's older read-set text is not fully superseded. Raw argv is read before redaction; `reason` is sanitized separately from `cmd`. **[INFERENCE]** An argv-derived credential-shaped path might therefore bypass command redaction in `reason`; no payload was constructed, no runtime leak observed, and no value inspected. The entry still cites S083–S085 rather than their S086–S088 narrowing rows. Those are routed precision/provenance debts, not permission to inspect private data.

F5 reap and NAMESPACE_SHA256 remain held. The README's broad `souji | round-16` pointer must not be substituted for the specific open `souji | round-18` requests. The inherited 58-orphan observation is historical/advisory, not a current count or cleanup authorization. Certification remains OFF; K5 remains HELD.

## Acceptance and wave evidence

`final-verification-bbeb73b-fixed.json` names measured commit `bbeb73bd4dad181b9b293b242dbf5749acbe3568`. Independent JSON count: **18 results /18 matched /0 failures**. Its fifteen stored file digests all match bbeb73b; fourteen match final e6df080. The sole later hashed-file difference is `tests/fixtures/r17-census-hygiene.py`, SHA-256 `9dc50de6…`→`367b3bcb8013a860cbde763f472874a154c4e82986441adc53125da2d1bad556`, for the UnicodeDecodeError guard. Erratum18 reports a separate29/0 rerun, not full acceptance at final. `run-acceptance.py` also changes its replay-output naming after bbeb73b and is outside that receipt's digest map. The earlier failed receipt is retained: gate-replays exit2 refused an existing output; it is not concealed or misread as a product failure. The later fixed receipt proves its stated revision, not final-tip-wide acceptance.

Wave bookkeeping is not “zero seats”: the first 68-seat attempt was entirely refused, followed by68 starts,0 dead,22 packing-unexecuted items. The packed spec has68 distinct items; the22 names exactly equal original90 minus packed68. There are **67 committed Markdown reports**, plus the JSON registry, under w1. `ReviewerRevPinHelper` is in the packed set but has no committed report. This proves a missing report, not a dead seat; no replacement or respawn was requested. The registry actually retains **90 members**, not the Erratum1 wording “68-member registry.” All available evidence is committed, but that does not imply all68 reports or a transcript export exist. Wave2's65-item spec is preparation only; no wave2 execution is claimed. The r19 transcript export and an r18-style census matrix were not produced.

The numeric L2 floor is met by68 actual starts. Planner/executor participation in the original contract is not inferred from the90-seat plan: the packed retained seats are read-only falsifiers, the22 build items were not executed, and wave2 did not run. R19-M7 honestly records the private synthetic-Git fixture/blanket no-mutation conflict; no killed-mutant claim is awarded for the refused rev-pin mutations.

Two Q26 read deviations remain disclosed: ScoutCountClaims' initial broad search reached the operator-sweep subtree, and ConnToolsPatterns listed its metadata. Neither is erased, rerun or used as proof here. The abbreviation finding was independently derived from committed LOG/README/receipt bytes; the duplication findings need no operator-sweep output.

## Discernment spot-check and public source reopens

Reopened on2026-10-21 using the reader tool; no source was executed.

| item | decision being checked | reopened source/location | agree/disagree | reason |
|---|---|---|---|---|
| S082/F5 kernel fact | admit/mined in r19 Gate | https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html, DESCRIPTION, man-pages6.19 (2026-02-08) | agree | “This is a symbolic link to the current working directory of the process.” is exact, **13 words**, ≤25. Ptrace-access wording is present; no cwd deleted-suffix guarantee is attributed to this page. |
| S084 teaches, superseded by S087 | reject the original **teaching attribution**, not the source | https://man7.org/linux/man-pages/man5/proc_pid_wchan.5.html, DESCRIPTION | agree with narrowing | The15-word sleep-location quote is exact. “Never proof” is lane policy/inference, not page text; the appended lesson correction and S087 appropriately separate it. |
| proc_pid_stat field22 proposed duplicate | linked r19 source exclusion, not a formal Gate reject row | https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html, DESCRIPTION field22; `w1/ScoutSourceSearch.md` | agree | starttime is documented in clock ticks; S075 already covers this, so no duplicate new row is needed. |
| S032 historical actual rejected source | reject repository-cleanup use; supplemental standing-reject sample | https://git-scm.com/docs/git-filter-branch, WARNING (last updated2.44.0, unchanged through2.56.0) | agree | The official warning says “its use is not recommended,” describes history-mangling pitfalls, and history rewrite remains outside Souji's province. This is a real rejected row, not an invented r19 reject. |

The mandated admit and reject **source reopens** were performed. The stronger instruction to sample an actual r19 `## Gate` source rejection cannot be satisfied by relabeling the source correction or the standing r16 rejection: the r19 Gate has **no explicit source-reject catalogue**, and all S079–S088 are mined. That absence is a conformance defect and blocks a positive current-round discernment trend. The linked exclusion and narrowed teaching are recorded as what they actually are. The four final `rejected` statuses are pre-existing; no new rejected source row is fabricated. SOURCES has no r19 search-log entry; its last bounded search account is r18. S086–S088's corrections reuse the earlier pages/quotes; full per-new-row Gate accounting still needs explicit treatment.

Prescribed `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` ran once: **exit0, souji ok,17 W04 duplicate-URL/scope warnings, no errors**. These warnings are not17 bad rows and are not a failed validation. This is the only lane-related validator this closure executed.

## Axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | **harmed** | C1 carry improves, but unconditional five-suffix clearance contradicts the exact per-item grant rule; broad C1 authorization and input-bound re-audit claims do not verify. |
| operability | **harmed** | Narrow revision guard works on listed paths, but copied documented short-ID replay commands contract without migration; full provenance and caller refusal coverage remain unproved. |
| coverage | **improved** | C3 adds one sourced list-only F5 observation entry,6→7 admitted-marked entries; the count and documentary boundary verify, with precision debts explicitly limited above. |
| depth | unchanged | no separately claimed/measured move |
| freshness | unchanged | source reopens and later receipts do not establish a separately measured freshness gain; S038 drift remains routed |
| adjacency | unchanged | no new authority granted; the wording assigning all other-UID residue to Mori is not an ownership adjudication |

## Learning trends

- **expansion: improved.** One net new F5 observation entry and its coverage-map row are real, with mined primary sources and independently measured6→7. Sources78→88 is supporting curation, not ten knowledge entries. This does not admit the whole round or expand reap/private-data authority.
- **quality: harmed.** The newly broadened auditor allowance is less faithful to the actual grant rule, while formerly runnable displayed count commands are now un-migrated refusals. Better carry and source narrowing cannot cancel these losses. Provenance omissions and stale read-set wording remain open rather than passed.
- **discernment: unchanged.** The sampled admitted fact and standing rejected source agree, and rejecting the over-attributed teaching is sound. But no actual current-round Gate rejection catalogue exists, broad C1/C2 claims fail outside review, and their disagreements have not yet become landed corrections. No improved current-round outside-discernment verdict is awarded.

## Routed defects and held decisions

These are closure findings, not authorization to begin another round or edit author files during this closure.

1. **Souji — exact auditor authorization (blocking C1/no-harm):** derive sibling permissions from each item's exact requested artifact instead of granting every suffix. Preserve tools/tests/census/corpus refusals except exact OWN ONLY contracts; retain lexical/symlink limitations. Add contract-class evidence for unrequested same-stem artifacts and slot-qualified scratch roots.
2. **Souji — audit precision/provenance:** bind auditor/spec/transcript-manifest/input bytes in re-audit receipts; distinguish retrospective classifier rows from historical contract violations. Review slot spelling, sudo signal shapes, existence probes and quoted tokens; preserve no-private-value reporting. A secret scan of inputs is not an output-redaction proof.
3. **Souji — complete runner binding and caller evidence (blocking C2):** inventory actual code/fixture/corpus inputs, include helper/targeted/frozen inputs or narrow each record's claim, and commit caller-level refusal/no-output observations at measured revisions. Retain real red observations. Review inherited Git repository-selection environment as an unexercised risk.
4. **Souji — clean cutover of replay commands (operability harm):** migrate current examples to full durable hashes, append named corrections for LOG/record history, and demonstrate the documented entry points. Do not rewrite old receipts or remove the full-ID guard merely to make old text pass.
5. **Souji — F5 precision and source accounting:** narrow enumeration/redaction/read-set statements, name source/code/fixture bindings and skipped-data limits, reference S086–S088, supersede Q32's stale read list, add r19 search accounting and actual admit/reject Gate decisions. Keep the potential reason-field issue labeled inference until safely evidenced; no live private-value probe is authorized.
6. **Souji — wave record accuracy:** resolve the missing ReviewerRevPinHelper report as unavailable unless it actually lands; correct the90-member/68-item distinction append-only. Preserve first-refusal/start/dead/unexecuted distinctions and wave2-not-run disclosure; do not respawn a dead/refused seat from this closure. No report or transcript completeness is fabricated.
7. **Souji — fixture and containment residuals:** carry fixture should enforce both recorded base discriminators and summary counters; D5 identity recheck remains bounded with a check-to-signal window and a later killpg outside that per-PID check. The late UnicodeDecodeError repair has only its separately reported29/0 evidence, not final-tip-wide acceptance. S038 anchor drift and r16 carry-history disclosures remain open.
8. **Protocol/template owner — reusable prompt fidelity:** move explicit child write scope, commit-before-report ordering and pushed-hash citation obligations into the reusable template. This dispatch's addendum supplied them; no dispatched-prompt failure or marker is inferred.
9. **Operator/Kagi/Mori/Tsukuroi boundary:** F5 reading-before-redaction and all-other-UID wording require explicit scope reconciliation; field names are not secret values. F5 reap and NAMESPACE_SHA256 remain held under the specific round18 L0 requests. Historical advisory census rows authorize no cleanup, quarantine, signal or reap. Certification OFF and K5 HELD are unchanged.

Only this non-author lesson is written in the lane. No report, author lesson, SCORECARD, LOG, SKILL, PROVINCE, SHONEN, runtime, or operator-owned sweep was edited.
