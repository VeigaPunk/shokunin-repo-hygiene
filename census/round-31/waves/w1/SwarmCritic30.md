# SwarmCritic30 — attack on C3 (coverage: jj dropped-keep object lifetime)

## Status

STATUS: PASS — attack executed and reproduced: the frozen C3 target (`legs=11 fail=0 f1_entries=4`, v2 `legs=12 fail=0 f1_entries=4`) is reached by a state that fabricates the snapshot, the fetch receipt, the run record and the entry's novelty, while a fixture prints a literal record and measures nothing.

Lane base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc; lane HEAD read at 1b81136 (report-only seat, nothing written outside this file).

## Evidence

Base control, both counters, lane repo (read-only), scratch under `/fast/scratch/hyaku/souji-r31/AttackC3/`:

```
python3 -B census/round-31/c3-counter.py --root <lane> --rev 9f17a1e... --base 9f17a1e... --scratch <scratch>
SUMMARY legs=11 fail=10 f1_entries=3 rev=9f17a1e...
python3 -B census/round-31/c3-counter-v2.py ...  # same args
SUMMARY legs=12 fail=11 f1_entries=3 rev=9f17a1e...
```

Cheating state: clone of the lane at base (`git clone --no-local`, `origin` removed, identity set only with `git -C <scratch> config`), one commit `a1427d36f0110650599db3d6b0433face8864cfa`, scored twice:

```
python3 -B census/round-31/c3-counter.py --root /fast/scratch/hyaku/souji-r31/AttackC3/r.ZX4kDK/c \
  --rev a1427d36f0110650599db3d6b0433face8864cfa --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --scratch <scratch>
L1 PASS f1_entries=4 / L2 PASS coverage="grounded=17 mapped=17 dangling=0 mismatches=0"
L3 PASS gate="entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0" rc=0
L4 PASS snapshots=1 bad=[] / L5 PASS quotes=1 bad=[] / L6 PASS cited=['S063','S222'] new_opened_today=['S222']
L7 PASS / L8 PASS run_record=present results=4 / L9 PASS replays=[(0,4,True),(0,4,True)]
L10 PASS result_spans=4 not_in_record=[] / L11 PASS sources-census rc=0
SUMMARY legs=11 fail=0 f1_entries=4 rev=a1427d36f0110650599db3d6b0433face8864cfa
SUMMARY legs=12 fail=0 f1_entries=4 rev=a1427d36f0110650599db3d6b0433face8864cfa   # v2, L12 PASS missing=[]
```

Fields proven unbound to any observation (fixture ran under my own PATH shim, `TMPDIR` under scratch):

```
git -C <fixture repo> cat-file -e 1111111111111111111111111111111111111111
cat-file -e rc=1 -> object absent, record still prints object_present=yes
git -C <fixture repo> for-each-ref refs/jj/keep/   -> 3 refs
record steps b_ref_gone and c_expire_prune print keep_refs=0 target_keep=no
shim log (fixture-issued and jj-issued argv):
  jj -R <repo> abandon -r @-
  jj -R <repo> util gc --expire=now
  git --git-dir=. gc --prune=@1792996331 +0000          # issued by jj itself, not by the fixture
  git -C <repo> reflog expire --expire=now --all
  git -C <repo> gc --prune=now
  git -C <repo> cat-file -e 1111...1111
```

Fabricated provenance accepted as Gate evidence: snapshot first line is `FABRICATED SNAPSHOT — written by AttackC3, not fetched from git and not git's manual.`; `census/round-31/records/fetch-receipts.tsv` carries `200` and sha256 `dd4c6c88d6fd...` computed from my own bytes; `SHA256SUMS` carries the same hash. L4 passed on that pair.

Novelty anchors (bytes opened this run):

- `corpus/knowledge/jj-keep-ref-expiry.md:126` (wave-2 corrections): "the abandoned commit B stays reachable after its own keep ref is removed, because a surviving keep ref names a descendant whose parent is B".
- `corpus/knowledge/jj-keep-ref-expiry.md:78`: "Object removal is not measured." — but the removal it calls unmeasured is already observed elsewhere: `corpus/knowledge/git-grace-periods-and-expire-to.md:21` "still present after default two-week pruning, and absent after `gc --prune=now`".
- `corpus/knowledge/git-grace-periods-and-expire-to.md:9` "`gc.reflogExpire` defaults to 90 days"; `corpus/SOURCES.md:23` (S002) scope "§ CONFIGURATION gc.reflogExpire, gc.reflogExpireUnreachable"; `:8` holds the two-week prune date.
- `corpus/knowledge/jj-keep-ref-expiry.md:44` already holds the gc-reachability rule from the same S063 the draft re-opens, and its claim 3 holds `--prune=@<keep_newer>` at `git_backend.rs:977`, which draft claim 7 re-derives.
- Draft `deliver-entry-jj-dropped-keep-object-lifetime.md:16` says "this entry does not restate it", yet `:32` calls claim 2 "the mechanism behind the round-30 wave-2 observation".
- `gc.recentObjectsHook` is absent from the whole corpus (`grep -rn recentObjectsHook corpus/` → no rows), so it is the draft's one genuinely new source item.

