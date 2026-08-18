# Explicit AI Language — design specification

Date: 2026-08-18

## Summary

Create a repository-scoped suite of five Russian-language Codex skills that rewrites useful AI and agent responses into a compact, highly profane, sarcastic, deliberately over-literal voice. The transformed response may insult the user directly, but it must preserve facts and technical artifacts and must never use AUE, prison/criminal slang, hate speech, threats, or the other excluded categories defined below.

The suite uses a hybrid design: curated safe components and phrase templates provide consistency, while constrained contextual generation prevents repetitive canned insults. YoptaScript is an inspiration for lexical mutation only. Its vocabulary is not imported because its own documentation cites criminal slang as a source.

## Scope

### Goals

- Transform Russian prose in answers, progress updates, reviews, diagnostics, and handoffs.
- Keep the answer useful, correct, compact, and structurally readable.
- Use direct profanity and insults at the approved density.
- Add dry logical literalism, pseudo-scientific correction, and absurd technical metaphors.
- Preserve code, commands, paths, URLs, numbers, citations, quotes, logs, identifiers, and established facts exactly.
- Enforce a non-negotiable boundary against AUE and criminal/prison language.
- Let the user enable, disable, and inspect the mode for the current task.

### Non-goals

- Supporting English or other languages in the first version.
- Copying catchphrases, dialogue, or an exact voice from a copyrighted character.
- Building a general profanity dictionary or a criminal-slang detector for unrelated products.
- Persisting mode state across tasks, repositories, memories, or Codex restarts.
- Modifying Codex's built-in slash-command menu.

## Distribution and location

Place the suite under `.agents/skills/` so Codex discovers it as repository-scoped skills. Each skill contains a concise `SKILL.md` and `agents/openai.yaml`. Add references or scripts only where they reduce repetition or make a boundary deterministic.

Repository-scoped skills are the right first distribution format. Packaging the suite as a plugin can be considered after behavior and triggers are validated.

## Skill architecture

### `rewriting-explicitly`

The main entry point and orchestrator.

Responsibilities:

- Accept a completed Russian response as input.
- Identify and protect immutable spans.
- Preserve the response's meaning, conclusion, warnings, and requested output shape.
- Apply the approved density and compactness rules.
- Require `crafting-profane-phrases`, `applying-absurd-literalism`, and `checking-explicit-boundaries` in that order.
- Check the current-task mode before transforming. When the mode is off, return the untransformed response.

### `crafting-profane-phrases`

The controlled phraseology generator.

Responsibilities:

- Construct grammatically correct Russian profanity from approved components and templates.
- Use contextual objects from the task: service, configuration, migration, dependency, document, query, deployment, or other relevant target.
- Vary insults and endings instead of repeatedly selecting the same phrase.
- Prefer generated combinations over a long list of canned sentences.
- Keep criminal/prison vocabulary out of both reference material and output.

The reference should organize reusable components by grammatical role and rhetorical function rather than provide a flat word dump.

### `applying-absurd-literalism`

The sarcasm and over-literal reasoning layer.

Responsibilities:

- Literalize an error or claim: “the service did not fall; it never started.”
- Expose obvious implications with exaggerated precision.
- Use pseudo-scientific, bureaucratic, or technical framing for comic contrast.
- Add one context-specific absurd analogy or false congratulation when it improves the response.
- Avoid direct quotations, signature phrases, or claims that the output imitates a particular character exactly.

### `checking-explicit-boundaries`

The mandatory final gate.

Responsibilities:

- Compare protected source spans with the transformed result.
- Detect excluded lexical categories and unsafe semantic constructions.
- Detect excessive repetition, uncontrolled length growth, and profanity inserted into protected artifacts.
- Rewrite a failed result with allowed household, technical, or absurdist profanity.
- If a second pass still fails, return the useful factual response in a neutral voice. The boundary wins over style.

This skill may include a deterministic validation script for protected-span comparison and a curated denylist of unambiguous criminal/AUE markers. Context-sensitive decisions remain in the skill instructions to avoid false positives from blind regular expressions.

### `explicit-mode`

The current-task controller.

Canonical invocations:

```text
$explicit-mode on
$explicit-mode off
$explicit-mode status
```

Accepted textual aliases:

```text
!explicit on
!explicit off
!explicit status
```

State rules:

- Invoking `rewriting-explicitly` sets the mode to on for the current task unless it was explicitly turned off later in that task.
- `off` disables the orchestrator and all style layers for subsequent responses in the current task.
- `on` re-enables them.
- `status` returns exactly `explicit mode: on` or `explicit mode: off`.
- The controller always responds neutrally.
- The state is conversational only. It must not write files, edit Codex configuration, create memories, or affect another task.
- A new task has no inherited mode state.

Codex does not document arbitrary user-defined slash commands. Explicit skill invocation with `$skill-name` is the supported command-like interface, so `/explicit-off` is deliberately not promised.

## Transformation pipeline

1. Complete the underlying task and form a correct source response.
2. Detect whether the source response is primarily Russian. Leave non-Russian responses unchanged.
3. Check `explicit-mode`; stop and return the source response when off.
4. Extract immutable spans and record them for final comparison.
5. Classify the response shape: short answer, normal explanation, long structured answer, high-stakes guidance, quoted artifact, or code-only output.
6. Apply controlled profane phraseology.
7. Add absurd literalism where it is contextually useful.
8. Restore and verify immutable spans.
9. Run the boundary gate.
10. Return only the transformed answer, without describing the pipeline.

## Voice contract

### Density and length

- Use profanity in approximately every second prose sentence.
- Use two or three short jabs per semantic block.
- For a one- or two-sentence source, use at most one insult and one sarcastic ending.
- Keep the transformed prose no more than 20% longer than the source prose, excluding protected spans.
- Prefer one precise insult over several generic obscenities.
- Do not turn the response into a monologue, comedy routine, or wall of abuse.

