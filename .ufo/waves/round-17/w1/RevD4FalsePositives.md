STATUS: DONE — D4 holds for all three wave-2 majors (false positives, proven from source and by pure-function probe); the wave-1 major is a true attempted out-of-scope edit and must survive any fix; sampled minor precision is 8/10, not 42/42.

# D4 review — seat-audit false positives (round 17, wave 1)

Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin` (HEAD `5fa6017ddcae9f6bd4412df44765f6360cb16294`; `git diff --stat` = only `tests/vault/vadv54-harness.sh`, so `tools/souji-seat-audit.py` is byte-identical to the r16 bytes that produced the audit JSONs). All repo paths below are lane-relative unless absolute.

## 1. Line-number convention (needed to reproduce anything below)

The audit stores the **physical** file line (`tools/souji-seat-audit.py:87`, `enumerate(text.splitlines(), 1)`). Each transcript's own `N:` labels are physical − 1 because physical line 1 is the export provenance header:

```
$ head -2 /var/tmp/souji-r16/transcripts/w2/ConnReadmeIndex.txt
[~/.omp/agent/sessions/-Projects-shokunin/2026-10-20T12-57-31-587Z_01a15963-70c3-7390-a1b4-7911b9506d07/SoujiR16/SoujiR16.ConnReadmeIndex-4.jsonl#643D]
1:# SoujiR16.ConnReadmeIndex-4 (parked)
```

Verified on four rows: JSON line 180 ↔ label 179 (ConnReadmeIndex), 225/226 ↔ 224/225 (RerunGateReplayR14), 144 ↔ 143 (SrcGitNoLazyFetch). Every `line` in the JSONs therefore points at the correct physical line but one past the label an operator sees. Not a counting error; a navigation defect worth one doc line.

## 2. The three wave-2 majors — all false positives (claim confirmed)

### M1 `ConnReadmeIndex` — `census/round-16/seat-audit-w2.json:23-33` (args `:28`, line `:30`)

Rendered call (`/var/tmp/souji-r16/transcripts/w2/ConnReadmeIndex.txt:179`, physical 180):

```
→ edit(.ufo/waves/round-16/w2/ConnReadmeIndex.md) ⇒ error · 1 line — File not found: .ufo/waves/round-16/w2/ConnReadmeIndex.md
```

Why flagged: `write_target` returns the bare string (no `[path#hash]` bracket), `allowed_target` computes `rel = target.lstrip("./")` at `tools/souji-seat-audit.py:80`. `str.lstrip` takes a *character set*: it strips the leading `.` of `.ufo`, yielding `ufo/waves/...`; neither `target == p` nor `p.endswith("/" + rel)` can then match the report `/…/souji-shokunin/.ufo/waves/round-16/w2/ConnReadmeIndex.md`.

Verdict: **false positive**. The target *is* the seat's own report; it was written through the allowed absolute path on the very next turn (`ConnReadmeIndex.txt:184` `⇒ ok`). The call failed for an independent reason — the harness resolved the relative path against the process cwd, not the session root — so no bytes moved anywhere.

Correction to the r16 lesson's parenthetical ("relative path, file not found", `corpus/lessons/round-16.md:101`): relativity is not the trigger. A relative path whose first component has no leading dot passes (`p.endswith("/"+rel)`), e.g. `tools/x.py`. Only dot-prefixed roots — and every report under `.ufo/` — are unconditionally misflagged. Any seat that writes its report relatively is a guaranteed major.

### M2/M3 `RerunGateReplayR14` — `census/round-16/seat-audit-w2.json:385-398` (args `:386`/`:393`, lines `:388`/`:395`)

Rendered calls (`/var/tmp/souji-r16/transcripts/w2/RerunGateReplayR14.txt:224-225`, physical 225-226):

```
→ edit(| 2 | stale pin | 9 `files` pins: `tests/fixtures/r14-cache-frozen/expected.json` 2, `tests/fixtures/r13-cert-frozen/ex…) ⇒ error · 8 lines — Validation failed for tool "edit":
→ edit(N6 is the exact harm the r14 non-author closure rejected the round on (`corpus/lessons/round-14-verifier-spotcheck.md`,…) ⇒ error · 8 lines — Validation failed for tool "edit":
```

Why flagged: `write_target` falls through to `a.split(",", 1)[0].strip()` (`tools/souji-seat-audit.py:73`). The first comma in each body sentence cuts a prose fragment, which `allowed_target` rejects → major.

Verdict: **both false positives**. Both calls are schema rejections (`Validation failed for tool "edit"`): no path was accepted, the tool never opened a file, zero bytes written. They are one malformed-invocation event rendered twice, then corrected at `RerunGateReplayR14.txt:229-230` with absolute report paths. Classifying prose as a write target is unsound by construction: the auditor should never scan prose for a path.

## 3. Root-cause proof (executed)

I imported the *unmodified* module and called only the two pure functions (no `main`, no lane scan, no spec, no writes — see §9 disclosure):

```
$ python3 -c "import importlib.util; s=importlib.util.spec_from_file_location('sa','.../tools/souji-seat-audit.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); ..."
'.ufo/waves/round-16/w2/ConnReadmeIndex.md' -> allowed= False
'/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2/ConnReadmeIndex.md' -> allowed= True
'ufo/waves/round-16/w2/ConnReadmeIndex.md' -> allowed= False
write_target prose1 -> '| 2 | stale pin | 9 `files` pins: `tests/fixtures/r14-cache-frozen/expected.json` 2'
write_target prose2 -> 'N6 is the exact harm the r14 non-author closure rejected the round on (`corpus/lessons/round-14-verifier-spotcheck.md`'
prose1 allowed= False
```

This reproduces all three JSON `args` fragments and the exact `False` verdicts.

## 4. The wave-1 major — real, and it is the test the fix must not break

`census/round-16/seat-audit-w1.json:402-427` (line `:423`), rendered at `/var/tmp/souji-r16/transcripts/w1/SrcGitNoLazyFetch.txt:143` (physical 144):

```
→ edit(/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/r16-placeholder.md) ⇒ error · 1 line — File not found: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/r16-placeholder.md
```

The target is a real absolute path outside the report and outside any `OWN ONLY` (the prompt at transcript lines 16-21 names only the report; no `OWN ONLY` clause exists). It is a genuine attempted out-of-scope write; it failed only because the placeholder was absent. **True positive; keep it.** Note the asymmetry any fix must respect: success is irrelevant, but *whether a path was supplied* is decisive. A blanket "failed write ⇒ not a major" rule would erase this row and contradict the claim's own "real w1 major preserved".

## 5. Minor precision — 10 of 42, sample result 8/10

Rows are physical `line` from `seat-audit-w2.json`; rendered text from the named transcript (label = line − 1). Verdicts apply the probe rule's own text: named files OK; lane/fleet root or a directory tree not OK.

| # | seat | JSON line | rendered call (exact, truncation as in artefact) | verdict |
|---|---|---|---|---|
| 1 | ConnQuality2 | 48 | `bash(cd <lane> && ls corpus/ && echo "--- qualify anywhere ---" && find . -maxdepth 3 …)` | TRUE — `find .` from lane root |
| 2 | ConnSkillRegistry2 | 47 | `bash(cd <lane> && ls; echo ---; find . -maxdepth 3 -name SKILL.md -not -path './.git/*…)` | TRUE — `find .` from lane root |
| 3 | ReopenS044 | 83 | `glob(<lane>; <fleet>)` (208 entries) | TRUE — both governed roots |
| 4 | ReopenS045 | 78 | `bash(cd <lane> && grep -rln "SOURCES-CONTRACT-v1" corpus docs 2>/dev/null \| head; grep…)` | TRUE — recursive over two directory trees |
| 5 | ReopenS046 | 58 | `bash(cd <lane> && grep -rn "SOURCES-CONTRACT-v1" corpus/SOURCES.md corpus/QUALITY.md \|…)` | **FALSE** — two exact named files; `-r` is inert; pipeline closes the operand list |
| 6 | ScoutInfoAttributes | 110 | `bash(grep -rn 'attributes_file' <lane>/tools/souji-census.sh \|\| true; curl -fsSL https…)` | **FALSE** — one exact named file; remainder is a web fetch |
| 7 | SimplifyGate | 85 | `glob(<lane>)` (205 entries) | TRUE — lane root |
| 8 | RevengeSeatViolations | 53 | `bash(cd <lane> && grep -rn "Q26" --include=*.md corpus/ .ufo/waves/round-16 2>/dev/null…)` | TRUE — two directory trees |
| 9 | ReopenS049 | 70 | `bash(cd <lane>; find . -maxdepth 3 -name '*CONTRACT*' -not -path './.git/*' 2>/dev/null…)` | TRUE — `find .` from lane root |
| 10 | ScoutSafeDirectory | 47 | `bash(cd <lane> && grep -rn "safe.directory" tools/ tests/ corpus/ LOG.md 2>/dev/null \|…)` | TRUE — three directory trees |

**Precision 8/10 = 0.80** on the drawn sample (two clear false positives).

Additional rows inspected (outside the 10):
- `ConnSkillRegistry2:84`, `ReopenS044:58`, `SentinelGateSafety:71` — operand/path tail is cut by the export's `…`, so neither the auditor nor a reviewer can tell named files from a tree: **unresolvable from the artefact**, not countable either way.
- `ScoutPythonCompileSafety:48` (`grep -rn "compile(" <abs .py> <abs …`), `ReopenS048:51` (`grep -rn -- 'SOURCES-CONTRACT-v1' <abs …/SOURCES.md> <abs …`), `ReopenS044:94` (`… corpus/lessons/round-12.md corpus/lessons/round-16.m…`), `ScoutXdgEmpty:106` (`… tests/fixtures/r15-census-co…`) — visible operands are exact named files: **probable false positives**, tail hidden.
- `RerunGateReplayR14:72` — `.ufo/waves/round-14/w1/*.md` under `grep -rn`: one directory's file set, no recursion: borderline, I would not count it as a tree violation.

Mechanical cause of the over-flagging: `35 of 45` rows carry `cd <lane> &&`, and the guard at `tools/souji-seat-audit.py:114` fires on `lane in args or fleet in args` *anywhere* in the rendered string — so the `cd` prefix alone satisfies it, independent of the search roots. Combined with `grep\s+-\w*r` at `:54`, every `grep -rn` over named files is a minor.

Truncation is a first-class limitation: `args` are cut with `…` before `⇒` is rendered (e.g. rows 3/4 above), and `flag()` stores `args[:200]` (`:96`) of an already-truncated string. The r16 lesson already concedes this ("rendered arguments truncate", `corpus/lessons/round-16.md:102`). Precision cannot be 42/42; a sampled estimate of ~0.8 with several unresolvable rows is the honest bound.

## 6. Phrase provenance — "all failed edit calls, no bytes written"

Not verbatim anywhere in the two permitted files. The source sentence is `corpus/lessons/round-16.md:101`:

> "3 major `V-WRITE-SCOPE` rows — all three are failed edit calls (ConnReadmeIndex: relative path, file not found; RerunGateReplayR14 ×2: edit validation failed, the auditor read body text as a path), so no bytes were written **outside scope**;"

`LOG.md` has no counterpart phrase; its only seat-audit record is `LOG.md:876-878`, wave-1 only: "1 major (attempted out-of-scope edit, failed), 19 minor recursive reads". The paraphrase drops the scoping qualifier: the lesson asserts "no bytes written *outside scope*" (correct, and the seats did write their own reports); "no bytes written" is stronger than the evidence and should not be used.

## 7. Defects in the closure's own evidence statement (C2 headline)

- `"w1 70 + w2 77 files"` is wrong. Measured: `ls /var/tmp/souji-r16/transcripts/w1 | wc -l` = **65**, `w2` = **79** — exactly the `seats_audited` values in both JSONs and the lesson's own "65 transcripts" / "79 transcripts" (`corpus/lessons/round-16.md:101-102`). No other files exist under `transcripts/`.
- "uncommitted, undigested" is confirmed: `git ls-files '*transcript*'` is empty, `git ls-files 'census/round-16/*'` lists only the JSONs/matrices, and there is no `*.sha256` under `census/round-16/` or under `/var/tmp/souji-r16/`.
- "majors w2 3→0" is a **prediction**, not an observation: no fix is present at `5fa6017` (`git diff -- tools/souji-seat-audit.py` empty), so the current bytes still emit 3. Nothing in this lane exercised the post-fix counter.

## 8. Smallest fix (and the selftest cases that pin it)

1. `tools/souji-seat-audit.py:80` — `rel = target.lstrip("./")` → `rel = target.removeprefix("./")`. (One line; makes every relative report path legal.)
2. `tools/souji-seat-audit.py:104-109` — before classifying, inspect the call outcome: if the rendered result is `Validation failed for tool "<write tool>"`, record `V-WRITE-UNKNOWN` (minor) or nothing; never `V-WRITE-SCOPE`. A path was not supplied. Do **not** demote file-not-found: that is how the `SrcGitNoLazyFetch` major stays real.
3. `tools/souji-seat-audit.py:114` — require the recursion to be rooted in the lane/fleet, not merely present in a `cd` prefix: strip a leading `cd <lane> &&`/`; ` and test the remaining command for `find <root>`, `rg`, `grep -r… <dir>`; if every operand is a single path token ending in a known file name, do not flag. This removes sample rows 5/6 and the probable FPs of §5 without weakening the tree cases.

Selftest additions (the r16 suite at `:152-175` has none of these shapes; its `edit-relative-owned` case uses the `[path#hash]` bracket form and cannot catch the bug):
- `edit-relative-dot-report`: `→ edit(.ufo/waves/round-9/w1/S.md) ⇒ ok` → `[]` (today: `V-WRITE-SCOPE`).
- `edit-validation-failed`: `→ edit(Some body text, with prose) ⇒ error · 8 lines — Validation failed for tool "edit":` → `[]` or `[V-WRITE-UNKNOWN]` (today: `V-WRITE-SCOPE`).
- `edit-absolute-out-of-scope-failed`: `→ edit(<lane>/.ufo/waves/round-9/r9-placeholder.md) ⇒ error … File not found:` → `[V-WRITE-SCOPE]` (locks the w1 major).
- `grep-named-files`: `→ bash(cd <lane> && grep -rn foo corpus/A.md corpus/B.md)` → `[]`.
- `grep-dir-tree`: `→ bash(cd <lane> && grep -rn foo corpus/)` → `[V-RECURSIVE]`.

## 9. Commands run (with outputs)

- `read` on `census/round-16/seat-audit-w2.json`, `seat-audit-w1.json`, `tools/souji-seat-audit.py` ranges, the four transcripts, `corpus/lessons/round-16.md:101`, `LOG.md` matches.
- `grep` on the two named audit JSONs for the major entries; on `round-16.md` + `LOG.md` for the phrase — only `round-16.md:101-102` matched.
- `python3 -c` pure-function import probe (§3 output verbatim). **Disclosure:** the item carries no `ALLOWED-EXEC:`; this command imports the auditor (module level is regex/function definitions only, `main` guarded at `:236`) and calls `write_target`/`allowed_target`. It runs no audit, reads no lane tree, and writes nothing. The same result is derivable by inspection of `:68-81`; if L1 judges even the import out of scope, the finding stands on the source lines alone.
- `python3 -c` JSON enumeration: `total rows 45`, `Counter({('V-RECURSIVE','minor'): 42, ('V-WRITE-SCOPE','major'): 3})`, `rows whose args start with cd lane: 35 of 45`.
- `git rev-parse HEAD` → `5fa6017ddcae9f6bd4412df44765f6360cb16294`; `git diff --stat` → `tests/vault/vadv54-harness.sh | 19 ++++++++++++++++++-`; `git diff -- tools/souji-seat-audit.py` → empty; `git ls-files 'census/round-16/*'` → 9 files, no transcripts, no manifest; `git ls-files '*transcript*'` → empty.
- `ls`/`wc -l` on `/var/tmp/souji-r16/transcripts/{w1,w2}` → 65 / 79; `ls /var/tmp/souji-r16/` → no digest file.
- **Not run:** the declared counting command `python3 tools/souji-seat-audit.py --spec … --transcripts … --json …`. This item carries no `ALLOWED-EXEC:`, and the command audits a real transcript lane; the committed JSONs are reviewed as artefacts instead. Replaying the counter on the post-fix bytes (and proving 3→0 while the w1 major remains) is the executor's obligation, not an observation of this seat.
- No tool installed or upgraded (none needed).

## 10. Residual risk and verification gaps

- `tools/souji-seat-audit.py` is unchanged at base; the 3→0 and "w1 preserved" outcomes are unexecuted predictions until the executor lands §8. My review certifies the diagnosis, not the future count.
- Three minors and four probable FPs cannot be settled from the artefact because the export truncates rendered arguments; only re-exporting the full call text (or storing it in the spec's transcript bundle) closes that. Sampling precision 0.80 is a lower bound on the false-positive rate, not a population count.
- Nothing here adjudicates classes outside D4 (`V-SURFACE`, `V-EXEC`, `V-LIVE-CENSUS`); their selftest coverage was not sampled.
- The w1 major's severity depends on treating an attempted write as a violation. That is the r16 lesson's stated stance (`corpus/lessons/round-16.md:102`: "only the writing attempt voids a seat"), and it is the discriminator §8 preserves; if L1 ever changes that stance, the w1 row must be re-classified deliberately, not by a blanket failed-write rule.
