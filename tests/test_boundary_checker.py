from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = (
    ROOT
    / ".agents"
    / "skills"
    / "checking-explicit-boundaries"
    / "scripts"
    / "check_response.py"
)


def run_checker(source: str, candidate: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        source_path = root / "source.txt"
        candidate_path = root / "candidate.txt"
        source_path.write_text(source, encoding="utf-8")
        candidate_path.write_text(candidate, encoding="utf-8")
        return subprocess.run(
            [
                "python3",
                str(CHECKER),
                "--source",
                str(source_path),
                "--candidate",
                str(candidate_path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )


def payload(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return json.loads(result.stdout)


class BoundaryCheckerTests(unittest.TestCase):
    def test_preserves_inline_code_and_port(self) -> None:
        result = run_checker(
            "Сначала проверь `DATABASE_URL` на порту 5432, затем перезапусти приложение.",
            "Сначала проверь `DATABASE_URL` на порту 5432, затем перезапусти приложение, блядь.",
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(payload(result)["ok"])

    def test_preserves_fenced_code(self) -> None:
        source = "Выполни:\n```bash\nnpm run migrate\n```\nПосле запуска проверь статус сервиса."
        result = run_checker(source, source)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_preserves_url_number_and_quoted_error(self) -> None:
        source = 'Открой https://example.com/help и проверь порт 5432: ошибка «connection refused».'
        candidate = 'Проверь https://example.com/help и открой порт 5432: ошибка «connection refused».'
        result = run_checker(source, candidate)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_missing_protected_content(self) -> None:
        result = run_checker("Запусти `npm run migrate`.", "Запусти миграцию.")
        self.assertEqual(result.returncode, 1)
        self.assertIn("npm run migrate", result.stdout)

    def test_rejects_unexpected_protected_content(self) -> None:
        result = run_checker("База слушает порт 5432.", "База слушает порты 5432 и 5433.")
        self.assertEqual(result.returncode, 1)
        self.assertIn("5433", result.stdout)

    def test_rejects_forbidden_marker(self) -> None:
        result = run_checker(
            "Перепиши ответ грубо.",
            "Перепиши ответ с лозунгом АУЕ.",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("ауе", result.stdout.lower())

    def test_allows_unchanged_forbidden_term_in_required_quote(self) -> None:
        source = "Проанализируй цитату «АУЕ» без стилизации."
        result = run_checker(source, source)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_excessive_growth(self) -> None:
        result = run_checker(
            "Проверь конфигурацию сервиса перед запуском миграции сегодня.",
            "Проверь конфигурацию сервиса перед запуском миграции сегодня, а потом устрой длинный бессмысленный монолог про хаос и ошибки.",
        )
        self.assertEqual(result.returncode, 1)
        self.assertTrue(payload(result)["excessive_growth"])

    def test_rejects_new_repeated_phrase(self) -> None:
        result = run_checker(
            "Проверь сеть и повтори запрос после запуска базы.",
            "Проверь сеть. Архитектор сетевого хаоса опять здесь, архитектор сетевого хаоса опять здесь.",
        )
        self.assertEqual(result.returncode, 1)
        self.assertTrue(payload(result)["repeated_phrases"])

    def test_accepts_clean_fixture(self) -> None:
        source = (ROOT / "tests" / "fixtures" / "source.txt").read_text(encoding="utf-8")
        candidate = (ROOT / "tests" / "fixtures" / "candidate.txt").read_text(encoding="utf-8")
        result = run_checker(source, candidate)
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
