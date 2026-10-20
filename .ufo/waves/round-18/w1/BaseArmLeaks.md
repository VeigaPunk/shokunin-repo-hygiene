STATUS: DONE — measured the assigned C1 baseline fixture residue and b576341 selftest.

Axis: operability. Scope: report only; no tracked repository files were changed. No tools were installed or updated.

## Baseline and fixture results

Assigned clone identity:

```text
git -C /var/tmp/souji-r18-BaseArmLeaks/lane rev-parse HEAD
b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
```

1. **r15 / pre-harm a31642d**

```text
python3 tests/fixtures/r15-census-config.py --tool /var/tmp/RevR14-census-a31642d.sh
TOOL  /var/tmp/RevR14-census-a31642d.sh  sha256=6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026
TOOL-KIND  pre-harm-a31642d
SUMMARY  total=20  failed=8
exit 1
```

The failing `R15CFG-03` detail included `r-inc-fifo: exit=124`, consistent with the pre-harm FIFO hang arm. The post-run `ps -eo pid,etimes,args` snapshot is `artifact://90179`; searching it for `r15-census-config.thjxtrmy` identified exactly these two processes from this invocation:

```text
504645  bash /var/tmp/RevR14-census-a31642d.sh --root /var/tmp/r15-census-config.thjxtrmy/unsafe-repos/r-inc-fifo --include-root
504728  /usr/bin/git -C /var/tmp/r15-census-config.thjxtrmy/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
```

I killed only those PIDs with `kill -KILL 504645 504728`. The subsequent `ps -eo pid,etimes,args` snapshot is `artifact://90253`; searching for the same prefix returned `No matches found` (2 → 0). Other fixture processes visible in the full process table had different prefixes and were not signalled.

2. **r17 / 5fa6017 census**

No `/var/tmp/*5fa6017*` extraction was present. I extracted the named source from the assigned clone's commit into the seat's temporary directory:

```text
git -C /var/tmp/souji-r18-BaseArmLeaks/lane show 5fa6017:tools/souji-census.sh > /var/tmp/souji-r18-BaseArmLeaks/census-5fa6017.sh && sha256sum /var/tmp/souji-r18-BaseArmLeaks/census-5fa6017.sh
64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c  /var/tmp/souji-r18-BaseArmLeaks/census-5fa6017.sh
```

Then:

```text
python3 tests/fixtures/r17-census-hygiene.py --census /var/tmp/souji-r18-BaseArmLeaks/census-5fa6017.sh
TOOL  /var/tmp/souji-r18-BaseArmLeaks/census-5fa6017.sh  sha256=64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c
SUMMARY  total=29  failed=15
exit 1
```

The output's `R17-29` case reported `exit=124`. The fixture did not print its generated random tempdir prefix. The post-run `ps -eo pid,etimes,args` snapshot is `artifact://90502`: searching for `census-5fa6017.sh` returned `No matches found`. Searching the generic `r17-census-hygiene.` prefix found only concurrent processes invoking `/var/tmp/souji-r17-FixtureR17Census/a31642d.sh` under `.e80b0xqe` and `/var/tmp/souji-r17-FixtureR17Census/cc21683.sh` under `.lwka_g_w`; neither was this run, and neither was signalled. Thus the count attributable to this invocation was 0, with no cleanup signal required. The fixture's omitted tempdir name means the available attribution is by its unique extracted tool path plus the complete generic-prefix scan, not a separately reported random prefix.

3. **r14 / cc21683 census**

```text
python3 tests/fixtures/r14-census-boundary.py --tool /var/tmp/RevR14-census-cc21683.sh
TOOL  /var/tmp/RevR14-census-cc21683.sh  sha256=fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9
SUMMARY  total=12  failed=0
exit 0
```

The post-run `ps -eo pid,etimes,args` snapshot is `artifact://90586`; searching for `r14-census-boundary.` returned `No matches found`: 0 residue, no PIDs to kill.

## Assigned selftest

```text
TMPDIR=/var/tmp bash tools/souji-census.sh --selftest
PASS hardlinked info/attributes: stderr finding + path
PASS git-metadata-unsupported printed once per repo (2)
PASS FIFO info/attributes: error row (no hang)
PASS FIFO info/attributes: stderr finding + path
PASS hygiene neighbour unaffected (clean)
PASS hardlinked config still refuses whole run (exit 2)
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.IXwnlB)
selftest: 49 checks, 0 failed
exit 0
```

## Finding

The assigned before-count is **2 leftover processes for the r15 pre-harm run, reaped to 0**; **0 attributable leftovers for r17**; and **0 for r14**. The r15 fixture's FIFO timeout is the concrete operability residue in this measurement. The b576341 census selftest completed with 49 checks and 0 failures, including its FIFO no-hang check. Exact retained process evidence: `artifact://90179`, `artifact://90253`, `artifact://90502`, and `artifact://90586`.
