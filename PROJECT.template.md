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
  ~/p/darais-issues-workflow>`, updated at the start of every round as
  `SKILL.md` says. `<.claude/skills/darais-issues-workflow
  is a symbolic link to it.>` Its `lock.py` is run as `python3
  <path>/lock.py`.
- **Workflow version:** `1.1.0`, the version of the skill whose changes
  this project has applied (the Worker updates it, as `SKILL.md` says).
- **The main branch:** `<main>`, pushed with `<git push origin main>`.
  <Push after every commit to it, or not.> <Who merges it into the release
  branch.>
- **Worktrees** go in `<a folder git ignores, such as .worktrees/<issue>>`.
- **The full checks:** <the build, the tests, and anything else that must
  pass before an issue closes>.
- **Anything else the workflow needs to run here:** <sandbox rules for its
  commands, ...>, or nothing.
