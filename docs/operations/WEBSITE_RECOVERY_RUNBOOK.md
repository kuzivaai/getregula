# Website recovery runbook

Status: owner-gated. This document specifies a reversible recovery. It does not
authorise an agent session to change DNS, deploy, publish or alter repository
settings.

## Purpose and claim boundary

Restore the public informational website through the already functioning
Netlify deployment while package publication remains blocked. The site may
describe Regula as a source-code indicator and evidence-scaffolding tool. It
must not imply that Regula determines applicability, legal classification,
conformity or compliance, or that a public PyPI package is currently available.

## Stop conditions

Stop before changing anything if any of these cannot be established from the
authenticated owner account:

- the exact Netlify project and production deployment;
- control of the apex domain and `www` host;
- the existing DNS record set and its TTLs;
- the project-specific DNS values shown by Netlify;
- the last known-good atomic deployment and its rollback control;
- the public commit and tree represented by the deployment.

Do not infer project-specific DNS targets from examples in documentation. Do
not combine this recovery with a package release, a tag push, a history rewrite
or a product rename.

## Evidence to capture before the change

Record the UTC time and exact output of:

```bash
dig +short getregula.com A
dig +short getregula.com AAAA
dig +short www.getregula.com CNAME
curl -sS -D - -o /dev/null https://getregula.com/
curl -sS -D - -o /dev/null https://www.getregula.com/
```

Export or screenshot the complete DNS record set, the Netlify custom-domain
panel, the selected production deployment and its public commit. Store account
or project identifiers in the private operating record, not this public
repository.

## Owner-controlled recovery

1. In the verified Netlify project, add or confirm the apex domain and `www`.
2. Apply only the project-specific DNS values Netlify displays. Preserve
   unrelated DNS records.
3. Set one canonical host and a permanent redirect from the other host.
4. Wait for Netlify to confirm domain verification and TLS certificate issue.
5. Observe the actual public answers from at least two independent resolvers.

## Public verification

The recovery is complete only when all of the following are observed from the
public internet:

- the apex and `www` resolve to the intended Netlify service;
- HTTPS succeeds with a valid certificate for both hosts;
- the non-canonical host redirects once to the canonical HTTPS URL;
- the home page, `/assess/`, installation and trust content, EN, DE and PT-BR
  pages, and an invalid route return the intended states;
- no page offers a bare `pip install regula-ai` or `pipx install regula-ai`
  command while the registry package is unavailable;
- keyboard-only use reaches navigation, questionnaire controls, errors,
  results and reset without a focus trap;
- the unanswered questionnaire state identifies every missing question and
  moves focus to the first one;
- the completed questionnaire moves focus to its result heading and retains
  explicit limits;
- representative 390 × 844 and 1440 × 1000 layouts have no clipping,
  horizontal overflow or obscured controls.

Repeat the DNS and HTTP commands from the pre-change record and retain their
outputs. Automated checks and screenshots are mechanical evidence. They do not
replace representative human comprehension or assistive-technology testing.

## Rollback

Rollback is either restoration of the exact pre-change DNS records or selection
of the previously recorded known-good Netlify deployment. Use the cheaper
reversible option that addresses the observed fault. After rollback, repeat the
same DNS and HTTP evidence commands and record the outcome.

If the deployed content is wrong but DNS and TLS are correct, roll back the
atomic deployment. If traffic is routed to the wrong service, restore the
recorded DNS set. Do not improvise a second hosting migration during incident
recovery.
