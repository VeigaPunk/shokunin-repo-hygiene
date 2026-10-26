# SwarmCritic35 — attack on C3 (r32 wave 1, coverage 8)

## Status
STATUS: PASS — the attack ran and reproduced: a fixture that measures nothing scores the frozen C3
target, `SUMMARY legs=14 fail=0 f1_entries=5`, exit 0, against `SUMMARY legs=14 fail=13
f1_entries=4` at base `85b61a151923986e7e6b48f7084b9122561b5f3d`; the defects are located by leg
and line, and a stricter-only correction is proposed. Nothing was written under the lane except
this report.

## Evidence

Read this run, absolute paths, lane at prereg commit `3ec84fc81b3243429c834a051880b0bcde06291c`:

- `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/records/preregistration.txt` — C3 clause and MACHINE BLOCK, target `legs=14 fail=0 f1_entries=5`.
- `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c3-contract.txt` — 5 keys in order: arm, step, obj, mtime, where, object_present (line 6 holds the key list start).
- `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c3-counter.py` — legs at `:138` (L1), `:223` (L4), `:232` (L6), `:244` (L8), `:246` (L9), `:262` (L12), `:270` (L13), `:274` (L14); shim writer `:185`; fixture runner `:166`.
- Prior F1 text: `corpus/knowledge/jj-dropped-keep-object-lifetime.md:44-53` (claim 4) and `:238` (wave-2 qualification); `corpus/knowledge/git-grace-periods-and-expire-to.md:8`; `corpus/README.md:677-682` (`### Frontier (r31)`).

Scratch (operator directive 2026-10-25): `/fast/scratch/hyaku/souji-r32/AttackC3/`, `TMPDIR` under it,
clone by `git clone -q --no-local <lane> $D/c` then `git -C $D/c remote remove origin`; throwaway
identity set only with `git -C $D/c config`. Removed before this report was written.

### Counter readings (same counter, same base and list-rev, different scratch rev)

    $ python3 -B census/round-32/c3-counter.py --root $D/c --rev 85b61a1... --base 85b61a1... --list-rev 3ec84fc...
    L12 FAIL rc=None results_equal=False jj_calls=0 git_calls=0 touch_calls=0 missing=[...6 calls...]
    L13 FAIL fixture absent
    L14 FAIL lines=0 contract_unchanged=False bad=[]
    SUMMARY legs=14 fail=13 f1_entries=4 rev=85b61a151923986e7e6b48f7084b9122561b5f3d

    $ ... --rev fade71abef74fc25edf66515407166c4de9edde0          # attack rev, cheat "B"
    L1 PASS f1_entries=5
    L2 PASS coverage="grounded=18 mapped=18 dangling=0 mismatches=0"
    L3 PASS gate="entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0" rc=0
    L4 PASS snapshots=1 bad=[]
    L5 PASS quotes=2 bad=[]
    L6 PASS cited=['S063', 'S900'] missing=[] new_opened_today=['S900'] url_unbound=[]
    L7 PASS bad=[]
    L8 PASS run_record=present results=12 arms_with_gc=['mixed', 'never', 'nocruft', 'old', 'recent'] mixed_objs=['B', 'C']
    L9 PASS replays=[(0, 12, True), (0, 12, True)]
    L10 PASS result_spans=3 not_in_record=[]
    L11 PASS sources-census rc=0
    L12 PASS rc=0 results_equal=True jj_calls=3 git_calls=6 touch_calls=1 missing=[]
    L13 PASS M2:rc=0,lines=12,differs=True,no=0<2=True M3:rc=0,lines=12,differs=True,no=0<2=True
    L14 PASS lines=12 contract_unchanged=True bad=[]
    SUMMARY legs=14 fail=0 f1_entries=5 rev=fade71abef74fc25edf66515407166c4de9edde0

    $ ... --rev 10e65921760a71da5cb4c4365056bd1c814880a9          # cheat "A": presence from touch exit
    L13 FAIL M2:rc=0,lines=12,differs=False,no=2<2=False M3:rc=0,lines=12,differs=False,no=2<2=False
    SUMMARY legs=14 fail=1 f1_entries=5

    $ ... --rev 292b4bbd5f60fd76f380926f73cb9efcc9b1371f          # cheat "C": clock readback only
    L13 FAIL M2:rc=0,lines=12,differs=False,no=2<2=False M3:rc=0,lines=12,differs=True,no=0<2=True
    SUMMARY legs=14 fail=1 f1_entries=5

    $ ... --rev 40d5f59053050b320565a98d6d13fe23353cb544          # cheat "D": literal version anchors
    L8 PASS ... L12 PASS ... L13 PASS M2:...differs=True... M3:...differs=True...
    SUMMARY legs=14 fail=0 f1_entries=5

