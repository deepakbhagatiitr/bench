#!/usr/bin/env python3
"""
env.py — Minimal gridworld API for the agent via bash:
  python /workdir/env.py init
  python /workdir/env.py pos
  python /workdir/env.py move N|S|E|W
  python /workdir/env.py look
  python /workdir/env.py scan
  python /workdir/env.py dims

All outputs are simple, parseable JSON on stdout.
"""

import json
import sys
from pathlib import Path
import random

STATE_PATH = Path("/workdir/state.json")

TRUE_MAP_STR = """\
#######
#S..T.#
#.#.#.#
#...#.#
#T#...#
#..#..#
#######
"""

GRID = [list(line) for line in TRUE_MAP_STR.strip("\n").split("\n")]
ROWS = len(GRID)
COLS = len(GRID[0])

# Find open cells ('.' or 'T') for random start placement
OPEN_CELLS = [(r, c) for r in range(ROWS) for c in range(COLS) if GRID[r][c] in (".", "T")]

DIRS = {
    "N": (-1, 0),
    "S": (1, 0),
    "W": (0, -1),
    "E": (0, 1),
}

def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"pos": None, "inited": False, "orig_cell": None}

def save_state(st):
    STATE_PATH.write_text(json.dumps(st))

def is_wall(r, c):
    return not (0 <= r < ROWS and 0 <= c < COLS) or GRID[r][c] == "#"

def cmd_init():
    st = load_state()
    if not OPEN_CELLS:
        print(json.dumps({"error": "no_open_cells"}))
        return
    # Randomly select start position
    START = random.choice(OPEN_CELLS)
    # Store original cell at new start position
    orig_cell = GRID[START[0]][START[1]]
    # Clear all 'S' from grid
    for r in range(ROWS):
        for c in range(COLS):
            if GRID[r][c] == "S":
                GRID[r][c] = "."
    # Place new 'S'
    GRID[START[0]][START[1]] = "S"
    st["pos"] = list(START)
    st["inited"] = True
    st["orig_cell"] = orig_cell
    save_state(st)
    print(json.dumps({"ok": True, "pos": st["pos"]}))

def cmd_pos():
    st = load_state()
    if not st["inited"]:
        print(json.dumps({"error": "not_inited"}))
        return
    print(json.dumps({"pos": st["pos"]}))

def cmd_dims():
    print(json.dumps({"rows": ROWS, "cols": COLS}))

def cmd_look():
    st = load_state()
    if not st["inited"]:
        print(json.dumps({"error": "not_inited"}))
        return
    r, c = st["pos"]
    out = {}
    for d, (dr, dc) in DIRS.items():
        out[d] = is_wall(r + dr, c + dc)
    print(json.dumps(out))

def cell_kind(ch):
    if ch == "S":
        return "start"
    if ch == "T":
        return "treasure"
    if ch == ".":
        return "empty"
    if ch == "#":
        return "wall"
    return "unknown"

def cmd_scan():
    st = load_state()
    if not st["inited"]:
        print(json.dumps({"error": "not_inited"}))
        return
    r, c = st["pos"]
    ch = GRID[r][c]
    print(json.dumps({"cell": cell_kind(ch), "pos": [r, c]}))

def cmd_move(arg):
    st = load_state()
    if not st["inited"]:
        print(json.dumps({"error": "not_inited"}))
        return
    if arg not in DIRS:
        print(json.dumps({"ok": False, "error": "bad_direction"}))
        return
    r, c = st["pos"]
    dr, dc = DIRS[arg]
    nr, nc = r + dr, c + dc
    if is_wall(nr, nc):
        print(json.dumps({"ok": False, "hit": "wall", "pos": [r, c]}))
        return
    st["pos"] = [nr, nc]
    save_state(st)
    ch = GRID[nr][nc]
    print(json.dumps({"ok": True, "pos": [nr, nc], "cell": cell_kind(ch)}))

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "missing_command"}))
        return
    cmd = sys.argv[1]
    if cmd == "init":
        cmd_init()
    elif cmd == "pos":
        cmd_pos()
    elif cmd == "move":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "missing_direction"}))
        else:
            cmd_move(sys.argv[2])
    elif cmd == "look":
        cmd_look()
    elif cmd == "scan":
        cmd_scan()
    elif cmd == "dims":
        cmd_dims()
    else:
        print(json.dumps({"error": "unknown_command", "cmd": cmd}))

if __name__ == "__main__":
    main()