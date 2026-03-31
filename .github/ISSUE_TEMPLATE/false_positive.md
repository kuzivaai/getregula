---
name: False Positive Report
about: Report a file or pattern incorrectly classified by Regula
title: "[FP] "
labels: false-positive, accuracy
assignees: ''
---

## File or Code That Triggered the False Positive

Paste the relevant code snippet or describe the file:

```python
# Paste the code that was incorrectly flagged
```

## Actual Classification (What Regula Said)

- **Risk level assigned**: (e.g., high, unacceptable)
- **Pattern matched**: (if shown in output)
- **Command run**: (e.g., `regula check src/`)

## Expected Classification

What the correct classification should be and why.

## Why This Is Wrong

Explain why the flagged code does not match the risk category Regula assigned. For example:
- The library is used for a non-AI purpose
- The pattern match is too broad
- The context changes the meaning

## Environment

- **Regula version**: (run `regula --version`)
- **Python version**: (run `python3 --version`)

## Additional Context

Any other details that help understand why this is a false positive.
