# This project's settings for the Darais Issues Workflow

The workflow (`SKILL.md`, in the skill's checkout) refers to these by
name. Copy this file to the issues directory as `PROJECT.md` and fill it
in. Keep it to these settings: what the project adds to the workflow goes
in the issues directory's `README.md`.

- **The Reviewer's name:** `<the person who directs the work, such as Ada>`.
- **The Worker's name:** `<the agent doing the work, such as Claude>`, used
  in issues' section headings.
- **The issues directory:** `issues/`.
- **The skill's checkout:** `<path, such as submodules/darais-issues-workflow>`,
  a `<git submodule of the project | clone of its own, such as
  ~/p/darais-issues-workflow>`, kept current `<by a SessionStart hook
  running its update.sh | by the Worker, once per session>`, as
  `SKILL.md` says. `<.claude/skills/darais-issues-workflow
  is a symbolic link to it.>` Its `lock.py` is run as `python3
  <path>/lock.py`.
- **Workflow version:** `1.5.2`, the version of the skill whose changes
  this project has applied (the Worker updates it, as `SKILL.md` says).
- **The main branch:** `<main>`, pushed with `<git push origin main>`.
  <Push after every commit to it, or not.> <Who merges it into the release
  branch.>
- **Worktrees:** <as `SKILL.md` says: an issue has a branch but no worktree
  of its own; subagents work on it in temporary worktrees that Claude Code
  makes under `.claude/worktrees/`, and the full checks run in
  `.worktrees/<issue>-checks` (git ignores both folders) | one long-lived
  worktree per issue, in `<a folder git ignores>/<issue>`, where the Worker
  can commit in a worktree it made itself>.
- **The full checks:** <the build, the tests, and anything else that must
  pass before an issue closes>. Their steps are in `checks.sh`, beside
  this file, and are run with `sh <path>/full-checks.sh <issue>`.
- **Anything else the workflow needs to run here:** <sandbox rules for its
  commands, ...>, or nothing.
