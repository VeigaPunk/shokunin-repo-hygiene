# R43revenger01 — routed legacy surfaces, findings only

Axes: calibration (source/predicate fidelity) and coverage (negative-control population fidelity). No instruments or candidates changed; no counter or fixture executed, no target module imported, no tools installed. Exact computation commands, including the initial AST-reader failure and successful recovery, are in `.ufo/waves/round-43/w1/R43revenger01/commands.txt`; observed committed-byte counts are in `.ufo/waves/round-43/w1/R43revenger01/anchor-count.txt`.

## 1. S259 / E-5 — supplement the source chain; inherited C2 still depends on it

**Disposition: source gap remains load-bearing for the inherited patches leg, not for all three claims.** The r43 round needs a new source row for `using/cmdline`'s PYTHONPATH discovery mechanism to claim that the entire patches leg is registry-sourced. A superseding S259 row is appropriate for narrowing/correcting S259's own scope; the discovery page can be a separate complementary row rather than pretending the site page itself states discovery semantics. Do not rewrite S259 or the frozen counters; no particular next source ID is assumed.

Evidence chain (direct source reads; no semantic-reference claim):

- `corpus/SOURCES.md:213` scopes S259 to the startup `sitecustomize` attempt and suppression through `-S`, excludes `-I`, and cites only `https://docs.python.org/3/library/site.html`. `corpus/lessons/round-42.md:27-30` nevertheless describes the C2 patches leg as resting on S259.
- `corpus/lessons/round-42.md:222` (E-5) already narrows that statement: the site's `-S` sentence concerns the import of `site`, and PYTHONPATH discovery belongs to `using/cmdline`, with no registry row. The current registry ends at S259; no superseding row is present in the reviewed bytes. This is an acknowledged outstanding provenance gap, not a newly discovered execution failure.
- `census/round-42/c2-counter.py:332-345` writes `sitecustomize.py`, assigns its directory to `e["PYTHONPATH"]`, and launches `python3 -B tool --selftest`. The patch implementations at :298-327 modify hashlib/subprocess; :407-421 requires `patches=3/3`.
- `census/round-43/c2-counter.py:351-371` runs that r42 counter on the candidate and explicitly requires both rc=0 and `patches=3/3`. Thus the r43 C2 retention criterion still rests on this mechanism even though r43 does not introduce a new patches leg.
- `census/round-43/preregistration.txt:32` declares new C2 grounding in subprocess stderr/environment semantics. That is not documentation of CPython's interpreter-startup path processing; it does not remove the inherited dependency. C1's historical corrections and C3's drift coverage/symlink refusal have no identified dependency on S259 in this scoped trace.

Primary page opened by `read https://docs.python.org/3/using/cmdline.html` (observed title: Python 3.15.2 documentation): [§ PYTHONPATH](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH) says **“Augment the default search path for module files.”** Its `-E`/`-I` clauses document ignoring PYTHON* variables. Combined with S259's startup-import attempt, this supplies the missing documented channel; it does not prove the particular patches execute or reach every honest implementation. Historical patch observations remain historical observations, not fresh verification by this seat.

Confidence: high on the code dependency and registry gap; no claim that documentation mismatch alone makes a candidate fail C2.

## 2. Six EQUIV controls / seventeen survey equivalents — the proposed subset relation is false

**Disposition: retain the frozen six as applicable controls, but do not describe them as a subset of the seventeen.** The six are B3, B4, E5, E7, E9, H4; the seventeen are S18, S19, S28, S29, S30, S39, S41, S51, S65, S66, S67, S68, S69, S74, S75, S76, S77. Exact `(old,new)` pair intersection is **empty**, not six. This attacks the routed item's premise, not the integrity of the six frozen controls.

Commands: AST literal extraction (no module execution) of `EQUIV` from `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c3-counter.py` and survey `MUTANTS` from the pinned master, followed by `tool_text.count(old)` and pair-set lookup; exact Eval cells are retained in `commands.txt`.

Observed output, at BOTH frozen instrument commit `f8c805dbfa7f45814cf9a7270fa8bbffb41a8373` and pinned master `13de0e84b45efd1113f077d58fc1e89bc586a013`:

```
tool_sha256=b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6
EQUIV old counts: B3=1 B4=1 E5=1 E7=1 E9=1 H4=1
survey-equivalent old counts: S18=1 S19=1 S28=1 S29=1 S30=1 S39=1 S41=1 S51=1 S65=1 S66=1 S67=1 S68=1 S69=1 S74=1 S75=1 S76=1 S77=1
exact EQUIV pairs in 17 survey equivalents: [('B3', None), ('B4', None), ('E5', None), ('E7', None), ('E9', None), ('H4', None)]
working tool equals pinned tip: True
frozen c3 instrument equals tip: True
```

The earlier report itself says the survey did not repeat frozen pairs (`census/round-42/waves/w2/R42w2critic04.md:14-15,78-81`). Its line 128 mistakenly locates the equivalent table in section 5; the actual table is **section 7**, with equivalence caveats in section 6. This is a pointer error in the routed reasoning.

Applicability at these unchanged tool bytes, by direct implementation reading (not a new dynamic equivalence proof):

| Frozen control | Preserved invariant / evidence |
|---|---|
| B3 | Only regular record descriptors reach `set_blocking`; removing that toggle does not change regular-file reads (`tools/souji-worktree-drift.py:133-148`). |
| B4 | Only regular output descriptors reach the second toggle (:261-278); blocking mode does not change regular-file writes. |
| E5 | The root is already in `measured`; all appended resolved row paths and accepted gitdirs are inside that root (:292-318), so checking root alone rejects the same JSON subtree (:342-348). |
| E7, E9 | Removing either redundant contained-path append preserves that same root containment test. |
| H4 | Omitted `--json` becomes `""` rather than None; `if args.json` skips both, and `json_target` stays None (:319-320,419,444). |

