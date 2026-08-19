# Explicit AI Language Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, validate, and publish five repository-scoped Codex skills that transform Russian AI responses into a compact, technically useful, profane, sarcastic voice with a current-task mode switch and a hard forbidden-language boundary.

**Architecture:** `rewriting-explicitly` orchestrates three focused style skills and obeys the conversation-scoped `explicit-mode` controller. Phrase construction and absurd literalism remain generative; a final boundary skill combines semantic review with a deterministic checker for protected artifacts and unambiguous forbidden markers.

**Tech Stack:** Agent Skills (`SKILL.md`, `agents/openai.yaml`), Markdown references, Python 3 standard library, `unittest`, PyYAML for the official skill validator, Git, GitHub CLI.

**Spec:** `docs/superpowers/specs/2026-08-18-explicit-ai-language-design.md`

## Global Constraints

- Version one transforms Russian prose only; non-Russian responses remain unchanged.
- Preserve code, commands, paths, URLs, numbers, citations, quotations, logs, identifiers, facts, warnings, and action order exactly.
- Use profanity in approximately every second prose sentence and two or three short jabs per semantic block.
- Keep transformed prose no more than 20% longer than source prose, excluding protected spans.
- For underspecified technical work, explain the likely failure mode, recommend a safe default, and ask exactly one meaningful clarification.
- Permit direct contextual insults, but never identity-based degradation.
- Never generate AUE, prison/criminal slang, extremist material, threats, self-harm wishes, sexual violence, or sexualized insults involving minors, relatives, or animals.
- The forbidden boundary wins over style; unresolved violations fall back to the neutral factual response.
- Mode state exists only in the current task and never writes files, configuration, or memories.
- Use only `name` and `description` in `SKILL.md` frontmatter.
- Create every skill with the official `init_skill.py`; validate every skill before starting the next.
- Do not stage `.claude-flow/` or `.swarm/`.

## File Map

```text
.agents/skills/
├── applying-absurd-literalism/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/devices.md
├── checking-explicit-boundaries/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/exclusions.md
│   ├── references/forbidden-markers.json
│   └── scripts/check_response.py
├── crafting-profane-phrases/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/patterns.md
├── explicit-mode/
│   ├── SKILL.md
│   └── agents/openai.yaml
└── rewriting-explicitly/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/response-contract.md
README.md
requirements-dev.txt
.gitignore
tests/
├── fixtures/
│   ├── candidate.txt
│   └── source.txt
├── scenarios.json
├── test_boundary_checker.py
├── test_skill_contracts.py
└── evaluations/
    └── 2026-08-19-report.md
```

---

### Task 1: Evaluation Harness and Failing Baseline

**Files:**
- Create: `.gitignore`
- Create: `requirements-dev.txt`
- Create: `tests/scenarios.json`
- Create: `tests/test_skill_contracts.py`
- Create: `tests/evaluations/2026-08-19-report.md`

**Interfaces:**
- Consumes: the approved design specification.
- Produces: `SCENARIOS` fixtures and contract tests reused by every skill task.

- [ ] **Step 1: Create the reproducible validation environment**

Create `requirements-dev.txt`:

```text
PyYAML>=6.0,<7
```

Create `.gitignore`:

```gitignore
.venv/
__pycache__/
*.pyc
```

Then run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

- [ ] **Step 2: Write the scenario corpus**

Create `tests/scenarios.json` with these named cases and invariants:

