# Git Survival Guide

## Everyday Workflow

Start the day with `git pull` to fetch your teammates' changes. Create a feature branch with `git checkout -b feature/my-change` so your work stays isolated. Commit early and often with `git commit -m "descriptive message"`. Push your branch with `git push -u origin feature/my-change` the first time, then open a pull request for review.

## Undoing Things

To undo your last commit but keep the changes in your working tree, run `git reset --soft HEAD~1`. If you want to discard the last commit entirely, use `git reset --hard HEAD~1`, but be careful: this permanently deletes work. To undo only the unstaged changes in one file, use `git checkout -- filename` or the newer `git restore filename`. If you already pushed a bad commit, do not rewrite history; instead create a revert commit with `git revert <sha>`.

## Branching and Merging

Merge a finished branch with `git checkout main` followed by `git merge feature/my-change`. For a cleaner history, many teams prefer `git rebase main` on the feature branch before merging. Resolve conflicts by editing the marked sections, then `git add` the resolved files and run `git rebase --continue` or `git commit`.

## Stash

`git stash` temporarily shelves your uncommitted changes so you can switch branches with a clean tree. Bring them back with `git stash pop`. List stashes with `git stash list`, and give them names with `git stash push -m "wip: experiment"`.

## Logs and Inspection

`git log --oneline --graph --decorate -15` shows a compact history of the last 15 commits. Use `git diff` to see unstaged changes and `git diff --staged` for staged ones. `git blame filename` shows who last changed each line, which is invaluable when tracking down a regression.

## Remotes

`git remote -v` lists your configured remotes. Add one with `git remote add upstream <url>`. Never force-push to shared branches like `main` unless the whole team has agreed to it.
