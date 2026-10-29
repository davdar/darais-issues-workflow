---
name:
  darais-issues-workflow
description:
  Work through a project's tasks asynchronously through issue files in the
  repository, between a Reviewer (who directs and decides) and a Worker (who
  does the work, on its own branch per issue). Use when asked to "make progress
  on issues", to work on, file, split or close an issue, or to look at TODO.md
  or the issues directory.
---

# The Darais Issues Workflow

Version 1.0.1. `CHANGELOG.md`, beside this file, lists what changed
between versions.

A way for two parties to work through a project's tasks asynchronously,
through files in the repository. Each task is an *issue*, a markdown file
that holds the whole conversation about it: the Reviewer answers in the
files when it suits them, and the Worker works on whatever is ready for
it, each issue on its own branch.

## Roles

- **The Reviewer** is who directs the work and decides: typically the human
  doing project management for the project, directing an AI agent. They
  write requests in `TODO.md`, answer questions in issues, and say when an
  issue may be closed.
- **The Worker** is who does the work: typically an AI agent, such as
  Claude. It turns requests into issues, analyzes and implements them,
  asks the Reviewer whatever needs their decision, and reports what it did
  with evidence.

Design decisions are the Reviewer's: the Worker raises them as questions,
with a recommendation, rather than deciding them itself.

`PROJECT.md` gives each role's name in the project, such as "David" and
"Claude". This file says "the Reviewer" and "the Worker" throughout; in an
issue's text, the Worker uses the names.

## The project's settings

Each project has a `PROJECT.md` in its issues directory, with its own
settings, which this file refers to by name (`PROJECT.template.md`, beside
this file, is a template):

- the *Reviewer's name* and the *Worker's name*;
- the *issues directory* (usually `issues/`);
- the *skill's checkout*: where this skill is, and whether it's a git
  submodule of the project or a clone of its own;
- the *workflow version*: the version of this skill whose changes the
  project has applied, as `Workflow version: 1.0.0`;
- the *main branch*, and how to push it;
- where *worktrees* go;
- the *full checks*, which must pass before an issue closes;
- anything else particular to the project, such as how to run commands
  in its sandbox.

## Keeping this skill current

This skill lives in its own git repository, and at the start of every
round the Worker updates its checkout, so that improvements made in one
project reach every project that uses it. How depends on the checkout:

- **A submodule of the project:** from the project's root,

      git submodule update --remote <checkout>

  which moves it to the latest commit of the branch it tracks (set when it
  was added, with `git submodule add -b <branch>`). A submodule is checked
  out at a commit, not on a branch, so `git pull` inside it doesn't work.
  If the checkout moved, the Worker commits it on the main branch
  (`git add <checkout>`), with any changes the update calls for (below).
- **A clone of its own** (outside the project, such as one in the home
  directory that every project shares, or in a folder git ignores):
  `cd <checkout>` as a command of its own, then, as another,

      git pull --ff-only

  then `cd` back to the project. (Not `git -C <checkout> pull`, nor
  `cd <checkout> && git pull`: a sandbox's exclusion matches only a plain
  command that is the whole call, so either form stays sandboxed and can't
  reach the remote.) There's nothing to commit in the project, beyond the
  changes below.

Then the Worker compares the version at the top of this file with the
project's *workflow version*. It doesn't compare with what the checkout
was before the update: a shared clone may have been updated in another
project's round, whose changes this project hasn't applied yet. If this
file's version is newer, the Worker re-reads this file, reads
`CHANGELOG.md` from the project's version to this one, applies what it
says to the project (a new status, a renamed file, a migration of the
issues directory), sets the project's workflow version to this one,
commits that on the main branch, and tells the Reviewer what changed. A
new major version means the issues directory needs migrating, and the
changelog says how: the Worker shows the Reviewer the migration, in an
issue, before applying it.

## Files

In the issues directory:

- `PROJECT.md`: the project's settings.
- `TODO.md`: new requests from the Reviewer, not yet issues.
- `open/<issue>.md`: an open issue, named in kebab case (`check-speed`).
- `closed/<issue>.md`: a closed one.
- `locks/`: the locks held, one file each (ignored by git).
- `mocks/<issue>/`, ...: files an issue needs, such as mock outputs for
  others to review.

## An issue