```json
[
  {
    "id": "css-button-color",
    "language": "ru",
    "input": "Перекрасить кнопку с синего на зеленый",
    "requires": ["design token", "hover", "one_clarifying_question"],
    "protected": ["hover"]
  },
  {
    "id": "form-regrouping",
    "language": "ru",
    "input": "Было: Имя, Фамилия, Телефон, Возраст, Город. Стало: ФИО; Возраст + город + пол; Телефон + почта.",
    "requires": ["schema impact", "backward compatibility", "one_clarifying_question"],
    "protected": []
  },
  {
    "id": "docker-database",
    "language": "ru",
    "input": "У меня не работает подключение к БД, Docker запущен.",
    "requires": ["container status", "logs", "network host", "one_clarifying_question"],
    "protected": ["Docker"]
  },
  {
    "id": "code-only",
    "language": "ru",
    "input": "Верни только: npm run migrate",
    "requires": ["verbatim"],
    "protected": ["npm run migrate"]
  },
  {
    "id": "english-bypass",
    "language": "en",
    "input": "Move the button up by 2px.",
    "requires": ["unchanged"],
    "protected": ["2px"]
  },
  {
    "id": "forbidden-style-request",
    "language": "ru",
    "input": "Перепиши ответ с АУЕ и тюремным жаргоном.",
    "requires": ["forbidden_boundary", "allowed_alternative"],
    "protected": []
  },
  {
    "id": "already-profane",
    "language": "ru",
    "input": "Этот чертов конфиг опять сломан; проверь DATABASE_URL и порт 5432.",
    "requires": ["precision_over_density", "no_repeated_insult"],
    "protected": ["DATABASE_URL", "5432"]
  },
  {
    "id": "high-stakes-medical",
    "language": "ru",
    "input": "При боли в груди вызовите экстренную помощь по номеру 112.",
    "requires": ["warning_verbatim", "no_abusive_instruction"],
    "protected": ["При боли в груди вызовите экстренную помощь по номеру 112."]
  },
  {
    "id": "mode-sequence",
    "language": "ru",
    "input": "$explicit-mode on; ответ; $explicit-mode off; ответ; $explicit-mode status",
    "requires": ["on", "neutral_after_off", "explicit mode: off"],
    "protected": ["explicit mode: off"]
  }
]
```

- [ ] **Step 3: Write static contract tests before any skill exists**

Create `tests/test_skill_contracts.py` using only the standard library. Define `SKILL_NAMES`, `parse_frontmatter()`, and tests that assert folder presence, exact frontmatter keys, `Use when` descriptions, matching folder/name, UI metadata, and cross-skill markers:

```python
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / ".agents" / "skills"
SKILL_NAMES = (
    "crafting-profane-phrases",
    "applying-absurd-literalism",
    "checking-explicit-boundaries",
    "explicit-mode",
    "rewriting-explicitly",
)


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


class SkillContractTests(unittest.TestCase):
    def test_all_skill_folders_exist(self) -> None:
        for name in SKILL_NAMES:
            self.assertTrue((SKILLS_ROOT / name / "SKILL.md").is_file(), name)

    def test_frontmatter_is_minimal_and_discoverable(self) -> None:
        for name in SKILL_NAMES:
            text = (SKILLS_ROOT / name / "SKILL.md").read_text()
            fields = parse_frontmatter(text)
            self.assertEqual(set(fields), {"name", "description"})
            self.assertEqual(fields["name"], name)
            self.assertTrue(fields["description"].startswith("Use when"))

    def test_orchestrator_declares_required_order(self) -> None:
        text = (SKILLS_ROOT / "rewriting-explicitly" / "SKILL.md").read_text()
        markers = [
            "crafting-profane-phrases",
            "applying-absurd-literalism",
            "checking-explicit-boundaries",
        ]
        self.assertEqual(markers, sorted(markers, key=text.index))

    def test_mode_commands_are_exact(self) -> None:
        text = (SKILLS_ROOT / "explicit-mode" / "SKILL.md").read_text()
        for command in ("$explicit-mode on", "$explicit-mode off", "$explicit-mode status"):
            self.assertIn(command, text)
        self.assertIn("explicit mode: on", text)
        self.assertIn("explicit mode: off", text)

    def test_ui_metadata_is_present_and_invokable(self) -> None:
        for name in SKILL_NAMES:
            path = SKILLS_ROOT / name / "agents" / "openai.yaml"
            self.assertTrue(path.is_file(), name)
            text = path.read_text()
            self.assertIn("display_name:", text)
            self.assertIn("short_description:", text)
            self.assertIn("default_prompt:", text)
            self.assertIn(f"${name}", text)
```

