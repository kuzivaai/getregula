# Session log, 31 July 2026 (session C)

Raw evidence record, appended as each check ran. Sessions A and B on the
same date are `SESSION-LOG-2026-07-31.md` and `-31b.md`. This session began
with a context reset, so **everything session B asserted is treated as
unverified until re-derived here** (measurement rule 3).

## STEP 1: state re-established from the repository

```
$ date -Is
2026-07-31T08:34:32+01:00
$ git rev-parse --short HEAD; git rev-parse 'HEAD^{tree}'
d410405
cb02b240f6a49ce9898f5c8973d08db15f6afd63
$ git status --porcelain
 M README.md
 M SECURITY.md
 M data/site_facts.json
 M data/site_facts.md
 M docs/MODEL_CARD.md
 M docs/TRUST.md
 M docs/improvement/LEDGER.md
 M scripts/site_facts.py
 M site/about.html
 M site/llms-full.txt
 M site/regions/uae.html
 M tests/test_site_facts.py
?? docs/improvement/SESSION-LOG-2026-07-31b.md
?? docs/improvement/SESSION-LOG-2026-07-31c.md
$ git log --oneline -3
d410405 docs(improvement): fill the unresolved commit placeholder in ledger row N49
a5c6a7a docs(improvement): record the final suite result in the session log
30fd6e8 feat(guard): an artefact backing a published number cannot be built from untracked inputs; cascade 2,595 to 2,608
```

### Linter
```
$ ruff check scripts/ tests/ --select F821,F811 --ignore E402 --exclude "tests/fixtures"; echo rc=$?
All checks passed!
rc=0
```

### Independent re-derivation of the cascaded count (rule 3: session B's figure is not evidence)
```
$ python3 -m pytest tests/ -q --collect-only 2>&1 | tail -1
2612 tests collected in 1.69s
```

### Six fast gates, each exit code captured separately
```
rc=0 python3 scripts/claim_auditor.py --verify-facts
rc=0 python3 scripts/site_integrity.py
rc=0 python3 scripts/cascade_count.py --check
rc=0 python3 scripts/build_recall_artefact.py --check
rc=0 python3 scripts/build_gap_demo.py --check
rc=0 python3 scripts/check_selfref_sourcing.py --control-only
```

### Fail-before / pass-after, re-derived in THIS session for session B's pending fix
Implementation reverted to HEAD, the new test kept:
```
$ git checkout HEAD -- scripts/site_facts.py
$ python3 -m pytest tests/test_site_facts.py -q
FAILED tests/test_site_facts.py::test_untracked_contributors_flags_a_file_git_does_not_track
FAILED tests/test_site_facts.py::test_untracked_contributors_is_quiet_when_every_contributor_is_tracked
FAILED tests/test_site_facts.py::test_untracked_contributors_defaults_to_asking_git
FAILED tests/test_site_facts.py::test_generation_warns_when_a_contributor_is_untracked
4 failed, 6 passed in 0.23s   rc=1
AttributeError: module 'site_facts' has no attribute 'untracked_test_contributors'
```
Implementation restored:
```
$ python3 -m pytest tests/test_site_facts.py -q
10 passed in 0.31s
```

## STEP 2 (revised): the binding constraint is NOT what session B chose

An adversarial review of session B's diff, launched by session B and
returned into this session, found something that outranks it. **Verified
here independently, not taken on the reviewer's word.**

### THE LIVE DEFECT: three published surfaces carry a stale count and both gates report green

```
$ grep -n -E '(2,354|2\.349)' site/index.html site/locales/de.html site/locales/pt-br.html
site/index.html:346:      <strong style="color:var(--text);">2,354</strong> tests
site/locales/de.html:328: <strong style="color:var(--text);">2.349</strong> Tests
site/locales/pt-br.html:337: <strong style="color:var(--text);">2.349</strong> testes
```
All three ARE listed in `data/published_count_manifest.json` (10 surfaces).
`site/index.html` is the landing page deployed to getregula.com.
The true collected count, re-derived here: **2,612**.
So the landing page understates by **258** and the locales by **263**.

The gate that exists to prevent exactly this reports green:
```
$ python3 scripts/cascade_count.py --check; echo rc=$?
canonical count (data/site_facts.json): 2,612
manifest surfaces: 10
  all manifest surfaces already carry the canonical value
rc=0
```
That sentence is false. This is measurement rule 5 (a gate that tests
something narrower than the claim) and rule 4 (a blank gate is not a green
gate) in the instrument built to enforce rule 4.