An issue is **append only**: the Worker adds plans, analyses, questions,
progress and results at the end, each in a section headed with the
Worker's name, the date and time, and what it is:

    ## Claude, 2026-10-29 14:05: the plan

The Reviewer answers in the response block that the Worker leaves at the
end whenever it has something to ask or report:

    ---------------------------------------------
    REVIEWER RESPONSE

    ---------------------------------------------

At the top of every open issue is its status block:

    [ ] Ready for Worker
    [ ] Ready for Reviewer
    [ ] Blocked for Worker
    [ ] Blocked for Reviewer
    [ ] Worker Working

    Priority: <Low, Medium, High or Auto>
    Worker Blocked On: <issue>, ..., <issue>    (only when blocked for the Worker)
    Reviewer Blocked On: <description>          (only when blocked for the Reviewer)
    Parent: <issue>                             (only when it came from another)

with exactly one box checked.

- **Ready for Worker:** the Worker may work on it.
- **Ready for Reviewer:** waiting for the Reviewer. The Worker never
  changes an issue in this state.
- **Blocked for Worker:** the Worker can't go on until the issues named in
  its `Worker Blocked On:` line are closed. Only the Worker sets this;
  waiting for the Reviewer is "Ready for Reviewer" instead. When the last
  of them closes, the Worker unblocks it (`lock.py unblock`).
- **Blocked for Reviewer:** the Reviewer can't go on until something else
  happens (feedback from a colleague, say), described briefly in its
  `Reviewer Blocked On:` line. Only the Reviewer sets this. To the Worker
  it's the same as "Ready for Reviewer": the Worker never changes it. It
  reminds the Reviewer, when they open the issue, that it may not be ready
  for them yet.
- **Worker Working:** the Worker is working on it, and holds its lock.
- **Priority** "Auto" means the Worker chooses one. A file without a
  status block, or without a priority, gets one added: "Ready for Worker",
  and "Auto".

`TODO.md` has the same status block and is handled like any issue. What's
special about it is its name and place, that the Worker takes it first in
a round, and that its job is to turn its items into issues.

## A round: "make progress on issues"

1. **Update this skill** (see "Keeping this skill current").
2. **Commit the Reviewer's changes** on the main branch (their responses,
   new items in `TODO.md`, status boxes they set) before working on them,
   so that their changes and the Worker's are separate commits. The box is
   the signal that they're done: commit the changes of an issue (or
   `TODO.md`) only once it's "Ready for Worker". One still "Ready for
   Reviewer" (or "Blocked for Reviewer") may be half written: leave its
   changes uncommitted and untouched, and keep them out of the Worker's own
   commits (stage files by name, never all of `open/` at once). So the
   Reviewer ticks the box last.
3. **`TODO.md` first,** if it's "Ready for Worker". Turn each of its items
   into an open issue (small related items may share one), and delete it
   from `TODO.md`. Analyze each new issue: if it needs no decision from the
   Reviewer, it's ready to work on; otherwise ask, and hand it to the
   Reviewer.
4. **Then the open issues** marked "Ready for Worker" (and only those),
   the new ones included, in the order that makes sense: blockers first,
   then by priority, and by how much each unblocks.
5. For each: lock it (`lock.py take`, which checks "Worker Working"), read
   its last response, do what's ready, and append what was done, with
   results and evidence, and any questions. Then release it, with the
   status it's left in. A question doesn't stop the rest: keep working on
   everything it doesn't affect, and hand the issue to the Reviewer only
   when nothing is left that doesn't need them.
6. **New work found along the way** becomes a new issue, with `Parent:`
   naming the issue it came from.

## Branches and worktrees

- **One branch and worktree per issue,** never the main checkout:

      git worktree add <worktrees>/<issue> -b issue/<issue> <main branch>

  Commit to the branch as often as is useful, and rebase it on the main
  branch to take in other issues' work.
- **A branch that needs another issue's unmerged work** is created from
  that issue's branch instead (*stacked*), and its issue says so. It merges
  after that issue closes, rebased onto the main branch then; commits
  already merged in their rebased form are skipped (`git rebase --skip`).
- **Issue files live only in the main checkout,** on the main branch: its
  copy is the one source of truth. Edit an issue's file there, not in a
  worktree's copy, and commit it on the main branch. Check the working
  directory before editing or committing one: a shell left in a worktree
  is the easy way to get this wrong.

## Locks