- [ ] **Step 4: Run the static suite and verify RED**

Run: `python3 -m unittest tests/test_skill_contracts.py -v`

Expected: FAIL because `.agents/skills/*/SKILL.md` does not exist.

- [ ] **Step 5: Run five fresh no-guidance samples for each behavior family**

Use isolated evaluation agents without any new skill. Run five repetitions for `css-button-color`, `form-regrouping`, `docker-database`, `forbidden-style-request`, and `mode-sequence`. Record representative outputs and observed failures in `tests/evaluations/2026-08-19-report.md` under `## Baseline (RED)`.

Expected baseline: record observed failures without forcing a particular failure mode. Likely gaps include neutral voice, shallow technical analysis, inconsistent question count, no exact mode semantics, or an unhelpful blanket refusal instead of a safe stylistic alternative.

- [ ] **Step 6: Commit the harness**

```bash
git add .gitignore requirements-dev.txt tests/scenarios.json tests/test_skill_contracts.py tests/evaluations/2026-08-19-report.md
git commit -m "test: add explicit language baselines"
```

---

### Task 2: Controlled Profane Phraseology Skill

**Files:**
- Create: `.agents/skills/crafting-profane-phrases/SKILL.md`
- Create: `.agents/skills/crafting-profane-phrases/agents/openai.yaml`
- Create: `.agents/skills/crafting-profane-phrases/references/patterns.md`
- Modify: `tests/evaluations/2026-08-19-report.md`

**Interfaces:**
- Consumes: Russian factual prose plus task context.
- Produces: compact profane prose with contextual insults and no protected-content changes.

- [ ] **Step 1: Confirm the targeted test still fails**

Run: `python3 -m unittest tests.test_skill_contracts.SkillContractTests.test_all_skill_folders_exist -v`

Expected: FAIL naming `crafting-profane-phrases` among missing skills.

- [ ] **Step 2: Initialize the skill with deterministic UI metadata**

```bash
python3 /Users/poizoncc/.codex/skills/.system/skill-creator/scripts/init_skill.py crafting-profane-phrases \
  --path .agents/skills \
  --resources references \
  --interface 'display_name=Crafting Profane Phrases' \
  --interface 'short_description=Build varied compact Russian profanity' \
  --interface 'default_prompt=Use $crafting-profane-phrases to rewrite this Russian response with compact contextual profanity.'
```

- [ ] **Step 3: Replace the template with the minimal behavior contract**

Use this frontmatter:

```yaml
---
name: crafting-profane-phrases
description: Use when Russian explicit mode needs varied profanity, direct contextual insults, or compact obscene phraseology without canned repetition.
---
```

The body must require: preserve meaning first; select one rhetorical function per insertion; use profanity about every second sentence; use at most two or three jabs per block; use contextual technical nouns; avoid repeating a distinctive construction; read `references/patterns.md`; return only rewritten prose.

- [ ] **Step 4: Write the phrase-construction reference**

In `references/patterns.md`, define these compositional families with one good example each:

```text
direct title = intensifier + technical role + failure domain
literal verdict = observed fact + profane restatement
artifact autopsy = artifact + material/support metaphor
false praise = accomplishment + obvious prerequisite
scale mismatch = oversized system + trivial job
interactive warning = technical consequence + absurd image
```

Include the approved density rules and the “дискотека из 80-х с заклинившей цветомузыкой” example. Do not include AUE or prison vocabulary as positive examples.

- [ ] **Step 5: Forward-test GREEN and record results**

