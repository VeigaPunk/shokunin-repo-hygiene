#!/usr/bin/env bash
# tests/fixtures/case-F3/make-fixture.sh — fixture F3 for tools/souji-verify.sh
#
# Builds the kotodama-shaped "repo-root" case (spec: "Fixture cases" F3 +
# "Artifact kinds" 1):
#   * a real git repo; HEAD -> refs/heads/master, 2 commits ahead of a
#     hand-written refs/remotes/origin/master (no remote, no fetch)
#   * refs/remotes/origin/HEAD -> refs/remotes/origin/master, and
#     branch.master.{remote,merge} set so @{u} resolves to origin/master
#   * 1 tracked file modified, unstaged; 0 staged, 0 untracked
# Expected verdict: NOT-SAFE, evidence mentioning unpushed=2 and dirty=1.
#
# Usage: make-fixture.sh [--force] [--json] [<outdir>]
#   (no <outdir>)  build under a fresh mktemp -d                     [default]
#   <outdir>       build the repo AT <outdir> (created if missing)
#   --json         stdout: one JSON object instead of the bare target path
#   --force        wipe <outdir> first; honoured only if <outdir> is
#                  missing, empty, or carries the .git/souji-fixture-F3
#                  marker written by an earlier run of this script
#   stdout: the absolute fixture repo root — pass it verbatim as the <path>
#           argument to tools/souji-verify.sh
#   stderr: deterministic key=value facts (shas, counts) for receipts
#   exit: 0 built + self-checked, 1 build/self-check error, 2 usage
#
# Deterministic: fixed identities, dates and content -> identical commit SHAs
# on every run. Hermetic: system/global git config disabled for this script.
# Plumbing only — never git fetch/push/commit/branch/checkout/reset/rebase.
set -euo pipefail

readonly FIX_MARKER=".git/souji-fixture-F3"
readonly FIX_NAME="souji-fixture"
readonly FIX_EMAIL="fixture@souji.invalid"
readonly D1="2026-01-01T00:00:00+0000"
readonly D2="2026-01-02T00:00:00+0000"
readonly D3="2026-01-03T00:00:00+0000"
readonly D4="2026-01-04T00:00:00+0000"

FIX_TARGET=""
FIX_BASE=""
FIX_C2=""
FIX_HEAD=""
FIX_LATEST_SHA=""

die() {
  printf 'make-fixture(F3): %s\n' "$*" >&2
  exit 1
}

usage() {
  cat >&2 <<'EOF'
usage: make-fixture.sh [--force] [--json] [<outdir>]
  (no <outdir>)  build the fixture under a fresh mktemp -d (default)
  <outdir>       build the fixture repo AT <outdir>
  --json         stdout: one JSON object {"case","target","unpushed",...}
  --force        wipe <outdir> when it is missing/empty or a previous
                 case-F3 build (.git/souji-fixture-F3 marker present)
  stdout         absolute fixture repo root (single line by default)
exit: 0 ok, 1 build/self-check error, 2 usage
EOF
  exit 2
}

json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  printf '%s' "$s"
}

build_fixture() {
  local repo="$1"
  export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
  export GIT_AUTHOR_NAME="$FIX_NAME" GIT_AUTHOR_EMAIL="$FIX_EMAIL"
  export GIT_COMMITTER_NAME="$FIX_NAME" GIT_COMMITTER_EMAIL="$FIX_EMAIL"
  local g=(git -C "$repo" -c commit.gpgsign=false)
  local sha tree porcelain count

  "${g[@]}" init -q -b master

  # Stamps every non-.git path in the worktree with a fixed date so the whole
  # fixture (content + mtimes) is reproducible. Run before `git add` so the
  # index records the fixed stat and the tree stays clean afterwards.
  stamp() {
    find "$repo" -name .git -prune -o -exec touch -h -d "$1" {} +
  }

  stage_commit() { # $1=message $2=parent ("" for root) $3=fixed date
    local msg="$1" parent="$2" date="$3"
    stamp "$date"
    "${g[@]}" add -A
    tree="$("${g[@]}" write-tree)"
    if [[ -n "$parent" ]]; then
      sha="$(GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" \
        "${g[@]}" commit-tree "$tree" -p "$parent" -m "$msg")"
    else
      sha="$(GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" \
        "${g[@]}" commit-tree "$tree" -m "$msg")"
    fi
    "${g[@]}" update-ref refs/heads/master "$sha"
    FIX_LATEST_SHA="$sha"
  }

  # --- c1: base, this is what the fake origin/master points at ---------------
  mkdir -p "$repo/corpus/notes"
  cat >"$repo/README.md" <<'EOF'