Several Workers may work on the issues at once, each on the issues it has
locked. `lock.py`, beside this file, keeps them apart. It finds the issues
directory from `--dir DIR`, or the `ISSUES_DIR` environment variable, or
else `issues/` in the working directory. Its commands:

- **`lock.py take <issue>`** creates `locks/<issue>.lock` atomically
  (failing if another Worker holds it), checks "Worker Working", and makes
  the file read-only, so that an editor warns the Reviewer before they
  change it. It refuses an issue that isn't "Ready for Worker" (or a stale
  "Worker Working").
- **`lock.py open <issue>`** makes a held issue's file writable, to append
  to it; **`lock.py shut <issue>`** makes it read-only again.
- **`lock.py release <issue> <status>`** sets the status (`worker`,
  `reviewer`, `blocked` or `working`), makes the file writable, and removes
  the lock. `blocked` is "Blocked for Worker": the Worker adds the `Worker
  Blocked On:` line itself, before releasing.
- **`lock.py unblock <issue>`** is for an issue blocked for the Worker
  whose blockers have all closed: it checks "Ready for Worker" and removes
  the `Worker Blocked On:` line (no lock needed).
- **`lock.py drop <issue>`** removes the lock, leaving the status, after
  closing an issue.
- **`lock.py status`** lists the locks, with their age.

Use `TODO` as the issue to lock `TODO.md`.

**Stale work:** "Worker Working" with no lock, or with a lock older than a
day whose worktree has no recent changes, was left by a session that
ended mid-issue (a crash, a stop, a usage limit). It means "Ready for
Worker", and the lock may be broken, saying so in the issue. Locks are
local to one machine.

## Closing an issue

Only when the Reviewer asks (to close it, or in a response saying it's
ready). In this order, since every commit on the main branch moves it, and
a fast-forward merge needs the branch rebased after the last of them:

1. In the main checkout, append the final notes to the issue, and commit
   them on the main branch.
2. In the worktree, rebase on the main branch, then run the full checks.
3. In the main checkout, `git merge --ff-only issue/<issue>`.
4. Remove the status boxes and the `Priority:` and `... Blocked On:` lines,
   keeping `Parent:` if it has one; `git mv` the file to `closed/`,
   commit, `lock.py drop <issue>`, and push the main branch.
5. In the main checkout, `git worktree remove <worktrees>/<issue>`, then
   `git branch -d issue/<issue>`, each as its own command.
6. Issues blocked on it, once all their blockers are closed, become ready
   (`lock.py unblock`), and branches stacked on it are rebased onto the
   main branch.

## Splitting

The Worker may split an issue into several (closing it, with a note
naming the new ones) or spawn sub-issues (keeping it open as their
parent, and closing it when they have all closed). Each new issue names
the one it came from in its `Parent:` line.

## Markdown style

Issues are read in a plain text editor as much as rendered, so:

- **Lines at most 100 characters.**
- **Tables aligned:** columns padded so that the `|`s line up in the raw
  text.
- **A table too wide for that** becomes a list (one item per row, as in
  "Locks" above), or a grid table whose cells wrap over several lines:

      +---------+------------------------------------+
      | Command | What it does                       |
      +=========+====================================+
      | take    | creates the lock atomically, and   |
      |         | checks "Worker Working"            |
      +---------+------------------------------------+

## Blocked commands

When a command is blocked, by a sandbox or by a permission rule or check,
don't ask to run it unsandboxed or retry it some other way round the
block. (A command that a setting should allow may just be written in a
form the setting doesn't match. A sandbox exclusion matches only a plain
command that is the whole call: no pipes, no chaining, no `cd` in the same
call, and no options before the subcommand, such as `git -C <repo>` or
`git -c ...`. So `cd <repo>` as a command of its own, if the shell isn't
there already, then run `git push origin main` as another; never
`git -C <repo> push origin main`.) Find a different approach that stays
within it (such as a `python3` script, a path under `$TMPDIR`, or a
file-editing tool). If there is none, write in the issue what was blocked
and why, and move on to other work. In either case, recommend the change
to the project's settings (for Claude Code, `.claude/settings.local.json`)
that would stop the same block next time: an entry in
`sandbox.excludedCommands`, a path for `sandbox.filesystem.allowRead` or
`allowWrite`, or a rule in `permissions.allow`, with the exact JSON to add
and why. Offer a command for the Reviewer to run
themselves only for what no setting can cover, such as an interactive
login.