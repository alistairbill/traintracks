import itertools
import random
from typing import Optional
import z3
from traintracks.core import Direction, Piece, Puzzle, PuzzleSolution
from traintracks.constraints import Constraints


class Generator(Constraints):
    def __init__(self, grid_size: int, name: str = "gen"):
        start_row = random.randrange(1, grid_size - 1)
        end_col = random.randrange(1, grid_size - 1)
        start_pieces = [k for k in Piece if k & Direction.WEST != 0]
        end_pieces = [k for k in Piece if k & Direction.SOUTH != 0]
        start_positions = {
            (start_row, 0): random.choice(start_pieces),
            (grid_size - 1, end_col): random.choice(end_pieces),
        }
        for _ in range(0, random.randrange(1, 5)):
            row = random.randrange(1, grid_size - 1)
            col = random.randrange(1, grid_size - 1)
            start_positions[(row, col)] = random.choice(list(Piece))

        super().__init__(
            Puzzle(
                grid_size,
                [],
                [],
                start_row,
                end_col,
                start_positions,
                name,
            )
        )
        self.solver.add(self.max_line_constraints())

    def max_line_constraints(self) -> list[z3.BoolRef]:
        return [
            con
            for line in itertools.chain(zip(*self.grid), self.grid)
            for con in (
                z3.PbLe([(cell != 0, 1) for cell in line], 9),
                z3.PbGe([(cell != 0, 1) for cell in line], 1),
            )
        ]

    def solution(self) -> Optional[PuzzleSolution]:
        sol = super().solution()
        if sol is not None:
            sol.puzzle.row_totals = [
                sum(cell != 0 for cell in row) for row in sol.complete_grid
            ]
            sol.puzzle.col_totals = [
                sum(cell != 0 for cell in col) for col in zip(*sol.complete_grid)
            ]
        return sol
