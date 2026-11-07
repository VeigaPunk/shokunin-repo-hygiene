#!/usr/bin/env bash
# souji r79 probe: a process started as an asynchronous command of a non-interactive shell (job control off)
# begins with SIGINT ignored (S325: "asynchronous commands ignore SIGINT and SIGQUIT"), the disposition is
# inherited across exec, and bash cannot trap a signal ignored on entry. This is why the A run of the C1 counter
# (launched with `&` from a script) scored row s4 (INT) as a mismatch for every gate, including the R1 repair.
# Prints one line per arm; exit 0 iff both arms show the expected disposition.
set -u
fg=$(bash -c 'trap "echo trapped" INT; trap -p INT')
bg=$(bash -c 'bash -c '\''trap "echo trapped" INT; trap -p INT'\'' & wait')
pyfg=$(python3 -c 'import signal; print(signal.getsignal(signal.SIGINT) is signal.SIG_IGN)')
pybg=$(bash -c 'python3 -c "import signal; print(signal.getsignal(signal.SIGINT) is signal.SIG_IGN)" & wait')
printf 'ARM foreground-bash trap=%s\n' "$fg"
printf 'ARM background-bash trap=%s\n' "$bg"
printf 'ARM foreground-python sigint_ignored=%s\n' "$pyfg"
printf 'ARM background-python sigint_ignored=%s\n' "$pybg"
[[ $fg == *"echo trapped"* && $bg == "trap -- '' SIGINT" && $pyfg == False && $pybg == True ]]
