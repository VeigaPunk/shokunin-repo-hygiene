# S58Sentinel11 — C2 trust-boundary review

Axes: confinement before receipt-content I/O; special-file/bounded resource behavior; symlink containment; Git environment write isolation; exclusive scratch ownership; subprocess cleanup; provenance honesty.

Reviewed frozen predicate e7f64f30324e8ddb3f2266302daa9066054cdbb3 and canonical Executor3 candidate. L1 SoujiR58 alone retains integration/judgment authority. No production, historical-counter, sibling, Git/JJ, service, configuration, or PATH edits by this seat. No Markdown repair claim.

Final reviewed candidate SHA256: `56f2a31163035726f1190db3e6b827fc121602377e187d16a54a6ae8f15af543`.

## Observed bounded behavior

Evidence prefix: `.ufo/waves/round-58/w1/S58Sentinel11/`.

- `frozen-r57.txt`: synthetic absolute path, traversal, intermediate symlink each reached `Path.read_bytes` outside synthetic root before REV-MISSING. Leaf symlink, FIFO, directory did not reach content read. Baseline source SHA256 `174d7b8a3c105875f1757f9137f26ed54e38ac11c963a134015bce8a9dd16ec2`.
- `candidate-56f2a31.txt`: same three escape classes return RECEIPT-PATH-UNCONFINED with zero `Path.read_bytes` calls; leaf symlink returns RECEIPT-SYMLINK without read; FIFO/directory return RECEIPT-MISSING without read; ordinary synthetic file is read and reports REV-MISSING. This checks pre-content-I/O, not absence of metadata I/O: confinement necessarily performs islink/realpath/stat operations.
- Baseline and final candidate drop injected GIT_TRACE and GIT_CONFIG_COUNT/KEY/VALUE from git_env; `git --version` returns `git version 2.56.0`, EXIT=0, synthetic trace file absent. Optional locks=0, lazy fetch disabled=1. No Git mutation performed.
- Every probe child used Python `-B`; `sys.dont_write_bytecode=true`, own scratch `.pyc` list empty. No claim about preexisting repository caches.
- `scratch-safety-final.txt`: mocked fixture/scoring functions exercise the real final `run_selftest` allocation/finally cleanup only. Existing caller `c2-fixtures/synthetic-marker` survives both success and synthetic builder exception; newly allocated fixture directories disappear. This is NOT a real gate selftest or fixture Git run.
- Probe subprocesses run in a fresh session, with 15-second communicate timeout and killpg(SIGKILL) fallback followed by communicate/reap. No timeout occurred. No adversarial process-tree automation executed.

Receipts retain command, stdout/stderr and EXIT. Driver sources and exact reviewed final candidate copied alongside evidence. Earlier candidate probe receipts remain explicitly versioned, not rewritten.

## Findings and disposition

### High — new deletion of preexisting caller subtree (superseded)

Exploit path: invoke initial selftest with a --work directory whose `c2-fixtures` contains caller data. Initial candidate `dfd90d9da263d0bdc28d118bbc75f355c41432034854a2de3b3ab7749cbc3bdf` build_fixtures lines227–228 computed `work.resolve() / 'c2-fixtures'` then unconditional `shutil.rmtree(..., ignore_errors=True)` before allocation. Frozen r57 builder did not recursively delete that subtree. Impact: unrelated caller data loss; genuine new authority/regression, not permitted as an idempotence shortcut. Destructive path NOT executed.

Smallest remediation: allocate an exclusive mkdtemp child and clean only that allocation. Escalated to L1; final candidate implements this in run_selftest lines354–362. Synthetic ownership probe above supports the repair. Final cleanup still deliberately deletes its own created subtree; no general filesystem-delete authority is granted. Receipt CLI path does not call cleanup.

### Medium — new arbitrary expectation-output overwrite (superseded)

