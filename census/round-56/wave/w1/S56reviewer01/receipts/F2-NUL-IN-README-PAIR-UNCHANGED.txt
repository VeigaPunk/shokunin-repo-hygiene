CASE F2-NUL-IN-README-PAIR-UNCHANGED
KIND limit  CLASS LIMIT
NOTE NUL splits an overstated pair annotation in corpus/README.md (unchanged)
FIXTURE dir=/fast/scratch/hyaku/souji-r56/S56reviewer01/work/f2_nul_in_readme_pair_unchanged base=f3294baad924e7291180224e7639ff7c3a0c5c95 tip=2e066e5389d1d44e99e6e8443cb9d74389ebf79b
SCORECARD.md tip bytes (repr):
'# fixture SCORECARD (round-54 C1 matrix, f2_nul_in_readme_pair_unchanged)\n\n| row | note |\n|---|---|\n| C1 | command `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) recomputed below |\n\nR52-CORRECTION SCORECARD.md:5 stale=78 recomputed=79\nR52-CORRECTION census/round-51/preregistration.txt:3 stale=78 recomputed=79\n\n'
LOG.md tip bytes (repr):
''
CM (markdown-it-py 4.2.0 commonmark): n/a
--- v4 committed round-55 (c1-v4.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v4.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f2_nul_in_readme_pair_unchanged --rev 2e066e5389d1d44e99e6e8443cb9d74389ebf79b --base f3294baad924e7291180224e7639ff7c3a0c5c95 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 2e066e5389d1d44e99e6e8443cb9d74389ebf79b --sources-rev-after 2e066e5389d1d44e99e6e8443cb9d74389ebf79b --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/F2-NUL-IN-README-PAIR-UNCHANGED
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=2e066e5389d1 base=f3294baad924
EXIT=0
--- v5 committed round-56 (c1-v5.py) ---
CMD: python3 -B /fast/scratch/hyaku/souji-r56/S56reviewer01/bin/c1-v5.py --root /fast/scratch/hyaku/souji-r56/S56reviewer01/work/f2_nul_in_readme_pair_unchanged --rev 2e066e5389d1d44e99e6e8443cb9d74389ebf79b --base f3294baad924e7291180224e7639ff7c3a0c5c95 --record-sha256 d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf --sources-rev-before 2e066e5389d1d44e99e6e8443cb9d74389ebf79b --sources-rev-after 2e066e5389d1d44e99e6e8443cb9d74389ebf79b --scratch /fast/scratch/hyaku/souji-r56/S56reviewer01/scratch-att/F2-NUL-IN-README-PAIR-UNCHANGED
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=2e066e5389d1 base=f3294baad924
EXIT=0
SUMMARY v4 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79 rev=2e066e5389d1 base=f3294baad924
SUMMARY v5 SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=2e066e5389d1 base=f3294baad924
EXPECTATION-CHECK ok
EXIT=0
