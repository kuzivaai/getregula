# Regula for Governance Consultants

A workflow guide for AI governance consultants and advisors who use
Regula inside client engagements to produce verifiable, reproducible
compliance evidence.

Audience: consultants who advise on AI governance, risk, or compliance.
You do not need to be a developer, but the client-facing workflow below
assumes you (or someone on the engagement) can run commands in a
terminal. For a no-install first conversation, use the web assessment
at [getregula.com/assess](https://getregula.com/assess/) — it runs
entirely in the browser and nothing leaves the client's machine.

---

## 0. Install and check your version (do this first)

```bash
pipx install regula-ai     # or: pip install regula-ai
regula --version
```

The package name is `regula-ai`; the command it installs is `regula`.

**Version matters.** This guide describes the current development line
(newer than v1.7.4). On v1.7.4 or older: positional paths do not work on
most commands (use `--project .` instead of `.`), `evidence-pack --sign`,
the engagement branding fields, and the `kr`/`co` aliases do not exist
yet. When any command in this guide is rejected, run
`regula <command> -h` and prefer what the installed version prints.

## 1. What Regula gives an engagement

Consultancy deliverables in this space are usually interviews and
questionnaires — what the client *says* about their system. Regula adds
the other half: evidence from the code itself — what the system
actually *does*. The two together are stronger than either alone.

Concretely, one engagement produces:

| Deliverable | Command | What the client receives |
|---|---|---|
| Risk indicator scan | `regula check .` | Findings mapped to risk tiers and articles |
| Gap assessment | `regula gap .` | Documentation/process gaps against Articles 9–15 |
| Remediation plan | `regula plan .` | Prioritised fix list with effort estimates |
| Executive summary | `regula report . -f exec-summary` | One-page print-ready HTML for boards and counsel |
| Evidence pack | `regula evidence-pack --sign .` | Signed, tamper-evident bundle for auditors |

Everything runs locally. No code, findings, or metadata leave the
client's machine — there is no vendor data-processing relationship to
paper, which materially simplifies engagement setup with security-
conscious clients.

## 2. Getting the regulatory framing right

Before you present results, be precise about what the regulations do —
clients lose confidence fast when the framing is wrong.

- **The EU AI Act regulates AI *systems* by risk tier.** It prohibits
  certain practices outright (Article 5), imposes obligations on
  high-risk systems (Articles 9–15), and sets transparency duties for
  limited-risk systems (Article 50). Whether a system is "high-risk"
  depends on its *use case* (employment, credit, medical, biometrics,
  and the other Annex III categories), not on which libraries it
  imports.
- **The Act does not regulate how software is written.** Using AI
  coding assistants is not an AI Act issue. Code quality is not an AI
  Act issue. What matters is what the shipped system does to people.
- **Regula produces risk *indication*, not legal classification.**
  Article 6 classification requires contextual judgement (intended
  purpose, deployment context, Article 6(3) exemptions) that no scanner
  can make. Regula flags code-level indicators for human review — your
  review. That division of labour is the consulting opportunity: the
  tool does the evidence gathering; you do the judgement.

Read [what-regula-does-not-do.md](what-regula-does-not-do.md) before
your first engagement and keep its limits in your report language.
Overselling a scanner as a compliance determination is the fastest way
to lose a governance client — and it would be wrong.

## 3. Engagement metadata: branding the deliverables

Client-facing deliverables can carry the engagement context. Add an
`engagement:` section to the client project's `regula-policy.yaml`:

```yaml
engagement:
  client: "Client Legal Name"
  prepared_by: "Your Firm"
  reference: "ENG-2026-014"
```

The executive summary then renders **Prepared for / Prepared by /
Engagement ref** lines in its header, and the evidence-pack manifest
records the same block — inside the signed content, so the signature
covers it.

On versions where the engagement fields are not supported, the
`engagement:` block is ignored silently — check the generated summary
header before sending anything to a client.

One-off overrides are available as flags on `regula report` and
`regula evidence-pack`:

```bash
regula report . -f exec-summary --client "Client Ltd" \
  --prepared-by "Your Firm" --engagement-ref "ENG-2026-014"
```

## 4. The engagement workflow

### Step 0 — Scope with the client

Two facts determine everything downstream; establish them in the
kick-off interview, not from the code:

1. **What does the system do to people?** (Hiring? Credit? Medical?
   Education? Biometrics?) This sets the `--domain` declaration.
2. **Where are its users?** This sets the jurisdictions.

### Step 1 — Set up the client project

```bash
cd /path/to/client/codebase
regula init          # guided policy setup
```

Note: `init` never installs editor hooks without asking. Non-interactive
runs only print the install command; interactive runs prompt before
writing anything outside `regula-policy.yaml`. On a read-only or
NDA-bound engagement, simply decline the hook prompt.

Add the `engagement:` block (§3) and declare the client's domain in
`regula-policy.yaml` so every later command sees it:

```yaml
system:
  domain: employment   # or medical, finance, biometrics, education, ...
```

### Step 2 — Scan

```bash
regula check . --domain employment --jurisdictions eu,korea,colorado
```

- `--domain` activates domain-gated high-risk patterns. Regula
  deliberately suppresses opt-in domain patterns (employment, medical,
  finance, biometrics, education, law_enforcement, infrastructure,
  migration) unless the domain is declared or evidenced by imports —
  this is a precision feature, not a gap. Declare what the client told
  you in Step 0.
- `--scope all` includes test/example files if the engagement needs a
  full inventory; the default `production` scope excludes them.
- `--jurisdictions` adds per-jurisdiction obligation mappings to each
  finding (see §5).

### Step 3 — Assess gaps and plan remediation

```bash
regula gap .                          # Articles 9–15 documentation gaps
regula gap . --framework iso-42001    # cross-reference other frameworks
regula plan .                         # prioritised remediation plan
```

**Carry the domain through every step.** If the domain lives only on
your `check` command and not in the policy file, later commands run
domain-blind and can produce a minimal-risk summary or an empty
evidence pack that contradicts your scan. Declaring `system.domain` in
the policy (Step 1) prevents this whole class of self-contradicting
deliverable.

`gap` checks whether compliance *documentation* exists; it does not
verify the documentation is any good. Say so in your report — that
verification is your job, and clients should hear the distinction from
you rather than discover it.

### Step 4 — Produce deliverables

```bash
regula report . -f exec-summary -o exec-summary.html
regula evidence-pack --sign .
```

Both commands write into the current directory: the exec summary
where `-o` points, and the pack as an `evidence-pack-<name>-<date>/`
folder. The pack contains a summary, scan findings, gap assessment,
dependency report, audit trail, remediation plan, Annex IV scaffolding,
risk decisions, a README, and a `manifest.json` with SHA-256 hashes of
every file (signed when `--sign` is used). The audit trail is
project-scoped: it contains only events from the client project's own
audit chain, never activity from other projects or engagements on your
machine — the pack's `05-audit-trail.json` carries a `scope` field
stating the guarantee. The client (or
their auditor, or a successor consultant) can re-verify integrity at
any time with `regula verify <pack-dir>` — no trust in you or in
Regula required. That reproducibility is the point: your deliverable
survives scrutiny you are not in the room for.

### Step 5 — Re-scan on a cadence

Codebases move. A quarterly re-scan against the baseline
(`regula baseline save`, then `regula check --diff` — diff mode
needs the client codebase to be a git repository) turns a one-off
assessment into a monitoring engagement, and the evidence packs
accumulate into an audit trail.

## 5. Choosing jurisdictions

Regula ships domain-to-obligation mappings for three jurisdictions
(defined in the project's [`references/jurisdictions/`](https://github.com/kuzivaai/getregula/tree/main/references/jurisdictions) configs):

| Jurisdiction | Instrument | Status |
|---|---|---|
| `eu` | EU AI Act (Regulation (EU) 2024/1689) | In force, phased enforcement; Annex III high-risk obligations deferred to 2 Dec 2027 under the Digital Omnibus (adopted June 2026, pending OJ publication) |
| `korea` | South Korea AI Basic Act (Act No. 20676) | In force 22 January 2026 |
| `colorado` | Colorado SB 26-189 | Disclosure-focused, plus consumer correction and human-review rights; duties from 1 January 2027 |

`kr` and `co` are accepted as aliases for `korea` and `colorado` on the current development line (not in v1.7.4 or older — use the full names there).

Additional crosswalk-level mappings (`uk`, `brazil`, `nist`, `iso`)
label findings with the corresponding framework references but do not
carry domain-level obligation data.

Select jurisdictions by *user base*, not company location — the EU AI
Act, for instance, applies to any provider whose system output is used
in the EU (Article 2).

## 6. Positioning honestly

Regula's published accuracy figures, methodology, and limits live in
[TRUST.md](TRUST.md) and the
[benchmark reports](benchmarks/PRECISION_RECALL_2026_04.md). Use those
numbers, with their caveats, and no others. In particular:

- Present scan output as **risk indication requiring review** — never
  as a compliance determination or certificate. The exec summary's own
  disclaimer says this; do not remove it.
- False positives and negatives occur; the benchmark pages quantify
  them. A finding is the start of a conversation with the client's
  engineers, not a verdict.
- If a client asks whether running Regula makes them "compliant", the
  honest answer is no — it gives them evidence, visibility, and
  scaffolding, and compliance is a process the engagement builds
  around those.

The tool is open source (Apache 2.0/EUPL 1.2) and free. Your value is
the scoping judgement (Step 0), the interpretation, the remediation
programme, and the accountability structure you build around the
evidence — not access to the scanner.