### Mechanism, proven by positive control rather than by reading
```
site/index.html      candidates: ['2,354']   template hits: []
site/locales/de.html candidates: []          template hits: []
site/locales/pt-br.html candidates: []       template hits: []

CONTROL, same string with the markup stripped:
   with markup : []
   stripped    : ['2,354 tests']
```
Two INDEPENDENT blindnesses, either one alone sufficient to hide the drift:
1. **Intervening markup.** Every entry in `COUNT_TEMPLATES` joins the number
   to its unit word with `\s+` (`cascade_count.py:75`). The surfaces
   interpose `</strong> `, which is not whitespace, so no template matches
   and `_stale_values` never nominates the value.
2. **Dot-grouped thousands separators.** The candidate scanner
   (`cascade_count.py:212`) is `(?<![\w,.])(\d{1,3},\d{3}|\d{4})(?![\w,.])`,
   which cannot see `2.349` at all. A third, latent defect follows from it:
   `_swap` writes `f"{new:,}"`, so even once detected a de/pt-BR surface
   would receive an English-formatted `2,612` into dot-grouped copy.

**Age.** `site/index.html` has carried 2,354 since `bb52488` (2026-07-28),
across cascades to 2,595, 2,608 and 2,612, with `--check` green each time.

**Precedence.** The directive ranks "anything that makes an existing claim,
figure or output wrong" above new capability, and closing a class above
fixing an instance. This is a wrong number on the public landing page whose
guard is blind by construction. It outranks session B's chosen item, which
is already built and merely needs to land.

## STEP 3: the fix

### FAIL-BEFORE (behavioural, on the exact published bytes)
```
$ python3 -m pytest tests/test_cascade_count.py::TestCountsAreSeenInsidePublishedMarkup -q
E  AssertionError: Items in the second set but not the first:
E  2354 : a count separated from its unit word by inline markup was not seen; this is how site/index.html published 2,354 for 3 days
E  2349 : dot-grouped count invisible to the scanner (de)
E  AssertionError: '2.612' not found in '<strong>2.349</strong> Tests' : separator style not preserved
3 failed, 2 passed in 0.12s
```
The two CONTROL tests in the same class (unrelated number in the same
sentence; years behind markup) passed before AND after, so the widening did
not become the heuristic this module abandoned twice.

### The three changes, all in scripts/cascade_count.py
1. `GAP = r"(?:\s|</?[a-zA-Z][^>]*>)+"` replaces `\s+` in every template.
   Whitespace or complete HTML tags, nothing else. The unit word is still
   required, which is what keeps years safe.
2. The candidate scanner accepts `.` as a thousands separator:
   `(?<![\w,.])(\d{1,3}[.,]\d{3}|\d{4})(?![\w,.])`.
3. `_swap` tries the dotted form FIRST, so de-DE and pt-BR keep their
   separator. Writing `2,622` into German copy would fix a number and break
   a language.
Plus `tests\b` widened to `test(?:s|es)\b` so pt-BR "testes" matches while
"963 test functions" still does not.

### PASS-AFTER, and the tool then saw what it had been blind to
```
$ python3 scripts/cascade_count.py --apply
canonical count (data/site_facts.json): 2,618
manifest surfaces: 10
  updated: 10 surface(s)   [including site/index.html, de.html, pt-br.html]
```

### A SECOND, LARGER INSTANCE FOUND BY ENUMERATION (measurement rule 4c)
Enumerating every tracked `.md/.html/.txt` rather than reading the manifest:
```
docs/architecture.md:53  "45 test files, 1,223 tests (pytest --collect-only)"
```
Short by **1,395**, and absent from BOTH the manifest and
`claim_auditor.VERIFY_FACTS_FILES`. `scripts/claim_auditor.py:1109-1114`
had recorded that exact gap as known and parked behind 1.5c. Corrected to
101 test files / 2,622 tests; both figures re-derived (`git ls-files
'tests/test_*.py' | wc -l` = 101).

`docs/CONTINUITY.md` says "2,600+ tests", which remains true at 2,622 and is
deliberately left alone: cascading a hard number into it would make a
maintenance-free doc need maintenance.

### The class fix, not the instance
`TestEveryPublishedSurfaceCarriesTheCanonicalCount` now enumerates tracked
files with `git ls-files` and never reads the manifest, because a
hand-maintained list cannot prove its own completeness. Exemptions are named
(historical/verbatim records) and a second test asserts the enumeration
actually reaches README, index.html, TRUST.md, de.html and architecture.md,
so an exemption typo cannot make it pass by scanning nothing.

