# S44reviewer57 — C3 semantic cutover review

Axes: **calibration / operability / coverage**. Assigned emphasis: coverage; no numerical score change or admission recommended by this seat.

Reviewed frozen revision `d314fd6e85d62565344fa6c4b102f52f62297884` versus registered base `55d7af6f5a22340f7a3de1c386e514ababfaa75f`. Domain files were read-only. This is a recommendation, not integration, operator adjudication, or non-author admission.

## Findings (severity order)

### P2 — New leaf preflight turns established output refusals into tracebacks

`tools/souji-worktree-drift.py:326-332` introduces `os.lstat(json_path)` but catches only `FileNotFoundError`. A caller output beneath a regular-file parent raises `NotADirectoryError`; a looping parent raises `OSError(ELOOP)`. Neither reaches the existing `JSON-UNWRITABLE` conversion at `:444-447`; `main` catches only `Refusal` at `:462-466`.

Bounded, frozen-byte comparisons reproduce both regressions:

| `--json` shape | base | frozen |
|---|---|---|
| regular-file parent / out.json | rc 2, `REFUSAL JSON-UNWRITABLE: [Errno 20] Not a directory: 'victim'`, no traceback | rc 1, traceback ending `NotADirectoryError: [Errno 20] Not a directory: '<scratch>/victim/out.json'` |
| self-loop parent / out.json | rc 2, same structured JSON-UNWRITABLE refusal | rc 1, traceback ending `OSError: [Errno 40] Too many levels of symbolic links: '<scratch>/victim/out.json'` |

Evidence: `probe-receipt-valid.json`, probes `base/frozen parent-file` and `parent-loop`; each records exact argv, rc, stdout and stderr. All record bytes remained unchanged. The error change is not the intentional leaf-symlink cutover: these paths have an inaccessible final component and fail while traversing a parent. The new battery covers a valid symlinked parent but not these failures (`tests/fixtures/r44-drift-symlink-refusal.py:161-174`).

Recommendation for L1: translate other `lstat` filesystem errors to the existing structured output-refusal contract while preserving absent-leaf creation and explicit leaf-symlink refusal; add bounded parent-error regression cases. No production edit made here.

## Operator decision and existing holds

- **Local defensive refusal does not acquire deletion authority.** PROVINCE Owns includes dry-run census/proposals (`:17`); the existing tool-contract precedent explicitly says such repairs create neither receipt class nor deletion verdict/authority (`:276-289`). The inspected tool diff only adds a refusal enumeration, leaf metadata check and path-variable reuse. It adds no unlink, quarantine, pruning, receipt authorization, process action or cleanup operation. PROVINCE, SHONEN, SKILL and SCORECARD have no base-to-freeze diff in the scoped command below.
- **The existing cleanup holds can remain intact while this defensive contract is repaired.** PROVINCE `:108-110`, `:156-159`, and `:283` keep certification OFF / K5 HELD and preserve specific reap/NAMESPACE restrictions. These are not a general prohibition on refusing caller-requested writes; conversely they do not authorize deletion or waive caller compatibility requirements. A symlink is not a preservation receipt.
- **Do not conflate permission for defensive work with closure of routed defect 5.** The prior non-author verifier explicitly demands an *operator-level contract decision plus joint cutover under a new freeze* (`corpus/lessons/round-43-verifier-spotcheck.md:82`). R43 lesson M43-2 (`:40`) and SCORECARD `:903` require explicitly choosing semantics and updating consumers together, not rewriting the historical failed target. R44 preregistration `:4` selects refusal and describes the joint cutover; the actual frozen diff changes both tool and r38 consumer. This satisfies the technical joint-cutover shape. However, the reviewed frozen authority documents contain no separately attributable operator disposition of that routed decision. The counter's phrase “under a decided contract” (`c3-counter.py:5`) is a claim, not proof of who decided it. L1/non-author closure should cite the actual operator authorization, or retain that documentary closure gap. This reviewer does not issue that decision. No broader operator waiver is required merely because the change is defensive; the specific prior decision requirement must still be honored.

## Actual changed behavior and consumer check

