#!/usr/bin/env bash
# souji-wave-evidence-capture.sh
#
# Capture a round's .ufo/waves evidence into a committable census receipt.
#
#   bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify]
#
# Copies <lane>/.ufo/waves/round-<N>/ (byte-exact file contents) into
# <lane>/census/round-<N>/waves/ together with:
#   manifest.sha256 - sha256 of every captured regular file (paths as listed
#                     by `find . -type f | LC_ALL=C sort` inside the receipt),
#                     excluding manifest.sha256 itself; summary.tsv is
#                     included in the manifest.
#   summary.tsv     - header only (no results file present) or one TSV row
#                     per seat row from each <*-results.json> found in the
#                     source (name, agent, id, status, final_output_available).
#
# The receipt is then re-verified: the manifest is recomputed over the copy and
# compared byte-for-byte to the stored manifest, and the file-hash set is
# compared against the source tree. Exit 0 means captured+verified. With
# --verify, only the verification step runs against an existing receipt.
#
# Source access is read-only; no git/jj mutation; never network.
#
# Exit codes:
#   0 captured + verified
#   1 usage error
#   2 source directory missing
#   3 refusal: special file / path escape / nested src-dst
#   4 verification failed (manifest mismatch or source mismatch)
#   5 copy / receipt write failure
set -u
set -o pipefail
export LC_ALL=C

usage() {
  printf '%s\n' \
    'Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify]' \
    '  <lane-abs> absolute path to the lane repo root' \
    '  <round-N>  integer round number' \
    '  --verify   only re-verify an existing receipt (no copy)'
}

