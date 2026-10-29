#!/usr/bin/env python3
"""Locks on issue files, for the Darais Issues Workflow (see SKILL.md, "Locks").

    lock.py [--dir DIR] take <issue>     take an issue: create its lock
                                         atomically, check "Worker Working",
                                         make the file read-only; refused
                                         unless the issue is "Ready for
                                         Worker" (or a stale "Worker Working")
    lock.py [--dir DIR] open <issue>     make a held issue's file writable
                                         (to append to it)
    lock.py [--dir DIR] shut <issue>     make it read-only again
    lock.py [--dir DIR] release <issue> <status>
                                         set the status (worker, reviewer,
                                         blocked, meaning "Blocked for
                                         Worker", or working), make the file
                                         writable, remove the lock
    lock.py [--dir DIR] unblock <issue>  for an issue blocked for the Worker
                                         whose blockers have all closed:
                                         "Ready for Worker", and its `Worker
                                         Blocked On:` line removed
    lock.py [--dir DIR] drop <issue>     remove the lock and make the file
                                         writable, leaving the status (after
                                         closing an issue)
    lock.py [--dir DIR] status           list the locks, with their age

The issues directory is --dir DIR, or the ISSUES_DIR environment variable,
or else issues/ in the working directory. <issue> is a file name in its
open/ without ".md", or "TODO" for its TODO.md. A lock is
locks/<issue>.lock, created with O_EXCL, so two Workers can't both take an
issue; it holds who took it and when.
"""

import datetime
import os
import stat
import sys

ISSUES = os.environ.get("ISSUES_DIR", "issues")
LOCKS = os.path.join(ISSUES, "locks")
# The status block's lines, in order, in every issue and in TODO.md.
LABELS = [
    "Ready for Worker",
    "Ready for Reviewer",
    "Blocked for Worker",
    "Blocked for Reviewer",
    "Worker Working",
]
# The statuses the Worker may set. "Blocked for Reviewer" is the
# Reviewer's alone.
STATUSES = {
    "worker": "Ready for Worker",
    "reviewer": "Ready for Reviewer",
    "blocked": "Blocked for Worker",
    "working": "Worker Working",
}
BLOCKED_ON = "Worker Blocked On: "


def issue_file(issue):
    if issue == "TODO":
        return os.path.join(ISSUES, "TODO.md")
    return os.path.join(ISSUES, "open", issue + ".md")


def lock_file(issue):
    return os.path.join(LOCKS, issue + ".lock")


def set_writable(path, writable):
    mode = os.stat(path).st_mode
    if writable:
        os.chmod(path, mode | stat.S_IWUSR)
    else:
        os.chmod(path, mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def read_status(path):
    """The file's lines, how many of them are its status block, and the
    label checked in it (None if none is)."""
    with open(path) as f:
        lines = f.read().split("\n")
    n = 0
    checked = None
    while n < len(lines) and n < len(LABELS) and lines[n][4:] == LABELS[n] \
            and lines[n][:4] in ("[ ] ", "[x] "):
        if lines[n][1] == "x":
            checked = LABELS[n]
        n += 1
    if n < len(LABELS):
        sys.exit(f"{path}: no status block at the top")
    return lines, n, checked


def set_status(path, status):
    lines, n, _ = read_status(path)
    label = STATUSES[status]
    for i in range(n):
        lines[i] = ("[x] " if LABELS[i] == label else "[ ] ") + LABELS[i]
    with open(path, "w") as f:
        f.write("\n".join(lines))


# Who holds a lock: a Claude Code background job's name, when it runs as one
# (its CLAUDE_JOB_DIR), else the parent process, with the time.
def holder():
    job = os.environ.get("CLAUDE_JOB_DIR", "")
    who = os.path.basename(job) if job else f"pid {os.getppid()}"
    return f"{who} {datetime.datetime.now().isoformat(timespec='seconds')}"


def take(issue):
    path = issue_file(issue)
    if not os.path.exists(path):
        sys.exit(f"no issue {path}")
    os.makedirs(LOCKS, exist_ok=True)
    try:
        fd = os.open(lock_file(issue), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        with open(lock_file(issue)) as f:
            sys.exit(f"{issue} is locked: {f.read().strip()}")
    with os.fdopen(fd, "w") as f:
        f.write(holder() + "\n")
    # Checked once the lock is held, so that no other Worker changes it
    # in between. "Worker Working" with no lock is a crashed session's.
    try:
        _, _, checked = read_status(path)
        if checked not in (STATUSES["worker"], STATUSES["working"]):
            sys.exit(f"{issue} is not ready for the Worker: {checked or 'nothing checked'}")
    except SystemExit:
        os.remove(lock_file(issue))
        raise
    set_writable(path, True)
    set_status(path, "working")
    set_writable(path, False)


def release(issue, status):
    path = issue_file(issue)
    set_writable(path, True)
    set_status(path, status)
    if os.path.exists(lock_file(issue)):
        os.remove(lock_file(issue))
    else:
        print(f"{issue} wasn't locked; its status is set", file=sys.stderr)


def unblock(issue):
    path = issue_file(issue)
    _, _, checked = read_status(path)
    if checked != STATUSES["blocked"]:
        sys.exit(f"{issue} isn't blocked for the Worker: {checked or 'nothing checked'}")
    set_writable(path, True)
    set_status(path, "worker")
    with open(path) as f:
        lines = f.read().split("\n")
    with open(path, "w") as f:
        f.write("\n".join(l for l in lines if not l.startswith(BLOCKED_ON)))


def drop(issue):
    path = issue_file(issue)
    if os.path.exists(path):
        set_writable(path, True)
    os.remove(lock_file(issue))


def show_status():
    if not os.path.isdir(LOCKS):
        return
    now = datetime.datetime.now()
    for name in sorted(os.listdir(LOCKS)):
        if name.endswith(".lock"):
            with open(os.path.join(LOCKS, name)) as f:
                text = f.read().strip()
            age = now - datetime.datetime.fromtimestamp(os.stat(os.path.join(LOCKS, name)).st_mtime)
            print(f"{name[:-5]}: {text} (age {str(age).split('.')[0]})")


def main(args):
    global ISSUES, LOCKS
    if args[:1] == ["--dir"] and len(args) >= 2:
        ISSUES, args = args[1], args[2:]
        LOCKS = os.path.join(ISSUES, "locks")
    if args[:1] == ["status"]:
        show_status()
    elif len(args) == 2 and args[0] == "take":
        take(args[1])
    elif len(args) == 2 and args[0] == "open":
        set_writable(issue_file(args[1]), True)
    elif len(args) == 2 and args[0] == "shut":
        set_writable(issue_file(args[1]), False)
    elif len(args) == 3 and args[0] == "release" and args[2] in STATUSES:
        release(args[1], args[2])
    elif len(args) == 2 and args[0] == "unblock":
        unblock(args[1])
    elif len(args) == 2 and args[0] == "drop":
        drop(args[1])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])