# fjord-harness (fixture lane)

Kotodama-shaped fixture: two unpushed commits over a stale origin/master and
one modified tracked file in the working tree.
EOF
  cat >"$repo/LOG.md" <<'EOF'
# LOG

## 2026-01-01 — mint

Fixture log for case F3.
EOF
  cat >"$repo/PROVINCE.md" <<'EOF'
# PROVINCE

- scope: fixture
- state: base
EOF
  cat >"$repo/corpus/notes/brief.md" <<'EOF'
Case F3 fixture note (base commit).
EOF
  stage_commit "c1 base (pushed)" "" "$D1"
  FIX_BASE="$FIX_LATEST_SHA"

  # --- c2: first unpushed commit -------------------------------------------
  cat >"$repo/README.md" <<'EOF'
# fjord-harness (fixture lane)

Kotodama-shaped fixture: two unpushed commits over a stale origin/master and
one modified tracked file in the working tree.

Status: round 22 in flight (unpushed).
EOF
  mkdir -p "$repo/plans"
  cat >"$repo/plans/round-22.md" <<'EOF'
# round 22 plan (unpushed)

- [ ] first unpushed change
EOF
  stage_commit "c2 round-22 scaffold" "$FIX_BASE" "$D2"
  FIX_C2="$FIX_LATEST_SHA"

  # --- c3: second unpushed commit ------------------------------------------
  cat >"$repo/LOG.md" <<'EOF'
# LOG

## 2026-01-01 — mint

Fixture log for case F3.

## 2026-01-03 — round 22

Second unpushed commit.
EOF
  stage_commit "c3 round-22 notes" "$FIX_C2" "$D3"
  FIX_HEAD="$FIX_LATEST_SHA"

  # --- fake origin: refs and config written by hand, no fetch ever ---------
  # remote.origin.* exists only so @{u} / branch.master.* resolve; the URL is
  # unreachable on purpose and nothing in this fixture contacts it.
  "${g[@]}" config remote.origin.url "example.invalid:fixture-lane.git"
  "${g[@]}" config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
  "${g[@]}" update-ref refs/remotes/origin/master "$FIX_BASE"
  "${g[@]}" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  "${g[@]}" config branch.master.remote origin
  "${g[@]}" config branch.master.merge refs/heads/master

  # --- dirty the tree: 1 tracked file modified, unstaged -------------------
  cat >"$repo/PROVINCE.md" <<'EOF'
# PROVINCE

- scope: fixture
- state: dirty working tree (unstaged modification, not part of c3)

