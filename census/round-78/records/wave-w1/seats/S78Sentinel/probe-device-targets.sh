#!/bin/bash
# #1: what `[[ -f ]]` admits and whether `git config --file` blocks.
. "$(dirname "$0")/probe-common.sh"; mkdir -p "$H/dev"; cd "$H/dev" || exit 1
python3 -c 'import socket,os;s=socket.socket(socket.AF_UNIX);s.bind("s.sock")' 2>/dev/null; [ -e f.fifo ] || mkfifo f.fifo
for t in /proc/kmsg /proc/self/mem /proc/self/environ /proc/sysrq-trigger /dev/zero /dev/stdin "$H/dev/f.fifo" "$H/dev/s.sock"; do
  [[ -f $t ]] && f=yes || f=no
  s=$(date +%s%N); timeout -k 2 5 git config --no-includes --file "$t" --get-regexp '^x$' >/dev/null 2>&1; rc=$?
  printf '%-24s -f=%s rc=%s %sms\n' "$t" "$f" "$rc" "$(( ($(date +%s%N)-s)/1000000 ))"
done
