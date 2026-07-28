# Measurement Rules

Five rules. This programme paid for every one of them with a wrong number
that was published or nearly published. They are loaded every session so
they survive a context reset, which a promise does not.

If you are about to report a number, you are in scope.

## 1. Measure in place.

Run the real module from its real location, against the real files.

Never measure with a copy. `scripts/claim_auditor.py` derives `REPO_ROOT`
from its own file location, so a patched copy run from a scratchpad
resolves every repo-file citation against that scratchpad. Sourced
paragraphs then count as unsourced. That is exactly how the figures 185
and 168 were produced, and **185 was never a state this repo was in.**

If you must instrument something, wrap the real function to tally and
delegate to it. Do not fork it.

## 2. One variable at a time, on one code state.

If two things changed between two measurements, you cannot attribute the
difference to either. Commit `35fc763` credited a CSS fence with removing
140 findings; the F7 coordinate fix had landed between the measurements
and the real fence delta was 16.

Toggle one flag. Re-measure. Then toggle the next.

## 3. Never trust a number produced by a copy, including your own earlier one.

A number in prose is not evidence. A number in a handover is not evidence.
A number you wrote yesterday is not evidence.

Re-derive it from the command. If you cannot re-derive it, say
"unverified" and move on. Quoting a figure forward is how 2,821 survived
across nine published surfaces while being overstated by 18.5%, and how
"55 occurrences" sat five lines above "45 occurrences" in the same file.

## 4. Require positive proof the code path executed.

An absent signal is not a passing signal.

- A blank gate is not a green gate.
- A piped exit code is not an exit code. Use `PIPESTATUS`, or redirect to
  a file and check `$?`.
- A test that never created its fixture file passes its filename
  assertion for the wrong reason.

Before reporting a result, run the control: make the thing fail on
purpose and confirm you see the failure. If you never saw it fail, you do
not know it can.

## 4b. Before calling a file a published surface, check it is tracked.

**Untracked files are not surfaces.** They are local scratch. They do not
ship, they are not on the website, and nobody outside this machine can read
them.

Counting them inflates scope and produces confident wrong numbers. This
programme has done it twice in one session: a reviewer counted
`docs/FULL_REVIEW.md` (gitignored) as a published surface, and one section
later I counted 22 untracked files in my own scope figure and reported
**58** ungated docs files when the tracked, publishable figure is **34**.

```
git ls-files <path>        # empty output means NOT a surface
```

Corollary, learned the same day: **produce counts with a test, not with
prose.** A hand-built list of "every location" of the 83.5% figure had
**eight** entries; the tracked total is **fourteen**. The test found the
other six in one run. Any number you assert in a document will drift; a
number a test computes cannot.

## 4c. Any completeness claim must be produced by enumeration, never by hand.

"Every location", "all surfaces", "the full list" — if you are about to
write one of those phrases, the set behind it must come from
`git ls-files` plus a pattern match, executed. Not from reading. Not from
grep-and-eyeball. Not from memory.

**Hand enumeration has now failed twice in this programme:**

- A pack table claimed to cover **every** location of the 83.5% figure and
  listed **8**. The tracked total is **14**. The six it missed included
  `site/index.html`, the landing page. The owner approved a disposition on
  that table, so approval was granted on incomplete evidence.
- A scope figure claimed **58** ungated docs files. The tracked,
  publishable figure is **34**; the other 22 were untracked local scratch.

Both were confident, both were wrong, and in both cases a five-line script
produced the right answer immediately.

**The rule:** a completeness claim is a measurement. Produce it the way you
produce any other measurement, and let the enumeration be the source of the
number in the document.

## 4d. Enumeration picks the files. It does not license a blind replace.

Corollary to 4c, learned by nearly shipping a corrupted lockfile.

Cascading a test count from 2,353 to 2,354, I enumerated the affected
files correctly with `git ls-files | xargs grep -l`, then ran a global
string replace across every hit. One hit was `uv.lock`, where `2353`
appeared inside a package download URL hash path and inside an integrity
`size = 222353` field. Both were rewritten. That lockfile would have
failed installs and integrity verification.

**Enumeration answers "which files". It does not answer "which
occurrences".** A digit sequence is not a claim just because it appears in
a file that also contains claims.

- Replace with context, not bare digits: match `2,353 tests`, a JSON key,
  a known template, not `2353`.
- **Never text-replace inside lockfiles, checksums, hashes, or generated
  binaries.** Exclude them by extension before you start.
- Read the diff of every file you touched before committing. `git diff`
  caught this; nothing else would have.

## 4e. Before asserting two artefacts contradict, read both in full.

**A discrepancy claim is a claim.** It carries the same evidence burden as
the number it disputes, and an artefact's own methodology section is part
of the artefact.

I reported that a blog post's headline statistics "do not reconcile" with
the repo's tracked scan data, called it the most serious item in an
approval pack, and escalated it. The post's own methodology note disclosed
the exact figure I was citing against it, named the version and date of
both scans, and explained the difference. I had not read that far into the
post.

The cost was one escalation rather than a false correction to a correct
post, and only because the finding was quarantined rather than acted on.
**Quarantine-and-escalate is what absorbed the error. Do not skip it on a
finding that feels obvious.**

## 5. Passing a gate is not evidence of meeting a standard when the gate tests something narrower.

This is the one that keeps recurring, in two different instruments.

- The 83.5% precision claim is not in the quarantine, so it passed the
  auditor's criterion (an annotation exists somewhere). The bar was honest
  provenance at the point of use. It failed that at **five of eight**
  locations, including a bare number on a public page.
- Every `<meta>` description number passes the auditor because the `<head>`
  block contains `<link rel="canonical">`, and a URL satisfies
  `paragraph_has_source()`. The page's own address is not a source for
  anything. Finding F21.

Before reporting a gate as evidence, state in one sentence what the gate
actually tests, and compare it to what you are claiming. If the gate is
narrower, say so and report the gap.