FAIL-BEFORE for that class, planting the original wrong value back:
```
E  AssertionError: Lists differ: ['docs/architecture.md: publishes 1,223'] != []
```

### claim_auditor had the SAME blindness, and its comment claimed otherwise
Its `unit_patterns["tests"]` used `(?:\s*|%20)`, equally blind to
`</strong> `. Its comment asserted it "matches the shape list
scripts/cascade_count.py already uses ... so the two instruments agree".
Repairing one would have made that comment false, so claim_auditor now
IMPORTS `cascade_count.GAP` and a test asserts the two are identical.

CONTROL, both gates against the exact original defect re-planted:
```
$ sed -i 's|2,620</strong> tests|2,354</strong> tests|' site/index.html
$ python3 scripts/claim_auditor.py --verify-facts   ; rc=1
  site/index.html:L346 - tests: found 2,354, expected 2620 (context: '2,354</strong> tests')
$ python3 scripts/cascade_count.py --check          ; rc=1
  would update: 1 surface(s) -> site/index.html
```
Both reported rc=0 on that identical state before this change.

### Widening reach surfaced two FALSE POSITIVES, fixed rather than allowlisted
Adding architecture.md made `--verify-facts` report:
```
docs/architecture.md:L23 - tier_regexes: found 18, expected 419 (context: '18 pattern')
docs/architecture.md:L34 - tier_regexes: found 14, expected 419 (context: '14 pattern')
```
Both are correct PER-MODULE counts, verified against the modules:
`len(credential_check.SECRET_PATTERNS) == 18`,
`len(gdpr_patterns.GDPR_PATTERNS) == 14`. The file makes no repo-wide
pattern claim; the gate inferred one. `VERIFY_FACTS_FILES` entries may now
be `(path, {facts})`, and architecture.md is scoped to `{"tests"}`. Two
tests hold the scoping honest: a scoped entry must still flag a planted
stale value for a fact it DECLARES (rc=1) and must not check one it does
not (rc=0). An allowlist entry would have hidden a real class behind a real
false positive.

### Gates, each exit code captured from $? after redirection, not through a pipe
```
rc=0 scripts/claim_auditor.py --verify-facts       (147 refs across 17 files)
rc=0 scripts/site_integrity.py
rc=0 scripts/cascade_count.py --check
rc=0 scripts/build_recall_artefact.py --check
rc=0 scripts/build_gap_demo.py --check
rc=0 scripts/check_selfref_sourcing.py --control-only
rc=0 scripts/check_decompositions.py
rc=0 ruff check scripts/ tests/ --select F821,F811
$ python3 -m pytest tests/test_stale_number_floor.py tests/test_cascade_count.py \
      tests/test_site_facts.py tests/test_published_count_manifest.py -q
45 passed in 22.80s   rc=0
```

### Final published state
```
site/index.html:346          <strong ...>2,622</strong> tests
site/locales/de.html:328     <strong ...>2.622</strong> Tests
site/locales/pt-br.html:337  <strong ...>2.622</strong> testes
docs/architecture.md:53      101 test files, 2,622 tests
```

## FULL SUITE, quiescent tree, commit captured before launch and confirmed after
```
$ git rev-parse --short HEAD; git rev-parse 'HEAD^{tree}'
a181128
dae3093ef5f89eef6bd8f1359384679c1c8604ae
$ python3 -m pytest tests/ -q
2622 passed in 1441.20s (0:24:01)
FULL SUITE rc=0          (read from $? after redirection, not through a pipe)
$ git status --porcelain  -> empty, still a181128
$ grep -c FAILED          -> 0
```
The passing count equals the published count exactly: 2,622.

## STEP 4: adversarial check

A read-only subagent was given the four commits, the ledger and the session
log, and told to falsify the work and that finding nothing was acceptable.
It returned 11 findings. **Every one below was reproduced in this session
before being acted on; none was taken on the reviewer's word.**

