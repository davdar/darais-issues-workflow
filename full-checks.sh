#!/bin/sh
# Runs a project's full checks in an issue's checks checkout,
# .worktrees/<issue>-checks, which checkout.sh (beside this file) brings to
# the issue's branch first ("Branches and worktrees" in SKILL.md). Run from
# the repository's main checkout:
#
#   sh <this checkout>/full-checks.sh <issue>
#
# The steps are the project's: checks.sh in its issues directory (issues/,
# or the ISSUES_DIR environment variable, as for lock.py), read from the
# main checkout, with one line per step:
#
#   step <name> <directory> <command ...>
#
# which runs the command in that directory of the checks checkout ("." for
# its root). Each step's output goes to
# .worktrees/<issue>-checks.logs/<name>.log; a line per step says whether it
# passed, and the exit status is nonzero if any failed.
set -u
issue=${1:?usage: full-checks.sh <issue>}
here=$(cd "$(dirname "$0")" && pwd)
repo=$(git rev-parse --show-toplevel) || exit 1
steps="${ISSUES_DIR:-issues}/checks.sh"
if [ ! -f "$steps" ]; then
  echo "no $steps: the project's steps, one 'step <name> <directory> <command ...>' per line" >&2
  exit 1
fi
sh "$here/checkout.sh" "$issue" || exit 1
w="$repo/.worktrees/$issue-checks"
logs="$w.logs"
mkdir -p "$logs"
status=0
step() {
  name=$1; dir=$2; shift 2
  if (cd "$w/$dir" && "$@") > "$logs/$name.log" 2>&1; then
    echo "PASS $name"
  else
    echo "FAIL $name (see $logs/$name.log)"; status=1
  fi
}
echo "started $(date +%T)"
. "$steps"
echo "finished $(date +%T): overall $status"
exit $status
