#!/usr/bin/env bash
# souji-proc-census — read-only census of current-uid processes retaining
# deleted scratch paths. It never signals a process outside its selftest.
#
# Output begins with a boot-id comment, then ten TSV fields: pid, ppid,
# pgid, sid, age_s, starttime, state, wchan, reason, and cmd. Both reason and
# cmd have bounded secret-pattern redaction; raw reads are not secret-free.
# Usage: tools/souji-proc-census.sh [--prefix DIR]... [--min-age S] [--selftest]
#        tools/souji-proc-census.sh --reason-only argv|fd [--prefix DIR]...
set -euo pipefail
unset -f bash basename cat cd command dirname getconf kill mkdir mkfifo mktemp \
  printf pwd read readlink rm setsid sleep wait 2>/dev/null || true
export LC_ALL=C

readonly HEADER=$'pid\tppid\tpgid\tsid\tage_s\tstarttime\tstate\twchan\treason\tcmd'
readonly SELF_PID=$BASHPID
MIN_AGE=0
SELFTEST=0
REASON_ONLY=''
PREFIX_SET=0
PREFIXES=()

usage() {
  cat <<'USAGE'
Usage: souji-proc-census.sh [--prefix DIR]... [--min-age S] [--selftest]
       souji-proc-census.sh --reason-only argv|fd [--prefix DIR]...
  --prefix DIR  Scratch-path prefix for argv/fd checks only (repeatable;
                defaults to /var/tmp, /tmp, /dev/shm); cwd checks are not narrowed
  --min-age S   Minimum process age in integer seconds (default: 0)
  --selftest    Run the bounded /var/tmp residue and redaction fixture
  --reason-only argv|fd
                Format synthetic stdin only, without opening /proc: argv is
                NUL-separated; fd is one path (one trailing newline removed).
                Exit 3, no output, when no vanished scratch path is selected.

Exit status: 0 census emitted, 1 selftest/setup failure, 2 invalid usage.
USAGE
}

