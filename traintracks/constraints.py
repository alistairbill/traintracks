import itertools
from typing import Optional
import z3
from traintracks.core import Direction, Piece, Puzzle, PuzzleSolution


class Constraints:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.solver = z3.Solver()
        self.grid = [
            [z3.BitVec(f"grid_{r}_{c}", 4) for c in range(self.puzzle.grid_size)]
            for r in range(self.puzzle.grid_size)
        ]
        self.path_order = [
            [z3.Int(f"path_{r}_{c}") for c in range(self.puzzle.grid_size)]
            for r in range(self.puzzle.grid_size)
        ]
        self.solver.add(
            self.piece_constraints()
            + self.path_constraints()
            + self.connected_constraints()
            + self.starting_constraints()
        )

    def solution(self) -> Optional[PuzzleSolution]:
        if self.solver.check() != z3.sat:
            return None
        model = self.solver.model()
        complete_grid = [[Piece(model.eval(cell).as_long()) for cell in row] for row in self.grid]  # type: ignore
        return PuzzleSolution(self.puzzle, complete_grid)

    def piece_constraints(self) -> list[z3.BoolRef]:
        return [
            z3.Or([cell == int(key) for key in Piece])  #  type: ignore
            for row in self.grid
            for cell in row
        ]

    def path_constraints(self) -> list[z3.BoolRef]:
        # to disallow loops each grid cell is given an integer which
        # increments along the path
        distinct = [z3.Distinct([cell for row in self.path_order for cell in row])]
        n_cells = len(self.grid) * len(self.grid[0])
        bounds: list[z3.BoolRef] = [  # type: ignore
            z3.And(cell >= -n_cells, cell <= n_cells)
            for row in self.path_order
            for cell in row
        ]
        populated: list[z3.BoolRef] = [  # type: ignore
            z3.If(cell == 0, path_index < 0, path_index > 0)
            for row_g, row_p in zip(self.grid, self.path_order)
            for cell, path_index in zip(row_g, row_p)
        ]
        return distinct + bounds + populated

    def starting_constraints(self) -> list[z3.BoolRef]:
        start_positions: list[z3.BoolRef] = [
            self.grid[r][c] == int(val)  #  type: ignore
            for (r, c), val in self.puzzle.start_positions.items()
        ]
        start_min: list[z3.BoolRef] = [
            self.path_order[self.puzzle.start_row][0] == 1  #  type: ignore
        ]
        end_max = [
            cell <= self.path_order[-1][self.puzzle.end_col]
            for row in self.path_order
            for cell in row
        ]
        return start_positions + start_min + end_max

    def connected_constraints(self) -> list[z3.BoolRef]:
        res = []
        max_index = self.puzzle.grid_size - 1
        for r, c in itertools.product(
            range(self.puzzle.grid_size),
            range(self.puzzle.grid_size),
        ):
            for cond, alt_cond, direction in [
                (r > 0, True, Direction.NORTH),
                (c < max_index, True, Direction.EAST),
                (r < max_index, c != self.puzzle.end_col, Direction.SOUTH),
                (c > 0, r != self.puzzle.start_row, Direction.WEST),
            ]:
                if cond:
                    nr, nc = direction.move(r, c)
                    res.append(
                        z3.Implies(
                            self.grid[r][c] & int(direction) != 0,
                            z3.And(
                                self.grid[nr][nc] & int(direction.opposite()) != 0,
                                z3.Or(
                                    self.path_order[r][c]
                                    == self.path_order[nr][nc] - 1,
                                    self.path_order[r][c]
                                    == self.path_order[nr][nc] + 1,
                                ),
                            ),
                        )
                    )
                elif alt_cond:
                    res.append(self.grid[r][c] & int(direction) == 0)
        return res
