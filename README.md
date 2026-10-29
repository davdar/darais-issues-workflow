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
- **The update needs the network:** exclude it from the sandbox in
  `sandbox.excludedCommands`, exactly as the Worker runs it, such as
  `"git submodule update --remote submodules/darais-issues-workflow"`, or
  `"git pull *"` for a clone (run from inside the clone: an exclusion may
  not match `git -C <dir> pull`).
- **A clone outside the project** (such as `~/p/darais-issues-workflow`,
  shared by every project) is outside what Claude Code lets a session
  reach, so in `~/.claude/settings.json`, for every project:

      "permissions": {
        "additionalDirectories": ["/Users/<you>/p/darais-issues-workflow"]
      },
      "sandbox": {
        "filesystem": {
          "allowRead": ["~/p/darais-issues-workflow"],
          "allowWrite": ["~/p/darais-issues-workflow"]
        }
      }

  `additionalDirectories` lets the Worker read the skill and work inside
  its checkout, `allowRead` lets a sandboxed `python3` run its `lock.py`,
  and `allowWrite` lets the Worker improve the skill and commit there.

**Trust:** the Worker follows what this repository says, in every project
that uses it, so only people you trust should be able to push to it.