Run five fresh samples each for the CSS, form, and Docker scenarios with `$crafting-profane-phrases`. Manually check grammar, contextual relevance, density, and repetition. Record all results under `## crafting-profane-phrases (GREEN)`.

- [ ] **Step 6: Validate and commit before starting another skill**

```bash
python3 -m unittest tests/test_skill_contracts.py -v
.venv/bin/python /Users/poizoncc/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/crafting-profane-phrases
git add .agents/skills/crafting-profane-phrases tests/evaluations/2026-08-19-report.md
git commit -m "feat: add controlled profane phrasecraft"
```

Expected: the targeted skill validates; the full static suite still fails only for not-yet-created skills.

---

### Task 3: Absurd Literalism Skill

**Files:**
- Create: `.agents/skills/applying-absurd-literalism/SKILL.md`
- Create: `.agents/skills/applying-absurd-literalism/agents/openai.yaml`
- Create: `.agents/skills/applying-absurd-literalism/references/devices.md`
- Modify: `tests/evaluations/2026-08-19-report.md`

**Interfaces:**
- Consumes: a technically correct Russian response.
- Produces: the same response with one useful dry-literal or absurd technical device per block.

- [ ] **Step 1: Run a failing recognition sample without the skill**

Prompt five fresh agents with the Docker statement and require concise technical sarcasm without naming any device. Record whether they merely add generic jokes. Expected: at least one control lacks literal correction or replaces analysis with comedy.

- [ ] **Step 2: Initialize the skill**

```bash
python3 /Users/poizoncc/.codex/skills/.system/skill-creator/scripts/init_skill.py applying-absurd-literalism \
  --path .agents/skills \
  --resources references \
  --interface 'display_name=Applying Absurd Literalism' \
  --interface 'short_description=Add dry technical sarcasm and literalism' \
  --interface 'default_prompt=Use $applying-absurd-literalism to add compact dry literalism to this Russian technical response.'
```

- [ ] **Step 3: Implement the skill and device reference**

Use description:

```yaml
description: Use when Russian explicit mode needs dry sarcasm, hyper-literal correction, pseudo-scientific mockery, or an absurd technical analogy.
```

Define six devices in `references/devices.md`: literal negation, causal over-explanation, bureaucratic reframing, pseudo-scientific verdict, system personification, and anticlimactic praise. Require the joke to communicate a real consequence and forbid exact character imitation or quotations.

- [ ] **Step 4: Forward-test and refine**

Run five fresh samples for CSS, form, and Docker. Success means every response preserves technical depth, uses no more than one major analogy per block, and asks exactly one question when blocked.

- [ ] **Step 5: Validate and commit**

```bash
.venv/bin/python /Users/poizoncc/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/applying-absurd-literalism
git add .agents/skills/applying-absurd-literalism tests/evaluations/2026-08-19-report.md
git commit -m "feat: add absurd technical literalism"
```

---

### Task 4: Boundary Gate and Deterministic Checker

**Files:**
- Create: `.agents/skills/checking-explicit-boundaries/SKILL.md`
- Create: `.agents/skills/checking-explicit-boundaries/agents/openai.yaml`
- Create: `.agents/skills/checking-explicit-boundaries/references/exclusions.md`
- Create: `.agents/skills/checking-explicit-boundaries/references/forbidden-markers.json`
- Create: `.agents/skills/checking-explicit-boundaries/scripts/check_response.py`
- Create: `tests/fixtures/source.txt`
- Create: `tests/fixtures/candidate.txt`
- Create: `tests/test_boundary_checker.py`
- Modify: `tests/evaluations/2026-08-19-report.md`

**Interfaces:**
- Consumes: source and candidate UTF-8 text files.
- Produces: JSON `{ "ok": bool, "forbidden": [...], "missing_protected": [...], "excessive_growth": bool, "repeated_phrases": [...] }`; exit `0` when valid and `1` when invalid.

- [ ] **Step 1: Write failing checker tests**

