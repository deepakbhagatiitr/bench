import os
import pandas as pd
import json
from apex_arena._types import GradingResult

def grade(transcript: str) -> GradingResult:
    answers_path = "/tests/answers.json"
    solution_path = "/workdir/solution.csv"
    feedbacks = []
    subscores = {}
    weights = {"all_correct": 1.0}
    all_passed = True

    if not os.path.exists(solution_path):
        return GradingResult(score=0.0, subscores={}, weights=weights,
                             feedback="Solution file missing.")

    if not os.path.exists(answers_path):
        return GradingResult(score=0.0, subscores={}, weights=weights,
                             feedback="Answer key missing.")

    with open(answers_path, "r") as f:
        answers_data = json.load(f)

    df = pd.read_csv(solution_path)
    solution_dict = dict(zip(df["question"], df["answer"]))

    for q, expected in answers_data["answers"].items():
        if q not in solution_dict:
            all_passed = False
            feedbacks.append(f"{q}: MISSING")
        elif str(solution_dict[q]).strip() == str(expected).strip():
            feedbacks.append(f"{q}: Correct")
        else:
            all_passed = False
            feedbacks.append(
                f"{q}: Incorrect (Expected {expected}, Got {solution_dict[q]})"
            )

    score = 1.0 if all_passed else 0.0
    subscores["all_correct"] = score

    return GradingResult(score=score, subscores=subscores, weights=weights,
                         feedback="; ".join(feedbacks))
