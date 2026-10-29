#!/bin/bash
t=S; [ "$GIT_NO_REPLACE_OBJECTS" = 1 ] && t=T
{ printf '%s' "$t"; printf ' %q' "$@"; printf '\n'; } >> /fast/scratch/hyaku/souji-r42/R42w2executor02/c2/self.git
exec /usr/bin/git "$@"
