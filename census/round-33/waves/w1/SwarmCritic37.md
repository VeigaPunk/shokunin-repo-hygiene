# SwarmCritic37 — C2 legs and counter (attack)

## Status
STATUS: PASS — the frozen C2 leg set and counter were attacked on paper and by runs; four doubts were reproduced in scratch (three with the frozen counter or its own guards), one leg was shown to be unstable on the base anchor. No frozen artifact was changed; no lane write outside this file.

## Evidence

Scratch root `/fast/scratch/hyaku/souji-r33/AttackC2Predicates/`, clone of the lane at base `6017a482e7068d5afb7617640198fbb0fe743357`, legs read at prereg `2d9bca55a9f042a2c9ed60a797a8069e74c41f46` (all runs `python3 -B`, `TMPDIR` a scratch dir, origin dropped immediately after clone).

**E1 — constants fixture passes the frozen `sandbox-nt` leg.** Scratch commit `c3ac4997cfc7d7dbbe7deb91dbc344853e41f404` = base + `tests/fixtures/r15-census-config.py` replaced by five lines that print one constant and exit 0, with no scratch dir, no HOME, no tool run:
```
LEG	O2	sandbox-nt	PASS	base=rc0:SUMMARY total=20 failed=0	sbox=rc0:SUMMARY total=20 failed=0
SUMMARY legs=1 pass=1 fail=0 harm=0 partial=1 rev=c3ac4997cfc7d7dbbe7deb91dbc344853e41f404
rc=0
```
Command: `census/round-33/c2-counter.py --root <clone> --rev c3ac499… --base 6017a48… --list-rev 2d9bca5… --scratch <s1> --only O2`.

**E2 — the agreed O1 repair path removes the live identity check.** Base runner `census/round-21/run-acceptance.py:503` compares the r21 receipt's `gate.sha256` to `sha256(live tools/souji-evidence-cache.py)`. Appending one comment byte to that file in a clone turned the r22 oracle red (`{"total":258,"pass":256,"fail":2,"finding_id":"R22-RESULT-CONTRACT"}`, rc 1). Applying the feasibility runner hunk (`census/round-33/records/feasibility.txt:248-255`: read the blob at `revision` instead of the live file) with the comment still in place turned it green: `{"total":258,"pass":258,"fail":0,"finding_id":null}`, rc 0.

**E3 — slash legs test one spelling.** With a fix that strips exactly one trailing slash (`TMPDIR=${TMPDIR%/}`, inserted once after `tools/souji-census.sh:188`), scratch commit `8f974e665db28da4e79fd91a5d0163042fc52f64`:
- `TMPDIR=<dir>/` → `selftest: 69 checks, 0 failed` (rc 0), and `TMPDIR=<dir>` → `69 checks, 0 failed`, which is the whole `slash` PASS rule.
- `TMPDIR=<dir>//` → `selftest: 69 checks, 10 failed` (rc 1) — the base defect, unchanged.

Kernel-vs-pattern micro-test (same scratch, `mktemp`-style path + `/proc/self/fd` readlink): for `<dir>/` raw pattern `…/x//souji-census-now.*` does not match the kernel's `…/x/souji-census-now.*`; the strip-one pattern does; for `<dir>//` and `<dir>/.` the strip-one pattern still does not match (kernel reports the collapsed single-slash path in both cases).

**E4 — G4 accepts a self-consistent but false re-pin.** Clone at base, `tools/souji-census.sh:1240` changed `--untracked-files=normal` → `--untracked-files=no` (a documented semantic, `SKILL.md:202`; new tool sha256 `16c88d9f31d72eb9121a55dcb8636989100c500c09e49bf05f7ecffeddbb17fe`), then `record.json` changed-arm/namespace tool sha and commit restamped (`measured_commit=1111…`) and `expected.json` re-pinned by hand:
```
souji-preservation-evidence: clean
scope: declared-record consistency only; no command execution or execution proof
measured_commit: 1111111111111111111111111111111111111111
frozen_files: 3
rc=0
```
That is exactly the guard line the counter compares (`frozen_files: 3`, `tools/souji-preservation-evidence.py:1783-1784`).

