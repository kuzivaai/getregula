# Git Rules

These are not style preferences. Each one exists because it was broken and
the breakage is recorded in `docs/improvement/COMMIT_ERRATA.md`.

## Stage explicitly by path. Never stage in bulk.

- **NEVER** `git add -A`, `git add .`, `git add -u`, or `git commit -a`.
- Stage each path by name: `git add path/one.py path/two.md`.
- If the list is long, that is a signal the commit is doing too much, not
  a reason to reach for `-A`.
- This applies to every commit, including checkpoints and "just docs"
  commits. Both recorded errata came from a docs commit that swept up
  code.

## A commit message must name every file the commit touches.

- Before writing the message, run `git diff --cached --stat` and write the
  message against that list, not against what you intended to commit.
- If a file is in the diff and not in the message, either remove it from
  the staging area or add it to the message. Those are the only two
  options.
- A checkpoint commit is held to this most strictly. `0971e28` is a
  checkpoint whose message states a fix was NOT landed while the commit
  contains that exact fix. A bisect that trusts the message walks past the
  real change point.

## Verify the staged set before every commit.

Run both, and read the output:

```
git status --porcelain
git diff --cached --stat
```

Then ask: is every file here one I chose to stage? If any file is a
surprise, unstage it before committing. Do not "fix it in the next
commit"; the message is already wrong by then and history is immutable.

## History is immutable on this branch.

- **Never** commit to `main`. Never force-push. Never rewrite history,
  including rebase, amend of a pushed commit, or filter-branch.
- Because of this, a wrong commit message can only be corrected by a
  separate record. That record is
  `docs/improvement/COMMIT_ERRATA.md`. **If you land a commit whose
  message is inaccurate about its own contents, add an entry there in the
  same session.** Do not leave it for a handover to describe.

## Do not commit generated or ignored output by accident.

- `regula governance` and `regula model-card` drop `AI_GOVERNANCE.md` and
  `MODEL_CARD.md` at the repo root when run inside this repo. These are
  root-anchored in `.gitignore` for that reason, and explicit staging is
  the second line of defence.
- `.claude/` is ignored except `rules/` and `commands/`, which are
  deliberately tracked. Check `git check-ignore -v <path>` if unsure
  whether something is meant to be tracked; note that the user's global
  ignore file also lists `.claude/`, which is why `.gitignore` un-ignores
  the parent directory before re-including subpaths.
