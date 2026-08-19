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
            path = SKILLS_ROOT / name / "SKILL.md"
            self.assertTrue(path.is_file(), name)
            fields = parse_frontmatter(path.read_text(encoding="utf-8"))
            self.assertEqual(set(fields), {"name", "description"})
            self.assertEqual(fields["name"], name)
            self.assertTrue(fields["description"].startswith("Use when"))

    def test_orchestrator_declares_required_order(self) -> None:
        path = SKILLS_ROOT / "rewriting-explicitly" / "SKILL.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        markers = [
            "crafting-profane-phrases",
            "applying-absurd-literalism",
            "checking-explicit-boundaries",
        ]
        self.assertTrue(all(marker in text for marker in markers))
        self.assertEqual(markers, sorted(markers, key=text.index))

    def test_mode_commands_are_exact(self) -> None:
        path = SKILLS_ROOT / "explicit-mode" / "SKILL.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        for command in ("$explicit-mode on", "$explicit-mode off", "$explicit-mode status"):
            self.assertIn(command, text)
        self.assertIn("explicit mode: on", text)
        self.assertIn("explicit mode: off", text)

    def test_ui_metadata_is_present_and_invokable(self) -> None:
        for name in SKILL_NAMES:
            path = SKILLS_ROOT / name / "agents" / "openai.yaml"
            self.assertTrue(path.is_file(), name)
            text = path.read_text(encoding="utf-8")
            self.assertIn("display_name:", text)
            self.assertIn("short_description:", text)
            self.assertIn("default_prompt:", text)
            self.assertIn(f"${name}", text)


if __name__ == "__main__":
    unittest.main()
