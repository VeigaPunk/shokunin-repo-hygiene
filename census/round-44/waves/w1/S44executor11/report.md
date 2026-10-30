# S44executor11 — C1 partition 11/16

## Axes
- Calibration: registered four emitted population keys with token-bound derivations.
- Operability: used the frozen counter in emit mode and checked committed base referents without modifying production.
- Coverage: audited the selected keys against the earlier round-42/43 correction declarations.

## Output
Correction register: `.ufo/waves/round-44/w1/S44executor11/corrections.txt` (four exact `CORRECTION-R44` lines; no optional fields). It is an output artifact only; the historical SCORECARD line numbers were not rewritten.

## Evidence
Commands run from the seat scratch, with lane as explicit `--root`:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor11 --emit
```

Counter emitted 66 unique records; zero-based indices `10,26,42,58` (index modulo 16 = 10) selected these exact records:

```text
R44-11 line=71 class=mismatch:path-absent stale=git-repo-structure-readonly.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md;census/round-26/waves/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md;corpus/knowledge/git-repo-structure-readonly.md
R44-27 line=512 class=mismatch:path-absent stale=c1-at-c2-repair.txt derived=census/round-33/records/c1-at-c2-repair.txt
R44-43 line=710 class=mismatch:path-absent stale=c2-after5.txt derived=census/round-38/records/c2-after5.txt
R44-59 line=792 class=mismatch:path-absent stale=c2-after-d.txt derived=census/round-40/records/c2-after-d.txt
```

Independent source check: `git cat-file -e <base>:<path>` against `55d7af6f5a22340f7a3de1c386e514ababfaa75f` returned PRESENT for the 5 derived paths listed in the lines (3 candidates for R44-11; one path each for the other three). The corresponding base SCORECARD cells were read directly at lines 71, 512, 710 and 792; their stale tokens match the emitted records. The attempted first R44-11 candidate `.ufo/waves/round-26/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md` was ABSENT, exactly distinguishing the surviving three paths from the superficially similar name.

Earlier-correction check: inspected the committed round-42 and round-43 lesson correction declarations at the base. Round 42 `CORRECTION-DE` covers lines 14, 68, 92 and 175; its `CORRECTION-SC` declarations cover lines 697 and 839. Round 43 declares only three R39 data corrections (rows, W04, header revision). Neither earlier declaration matches any of the four selected `(line,class,stale)` items; thus each is **not already covered by an r42/r43 correction**. Line 512's prose says older table cells were restated in r30/r31, but that is not an earlier correction of this `c1-at-c2-repair.txt` mismatch. Registration does not establish a new factual correction.

## Exact retained evidence / limitations
- Frozen revision was confirmed by `git show -s --format='%H' d314fd6e85d62565344fa6c4b102f52f62297884` → `d314fd6e85d62565344fa6c4b102f52f62297884`.
- Root was confirmed by `git rev-parse --show-toplevel` → `/home/vgpnk/Projects/shokunin/souji-shokunin`.
- Counter source defines derivation at `BASE_REV`, unique path selection / sorted `multi:` candidates, and emit IDs over unique `(line,token,class)` keys. The selected referents are independently present in the committed base tree.
- Counter `--emit` is a dry derivation output, not a registration acceptance run; no post-registration counter verdict is claimed. The broader round target and admission/closure remain outside this leaf task.
- No tools installed or updated.
