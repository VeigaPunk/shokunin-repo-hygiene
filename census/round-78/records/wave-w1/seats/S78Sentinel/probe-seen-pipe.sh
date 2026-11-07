#!/bin/bash
# LOW-2: gitsrc_seen is a "|"-joined string with no escaping, so a path containing "|"
# aliases a path that was never scanned.  /x/a and /x/b are true members; the third is not.
gitsrc_seen="|/x/a|/x/b"
for p in /x/a /x/b "/x/a|/x/b" /x/c; do
  case "|$gitsrc_seen|" in
    *"|$p|"*) [[ $p == /x/a || $p == /x/b ]] && echo "SKIPPED (true member): $p" || echo "SKIPPED (FALSE ALIAS, never scanned): $p" ;;
    *) echo "scanned: $p" ;;
  esac
done
