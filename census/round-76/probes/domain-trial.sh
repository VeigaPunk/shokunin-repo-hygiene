#!/usr/bin/env bash
L=/home/vgpnk/Projects/shokunin/souji-shokunin
printf '# amendment (prereg C1 domain-trial clause): C1 candidate gate blob (e827d2bf) sha256=18587bd2ff103f8ee136a3b6e59e96039f3202e06c688a8ecb7c8f4bf76623ad -> wave-repaired gate blob (9cbfd296) sha256=%s\n' "$(sha256sum "$L/tools/souji-pre-report-gate.sh" | cut -d' ' -f1)"
printf '# writer sha256=%s\n' "$(sha256sum "$L/tools/souji-receipt-write.py" | cut -d' ' -f1)"
printf '# lane master=%s ls-remote=%s tracked=%s ignored-untracked=%s\n' "$(git -C "$L" rev-parse master)" "$(git -C "$L" ls-remote origin refs/heads/master | cut -f1)" "$(git -C "$L" ls-files | wc -l)" "$(git -C "$L" ls-files -o -i --exclude-standard | wc -l)"
printf '# attribution by source: %s\n' "$(git -C "$L" ls-files -z -o -i --exclude-standard | git -C "$L" -c core.excludesFile=/dev/null check-ignore -v -n -z --stdin | tr '\0' '\n' | paste - - - - | cut -f1 | sort | uniq -c | tr '\n' ';')"
s=$(date +%s%N)
bash "$L/tools/souji-pre-report-gate.sh" --lane "$L" --branch master --report "/home/vgpnk/Projects/shokunin/.ufo/reports/round-76/souji.md" --prereg "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-76/preregistration.txt"
rc=$?
printf '# wall_ms=%s\n' "$(( ($(date +%s%N)-s)/1000000 ))"
exit $rc
