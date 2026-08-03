# Commit errata

Commits on this branch whose message is inaccurate about its own contents.

History is immutable here (`PROGRAMME.md` principle 6: no history rewrite,
no force-push), so these cannot be fixed in place. This file is the
correction of record. It exists because the disclosure in `STATE.md` does
not sit where a reader who has hit one of these commits will be looking. A
tracked errata file next to the programme documents does.

**Who this is for: anyone running `git bisect`, `git log -S`, or
`git blame` on this branch, or reading a commit message to decide what a
commit did.** Both entries below will mislead you if you trust the message.

Every claim in this file was verified against git at the time of writing
(`git show --stat`, `git show <sha> -- <path>`, `git log -S`), not carried
from prose. Re-verify with the commands given rather than trusting this
table.

---

## E1. `8a5888d` says F1 was NOT landed. It contains the F1 fix.

**This is the more serious of the two, because it actively misleads.**

| | |
|---|---|
| SHA | `8a5888dea1f47fceb7281f5b867410f0efc9832f` |
| Subject | `docs(improvement): checkpoint Phase 1.5 - revert landed, F1 pending AC2` |
| Date | 28 Jul 2026 01:41:53 +0100 |
| Cause | `git add -A` swept in working-tree changes that were not meant to ride along |

**What the message asserts:**

> F1 is not landed: the post-fix runner shows 1,380 passed and 1 failed
> against a required 1,386/0. [...] F1 will not land until it is green or
> shown unrelated.

**What the commit actually contains:**

```
docs/improvement/STATE.md          |  67 +++++++++++++++
tests/test_classification.py       |  20 +++++-
tests/test_collection_integrity.py | 131 +++++++++++++++++++++++++++++
```

`tests/test_classification.py` in this commit introduces
`RUNNER_ALIAS_PREFIX = "_runner_test_"` and changes the rebind from
`globals()[_name] = _fn` to `globals()[RUNNER_ALIAS_PREFIX + _name] = _fn`.
**That is the F1 fix itself.** `tests/test_collection_integrity.py` is its
regression guard, added whole in the same commit.

**Verify:**

```
git log --oneline --reverse -S'RUNNER_ALIAS_PREFIX' main..HEAD
```

Returns `8a5888d` and nothing earlier. The identifier exists nowhere on
this branch before this commit.

**Consequence for a bisecting reader.** If you are looking for where the
double-counting stopped, the behaviour changes at `8a5888d`, not at
`fd212fb`. A bisect that trusts commit messages will skip past the real
change point. `fd212fb` is where the **published numbers** were corrected
and where the deviation was disclosed; it is not where the code landed.

---

## E2. `140e7fb` contains two files its message never mentions.

| | |
|---|---|
| SHA | `140e7fb583be0478b94bd18da011adf57a978b07` |
| Subject | `docs(improvement): close the reconciliation chain and audit 83.5% per occurrence` |
| Date | 28 Jul 2026 02:29:38 +0100 |
| Cause | `git add -A`, same root as E1 |

**What the message covers:** the reconciliation chain re-measurement and
the per-occurrence 83.5% provenance audit. Both are `STATE.md` content.

**What the commit actually contains:**

```
.claim-quarantine.json                 |   3 +-
data/published_count_manifest.json     |  40 +++++++++++
docs/improvement/STATE.md              |  68 ++++++++++++++++++
tests/test_published_count_manifest.py | 127 +++++++++++++++++++++++++++++
```

`data/published_count_manifest.json` and
`tests/test_published_count_manifest.py` are both new files, neither
mentioned anywhere in the message. They were meant to ride in `fd212fb`,
the count-correction commit.

**Verify:**

```
git show --stat --format="" 140e7fb
git show 140e7fb --format="%B" | grep -i manifest   # returns nothing
```

**Consequence.** Milder than E1: the message is incomplete rather than
contradictory. But `git log -- data/published_count_manifest.json` points
at a commit whose message is about something else, so the reason the
manifest exists is not discoverable from its own history.

---

## Disclosure trail

Both deviations were disclosed by the session that caused them, in the
body of `fd212fb`, under a heading `DEVIATIONS TO DISCLOSE`. They are also
recorded in `STATE.md` and in `HANDOVER.md` section 6. This file adds no
new facts; it puts the existing ones where a bisecting reader will find
them.

## What changed so this does not recur

The cause in both cases was `git add -A`. The countermeasure was a
behavioural promise by the session that made the error, which does not
survive a context reset. It is now a loaded rule instead:
**`.claude/rules/git.md`**, tracked as of 28 Jul 2026, requiring explicit
per-path staging and requiring a checkpoint commit's message to name every
file it touches.
