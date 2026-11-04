# S58Executor4 — C2 acceptance delivery

Axes: literal-case discrimination; honest-receipt preservation; reproducible, retained evidence; confined writes.

## Files delivered

- `.ufo/waves/round-58/w1/S58Executor4/c2-acceptance.py`
  - SHA-256 `55b5e063fa57a02d7fcf186c9d8e9b719b0ecb76b08001ad0988ad76aa3fc82e`.
- `.ufo/waves/round-58/w1/S58Executor4/before-arm.json`
  - Outer observed argv, stdout, stderr, EXIT; stdout is the driver's complete JSON including per-case argv/output/EXIT/findings, fixture commands and toplevel guards, tool digest, real receipt bytes/digests, and control receipts.
- This report.

No production files or historical counter bytes were changed. No builds, lint, formatters, installs, services, commits outside scratch, pushes, or model-routing changes. No LSP tool is available in this seat; no production symbol edits were needed.

## Driver contract

`python -B .ufo/waves/round-58/w1/S58Executor4/c2-acceptance.py --tool GATE.py --root LANE --work OWN_SCRATCH [--selftest]`

Exactly five hardcoded refusal identities: absolute path, `../`, intermediate parent symlink escape, annotated tag OBJECT, conflicting revisions. The first three require EXIT=1 and exactly `[RECEIPT-PATH-UNCONFINED]`; tag requires EXIT=1 and exactly `[RECEIPT-REV-ABSENT]`; conflict requires EXIT=1 and exactly `[RECEIPT-REV-CONFLICT]`. Ordered full finding-ID lists are compared, not substring matches; complete finding lines remain in JSON.

The three hardcoded real rows from r57 `manifests/after.tsv` are each measured against the real lane, without rewriting their bytes, requiring EXIT=0 and no findings. All five synthetic receipts include a correct committed instrument digest. Conflict uses two distinct durable commits with unchanged instrument bytes. The tag case supplies the actual tag object's full SHA-1, verifies `cat-file -t` is `tag`, and verifies its peeled commit.

Scratch Git mutation commands are only explicit `git -C` init/add/commit; each post-init Git call checks the exact toplevel first. Init first confirms the new fixture is outside an existing repository. Dates, identities, locale and Git environment are fixed; identity is provided only via subprocess environment. Annotated tag fixture bytes are written directly as a deterministic loose object with hashlib/zlib; no git tag/hash-object/update-ref/reset command is used. Each invocation creates an isolated fixture under caller work, avoiding stale-fixture reuse.

`--selftest` actually invokes both always-clean and always-refuse stub executables across the same eight cases. Its `selftest.passed` requires both be rejected. Overall driver EXIT still reflects the candidate target: a failing old gate remains EXIT=1 even when controls work.

## Measured before arm

Observed invocation (absolute paths retained in JSON):

`python -B /fast/scratch/hyaku/souji-r58/S58Executor4/c2-acceptance.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-57/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --work /fast/scratch/hyaku/souji-r58/S58Executor4/before-work --selftest`

Outer EXIT=1; stderr empty. Every one of the five required refusal cases returned EXIT=0, findings=[]: **0/5 required refusals met**. Each of the three real r57 after-manifest receipt rows returned EXIT=0, findings=[]: **3/3 preserved clean**. Both actual stub controls were rejected; `selftest.passed=true`. This is a discriminating failing before arm, not a closure claim.

## Bounds and handoff

No repaired target was scored by this seat: post-integration candidate scoring belongs to L1. L1 should invoke the delivered driver against the integrated gate with fresh own scratch and retain its JSON. No C1 correction, Markdown repair, universal parser safety, execution authentication, or broader privacy claim is made. Driver and evidence locations were sent to the C2 reviewer, mutation tester, critic, sentinel, and implementation seat coordination channel. Own scratch is removed after copying evidence and driver to delivery.

Self-evaluation (1–5): accuracy 4 (before arm observed; after arm intentionally unrun), completeness 4 (all assigned driver/control legs delivered; integration belongs to L1), clarity 4 (nested JSON stdout needs parsing for tabulation), actionability 4 (explicit CLI; requires lane history and writable scratch), conciseness 4 (full raw evidence intentionally larger than summary); mean 4.0. Priority: L1 retain repaired-target JSON; do not infer repair success from the before arm. Would the user agree? Evidence supports only the bounded before/control results above.

Residual limit identified by Sentinel11: subprocess timeouts terminate the direct process, not an entire descendant process group. No timeout/process-tree safety claim is made; no process-tree offense was run.
