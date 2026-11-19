# Watching a project's issues (README.md, "Watching the issues"): copy this
# file to the project's root, or its targets into the project's Makefile, and
# change lock.py's path if the skill isn't in ~/.claude/skills.

# The issues, one line each, sorted and highlighted by status.
.PHONY: status
status:
	@python3 ~/.claude/skills/darais-issues-workflow/lock.py list --color

# `make status` again whenever an issue file changes, with entr
# (https://eradman.com/entrproject/), and whenever the terminal changes size,
# since the list is cut to the terminal's width.
#
# - A file changes: entr runs `make status` again.
# - An issue comes or goes: entr exits when a watched file is removed (status
#   1: an issue closed, so moved to closed/) or a file is added to a watched
#   directory (status 2: a new issue), so the loop starts it again with the
#   new list of files.
# - The terminal changes size: entr doesn't watch for that, so the shell does.
#   entr runs in the background while the shell waits for it. On SIGWINCH the
#   shell's trap sets r and stops entr, and the loop starts it again, which
#   prints the list at the new width. The second `wait` collects the stopped
#   entr, since the first returned early, for the signal.
# - Ctrl-C ends it: a background command ignores SIGINT in a shell without
#   job control, so the shell's trap stops entr and exits.
# - Any other exit of entr (an error, or entr not installed) ends the loop.
.PHONY: watch
watch:
	@trap 'r=1; kill $$p 2>/dev/null' WINCH; \
	trap 'kill $$p 2>/dev/null; exit 0' INT TERM; \
	while true; do \
	  r=0; \
	  find issues/TODO.md issues/open/* | entr -n -d -c -c -s "make status" & p=$$!; \
	  wait $$p; s=$$?; \
	  if [ $$r = 1 ]; then wait $$p; continue; fi; \
	  case $$s in 1|2) sleep 0.2 ;; *) break ;; esac; \
	done
