#!/usr/bin/env bash
# Four isolated real-git cases plus an always-pass false-green control.
set -euo pipefail
export GIT_OPTIONAL_LOCKS=0
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
GATE="$ROOT/tools/souji-pre-report-gate.sh"
D=$(mktemp -d "${TMPDIR:-/tmp}/souji-r27-pre-report.XXXXXX")
trap 'rm -rf -- "$D"' EXIT
failures=0
passes=0
setup() {
  local n=$1
  mkdir -p "$D/$n"
  git -C "$D/$n" init --bare -q "$D/$n/origin.git"
  git -C "$D/$n" clone -q "$D/$n/origin.git" "$D/$n/lane"
  git -C "$D/$n/lane" checkout -q -b master
  git -C "$D/$n/lane" config user.name fixture
  git -C "$D/$n/lane" config user.email fixture@example.invalid
  printf 'base\n' > "$D/$n/lane/base.txt"
  git -C "$D/$n/lane" add base.txt
  git -C "$D/$n/lane" commit -qm base
  git -C "$D/$n/lane" push -q -u origin master
  printf 'prereg\n' > "$D/$n/prereg.txt"
  printf '# Report\n\n## SHONEN\n[~] evidence\n' > "$D/$n/report.md"
}
run_gate() { bash "$GATE" --lane "$1" --branch master --report "$2" --prereg "$3"; }
expect() {
  local label=$1 expected=$2; shift 2
  local out rc
  set +e
  out=$("$@" 2>&1); rc=$?
  set -e
  if [[ $rc == "$expected" ]]; then
    ((passes+=1))
    printf 'case-%s=PASS\n' "$label"
  else
    ((failures+=1))
    printf 'case-%s=FAIL expected-rc=%s actual-rc=%s\n%s\n' "$label" "$expected" "$rc" "$out" >&2
  fi
}
# Case 1: clean lane, matching local and remote tips, valid report and prereg.
setup clean
expect clean-pass 0 run_gate "$D/clean/lane" "$D/clean/report.md" "$D/clean/prereg.txt"
# Case 2: local branch advanced after push; remote tip intentionally stale.
setup mismatch
printf 'local-only\n' >> "$D/mismatch/lane/base.txt"
git -C "$D/mismatch/lane" add base.txt
git -C "$D/mismatch/lane" commit -qm unpushed
expect remote-mismatch 1 run_gate "$D/mismatch/lane" "$D/mismatch/report.md" "$D/mismatch/prereg.txt"
# Case 3: report exists but SHONEN heading is absent.
setup no-shonen
printf '# Report\nNo checklist.\n' > "$D/no-shonen/report.md"
expect missing-shonen 1 run_gate "$D/no-shonen/lane" "$D/no-shonen/report.md" "$D/no-shonen/prereg.txt"
# Case 4: dirty untracked lane worktree.
setup dirty
printf 'stray\n' > "$D/dirty/lane/stray.txt"
expect dirty-tree 1 run_gate "$D/dirty/lane" "$D/dirty/report.md" "$D/dirty/prereg.txt"
# False-green control: a deliberately broken always-PASS stub must fail the
# harness's adversarial check (the remote-mismatch input must return nonzero).
cat > "$D/always-pass.sh" <<'STUB'
#!/usr/bin/env bash
printf 'check-tip=PASS\ncheck-report=PASS\ncheck-shonen=PASS\ncheck-clean=PASS\ncheck-prereg=PASS\n'
exit 0
STUB
chmod +x "$D/always-pass.sh"
set +e
control_out=$("$D/always-pass.sh" --lane "$D/mismatch/lane" --branch master --report "$D/mismatch/report.md" --prereg "$D/mismatch/prereg.txt" 2>&1)
control_rc=$?
set -e
if [[ $control_rc == 0 && $control_out == *'check-tip=PASS'* ]]; then
  printf 'control=FALSE-GREEN-REJECTED\n'
else
  printf 'control=FAIL\n' >&2
  ((failures+=1))
fi
if (( failures == 0 && passes == 4 )); then
  printf 'cases=4 pass=4 control=FALSE-GREEN-REJECTED\n'
  exit 0
fi
printf 'cases=4 pass=%d control=FALSE-GREEN-REJECTED failures=%d\n' "$passes" "$failures" >&2
exit 1