Provenance probe (the snapshot the passing rev cites is a file, not a fetch):

    $ curl -sS -o /dev/null -w 'http=%{http_code}\n' --max-time 20 https://git-scm.com/docs/git-gc-nonexistent-attack-probe
    http=404

Call-status probe inside the cheat fixture's own calls (all logged by the L12 shim, all ignored):

    rc=1 :: jj abandon -r attack-probe-nonexistent
    rc=0 :: git reflog expire --expire=now --all        # empty repo: nothing to expire
    rc=0 :: git update-ref -d refs/jj/keep/attack-probe-nonexistent
    rc=1 :: git cat-file -e 0000000000000000000000000000000000000000

## Findings

1. **L12 and L13 are satisfiable with zero measurement.** The passing rev's fixture issues the six
   calls L12 looks for in the shim log (`c3-counter.py:262` matches argv strings only), discards
   every status, and prints twelve RESULT lines from constants; its only branch reads the shim's own
   bytes (`grep -q 'gc|prune|repack) exit 0'`) so that both neutered shims print a different table.
   Location: `census/round-32/c3-counter.py:166` (runner), `:185` (shim writer), `:262` (L12), `:270`
   (L13).

2. **M3 does not prove the outcome depends on mtime; M3 proves only that the fixture notices touch's
   effect.** Cheat A — presence computed as "touched, therefore absent", branching on `touch`'s exit
   status — prints the record unchanged under M3 (`differs=False`) and fails. Cheat C — reads the
   stamp back with `stat -c %Y` and labels `mtime` from the readback — passes M3 and fails M2. So
   L13's two legs test different things: M3 tests that the clock label is not taken on trust, M2
   tests that gc's execution is observed at all. Neither tests that the *object's* fate was read;
   cheat B satisfies both without either, because the verdict never came from a repository.

3. **Provenance legs are self-declared.** The passing rev admits a registry row (S900) whose own
   `teaches` cell says the page was never fetched, a 1845-byte snapshot written by hand, and a
   `fetch-receipts.tsv` row claiming `http 200` for a URL that answers 404. L4 (`:223`) compares the
   blob's sha256 to two lane-authored files, and L6 (`:232`) compares Gate URLs to the cited row's
   own cell; `sources-census.sh validate` (L11) checks column shape only. Location:
   `census/round-32/c3-counter.py:223,232`; `scripts/sources-census.sh` E01-E12.

4. **Novelty is asserted, not tested.** L1 (`:138`) is a file count and L2 is a map agreement. The
   passing entry's body restates held text — `git-grace-periods-and-expire-to.md:8` ("`gc.pruneExpire`
   defaults to `2.weeks.ago`"), `jj-dropped-keep-object-lifetime.md:44-53` (the mtime keeper, "for as
   long as its own mtime is inside the window"), and `corpus/README.md:680-682` ("handling changes
   the mtime keeper's reach") — and still scores `f1_entries=5`.

