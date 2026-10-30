# S44executor16 — C1 correction-register partition

Axes: calibration / operability / coverage. This seat contributes calibration bookkeeping only; it does not claim a new factual correction or admission.

## Output

- `corrections.txt` — four emitted records selected by zero-based index modulo 16 = 15: R44-16, R44-32, R44-48, R44-64. Records use `scope=base-SCORECARD-token-referents`, base `rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f`, and have no optional disposition/capture/register fields.
- No production or frozen counter files changed. Historical SCORECARD line numbers are identifiers only; SCORECARD was not rewritten.

## Commands and observed evidence

Executed from the seat scratch directory:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev d314fd6e85d62565344fa6c4b102f52f62297884 \
  --scratch /fast/scratch/hyaku/souji-r44/S44executor16 --emit
```

Exit 0. The instrument emitted 66 unique records; modulo-16 positions (zero-based) 15, 31, 47, 63 correspond exactly to `R44-16`, `R44-32`, `R44-48`, `R44-64`. Exact emitted rows:

```text
R44-16 line=175 class=mismatch:path-absent stale=c2-fixture-after.tsv derived=census/round-24/records/c2-fixture-after.tsv
R44-32 line=666 class=mismatch:path-absent stale=c1-after2.txt derived=census/round-38/records/c1-after2.txt
R44-48 line=731 class=mismatch:path-absent stale=c1-after8.txt derived=census/round-38/records/c1-after8.txt
R44-64 line=822 class=mismatch:path-absent stale=controls/c2-control.txt derived=multi:census/round-41/controls/c2-control.txt;census/round-42/controls/c2-control.txt
```

Independent base-byte check (read-only):

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:SCORECARD.md | awk 'NR==175 || NR==666 || NR==731 || NR==822 {print NR ":" $0}'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only 55d7af6f5a22340f7a3de1c386e514ababfaa75f | grep -E '(^|/)c2-fixture-after.tsv$|(^|/)c1-after2.txt$|(^|/)c1-after8.txt$|(^|/)c2-control.txt$'
```

The four SCORECARD lines contain the respective stale tokens. The committed tree has exactly one suffix match each for `c2-fixture-after.tsv`, `c1-after2.txt`, and `c1-after8.txt`, at the derived paths above. It has two suffix matches for `c2-control.txt`, at `census/round-41/controls/c2-control.txt` and `census/round-42/controls/c2-control.txt`, consistent with the emitted `multi:` value.

## Earlier correction status (Q76)

Inspected the round-42 and round-43 lesson corrections for these selected line/token referents. No earlier correction covers the exact selected token referent for R44-16, R44-32, R44-48, or R44-64. Round 42 does have `CORRECTION-DE line=175 token=c2-after.tsv derived=path-absent`; it concerns another token on the same historical line and does **not** cover R44-16's `c2-fixture-after.tsv`. The other three selected tokens have no matching r42/r43 correction located. Accordingly this filing is registration only, not a claim that four new facts were corrected; line 175's earlier correction remains intact.

## Limitations

The bounded counter invocation was in `--emit` mode and intentionally did not run the full counter acceptance summary. This seat verified only its four derived referents against committed base `SCORECARD.md` and `ls-tree` output; no broader calibration inference, runtime remeasurement, admission, or score delta is claimed. No tool was installed or updated.