## Findings

1. **The C3 target is satisfiable without measurement; the legs bind self-consistency, not observation.** Location: `census/round-31/c3-counter-v2.py:179-196` (L8 reads only the two version-line prefixes and the presence of `object_present=yes`/`no` tokens; L9 compares two runs to the committed record; L10 compares the entry's spans to the record; L12 compares the shim run to the record and greps argv substrings). The counterexample above reaches `legs=11 fail=0` and `legs=12 fail=0`. Concretely, the record's `object_present=yes` at `a_setup`/`b_ref_gone` coexists with `git cat-file -e` returning 1 for the only id the fixture ever passed. Covered axis: coverage; the claim can move with no surface moving.

2. **A0's "reality" leg does not test reality.** `c3-counter-v2.py:192-195` requires only that *some* jj call contains `abandon` and `util gc` and *some* git call contains `reflog expire`, `gc`, `cat-file -e`, in a log the fixture's own PATH produces. Every call may be issued against a repo unrelated to the claim and every outcome discarded; the shim log shows a `git --git-dir=. gc --prune=@...` line that jj itself emitted, so even the `git gc` requirement is satisfiable by jj's internal shell-out rather than by the fixture [INFERENCE: from the log line's `--git-dir=.` form, which the fixture's own calls, all `-C`, never use]. A fixture that calls the five names and prints a typed record passes.

3. **`reflog_hits` is undefined and unread.** No leg parses it (`c3-counter-v2.py:179-181`, `:185-187` only tokenise `object_present` and whole-line equality), and the draft concedes the file set: `deliver-entry-jj-dropped-keep-object-lifetime.md:156` "Which reflog file carries the entry naming B is not settled here." Nothing states whether `logs/HEAD`, `logs/refs/heads/*` or `logs/refs/jj/keep/*` count, nor whether `git reflog` (HEAD) or `git log -g --all` is the enumeration, so the field is a report, not a predicate; my record printed 1 and 0 at steps where no enumeration was run.

4. **The claim is F1 depth, not a moved surface, and most of the draft is held ground.** Claims 1, 2, 6 and 7 restate `jj-keep-ref-expiry.md:44`, `:126` and its claim 3; claim 3's 90/30-day windows and claim 4's two-week prune date are held in `git-grace-periods-and-expire-to.md:8-10` and S002's registry row (`SOURCES.md:23`), which the draft never names as held; the removal itself is already an observation at `git-grace-periods-and-expire-to.md:21` (r12 probe, `tests/results/r12-maintenance-guard.txt:33-40`). Net-new: the reflog-entry-as-keeper mechanism at v2.56.0, expire-then-prune ordering, and `gc.recentObjectsHook`. That is a legitimate frontier increment for F1, but the counter moves only by file count (L1), a README map span (L2) and a fresh row (L6); a pure restatement moves it too (proved in the counterexample). Whether F1 depth counts as coverage is an L1/operator decision, not something these legs measure.

5. **L4's fetch receipts are self-attested, so a fabricated snapshot is indistinguishable from a fetched one.** `c3-counter-v2.py:152-163` compares the committed hash with the committed receipt row and accepts `200` as written; my marker file plus a hand-written row passed. This is inherent to the lane's committed-receipt model, so it is a tradeoff to state, not a C3-only bug — but it means L4 evidences integer consistency, not provenance.

6. **L9's two-run byte equality rewards literal output over measurement.** A heredoc is stable by construction; a real arm whose keeper is an mtime or a pack-ref state (the held entry records the racy re-import check at `git_backend.rs:929-937`) is the arm more likely to differ between two runs. Determinism here is a false friend; the leg is not wrong, but it cannot be the only anti-fabrication guard.

7. **Minor: SHA256SUMS is keyed by basename.** `c3-counter-v2.py:155` maps `sums[os.path.basename(sp)]`, so two `snapshot:` paths with the same basename in different directories share one hash line; today every snapshot is unique, so it is latent.

Impacted axes: coverage (primary — target reachable without a surface moving and without measurement), calibration (secondary — the run record's fields are self-reports; `object_present`, `keep_refs`, `reflog_hits` are not observables of the instrument). Operability is not harmed; C2's REGRESS leg reads other content.

### Smallest safe correction (stricter-only, L1 to log as amendment A1)

1. **Keeper-subtraction mutation (load-bearing).** New leg L13: the counter copies `FIXTURE@REV` twice, deletes the `git reflog expire` invocation in one copy and the `git gc` invocation in the other, runs each and requires the RESULT lines to *differ* from RUN in the step whose claim depends on that remover (object_present flips yes→no or vice versa). A fixture that prints a fixed record is unchanged and fails; a fixture that measures keeps passing. This is the only check here that cannot be satisfied by a literal heredoc.
2. **Bind `object_present`.** Require each RESULT line to carry `target_id=<40hex>`, the fixture to leave its arm repos at a path it prints, and the counter to re-run `git -C <repo> cat-file -e <id>` for the step's id and require agreement. Printing alone then fails; a dummy repo with one present and one random id still passes, so 1 remains the load-bearing leg.
3. **Define `reflog_hits`.** In the entry, name the enumeration (`git log -g --all --format=%H`, and whether `logs/HEAD` is included) and have the counter re-run that command against the arm repo for the step claiming hits>0, comparing the count.

No amendment may relax the frozen target; these add legs and keep `legs=11`/`legs=12` passing only if the fixture is a measurement.

## Attack log

- Target: C3 frozen contract (`census/round-31/records/preregistration.txt` C3 paragraph), counters `census/round-31/c3-counter.py`, `c3-counter-v2.py`.
- Hypotheses tested: (a) a trivial fixture plus a typed record meets L8-L12; (b) `reflog_hits` is unenforced; (c) a restatement entry meets L1/L2 and the coverage axis. All three confirmed by the scored state.
- Scratch: `/fast/scratch/hyaku/souji-r31/AttackC3/`, clone at base with `origin` removed, one commit `a1427d36f0110650599db3d6b0433face8864cfa`; no lane write, no jj mutation in the lane, no network fetch (so the receipt's `200` could not have come from a fetch).
- Cheat fixture (verbatim, the only measurement-free part that the legs accepted):

```
#!/usr/bin/env bash
set -u
[ -n "${TMPDIR:-}" ] || { echo "TMPDIR unset" >&2; exit 2; }
D=$(mktemp -d "$TMPDIR/cheat.XXXXXX") || exit 2
jj git init --colocate "$D" >/dev/null 2>&1 || true
printf 'a\n' > "$D/f" 2>/dev/null || true
git -C "$D" add f >/dev/null 2>&1 || true
git -C "$D" -c user.name=a -c user.email=a@invalid commit -qm a >/dev/null 2>&1 || true
jj -R "$D" abandon -r @- >/dev/null 2>&1 || true
jj -R "$D" util gc --expire=now >/dev/null 2>&1 || true
git -C "$D" reflog expire --expire=now --all >/dev/null 2>&1 || true
git -C "$D" gc --prune=now >/dev/null 2>&1 || true
git -C "$D" cat-file -e 1111111111111111111111111111111111111111 >/dev/null 2>&1 || true
cat <<'REC'
RESULT arm=solo step=a_setup keep_refs=1 target_keep=yes reflog_hits=1 object_present=yes
RESULT arm=solo step=b_ref_gone keep_refs=0 target_keep=no reflog_hits=1 object_present=yes
RESULT arm=solo step=c_expire_prune keep_refs=0 target_keep=no reflog_hits=0 object_present=no
RESULT arm=descendant step=c_expire_prune keep_refs=1 target_keep=no reflog_hits=0 object_present=yes
REC
exit 0
```

- What the legs saw: L9 two runs equal (heredoc); L10 four spans are whole lines of the record (copied); L12 exit 0, results equal, five argv substrings present; L4 hash matches a fabricated snapshot and a hand-written `200` row; L5 one 13-word quote; L6 S222 fresh row added by me; L1/L2 one added grounded file plus one appended map span.
- Not claimed: the wave-1 delivered entry's own numbers may be honestly measured; this attack shows the target number is not evidence of that, and names the held ground the draft re-covers.
- Scratch removed after this report was written; nothing was copied into the lane except this file.

## Deliveries

- `.ufo/waves/round-31/w1/SwarmCritic30.md` (this report; no delivery file was named for this seat)
