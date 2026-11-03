#!/bin/sh
# A Claude Code SessionStart hook (README.md says how to set it up): update
# this checkout of the skill, and print one line, which goes into the
# session's context, with the skill's version and the version the project in
# the current directory has applied, so that the Worker has nothing to run
# ("Keeping this skill current" in SKILL.md). Prints nothing in a directory
# without an issues directory, so other projects' sessions see nothing.
here=$(cd "$(dirname "$0")" && pwd)
if git -C "$here" pull --ff-only -q >/dev/null 2>&1
then updated="checkout updated"
else updated="checkout NOT updated (the pull failed: offline, or not a clone?)"
fi
skill=$(sed -n 's/^Version \([0-9][0-9.]*\)\..*/\1/p' "$here/SKILL.md" | head -1)
dir=${ISSUES_DIR:-issues}
project=$(sed -n 's/.*Workflow version:\*\* `\([0-9][0-9.]*\)`.*/\1/p' \
  "$dir/PROJECT.md" 2>/dev/null)
if [ -n "$project" ]
then echo "darais-issues-workflow: $updated; skill version $skill, this project's $project"
fi
