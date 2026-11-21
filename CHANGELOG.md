# Changes to the Darais Issues Workflow

Each version, newest first: what changed in `SKILL.md` and `lock.py`, so
that a project on an older version can see what to do differently after
updating, and how to migrate its issues directory when it must.

## 1.5.2 (2026-11-20)

`TODO.md` has the six status boxes and nothing else: no `Priority:`
line, nor any other line of the status block. `SKILL.md` said that
`TODO.md` has "the same status block" as an issue, and that a file
without a priority gets one added, which gave `TODO.md` a priority it
has no use for. The text now says so; `lock.py` is unchanged, and
already worked so.

Migrating: delete the `Priority:` line from `TODO.md`, if it has one.
Set `Workflow version: 1.5.2`.

## 1.5.1 (2026-11-19)

`make watch` prints the list again when the terminal changes size. Since
1.4.1 `lock.py list` cuts its lines to the terminal's width, but `entr`
runs it again only when a file changes, so a list printed in a narrow
terminal stayed cut after the terminal was widened. `Makefile`'s `watch`
target now runs `entr` in the background and starts it again on
`SIGWINCH`; its comment says how. (David's change.)

Migrating: a project with its own copy of the `watch` target copies it
again from `Makefile`, with its comment. Set `Workflow version: 1.5.1`.

## 1.5.0 (2026-11-18)

An issue has a branch but no long-lived worktree. Since Claude Code
2.1.323 (November 2026), its sandbox keeps `.git/worktrees/` read-only
except for worktrees Claude Code made itself, so `git commit` fails in a
worktree made with `git worktree add` (`Unable to create
'.git/worktrees/<name>/index.lock': Operation not permitted`), and no
setting short of turning off the sandbox's filesystem isolation lifts it.
(Worked out in David's `research-ideas` project, 2026-11-16.) So
"Branches and worktrees" now says:

- every change to an issue's branch is made by a subagent started with
  `isolation: "worktree"`, which switches to the branch, commits there, and
  switches back at the end so that its worktree is removed;
- the main session stays in the main checkout, and never enters a
  worktree;
- the full checks run in a checks checkout, `.worktrees/<issue>-checks`, a
  plain directory that keeps its build outputs. Two new scripts beside
  `SKILL.md` do it: `checkout.sh <issue>` brings the checkout to the
  issue's branch, and `full-checks.sh <issue>` runs that, then the
  project's steps, from a new file in the issues directory, `checks.sh`
  (one `step <name> <directory> <command ...>` line each).

"Closing an issue" changes with it: a subagent does the rebase, and there
is a checks checkout to delete instead of a worktree to remove. A project
whose Worker can commit in a worktree it made itself may keep long-lived
worktrees, saying so in its `PROJECT.md`.

Migrating:

1. Add `/.worktrees/` and `/.claude/worktrees/` to `.gitignore`.
2. Write `checks.sh` in the issues directory, from the full checks in
   `PROJECT.md`. If the project has its own copies of `checkout.sh` and
   `full-checks.sh`, their steps move to `checks.sh`, and the copies are
   deleted.
3. In `PROJECT.md`, rewrite the "Worktrees" and "The full checks"
   settings as `PROJECT.template.md` has them, and set `Workflow version:
   1.5.0`. If the issues directory's `README.md` describes this
   arrangement as the project's own addition, cut that down to what is
   particular to the project.
4. An open issue with a long-lived worktree keeps it until the issue next
   resumes. Then check that it has nothing uncommitted (`git -C <worktree>
   status --short`) and remove it (`git worktree remove <worktree>`), so
   that its branch is free for subagents.

## 1.4.1 (2026-11-09)

`lock.py list` fits the terminal: in a terminal (or with `COLUMNS` set),
each line is cut to its width, with `…` as its last column where it was
cut, gray with `--color` ("Paused by Reviewer"'s color), so that no line
wraps. Piped, with no width to fit, the lines are whole, as before.

Nothing to migrate: set `Workflow version: 1.4.1`.

## 1.4.0 (2026-11-06)

A new status, "Paused by Reviewer": an issue put down for a while,
neither to be worked on nor closed. Only the Reviewer sets it; to the Worker it's the
same as "Ready for Reviewer". The status block's lines have a new order:

    [ ] Ready for Reviewer
    [ ] Ready for Worker
    [ ] Worker Working
    [ ] Blocked for Reviewer
    [ ] Blocked for Worker
    [ ] Paused by Reviewer

`lock.py list` sorts its lines by status, in that order (`TODO.md` first
among its status's files, then by name), and `lock.py list --color`
prints each status in bold, in a color of its own. A new `Makefile`, to
copy into a project, has `make status` (the list, in color) and `make
watch` (the list again whenever an issue changes, with `entr`);
`README.md` says how to use them.

`lock.py` reads a status block in any order of its lines, with or without
"Paused by Reviewer", and writes it in the new order whenever it sets a
status, so nothing breaks before a project migrates.

Migrating: rewrite the status block of `TODO.md` and of each open issue in
the new order, with "Paused by Reviewer" added and the same box checked,
except in files with the Reviewer's uncommitted changes (one "Ready for
Reviewer" being written, say): leave those to be rewritten when `lock.py`
next sets their status. Commit the rest on the main branch, and set `Workflow
version: 1.4.0`.

## 1.3.0 (2026-11-05)

`lock.py list`: one line per file (`TODO.md`, then the open issues) with
its status, its `Priority:`, `... Blocked On:` and `Parent:` lines,
whether its last REVIEWER RESPONSE block has text, and whether it's
locked, so that a round can be planned without reading every issue in
full. A file without a status block is listed as such. A round's step 1
now ends with triage by `lock.py list`: only the files it shows as
"Ready for Worker" (or a possibly stale "Worker Working") are read
further. Nothing to migrate; set `Workflow version: 1.3.0`.

## 1.2.2 (2026-11-05)

A round's step 3 says that the Worker locks `TODO.md` (`lock.py take
TODO`, so it shows "Worker Working" while its items become issues) and,
once they're issues, releases it, empty, as "Ready for Reviewer"; step 5
says which status a released issue gets: "Ready for Reviewer" when the
Worker is done with it for now, "Ready for Worker" only when work is
left that needs no Reviewer. (Workers had left an emptied `TODO.md`
"Ready for Worker".) Nothing to migrate: a `TODO.md` left "Ready for
Worker" and empty waits until a Worker releases it. Set `Workflow
version: 1.2.2`.

## 1.2.1 (2026-11-03)

`lock.py take` says that it made the issue's file read-only and that
`lock.py open` comes before editing it, so that the Worker doesn't find
out from a refused edit; `lock.py drop` no longer fails on an issue with
no lock (one handed to the Reviewer before being closed). Nothing to
migrate; set `Workflow version: 1.2.1`.

## 1.2.0 (2026-11-03)

Checking that the skill's checkout is current costs the Worker less (the
CPML project's issue `skill-update-cost`): it's done once per session,
not at every round, and a clone can be kept current by a Claude Code
`SessionStart` hook running the new `update.sh`, outside the sandbox,
which prints one line with the skill's version and the project's into the
session's context, so that the Worker runs nothing. `README.md` says how
to set the hook up.

Migrating: nothing required; set `Workflow version: 1.2.0`. To use the
hook, add it to `~/.claude/settings.json` as `README.md` says, and say so
in `PROJECT.md`'s *skill's checkout* setting.

## 1.1.0 (2026-10-29)

`PROJECT.md` is the skill's settings only; what a project adds to the
workflow goes in the issues directory's `README.md` (optional), which the
Worker reads with `PROJECT.md` at the start of a round.

Migrating: move anything in `PROJECT.md` that isn't a setting `SKILL.md`
refers to (the project's own conventions for issues, say) into
`issues/README.md`, creating it if needed, with a pointer to the skill and
to `PROJECT.md` at its top; set `Workflow version: 1.1.0`.

## 1.0.1 (2026-10-29)

Clearer rules for commands a sandbox excludes; nothing to migrate.

- An exclusion matches only a plain command that is the whole call, so
  `git -C <dir> pull` and `cd <dir> && git pull` stay sandboxed. Updating
  a clone, and pushing from another repository, is a `cd` as a command of
  its own, then the git command as another.
- `git worktree remove` and `git branch -d`, when closing an issue, run in
  the main checkout.
- A blocked command's recommended settings change may also be a path for
  `sandbox.filesystem.allowRead`.

## 1.0.0 (2026-10-29)

The first version.

**Adopting it in a project that already tracks issues as files,** with
its own copy of rules like these:

1. In every open issue and in `TODO.md`, replace the status block with
   this version's five boxes ("Ready for Worker", "Ready for Reviewer",
   "Blocked for Worker", "Blocked for Reviewer", "Worker Working"), in that
   order, keeping which one is checked; a blocked issue's line becomes
   `Worker Blocked On: <issue>, ...`.
2. In every open issue, the last response block's heading becomes
   `REVIEWER RESPONSE`. Older blocks, and closed issues, can stay as they
   are.
3. Move the workflow's rules out of the project's own files, since
   `SKILL.md` has them, and keep only the project's settings, in
   `PROJECT.md` (from `PROJECT.template.md`), with the Reviewer's and the
   Worker's names, and `Workflow version: 1.0.0`.
4. Release every lock, then use this `lock.py` in place of any copy.