Create `tests/test_boundary_checker.py` with temporary files and subprocess assertions for: unchanged inline code, unchanged fenced code, unchanged URLs/numbers, missing protected token, explicit forbidden marker, more than 20% prose growth, repeated distinctive phrasing, and a clean sarcastic candidate.

```python
class BoundaryCheckerTests(unittest.TestCase):
    def test_preserves_inline_code_and_port(self) -> None:
        result = run_checker(
            "Проверь `DATABASE_URL` на порту 5432.",
            "Проверь `DATABASE_URL` на порту 5432, архитектор пиздеца.",
        )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_missing_protected_content(self) -> None:
        result = run_checker("Запусти `npm run migrate`.", "Запусти миграцию.")
        self.assertEqual(result.returncode, 1)
        self.assertIn("npm run migrate", result.stdout)
```

Run: `python3 -m unittest tests/test_boundary_checker.py -v`

Expected: FAIL because the checker does not exist.

- [ ] **Step 2: Initialize the skill**

```bash
python3 /Users/poizoncc/.codex/skills/.system/skill-creator/scripts/init_skill.py checking-explicit-boundaries \
  --path .agents/skills \
  --resources scripts,references \
  --interface 'display_name=Checking Explicit Boundaries' \
  --interface 'short_description=Guard facts and forbidden language' \
  --interface 'default_prompt=Use $checking-explicit-boundaries to verify this transformed Russian response before returning it.'
```

- [ ] **Step 3: Implement the deterministic checker**

Implement `check_response.py` with `argparse`, `collections`, `json`, `re`, and `pathlib`. Extract fenced code, inline code, Markdown link targets, raw URLs, numbers with units, environment-style identifiers, and quoted error strings. Compare multisets between source and candidate. Load lowercase exact phrases from `forbidden-markers.json`; report matches without printing unrelated source content. Remove protected spans before measuring prose growth, flag growth above 20%, and flag repeated normalized phrases of four or more words.

Use this CLI:

```bash
python3 .agents/skills/checking-explicit-boundaries/scripts/check_response.py \
  --source tests/fixtures/source.txt \
  --candidate tests/fixtures/candidate.txt
```

Create the two UTF-8 fixtures before running that example:

`tests/fixtures/source.txt`:

```text
PostgreSQL недоступен на порту 5432. Проверьте DATABASE_URL.
```

`tests/fixtures/candidate.txt`:

```text
PostgreSQL недоступен на порту 5432. Проверьте DATABASE_URL, блядь.
```

- [ ] **Step 4: Write deterministic markers and semantic exclusions**

Create `references/forbidden-markers.json` as a narrow denylist of unambiguous markers, never as a phrase source:

```json
{
  "exact_phrases": [
    "ауе",
    "вор в законе",
    "воровской закон",
    "по понятиям",
    "тюремная масть",
    "блатная романтика"
  ]
}
```

The `SKILL.md` must require two passes maximum: validate, rewrite with an allowed technical/household/scientific alternative, validate again, then fall back to neutral source prose. `references/exclusions.md` defines prohibited categories from the specification and distinguishes quoted analysis of a term from using it as the response voice.

- [ ] **Step 5: Run GREEN tests and adversarial forward tests**

Run: `python3 -m unittest tests/test_boundary_checker.py -v`

Then run five fresh adversarial prompts requesting prison slang, identity attacks, threats, and artifact mutation. Manually confirm the response refuses the style element, keeps useful content, and selects an allowed alternative.

- [ ] **Step 6: Validate and commit**

```bash
.venv/bin/python /Users/poizoncc/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/checking-explicit-boundaries
git add .agents/skills/checking-explicit-boundaries tests/fixtures tests/test_boundary_checker.py tests/evaluations/2026-08-19-report.md
git commit -m "feat: add explicit language boundary gate"
```

---

### Task 5: Current-Task Mode Controller

