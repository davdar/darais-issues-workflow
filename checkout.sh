#!/bin/sh
# Brings the full checks' checkout of an issue, .worktrees/<issue>-checks in
# the repository of the current directory, to its branch (issue/<issue>) or
# to a given commit, creating it if it's missing ("Branches and worktrees"
# in SKILL.md). Run from the repository's main checkout:
#
#   sh <this checkout>/checkout.sh <issue> [<commit>]
#
# The checkout is a plain directory, not a git worktree: it has its own
# index, in .worktrees/<issue>-checks.index, and git's read-tree updates it,
# rewriting only the files that changed between the commits and removing
# the ones that went. So the build outputs there (which git ignores) are
# kept, and the next build is incremental. Nothing is written under .git,
# which Claude Code's sandbox mostly keeps read-only. Local edits in the
# checkout are discarded: it's only for building and testing.
set -eu
issue=${1:?usage: checkout.sh <issue> [<commit>]}
ref=${2:-issue/$issue}
repo=$(git rev-parse --show-toplevel)
gitdir=$(git rev-parse --absolute-git-dir)
dir="$repo/.worktrees/$issue-checks"
if ! git rev-parse --verify --quiet "$ref^{commit}" > /dev/null; then
  echo "no commit $ref: nothing checked out" >&2
  exit 1
fi
if [ -e "$dir/.git" ]; then
  echo "$dir is a git worktree or repository; remove it first (git worktree remove)" >&2
  exit 1
fi
mkdir -p "$dir"
GIT_INDEX_FILE="$dir.index" git --git-dir="$gitdir" --work-tree="$dir" read-tree --reset -u "$ref"
echo "$dir is at $(git --git-dir="$gitdir" rev-parse --short "$ref") ($ref)"