5. **Is the mtime clock new F1 ground?** On paper yes, and this is the one place the claim is
   defensible: r31's record isolates a descendant keep ref and a reflog entry only, every r31 prune
   is `--prune=now` or `--expire=now` (`jj-dropped-keep-object-lifetime.md:238`), and
   `corpus/README.md:680-682` names cruft-pack reach as disclosed-not-measured. The new edge class is
   therefore the *measured* one: loose versus cruft versus pack, per-object `.mtimes`, and the
   `pruneExpire=never` / `cruftPacks=false` arms — none of which any held entry measures. The
   proposition is depth on held documentation; the claim is coverage; and finding 1 is that this
   counter scores the claim without evidence of the increment. Location:
   `census/round-32/c3-contract.txt:6` (the `where` enum is the only field carrying the new edge).

6. **L8's version anchors and L10's spans are free text.** Cheat D prints `jj-version: jj 0.45.1` and
   `git-version: git version 2.56.0` as literals with no `jj --version`/`git --version` behind them
   and still scores `fail=0`; L10 only requires the three backticked spans to equal RUN lines.
   Location: `census/round-32/c3-counter.py:244,248`.

## Attack log

Seat: attack C3 only. Designated cheat built in `/fast/scratch/hyaku/souji-r32/AttackC3/` (origin
removed; deleted after scoring). Cheat B's decision core, abridged from
`tests/fixtures/r32-jj-mtime-clock.sh` in that scratch tree:

    m2=no; m3=no
    g=$(command -v git); t=$(command -v touch)
    case "$g" in */shim*/git)   grep -q 'gc|prune|repack) exit 0' "$g" && m2=yes ;; esac
    case "$t" in */shim*/touch) grep -qx 'exit 0' "$t" && m3=yes ;; esac
    # six calls issued here, every status discarded
    row() { where=$5; present=$6
      if [ "$m2" = yes ] || [ "$m3" = yes ]; then where=loose; present=yes; fi
      printf 'RESULT arm=%s step=%s obj=%s mtime=%s where=%s object_present=%s\n' \
        "$1" "$2" "$3" "$4" "$where" "$present"; }

Rev table, all against base `85b61a1...` and list-rev `3ec84fc...`:

- `fade71ab` cheat B, shim-byte sniff: `fail=0`, frozen target met.
- `10e65921` cheat A, presence from touch's exit: `fail=1`, L13 both legs identical output.
- `292b4bbd` cheat C, clock readback only: `fail=1`, M2 leg identical output.
- `40d5f590` cheat D, literal version anchors: `fail=0`.

Impacted axes: coverage (8) only — C3 can be certified without coverage of the edge it claims;
calibration (7) and operability (8) are untouched by this attack. No axis is harmed by the
correction below.

Smallest safe correction (stricter-only; the L1 owns the amendment and the target):

- **A1, independent verification, the load-bearing one.** Require the fixture to print one
  `REPO path=<dir>` and one `OBJECT sha=<40hex>` line per repository, and have the counter, after
  each of the four runs (two replays, shim, M2, M3), itself execute `git -C <dir> cat-file -e <sha>`
  and `stat` the loose object or the cruft pack's `.mtimes`, then require every RESULT line's
  `object_present` and `mtime` to agree. Because the check runs outside the fixture, shim sniffing
  and constant tables both die: cheat B fails on the first line, and cheat D on the version anchors.
- **A2, provenance.** Have L4 fetch each snapshot URL itself and require HTTP 200 plus byte length
  and sha256 equality with the committed blob, and have L6 require the cited row's anchor bytes to
  exist at that URL. The 404 URL and the self-declared receipt then fail L4.
- **A3, novelty.** Require one RESULT line whose field values instantiate the edge class the entry
  names (here: at least one `where=cruft` line whose `object_present=yes` is independently confirmed
  by A1), so a restatement that prints documented enums without the new edge fails.

A cheaper alternative, if the L1 prefers not to add a leg: record in the C3 receipt that `fail=0` is
reachable by a fixture with no measurement, so the claim is certified as seat-quality, not as
coverage.

## Deliveries

- `.ufo/waves/round-32/w1/SwarmCritic35.md` (this report). No other file written; no lane git or jj
  mutation; scratch removed.
