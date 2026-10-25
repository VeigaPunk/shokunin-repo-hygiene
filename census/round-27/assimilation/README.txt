Round-27 assimilation collision proof (source repo read-only)

Commands executed before the first SOURCES append; extracted files were copied into this committed-evidence directory and compared byte-for-byte with the .ufo/waves/round-27/assimilation outputs:

S=/home/vgpnk/Projects/shokuknow
A=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/assimilation
mkdir -p "$A"
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort > "$A/reg-ids"
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' "$S/merge/souji/SOURCES.append.md" | grep -oE 'S[0-9]+' | sort > "$A/staged-ids"
comm -12 "$A/reg-ids" "$A/staged-ids" > "$A/collisions"

Observed: reg-ids=132; staged-ids=134; collisions=24 (S109–S132). `renumber-map.tsv` accounts for all 24 collisions: 14 aliases to already-held rows, 2 rejected, 8 quarantined/not adopted. The three adopted ids S152/S210/S211 are absent from the collision set and are above the base maximum S132. There is no arithmetic renumbering of adopted ids.

The parser-compatible extractor accepts 0–3 leading spaces. The corresponding indented-row false-negative is independently demonstrated in `.ufo/waves/round-27/w1/LabCensusProbe.md` and reviewed in `.ufo/waves/round-27/w1/CritAssimAttack.md`.
