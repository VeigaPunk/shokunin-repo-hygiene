# R43scout03 — C2 inherited part-A gap crosswalk

## Verdict and scope

**Actual count: 30 mutant IDs = 13 inherited M gaps + 17 new W gaps.** M61/M62 are excluded: the r42 real leg already observes them. The inherited w2 numbered list has 13 entries but groups M28/M29 and includes M61/M62 together; use the w3 GAP rows, not the numbered-item count.

Source inspection identifies **2 directly covered witnesses (M31, W29), 27 remaining named limits, and 1 superseded r42 expectation (M59)** whose exact first-empty-Target witness remains untested. Thus **28/30 historical witnesses lack direct r43 case enforcement**; this is not a measured mutant-survival result. No candidate, counter, selftest, or mutation run was performed.

Axes: faithful transcription; exact case observability versus normative requirements; frozen-byte provenance. Findings attack the completeness of **C2 r43 newtable/hidden coverage**, not candidate correctness. No frozen instruments were edited.

## Evidence sources

All paths below are lane-relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`.

- A: `census/round-42/waves/w3/R42w3mutationtester01.md`, lines 279–309 and 311–352: 13 M GAP rows, 17 W gap descriptions; lines 14–37 state 30 gaps no r42 leg observes.
- B: `census/round-42/waves/w2/R42w2mutationtester01.md`, lines 124–140: inherited witness behavior.
- G: `census/round-43/c2-counter.py`, lines 11–26: normative grammar; lines 116–188: visible builders; lines 209–215 and 279–304: class-multiset/exit oracle; lines 330–350: hidden audit invocation; lines 351–371: r42 retention invocation.
- V: `census/round-43/c2-cases.tsv`, lines 6–14: nine visible cases.
- H: `census/round-43/c2-hidden-audit.py`, lines 47–88: builder; 100–122: class projection and ten scenarios; 135–160: invocation/oracle.

`covered-by` below is a source-level inference about the specific historical witness. It is not a guarantee for every spelling or implementation, and it does not claim a mutant was re-executed. High confidence in transcription and explicit scenario presence/absence; candidate-specific kill outcomes are unmeasured.

## Thirty-row crosswalk

| ID | One-line r42 behavior change (A/B) | covered-by / r43 disposition |
|---|---|---|
| M02 | Accept uppercase Base hex, changing BASE-UNRESOLVED to clean. | **Named limit** — V/H only generate ordinary lowercase commit IDs; no uppercase Base. |
| M03 | Accept a 41-character `--rev` instead of refusal exit 2. | **Named limit** — V/H pass git-generated full commit IDs; hidden h10 tests missing prereg, not malformed revision. |
| M09 | Preserve trailing key-value blanks, making padded Base unresolved. | **Named limit** — h1 pads Round only; no Base/key-value trailing-blank witness. |
| M13 | Reject a BOM before Round, previously clean. | **Named limit** — no BOM-bearing Round in V/H. |
| M15 | Treat `EXIT=1 (red)` as a red control instead of CONTROL-NOT-RED. | **Named limit** — control contents use canonical EXIT lines or symlink link text, never trailing prose. |
| M18 | Honor git replace refs, changing freeze verdict/exit behavior. | **Named limit** — no V/H builder installs replace refs. |
| M22 | Crash with embedded NUL Counter path instead of COUNTER-MISSING. | **Named limit** — no NUL path in V/H. |
| M28 | Drop `--reverse`, selecting newest prereg addition after delete/re-add. | **Named limit** — V/H do not delete/re-add prereg; frozen-edit-prereg edits an existing file only. |
| M29 | Select `ids[-1]`, likewise choosing newest rather than oldest prereg addition. | **Named limit** — same absent delete/re-add history as M28. |
| M31 | Report missing Round as FIELD-EMPTY instead of FIELD-MISSING. | **Covered by V `round-missing`** — exit 1 with exactly C0:FIELD-MISSING; G builder explicitly removes the Round line. |
| M40 | Keep newest dispatch addition, overlooking dispatch deleted and re-added after freeze. | **Named limit** — h7/h9 add early dispatch files once; no deletion/re-addition. |
| M43 | Treat whole digest-less `census/c1.py extra` as path, returning COUNTER-MISSING rather than COUNTER-DIGEST. | **Named limit** — all V/H Counter values carry valid full digests; no fallback-with-trailing-text witness. |
| M59 | Evaluate duplicate first-empty Target, adding FIELD-EMPTY to KEY-DUPLICATE. | **Superseded by G first-wins grammar**, not a defect to restore: first value must now be evaluated. V `dup-key-first-bad` forces Base evaluation, but neither V nor H has first-empty Target; that exact witness remains an enforcement limit. Do not claim the historical mutant is killed. |
| W08 | Broaden FULL40 to `\w{40}`, allowing uppercase/noncanonical Base names. | **Named limit** — no uppercase/noncanonical Base witness, as for M02. |
| W11 | Reject TAB after key colon, losing fields instead of reading a clean claim. | **Named limit** — V/H emit colon-plus-space, not colon-plus-TAB. |
| W12 | Accept 32-hex digest and compare it instead of rejecting missing full digest syntax. | **Named limit** — V/H use 64-hex digests; detail-only changes also escape class projection. |
| W13 | Accept digit-less `Round:`, scanning `round-/` instead of reporting missing Round. | **Named limit in enforcement; G normatively forbids it** — a present empty Round must be ROUND-MALFORMED, but V `round-missing` is an absent line, not empty digits; h2 tests `1729x`, not empty. |
| W21 | Inherit caller environment, letting hostile GIT_DIR redirect repository operations. | **Named limit** — G/H run tools with constructed environments; no hostile GIT_DIR injection scenario. |
| W28 | Shift HEADING-MALFORMED detail line numbers by one. | **Named limit** — G `findings_of` and H `classes` discard all tokens after label/class; no line-number oracle. |
| W29 | Split only on LF, leaving CR in CRLF prereg and producing spurious findings. | **Covered by H `h8-crlf-prereg`** — H builder writes CRLF bytes; required exit 0, no classes. This covers the recorded witness, not arbitrary CRLF details. |
| W30 | Close a claim at `### ` subheading, losing later keys. | **Named limit** — malformed `##C2` scenarios are not `### ` inside a claim. |
| W32 | Omit `--full-history`, pruning merge-side prereg history and selecting wrong freeze. | **Named limit** — no V/H builder makes a merge. |
| W35 | Treat any wave `.json` (e.g. notes.json) as dispatch and spuriously flag early dispatch. | **Named limit** — h7 is `notes.ready` and h9 is `deep-spec.json`, both genuine dispatch names; neither tests irrelevant plain `.json`. |
| W37 | Skip Counter validation when sha256 is absent, returning clean instead of COUNTER-DIGEST. | **Named limit** — all V/H Counter values supply a digest. |
| W40 | Treat empty Counter blob at freeze as missing instead of valid empty content. | **Named limit** — V/H Counter content is nonempty; Population nonemptiness is a different rule. |
| W41 | Check Counter symlink mode at REV rather than FREEZE, changing symlink/digest findings. | **Named limit** — V/H symlink tests target Control and do not change its mode after freeze; no Counter symlink-to-file transition. |
| W46 | Report only the first of multiple malformed headings. | **Named limit** — V/H malformed-heading scenarios each contain one malformed heading; two unattached keys are not two malformed headings. |
| W57 | Omit git `--` separator, misreading leading-dash path and changing COUNTER-SYMLINK to COUNTER-DIGEST. | **Named limit** — V/H use `census/...` paths, none beginning with `-`. |
| W70 | Change NO-CLAIMS finding detail text while preserving its class. | **Named limit** — G/H project only label/class, never exact detail. |
| W71 | Print duplicated key as `TARGET` rather than `Target` in finding detail. | **Named limit** — even new duplicate scenarios and h6 three occurrences inspect label/class counts only. |

