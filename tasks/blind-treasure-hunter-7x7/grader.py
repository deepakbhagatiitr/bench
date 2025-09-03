from typing import Any, Dict, Optional, List
import json
from pathlib import Path

# Base maze with fixed start position 'S' at [1,1]
BASE_MAZE: List[str] = [
    "#######",
    "#S..T.#",
    "#.#.#.#",
    "#...#.#",
    "#T#...#",
    "#..#..#",
    "#######",
]

GT_ROWS = len(BASE_MAZE)
GT_COLS = len(BASE_MAZE[0]) if GT_ROWS else 0
VALID_CHARS = {"#", ".", "S", "T"}

def _read_candidate_map(path: str = "/workdir/map.txt") -> Optional[List[str]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        return lines
    except FileNotFoundError:
        return None

def _first_diff(gt, cand):
    for r in range(GT_ROWS):
        for c in range(GT_COLS):
            if gt[r][c] != cand[r][c]:
                return (r, c, gt[r][c], cand[r][c])
    return None

class GradingResult:
    def __init__(
        self,
        score: float,
        feedback: str,
        subscores: Optional[Dict[str, float]] = None,
    ):
        self.score = score
        self.feedback = feedback
        self.subscores = subscores or {}
        self.weights = {"all_correct": 1.0}
        self.metadata = {"feedback": feedback}
        self.details = {}

def grade(_=None) -> GradingResult:
    cand = _read_candidate_map("/workdir/map.txt")
    if cand is None:
        return GradingResult(0.0, "Missing /workdir/map.txt")

    if len(cand) != GT_ROWS:
        return GradingResult(0.0, f"Wrong number of rows: expected {GT_ROWS}, got {len(cand)}")

    for i, row in enumerate(cand):
        if len(row) != GT_COLS:
            return GradingResult(0.0, f"Row {i} length mismatch: expected {GT_COLS}, got {len(row)}")
        bad = set(row) - VALID_CHARS
        if bad:
            return GradingResult(0.0, f"Invalid characters in row {i}: {sorted(bad)}")

    # Convert candidate map lines to lists of chars for accurate comparison
    cand_chars = [list(line) for line in cand]

    # Use fixed base maze as ground truth with fixed 'S' at [1,1]
    gt = [list(row) for row in BASE_MAZE]

    gt_str = "\n".join("".join(row) for row in gt)
    cand_str = "\n".join("".join(row) for row in cand_chars)
    feedback = f"Ground truth:\n{gt_str}\nCandidate map:\n{cand_str}"

    if cand_chars == gt:
        return GradingResult(1.0, "Perfect match with fixed ground truth maze", subscores={"all_correct": 1.0})

    diff = _first_diff(gt, cand_chars)
    if diff is None:
        return GradingResult(0.0, f"Map does not match ground truth layout.\n{feedback}")

    r, c, exp, got = diff
    return GradingResult(0.0, f"First mismatch at (row {r}, col {c}): expected '{exp}', got '{got}'\n{feedback}")

if __name__ == "__main__":
    result = grade()
    print(
        json.dumps(
            {
                "score": result.score,
                "feedback": result.feedback,
                "subscores": result.subscores,
                "metadata": result.metadata,
            }
        )
    )