if [[ $# -lt 2 || $# -gt 3 ]]; then usage >&2; exit 1; fi
lane=$1
round=$2
verify_only=0
if [[ $# -eq 3 ]]; then
  [[ $3 == --verify ]] || { usage >&2; exit 1; }
  verify_only=1
fi

case $round in
  ''|*[!0-9]*) usage >&2; exit 1 ;;
esac
if [[ $lane != /* ]]; then printf '%s\n' 'error: lane must be absolute' >&2; exit 1; fi
case /$lane in
  */../*|*/..) printf '%s\n' 'error: lane must not contain .. segments' >&2; exit 1 ;;
esac

src="$lane/.ufo/waves/round-$round"
dst="$lane/census/round-$round/waves"

if [[ $verify_only -eq 0 ]]; then
  if [[ ! -d $src ]]; then
    printf 'error: source directory not found: %s\n' "$src" >&2
    exit 2
  fi
  if [[ -L $src ]]; then printf '%s\n' 'error: source is a symlink' >&2; exit 3; fi

  # Refusal scan: special files (fifo/socket/device/other non-regular,
  # non-directory, non-symlink entries) are refused outright; path
  # components must not contain `..`. Symlink entries are copied verbatim
  # (never dereferenced) and, like the frozen recipe's `find -type f`, are
  # not part of the manifest hash set.
  bad=0
  while IFS= read -r -d '' p; do
    rel=${p#"$src"/}
    case /$rel in
      */../*|*/..) bad=1 ;;
    esac
    if [[ ! -f $p && ! -d $p && ! -L $p ]]; then bad=1; fi
    (( bad )) && break
  done < <(find "$src" -mindepth 1 -print0)
  if (( bad )); then
    printf '%s\n' 'error: refused special file / escaping path in source' >&2
    exit 3
  fi

  case "$dst" in
    "$src"/*|"$src") printf '%s\n' 'error: destination nested in source' >&2; exit 3 ;;
  esac
  case "$src" in
    "$dst"/*) printf '%s\n' 'error: source nested in destination' >&2; exit 3 ;;
  esac

  # Fresh receipt (the destination is an artifact this tool owns).
  rm -rf -- "$dst" || { printf '%s\n' 'error: cannot clear prior receipt' >&2; exit 5; }
  mkdir -p -- "$dst" || { printf '%s\n' 'error: cannot create receipt directory' >&2; exit 5; }
  if ! cp -a -- "$src/." "$dst/"; then
    printf '%s\n' 'error: copy failed' >&2
    exit 5
  fi

  # summary.tsv (best-effort; manifest still guards the receipt bytes).
  if ! python3 -B - "$src" "$dst/summary.tsv" <<'PY'
import json, os, sys, ast
src, out = sys.argv[1], sys.argv[2]
rows = ["name\tagent\tid\tstatus\tfinal_output_available"]
try:
    names = sorted(n for n in os.listdir(src) if n.endswith("-results.json"))
except OSError:
    names = []
for n in names:
    try:
        with open(os.path.join(src, n), encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        print("warning: cannot parse %s: %s" % (n, exc), file=sys.stderr)
        continue
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        continue
    for e in results:
        if not isinstance(e, dict):
            continue
        name = e.get("name", "")
        agent = e.get("agent", "")
        eid = e.get("id", "")
        raw = e.get("output")
        avail = 0 if raw in (None, "", [], {}) else 1
        status = ""
        if avail:
            try:
                dd = ast.literal_eval(raw) if isinstance(raw, str) else None
                txt = dd.get("text", "") if isinstance(dd, dict) else ""
                inner = json.loads(txt) if isinstance(txt, str) and txt.strip() else {}
                status = str(inner.get("status", "")) if isinstance(inner, dict) else ""
            except Exception:
                status = ""
        rows.append("\t".join((str(name), str(agent), str(eid), status, str(avail))))
try:
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(rows) + "\n")
except Exception as exc:
    print("error: cannot write summary: %s" % exc, file=sys.stderr)
    sys.exit(1)
PY
  then
    printf '%s\n' 'error: summary.tsv write failed' >&2
    exit 5
  fi

  # manifest.sha256: hashes of every regular file in the receipt except itself.
  (
    cd "$dst" || exit 5
    mapfile -d '' files < <(find . -type f ! -name manifest.sha256 -print0 | LC_ALL=C sort -z)
    if (( ${#files[@]} )); then
      printf '%s\0' "${files[@]}" | xargs -0 sha256sum > manifest.sha256
    else
      : > manifest.sha256
    fi
  ) || exit 5
fi

# ---- verification (always runs; also the --verify mode) ----
if [[ ! -f "$dst/manifest.sha256" ]]; then
  printf '%s\n' 'error: manifest.sha256 missing in receipt' >&2
  exit 4
fi
verify_ok=1
(
  cd "$dst" || exit 1
  mapfile -d '' files < <(find . -type f ! -name manifest.sha256 -print0 | LC_ALL=C sort -z)
  if (( ${#files[@]} )); then
    printf '%s\0' "${files[@]}" | xargs -0 sha256sum | cmp -s - manifest.sha256 || exit 1
  else
    [[ -s manifest.sha256 ]] && exit 1
  fi
) || verify_ok=0

if [[ $verify_only -eq 0 ]]; then
  # Source-vs-receipt hash-set identity (values only, path-normalized).
  src_hashes=$(cd "$src" && {
    mapfile -d '' sf < <(find . -type f -print0 | LC_ALL=C sort -z)
    if (( ${#sf[@]} )); then printf '%s\0' "${sf[@]}" | xargs -0 sha256sum; fi
  } | awk '{print $1}' | LC_ALL=C sort)
  dst_hashes=$(cd "$dst" && {
    mapfile -d '' df < <(find . -type f ! -name manifest.sha256 ! -name summary.tsv -print0 | LC_ALL=C sort -z)
    if (( ${#df[@]} )); then printf '%s\0' "${df[@]}" | xargs -0 sha256sum; fi
  } | awk '{print $1}' | LC_ALL=C sort)
  if [[ $src_hashes != "$dst_hashes" ]]; then
    printf '%s\n' 'error: source and receipt file sets differ' >&2
    verify_ok=0
  fi
fi

if [[ $verify_ok -eq 0 ]]; then
  printf '%s\n' 'error: verification failed' >&2
  exit 4
fi
printf 'captured+verified: %s -> %s\n' "$src" "$dst"
exit 0
