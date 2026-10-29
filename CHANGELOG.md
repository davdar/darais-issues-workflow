# Changes to the Darais Issues Workflow

Each version, newest first: what changed in `SKILL.md` and `lock.py`, so
that a project on an older version can see what to do differently after
updating, and how to migrate its issues directory when it must.

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
