#!/usr/bin/env bash
# tests/runner-25.sh — independent conformance runner for tools/souji-verify.sh
#
# Seat S25. Independent of the tool's own --selftest: every fixture is built
# from scratch here, in a mktemp -d tree, and every expectation is taken
# directly from tools/souji-verify.spec.md (F1..F10, CLI, exit codes, rails).
#
# Usage: tests/runner-25.sh [--tool PATH] [--json-out PATH] [--fixtures-only]
#                           [--keep] [--quiet] [--list-cases]
# Exit:  0 all cases pass; 1 case failure / tool missing / evaluation error;
#        2 usage error.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FLEET_ROOT="$(cd "$REPO_ROOT/.." && pwd)"
TOOL="$REPO_ROOT/tools/souji-verify.sh"
SPEC="$REPO_ROOT/tools/souji-verify.spec.md"
JSON_OUT="$REPO_ROOT/tests/results/runner-25.json"
MODE_FIXTURES_ONLY=0
KEEP=0
QUIET=0

while [ $# -gt 0 ]; do
  case "$1" in
    --tool)        TOOL="${2:?--tool needs a path}"; shift 2 ;;
    --json-out)    JSON_OUT="${2:?--json-out needs a path}"; shift 2 ;;
    --fixtures-only) MODE_FIXTURES_ONLY=1; shift ;;
    --keep)        KEEP=1; shift ;;
    --quiet)       QUIET=1; shift ;;
    --list-cases)  sed -n 's/^#CASE //p' "$0"; exit 0 ;;
    -h|--help)     sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)             printf 'usage: %s [--tool PATH] [--json-out PATH] [--fixtures-only] [--keep] [--quiet] [--list-cases]\n' "$0" >&2
                   exit 2 ;;
  esac
done

#CASE F1	file introduced pre-default-branch-tip, ancestor -> SAFE(pushed)
#CASE F2	file whose introducing commit is local-only -> NOT-SAFE(pushed-unverifiable|none)
#CASE F3	repo with unpushed commits + dirty tree -> NOT-SAFE + evidence unpushed=N dirty=M
#CASE F4	worktree registration, dir absent, unique=0 -> SAFE(metadata-prune)
#CASE F5	worktree registration, named branch, 1 unpushed commit -> NOT-SAFE(unpushed-branch)
#CASE F6a	ledger row, absolute source path -> SAFE(moved-to-obsidian)
#CASE F6b	ledger row, fleet-relative source path -> SAFE(moved-to-obsidian)
#CASE F6c	ledger row with source sha mismatch -> must NOT be SAFE(moved-to-obsidian)
#CASE F7	scratch file, no refs, old mtime -> SAFE(stale)
#CASE F7b	scratch file, fresh mtime, default --stale-days -> NOT-SAFE
#CASE F7c	old scratch file + --stale-days 99999 -> NOT-SAFE (flag honored)
#CASE F8	scratch file referenced only under souji-shokunin/census/ -> SAFE(stale) (D3)
#CASE F8d	scratch file with a live reference outside census -> NOT-SAFE (D3 is surgical)
#CASE F9a	origin/HEAD missing, single origin/main ref, no local master -> SAFE(pushed) (D1)
#CASE F9b	origin/HEAD missing, single origin/trunk ref -> SAFE(pushed) (D1)
#CASE F9c	no origin refs, no local master -> NOT-SAFE(pushed-unverifiable)
#CASE F10	target basename *.env -> NOT-SAFE(secrets-refusal)
#CASE F10b	target basename id_* -> NOT-SAFE(secrets-refusal)
#CASE F11	missing path -> NOT-SAFE(unreachable), exit 0
#CASE T-multi	one verdict line per target, exit 0, tab shape
#CASE T-usage-noargs	no arguments -> exit 2
#CASE T-usage-bogus	unknown flag -> exit 2
#CASE T-json	--json -> parseable JSON document, exit 0
#CASE T-selftest	tool --selftest -> exit 0, live corpus unchanged
#CASE T-git-rails	no forbidden git verb on PATH during evaluation (shim)
#CASE L1-kotodama	live kotodama-shokunin unpushed/dirty -> NOT-SAFE (r2 gate)
#CASE L2-gd2d-worktrees	live game-dev-2d named-branch worktrees -> NOT-SAFE(unpushed-branch)
#CASE L3-lore-worktree	live lore prunable worktree (dir absent, unique=0) -> SAFE(metadata-prune)

