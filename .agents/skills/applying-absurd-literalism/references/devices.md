# Absurd Technical Devices

Examples demonstrate reasoning structures. Do not copy them verbatim; generate from facts already present in the source.

## Literal negation

Correct an imprecise claim by separating two states the user treated as equivalent.

Pattern: “X did not happen; only prerequisite Y happened.” Example mechanism: Docker daemon running does not mean the database container is running or ready.

## Causal over-explanation

Walk through an obvious dependency chain with exaggerated precision until the omitted prerequisite becomes undeniable.

Pattern: daemon → container → process → listening socket → reachable network → accepted credentials. Mention only links relevant to the actual case.

## Bureaucratic reframing

Describe a chaotic change as if it were an official procedure with a brutally accurate outcome.

Pattern: “The proposal has successfully converted one UI rearrangement into coordinated changes to schema, API, validation, and migration.” The formal tone exposes scope inflation.

## Pseudo-scientific verdict

Frame an observed contradiction as a repeatable experiment or measurement.

Pattern: “The experiment confirms that a green base token does not quantum-entangle `hover`.” The real conclusion is that interaction states must be updated independently.

## System personification

Give the system a narrow reaction consistent with its actual behavior.

Pattern: “PostgreSQL has not gone silent out of spite; no process is listening on the configured socket.” Never assign motives that replace diagnosis.

## Anticlimactic praise

Congratulate completion of a prerequisite, then name the unresolved requirement.

Pattern: “Excellent, Docker is running. Now the database only needs to exist, become ready, and be reachable.” Keep the unresolved list short and accurate.

## Selection rules

- Use literal negation for conflated states.
- Use causal over-explanation for missing dependency links.
- Use bureaucratic reframing for underestimated change scope.
- Use pseudo-scientific verdict for conflicting UI or configuration states.
- Use system personification for observable service behavior.
- Use anticlimactic praise for a completed prerequisite presented as proof of success.
- Rotate devices across adjacent blocks and repeated requests.
