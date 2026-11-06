# Watching a project's issues (README.md, "Watching the issues"): copy this
# file to the project's root, or its targets into the project's Makefile, and
# change lock.py's path if the skill isn't in ~/.claude/skills.

# The issues, one line each, sorted and highlighted by status.
.PHONY: status
status:
	@python3 ~/.claude/skills/darais-issues-workflow/lock.py list --color

# `make status` again whenever an issue file changes, with entr
# (https://eradman.com/entrproject/). entr exits when a watched file is
# removed (status 1: an issue closed, so moved to closed/) or a file is added
# to a watched directory (status 2: a new issue), so the loop starts it again
# with the new list of files; Ctrl-C (status 0) ends it.
.PHONY: watch
watch:
	@while true; do \
	  find issues/TODO.md issues/open/* | entr -n -d -c -c -s "make status"; \
	  case $$? in 1|2) sleep 0.2 ;; *) break ;; esac; \
	done