# ---------- scratch tree ----------
FIX="$(mktemp -d "${TMPDIR:-/tmp}/souji-r25.XXXXXXXX")"
case "$FIX" in /tmp/*) ;; *) echo "refusing: scratch not under /tmp ($FIX)" >&2; exit 1 ;; esac
# Harness bookkeeping lives outside $FIX: the tool's reference sweep must not
# see verdict lines / invariant commands that quote fixture basenames, or it
# would count the harness itself as a live reference. rg does not follow the
# results symlink (no --follow), so the fixture tree stays clean.
BOOK="$(mktemp -d "${TMPDIR:-/tmp}/souji-r25-book.XXXXXXXX")"
mkdir -p "$BOOK/results"
ln -sfn "$BOOK/results" "$FIX/results"
cleanup() {
  local rc=$?
  if [ "$KEEP" = 1 ]; then printf 'kept scratch: %s bookkeeping: %s\n' "$FIX" "$BOOK"
  else rm -rf "$FIX" "$BOOK"; fi
  exit $rc
}
trap cleanup EXIT

mkdir -p "$FIX"/{origins,vault,home,tmp,shim,lib}

cat >"$FIX/lib/parse.py" <<'PY'
import os, re, sys
target = sys.argv[1]
def norm(p):
    try: return os.path.realpath(p)
    except Exception: return p
nt = norm(target)
best = None
for raw in sys.stdin.read().splitlines():
    raw = re.sub(r'\x1b\[[0-9;]*m', '', raw)
    f = raw.split('\t')
    if len(f) < 2:
        continue
    if f[1].strip() == target or norm(f[1].strip()) == nt:
        best = f
        break
if best is None:
    print('')
    sys.exit(0)
fmt = ''
if best[0].strip() != 'VERDICT':
    fmt = 'format:first-field=' + best[0].strip()[:40]
verdict  = best[2].strip() if len(best) > 2 else ''
receipt  = best[3].strip() if len(best) > 3 else ''
evidence = '\t'.join(best[4:]).strip() if len(best) > 4 else ''
m = re.match(r'^(SAFE|NOT-SAFE)\s*\((.*)\)$', verdict)
if m:
    verdict = m.group(1)
    receipt = m.group(2)
    evidence = '\t'.join(best[3:]).strip() if len(best) > 3 else evidence
    fmt = (fmt + '; ' if fmt else '') + 'format:inline-parenthesized'
print('\t'.join([verdict, receipt, evidence, fmt]))
PY

cat >"$FIX/lib/emit.py" <<'PY'
import json, os, re, sys
cases_tsv, meta_tsv, inv_tsv, out_path, fix, repo = sys.argv[1:7]

def rows(path):
    out = []
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            for line in fh:
                line = line.rstrip('\n')
                if line:
                    out.append(line.split('\t'))
    except FileNotFoundError:
        pass
    return out

def clean(s):
    s = s.replace(fix, '<FIX>').replace(repo, '<REPO>')
    return re.sub(r'/tmp/([A-Za-z0-9._-]+)\.([A-Za-z0-9]{8})(?![A-Za-z0-9])', r'/tmp/\1.XXXXXXXX', s)

meta = {}
for r in rows(meta_tsv):
    if len(r) >= 2:
        meta[r[0]] = clean('\t'.join(r[1:]))

cases = []
for r in rows(cases_tsv):
    r = (r + ['', '', '', ''])[:5]
    cases.append({'id': r[0], 'status': r[1], 'expect': clean(r[2]),
                  'actual': clean(r[3]), 'detail': clean(r[4])})

inv = []
for r in rows(inv_tsv):
    r = (r + ['', ''])[:3]
    inv.append({'id': r[0], 'status': r[1], 'detail': clean(r[2])})

counts = {'total': len(cases),
          'pass': sum(1 for c in cases if c['status'] == 'pass'),
          'fail': sum(1 for c in cases if c['status'] == 'fail'),
          'skip': sum(1 for c in cases if c['status'] == 'skip')}

def split_meta(key):
    return [v for v in meta.get(key, '').split(',') if v]

def case_status(cid):
    for c in cases:
        if c['id'] == cid:
            return c['status']
    return 'absent'

result = 'tool-missing' if meta.get('tool_present') == '0' else ('fail' if counts['fail'] else 'pass')
doc = {
    'runner': 'tests/runner-25.sh',
    'seat': 'S25',
    'result': result,
    'counts': counts,
    'meta': meta,
    'fixture_invariants': inv,
    'safety': {
        'git_shim_calls': meta.get('git_shim_calls', '0'),
        'git_verbs_observed': split_meta('git_verbs_observed'),
        'mutating_verbs_observed': split_meta('mutating_verbs_observed'),
        'live_write_probe': meta.get('live_write_probe', 'none'),
        'selftest_live_corpus_unchanged': case_status('T-readonly-corpus'),
        'live_corpus_unchanged': case_status('T-readonly-live'),
        'note': 'git verbs observed through a PATH shim; absolute-path git invocations are not visible to it',
    },
    'cases': cases,
}
tmp = out_path + '.tmp'
with open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(doc, fh, indent=2, sort_keys=True)
    fh.write('\n')
os.replace(tmp, out_path)
PY

CASES_TSV="$FIX/results/cases.tsv"; : >"$CASES_TSV"
META_TSV="$FIX/results/meta.tsv";  : >"$META_TSV"
INV_TSV="$FIX/results/inv.tsv";    : >"$INV_TSV"
GIT_LOG="$FIX/results/git-calls.log"; : >"$GIT_LOG"
GIT_SHIM_LOG="$GIT_LOG"

# ---------- isolated git identity for every fixture + tool run ----------
cat >"$FIX/gitconfig" <<'CFG'
[user]
	name = souji fixture
	email = souji-fixture@local
[init]
	defaultBranch = master
[commit]
	gpgsign = false
[core]
	pager = cat
[advice]
	detachedHead = false
[protocol]
	allow = file
CFG
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_GLOBAL="$FIX/gitconfig"
export GIT_TERMINAL_PROMPT=0 GIT_PAGER=cat
export GIT_AUTHOR_DATE="2026-10-18T00:00:00+00:00"
export GIT_COMMITTER_DATE="2026-10-18T00:00:00+00:00"

# ---------- git PATH shim: logs verbs, refuses the spec-forbidden ones ----------
cat >"$FIX/shim/git" <<'SHIM'
#!/usr/bin/env bash
set -u
log="${GIT_SHIM_LOG:-/dev/null}"
verb=""
skip_next=0
for a in "$@"; do
  if [ "$skip_next" = 1 ]; then skip_next=0; continue; fi
  case "$a" in
    -C|-c) skip_next=1; continue ;;
    --git-dir=*|--work-tree=*|--exec-path=*|--namespace=*|-p|--paginate|--no-pager|--bare|--literal-pathspecs|--no-replace-objects) continue ;;
    -*) continue ;;
    *) verb="$a"; break ;;
  esac
done
printf '%s\t%s\n' "${verb:-<none>}" "$*" >>"$log" 2>/dev/null || true
case "$verb" in
  fetch|push|commit|branch|checkout|reset|rebase|clone|submodule)
    printf 'souji-r25 shim: refusing forbidden git verb %s\n' "$verb" >&2
    exit 128 ;;
esac
exec /usr/bin/git "$@"
SHIM
chmod +x "$FIX/shim/git"

# ---------- helpers ----------
san() { printf '%s' "$1" | tr '\t\n\r' '   ' | cut -c1-320; }
meta() { printf '%s\t%s\n' "$1" "$(san "$2")" >>"$META_TSV"; }
record() { # id status expect actual detail
  printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$(san "$3")" "$(san "$4")" "$(san "$5")" >>"$CASES_TSV"
  [ "$QUIET" = 1 ] || printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$(san "$3")" "$(san "$5")"
}
note() { [ "$QUIET" = 1 ] || printf '%s\n' "$*"; }
TOOL_RC=0
INVOKE_ROOT=""
INVOKE_CWD=""
RUN_TIMEOUT=60

invoke() { # invoke OUTFILE ARG...
  local out="$1"; shift
  set +e
  (
    cd "${INVOKE_CWD:-$FIX}" || exit 1
    exec timeout "$RUN_TIMEOUT" env \
      PATH="$FIX/shim:$PATH" GIT_SHIM_LOG="$GIT_SHIM_LOG" \
      HOME="$FIX/home" GIT_CONFIG_GLOBAL="$FIX/gitconfig" GIT_CONFIG_NOSYSTEM=1 \
      GIT_TERMINAL_PROMPT=0 TMPDIR="$FIX/tmp" \
      SHOKUNIN_ROOT="${INVOKE_ROOT:-$FIX}" SOUJI_ROOT="${INVOKE_ROOT:-$FIX}" \
      SOUJI_LEDGER="$FIX/souji-shokunin/corpus/knowledge/obsidian-ledger.tsv" \
      bash "$TOOL" "$@"
  ) >"$out" 2>"${out}.err"
  TOOL_RC=$?
  set -e
}

parse() { # parse TARGET < outfile -> verdict \t receipt \t evidence \t format-marker
  python3 "$FIX/lib/parse.py" "$1"
}

expect_verdict() { # id target outfile want rc receipts evidence_re detail
  local id="$1" target="$2" out="$3" want="$4" want_rc="$5" receipts="$6" ev_re="$7" detail="$8"
  local parsed v r e fmt rest actual ok=1 why=""
  parsed="$(parse "$target" <"$out")"
  v="${parsed%%$'\t'*}"; rest="${parsed#*$'\t'}"
  r="${rest%%$'\t'*}";   rest="${rest#*$'\t'}"
  e="${rest%%$'\t'*}";   fmt="${rest##*$'\t'}"
  actual="rc=$TOOL_RC verdict=${v:-<none>} receipt=${r:-<none>}"
  if [ "$TOOL_RC" != "$want_rc" ]; then ok=0; why="exit $TOOL_RC != $want_rc"; fi
  if [ -z "$v" ]; then ok=0; why="${why:+$why; }no verdict line for target"; fi
  if [ -n "$v" ] && [ "$v" != "$want" ]; then ok=0; why="${why:+$why; }verdict $v != $want"; fi
  if [ -n "$v" ] && [ "$receipts" != "*" ]; then
    case "|$receipts|" in *"|$r|"*) ;; *) ok=0; why="${why:+$why; }receipt '$r' not in {$receipts}" ;; esac
  fi
  if [ -n "$ev_re" ] && ! printf '%s' "$e" | grep -Eq "$ev_re"; then
    ok=0; why="${why:+$why; }evidence '$e' !~ /$ev_re/"
  fi
  if [ -n "$fmt" ]; then why="${why:+$why; }$fmt"; fi
  if [ "$ok" = 1 ]; then
    record "$id" pass "verdict=$want receipt=$receipts rc=$want_rc" "$actual" "$detail evidence=[$e]"
  else
    local tail_out=""
    tail_out="$(tail -c 300 "$out" 2>/dev/null || true)"
    record "$id" fail "verdict=$want receipt=$receipts rc=$want_rc ev~/$ev_re/" "$actual" \
      "$detail | $why | stdout-tail=[$(san "$tail_out")] stderr-tail=[$(san "$(tail -c 200 "${out}.err" 2>/dev/null || true)")]"
  fi
}

inv_check() { # id expectation cmd... -> record invariant
  local id="$1" want="$2"; shift 2
  local got
  set +e; got="$("$@" 2>&1)"; local rc=$?
  set -e
  if [ "$rc" = 0 ] && [ "$got" = "$want" ]; then
    printf '%s\tok\t%s\n' "$id" "$(san "$got")" >>"$INV_TSV"
  else
    printf '%s\tFAIL\trc=%s got=[%s] want=[%s] cmd=%s\n' "$id" "$rc" "$(san "$got")" "$(san "$want")" "$(san "$*")" >>"$INV_TSV"
    INV_FAILURES=$((INV_FAILURES + 1))
  fi
}
INV_FAILURES=0
fgit() { local r="$1"; shift; git -C "$r" "$@"; }
mkfile() { printf '%s\n' "$2" >"$1"; }
count_lines() { printf '%s' "$1" | grep -c . || true; }

meta seat S25
meta runner tests/runner-25.sh
meta repo_root "<REPO>"
meta tool_path "${TOOL#"$REPO_ROOT"/}"
meta spec_sha256 "$(sha256sum "$SPEC" | cut -d' ' -f1)"
meta bash_version "$BASH_VERSION"
meta fixed_date 2026-10-18T00:00:00+00:00
meta rg_basename_supported "$(rg --help 2>/dev/null | grep -c -- '--basename' || true)"

# ---------- fixtures ----------
make_origin() { # make_origin REPO BARE_PATH — mirror the repo's .git as its origin
  local repo="$1" bare="$2"
  rm -rf "$bare"
  cp -a "$repo/.git" "$bare"
  git -C "$bare" config core.bare true
  fgit "$repo" remote add origin "$bare"
}
set_remote_ref() { # set_remote_ref REPO BRANCH [origin-HEAD: yes|no]
  local repo="$1" branch="$2" set_head="${3:-yes}"
  fgit "$repo" update-ref "refs/remotes/origin/$branch" "refs/heads/$branch"
  if [ "$set_head" = yes ]; then
    fgit "$repo" symbolic-ref refs/remotes/origin/HEAD "refs/remotes/origin/$branch"
  fi
}

build_fixtures() {
  # --- alpha-shokunin: worktree owner (F4, F5) ---
  local A="$FIX/alpha-shokunin"
  mkdir -p "$A"; fgit "$A" init -q -b master
  mkfile "$A/README.md" "alpha"; fgit "$A" add README.md; fgit "$A" commit -qm base
  make_origin "$A" "$FIX/origins/alpha.git"
  set_remote_ref "$A" master
  # F5 first: named branch with one unpushed commit, dir present
  fgit "$A" worktree add -q -b wt-unpushed "$FIX/alpha-wt-unpushed" HEAD
  mkfile "$FIX/alpha-wt-unpushed/wt.txt" "wt"; fgit "$FIX/alpha-wt-unpushed" add wt.txt
  fgit "$FIX/alpha-wt-unpushed" commit -qm "wt commit"
  # F4: detached registration, then remove the directory
  fgit "$A" worktree add -q --detach "$FIX/alpha-wt-prunable" HEAD
  rm -rf "$FIX/alpha-wt-prunable"

  # --- beta-shokunin: repo-root, unpushed + dirty (F3) ---
  local B="$FIX/beta-shokunin"
  mkdir -p "$B"; fgit "$B" init -q -b master
  mkfile "$B/README.md" "beta"; mkfile "$B/tracked.txt" "one"
  fgit "$B" add README.md tracked.txt; fgit "$B" commit -qm base
  make_origin "$B" "$FIX/origins/beta.git"
  set_remote_ref "$B" master
  mkfile "$B/unpushed.txt" "u"; fgit "$B" add unpushed.txt; fgit "$B" commit -qm "unpushed work"
  mkfile "$B/tracked.txt" "dirty modification"

  # --- delta-shokunin: F1 pushed file ---
  local D="$FIX/delta-shokunin"
  mkdir -p "$D"; fgit "$D" init -q -b master
  mkfile "$D/README.md" "delta"; fgit "$D" add README.md; fgit "$D" commit -qm base
  mkdir -p "$D/notes"; mkfile "$D/notes/pushed-25.txt" "PUSHED25"
  fgit "$D" add notes/pushed-25.txt; fgit "$D" commit -qm "add pushed-25"
  mkfile "$D/README.md" "delta2"; fgit "$D" add README.md; fgit "$D" commit -qm tip
  make_origin "$D" "$FIX/origins/delta.git"
  set_remote_ref "$D" master

  # --- gamma-shokunin: F2 local-only commit ---
  local G="$FIX/gamma-shokunin"
  mkdir -p "$G"; fgit "$G" init -q -b master
  mkfile "$G/README.md" "gamma"; fgit "$G" add README.md; fgit "$G" commit -qm base
  make_origin "$G" "$FIX/origins/gamma.git"
  set_remote_ref "$G" master
  mkdir -p "$G/notes"; mkfile "$G/notes/local-only-25.txt" "LOCALONLY25"
  fgit "$G" add notes/local-only-25.txt; fgit "$G" commit -qm "local-only commit"

  # --- epsilon-shokunin: F6 ledger, F10 secrets ---
  local E="$FIX/epsilon-shokunin"
  mkdir -p "$E"; fgit "$E" init -q -b master
  mkfile "$E/README.md" "epsilon"
  mkfile "$E/.gitignore" $'notes/\nconfig/\nkeys/'
  fgit "$E" add README.md .gitignore; fgit "$E" commit -qm base
  make_origin "$E" "$FIX/origins/epsilon.git"
  set_remote_ref "$E" master
  mkdir -p "$E/notes" "$E/config" "$E/keys" "$FIX/vault"
  mkfile "$E/notes/export-me-25.md" "R25 EXPORT PAYLOAD ABS"
  mkfile "$E/notes/export-me-25b.md" "R25 EXPORT PAYLOAD REL"
  mkfile "$E/notes/export-me-25c.md" "R25 EXPORT PAYLOAD MISMATCH"
  mkfile "$E/config/app-f25.env" "PLACEHOLDER=not-a-secret"
  mkfile "$E/keys/id_fixture25_rsa" "PLACEHOLDER-NOT-A-KEY"
  cp "$E/notes/export-me-25.md"  "$FIX/vault/export-me-25.md"
  cp "$E/notes/export-me-25b.md" "$FIX/vault/export-me-25b.md"
  cp "$E/notes/export-me-25c.md" "$FIX/vault/export-me-25c.md"
  local L="$FIX/results/ledger.tsv"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' >"$L"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$E/notes/export-me-25.md"  "$(sha256sum "$E/notes/export-me-25.md"  | cut -d' ' -f1)" \
    "$FIX/vault/export-me-25.md"  "$(sha256sum "$FIX/vault/export-me-25.md"  | cut -d' ' -f1)" \
    "2026-10-18" "r25 fixture abs" >>"$L"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "epsilon-shokunin/notes/export-me-25b.md" "$(sha256sum "$E/notes/export-me-25b.md" | cut -d' ' -f1)" \
    "$FIX/vault/export-me-25b.md" "$(sha256sum "$FIX/vault/export-me-25b.md" | cut -d' ' -f1)" \
    "2026-10-18" "r25 fixture rel" >>"$L"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$E/notes/export-me-25c.md" "0000000000000000000000000000000000000000000000000000000000000000" \
    "$FIX/vault/export-me-25c.md" "$(sha256sum "$FIX/vault/export-me-25c.md" | cut -d' ' -f1)" \
    "2026-10-18" "r25 fixture mismatched source sha" >>"$L"
  mkdir -p "$FIX/corpus/knowledge" "$FIX/souji-shokunin/corpus/knowledge"
  cp "$L" "$FIX/corpus/knowledge/obsidian-ledger.tsv"
  cp "$L" "$FIX/souji-shokunin/corpus/knowledge/obsidian-ledger.tsv"

  # --- zeta-shokunin: F7/F7b/F7c/F8/F8d/F11 stale ---
  local Z="$FIX/zeta-shokunin"
  mkdir -p "$Z"; fgit "$Z" init -q -b master
  mkfile "$Z/README.md" "zeta"
  mkfile "$Z/.gitignore" ".scratch/"
  fgit "$Z" add README.md .gitignore; fgit "$Z" commit -qm base
  mkdir -p "$Z/.scratch" "$FIX/souji-shokunin/census"
  mkfile "$Z/.scratch/$P7"      "SCRATCH R25 PAYLOAD SEVEN"
  mkfile "$Z/.scratch/$P7fresh" "SCRATCH R25 PAYLOAD SEVEN FRESH"
  mkfile "$Z/.scratch/$P8"      "SCRATCH R25 PAYLOAD EIGHT"
  mkfile "$Z/.scratch/$P8d"     "SCRATCH R25 PAYLOAD EIGHT D"
  touch -d '3 days ago' "$Z/.scratch/$P7" "$Z/.scratch/$P8" "$Z/.scratch/$P8d"
  printf 'census reference row (D3 fixture): %s\n' "$P8" >"$FIX/souji-shokunin/census/notes-r25.txt"
  printf 'live reference outside census: %s\n' "$P8d" >>"$Z/README.md"
  fgit "$Z" add README.md; fgit "$Z" commit -qm "live reference"
  make_origin "$Z" "$FIX/origins/zeta.git"
  set_remote_ref "$Z" master

  # --- eta-shokunin: F9a single origin/main, no origin/HEAD, no local master ---
  local T="$FIX/eta-shokunin"
  mkdir -p "$T"; fgit "$T" init -q -b main
  mkfile "$T/README.md" "eta"; fgit "$T" add README.md; fgit "$T" commit -qm base
  mkdir -p "$T/notes"; mkfile "$T/notes/pushed-main-25.txt" "PUSHEDMAIN25"
  fgit "$T" add notes/pushed-main-25.txt; fgit "$T" commit -qm "add pushed-main-25"
  make_origin "$T" "$FIX/origins/eta.git"
  set_remote_ref "$T" main no

  # --- theta-shokunin: F9b single origin/trunk ---
  local H="$FIX/theta-shokunin"
  mkdir -p "$H"; fgit "$H" init -q -b trunk
  mkfile "$H/README.md" "theta"; fgit "$H" add README.md; fgit "$H" commit -qm base
  mkdir -p "$H/notes"; mkfile "$H/notes/pushed-trunk-25.txt" "PUSHEDTRUNK25"
  fgit "$H" add notes/pushed-trunk-25.txt; fgit "$H" commit -qm "add pushed-trunk-25"
  make_origin "$H" "$FIX/origins/theta.git"
  set_remote_ref "$H" trunk no

  # --- iota-shokunin: F9c no origin refs, no local master ---
  local I="$FIX/iota-shokunin"
  mkdir -p "$I"; fgit "$I" init -q -b main
  mkfile "$I/README.md" "iota"; fgit "$I" add README.md; fgit "$I" commit -qm base
  mkdir -p "$I/notes"; mkfile "$I/notes/unverifiable-25.txt" "UNVERIFIABLE25"
  fgit "$I" add notes/unverifiable-25.txt; fgit "$I" commit -qm "add unverifiable-25"
}

# payload names are assembled at runtime so this script never contains a
# literal copy of a fixture payload basename (which would count as a live
# reference if a sweep ever scanned this file).
P7="f7pay""25.out"; P7fresh="f7fresh""25.out"; P8="f8pay""25.out"; P8d="f8dpay""25.out"

build_fixtures

# ---------- fixture invariants ----------
inv_check INV-F1-ancestor ok bash -c \
  "git -C '$FIX/delta-shokunin' merge-base --is-ancestor \
     \"\$(git -C '$FIX/delta-shokunin' log --diff-filter=A --format=%H -1 -- notes/pushed-25.txt)\" \
     refs/remotes/origin/master && echo ok"
inv_check INV-F2-unpushed 1 bash -c \
  "git -C '$FIX/gamma-shokunin' log --oneline HEAD --not --remotes | wc -l | tr -d ' '"
inv_check INV-F3-unpushed 1 bash -c \
  "git -C '$FIX/beta-shokunin' log --oneline HEAD --not --remotes | wc -l | tr -d ' '"
inv_check INV-F4-dir-absent ok bash -c "[ ! -d '$FIX/alpha-wt-prunable' ] && echo ok"
inv_check INV-F4-registered ok bash -c \
  "git -C '$FIX/alpha-shokunin' worktree list --porcelain | grep -qxF 'worktree $FIX/alpha-wt-prunable' && echo ok"
inv_check INV-F5-unpushed-branch 1 bash -c \
  "git -C '$FIX/alpha-shokunin' log --oneline wt-unpushed --not --remotes | wc -l | tr -d ' '"
inv_check INV-F5-clean "" bash -c "git -C '$FIX/alpha-wt-unpushed' status --porcelain"
inv_check INV-F6-vault-sha-equal ok bash -c \
  "[ \"\$(sha256sum '$FIX/epsilon-shokunin/notes/export-me-25.md' | cut -d' ' -f1)\" = \"\$(sha256sum '$FIX/vault/export-me-25.md' | cut -d' ' -f1)\" ] && echo ok"
inv_check INV-F7-old-mtime ok bash -c "find '$FIX/zeta-shokunin/.scratch/$P7' -mtime +1 | grep -q . && echo ok"
inv_check INV-F7-no-refs 0 sh -c "rg -l --no-ignore --fixed-strings -- '$P7' '$FIX/zeta-shokunin' -g '!.git' 2>/dev/null | wc -l | tr -d ' '"
inv_check INV-F8-census-only-ref 1 bash -c \
  "rg -l --no-ignore --fixed-strings -- '$P8' '$FIX/souji-shokunin/census' 2>/dev/null | wc -l | tr -d ' '"
inv_check INV-F8d-live-ref 1 bash -c \
  "rg -l --no-ignore --fixed-strings -- '$P8d' '$FIX/zeta-shokunin' 2>/dev/null | wc -l | tr -d ' '"
inv_check INV-F9a-single-ref 1 bash -c \
  "git -C '$FIX/eta-shokunin' for-each-ref --format='%(refname)' refs/remotes/origin/ | wc -l | tr -d ' '"
inv_check INV-F9a-no-origin-head "" bash -c \
  "git -C '$FIX/eta-shokunin' symbolic-ref -q refs/remotes/origin/HEAD || true"
inv_check INV-F9b-ref-endpoint origin/trunk bash -c \
  "git -C '$FIX/theta-shokunin' for-each-ref --format='%(refname:short)' refs/remotes/origin/"
inv_check INV-F9c-no-remote-refs 0 bash -c \
  "git -C '$FIX/iota-shokunin' for-each-ref refs/remotes/origin/ | wc -l | tr -d ' '"

if [ "$INV_FAILURES" != 0 ]; then
  note "FIXTURE INVARIANTS FAILED: $INV_FAILURES"
  while IFS=$'\t' read -r i s d; do [ "$s" = ok ] || note "  $i: $d"; done <"$INV_TSV"
  meta fixture_invariants FAIL
  KEEP=1
  exit 1
fi
meta fixture_invariants ok

# ---------- preflight: the tool under test ----------
TOOL_PRESENT=0; TOOL_SHA=""; TOOL_PREFLIGHT="absent"
if [ -f "$TOOL" ]; then
  TOOL_PRESENT=1
  TOOL_SHA="$(sha256sum "$TOOL" | cut -d' ' -f1)"
  if bash -n "$TOOL" 2>"$FIX/results/syntax.err"; then
    TOOL_PREFLIGHT="syntax-ok executable=$([ -x "$TOOL" ] && echo yes || echo no) bytes=$(wc -c <"$TOOL" | tr -d ' ')"
  else
    TOOL_PREFLIGHT="syntax-error: $(san "$(cat "$FIX/results/syntax.err")")"
  fi
fi
meta tool_present "$TOOL_PRESENT"
meta tool_sha256 "$TOOL_SHA"
meta tool_preflight "$TOOL_PREFLIGHT"

if [ "$MODE_FIXTURES_ONLY" = 1 ]; then
  note "fixtures-only: invariants ok (tool_present=$TOOL_PRESENT preflight=$TOOL_PREFLIGHT)"
  exit 0
fi

if [ "$TOOL_PRESENT" = 0 ] || [ "$TOOL_PREFLIGHT" = "absent" ] || [ "${TOOL_PREFLIGHT#syntax-ok}" = "$TOOL_PREFLIGHT" ]; then
  meta result tool-missing-or-invalid
  record T0-tool-present fail "tool present and syntactically valid" "present=$TOOL_PRESENT preflight=$TOOL_PREFLIGHT" \
    "tools/souji-verify.sh not runnable yet; all fixture cases not executed"
  mkdir -p "$(dirname "$JSON_OUT")"
  python3 "$FIX/lib/emit.py" "$CASES_TSV" "$META_TSV" "$INV_TSV" "$JSON_OUT" "$FIX" "$REPO_ROOT" || true
  note "RESULT: tool missing or invalid — no verdicts evaluated"
  exit 1
fi
record T0-tool-present pass "tool present and syntactically valid" "$TOOL_PREFLIGHT" "sha256=$TOOL_SHA"

# ---------- live corpus fingerprint (read-only rail) ----------
corpus_fp() { find "$REPO_ROOT/corpus" -type f -print0 2>/dev/null | sort -z | xargs -0 sha256sum 2>/dev/null | sha256sum | cut -d' ' -f1; }
CORPUS_BEFORE="$(corpus_fp)"

# ---------- fixture cases ----------
note "== fixture cases (scratch=$FIX) =="
INVOKE_ROOT="$FIX"; RUN_TIMEOUT=60

O="$FIX/results/f1.out";   invoke "$O" "$FIX/delta-shokunin/notes/pushed-25.txt"
expect_verdict F1 "$FIX/delta-shokunin/notes/pushed-25.txt" "$O" SAFE 0 pushed "" "introducing commit is ancestor of origin/master (F1)"

O="$FIX/results/f2.out";   invoke "$O" "$FIX/gamma-shokunin/notes/local-only-25.txt"
expect_verdict F2 "$FIX/gamma-shokunin/notes/local-only-25.txt" "$O" NOT-SAFE 0 "pushed-unverifiable|none" "" "introducing commit is local-only (F2)"

O="$FIX/results/f3.out";   invoke "$O" "$FIX/beta-shokunin"
expect_verdict F3 "$FIX/beta-shokunin" "$O" NOT-SAFE 0 "*" 'unpushed=[1-9][0-9]* dirty=[1-9][0-9]*' "repo-root: 1 unpushed commit + dirty tracked file (F3)"

O="$FIX/results/f4.out";   invoke "$O" "$FIX/alpha-wt-prunable"
expect_verdict F4 "$FIX/alpha-wt-prunable" "$O" SAFE 0 "metadata-prune" "" "worktree registration, dir absent, unique=0 (F4/D2)"

O="$FIX/results/f5.out";   invoke "$O" "$FIX/alpha-wt-unpushed"
expect_verdict F5 "$FIX/alpha-wt-unpushed" "$O" NOT-SAFE 0 "unpushed-branch" "" "worktree registration, named branch 1 unpushed commit (F5)"

O="$FIX/results/f6a.out";  invoke "$O" "$FIX/epsilon-shokunin/notes/export-me-25.md"
expect_verdict F6a "$FIX/epsilon-shokunin/notes/export-me-25.md" "$O" SAFE 0 "moved-to-obsidian" "" "ledger row with absolute source path + matching sha256 both sides (F6)"

O="$FIX/results/f6b.out";  invoke "$O" "$FIX/epsilon-shokunin/notes/export-me-25b.md"
expect_verdict F6b "$FIX/epsilon-shokunin/notes/export-me-25b.md" "$O" SAFE 0 "moved-to-obsidian" "" "ledger row with fleet-relative source path + matching sha256 both sides (F6)"

O="$FIX/results/f6c.out";  invoke "$O" "$FIX/epsilon-shokunin/notes/export-me-25c.md"
expect_verdict F6c "$FIX/epsilon-shokunin/notes/export-me-25c.md" "$O" NOT-SAFE 0 "*" "" "ledger source sha mismatch: no receipt may apply (F6 negative control)"

O="$FIX/results/f7.out";   invoke "$O" "$FIX/zeta-shokunin/.scratch/$P7"
expect_verdict F7 "$FIX/zeta-shokunin/.scratch/$P7" "$O" SAFE 0 "stale" "" "scratch type, zero live references, mtime 3d old (F7)"

O="$FIX/results/f7b.out";  invoke "$O" "$FIX/zeta-shokunin/.scratch/$P7fresh"
expect_verdict F7b "$FIX/zeta-shokunin/.scratch/$P7fresh" "$O" NOT-SAFE 0 "*" "" "fresh scratch file: not older than 1 day (default --stale-days)"

O="$FIX/results/f7c.out";  invoke "$O" --stale-days 99999 "$FIX/zeta-shokunin/.scratch/$P7"
expect_verdict F7c "$FIX/zeta-shokunin/.scratch/$P7" "$O" NOT-SAFE 0 "*" "" "same 3d-old file with --stale-days 99999: threshold flag honored"

O="$FIX/results/f8.out";   invoke "$O" "$FIX/zeta-shokunin/.scratch/$P8"
expect_verdict F8 "$FIX/zeta-shokunin/.scratch/$P8" "$O" SAFE 0 "stale" "" "only reference lives under souji-shokunin/census/ -> excluded (F8/D3)"

O="$FIX/results/f8d.out";  invoke "$O" "$FIX/zeta-shokunin/.scratch/$P8d"
expect_verdict F8d "$FIX/zeta-shokunin/.scratch/$P8d" "$O" NOT-SAFE 0 "*" "" "live reference outside census/ -> NOT-SAFE (D3 exclusion is surgical)"

O="$FIX/results/f9a.out";  invoke "$O" "$FIX/eta-shokunin/notes/pushed-main-25.txt"
expect_verdict F9a "$FIX/eta-shokunin/notes/pushed-main-25.txt" "$O" SAFE 0 "pushed" "" "origin/HEAD missing, single origin/main ref, no local master (F9/D1)"

O="$FIX/results/f9b.out";  invoke "$O" "$FIX/theta-shokunin/notes/pushed-trunk-25.txt"
expect_verdict F9b "$FIX/theta-shokunin/notes/pushed-trunk-25.txt" "$O" SAFE 0 "pushed" "" "origin/HEAD missing, single origin/trunk ref (F9/D1)"

O="$FIX/results/f9c.out";  invoke "$O" "$FIX/iota-shokunin/notes/unverifiable-25.txt"
expect_verdict F9c "$FIX/iota-shokunin/notes/unverifiable-25.txt" "$O" NOT-SAFE 0 "pushed-unverifiable" "" "no origin refs and no local master: default branch unresolvable"

O="$FIX/results/f10.out";  invoke "$O" "$FIX/epsilon-shokunin/config/app-f25.env"
expect_verdict F10 "$FIX/epsilon-shokunin/config/app-f25.env" "$O" NOT-SAFE 0 "secrets-refusal" "" "basename *.env -> secrets refusal (F10)"

O="$FIX/results/f10b.out"; invoke "$O" "$FIX/epsilon-shokunin/keys/id_fixture25_rsa"
expect_verdict F10b "$FIX/epsilon-shokunin/keys/id_fixture25_rsa" "$O" NOT-SAFE 0 "secrets-refusal" "" "basename id_* -> secrets refusal"

O="$FIX/results/f11.out";  invoke "$O" "$FIX/zeta-shokunin/does-not-exist-25.txt"
expect_verdict F11 "$FIX/zeta-shokunin/does-not-exist-25.txt" "$O" NOT-SAFE 0 "unreachable" "" "missing target -> unreachable, exit stays 0"

# --- CLI shape cases ---
O="$FIX/results/tmulti.out"; invoke "$O" "$FIX/delta-shokunin/notes/pushed-25.txt" \
  "$FIX/epsilon-shokunin/config/app-f25.env" "$FIX/zeta-shokunin/does-not-exist-25.txt"
multi_lines="$(grep -c '^VERDICT' "$O" 2>/dev/null || true)"
multi_fields="$(awk -F'\t' '/^VERDICT/{print NF}' "$O" | sort -u | tr '\n' ',')"
if [ "$TOOL_RC" = 0 ] && [ "$multi_lines" = 3 ] && [ "$multi_fields" = "5," ]; then
  record T-multi pass "3 targets -> 3 VERDICT lines, 5 fields, rc=0" "lines=$multi_lines fields=$multi_fields rc=$TOOL_RC" ""
else
  record T-multi fail "3 targets -> 3 VERDICT lines, 5 fields, rc=0" "lines=$multi_lines fields=$multi_fields rc=$TOOL_RC" \
    "note: fields set counts tab-separated fields on each VERDICT line"
fi

set +e; timeout 30 env PATH="$FIX/shim:$PATH" GIT_SHIM_LOG="$GIT_SHIM_LOG" HOME="$FIX/home" \
  bash "$TOOL" >"$FIX/results/usage1.out" 2>&1; rc1=$?
timeout 30 env PATH="$FIX/shim:$PATH" GIT_SHIM_LOG="$GIT_SHIM_LOG" HOME="$FIX/home" \
  bash "$TOOL" --bogus-flag-25 >"$FIX/results/usage2.out" 2>&1; rc2=$?
timeout 30 env PATH="$FIX/shim:$PATH" GIT_SHIM_LOG="$GIT_SHIM_LOG" HOME="$FIX/home" \
  bash "$TOOL" -h >"$FIX/results/usage3.out" 2>&1; rc3=$?
set -e
if [ "$rc1" = 2 ]; then record T-usage-noargs pass "exit 2" "exit $rc1" ""
else record T-usage-noargs fail "exit 2" "exit $rc1" "output=[$(san "$(cat "$FIX/results/usage1.out")")]"; fi
if [ "$rc2" = 2 ]; then record T-usage-bogus pass "exit 2" "exit $rc2" ""
else record T-usage-bogus fail "exit 2" "exit $rc2" "output=[$(san "$(cat "$FIX/results/usage2.out")")]"; fi
meta usage_help_exit "$rc3"

O="$FIX/results/tjson.out"; invoke "$O" --json "$FIX/delta-shokunin/notes/pushed-25.txt" "$FIX/epsilon-shokunin/config/app-f25.env"
json_shape="$(python3 - "$O" 2>"$FIX/results/json.err" <<'PY'
import json, sys
path = sys.argv[1]
lines = [l for l in open(path, encoding='utf-8', errors='replace').read().splitlines() if l.strip()]
shapes = []
for line in lines:
    try:
        obj = json.loads(line)
        shapes.append('object' if isinstance(obj, dict) else type(obj).__name__)
    except Exception:
        shapes.append('invalid')
try:
    json.loads(open(path, encoding='utf-8', errors='replace').read())
    whole = True
except Exception:
    whole = False
if not lines:
    print('empty')
elif all(s == 'object' for s in shapes) and len(lines) == 2:
    print('single-doc' if whole else 'jsonl')
elif all(s == 'object' for s in shapes):
    print('jsonl-count-%d' % len(lines))
else:
    print('invalid')
PY
)"
case "$json_shape" in
  jsonl|single-doc)
    record T-json pass "--json emits 2 parseable JSON objects (jsonl or single doc), rc=0" \
      "rc=$TOOL_RC shape=$json_shape" "sample=[$(san "$(head -c 200 "$O")")]" ;;
  *)
    record T-json fail "--json emits 2 parseable JSON objects (jsonl or single doc), rc=0" \
      "rc=$TOOL_RC shape=$json_shape" \
      "err=[$(san "$(cat "$FIX/results/json.err")")] sample=[$(san "$(head -c 200 "$O")")]" ;;
esac
meta json_shape "$json_shape"

# ---------- tool self-test + rails ----------
INVOKE_ROOT="$FLEET_ROOT"; RUN_TIMEOUT=240
LOG_MARK_SELFTEST="$(wc -l <"$GIT_LOG" | tr -d ' ')"
O="$FIX/results/selftest.out"; invoke "$O" --selftest
CORPUS_MID="$(corpus_fp)"
if [ "$TOOL_RC" = 0 ]; then
  record T-selftest pass "--selftest exit 0" "exit 0 corpus-unchanged=$([ "$CORPUS_BEFORE" = "$CORPUS_MID" ] && echo yes || echo no)" \
    "tail=[$(san "$(tail -c 200 "$O")")]"
else
  record T-selftest fail "--selftest exit 0" "exit $TOOL_RC" \
    "tail=[$(san "$(tail -c 300 "$O")")] err=[$(san "$(tail -c 200 "${O}.err")")]"
fi
if [ "$CORPUS_BEFORE" != "$CORPUS_MID" ]; then
  record T-readonly-corpus fail "corpus fingerprint unchanged after --selftest" "changed" "live corpus must be read-only"
else
  record T-readonly-corpus pass "corpus fingerprint unchanged after --selftest" "unchanged" ""
fi

eval_log="$GIT_LOG"
if [ "${LOG_MARK_SELFTEST:-0}" -gt 0 ] 2>/dev/null; then
  head -n "$LOG_MARK_SELFTEST" "$GIT_LOG" >"$FIX/results/git-calls-eval.log"
  tail -n "+$((LOG_MARK_SELFTEST + 1))" "$GIT_LOG" >"$FIX/results/git-calls-selftest.log"
  eval_log="$FIX/results/git-calls-eval.log"
else
  : >"$FIX/results/git-calls-selftest.log"
  cp "$GIT_LOG" "$eval_log"
fi
selftest_log="$FIX/results/git-calls-selftest.log"
forbidden_seen="$(cat "$eval_log" "$selftest_log" | cut -f1 | sort -u | grep -Ex 'fetch|push|commit|branch|checkout|reset|rebase|clone|submodule' || true)"
mutating_seen="$(cut -f1 "$eval_log" | sort -u | grep -Ex 'worktree|update-ref|config|hash-object|gc|repack|prune|reflog|rm|mv|apply|stash|tag|am|cherry-pick|revert|add|restore|clean|switch|filter-repo' || true)"
mutating_selftest="$(cut -f1 "$selftest_log" | sort -u | grep -Ex 'worktree|update-ref|config|hash-object|gc|repack|prune|reflog|rm|mv|apply|stash|tag|am|cherry-pick|revert|add|restore|clean|switch|filter-repo' || true)"
grep_real="$(cut -f1 "$eval_log" | grep -c . || true)"
meta git_shim_calls "$grep_real"
meta git_shim_calls_selftest "$(cut -f1 "$selftest_log" | grep -c . || true)"
meta git_verbs_observed "$(cut -f1 "$eval_log" | sort -u | tr '\n' ',' || true)"
meta git_verbs_selftest "$(cut -f1 "$selftest_log" | sort -u | tr '\n' ',' || true)"
if [ -n "$forbidden_seen" ]; then
  record T-git-rails fail "no forbidden git verb (fetch/push/commit/branch/checkout/reset/rebase)" \
    "forbidden: $(printf '%s' "$forbidden_seen" | tr '\n' ',')" "shim refuses these verbs; PATH-based invocations only"
else
  record T-git-rails pass "no forbidden git verb observed on PATH" "clean over $grep_real evaluation git calls" \
    "note: shim intercepts PATH-based git only; selftest-phase verbs reported separately"
fi
meta mutating_verbs_observed "$(printf '%s' "$mutating_seen" | tr '\n' ',')"
meta mutating_verbs_selftest "$(printf '%s' "$mutating_selftest" | tr '\n' ',')"

LIVE_WRITES="$(find "$REPO_ROOT" -newermt "$(date -d '-1 minute' '+%Y-%m-%d %H:%M:%S')" -type f \
  -not -path "$REPO_ROOT/.git/*" -not -path "$REPO_ROOT/tools/*" -not -path "$REPO_ROOT/tests/*" \
  -not -name LOG.md -not -name SCORECARD.md 2>/dev/null | sed "s|$REPO_ROOT/||" | tr '\n' ',' || true)"
meta live_write_probe "${LIVE_WRITES:-none}"
CORPUS_AFTER="$(corpus_fp)"
if [ "$CORPUS_BEFORE" != "$CORPUS_AFTER" ]; then
  record T-readonly-live fail "live corpus unchanged across the whole run" "changed" "corpus/** was modified during evaluation"
else
  record T-readonly-live pass "live corpus unchanged across the whole run" "unchanged" ""
fi

# ---------- live fleet cases (dynamic ground truth) ----------
note "== live fleet cases =="
kot="/home/vgpnk/Projects/shokunin/kotodama-shokunin"
if [ -d "$kot/.git" ]; then
  run_tmp="$(fgit "$kot" log --oneline HEAD --not --remotes 2>/dev/null | wc -l | tr -d ' ')"
  drt_tmp="$(fgit "$kot" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  O="$FIX/results/l1.out"; invoke "$O" "$kot"
  if [ "$run_tmp" -gt 0 ] || [ "$drt_tmp" -gt 0 ]; then
    expect_verdict L1-kotodama "$kot" "$O" NOT-SAFE 0 "*" 'unpushed=[0-9]+ dirty=[0-9]+' \
      "live: unpushed=$run_tmp dirty=$drt_tmp re-derived at run time (r2 gate)"
  else
    record L1-kotodama skip "live kotodama unpushed/dirty -> NOT-SAFE" "live tree clean now (unpushed=$run_tmp dirty=$drt_tmp)" "gate is conditional on live state"
  fi
else
  record L1-kotodama skip "live kotodama unpushed/dirty -> NOT-SAFE" "kotodama-shokunin absent" ""
fi

gd2d="/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"
if [ -d "$gd2d/.git" ]; then
  gd_any=0
  while IFS= read -r wpath; do
    branch="$(fgit "$gd2d" worktree list --porcelain |
      awk -v p="$wpath" 'BEGIN{RS="";FS="\n"} $1=="worktree "p {for(i=1;i<=NF;i++) if ($i ~ /^branch /) print $i}' | sed 's|^branch refs/heads/||')"
    case "$branch" in wt-r98|wt-r99|wt-r100) ;; *) continue ;; esac
    un="$(fgit "$gd2d" log --oneline "$branch" --not --remotes 2>/dev/null | wc -l | tr -d ' ')"
    [ "$un" -gt 0 ] || continue
    gd_any=1
    O="$FIX/results/l2-$(basename "$wpath").out"; invoke "$O" "$wpath"
    expect_verdict "L2-$(basename "$wpath")" "$wpath" "$O" NOT-SAFE 0 "unpushed-branch" "" \
      "live gd2d worktree on $branch with $un unpushed commit(s)"
  done < <(fgit "$gd2d" worktree list --porcelain | awk '$1=="worktree"{print $2}')
  [ "$gd_any" = 1 ] || record L2-gd2d-worktrees skip "live gd2d named-branch worktrees -> NOT-SAFE(unpushed-branch)" \
    "no wt-r98/99/100 branch still unpushed" "fleet may have pushed since round 1"
else
  record L2-gd2d-worktrees skip "live gd2d named-branch worktrees" "game-dev-2d-shokunin absent" ""
fi

lore="/home/vgpnk/Projects/shokunin/lore-shokunin"
if [ -d "$lore/.git" ]; then
  l3_done=0
  while IFS= read -r wpath; do
    [ -n "$wpath" ] || continue
    [ -d "$wpath" ] && continue
    whead="$(fgit "$lore" worktree list --porcelain | awk -v p="$wpath" '
      BEGIN { RS=""; FS="\n" }
      { for (i = 1; i <= NF; i++) { if ($i == "worktree " p) hit = 1; if (hit && $i ~ /^HEAD /) { print substr($i, 6); exit } } }')"
    [ -n "$whead" ] || continue
    uniq="$(fgit "$lore" log --oneline "$whead" --not --all 2>/dev/null | wc -l | tr -d ' ')"
    [ "$uniq" = 0 ] || continue
    l3_done=1
    O="$FIX/results/l3.out"; invoke "$O" "$wpath"
    expect_verdict L3-lore-worktree "$wpath" "$O" SAFE 0 "metadata-prune" "" \
      "live lore worktree registration, dir absent, unique commits=$uniq"
    break
  done < <(fgit "$lore" worktree list --porcelain | awk '$1=="worktree"{print $2}')
  [ "$l3_done" = 1 ] || record L3-lore-worktree skip "live lore prunable worktree -> SAFE(metadata-prune)" \
    "no absent-dir unique=0 registration found" "fleet may have pruned since round 1"
else
  record L3-lore-worktree skip "live lore prunable worktree" "lore-shokunin absent" ""
fi

# ---------- emit ----------
mkdir -p "$(dirname "$JSON_OUT")"
python3 "$FIX/lib/emit.py" "$CASES_TSV" "$META_TSV" "$INV_TSV" "$JSON_OUT" "$FIX" "$REPO_ROOT"
tot=0; pass=0; fail=0; skip=0
while IFS=$'\t' read -r id st rest; do
  tot=$((tot + 1))
  case "$st" in pass) pass=$((pass + 1));; fail) fail=$((fail + 1));; skip) skip=$((skip + 1));; esac
done <"$CASES_TSV"
note "== summary: $pass pass / $fail fail / $skip skip of $tot =="
note "json: $JSON_OUT"
[ "$fail" = 0 ] && exit 0
exit 1
