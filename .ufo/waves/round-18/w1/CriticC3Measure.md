STATUS: DONE — C3's "governed surfaces 0→1" is bookkeeping; the real measurement exists but the tool-vs-counter predicate has a spec ambiguity that makes pid-for-pid unachievable as written.

# CriticC3Measure — attack on C3's counting command

## F1. `governed surfaces 0→1` is a file-existence count, not a measurement — replace with recall/precision + agreement

`git ls-tree -r b5763415… -- tools/souji-proc-census.sh census/round-18/` → 0 entries (both absent at base). "Surface governed" reduces to "a file named tools/souji-proc-census.sh exists and a PROVINCE bullet cites it". A tool that prints only the TSV header satisfies it. The wave plan itself knows this: ProcCensusFixture's spec (`.ufo/waves/round-18/make-w1.py:59`) adds the vacuity check "a stub tool printing only the header must FAIL P1/P2". Keep the surface count as bookkeeping, but the claim's evidence must be the three falsifiable numbers below.

## F2. The base-side "detects 0" is vacuous — the honest before-number is a naive baseline's error set

"No tool exists ⇒ detects 0" is unfalsifiable bookkeeping of the same kind. A better before-arm: a naive same-uid `ps -eo pid,args` + `grep -E '/var/tmp|/tmp|/dev/shm'` baseline over the fixture world. It will (a) false-positive on controls whose argv names *existing* scratch paths and on substring tokens, and (b) false-negative on cwd-only orphans (argv contains no path — see S1 below). Measure before = baseline FP+FN count on the seeded world (expected ≥2), after = 0. That is a real delta.

## F3. The tool and the "independent" counter are specified with different argv predicates — pid-for-pid is unreachable until one rule is pinned

The two seat specs (both authored blind, QUALITY Q5) disagree on what makes an argv element residue:

- ProcCensus (`make-w1.py:57`): `argv-path-gone:<path>` when an element "is an absolute path whose **first existing-check fails and whose parent scratch dir is also gone**".
- LeakCounter (`make-w1.py:67`): argv "contains an absolute path under /var/tmp, /tmp or /dev/shm whose **top-level scratch directory (first component below the prefix) no longer exists**".

"Parent scratch dir" admits two readings: `dirname(element)` or the first component below the prefix. Under the dirname reading the tool counts a process holding `argv=/var/tmp/TOP/sub/file` when `TOP/sub` is deleted but `TOP` survives; the counter does not (its top-level `TOP` exists). A faithful blind pair can legitimately produce different pid sets on exactly this class — the "independent agreement" check then fails for spec reasons, not implementation reasons. Smallest fix: pin the identical sentence in both specs — *an argv element counts iff it is `/<prefix>` or starts with `/<prefix>/`, `! -e element`, and `! -e` the element's first component below the prefix* — and seed class S5 (below) as the differential case.

Related unpinned asymmetries, each enough to break pid-for-pid:

- **Own-pid-tree skip.** The tool spec says "skip its own pid tree"; the counter spec does not. If both are launched from a deleted cwd, the counter will count the tool (and vice versa) while the tool skips itself. Pin: both skip own pid tree, and the measurement protocol runs both from a stable existing cwd.
- **Reason precedence.** A process satisfying both rules (deleted cwd AND gone argv) gets `cwd-deleted` or `argv-path-gone:` depending on check order — unpinned. Pin pid-set equality as the agreement unit, and pin `cwd-deleted` wins for the fixture's reason assertion (S3).
- **Zombie/short-lived read failures.** Neither spec says what a state-Z process is. On this kernel a zombie's `/proc/<pid>/cwd` readlink fails and `cmdline` is empty, so both exclude it naturally — pin "excluded" anyway with a seeded zombie control (S9), else an impl that falls back to `/proc/<pid>/stat` comm could differ.
- **cwd rule scope.** The cwd-deleted predicate is unrestricted ("cwd is deleted"), while argv is prefix-scoped. A same-uid process whose deleted cwd is under `$HOME` is counted by the cwd rule on the live host. Both specs say this consistently, but the fixture should seed it (S11) or an implementer will reasonably prefix-scope the cwd check too and break live agreement.
- **Token boundary.** "absolute path under a prefix" needs: token split on NUL (not whitespace), match iff token == prefix or starts with `prefix + '/'` — `/tmpdir/x` must not match `/tmp`, `--root=/var/tmp/x` is a single token that must NOT match under a token-prefix rule (the real leaks all carry the path as a standalone argv element: `-C /var/tmp/…`, `--root /var/tmp/…` — verified in leaked-procs-before-1631.txt). Pin token-prefix, seed S8 as control.

- **`--min-age` default is unspecified.** The tool spec lists `--min-age S` with no default value; the counter has no age filter at all. Any nonzero default makes tool ⊊ counter on fresh leaks. Pin default 0 and require the agreement run to use defaults.

## F4. Seeded classes needed for the fixture world (K detected, J controls)

Observed on the live host just now (`/proc` reads, allowed): leaked pid 185592 cwd=`/var/tmp/r15-census-config.upcupkw1 (deleted)`, state=S, wchan=`do_wait`; its git child 185605 wchan=`wait_for_partner` (blocked in FIFO `open`), cwd deleted; 562276 wchan=`anon_pipe_read`. So the real residue has all three shapes — parent `do_wait`, child `wait_for_partner`, pipe reader — and every leaked pid is caught by BOTH rules (deleted cwd AND gone argv tokens), meaning the two rules currently have zero discriminating coverage on the live population. The fixture must therefore discriminate the classes itself:

