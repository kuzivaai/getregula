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

## E1. `0971e28` says F1 was NOT landed. It contains the F1 fix.

**This is the more serious of the two, because it actively misleads.**

| | |
|---|---|
| SHA | `0971e282d20694b3222605f6220949bef1c6a9e0` |
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

Returns `0971e28` and nothing earlier. The identifier exists nowhere on
this branch before this commit.

**Consequence for a bisecting reader.** If you are looking for where the
double-counting stopped, the behaviour changes at `0971e28`, not at
`093b839`. A bisect that trusts commit messages will skip past the real
change point. `093b839` is where the **published numbers** were corrected
and where the deviation was disclosed; it is not where the code landed.

---

## E2. `bfd8657` contains two files its message never mentions.

| | |
|---|---|
| SHA | `bfd86571799b79bcd54705c1f981007eb6d0c6bc` |
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
mentioned anywhere in the message. They were meant to ride in `093b839`,
the count-correction commit.

**Verify:**

```
git show --stat --format="" bfd8657
git show bfd8657 --format="%B" | grep -i manifest   # returns nothing
```

**Consequence.** Milder than E1: the message is incomplete rather than
contradictory. But `git log -- data/published_count_manifest.json` points
at a commit whose message is about something else, so the reason the
manifest exists is not discoverable from its own history.

---

## Disclosure trail

Both deviations were disclosed by the session that caused them, in the
body of `093b839`, under a heading `DEVIATIONS TO DISCLOSE`. They are also
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

---

## Erratum 3: `5786666` named two files it does not contain (15 Aug 2026)

**Commit:** `5786666` "feat(site): published pricing, a sourced comparison
table, and three integrity fixes", on `feat/engagement-fixes`.

**What the message says.** Its file list includes
`README.md, SECURITY.md, ... : count cascade only`.

**What the commit contains.** Neither. `git show --stat 5786666` lists 37 files
and neither README.md nor SECURITY.md is among them.

**Cause.** The staging command was `git add -- site/ examples/ content/ data/
docs/ scripts/ tests/ .github/`. Both omitted files sit at the repository root
and match none of those prefixes. This is the same root cause as errata 1 and
2, one step removed: not `git add -A`, but staging by directory rather than by
path, which `.claude/rules/git.md` requires for exactly this reason. Staging by
directory is bulk staging wearing a narrower name.

**Consequence.** At `5786666` the README badge, the README "Verified numbers"
row and the SECURITY.md regression-suite row published a stale collected count.
`cascade_count.py --check` passed while this was true, because it reads the
working tree, where the corrected values were sitting unstaged. **A green
cascade check is not evidence that the committed tree is consistent.** A
bisecting reader who trusts either the message or that gate at `5786666` will
be misled about both.

**Correction.** `a98ab06` lands the three lines. No history was rewritten.

**The same directory-staging command also swept in
`docs/venture/gtm-2026-08-14/`,** three files the 14 August handover records as
deliberately uncommitted pending a sourcing pass. That was caught before the
commit and unstaged, so it is a near miss rather than an erratum. It is
recorded here because it was the same command and the same cause, and because
the catch was manual review of the staged list rather than any gate.

---

## Erratum 4: `a98ab06` named this file before it existed (15 Aug 2026)

**Commit:** `a98ab06` "fix(counts): land the README and SECURITY cascade
omitted from 5786666".

**What the message says.** Its file list includes
`docs/improvement/COMMIT_ERRATA.md: the erratum for 5786666`.

**What the commit contains.** README.md and SECURITY.md only. Erratum 3 above
was written after `a98ab06` had already landed, so the commit that announced
the record did not carry it.

**Cause.** The message was written describing the intended end state rather
than the staged set. `.claude/rules/git.md` requires the message to be written
against `git diff --cached --stat`. That command was run and its output was
read, and the message was still written from intent. **Two consecutive commits
now carry a message naming a file they do not contain**, which makes the rule's
own countermeasure the thing that failed, not the rule.

**Consequence.** Minor and self-correcting: the record exists one commit later.
Recorded anyway, because a reader checking whether `a98ab06` was disclosed
would otherwise find the disclosure missing at the commit that claims it.

**Correction.** The commit landing this file carries both entries.