**E5 — the base anchor of the `slash` legs is not stable under the counter's own wrapper.** At base `6017a48`, `strace -f -qq -o log -e trace=mkdir,mkdirat,creat,open,openat,openat2 bash tools/souji-census.sh --selftest`, `TMPDIR` a clean scratch dir: `selftest: 69 checks, 7 failed`, rc 1 (failing checks: `watchdog neighbour … fields=0/0/error` ×2, `watchdog wall time 10856ms`, `timed-out FIFO nonblocking open did not return ENXIO`, `timed-out Git process remains`, `parent SIGKILL cleanup`, `SIGTERM-ignored run rc=0 flags=clean`). The same tree and TMPDIR **without** the wrapper: `69 checks, 0 failed`. The frozen receipt has `base=rc0:selftest: 69 checks, 0 failed` three times (`census/round-33/records/feasibility.txt:167,181,195`). The frozen counter run of the same leg on a correct-in-shape fix read `base=rc1:selftest: 69 checks, 8 failed  rev=rc1:… 7 failed  rev-slash=rc1:… 7 failed` → `fail=1`.

**E6 — consumer sweep** (`git grep -l -F <path> -- tools tests SKILL.md 'census/*/*.py' 'census/*/*.sh'`, live paths only): `tools/souji-census.sh` has registered-gate consumers `r14-census-boundary` (`SKILL.md:211`, default tool `tests/fixtures/r14-census-boundary.py:681`) and `r18-census-bounded` (`SKILL.md:223`, default `tests/fixtures/r18-census-bounded.py:1732`), plus `r17-census-hygiene` (G6), `r15-preservation-evidence` (G5), `r15-census-config` (O2) and `souji-landing-gate` (`SKILL.md:218`, frozen-pin finding). `census/round-13/run-verification.py:140-141` and `census/round-20/run-acceptance.py:30-75` list the tool but resolve digests at a named revision, so they are not live-byte pins. `tests/fixtures/r15-preservation-evidence.py` has one `subprocess.run` (`:84`, the preservation tool); arms are synthesized by `arm()` (`:113`) over a `#!/bin/sh` stand-in (`:156-158`), so it never executes the census tool or the config fixture.

## Findings

1. **`sandbox-nt` has no work proof: a constants fixture passes** (`census/round-33/c2-legs.tsv:8-11`; rule at `census/round-33/c2-counter.py:172-175`). E1 is a PASS from the frozen counter for a five-line fixture that builds no world, opens no file and runs no tool. The header says the work proof "is its own last line", but that line is lane-authored data. O3 has the same rule and the same exposure: its line is the fixed r16 matrix (`baseline_preharm=8/20 … changed=0/20 fail, verdict=clean`) with digests normalised to `<HEX>` (`c2-counter.py:52-58`). `[INFERENCE]` from the identical PASS rule and the same one-line summary shape; not run.
2. **The `slash` legs prove one spelling, not the class** (`c2-legs.tsv:12-14`; `c2-counter.py:146` appends exactly one `/`). E3: a fix that strips one slash satisfies the leg's whole comparison yet leaves `//` at the base's 10 false failures; `/./` is not covered by the strip-one pattern at all. The routed defect asks to "canonicalise the `case` pattern" (`corpus/lessons/round-32-verifier-spotcheck.md:131`), and the L1's demonstrated fix loops all trailing slashes (`feasibility.txt:257-262`), so the *fix* is broader than the *leg*: the leg would accept a repair that leaves a class member broken.
3. **O1's second half is not measured, and the repair path disables the check it was meant to update.** Routed defect 2 requires "an updated digest pin in `census/round-21/run-acceptance.py`, under Q73" (`round-32-verifier-spotcheck.md:132`). G1 grades the r21 receipt through the r22 oracle, but the feasibility repair rewrites the pin to compare the payload digest against the tool blob *at the payload's own revision* (`feasibility.txt:248-255`) — a tautology. E2 is the reproduced state: drift that the base runner catches (fail=2) is invisible after the repair (fail=0). G1 cannot see the difference because both forms print `"total": 258` and differ only in rc, which is identical when no drift is present. Q73's own allowed actions are "regenerated with its own committed script at the candidate, or the tool edit is reverted" (`corpus/QUALITY.md:178`); redefining the consumer is neither.
4. **Two registered gates that execute `tools/souji-census.sh` are missing from G1-G6** (E6): `r14-census-boundary` (`SKILL.md:211`) and `r18-census-bounded` (`SKILL.md:223`). Q73 requires "every registered gate" green at the candidate where it was green at base (`corpus/QUALITY.md:178`); the leg set measures only `r17-census-hygiene` (G6) for that tool. `souji-landing-gate` (`SKILL.md:218`, frozen-pin finding) is also absent. The five-file G set is otherwise well chosen for the cache tool (G1/G2/G3) and for the frozen pin (G4/G5), but G4/G5 are consistency checks, not behaviour checks (finding 5).
5. **The "C2 landing = re-pin commit" rule hides harms from the pin guards by construction** (`census/round-33/preregistration.txt`, C2 "C2 landing commit" paragraph). At that commit G4 compares the record against a pin the same commit regenerated, and `--frozen` executes nothing (`tools/souji-preservation-evidence.py:1772` prints "no command execution or execution proof"); G5 executes nothing but that tool (`tests/fixtures/r15-preservation-evidence.py:84`). E4 shows the upper bound: a tree whose `souji-census.sh` no longer counts untracked files as dirty returns G4 rc0/`frozen_files: 3` with a self-consistent hand-written record. The prereg's "the repair commit's own reading (G4 red) is recorded, not hidden" is an L1 receipt obligation: the predicate reads only the landing commit and the tip, so no reading at the repair commit is measured. Residual coverage of "nothing else changes" (Q71, `corpus/QUALITY.md:176`) is therefore exactly O4/G6 for `tools/souji-census.sh`, O2 for `r15-census-config.py`, O3 for `regenerate.py` — and the first and third are the unstable/self-asserted legs of findings 1 and 6. (I do not claim the E4 harm passes O4/G6; that was not run.)
6. **O4/O5's base anchor is not stable on a loaded host** (E5). The `slash`/`guard` runs are strace-wrapped (`c2-counter.py:171`, `trace=kind != "sandbox-nt"`), and the census selftest fails 6-8 of its own process-control checks under that wrapper at the base revision while passing 69/0 unwrapped at the same moment. Because the leg compares rev to base *within one run* on the count-only last line (`selftest: 69 checks, N failed`), drift can yield a spurious FAIL on honest work (observed: base 8 / rev 7) or a spurious PASS when the two drift to the same N. This is the r30-r32 "target honest work cannot reach" shape the prereg says it removed; Q70b stability was measured in a quiet window, not under wave load.