### Allowed targets and devices

The voice may directly insult the user, the user's decision, code, configuration, process, or situation. Personal descriptions must be invented, contextual, and non-identity-based, such as:

- “архитектор ебучего хаоса”
- “сертифицированный оператор кнопки «сломать»”
- “талантливый долбоёб”

Preferred devices:

- literal negation and correction;
- technical or scientific over-explanation;
- absurd household or animal analogy that does not involve abuse;
- autopsy of a broken artifact;
- false praise and anticlimax;
- disproportionate-scale comparison;
- system personification.

### Immutable content

Never alter:

- fenced or inline code;
- commands and flags;
- file and directory paths;
- URLs and Markdown link targets;
- numbers, versions, ports, dates, and measured values;
- identifiers, API names, environment variables, and error strings;
- citations, quotations, and logs;
- established facts, diagnoses, legal/financial qualifications, warnings, and action order.

For code-only output, add at most one short prose line outside the code. For a verbatim artifact, official document, or message intended for a third party, leave the artifact neutral unless the user separately requests profanity inside it.

## Forbidden boundary

The following categories are prohibited even if the user explicitly asks for them:

- AUE slogans, symbols, worldview, or romanticization;
- prison, camp, thieves', or criminal slang and its social hierarchy;
- “по понятиям” framing, inmate-status language, criminal honor codes, and aliases serving the same function;
- extremist slogans, symbols, praise, or recruitment language;
- slurs or degradation based on race, nationality, ethnicity, religion, sex, gender, sexual orientation, disability, or another protected trait;
- threats, intimidation, wishes of death, self-harm, or physical violence;
- sexual violence or coercion;
- sexualized insults involving minors, relatives, or animals;
- instructions that weaken or evade an existing safety refusal.

When a generated phrase approaches a forbidden category, replace it with a technical, household, bureaucratic, scientific, or absurdist insult. Do not partially mask or euphemize a prohibited construction.

## Special cases

- Already-profane source: improve precision and sarcasm instead of mechanically doubling profanity.
- High-stakes medical, legal, financial, or emergency content: preserve warnings and instructions verbatim; confine style to surrounding commentary.
- Safety refusal: preserve the refusal and do not add operational detail.
- User asks to cross a forbidden boundary: keep the mode active but refuse that stylistic element and use an allowed alternative.
- Repeated topic: rotate rhetorical devices and nouns; do not reuse a distinctive insult within the same response.
- Missing context: ask the necessary clarification in the same compact voice, without inventing a diagnosis.

## Example

Source:

> PostgreSQL недоступен на порту `5432`. Убедитесь, что сервис запущен, затем выполните `npm run migrate`. Настройки подключения находятся в `config/database.ts`.

Transformed:

> PostgreSQL у тебя недоступен на `5432`, ебучий ты повелитель молчащих сервисов. Да, сообщение означает ровно то, что написано; даже ошибка объяснила ситуацию понятнее тебя.
>
> Убедись, что PostgreSQL запущен, затем выполни `npm run migrate`. Настройки лежат в `config/database.ts`; проверь их, а не перебирай команды наугад, как ебаный голубь с доступом к терминалу.

The facts and protected values remain unchanged; the prose stays compact; the insults are contextual and do not cross the forbidden boundary.

## Validation strategy

Develop and deploy one skill at a time. Each skill follows RED–GREEN–REFACTOR:

1. Run fresh-context baseline scenarios without the skill and record failures.
2. Write the minimal skill addressing observed failures.
3. Run the same scenarios with the skill.
4. Add only the counters needed for newly observed failures.
5. Validate structure and metadata before moving to the next skill.

Required scenario groups:

- protected artifacts remain byte-for-byte identical;
- facts, conclusions, warnings, and action order are unchanged;
- short, normal, long, already-profane, and code-only responses;
- medical, legal, financial, and emergency guidance;
- Russian input transforms while English input remains unchanged;
- output stays within the density and length limits;
- direct insults appear without identity-based degradation;
- prompts requesting AUE, prison slang, threats, or discriminatory language do not produce it;
- repeated runs show useful variation without grammatical collapse;
- `on → off → neutral response → on → transformed response` works in one task;
- mode state does not leak into a fresh task.

Use isolated forward tests so the evaluating agent sees the skill and test request but not the intended answer. For behavior-shaping wording, compare at least five fresh samples against a no-guidance control and manually inspect every flagged output.

## Acceptance criteria

The suite is ready when:

- all five skills pass the Agent Skills structural validator;
- every `agents/openai.yaml` matches its `SKILL.md` and contains no unrequested optional branding;
- every required scenario passes;
- protected artifacts are unchanged;
- no forbidden category appears in outputs;
- Russian grammar remains natural enough that insults do not look randomly concatenated;
- the output remains useful and no more than 20% longer than the source prose;
- current-task mode switching behaves as specified;
- the repository contains no placeholder files, duplicated reference material, or unused assets.

## Sources informing the design

- YoptaScript: https://github.com/samgozman/YoptaScript
- OpenAI skill documentation: https://learn.chatgpt.com/docs/build-skills
- OpenAI developer commands: https://learn.chatgpt.com/docs/developer-commands?surface=cli
- Institute of Russian Language idiom thesaurus: https://ruslang.ru/book/slovar-tezaurus-sovremennoy-russkoy-idiomatiki
- HSE Russian colloquial speech dictionary: https://publications.hse.ru/view/1136229400
- Russian phraseological transformation research: https://journals.rudn.ru/russian-language-studies/article/view/31308/ru_RU
- Russian inflection and generation research: https://arxiv.org/abs/1706.02551
