# R43mutanchorS12 — anchor-to-probe fidelity

Axes: anchor fidelity, behavioral discrimination, exact restoration.

Attacks: frozen C3 population row S12 (`space-name`) and its old→new MUTANTS tuple in `census/round-43/c3-counter.py` at `f8c805dbfa7f45814cf9a7270fa8bbffb41a8373`. Pinned tool: `619a75034dd6324e1a725f73034c59f7bf9558ef:tools/souji-worktree-drift.py`.

| mutant | anchor count | pristine rc+token | mutant rc+token | flip holds (yes/no) | defect text if no |
|---|---:|---|---|---|---|
| S12: REPO name excludes spaces | 1 | 0; SUMMARY … drift_rows=0 unreachable=0 | 2; REFUSAL RECORD-MALFORMED: line 1 does not match the census schema | yes | — |

Verdict: **killed**. The named `space-name` scenario matches the row's claim: a valid recorded repository named `repo with space` measures cleanly on pristine bytes, but the mutant rejects its REPO row before measurement. No population defect found by this probe. Restored bytes again return 0 with zero drift.

## Reproduction and actual output

Full exact command argv, return codes, stdout, stderr, record bytes, replacement strings and hashes are preserved in [.ufo/waves/round-43/w1/R43mutanchorS12/receipt.json](R43mutanchorS12/receipt.json). Scratch paths inside that receipt are command parameters, not surviving evidence locations.

Read pinned inputs with these commands (all succeeded):
```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 619a75034dd6324e1a725f73034c59f7bf9558ef:tools/souji-worktree-drift.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c3-counter.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c3-survivors.tsv
```

Python extracted the literal S12 tuple with `ast.literal_eval`, asserted the old bytes occur exactly once, and wrote the pinned tool under the isolated seat scratch root. The surgical mutation changed only `(?P<name>[^\t]+)` to `(?P<name>[^ \t]+)` in ROW; the complete mutated bytes were asserted equal to `base.replace(old, new, 1)`.

Scenario setup used Python `mkdir(parents=True)` and wrote:
```text
REPO\trepo with space\tregs=1\tprunable=0
TOTAL\trepos=1\tregs=1\tprunable=0
```
Here `\t` denotes a literal tab; the receipt contains the actual bytes as JSON text. No commits or identity settings were needed.

Exact setup commands:
```sh
TMPDIR=/fast/scratch/hyaku/souji-r43/R43mutanchorS12 git -C '/fast/scratch/hyaku/souji-r43/R43mutanchorS12/fleet/repo with space' init -q
TMPDIR=/fast/scratch/hyaku/souji-r43/R43mutanchorS12 git -C '/fast/scratch/hyaku/souji-r43/R43mutanchorS12/fleet/repo with space' rev-parse --show-toplevel
```
Observed: init rc=0 with empty stdout/stderr; rev-parse rc=0 prints the exact repository directory above. No subsequent git mutation occurred.

The **identical command** ran pristine → mutant → restored, each subprocess bounded to 20 seconds:
```sh
TMPDIR=/fast/scratch/hyaku/souji-r43/R43mutanchorS12 python3 -B /fast/scratch/hyaku/souji-r43/R43mutanchorS12/tool.py --root /fast/scratch/hyaku/souji-r43/R43mutanchorS12/fleet --record /fast/scratch/hyaku/souji-r43/R43mutanchorS12/record.tsv --timeout 5
```
Pristine/restored stdout (stderr empty, rc=0):
```text
SUMMARY record=/fast/scratch/hyaku/souji-r43/R43mutanchorS12/record.tsv record_repos=1 record_regs=1 record_prunable=0 live_repos=1 live_regs=1 live_prunable=0 drift_rows=0 unreachable=0
```
Mutant stderr (stdout empty, rc=2):
```text
REFUSAL RECORD-MALFORMED: line 1 does not match the census schema
```

## Hashes and restoration

- Old anchor SHA-256: `005dd1d6d843e81e7f0b37313c7a7e9b626712d3d2c1b8280f6580ed454bed05`.
- New anchor SHA-256: `d2af51c5a5115224c60b6ea5eb02b479e8cc1dab3d6731a41d99e350759b9429`.
- Pristine tool SHA-256: `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`.
- Mutant tool SHA-256: `2fdb485764775400fe3c025237043141173bebdffd18a6bce901cbc594ce5b48`.
- Restored tool SHA-256: `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`.

Exact byte equality to the pinned source was asserted before the restored run. Python `finally: shutil.rmtree(scratch)` removed the entire seat scratch tree after saving the receipt; observed `scratch_removed True`. No tracked lane source changed; no tools installed. This is one local fidelity probe, not a claim that the full frozen fixture/counter passes.