| id | seed | expected |
|----|------|----------|
| S1 | `setsid bash -c 'cd $D && exec sleep 300'`, then `rm -rf` the scratch top containing `$D`; argv contains no path under a prefix | `cwd-deleted` — the argv rule CANNOT see this; the discriminating seed |
| S2 | `setsid python3 /var/tmp/TOP/waiter.py` (a script that sleeps forever, run with cwd OUTSIDE the deleted top — e.g. fixture HOME), then `rm -rf TOP`: cwd is live, argv[1] is the gone path | `argv-path-gone:<path>` — the cwd rule CANNOT see this; the discriminating seed |
| S3 | both conditions (cwd deleted under scratch top AND argv path under same gone top) — the shape of all 58 real leaks | listed once; reason precedence pinned to `cwd-deleted` |
| S4 | FIFO-blocked reader: `setsid bash -c 'cd $D && exec cat < $D/fifo'` (writer-less), dir deleted | `cwd-deleted`, state=S, wchan `fifo`-ish/`wait_for_partner` recorded in its column — proves "blocked" is descriptive, not a detection class |
| S5 | argv element `/var/tmp/TOP/sub/file` where `TOP/sub` is deleted but `TOP` survives | NOT listed — the F3 differential; pins top-level-scratch-dir rule |
| S6 | argv element under `/dev/shm` and `/tmp` (prefix coverage, not just /var/tmp) | `argv-path-gone` |
| S7 | cwd deleted that sits outside all prefixes (deleted dir under a fixture $HOME) | still `cwd-deleted` — pins the unrestricted cwd rule |
| S8 | substring tokens: `--root=/var/tmp/gone/x` (single token), a token `/tmpdir/gone` | NOT listed — token-prefix boundary |
| S9 | zombie: fork a child that exits unreaped whose cwd had been deleted | NOT listed (no readable cwd/cmdline) |
| S10 | deleted cwd recreated at the same path (rmdir+mkdir) — readlink still says `(deleted)` (inode differs) | `cwd-deleted` |
| J1 | `sleep 300` in an existing /var/tmp dir | not listed |
| J2 | process whose argv names an EXISTING /var/tmp path (`setsid python3 /var/tmp/live/waiter.py`) | not listed — the precision control the naive baseline (F2) fails |
| J3 | the fixture's own launcher processes | not listed (own-pid-tree skip) |

ProcCensusFixture's P1–P8 covers S1/S4 (P1), S2 (P2), J1 (P3), plus --prefix/--min-age/redaction/no-signal/usage. Missing: S3 precedence, S5 boundary, S6 prefix coverage, S7 unrestricted cwd, S8 token boundary, S9 zombie, S10 recreated-name, J2 existing-path control. Recommend cases P9–P15; each missing case is a class a passing tool could still get wrong while the gate stays green.

## F5. The live-host agreement command needs a defined comparison, not "agrees pid-for-pid" vibes

Concrete protocol:

1. Precondition: `census/round-18/leak-count.py` must land (seat LeakCounter) — it does not exist at base or in the working copy (`git ls-tree` F1). C3's measurement is unmeasurable until both artifacts land; flag as landing-order dependency.
2. Run tool with **default flags** (`--min-age 0`, default prefixes) and counter, both from a stable existing cwd, within one second, same uid.
3. Compare `(pid)` sets; expect symmetric difference = 0. For host churn, repeat the pair twice and count a pid as disagreement only if present in one tool across BOTH windows.
4. Agreement unit = pid set; reason class compared only for seeded worlds (reason strings are tool-specific: `cwd-deleted`/`argv-path-gone:` vs counter's `by_reason` — pin the two class names shared).
5. Cross-check against the snapshot `census/round-18/leaked-procs-before-1631.txt`: all 58 pids still counted (I verified a sample of 6 still alive in /proc at write time; pids 185592, 185605, 562276, 562279, 574984, 4037365 all present with deleted cwds). Report snapshot-missed/snapshot-extra separately — churn since 16:31 is data, not failure.
6. "Exactly K, 0 false positives" on a shared host must be subset-oracle: `seeded ⊆ detected` and `detected ∩ controls = ∅` (other same-uid residue legitimately appears). For an exact-equality arm run the whole fixture under a dedicated uid (`useradd`/`sudo -u`) — recommended, it converts the oracle from subset to equality.

## Verdict

Holds as a claim (a genuinely new governed surface with a non-gameable measurement available) but the counting command as written fails: (a) `0→1` is bookkeeping; (b) the two detection predicates are specified divergently enough that faithful blind implementations cannot guarantee pid-for-pid (F3); (c) the zombie/boundary/recreation classes are unpinned (F4); (d) the agreement protocol is undefined (F5). All four are fixable by contract text — smallest safe correction: pin the shared argv predicate verbatim in both seat specs, pin reason precedence + own-pid-tree + zombie exclusion, add cases P9–P15 to the gate, and adopt the F5 comparison. No axis tradeoff requires rejection.

Tools installed/updated: none (probe rules read only; no installs needed).
