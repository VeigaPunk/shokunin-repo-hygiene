# R94Critic — cheap-attack trio, savings vs frozen controls

Method: each cost-reduction was measured against the frozen control receipt for the same arm, not against a
fresh run of the after arm. Line counts are from the delivered files (`wc -l`, `wc -c < <(grep …)`).

1. **Composite no-sentinel rule (C1).** The frozen footprint is the sentinel (a 15-line write + precondition
   subprocess per search run) plus the `rc=70` disjunct; FB is its one-edit ablation. My cheap variant —
   `any(' got=- ' in l) or all(' rc=1 match=' in l)` over the 66 ROW lines, computed offline over `harness-out`
   text I already had — saved: one full extra search invocation (the FA-style run, ~25 s wall in my re-run
   since clone dominates), the `sitecustomize` write per mutant, and the precondition child. Per-mutant scoring
   cost falls from ~(17 s harness + hook setup) to (0 s beyond one harness run) for the *rule* step. Caveat:
   it equals licit only on the five fixtures; the sentinel proves a *mechanism*, the composite only a pattern,
   and it would spare a crash fixture that prints verdicts and exits 1 with only expect-`rc=1` rows while
   refusing a genuine two-row mutant reshaped like `h-crash-late`.

2. **Arm-name special-case probe (C2).** Frozen footprint: each of 10 arms runs up to 9 fixture executions
   (~50-90 s per arms run). Cheap variant: 15 lines at `main()` entry — `basename(abspath(--work))` dispatch —
   0 fixture executions, runs in under a second per arm (the measured 10/10 run was instant apart from Python
   startup). Saving: the entire forgery workload. Caveat: it validates arm names, not discipline; the only
   reason the real probe matters is that its code performs the checks the count certifies.

3. **Offline rule evaluation from `harness.out` (both).** The frozen forgeries (FA/FB, GA/GB) each cost a full
   search/arms invocation. Because the searches retain `harness.out` per mutant, five candidate verdicts and
   their predicate conformance could be computed from 5 files with zero subprocess runs after the two
   predicate re-runs I did for verification (26.9 s and 24.1 s wall). Saving per extra candidate: ~25 s (C1)
   / ~60 s (C2) avoided. Caveat: offline rows carry no exit-code/stderr beyond what the harness printed —
   exactly how the pattern rule hides its misclassification, and why live negative controls still matter.

Conservation note: I spent the two live re-runs anyway (they are the ground truth for *my* numbers) and reused
the retained outputs for the five rule variants and the four counterexample probes, rather than paying a fresh
search per variant. Anything I cite as "on the frozen receipt" is from `census/round-94/controls/`, costed
against my re-runs, not a new run of the after arm both instruments already had.