Owner note: this line exists only so the modification changes the blob size,
which makes `git status` detect it regardless of stat/racy-index timing.
EOF
  touch -h -d "$D4" "$repo/PROVINCE.md"

  printf 'souji-fixture-F3\n' >"$repo/$FIX_MARKER"

  # --- self-check: the fixture is only useful if these hold exactly --------
  [[ -d "$repo/.git" ]] || die "no .git directory at $repo"
  [[ "$("${g[@]}" rev-parse --abbrev-ref HEAD)" == "master" ]] \
    || die "HEAD is not on master"
  [[ "$("${g[@]}" symbolic-ref refs/remotes/origin/HEAD)" == "refs/remotes/origin/master" ]] \
    || die "origin/HEAD misconfigured"
  [[ "$("${g[@]}" rev-parse --verify --quiet '@{u}')" == "$FIX_BASE" ]] \
    || die "upstream @{u} does not resolve to the fake origin/master base"

  count="$("${g[@]}" rev-list --count HEAD --not --remotes)" || die "unpushed count failed"
  [[ "$count" == "2" ]] || die "self-check: expected unpushed=2, got $count"
  count="$("${g[@]}" rev-list --count HEAD --not refs/remotes/origin/master)" \
    || die "origin-relative count failed"
  [[ "$count" == "2" ]] || die "self-check: expected HEAD-not-in-origin/master=2, got $count"

  porcelain="$("${g[@]}" status --porcelain)" || die "git status failed"
  if [[ -z "$porcelain" ]]; then count=0; else count="$(wc -l <<<"$porcelain" | tr -d ' ')"; fi
  [[ "$count" == "1" ]] || die "self-check: expected dirty=1 porcelain lines, got $count"
  [[ "$porcelain" == " M PROVINCE.md" ]] \
    || die "self-check: expected exactly ' M PROVINCE.md', got '$porcelain'"

  if [[ -z "$("${g[@]}" diff --cached --name-only)" ]]; then count=0; else
    count="$("${g[@]}" diff --cached --name-only | wc -l | tr -d ' ')"; fi
  [[ "$count" == "0" ]] || die "self-check: expected staged=0, got $count"

  if [[ -z "$("${g[@]}" ls-files --others --exclude-standard)" ]]; then count=0; else
    count="$("${g[@]}" ls-files --others --exclude-standard | wc -l | tr -d ' ')"; fi
  [[ "$count" == "0" ]] || die "self-check: expected untracked=0, got $count"

  printf '[case-F3] target=%s\n' "$repo" >&2
  printf '[case-F3] shas base=%s c2=%s head=%s\n' "$FIX_BASE" "$FIX_C2" "$FIX_HEAD" >&2
  printf '[case-F3] unpushed=%s dirty=1 staged=0 untracked=0 (expected verdict NOT-SAFE)\n' \
    "$("${g[@]}" rev-list --count HEAD --not --remotes)" >&2
}

main() {
  local force=0 json=0 outdir=""
  while (($#)); do
    case "$1" in
      --force) force=1 ;;
      --json) json=1 ;;
      -h | --help) usage ;;
      --) shift && { (($#)) && outdir="$1"; break; } ;;
      -*) printf 'make-fixture(F3): unknown flag: %s\n' "$1" >&2; usage ;;
      *) [[ -n "$outdir" ]] && die "single <outdir> argument expected"; outdir="$1" ;;
    esac
    shift
  done

  if [[ -z "$outdir" ]]; then
    outdir="$(mktemp -d "${TMPDIR:-/tmp}/souji-fixture-F3.XXXXXX")"
  elif [[ -e "$outdir" ]]; then
    if [[ -n "$(ls -A "$outdir" 2>/dev/null)" ]]; then
      if [[ "$force" == 1 && -f "$outdir/$FIX_MARKER" ]]; then
        rm -rf "$outdir"
        mkdir -p "$outdir"
      elif [[ "$force" == 1 ]]; then
        die "refusing --force: $outdir is non-empty and has no $FIX_MARKER marker"
      else
        die "refusing to overwrite non-empty $outdir (use --force for a previous case-F3 build)"
      fi
    fi
  else
    mkdir -p "$outdir"
  fi

  FIX_TARGET="$(cd "$outdir" && pwd -P)"
  build_fixture "$FIX_TARGET"

  if [[ "$json" == 1 ]]; then
    printf '{"case":"F3","schema":"souji-verify-fixture/1","target":"%s","kind":"repo-root","verdict":"NOT-SAFE","unpushed":2,"dirty":1,"staged":0,"untracked":0,"shas":{"base":"%s","c2":"%s","head":"%s"}}\n' \
      "$(json_escape "$FIX_TARGET")" "$FIX_BASE" "$FIX_C2" "$FIX_HEAD"
  else
    printf '%s\n' "$FIX_TARGET"
  fi
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
