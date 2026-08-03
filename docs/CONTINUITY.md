# Business Continuity & Key-Person Risk

> **Last reviewed:** 2026-07-27 · **Regula version:** 1.9.0

This document answers, directly, the question a procurement or vendor-risk
team should ask about any small vendor: **"What happens to us if the
maintainer is unavailable?"** We state the risk plainly and show the
mitigations, because an evasive answer is a worse signal than the risk
itself.

## The honest statement of risk

Regula is maintained by a very small team — at times one person. That is
a genuine **key-person / bus-factor risk**, and it is not erased by
development velocity or by the use of AI-assisted tooling. Shipping
quickly and staying available if the maintainer is ill, unreachable, or
stops working on the project are **separate concerns**; we do not conflate
them. The `xz-utils` incident (CVE-2024-3094), in which a single
overburdened open-source maintainer was socially engineered into ceding
control of a critical library, is the reason vendor-risk teams treat
bus-factor-of-one as a *security* question, not only an availability one.
We take that framing seriously.

## Why Regula is structurally better placed than most small vendors

The mitigations below are not promises about the maintainer's future
availability — they are properties of how Regula is built that hold
**regardless** of what happens to any individual.

1. **The source is your escrow.** Regula is Apache-2.0 / EUPL-1.2, and the
   entire tool — engine, patterns, evidence format — is public at
   [github.com/kuzivaai/getregula](https://github.com/kuzivaai/getregula).
   If the project were abandoned tomorrow, any user could fork it, keep
   running it, and maintain it. This is the single strongest continuity
   guarantee a software vendor can offer, and most commercial competitors
   cannot: their code is closed, so their disappearance is your dead end.
   Honest caveat: having the code is not the same as being able to run and
   evolve it — see the forkability runbook below, which exists to close
   that gap.

2. **Nothing is hosted; you already hold your data.** The CLI runs entirely
   on your machine. There is no Regula server, no account, no cloud store.
   Your scans, findings, and evidence packs are local files you possess.
   There is no service that can go down and no data that can become
   inaccessible if the vendor stops operating. "Recovery Time / Recovery
   Point Objective" questions are therefore largely moot: the artifacts
   are already in your control.

3. **Reproducible, verifiable builds.** Releases are published to PyPI via
   OIDC trusted publishing with PEP 740 attestations, and evidence packs
   are hash-manifested and Ed25519-signable. A fork can rebuild and a
   recipient can verify without trusting the original maintainer — the
   trust is in the cryptography and the public source, not in a person.

4. **Forkability runbook.** The repository ships the architecture notes,
   release process, and the full test suite (2,600+ tests) needed to pick
   the project up. A competent Python developer can build, test, and cut a
   release from a clean checkout by following the documented process.

5. **Security clock runs independently of support.** The vulnerability
   response commitments in [`SECURITY.md`](../SECURITY.md) are maintained
   as a continuous obligation. If routine support pauses (see the leave
   policy in [`SUPPORT_SLA.md`](SUPPORT_SLA.md)), security triage does not.

## Where we are honest about the gaps

- **Successor plan (in progress).** The highest-value continuity control
  for a one-maintainer project is a written, tested plan for *who* receives
  signing keys and repository control if the maintainer is permanently
  unavailable, so that security fixes can still ship. This is being
  formalised; until it is, treat single-maintainer control of release
  signing as the residual risk. Stating this plainly is deliberate.
- **No second maintainer yet.** Bus factor is currently low. Raising it —
  a co-maintainer, and longer-term a neutral governance home — is on the
  roadmap, not yet done.
- **Paid-tier escrow.** If and when closed paid-tier components exist, a
  formal source-code escrow arrangement for paying customers is the
  appropriate control; it is not needed while everything is open source.

## What this means for you as an adopter

If you are a consultant or organisation evaluating Regula for client or
production work, the continuity question has an unusually clean answer:
because the tool is open, local, and produces artifacts you already hold,
your exposure to the maintainer's availability is **bounded** — you can
always fork, you never lose access to your own outputs, and you can verify
everything cryptographically. The residual risk is upstream feature and
security maintenance, which the successor plan above is designed to
address. We would rather you weigh that openly than discover it later.