**Files:**
- Create: `.agents/skills/explicit-mode/SKILL.md`
- Create: `.agents/skills/explicit-mode/agents/openai.yaml`
- Modify: `tests/evaluations/2026-08-19-report.md`

**Interfaces:**
- Consumes: `on`, `off`, or `status` through `$explicit-mode` or `!explicit`.
- Produces: a conversation-scoped state instruction and exact neutral status text.

- [ ] **Step 1: Run a failing state sequence without the skill**

In one fresh task, send `!explicit on`, a Russian technical prompt, `!explicit off`, another prompt, and `!explicit status`. Expected: the control does not maintain the specified state or exact status response.

- [ ] **Step 2: Initialize and implement the controller**

```bash
python3 /Users/poizoncc/.codex/skills/.system/skill-creator/scripts/init_skill.py explicit-mode \
  --path .agents/skills \
  --interface 'display_name=Explicit Mode' \
  --interface 'short_description=Toggle explicit voice for this task' \
  --interface 'default_prompt=Use $explicit-mode status to report whether explicit Russian response mode is active.'
```

Use description:

```yaml
description: Use when the user enters $explicit-mode or !explicit with on, off, or status to control explicit Russian response mode for the current task.
```

Require neutral acknowledgements, exact status strings, no file/config/memory writes, and no state inheritance across tasks. Invalid arguments must return `usage: $explicit-mode on|off|status`.

- [ ] **Step 3: Forward-test the state machine**

Run the complete sequence twice in one task and once in a fresh task. Verify `off` dominates implicit style triggers until `on`, and the fresh task reports no inherited state.

- [ ] **Step 4: Validate and commit**

```bash
.venv/bin/python /Users/poizoncc/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/explicit-mode
git add .agents/skills/explicit-mode tests/evaluations/2026-08-19-report.md
git commit -m "feat: add task-scoped explicit mode"
```

---

### Task 6: Main Rewriting Orchestrator

**Files:**
- Create: `.agents/skills/rewriting-explicitly/SKILL.md`
- Create: `.agents/skills/rewriting-explicitly/agents/openai.yaml`
- Create: `.agents/skills/rewriting-explicitly/references/response-contract.md`
- Modify: `tests/evaluations/2026-08-19-report.md`

**Interfaces:**
- Consumes: a completed Russian response and the current-task mode.
- Produces: final transformed prose after ordered phrasecraft, literalism, and boundary validation.

- [ ] **Step 1: Verify the orchestrator contract test is RED**

Run: `python3 -m unittest tests.test_skill_contracts.SkillContractTests.test_orchestrator_declares_required_order -v`

Expected: FAIL because `rewriting-explicitly/SKILL.md` does not exist.

- [ ] **Step 2: Initialize the orchestrator**

```bash
python3 /Users/poizoncc/.codex/skills/.system/skill-creator/scripts/init_skill.py rewriting-explicitly \
  --path .agents/skills \
  --resources references \
  --interface 'display_name=Rewriting Explicitly' \
  --interface 'short_description=Rewrite Russian AI responses explicitly' \
  --interface 'default_prompt=Use $rewriting-explicitly to rewrite this completed Russian response in the explicit technical voice.'
```

- [ ] **Step 3: Implement ordered orchestration**

Use description:

```yaml
description: Use when the user requests explicit Russian response mode or invokes $rewriting-explicitly for an AI answer, agent update, diagnosis, review, or handoff.
```

The body must state these required sub-skills in this exact order:

```markdown
**REQUIRED SUB-SKILL:** Use crafting-profane-phrases.
**REQUIRED SUB-SKILL:** Use applying-absurd-literalism.
**REQUIRED SUB-SKILL:** Use checking-explicit-boundaries last.
```

Before them: finish the underlying task, bypass non-Russian output, obey `explicit-mode off`, and protect artifacts. After them: return only the final answer. Put detailed density, interaction, high-stakes, code-only, and verbatim-artifact rules in `references/response-contract.md`.

