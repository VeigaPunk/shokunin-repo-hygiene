#!/usr/bin/env bash
# souji r78 C2 probe G6 (S77MutCounter G6: MOVED proves bytes, not location). Builds a scratch clone of the lane
# at REV, commits a byte-equal copy of P04's moved capture at an unrelated round's path, and judges a one-row
# forged ledger (P04 MOVED <that path>) with the frozen r77 counter and with the r78 successor counter.
# Expected: r77 status=MOVED (accepted), r78 status=REFUSED. Usage: g6-collision.sh LANE REV WORK (WORK empty,
# not under /tmp). The clone is removed on exit; only stdout is evidence.
set -u
lane=$1 rev=$2 work=$3
case $(realpath -m -- "$work") in /tmp/*|/var/tmp/*|/dev/shm/*) echo "G6-FATAL: work under /tmp" >&2; exit 2 ;; esac
[[ ! -e $work || -z $(ls -A -- "$work") ]] || { echo "G6-FATAL: work not empty" >&2; exit 2; }
mkdir -p -- "$work"
D=$work/clone
trap 'rm -rf -- "$D"' EXIT
git clone -q --shared --no-checkout -- "$lane" "$D"
[[ $(git -C "$D" rev-parse --show-toplevel) == "$(realpath -- "$D")" ]] || { echo "G6-FATAL: toplevel" >&2; exit 2; }
git -C "$D" checkout -q --detach "$rev"
src=census/round-32/waves/a2w1/SwarmExecutor08.md
dst=census/round-02/waves/a2w1/SwarmExecutor08.md
mkdir -p -- "$D/$(dirname "$dst")"
cp -- "$D/$src" "$D/$dst"
git -C "$D" add -- "$dst"
git -C "$D" -c user.name=g6-fixture -c user.email=g6@fixture.invalid commit -q -m "g6 fixture: byte-equal copy at an unrelated round"
frev=$(git -C "$D" rev-parse HEAD)
echo "fixture_rev=$frev copy=$dst sha256=$(sha256sum -- "$D/$dst" | cut -d' ' -f1)"
led=$work/ledger-g6.tsv
{ printf '# g6 forged ledger\n'; grep -v '^P04	' "$lane/census/round-77/c2-pointer-ledger.tsv" | grep -v '^#'; printf 'P04\tMOVED\t%s\tforged g6\n' "$dst"; } > "$led"
r77=$(python3 -B "$lane/census/round-77/c2-pointer-counter.py" --root "$D" --rev "$frev" --fleet-root "$(dirname "$lane")" --ledger "$led" | grep '^ITEM P04 ')
r78=$(python3 -B "$lane/census/round-78/c2-pointer-counter.py" --root "$D" --rev "$frev" --fleet-root "$(dirname "$lane")" --population "$lane/census/round-77/c2-population.tsv" --ledger "$led" | grep '^ITEM P04 ')
echo "r77: $r77"
echo "r78: $r78"
ok=1
[[ $r77 == *status=MOVED* ]] || ok=0
[[ $r78 == *status=REFUSED* ]] || ok=0
echo "G6 r77_accepts=$([[ $r77 == *status=MOVED* ]] && echo yes || echo no) r78_refuses=$([[ $r78 == *status=REFUSED* ]] && echo yes || echo no)"
(( ok )) && exit 0 || exit 1
