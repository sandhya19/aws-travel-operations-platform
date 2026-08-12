"""Evaluate a prompt-release candidate against its registered golden dataset."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from travel_operations.evaluations import evaluate_release
from travel_operations.prompts import PromptReleaseRegistry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-id", required=True)
    parser.add_argument("--answers-file", required=True, type=Path)
    arguments = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    release = PromptReleaseRegistry(root).active(arguments.prompt_id)
    dataset = json.loads((root / release.evaluation_dataset).read_text(encoding="utf-8"))
    answers = json.loads(arguments.answers_file.read_text(encoding="utf-8"))
    if not isinstance(dataset, list) or not isinstance(answers, dict):
        raise SystemExit(
            "Dataset must be a list and answers file must be an object keyed by case ID"
        )
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in answers.items()):
        raise SystemExit("Every candidate answer key and value must be a string")
    report = evaluate_release(release, dataset, answers)
    print(json.dumps(asdict(report), indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