Read-only command executed:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff 55d7af6f5a22340f7a3de1c386e514ababfaa75f d314fd6e85d62565344fa6c4b102f52f62297884 -- PROVINCE.md tools/souji-worktree-drift.py tests/fixtures/r38-drift-write-envelope.py tests/fixtures/r44-drift-symlink-refusal.py
```

Observed: no PROVINCE diff; tool gains JSON-TARGET-SYMLINK and the pre-realpath guard; r38 changes `json-symlink-resolved` to `json-symlink-refused` with rc 2/token/no-created-target/link-retained assertions and adds that case to behavioral base failures; r44 adds a six-case battery including positive regular and symlink-parent outputs. This is an explicit incompatible leaf contract change, not an invisible reinterpretation of the old green case. R43's sixteen survivor classes remain outside this C3 claim (`c3-counter.py:9`).

The canonical tool `run` performs root/record containment checks before the new output preflight (`:284-332`), then retains record-alias and measured-tree guards (`:339-360`), existing nofollow writer, descriptor hardlink check and delayed truncation (`:431-443`). No parallel runtime, alternate implementation or rerouting was introduced. Resume continuity and saturation are not changed or claimed in this diff.

## Bounded verification receipts

Executed from explicitly created seat scratch:

```sh
mkdir -p /fast/scratch/hyaku/souji-r44/S44reviewer57 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer57
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer57/probe.py
```

The corrected driver runs seven cases per revision, at most four subprocesses concurrently, each with a 15-second timeout. Each case has a valid one-row record naming an absent repository; this deliberately avoids git fixture/index mutations. Consequently successful JSON cases return rc 1 for the expected ABSENT finding, not a refusal. No git or jj mutation was executed.

Observed corrected output (all `record_unchanged=True`):

```text
base dangling rc=1 traceback=False
base existing rc=1 traceback=False
base directory rc=2 traceback=False   JSON-NOT-REGULAR
base regular rc=1 traceback=False
base parent-symlink rc=1 traceback=False
base parent-file rc=2 traceback=False JSON-UNWRITABLE
base parent-loop rc=2 traceback=False JSON-UNWRITABLE
frozen dangling rc=2 traceback=False JSON-TARGET-SYMLINK
frozen existing rc=2 traceback=False JSON-TARGET-SYMLINK
frozen directory rc=2 traceback=False JSON-TARGET-SYMLINK
frozen regular rc=1 traceback=False
frozen parent-symlink rc=1 traceback=False
frozen parent-file rc=1 traceback=True
frozen parent-loop rc=1 traceback=True
```

The existing-target victim stayed `keep\n` at frozen and was overwritten with JSON at base; the frozen leaf symlinks remained symlinks. Full outputs and argv are in `probe-receipt-valid.json`. The initial attempt mistakenly used a zero-row record and stopped at RECORD-EMPTY before the output guard; it supplies **no semantic verification** and is retained honestly in `probe-receipt.json`. The driver was corrected to a valid record before collecting the results above.

Frozen tool SHA256 `4d6bb64312e1cb52863d4d3b95f32503b6ff8d8189680d940b280ffcd21c490d`; base `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`. `frozen-document-evidence.json` preserves exact read-only `git show` argv, SHA256 and numbered frozen authority excerpts; C3 counter digest is `eba3e69ffef1493f4733c5c5537b8b2e5ed0a4cdcbaf551f560e03e8bcc64d66`, matching preregistration. Only the canonical frozen/base tool blobs were invoked, under the same Python executable.

Cleanup executed successfully:

```sh
rm -rf -- /fast/scratch/hyaku/souji-r44/S44reviewer57
```

No installs/updates, service changes, production edits, counter edits, commits, index/jj mutations, provider rerouting, or shared bookkeeping changes.

## Residual risk and verification gaps

- LSP device is unavailable: `read xd://lsp` returned “No such tool”. Therefore no semantic references/definition/diagnostics service answered; textual locations and actual bounded subprocess observations are used, not represented as semantic proof.
- This seat did not run the full C3 counter or unrelated suites. Its frozen acceptance only enumerates five prior fixtures plus r38 legacy, despite introductory “every prior drift suite” language; do not extend a 5/5 reading to every historical fixture or to all sixteen r43 survivor classes. This report makes no counter-green claim.
- Concurrent namespace replacement/race safety is not established by `lstat` and these deterministic tests. PROVINCE `:106-107` already disclaims universal protection against concurrent filesystem replacement.
- Operator-decision provenance is limited to reviewed frozen documents; absence there is not proof that no operator authorization exists elsewhere. Admission remains with the external non-author closure.

Self-evaluation: accuracy 4 (frozen receipts and reproducible failures; no whole-counter execution), completeness 4 (all assigned boundary questions addressed; operator provenance unresolved), clarity 4 (decision versus authority separated), actionability 4 (specific preflight error site and needed evidence named), conciseness 4 (receipt detail retained for audit). Overall 4.0/5; user should be able to reproduce the P2 and distinguish technical repair from admission without inferring broader authority.
