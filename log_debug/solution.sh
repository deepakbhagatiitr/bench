#!/bin/bash
python3 - <<'PY'
import pandas as pd
from collections import Counter

logfile = "/workdir/data/server.log"

errors = []
levels = []
warning_users = set()

with open(logfile) as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) < 3:
            continue
        ts = f"{parts[0]} {parts[1]}"
        level = parts[2].strip("[]")
        user_id = None
        for p in parts:
            if p.startswith("user_id="):
                user_id = p.split("=")[1]
        levels.append(level)
        if level == "ERROR":
            errors.append(ts)
        if level == "WARNING" and user_id:
            warning_users.add(user_id)

q1 = len(errors)
q2 = min(errors) if errors else ""
q3 = Counter(levels).most_common(1)[0][0]
q4 = len(warning_users)

df = pd.DataFrame([
    ["Q1", q1],
    ["Q2", q2],
    ["Q3", q3],
    ["Q4", q4]
], columns=["question", "answer"])

df.to_csv("/workdir/solution.csv", index=False)
PY
