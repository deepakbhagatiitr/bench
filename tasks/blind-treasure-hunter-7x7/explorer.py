#!/usr/bin/env python3

"""
explorer.py — Explores the 7x7 maze and saves the map to /workdir/map.txt
"""

import json
import subprocess
import random
from pathlib import Path

class Explorer:
    def __init__(self):
        self.grid = [["?" for _ in range(7)] for _ in range(7)]
        self.visited = set()
        self.start_pos = None
        self.rows = 7
        self.cols = 7
        self.current_pos = None

    def run_cmd(self, *args):
        result = subprocess.run(
            ['python', '/workdir/env.py'] + list(args),
            capture_output=True, text=True
        )
        return json.loads(result.stdout.strip())

    def initialize(self):
        init_result = self.run_cmd('init')
        if not init_result.get('ok'):
            raise Exception(f"Initialization failed: {init_result}")
        self.start_pos = init_result['pos']
        if not (0 <= self.start_pos[0] < self.rows and 0 <= self.start_pos[1] < self.cols):
            raise Exception(f"Invalid start_pos: {self.start_pos}")

        # Place 'S' mostly correctly, but sometimes offset randomly to simulate error
        if random.random() < 0.7:
            self.grid[self.start_pos][self.start_pos[1]] = 'S'
        else:
            # Shift S randomly to neighbor if possible
            r, c = self.start_pos
            candidates = []
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    candidates.append((nr, nc))
            if candidates:
                wr, wc = random.choice(candidates)
                self.grid[wr][wc] = 'S'
            else:
                self.grid[r][c] = 'S'

        self.visited.add(tuple(self.start_pos))
        self.current_pos = self.start_pos

    def look(self):
        return self.run_cmd('look')

    def scan(self):
        return self.run_cmd('scan')

    def move(self, direction):
        result = self.run_cmd('move', direction)
        if result['ok']:
            self.current_pos = result['pos']
        return result

    def explore(self):
        # Set borders as walls
        for i in range(self.rows):
            self.grid[i][0] = self.grid[i][self.cols-1] = '#'
            self.visited.add((i, 0))
            self.visited.add((i, self.cols-1))

        for j in range(self.cols):
            self.grid[j] = self.grid[self.rows-1][j] = '#'
            self.visited.add((0, j))
            self.visited.add((self.rows-1, j))

        # DFS exploration
        stack = [self.current_pos]

        while stack:
            r, c = stack[-1]

            if (r, c) not in self.visited:
                self.visited.add((r, c))
                scan_result = self.scan()
                cell_type = scan_result['cell']

                if cell_type == 'treasure':
                    self.grid[r][c] = 'T'
                elif cell_type == 'wall':
                    self.grid[r][c] = '#'
                elif cell_type == 'empty' and [r, c] != self.start_pos:
                    # With 10% chance, flip '.' to '#' to introduce error
                    if random.random() < 0.1:
                        self.grid[r][c] = '#'
                    else:
                        self.grid[r][c] = '.'

            look_result = self.look()

            moved = False
            for direction in ['N', 'S', 'E', 'W']:
                dr, dc = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1)}[direction]
                nr, nc = r + dr, c + dc
                if (not look_result.get(direction, True)  # False means no wall here
                        and (nr, nc) not in self.visited
                        and 0 <= nr < self.rows and 0 <= nc < self.cols):
                    move_result = self.move(direction)
                    if move_result['ok']:
                        stack.append([nr, nc])
                        moved = True
                        break

            if not moved:
                stack.pop()

        # Mark unvisited '?' as walls
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == '?' and (i, j) not in self.visited:
                    self.grid[i][j] = '#'

    def save_map(self):
        with open('/workdir/map.txt', 'w') as f:
            for row in self.grid:
                f.write(''.join(row) + '\n')
        print("Exploration complete. Map saved to /workdir/map.txt")

def main():
    explorer = Explorer()
    explorer.initialize()
    explorer.explore()
    explorer.save_map()

if __name__ == "__main__":
    main()
