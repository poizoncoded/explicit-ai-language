---
name: checking-explicit-boundaries
description: Use when a profane Russian response must be checked for immutable artifacts, excessive growth, repetition, and forbidden language before it is returned.
---

# Checking Explicit Boundaries

Act as the mandatory final gate for explicit Russian prose. The useful factual answer outranks style, and the boundary always wins.

## Validation Workflow

1. Keep the completed neutral or pre-style response as the source and the transformed response as the candidate.
2. Read [references/exclusions.md](references/exclusions.md).
3. Compare facts, conclusions, uncertainty, warnings, safety refusals, and action order semantically.
4. Verify that code, commands, paths, URLs, numbers, citations, quotations, logs, identifiers, API names, environment variables, error strings, and their Markdown boundaries are byte-for-byte unchanged.
5. When source and candidate files are available, run:

   ```bash
   python3 scripts/check_response.py --source SOURCE_FILE --candidate CANDIDATE_FILE
   ```

6. Reject identity-based degradation, threats, coercion, prohibited sexual content, criminal/prison framing, and every other category in the exclusions reference even when the deterministic checker has no marker for it.
7. Reject uncontrolled growth, repeated signature phrasing, profanity inside protected spans, and jokes that replace technical content.

## Recovery Rule

Use no more than two validation passes:

1. Validate the candidate.
2. On failure, replace only the failing style element with an allowed technical, household, bureaucratic, scientific, or absurdist construction; restore protected content; then validate once more.
3. If the second pass fails or uncertainty remains, return the useful source response in a neutral voice.

When the user requests a forbidden style element, keep the useful task active, decline only that element, and use an allowed alternative. Do not weaken an existing safety refusal or add operational detail to it.

Return only the accepted candidate or neutral fallback. Do not expose denylist internals, validation reasoning, or the pipeline.
