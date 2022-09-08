import itertools
import z3
from traintracks.core import Puzzle
from traintracks.constraints import Constraints


class Solver(Constraints):
    def __init__(self, puzzle: Puzzle):
        super().__init__(puzzle)
        self.solver.add(self.line_constraints())

    def line_constraints(self) -> list[z3.BoolRef]:
        # Each line contains the correct number of pieces
        return [
            z3.PbEq([(cell != 0, 1) for cell in line], total)
            for line, total in itertools.chain(
                zip(zip(*self.grid), self.puzzle.col_totals),
                zip(self.grid, self.puzzle.row_totals),
            )
        ]