**Which of the seventeen can the guard miss? All seventeen.** `census/round-43/c3-counter.py:113-120,354-356` scores only the six frozen EQUIV mutations. Preserving those six outcomes does not enforce any outcome on the distinct survey mutations; all seventeen could be falsely killed without the EQUIV leg detecting that particular error (other legs may independently reject a fixture).

The likely accidental overconstraints and their qualification are:

- **S18**: inspect the unused parse-record TOTAL return rather than CLI outcomes.
- **S19**: enforce an overly tight execution deadline, distinguishing one-byte reads by speed.
- **S28/S29**: enforce discovery/child-call order although emitted drift is sorted.
- **S30**: require a redundant isdir call when the following `.git` test implies a directory.
- **S39**: require the extra realpath call although the historical git 2.56.0 `rev-parse --absolute-git-dir` already resolves it (version-qualified equivalence, not a universal promise).
- **S41**: mock non-porcelain strings beginning `worktree` without the grammar's space, or inspect the spelling of the prefix predicate.
- **S51**: inspect spelling/calls in the record alias check although inode identity still protects aliases.
- **S65**: insist on UTF-8 encoder selection although default ensure_ascii makes JSON bytes ASCII in either encoding.
- **S66**: inspect the intermediate truncate size rather than the completed JSON write.
- **S67/S68**: compare serialized JSON formatting bytes (trailing newline/indent) instead of parsed JSON.
- **S69**: invoke the internal opener with a relative path, bypassing its CLI caller's realpath/abspath invariant.
- **S74**: require a trailing newline on stderr instead of the refusal class/exit.
- **S75/S76/S77**: inspect child environment keys rather than behavior; historical qualification is sanitized HOME/XDG, redundant `--no-optional-locks`, and the relevant attribute-free operations/host context.

These mechanisms are **[INFERENCE] possible false-kill routes**, not executed attacks. The historical labels themselves are observation-domain-relative: S67/S68/S74 do change raw bytes, S19 changes performance, S39 is git-version-qualified, and S75/S77 carry environment/host assumptions; describing all seventeen as universally having “no observable behaviour” would overstate the evidence. The guard does not even list their IDs, regardless of those qualifications. Evidence for the historical scope: `census/round-42/waves/w2/R42w2critic04.md:138-142,167-226,234` and its `mutants.py:49-52,72-78,97-103,123-124,155-183`.

Confidence: high on counts, unchanged bytes, empty intersection and guard omission; static equivalence reasoning is conditional on ordinary stable filesystem/regular-file operation and the stated observation domain. No candidate fixture was scored, so no claim that an actual r43 candidate falsely kills these mutants.

## 3. Frozen R1 predicate — two-sentence disposition

**Retire the frozen r1-counter as a next-round acceptance instrument, retaining it only as historical evidence: its required three appended exemption rows and zero deletions encode the rejected repair rather than the landed in-tree repoint (`census/round-42/r1-counter.py:8-15,69-79`; `census/round-42/waves/w2/R42w2reviewer08.md:278-299`).** **Its apparent green can also be vacuous because it ignores the gate exit status and accepts the zero-findings summary from a malformed-exemption exit-2 run (:62-79; `tools/souji-landing-gate.py:1030-1055,2467-2484`; committed independent reproduction in `census/round-42/waves/w2/R42w2reviewer08.md:301-338`), so any future instrument should newly specify successful evaluation and the actual pointer-resolution invariant instead of amending this obsolete append-three predicate.**

Confidence: high from the frozen implementation plus committed executable receipts; the historical failure was not rerun. “Unsatisfiable” in `corpus/lessons/round-42.md:217` must mean **honest successful gate evaluation**, not that counter exit 0 is impossible—the committed vacuous-green experiment disproves the latter reading.

## Method / limitations / commands

- `read xd://lsp` returned **“No such tool: xd://lsp”**. No server/device was available; direct source reads and literal searches were the fallback. Grep output is navigation evidence, never semantic-reference proof.
- Direct `read` ranges used for the core contract: `corpus/SOURCES.md:213:raw`; `corpus/lessons/round-42.md:217-225:raw`; `census/round-42/r1-counter.py:1-240`; `census/round-43/c2-counter.py:1-140,338-373`; `census/round-43/c3-counter.py:55-125`; `census/round-43/preregistration.txt:1-160`; `census/round-42/waves/w2/R42w2critic04.md:90-200,200-237`; its `mutants.py:1-220`; `tools/souji-worktree-drift.py:90-350,354-458`; `tools/souji-landing-gate.py:1030-1057,2460-2485`. Paths were supplied with the absolute lane prefix to the tool.
- Cross-check source reads: `census/round-42/waves/w2/R42w2reviewer07.md:1-160`; `census/round-42/c2-counter.py:298-355`. Literal search of the r43/r42 counters for `S259|Sourced:|patches|PYTHONPATH|SITECUSTOMIZE|r1-counter|R1` exposed the C2 handoff and committed R1 reproduction. Searching `corpus/lessons/round-43.md` reported it missing; no correction prose was assumed present.
- No fresh gate/counter/fixture execution, candidate scoring, git mutation, installation, or patch. Hence none is reported as a pass. Only the explicit static count was run. Scratch contained no fixtures and was removed with `rm -rf -- /fast/scratch/hyaku/souji-r43/R43revenger01`; retained evidence lives solely beside this report.

Report: `.ufo/waves/round-43/w1/R43revenger01.md`