### Reproduced, and all four are real
```
FINDING 1 control, entity gap:
   A tag gap (works today)      -> [2354]
   B &nbsp; entity gap          -> []
   C HTML comment gap           -> []

FINDING 4 control, _swap over a fragment carrying extra digits:
   IN : <strong>2,354</strong><a href="/c#build-2354" id="n2354"> tests</a>
   OUT: <strong>2,622</strong><a href="/c#build-2622" id="n2622"> tests</a>

FINDING 5 control, gap crossing block boundaries:
   D year across block tags     -> [2026]
   E adjacent table cells       -> [2468]

FINDING 3: architecture.md publishes the frameworks fact, twice
   :28  framework_mapper.py  # Cross-framework compliance mapping (13 frameworks)
   :88  **Multi-framework mapping.** 13 frameworks with full crosswalk data
```

### What was FIXED from the adversarial review (6 of 11, plus 1 it did not find)

After the fixes, the reviewer's own counterexamples:
```
FINDING 1 (entity / comment gap) now:
   A tag gap            -> [2354]
   B &nbsp; entity      -> [2354]
   C HTML comment       -> [2354]
   C2 &#160; numeric    -> [2354]

FINDING 4 (_swap must touch exactly one occurrence):
   OUT: <strong>2,622</strong><a href="/c#build-2354" id="n2354"> tests</a>
   badge: tests-2622%20passing
   dotted: 2.622</strong> Tests

FINDING 5 (must NOT cross block boundaries):
   D year across h2/p     -> []
   E table cells          -> []
   F list items           -> []
   M year tag word        -> []
```

FAIL-BEFORE for the three new regression tests, implementation reverted to
`a181128` with the tests kept:
```
E  AssertionError: 2354 : a count separated by named entity was not seen
E  AssertionError: 'href="/c#build-2354"' not found in
   '<strong>2,622</strong><a href="/c#build-2622" id="n2622"> tests</a>'
E  AssertionError: 2026 : the gap crossed a block boundary (year across h2/p)
3 failed, 6 passed in 0.25s
```

### An eighth defect, found BY the repair rather than by the reviewer
Regenerating moved the canonical to a value whose digits collide with a hex
colour, and `test_published_count_manifest.py` failed naming
`scripts/report.py`:
```
E  the published test count appears in files not listed in
   data/published_count_manifest.json: ['scripts/report.py']
$ grep -n '#dc' scripts/report.py    ->  exec_colour = "#dc2626"  (x3)
```
Its scan used `(?<!\d)`, which is the exact defect
`cascade_count._patterns` already carries a comment about ("ee2353d8330 must
NOT match ... the 28 July near-miss"). Fixed to `(?<!\w)`, with a both-ways
control:
```
OLD  (?<!\d) on '#dc2626'    -> ['2626']
NEW  (?<!\w) on '#dc2626'    -> []
OLD  (?<!\d) on '| 2,626 |'  -> ['2,626']
NEW  (?<!\w) on '| 2,626 |'  -> ['2,626']
```
Allowlisting `scripts/report.py` would have blinded the guard to every real
claim in it. **While writing that fix I wrote the count literal into the
comment and the test failed naming its own file** - the file warns about
exactly this - so the literal was removed and the control is constructed
from the live canonical instead.

### Gates and targeted tests after all repairs
```
rc=0 claim_auditor --verify-facts   rc=0 site_integrity
rc=0 cascade_count --check          rc=0 build_recall_artefact --check
rc=0 build_gap_demo --check         rc=0 check_selfref_sourcing --control-only
rc=0 check_decompositions           rc=0 ruff
$ pytest tests/test_cascade_count.py tests/test_stale_number_floor.py \
         tests/test_site_facts.py tests/test_published_count_manifest.py -q
50 passed in 27.88s   rc=0
canonical = 2627
```

### What was DISPUTED or left open, and why
Nothing was disputed as wrong. Five items are recorded OPEN on ledger N57
rather than fixed: the undisclosed 50% magnitude floor in `_stale_values`
(so the claim that manifesting `docs/architecture.md` brought it under the
cascade tool is WITHDRAWN; it was corrected by hand and is held by the
at-rest test and claim_auditor, neither of which has a floor); the
`.claim-allowlist` range patterns that silently covered the exact stale
strings in a third instrument; `--verify-facts` deriving its canonical from
a working-tree compute; the `scripts/` exemption swallowing
`scripts/dashboard/index.html` (measured to carry no count claim today);
and a cosmetic wrong figure in one `wrong_pat` message.

The reviewer's finding 6 was correct and is fixed: three artefacts stated
the architecture.md discrepancy as 1,395, 1,396 and (implicitly) 1,399,
because the canonical moved during the session. All now read "1,223 against
a canonical of 2,618 at the moment of discovery" with the instant named.