## Attack log

- A1 (E1) reproduced: frozen counter prints `LEG O2 sandbox-nt PASS` for a constants fixture at `rev=c3ac499…`; summary `pass=1 fail=0 harm=0`, rc 0.
- A2 (E2) reproduced: live-tool drift is red at the base runner (`fail=2`) and green after the feasibility runner hunk (`fail=0`), rc 0, same `"total": 258`.
- A3 (E3) reproduced at the level the leg compares: strip-one fix gives the same rc and last line for `TMPDIR=<dir>` and `<dir>/` (69/0, rc 0) while `<dir>//` gives 69/10; the counter's own attempt was inconclusive only because the base anchor flaked (E5). Micro-test shows the pattern/kernel mismatch mechanism for `/`, `//`, `/.`.
- A4 (E4) reproduced: G4 `clean`, rc 0, `frozen_files: 3` on a tree whose census semantics changed, with a hand-restamped record and pin.
- A5 (E5) reproduced: base `6017a48` under the counter's wrapper → `69 checks, 7 failed`; unwrapped → `69 checks, 0 failed`; frozen receipt says 0 failed three times.

## Smallest safe corrections (stricter-only; L1 owns any amendment)
- F1: for `sandbox-nt` legs, add a non-ptrace work proof — watch the leg's `TMPDIR` during the rev run (inotify or sampling) and require at least one entry to appear (a rev that only prints creates nothing); for O3 additionally require the regenerated pin bytes to differ from the base pin when the tree differs.
- F2: add one more `slash` spelling (`TMPDIR=<dir>//`) to the same leg; the L1's loop fix already passes it, the strip-one class of fix does not.
- F3: keep the live comparison at `census/round-21/run-acceptance.py:503` and re-pin the r21 payload by its own committed script at the candidate (Q73), or land no cache-tool edit; optionally add a pin-teeth leg that appends one comment byte to the live tool in the run clone and requires the r22 oracle to go red.
- F4: add `r14-census-boundary` and `r18-census-bounded` as guards (both must be green at base first), and `souji-landing-gate` if the landing gate is green at base.
- F5: make the guard line carry the verdict, not only the pin count (G4's last digit-bearing line is `frozen_files: N`), and require a regenerator negative control (a harmed tool copy must produce a red record).
- F6: run the O4/O5 base anchor three times on a loaded host before freezing, or compare the failing-check set (not only the count) so drift cannot pass; alternatively stop strace-wrapping timing-sensitive selftests.

## Deliveries
- `.ufo/waves/round-33/w1/SwarmCritic37.md` (this file).

Scratch removed after the receipts were copied. Observed and **not** removed (not attributable, and peers may be live): `/var/tmp/r15-census-config.{3tk6qehq,psjsbayp,xec8q0wl,vfspp20c}` — the 14:15:33 one is mine from a killed base run; the fixture's hardcoded `/var/tmp` root (`tests/fixtures/r15-census-config.py:1545`) leaves it when a run is killed. No tools installed or upgraded.
