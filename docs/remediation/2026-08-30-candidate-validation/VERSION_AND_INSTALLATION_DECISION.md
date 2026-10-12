# Version and installation decision

Date: 30 August 2026

## Decision

CONDITIONAL GO: retain 2.0.0 as the intended first release of public review schema 2.0, but do not release or publish it yet.

The existing local `v2.0.0` tag is not the candidate and must not be described as containing the remediation. It resolves to `0b2b1642cf5b7e8786a1a5dcba93f7b75e170ccd`; the candidate resolves to `3b6ca1f7e483ff35838a814c043e6b0361a2d55a`.

If the owner establishes that the existing tag was distributed or relied upon, do not move it. Use a subsequent version after reviewing compatibility and changelog impact. If it was never distributed, the owner may decide whether to delete and recreate the local tag only after the final gates pass. No tag was changed in this session.

## External availability truth

EXTERNALLY VERIFIED on 30 August 2026:

- PyPI serves `regula-ai` 1.9.0. The earlier assertion that PyPI was unavailable is CONTRADICTED.
- The public PyPI page still contains stronger classifier and obligation wording than the candidate boundary. The 1.9.0 package is not the candidate.
- GitHub displays no public releases.
- GitHub displays no public tags.

PyPI control or ownership was not verified. This remains an explicit publication-gate condition.

## Reproducible candidate identifiers

Use all of the following until a reviewed release exists:

- Commit `3b6ca1f7e483ff35838a814c043e6b0361a2d55a`.
- Source-distribution SHA-256 `d272eeda38cba7ce179e663b860add30fe2be96c5224c0605b094dde158f133c`.
- Wheel SHA-256 `4862f4653c287429dfdad522b8ab3886e1915b0010769f7d64c8bb0a33040741`.
- Public review schema 2.0.
- Evidence schema 1.0.
- Assessment share schema 4.
- Rating packet schema 1.0.
- Cache schema v8.

## Installation guidance

The candidate documentation no longer presents a moving main branch, the stale local tag, the existing PyPI package or a non-existent GitHub release as reproducible installation sources.

Before publication, replace the documentation placeholder `COMMIT_SHA` only with the exact reviewed public commit. Do not point it at a branch name.

REPRODUCED: both local artefacts install without network access and pass installed CLI and content verification. That supports local candidate review only. It does not authorise upload to PyPI or GitHub Releases.

## Build metadata correction

The candidate uses an SPDX licence expression and `project.license-files`. The declared build floor was setuptools 68, which failed locally. Authoritative setuptools documentation states these PEP 639 fields require setuptools 77 or later, so the candidate now declares `setuptools>=77,<84`.

## Owner release actions

1. Establish whether the local `v2.0.0` tag was ever distributed outside the public GitHub tag surface.
2. Verify PyPI project control and correct the stale 1.9.0 public description before any new upload.
3. Run the complete final suite in a loopback-capable clean environment against the candidate commit.
4. Run protected remote CI and required publication controls.
5. Decide whether 2.0.0 can be used or whether a subsequent version is required.
6. Create an annotated tag and release only after the above evidence is retained.
