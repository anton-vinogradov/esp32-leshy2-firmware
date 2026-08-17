from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class TargetReadmeTests(unittest.TestCase):
    def test_target_readmes_are_product_sites_not_review_ledgers(self):
        for readme_name in ("README.md", "README.ru.md"):
            readme = (REPO_ROOT / readme_name).read_text(encoding="utf-8")
            for ledger_prefix in ("DEC-", "REV-", "FND-", "IMP-"):
                self.assertNotIn(ledger_prefix, readme, readme_name)
            for stale_heading in ("## Development state", "## Состояние разработки"):
                self.assertNotIn(stale_heading, readme, readme_name)
            self.assertIn("docs/status/current-state", readme, readme_name)

    def test_target_readmes_keep_the_finished_safety_flow(self):
        required_tokens = {
            "README.md": (
                "flowchart TD",
                "STOP",
                "Controlled Zone",
                "3R/1T2R/2T1R/3T",
                "actual-TX",
                "100 ms",
            ),
            "README.ru.md": (
                "flowchart TD",
                "STOP",
                "Контролируемая зона",
                "3R/1T2R/2T1R/3T",
                "actual-TX",
                "100 мс",
            ),
        }
        for readme_name, tokens in required_tokens.items():
            normalized = " ".join(
                (REPO_ROOT / readme_name).read_text(encoding="utf-8").split()
            )
            for token in tokens:
                self.assertIn(token, normalized, f"{readme_name}: {token}")


if __name__ == "__main__":
    unittest.main()