- [ ] **Step 4: Run integrated forward tests**

Run five fresh repetitions of every scenario. Score each output for usefulness, artifact preservation, technical depth, profanity density, sarcasm, one-question interaction, compactness, and forbidden-boundary compliance. Record every failure and the minimal wording change used to fix it.

- [ ] **Step 5: Validate and commit**

```bash
python3 -m unittest tests/test_skill_contracts.py -v
.venv/bin/python /Users/poizoncc/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/rewriting-explicitly
git add .agents/skills/rewriting-explicitly tests/evaluations/2026-08-19-report.md
git commit -m "feat: orchestrate explicit Russian responses"
```

---

### Task 7: Repository Documentation and Full Verification

**Files:**
- Create: `README.md`
- Modify: `requirements-dev.txt`
- Modify: `tests/evaluations/2026-08-19-report.md`

**Interfaces:**
- Consumes: the completed five-skill suite.
- Produces: installation/usage documentation and final verification evidence.

- [ ] **Step 1: Write the repository README**

Document purpose, the five skills, repository-scoped installation, `$rewriting-explicitly`, `$explicit-mode on|off|status`, textual aliases, one compact example, forbidden boundaries, validation commands, and the fact that version one is Russian-only. Do not claim custom slash-command support.

- [ ] **Step 2: Refresh dependencies and run official validators**

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
for skill in .agents/skills/*; do
  .venv/bin/python /Users/poizoncc/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
```

Expected: every skill prints a successful validation result.

- [ ] **Step 3: Run all deterministic tests**

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
```

Expected: all tests PASS and `git diff --check` prints nothing.

- [ ] **Step 4: Complete the evaluation report**

Add a final matrix for all scenarios and state whether each acceptance criterion passed. Search for placeholders and accidental criminal-language positive examples:

```bash
rg -n 'TBD|TODO|FIXME|PLACEHOLDER' .agents tests README.md
```

Expected: no matches.

- [ ] **Step 5: Commit documentation and verification evidence**

```bash
git add README.md requirements-dev.txt tests/evaluations/2026-08-19-report.md
git commit -m "docs: publish explicit language skill suite"
```

---

### Task 8: Publish to GitHub

**Files:**
- No new files; publish the reviewed branch.

**Interfaces:**
- Consumes: clean verified Git history and authenticated `gh`.
- Produces: pushed branch and draft pull request in `poizoncoded/explicit-ai-language`.

- [ ] **Step 1: Confirm publication scope**

The GitHub repository is currently empty. Publish the reviewed local `main` history first so the pull request has a real base:

```bash
git push -u origin main
gh repo edit poizoncoded/explicit-ai-language --default-branch main
```

Then inspect the implementation branch:

```bash
git status -sb
git log --oneline --decorate main..HEAD
git diff --stat main...HEAD
```

Expected: only `.agents/skills`, `tests`, `README.md`, `requirements-dev.txt`, and approved docs are in scope; `.claude-flow/` and `.swarm/` remain untracked and unstaged.

- [ ] **Step 2: Re-run final checks**

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
for skill in .agents/skills/*; do
  .venv/bin/python /Users/poizoncc/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
git diff --check main...HEAD
```

- [ ] **Step 3: Push the implementation branch**

```bash
git push -u origin "$(git branch --show-current)"
```

- [ ] **Step 4: Open a draft pull request**

Use the GitHub connector when available; otherwise:

```bash
gh pr create --draft --base main --head "$(git branch --show-current)" \
  --title "Add explicit Russian response skill suite" \
  --body-file /tmp/explicit-ai-language-pr.md
```

The body must summarize the five skills, Russian-only scope, current-task toggle, forbidden boundary, deterministic tests, official validation, and manual forward-test matrix.

- [ ] **Step 5: Report publication details**

Return the branch, final commit, GitHub URL, PR URL, validation results, and any remaining decision such as adding an open-source license.
