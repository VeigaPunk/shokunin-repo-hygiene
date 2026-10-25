# Round 28 after-census recipe

Run from `/home/vgpnk/Projects/shokunin/souji-shokunin` after the round's changes are committed. These are frozen counters; do not alter predicates or targets. Expected values below are acceptance targets, not observed results.

1. **Grounded F4 entries — expect `6`:**
   ```sh
   grep -cE '^ground: F4' corpus/knowledge/*.md | paste -sd+ | bc
   ```
2. **SOURCES registry rows — expect `138`:**
   ```sh
   grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
   ```
3. **Landing gate — expect `SUMMARY findings=0` (no exemption used):**
   ```sh
   python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev "$(git rev-parse HEAD)" --round 28 --fleet-root /home/vgpnk/Projects/shokunin
   ```
4. **Dirty wave paths — expect `0`:**
   ```sh
   git status --porcelain=v1 --untracked-files=all | awk '$2 ~ /^\.ufo\/waves\// {n++} END{print n+0}'
   ```
5. **Evidence-capture fixture — expect `cases=6 pass=6 control=TAMPER-REJECTED`, exit 0:**
   ```sh
   bash tests/fixtures/r28-wave-evidence-capture.sh
   ```
6. **SOURCES census validation — expect exit code `0` and no `E` findings:**
   ```sh
   /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate /home/vgpnk/Projects/shokunin/souji-shokunin
   ```

Do not mark a target as passed unless the command was run at the final committed tip and its output/exit status was recorded. Recipe prepared against frozen contract `census/round-28/records/preregistration.txt` (C1–C3; C2 and C3 counter lines), read during this session.
