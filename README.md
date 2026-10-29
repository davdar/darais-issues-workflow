# The Darais Issues Workflow

A Claude Code skill.

A Reviewer (usually a person) and a Worker (usually Claude) work through a
project's tasks asynchronously, through markdown files in the repository:
one per issue, each the whole conversation about it, each worked on in its
own branch and worktree. `SKILL.md` is the workflow itself, which Claude
reads; this file is for people setting it up.

| File                  | What it is                                                          |
|-----------------------|---------------------------------------------------------------------|
| `SKILL.md`            | the workflow, with the skill's front matter (`name`, `description`) |
| `lock.py`             | takes and releases issues, so several Workers don't collide         |
| `PROJECT.template.md` | the settings each project fills in, as its `issues/PROJECT.md`      |
| `CHANGELOG.md`        | what changed between versions, and how to migrate                   |

## Using it in a project

1. **Check it out,** either way:
   - **As a submodule** (pins the version per project, in the project's
     history):

         git submodule add -b main <url> submodules/darais-issues-workflow

     `-b main` makes `git submodule update --remote` follow `main`. A fresh
     clone of the project then needs `git submodule update --init`.
   - **As a clone of its own,** outside the project or in a folder git
     ignores:

         git clone <url> ~/skills/darais-issues-workflow

2. **Let Claude Code find it:** a skill is a folder in `.claude/skills/`
   (the project's) or `~/.claude/skills/` (all of yours). It can be a
   symbolic link to the checkout, which Claude Code follows:

       ln -s ../../submodules/darais-issues-workflow .claude/skills/darais-issues-workflow

   Use a relative link for a submodule, so that it works in every clone.
   You can also check the skill out directly into `.claude/skills/`, but
   see "Sandboxes" below.
3. **Create the issues directory:** `issues/PROJECT.md` (from
   `PROJECT.template.md`), `issues/TODO.md` with its status block,
   `issues/open/` and `issues/closed/` (with a `.gitkeep` each), and ignore
   `issues/locks/` in `.gitignore`.
4. **Point the project's `CLAUDE.md` at it,** in a line such as "Work is
   tracked in `issues/` with the Darais Issues Workflow skill; read its
   `SKILL.md` and `issues/PROJECT.md` before working on an issue."

## Updating

At the start of every round the Worker updates the checkout (`git
submodule update --remote <checkout>` for a submodule, `git pull
--ff-only` inside the checkout for a clone). Each project records the
version it has applied (`Workflow version:` in its `PROJECT.md`), so a
clone shared by every project can be updated in one project's round and
still applied in each of the others at theirs: when `SKILL.md`'s version
is newer than the project's, the Worker reads `CHANGELOG.md` and applies
it. To publish an improvement, commit it here
with a new version in `SKILL.md` and an entry in `CHANGELOG.md`; each
project picks it up at its next round.

## Sandboxes and permissions

Claude Code's sandbox and permissions may stop the Worker from updating
the skill (network access), from running its `lock.py`, or from writing
under `.claude/skills/` (protected by default).

- **Keep the checkout outside `.claude/skills/`,** with a symbolic link
  there (step 2 above).
- **Some of the workflow's git commands can't run in the sandbox:** it
  can't reach SSH remotes or the SSH agent (`git pull`, `git push`,
  `git fetch`), and `git worktree` and `git branch -d` write under `.git/`
  where it doesn't allow them. Exclude them from the sandbox, and allow
  them, since an excluded command runs outside the sandbox, where
  `autoAllowBashIfSandboxed` doesn't approve it. In `~/.claude/settings.json`:

      "permissions": {
        "allow": [
          "Bash(git branch -d *)", "Bash(git fetch *)", "Bash(git ls-remote *)",
          "Bash(git pull *)", "Bash(git push *)", "Bash(git worktree *)"
        ],
        "deny": [
          "Bash(git push -f*)", "Bash(git push * -f*)", "Bash(git push *--force*)",
          "Bash(git * push -f*)", "Bash(git * push * -f*)", "Bash(git * push *--force*)"
        ]
      },
      "sandbox": {
        "excludedCommands": [
          "git branch -d *", "git fetch *", "git ls-remote *",
          "git pull *", "git push *", "git worktree *"
        ]
      }

  The deny rules keep force pushes out, whichever way they're written. For
  a submodule checkout, also exclude and allow the update exactly as the
  Worker runs it, such as
  `"git submodule update --remote submodules/darais-issues-workflow"`.
- **An exclusion matches only a plain command that is the whole call.**
  `git -C <dir> pull`, `cd <dir> && git pull`, a pipe or a chain all stay
  sandboxed, and fail. So the Worker `cd`s into a repository as a command
  of its own, then runs the git command as another.
- **A clone outside the project** (such as `~/p/darais-issues-workflow`,
  shared by every project) is outside what Claude Code lets a session
  reach, so in `~/.claude/settings.json`, for every project:

      "permissions": {
        "additionalDirectories": ["~/p/darais-issues-workflow"]
      }

  That makes it a working directory in every session: readable and
  writable by Claude's file tools and by sandboxed commands, so the Worker
  can read the skill, run its `lock.py` with `python3`, and improve the
  skill and commit there, with no `sandbox.filesystem` entries.

**Trust:** the Worker follows what this repository says, in every project
that uses it, so only people you trust should be able to push to it.
