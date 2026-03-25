# GPAI Model Obligations — EU AI Act Articles 53-55

Reference for Regula GPAI awareness notes.

## Who Is a GPAI Provider?

A GPAI model is an AI model trained using more than 10^23 FLOPs that is
capable of generating text, audio, images, or video, and can be integrated
into various downstream systems.

**Fine-tuning threshold:** A modifier/fine-tuner only becomes a GPAI provider
if the modification uses more than 1/3 of the original model's compute.
In practice, most fine-tuning (LoRA, QLoRA, adapters) does NOT meet this
threshold.

Source: EU Commission GPAI Guidelines, July 2025.

## Timeline

- **2 August 2025:** GPAI transparency obligations in effect
- **2 August 2026:** Commission enforcement powers begin (fines)
- **2 August 2027:** Legacy models (pre-August 2025) must comply

## Core Obligations (All GPAI Providers)

1. **Technical documentation** — Model architecture, training approach,
   evaluation results. Must be maintained and updated.

2. **Training data summary** — Using the Commission's mandatory template.
   High-level information about data types, sources, and collection methods.

3. **Copyright policy** — Document compliance with EU copyright law,
   particularly regarding text and data mining.

4. **Downstream provider notification** — Share documentation and
   information with providers integrating the GPAI model.

5. **Retention** — Documentation must be preserved for minimum 10 years
   after model's initial release.

## Code of Practice

The GPAI Code of Practice (published 10 July 2025) is voluntary but
provides a safe harbour: adherence demonstrates compliance until
harmonised standards are published.

## Systemic Risk Models (Additional Obligations)

Models with systemic risk (>10^25 FLOPs or Commission designation) have
additional requirements:
- Adversarial testing
- Serious incident reporting
- Cybersecurity protections
- Energy consumption reporting

Source: EU AI Act Articles 53-55; GPAI Code of Practice; EU Commission
Guidelines for providers of general-purpose AI models (July 2025).