usage_error() {
  printf 'souji-proc-census: %s\n' "$1" >&2
  usage >&2
  exit 2
}
normalize_prefix() {
  local path=$1 part
  local -a components=()
  [[ $path == /* ]] || path=$PWD/$path
  IFS=/ read -r -a components <<< "$path"
  NORMALIZED_PATH=''
  for part in "${components[@]}"; do
    case "$part" in
      ''|.) continue ;;
      ..)
        case "$NORMALIZED_PATH" in
          ''|/) ;;
          *) NORMALIZED_PATH=${NORMALIZED_PATH%/*}; [[ -n $NORMALIZED_PATH ]] || NORMALIZED_PATH=/ ;;
        esac
        ;;
      *)
        if [[ $NORMALIZED_PATH == / || -z $NORMALIZED_PATH ]]; then
          NORMALIZED_PATH=/$part
        else
          NORMALIZED_PATH+=/$part
        fi
        ;;
    esac
  done
  [[ -n $NORMALIZED_PATH ]] || NORMALIZED_PATH=/
}

while (($#)); do
  case "$1" in
    --prefix)
      (($# >= 2)) || usage_error '--prefix needs a directory'
      [[ -n $2 ]] || usage_error '--prefix needs a directory'
      normalize_prefix "$2"
      prefix=$NORMALIZED_PATH
      if ((PREFIX_SET == 0)); then
        PREFIXES=()
        PREFIX_SET=1
      fi
      PREFIXES+=("$prefix")
      shift 2
      ;;
    --min-age)
      (($# >= 2)) || usage_error '--min-age needs seconds'
      [[ $2 =~ ^[0-9]{1,10}$ ]] || usage_error '--min-age must be an integer from 0 to 2147483647'
      min_age_decimal=$((10#$2))
      ((min_age_decimal <= 2147483647)) || usage_error '--min-age must be an integer from 0 to 2147483647'
      MIN_AGE=$min_age_decimal
      shift 2
      ;;
    --reason-only)
      (($# >= 2)) || usage_error '--reason-only needs argv or fd'
      [[ $2 == argv || $2 == fd ]] || usage_error '--reason-only needs argv or fd'
      REASON_ONLY=$2
      shift 2
      ;;
    --selftest)
      SELFTEST=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage_error "unknown option: $1"
      ;;
  esac
done
[[ -z $REASON_ONLY || $SELFTEST == 0 ]] || usage_error '--reason-only and --selftest conflict'

if ((PREFIX_SET == 0)); then
  PREFIXES=(/var/tmp /tmp /dev/shm)
fi

# A snapshot of stat identity fields for each process lets the scanner omit
# itself and its descendants without spawning per-process helper commands.
declare -A PARENT_BY_PID=()
declare -A STAT_BY_PID=()

parse_proc_stat() {
  local proc_path=$1 stat_line='' stat_tail stat_part='' stat_started=0
  local -a fields=()

  while IFS= read -r stat_part || [[ -n $stat_part ]]; do
    if ((stat_started)); then stat_line+=$'\n'; fi
    stat_line+=$stat_part
    stat_started=1
  done < "$proc_path/stat" 2>/dev/null || return 1
  ((stat_started)) || return 1
  # comm may contain spaces, ')', or embedded newlines; remove through its
  # final ') ' delimiter before splitting the fixed numeric fields.
  stat_tail=${stat_line##*) }
  [[ $stat_tail != "$stat_line" ]] || return 1
  read -r -a fields <<< "$stat_tail"
  ((${#fields[@]} >= 20)) || return 1
  [[ ${fields[1]} =~ ^[0-9]+$ && ${fields[2]} =~ ^[0-9]+$ &&
     ${fields[3]} =~ ^[0-9]+$ && ${fields[19]} =~ ^[0-9]+$ ]] || return 1

  PROC_STATE=${fields[0]}
  PROC_PPID=${fields[1]}
  PROC_PGID=${fields[2]}
  PROC_SID=${fields[3]}
  PROC_STARTTICKS=${fields[19]}
}

is_self_tree() {
  local cursor=$1 parent hops=0
  while [[ $cursor =~ ^[0-9]+$ ]] && ((hops < 512)); do
    [[ $cursor == "$SELF_PID" ]] && return 0
    parent=${PARENT_BY_PID[$cursor]:-}
    [[ -n $parent && $parent != "$cursor" ]] || break
    cursor=$parent
    hops=$((hops + 1))
  done
  return 1
}

process_uid() {
  local proc_path=$1 line
  PROC_UID=''
  while IFS= read -r line; do
    if [[ $line == Uid:* ]]; then
      read -r _ PROC_UID _ <<< "$line"
      [[ $PROC_UID =~ ^[0-9]+$ ]] && return 0
      return 1
    fi
  done < "$proc_path/status" 2>/dev/null
  return 1
}

path_under_prefix() {
  local path=$1 prefix=$2
  if [[ $prefix == / ]]; then
    [[ $path == /* ]]
  else
    [[ $path == "$prefix" || ${path#"$prefix"/} != "$path" ]]
  fi
}
top_level_scratch_gone() {
  local path=$1 prefix=$2 remainder top
  [[ $path != "$prefix" ]] || return 1
  path_under_prefix "$path" "$prefix" || return 1
  if [[ $prefix == / ]]; then
    remainder=${path#/}
  else
    remainder=${path#"$prefix"/}
  fi
  [[ -n $remainder ]] || return 1
  top=${remainder%%/*}
  [[ -n $top ]] || return 1
  if [[ $prefix == / ]]; then
    TOP_LEVEL_PATH=/$top
  else
    TOP_LEVEL_PATH=$prefix/$top
  fi
  [[ ! -e $TOP_LEVEL_PATH ]]
}

sanitize_field() {
  SAFE_FIELD=${1//[$'\001'-$'\037'$'\177']/ }
}

redact_secrets() {
  local value=$1 replacement
  value=${value//[$'\001'-$'\037'$'\177']/ }

  while [[ $value =~ ([Aa][Uu][Tt][Hh][Oo][Rr][Ii][Zz][Aa][Tt][Ii][Oo][Nn]:[[:space:]]*[Bb][Ee][Aa][Rr][Ee][Rr][[:space:]]+)[^[:space:]]+ ]]; do
    replacement=${BASH_REMATCH[1]%%:*}': [REDACTED]'
    value=${value/"${BASH_REMATCH[0]}"/"$replacement"}
  done
  while [[ $value =~ (--[Tt][Oo][Kk][Ee][Nn]=)[^[:space:]]+ ]]; do
    replacement=${BASH_REMATCH[1]}' [REDACTED]'
    value=${value/"${BASH_REMATCH[0]}"/"$replacement"}
  done
  while [[ $value =~ (ghp_)[[:alnum:]_-]+ ]]; do
    replacement=${BASH_REMATCH[1]}'[REDACTED]'
    value=${value/"${BASH_REMATCH[0]}"/"$replacement"}
  done
  while [[ $value =~ (sk-)[[:alnum:]_.-]+ ]]; do
    replacement=${BASH_REMATCH[1]}'[REDACTED]'
    value=${value/"${BASH_REMATCH[0]}"/"$replacement"}
  done
  while [[ $value =~ ([Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]=)[^[:space:]]+ ]]; do
    replacement=${BASH_REMATCH[1]}' [REDACTED]'
    value=${value/"${BASH_REMATCH[0]}"/"$replacement"}
  done
  while [[ $value =~ ([[:alpha:]][[:alnum:].+-]*://)[^/@[:space:]]*@ ]]; do
    replacement=${BASH_REMATCH[1]}'[REDACTED] @'
    value=${value/"${BASH_REMATCH[0]}"/"$replacement"}
  done
  while [[ $value =~ AKIA[0-9A-Z]{16} ]]; do
    value=${value/"${BASH_REMATCH[0]}"/'[REDACTED]'}
  done
  while [[ $value =~ xox[baprs]-[[:alnum:]_.-]+ ]]; do
    value=${value/"${BASH_REMATCH[0]}"/'[REDACTED]'}
  done
  REDACTED_FIELD=$value
}

redact_command() {
  redact_secrets "$1"
  # Bash substring slicing is byte-based because LC_ALL=C is fixed above.
  REDACTED_CMD=${REDACTED_FIELD:0:160}
}

format_reason() {
  local kind=$1 path=$2 secret=${3:-0}
  if ((secret)); then path='[REDACTED]'; fi
  redact_secrets "$kind-path-gone:$path"
  REDACTED_REASON=${REDACTED_FIELD:0:160}
}

# The stream parser is shared by the census and the /proc-free fixture mode.
read_argv_stream() {
  local arg='' prefix candidate redact_next=0 secret normalized
  CMD_RAW=''
  PROC_GONE_PATH=''
  PROC_GONE_SECRET=0
  while IFS= read -r -d '' arg || [[ -n $arg ]]; do
    sanitize_field "$arg"
    normalized=$SAFE_FIELD
    redact_secrets "$arg"
    secret=$redact_next
    [[ $REDACTED_FIELD == "$normalized" ]] || secret=1
    candidate=''
    case "$arg" in
      /*) candidate=$arg ;;
      --*=/*) candidate=${arg#*=} ;;
    esac
    if [[ -z $PROC_GONE_PATH && $candidate == /* && ! -e $candidate ]]; then
      for prefix in "${PREFIXES[@]}"; do
        if top_level_scratch_gone "$candidate" "$prefix"; then
          PROC_GONE_PATH=$candidate
          PROC_GONE_SECRET=$secret
          break
        fi
      done
    fi

    if ((redact_next)); then
      arg='[REDACTED]'
      redact_next=0
    elif [[ ${arg,,} == --token ]]; then
      redact_next=1
    fi
    CMD_RAW+="${CMD_RAW:+ }$arg"
  done
}

read_process_argv() {
  read_argv_stream < "$1/cmdline" 2>/dev/null || true
}
find_deleted_fd_path() {
  local proc_path=$1 fd_path fd_link target prefix
  PROC_FD_GONE_PATH=''
  for fd_path in "$proc_path"/fd/*; do
    [[ -L $fd_path ]] || continue
    fd_link=$(readlink -- "$fd_path" 2>/dev/null) || continue
    [[ $fd_link == *' (deleted)' ]] || continue
    [[ -e $fd_link && $fd_link -ef $fd_path ]] && continue
    target=${fd_link%' (deleted)'}
    [[ $target == /* ]] || continue
    for prefix in "${PREFIXES[@]}"; do
      if top_level_scratch_gone "$target" "$prefix"; then
        PROC_FD_GONE_PATH=$target
        return 0
      fi
    done
  done
  return 1
}

read_uptime_ticks() {
  local clock_ticks=$1 uptime_value seconds hundredths
  IFS=' ' read -r uptime_value _ < /proc/uptime || return 1
  [[ $uptime_value =~ ^([0-9]+)\.([0-9]{2})$ ]] || return 1
  seconds=${BASH_REMATCH[1]}
  hundredths=${BASH_REMATCH[2]}
  UPTIME_TICKS=$((10#$seconds * clock_ticks + 10#$hundredths * clock_ticks / 100))
}
read_boot_id() {
  BOOT_ID=''
  IFS= read -r BOOT_ID < /proc/sys/kernel/random/boot_id || return 1
  [[ -n $BOOT_ID ]] || return 1
  sanitize_field "$BOOT_ID"
  BOOT_ID=$SAFE_FIELD
}

census() {
  local proc_path pid clock_ticks age reason cwd wchan snapshot_start
  read_boot_id || {
    printf 'souji-proc-census: unable to read boot_id from /proc/sys/kernel/random/boot_id\n' >&2
    return 1
  }

  clock_ticks=$(getconf CLK_TCK 2>/dev/null) || {
    printf 'souji-proc-census: unable to determine CLK_TCK\n' >&2
    return 1
  }
  [[ $clock_ticks =~ ^[1-9][0-9]*$ ]] || {
    printf 'souji-proc-census: invalid CLK_TCK\n' >&2
    return 1
  }
  read_uptime_ticks "$clock_ticks" || {
    printf 'souji-proc-census: unable to read uptime from /proc/uptime\n' >&2
    return 1
  }

  for proc_path in /proc/[0-9]*; do
    [[ -d $proc_path ]] || continue
    pid=${proc_path##*/}
    parse_proc_stat "$proc_path" || continue
    PARENT_BY_PID[$pid]=$PROC_PPID
    STAT_BY_PID[$pid]="$PROC_STATE $PROC_PPID $PROC_PGID $PROC_SID $PROC_STARTTICKS"
  done

  printf '# boot_id %s\n' "$BOOT_ID"
  printf '%s\n' "$HEADER"
  for proc_path in /proc/[0-9]*; do
    [[ -d $proc_path ]] || continue
    pid=${proc_path##*/}
    [[ -n ${STAT_BY_PID[$pid]:-} ]] || continue
    snapshot_start=${STAT_BY_PID[$pid]##* }
    parse_proc_stat "$proc_path" || continue
    [[ $PROC_STARTTICKS == "$snapshot_start" ]] || continue
    PARENT_BY_PID[$pid]=$PROC_PPID
    is_self_tree "$pid" && continue
    process_uid "$proc_path" || continue
    [[ $PROC_UID == "$UID" ]] || continue
    age=$(((UPTIME_TICKS - PROC_STARTTICKS) / clock_ticks))
    ((age >= 0)) || age=0
    ((age >= MIN_AGE)) || continue

    reason=''
    cwd=$(readlink -- "$proc_path/cwd" 2>/dev/null) || cwd=''
    if [[ $cwd == *' (deleted)' ]] &&
       ! [[ -e $cwd && $cwd -ef "$proc_path/cwd" ]]; then
      reason='cwd-deleted'
    fi
    read_process_argv "$proc_path"
    if [[ -z $reason && -n $PROC_GONE_PATH ]]; then
      format_reason argv "$PROC_GONE_PATH" "$PROC_GONE_SECRET"
      reason=$REDACTED_REASON
    fi
    if [[ -z $reason ]]; then
      find_deleted_fd_path "$proc_path" || true
      if [[ -n $PROC_FD_GONE_PATH ]]; then
        format_reason fd "$PROC_FD_GONE_PATH"
        reason=$REDACTED_REASON
      fi
    fi
    [[ -n $reason ]] || continue

    wchan=''
    IFS= read -r wchan < "$proc_path/wchan" 2>/dev/null || true
    [[ -n $wchan ]] || wchan='-'
    sanitize_field "$wchan"
    wchan=$SAFE_FIELD
    redact_command "$CMD_RAW"
    row_cmd=$REDACTED_CMD
    [[ -n $row_cmd ]] || row_cmd='-'
    safe_reason=$reason

    # Do not emit data read across a PID reuse or UID transition.
    process_uid "$proc_path" || continue
    [[ $PROC_UID == "$UID" ]] || continue
    parse_proc_stat "$proc_path" || continue
    [[ $PROC_STARTTICKS == "$snapshot_start" ]] || continue
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$pid" "$PROC_PPID" "$PROC_PGID" "$PROC_SID" "$age" \
      "$PROC_STARTTICKS" "$PROC_STATE" "$wchan" "$safe_reason" "$row_cmd"
  done
}

SELFTEST_TMP=''
SELFTEST_CONTROL_TMP=''
SELFTEST_OUT=''
SELFTEST_LITERAL_OUT=''
SELFTEST_PIDS=()
declare -A SELFTEST_STARTTIMES=()

remember_selftest_pid() {
  local pid=$1 attempt=0
  while ((attempt < 100)); do
    if parse_proc_stat "/proc/$pid" &&
       [[ $PROC_PPID == "$SELF_PID" && $PROC_PGID == "$pid" && $PROC_SID == "$pid" ]]; then
      SELFTEST_STARTTIMES[$pid]=$PROC_STARTTICKS
      return 0
    fi
    sleep 0.01
    attempt=$((attempt + 1))
  done
  return 1
}

selftest_pid_is_current() {
  local pid=$1 expected=${SELFTEST_STARTTIMES[$1]:-}
  [[ $expected =~ ^[0-9]+$ ]] || return 1
  parse_proc_stat "/proc/$pid" || return 1
  [[ $PROC_PPID == "$SELF_PID" && $PROC_PGID == "$pid" &&
     $PROC_SID == "$pid" && $PROC_STARTTICKS == "$expected" ]]
}
cleanup_selftest() {
  exec 2>/dev/null
  local pid
  for pid in "${SELFTEST_PIDS[@]}"; do
    [[ $pid =~ ^[0-9]+$ ]] || continue
    # Signal only the recorded child if its PID, parent, session, group, and
    # starttime still identify the worker started by this selftest.
    if selftest_pid_is_current "$pid"; then
      kill -KILL -- "$pid" 2>/dev/null || true
    fi
  done
  for pid in "${SELFTEST_PIDS[@]}"; do
    [[ $pid =~ ^[0-9]+$ ]] || continue
    wait "$pid" 2>/dev/null || true
  done
  if [[ $SELFTEST_TMP == /var/tmp/souji-proc-st.* ]]; then
    rm -rf -- "$SELFTEST_TMP"
  fi
  if [[ $SELFTEST_CONTROL_TMP == /var/tmp/souji-proc-control.* ]]; then
    rm -rf -- "$SELFTEST_CONTROL_TMP"
  fi
  if [[ $SELFTEST_OUT == /var/tmp/souji-proc-out.* ]]; then
    rm -f -- "$SELFTEST_OUT"
  fi
  if [[ $SELFTEST_LITERAL_OUT == /var/tmp/souji-proc-out.* ]]; then
    rm -f -- "$SELFTEST_LITERAL_OUT"
  fi
}

run_selftest() {
  local script_dir self_path gone_path fd_path mixed_fifo argv_fifo control_fifo
  local literal_cwd literal_fd_dir literal_fd_path argv_arg boundary_arg secret_arg
  local auth_arg bearer_arg bearer_value aws_arg slack_arg split_token_arg split_token_secret
  local redaction_probe fake_stat_dir pid
  local -a fake_stat_fields=(
    S
    1 2 3 0 -1
    0 0 0 0 0 0 0 0 0
    20 0 1 0 12345
  )
  local reader_pid sleeper_pid argv_pid fd_pid literal_fd_pid control_pid mixed_pid argv_fd_pid
  local boot_line header row_pid row_starttime row_wchan row_reason row_cmd
  local reader_found=0 sleeper_found=0 argv_found=0 fd_found=0 mixed_found=0 mixed_rows=0
  local argv_fd_found=0 reader_wchan_found=0 control_found=0 literal_fd_found=0
  local secret_ok=0 redaction_unit_ok=0 stat_newline_ok=0 starttime_ok=0
  local narrow_reader_found=0 narrow_sleeper_found=0 narrow_mixed_found=0
  local narrow_argv_listed=0 narrow_fd_listed=0 narrow_argv_fd_listed=0
  local narrow_control_listed=0 narrow_literal_fd_listed=0

  command -v setsid >/dev/null 2>&1 || {
    printf 'souji-proc-census: selftest requires setsid\n' >&2
    exit 1
  }
  script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
  self_path=$script_dir/$(basename -- "${BASH_SOURCE[0]}")
  SELFTEST_TMP=$(mktemp -d /var/tmp/souji-proc-st.XXXXXX) || {
    printf 'souji-proc-census: selftest could not create /var/tmp fixture\n' >&2
    exit 1
  }
  trap cleanup_selftest EXIT
  trap 'exit 1' HUP INT TERM
  SELFTEST_CONTROL_TMP=$(mktemp -d /var/tmp/souji-proc-control.XXXXXX) || {
    printf 'souji-proc-census: selftest could not create control directory\n' >&2
    exit 1
  }
  SELFTEST_OUT=$(mktemp /var/tmp/souji-proc-out.XXXXXX) || {
    printf 'souji-proc-census: selftest could not create output file\n' >&2
    exit 1
  }
  SELFTEST_LITERAL_OUT=$(mktemp /var/tmp/souji-proc-out.XXXXXX) || {
    printf 'souji-proc-census: selftest could not create literal-name output file\n' >&2
    exit 1
  }

  literal_cwd=$SELFTEST_CONTROL_TMP/'x (deleted)'
  literal_fd_dir=$SELFTEST_CONTROL_TMP/fd-literal
  literal_fd_path=$literal_fd_dir/'x (deleted)'
  argv_fifo=$SELFTEST_CONTROL_TMP/argv-fifo
  control_fifo=$SELFTEST_CONTROL_TMP/control-fifo
  mkdir -p -- "$SELFTEST_TMP/d" "$literal_cwd" "$literal_fd_dir"
  gone_path=$SELFTEST_TMP/d/gone
  fd_path=$SELFTEST_TMP/d/open-file
  mixed_fifo=$SELFTEST_TMP/d/mixed-fifo
  : > "$fd_path"
  : > "$literal_fd_path"
  mkfifo -- "$SELFTEST_TMP/d/fifo" "$mixed_fifo" "$argv_fifo" "$control_fifo"
  fake_stat_dir=$SELFTEST_TMP/fakeproc
  mkdir -p -- "$fake_stat_dir"
  printf '987 (line\nbreak) %s\n' "${fake_stat_fields[*]}" > "$fake_stat_dir/stat"
  if parse_proc_stat "$fake_stat_dir" &&
     [[ $PROC_STATE == S && $PROC_PPID == 1 && $PROC_PGID == 2 &&
        $PROC_SID == 3 && $PROC_STARTTICKS == 12345 ]]; then
    stat_newline_ok=1
  fi
  argv_arg=--workspace=$gone_path
  boundary_arg=--workspace=/tmpfoo/souji-proc-boundary/gone
  secret_arg='--token=fixture-secret ghp_FAKE_TOKEN_PART sk-fakevalue password=fakepass https://user:pass@example.test/path'
  auth_arg='Authorization:'
  bearer_arg='Bearer'
  bearer_value='split-bearer-secret'
  aws_arg='AKIA1234567890123456'
  slack_arg='xoxb-test'
  split_token_arg='--ToKeN'
  split_token_secret='split-token-secret'
  redaction_probe='-H Authorization: Bearer b AKIA1234567890123456 xoxb-test --token=t --TOKEN=c ghp_FAKE_TOKEN_PART sk-fake password=x https://u:p@h'

  redact_command "$redaction_probe"
  if [[ $REDACTED_CMD == *'[REDACTED]'* &&
        $REDACTED_CMD != *'Bearer b'* && $REDACTED_CMD != *AKIA1234567890123456* &&
        $REDACTED_CMD != *xoxb-test* && $REDACTED_CMD != *'--token=t'* &&
        $REDACTED_CMD != *'--TOKEN=c'* && $REDACTED_CMD != *ghp_FAKE_TOKEN_PART* &&
        $REDACTED_CMD != *sk-fake* && $REDACTED_CMD != *password=x* &&
        $REDACTED_CMD != *u:p* ]]; then
    redaction_unit_ok=1
  fi

  setsid bash -c 'cd -- "$1" && exec cat < fifo' _ "$SELFTEST_TMP/d" >/dev/null 2>&1 &
  reader_pid=$!
  SELFTEST_PIDS+=("$reader_pid")
  remember_selftest_pid "$reader_pid" || { printf 'souji-proc-census: selftest could not record reader identity\n' >&2; exit 1; }

  setsid bash -c 'cd -- "$1" && exec sleep 300' _ "$SELFTEST_TMP/d" >/dev/null 2>&1 &
  sleeper_pid=$!
  SELFTEST_PIDS+=("$sleeper_pid")
  remember_selftest_pid "$sleeper_pid" || { printf 'souji-proc-census: selftest could not record sleeper identity\n' >&2; exit 1; }

  setsid bash -c 'cd -- "$1" && read -r _ < "$2"' _ \
    "$SELFTEST_CONTROL_TMP" "$argv_fifo" "$secret_arg" \
    -H "$auth_arg" "$bearer_arg" "$bearer_value" "$aws_arg" "$slack_arg" "$split_token_arg" "$split_token_secret" "$argv_arg" \
    >/dev/null 2>&1 &
  argv_pid=$!
  SELFTEST_PIDS+=("$argv_pid")
  remember_selftest_pid "$argv_pid" || { printf 'souji-proc-census: selftest could not record argv identity\n' >&2; exit 1; }

  setsid bash -c 'cd -- "$1" && exec sleep 300 < "$2"' _ "$SELFTEST_CONTROL_TMP" "$fd_path" >/dev/null 2>&1 &
  fd_pid=$!
  SELFTEST_PIDS+=("$fd_pid")
  remember_selftest_pid "$fd_pid" || { printf 'souji-proc-census: selftest could not record fd identity\n' >&2; exit 1; }

  setsid bash -c 'cd -- "$1" && exec sleep 300 < "$2"' _ "$SELFTEST_CONTROL_TMP" "$literal_fd_path" >/dev/null 2>&1 &
  literal_fd_pid=$!
  SELFTEST_PIDS+=("$literal_fd_pid")
  remember_selftest_pid "$literal_fd_pid" || { printf 'souji-proc-census: selftest could not record literal-fd identity\n' >&2; exit 1; }

  setsid bash -c 'cd -- "$1" && read -r _ < "$2"' _ "$literal_cwd" "$control_fifo" "$boundary_arg" >/dev/null 2>&1 &
  control_pid=$!
  SELFTEST_PIDS+=("$control_pid")
  remember_selftest_pid "$control_pid" || { printf 'souji-proc-census: selftest could not record control identity\n' >&2; exit 1; }

  setsid bash -c 'cd -- "$1" && exec 8< "$2" && read -r _ < "$3"' _ \
    "$SELFTEST_TMP/d" "$fd_path" "$mixed_fifo" "$argv_arg" >/dev/null 2>&1 &
  mixed_pid=$!
  SELFTEST_PIDS+=("$mixed_pid")
  remember_selftest_pid "$mixed_pid" || { printf 'souji-proc-census: selftest could not record mixed-reason identity\n' >&2; exit 1; }

  setsid bash -c 'cd -- "$1" && exec 8< "$2" && read -r _ < "$3"' _ \
    "$literal_cwd" "$fd_path" "$argv_fifo" "$argv_arg" >/dev/null 2>&1 &
  argv_fd_pid=$!
  SELFTEST_PIDS+=("$argv_fd_pid")
  remember_selftest_pid "$argv_fd_pid" || { printf 'souji-proc-census: selftest could not record argv-fd identity\n' >&2; exit 1; }

  sleep 0.2
  rm -rf -- "$SELFTEST_TMP"
  for pid in "${SELFTEST_PIDS[@]}"; do
    selftest_pid_is_current "$pid" || {
      printf 'souji-proc-census: selftest worker changed identity before census (pid %s)\n' "$pid" >&2
      exit 1
    }
  done

  if ! bash "$self_path" --prefix /var/tmp --min-age 0 > "$SELFTEST_OUT"; then
    printf 'souji-proc-census: selftest default-prefix census failed\n' >&2
    exit 1
  fi
  {
    IFS= read -r boot_line || boot_line=''
    IFS= read -r header || header=''
    if [[ $boot_line != '# boot_id '* || $header != "$HEADER" ]]; then
      printf 'souji-proc-census: selftest boot-id or output header mismatch\n' >&2
      exit 1
    fi

    while IFS=$'\t' read -r row_pid _ _ _ _ row_starttime _ row_wchan row_reason row_cmd; do
      case "$row_pid" in
        "$reader_pid")
          [[ $row_reason == cwd-deleted ]] && reader_found=1
          [[ $row_wchan != - ]] && reader_wchan_found=1
          [[ $row_starttime =~ ^[0-9]+$ ]] && starttime_ok=1
          ;;
        "$sleeper_pid")
          [[ $row_reason == cwd-deleted ]] && sleeper_found=1
          [[ $row_starttime =~ ^[0-9]+$ ]] && starttime_ok=1
          ;;
        "$argv_pid")
          [[ $row_reason == "argv-path-gone:$gone_path" ]] && argv_found=1
          if [[ $row_cmd == *'[REDACTED]'* &&
                $row_cmd != *fixture-secret* && $row_cmd != *ghp_FAKE_TOKEN_PART* &&
                $row_cmd != *sk-fakevalue* && $row_cmd != *fakepass* &&
                $row_cmd != *user:pass* && $row_cmd != *split-bearer-secret* &&
                $row_cmd != *AKIA1234567890123456* && $row_cmd != *xoxb-test* &&
                $row_cmd != *split-token-secret* ]]; then
            secret_ok=1
          fi
          ;;
        "$fd_pid")
          [[ $row_reason == "fd-path-gone:$fd_path" ]] && fd_found=1
          ;;
        "$mixed_pid")
          mixed_rows=$((mixed_rows + 1))
          [[ $row_reason == cwd-deleted ]] && mixed_found=1
          ;;
        "$argv_fd_pid")
          [[ $row_reason == argv-path-gone:* ]] && argv_fd_found=1
          ;;
        "$control_pid") control_found=1 ;;
        "$literal_fd_pid") literal_fd_found=1 ;;
      esac
    done
  } < "$SELFTEST_OUT"

  if ! bash "$self_path" --prefix "$literal_fd_dir" --min-age 0 > "$SELFTEST_LITERAL_OUT"; then
    printf 'souji-proc-census: selftest literal-prefix census failed\n' >&2
    exit 1
  fi
  {
    IFS= read -r boot_line || boot_line=''
    IFS= read -r header || header=''
    if [[ $boot_line != '# boot_id '* || $header != "$HEADER" ]]; then
      printf 'souji-proc-census: selftest literal-prefix header mismatch\n' >&2
      exit 1
    fi
    while IFS=$'\t' read -r row_pid _ _ _ _ _ _ _ row_reason _; do
      case "$row_pid" in
        "$reader_pid") [[ $row_reason == cwd-deleted ]] && narrow_reader_found=1 ;;
        "$sleeper_pid") [[ $row_reason == cwd-deleted ]] && narrow_sleeper_found=1 ;;
        "$mixed_pid") [[ $row_reason == cwd-deleted ]] && narrow_mixed_found=1 ;;
        "$argv_pid") narrow_argv_listed=1 ;;
        "$fd_pid") narrow_fd_listed=1 ;;
        "$argv_fd_pid") narrow_argv_fd_listed=1 ;;
        "$literal_fd_pid") narrow_literal_fd_listed=1 ;;
        "$control_pid") narrow_control_listed=1 ;;
      esac
    done
  } < "$SELFTEST_LITERAL_OUT"

  if ((reader_found == 0 || reader_wchan_found == 0 || sleeper_found == 0 ||
       argv_found == 0 || fd_found == 0 || mixed_found == 0 || mixed_rows != 1 ||
       argv_fd_found == 0 || control_found != 0 || literal_fd_found != 0 ||
       secret_ok == 0 || redaction_unit_ok == 0 || starttime_ok == 0 ||
       narrow_reader_found == 0 || narrow_sleeper_found == 0 || narrow_mixed_found == 0 ||
       narrow_argv_listed != 0 || narrow_fd_listed != 0 || narrow_argv_fd_listed != 0 ||
       narrow_literal_fd_listed != 0 || narrow_control_listed != 0 || stat_newline_ok == 0)); then
    printf 'souji-proc-census: selftest failed (cwd=%s wchan=%s sleep=%s argv=%s fd=%s mixed=%s mixed_rows=%s argv_fd=%s control=%s literal_fd=%s redaction=%s redaction_unit=%s stat_newline=%s starttime=%s narrow_cwds=%s%s%s narrow_other=%s%s%s%s%s)\n' \
      "$reader_found" "$reader_wchan_found" "$sleeper_found" "$argv_found" "$fd_found" "$mixed_found" "$mixed_rows" \
      "$argv_fd_found" "$control_found" "$literal_fd_found" "$secret_ok" "$redaction_unit_ok" "$stat_newline_ok" "$starttime_ok" \
      "$narrow_reader_found" "$narrow_sleeper_found" "$narrow_mixed_found" "$narrow_argv_listed" \
      "$narrow_fd_listed" "$narrow_argv_fd_listed" "$narrow_literal_fd_listed" "$narrow_control_listed" >&2
    exit 1
  fi
  printf 'souji-proc-census: selftest PASS (newline comm parser, live literal cwd/fd, age identity, all redactions, prefix boundary/scope, mixed precedence, isolated cleanup)\n'
}

# This branch performs no process enumeration, stat/status/boot-id/uptime read,
# or signal. It exercises the exact parser and formatter used by census().
if [[ -n $REASON_ONLY ]]; then
  if [[ $REASON_ONLY == argv ]]; then
    read_argv_stream
    [[ -n $PROC_GONE_PATH ]] || exit 3
    format_reason argv "$PROC_GONE_PATH" "$PROC_GONE_SECRET"
  else
    target=''
    IFS= read -r -d '' target || true
    target=${target%$'\n'}
    matched=0
    for prefix in "${PREFIXES[@]}"; do
      if top_level_scratch_gone "$target" "$prefix"; then
        matched=1
        break
      fi
    done
    ((matched)) || exit 3
    format_reason fd "$target"
  fi
  printf '%s\n' "$REDACTED_REASON"
  exit 0
fi

if ((SELFTEST)); then
  run_selftest
  exit 0
fi

census
