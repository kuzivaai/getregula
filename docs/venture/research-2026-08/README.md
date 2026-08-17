# Research, August 2026

Written 2026-08-17. Every figure carries the source that produced it and the
date it was retrieved. Nothing here is a product decision; it is the evidence a
decision would have to rest on, and in two of the five areas the honest finding
is that the evidence does not exist.

## How to read the provenance labels

- **Primary**: retrieved from the body that produced it (legislation.gov.uk for
  a statutory instrument, a journal's own record for a paper, the vendor's own
  documentation for a claim about that vendor's product).
- **Vendor claim**: primary in the sense that the vendor said it, and not
  independent. A vendor describing its own filtering is evidence of what the
  vendor asserts, not of what the software does.
- **Secondary**: reported by someone other than the producer. Named as such,
  with the attempt to reach the primary recorded.
- **Measured here**: computed in this session from an artefact on this machine,
  with the command shown, so it can be re-derived rather than believed.
- **Reasoned, not evidenced**: no source was found. The reasoning, its
  assumptions, and the observation that would overturn it are stated.

## What did not survive

Recorded first, because the brief asked for failed verifications to be findings
in their own right and because a research document that reports only its
successes is not a research document.

1. **A citation I nearly made, caught by fetching it.** Looking for the primary
   record of Conrad et al. (2010) I constructed a PubMed Central identifier,
   `PMC2910433`, from the PubMed ID rather than from a link. It resolves to a
   real article: Hanson, Sawyer, Begle and Hubel, "The Impact of Crime
   Victimization on Quality of Life", *Journal of Traumatic Stress* 23(2),
   189-197, DOI 10.1002/jts.20508. Nothing to do with progress indicators. The
   correct identifier is `PMC2910434`. A guessed identifier that resolves is
   worse than one that 404s, because it looks verified. This is the class the
   ledger records at N39(c), where a published tree hash named no object in the
   repository, and the only reason it did not survive was that the object was
   checked rather than quoted.

2. **Every publisher record for the strongest paper in section (c) is closed to
   this machine.** ScienceDirect, the ACM Digital Library and Hogrefe each
   returned HTTP 403, and PubMed Central returned a CAPTCHA. The figures in
   section (c) therefore come from the accepted manuscript's own results text as
   surfaced by a search index, not from the publisher's PDF. That is stated at
   the point of use and is a weaker provenance than the rest of this document.

3. **Section (e) came back empty.** What that search returned, and why none of
   it is evidence, is in that section rather than hidden here.