Exploit path: safety revision `7c35d3ea22f75303cd593026119f30de862b439a51a5375afe2ecfc12a433ed0` exposed `--emit-expected PATH`; score_selftest lines376–381 wrote Path(emit_path) without work confinement or symlink checks. An operator-supplied output outside work could be overwritten; this contradicted the advertised writes-only-under-work contract. No outside write attempted. This was a new interface, absent frozen r57.

Smallest remediation: remove emission interface rather than permit rewriting the oracle. L1 independently requested the same change. Final main exposes no --emit-expected, and final score_selftest has no output-write branch (source snapshot `candidate-reviewed-56f2a31.py`). Old snapshot `candidate-reviewed-7c35d3e.py` preserves the superseded branch. Initial dfd source was not captured before replacement; its precise observed digest/lines are retained here and in tool transcript, not falsely represented by a newer file.

### Medium — TOCTOU and resource bounds remain open; not new

Exploit path [INFERENCE]: an actor controlling the receipt tree can replace a checked intermediate component or regular leaf after confinement/is_file but before read_bytes. Final code lines90–151 performs pathname checks then a separate unbounded open/read; it does not pin directory/file descriptors. Similarly an oversized regular receipt can consume memory; a caller-supplied FIFO manifest can block `manifest.read_text()` before Git timeouts apply. Candidate rejects a stable receipt FIFO/directory, but this does not establish atomic or bounded reads. Frozen gate already used separated checks/unbounded read_bytes and unbounded manifest read, so these remain unclosed hazards, not newly introduced C2 acceptance regressions. No race, large-file, or blocking-manifest attack executed.

Smallest remediation if separately authorized: descriptor-relative confined opens, validated regular-file descriptor/type, byte ceiling, and bounded manifest intake. Do not silently broaden this round's five-case predicate into universal confinement/privacy/resource safety.

### Low/Medium — timeout does not guarantee descendant cleanup; not new

Exploit path [INFERENCE]: git() uses subprocess.run(... timeout=120) without a new process group, so a surviving descendant is not guaranteed terminated. This pattern exists in frozen and final gate, and in independent acceptance driver's command(). Gate git_env is allowlisted and hooks/fsmonitor disabled, reducing ordinary child-launch opportunities; PATH remains inherited by design. Impact: possible leaked process or pipe retention in a hostile execution environment. Smallest remediation, if separately authorized: session/process-group lifetime ownership with timeout group termination and reap. No offensive descendant test executed. Our own probe wrapper does establish a cleanup group.

## Scope and unrun legs

No C1 measurement, full five-case acceptance, annotated-tag/conflict behavior, real historical receipt replay, full 17-case gate selftest, live-protected-name/private-value probe, build, lint, formatter, network, resume_continuity_v1 interface, race attack, memory-exhaustion attack, or blocked-manifest execution by this seat. Those are unrun, not inferred passes. The resume interface is not present in this assigned surface. Three real receipt preservation belongs to Executor4/L1 evidence; this report does not claim to have replayed it.

All executed synthetic drivers exited 0; check findings are retained verbatim, including expected refusals. Final narrow path/type/Git-env probes show no observed regression on the assigned exercised cases. No universal safety, execution-authentication, or fleet readiness claim. Original deletion and emission regressions were surfaced rather than suppressed and are absent from final reviewed code.

Tool installs/updates: none. Pacman transactions: none. Scratch removed only after evidence copies, using exact owned seat root; no sibling cleanup authority.

Self-evaluation: accuracy 4 (race/resource hazards are explicitly static inference); completeness 4 (full acceptance intentionally belongs to other seats); clarity 4 (three candidate versions required provenance detail); actionability 4 (smallest fixes and residual bounds named); conciseness 4 (retains necessary superseded defects). Average 4.0. Main should use final digest and independent acceptance evidence, not superseded probe receipts, for integration.

Report: .ufo/waves/round-58/w1/S58Sentinel11.md
