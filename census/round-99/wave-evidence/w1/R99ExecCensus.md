# R99ExecCensus — no-harm population search (r99 vs r98)

## Axes
- Correctness: survivor identity must match r98 exactly (symmetric difference 0).
- No-harm: byte-exact copy of the r98 hook; same counter/harness/population.

## Commands (all absolute paths; cwd = fleet root, all targets absolute)

```bash
mkdir -p /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99 \
         /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-99/w1/R99ExecCensus \
         /fast/scratch/hyaku/souji-r99/R99ExecCensus/search
cp /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-98/c1-survivor-search.py \
   /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99/c1-survivor-search.py
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-98/c1-survivor-search.py \
          /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99/c1-survivor-search.py
# e8ba780a5b8d807ff199c33a679d7d8dd7259fb93e934d123b009e9f9f2649e1 (both, identical)

timeout 3600 python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-99/c1-survivor-search.py \
  --counter /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-87/c1-pointer-counter.py \
  --harness /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-93/c1-false-row-harness.py \
  --population /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-93/c1-false-rows.tsv \
  --lane /home/vgpnk/Projects/shokunin/souji-shokunin \
  --fleet-root /home/vgpnk/Projects/shokunin \
  --work /fast/scratch/hyaku/souji-r99/R99ExecCensus/search --jobs 5 \
  > /fast/scratch/hyaku/souji-r99/R99ExecCensus/search-r99.log 2>&1
# exit code: 0 (wall time 852.71 s)
```

## Observed lines

```
# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2
# counter path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-87/c1-pointer-counter.py sha256=fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b
# harness path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-93/c1-false-row-harness.py sha256=1868a570b9100559637ab454e6f7737bfdc881339cf8045d75cc22b3060a84a4
# population path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-93/c1-false-rows.tsv sha256=d6439f65a632cf83fb9d47c78bd0d32d1f9104d2f6443bdfd770e1c1c5e1a88e
# search sha256=e8ba780a5b8d807ff199c33a679d7d8dd7259fb93e934d123b009e9f9f2649e1
SEARCH-SUMMARY generated=278 ambiguous=9 uncompiled=0 hung=1 scored=268 errored=53 killed=139 survived=76
```

Exit code: **0**.

## Survivor comparison vs `census/round-98/records/search-r98.log`

```
grep '^SEARCH.*killed=no' <log> | awk '{print $2}' | sort
r98 survivors: 76
r99 survivors: 76
symmetric difference size: 0
diff census/round-98/records/search-r98.log search-r99.log  -> rc=0 (byte-identical)
```

## Findings
- No findings. r99 search output is byte-identical to the r98 log; survivors-r99 = 76, symmetric difference size 0.
- Full per-mutant log preserved at `.ufo/waves/round-99/w1/R99ExecCensus/search-r99.log` (also copied from scratch before deletion).

## Files delivered
- `census/round-99/c1-survivor-search.py` (byte-exact copy of r98; sha256 `e8ba780a…e9f9f2649e1`)
- `.ufo/waves/round-99/w1/R99ExecCensus.md` (this report)
- `.ufo/waves/round-99/w1/R99ExecCensus/search-r99.log` (full run log)

Tooling: none installed (only python3/sha256sum/grep/awk/sort/comm/diff already present).
