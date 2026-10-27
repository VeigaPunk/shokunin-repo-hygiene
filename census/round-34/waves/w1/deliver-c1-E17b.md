# C1 delivery — E17b (SCORECARD.md:70, census/round-24/sources)

Verdict: **AGREE at base — no restatement row drafted.**

## Counter ITEM line (verbatim)

```
ITEM	E17b	AGREE	original	rc=0 expect_exit=0 predicate holds last=gitrepository-layout.5.txt: OK load=5.87
```

(The frozen predicate here is `COUNT: OK$==6`, a line-count conjunct, so the `last=` field is the run's last
digit-bearing line for disclosure only, not the carrier of the verdict.)

## Command (executed)

```
export TMPDIR=/fast/scratch/hyaku/souji-r34/RestateC1s9/tmp
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s9/cnt --only E16,E17a,E17b,E18,E19
```

Exit 0. Load before/after: `3.94 3.11 2.10` / `5.87 3.52 2.24`. Serialization: counter's own Q77 flock at `<scratch>/c1.lock`.
Counter bytes at `--list-rev`: sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`.
Lane HEAD at read time: `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`.

## Non-vacuity of the count (re-executed directly, same argv)

```
$ cd census/round-24/sources && sha256sum -c SHA256SUMS      # at 9c76c72, scrubbed env
git-v2.30.0-path.c: OK
git-v2.56.0-builtin-count-objects.c: OK
git-v2.56.0-path.c: OK
git-count-objects.1.txt: OK
git-worktree.1.txt: OK
gitrepository-layout.5.txt: OK
RC=0            load=11.08
```

`git show 9c76c72:census/round-24/sources/SHA256SUMS` has exactly 6 entries, so `OK$==6` is the full file, not a subset.

## Prior-correction / supersession sweep (Q76)

```
grep -n 'sha256sum -c SHA256SUMS' <base SCORECARD.md>   → 70 (the row itself only)
grep -n -F 'SCORECARD.md:70' <base SCORECARD.md>        → no match
grep -n '^| E1[6789]' <base SCORECARD.md>               → no match
```

No prior correction, supersession or binding row names this cell; the AGREE is a direct measurement.

## Cause commit

Not applicable: frozen (exit 0, `COUNT: OK$==6`) holds at `--rev`; Q75 is not engaged, no cause full40 claimed.

## Proposed restatement row

None. Item agrees.
