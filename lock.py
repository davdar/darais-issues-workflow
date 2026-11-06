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
    lock.py [--dir DIR] drop <issue>     remove the lock, if any, and make
                                         the file writable, leaving the
                                         status (after closing an issue)
    lock.py [--dir DIR] status           list the locks, with their age
    lock.py [--dir DIR] list [--color]   one line per file (TODO.md and the
                                         open issues): its status, its
                                         Priority, Blocked On and Parent
                                         lines, whether its last REVIEWER
                                         RESPONSE block has text, and
                                         whether it's locked; a round can be
                                         planned from it without reading
                                         every file. Sorted by status, in
                                         the status block's order (TODO.md
                                         first among its status's files,
                                         then by name); --color highlights
                                         each status

The issues directory is --dir DIR, or the ISSUES_DIR environment variable,
or else issues/ in the working directory. <issue> is a file name in its
open/ without ".md", or "TODO" for its TODO.md. A lock is
locks/<issue>.lock, created with O_EXCL, so two Workers can't both take an
issue; it holds who took it and when.

A status block is read in any order of its lines, and with or without its
"Paused" line (as files from before 1.4.0 have them); whenever lock.py sets
a status, it writes the whole block in LABELS' order.
"""

import datetime
import os
import stat
import sys

ISSUES = os.environ.get("ISSUES_DIR", "issues")
LOCKS = os.path.join(ISSUES, "locks")
# The status block's lines, in order, in every issue and in TODO.md. `list`
# sorts by this order too.
LABELS = [
    "Ready for Reviewer",
    "Ready for Worker",
    "Worker Working",
    "Blocked for Reviewer",
    "Blocked for Worker",
    "Paused",
]
# Lines a status block may lack: added in a later version than some files.
OPTIONAL_LABELS = {"Paused"}
# The statuses the Worker may set. "Blocked for Reviewer" and "Paused" are
# the Reviewer's alone.
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
    label checked in it (None if none is). The block's lines may come in any
    order, each at most once, and those in OPTIONAL_LABELS may be missing."""
    with open(path) as f:
        lines = f.read().split("\n")
    n = 0
    checked = None
    seen = set()
    while n < len(lines) and lines[n][4:] in LABELS and lines[n][4:] not in seen \
            and lines[n][:4] in ("[ ] ", "[x] "):
        seen.add(lines[n][4:])
        if lines[n][1] == "x":
            checked = lines[n][4:]
        n += 1
    if not seen >= set(LABELS) - OPTIONAL_LABELS:
        sys.exit(f"{path}: no status block at the top")
    return lines, n, checked


def set_status(path, status):
    """Check `status` (a key of STATUSES), writing the whole block, in
    LABELS' order."""
    lines, n, _ = read_status(path)
    label = STATUSES[status]
    block = [("[x] " if l == label else "[ ] ") + l for l in LABELS]
    with open(path, "w") as f:
        f.write("\n".join(block + lines[n:]))


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
    print(f"{issue} locked; its file is read-only: `lock.py open {issue}` before editing it")


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
    if os.path.exists(lock_file(issue)):
        os.remove(lock_file(issue))
    else:
        print(f"{issue} wasn't locked", file=sys.stderr)


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


HEADER_KEYS = ["Priority", "Worker Blocked On", "Reviewer Blocked On", "Parent"]


def header(path):
    """A file's status (None if nothing is checked), its header lines
    (HEADER_KEYS, between the status block and the title), and whether its
    last REVIEWER RESPONSE block has anything in it. Raises SystemExit if
    the file has no status block."""
    lines, n, checked = read_status(path)
    fields = {}
    for line in lines[n:]:
        if line.startswith("#"):
            break
        key, sep, value = line.partition(": ")
        if sep and key in HEADER_KEYS:
            fields[key] = value.strip()
    response = False
    marks = [i for i, line in enumerate(lines) if line.strip() == "REVIEWER RESPONSE"]
    if marks:
        for line in lines[marks[-1] + 1:]:
            if line.strip() and set(line.strip()) == {"-"}:
                break
            if line.strip():
                response = True
                break
    return checked, fields, response


# `list --color`: each status's background, from the 16 standard ANSI colors
# (the bright ones, and white, which terminals show as light gray), all light
# enough for the black text drawn on them.
COLORS = {
    "Ready for Reviewer": "102",    # bright green
    "Ready for Worker": "105",      # bright magenta: purple
    "Worker Working": "103",        # bright yellow
    "Blocked for Reviewer": "101",  # bright red
    "Blocked for Worker": "101",
    "Paused": "47",                 # white: light gray
}


def show_list(color):
    """One line per file (TODO.md and the open issues), sorted by status in
    LABELS' order, then TODO.md first, then by name; files with nothing
    checked or no status block come last."""
    names = ["TODO"] if os.path.exists(issue_file("TODO")) else []
    open_dir = os.path.join(ISSUES, "open")
    if os.path.isdir(open_dir):
        names += [f[:-3] for f in os.listdir(open_dir) if f.endswith(".md")]
    width = max((len(name) for name in names), default=0) + 2
    rows = []
    for name in names:
        try:
            checked, fields, response = header(issue_file(name))
        except SystemExit:
            rows.append((len(LABELS) + 1, name, f"{name:<{width}}no status block"))
            continue
        status = f"{checked or 'nothing checked':<20}"
        if color and checked in COLORS:
            status = f"\033[30;{COLORS[checked]}m{status}\033[0m"
        parts = [f"{name:<{width - 2}}", status]
        parts += [f"{key}: {fields[key]}" for key in HEADER_KEYS if key in fields]
        if response:
            parts.append("response written")
        if os.path.exists(lock_file(name)):
            parts.append("locked")
        rank = LABELS.index(checked) if checked in LABELS else len(LABELS)
        rows.append((rank, name, "  ".join(parts).rstrip()))
    for _, _, line in sorted(rows, key=lambda row: (row[0], row[1] != "TODO", row[1])):
        print(line)


def main(args):
    global ISSUES, LOCKS
    if args[:1] == ["--dir"] and len(args) >= 2:
        ISSUES, args = args[1], args[2:]
        LOCKS = os.path.join(ISSUES, "locks")
    if args[:1] == ["status"]:
        show_status()
    elif args == ["list"] or args == ["list", "--color"]:
        show_list(color=len(args) == 2)
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

