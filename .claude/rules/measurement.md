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
difference to either. Commit `30cb981` credited a CSS fence with removing
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