The 27 named limits above exclude M59's superseded old expectation; including its untested new first-empty witness yields 28 historical witnesses not directly enforced. W13 additionally illustrates a normative requirement without a matching exact witness. r42 retention cannot itself establish closure of these 30 gaps: their defining r42 result is that no r42 leg observes them. Candidate-authored selftests are not independent evidence of these witnesses.

## Commands/tool requests actually executed and observed output

No shell variables or fixture identity were exported. No scratch directory or clone was created, so no scratch remains to delete. No tool installation/update occurred.

Exact shell commands (read-only):

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c2-counter.py | sha256sum
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/c2-counter.py /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/c2-cases.tsv /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/c2-hidden-audit.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c2-hidden-audit.py | sha256sum
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c2-cases.tsv | sha256sum
```

Observed SHA-256 output, identical between frozen committed bytes and inspected working files:

| file | sha256 |
|---|---|
| c2-counter.py | `7249969604c0a8d46788a980732f8b162f1d7f4a4387439876b4c623e0f6ee6b` |
| c2-cases.tsv | `bcfc5afebf7b4ad537caec73366947be41b12de0038a1dfdf5764b2936316b80` |
| c2-hidden-audit.py | `4bb3fac7f3a2f8e6d59f3218a1aaccc45ee8b24717b9f4422bde31a2dabfa541` |

Specialized requests used absolute lane paths; source aliases above expand them exactly. Searches preceded section reads:

- `read skill://godspeed`; `read /home/vgpnk/.omp/agent/RULES.md`: observed Godspeed posture and official-channel tooling rules.
- `grep` A+B, case-insensitive pattern `Part|part|gap|M[A-Z]?[0-9]|mutant|hidden`: observed 30 GAP aggregate and inherited evidence pointers.
- `grep` G+V, case-insensitive pattern `hidden|audit|case|grammar`: observed nine-case table and mandatory hidden leg.
- `grep` A, case-insensitive pattern `^##|\| .*GAP|\| M.*gap|\| W.*gap`: located named limits and M/W rows.
- `grep` H, case-insensitive pattern `^def |CASES|scenarios|case|add\(|append\(`: located builders, class oracle, ten scenarios.
- `grep` B, case-insensitive pattern `^## Named|^###|^\| M(02|03|09|13|15|18|22|28|29|31|40|43|59)`: located inherited witness behaviors.
- Exact relevant `read` selectors: V`:1-30`; A`:305-353`; B`:124-170`; H`:47-168`; G`:1-54,115-190`, `:190-210,275-305,330-357`, `:80-105,209-215`. Observed source content summarized and cited above.
- `read xd://lsp`: observed **No such tool: xd://lsp** and mounted-device list without LSP. Therefore definitions/callers were traced through literal source fallback (G score -> run_tool/findings_of; G hidden leg -> H main -> classes/build), not semantic proof. No cold empty LSP result was interpreted as absence.

## Remaining unknowns

No r43 candidate was evaluated and no historical mutant was transplanted. The table maps frozen scenario/oracle capabilities, not measured candidate survival. Full conformance outside these finite scenarios remains unproven. Historical r42 outcomes are attributed to committed reports, not rerun here. Verdict: **transcription and frozen-source crosswalk complete; broad claims that r43 closes all 30 part-A limits are unsupported by these instruments.**
