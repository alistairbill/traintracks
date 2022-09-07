from enum import IntEnum, IntFlag
from dataclasses import dataclass
from copy import copy


class Direction(IntFlag):
    NORTH = 8
    EAST = 4
    SOUTH = 2
    WEST = 1

    def opposite(self) -> "Direction":
        return {
            Direction.NORTH: Direction.SOUTH,
            Direction.EAST: Direction.WEST,
            Direction.SOUTH: Direction.NORTH,
            Direction.WEST: Direction.EAST,
        }[self]

    def increment(self, row: int, col: int) -> tuple[int, int]:
        return {
            Direction.NORTH: (row - 1, col),
            Direction.EAST: (row, col + 1),
            Direction.SOUTH: (row + 1, col),
            Direction.WEST: (row, col - 1),
        }[self]


class Piece(IntEnum):
    EMPTY = 0
    SW = Direction.SOUTH | Direction.WEST
    EW = Direction.EAST | Direction.WEST
    SE = Direction.SOUTH | Direction.EAST
    NW = Direction.NORTH | Direction.WEST
    NS = Direction.NORTH | Direction.SOUTH
    NE = Direction.NORTH | Direction.EAST

    @classmethod
    def from_pipe(cls, pipe: str) -> "Piece":
        return {
            ".": Piece.EMPTY,
            "┓": Piece.SW,
            "━": Piece.EW,
            "┏": Piece.SE,
            "┛": Piece.NW,
            "┃": Piece.NS,
            "┗": Piece.NE,
        }[pipe]

    def to_pipe(self) -> str:
        return {
            Piece.EMPTY: ".",
            Piece.SW: "┓",
            Piece.EW: "━",
            Piece.SE: "┏",
            Piece.NW: "┛",
            Piece.NS: "┃",
            Piece.NE: "┗",
        }[self]


@dataclass
class Puzzle:
    name: str
    grid_size: int
    col_totals: list[int]
    row_totals: list[int]
    start_row: int
    end_col: int
    start_positions: dict[tuple[int, int], Piece]

    def serialise(self) -> str:
        res = self.name + "\n"
        res += " "
        res += "".join(map(str, self.col_totals)) + "\n"
        for r in range(self.grid_size):
            res += "A" if r == self.start_row else " "
            for c in range(self.grid_size):
                piece = self.start_positions.get((r, c), Piece(0))
                res += piece.to_pipe()
            res += str(self.row_totals[r]) + "\n"
        res += " " * (self.end_col + 1) + "B\n"
        return res

    @classmethod
    def parse(cls, raw: str) -> "Puzzle":
        lines = raw.splitlines()
        name = lines[0]
        col_totals = [int(c) for c in lines[1][1:]]
        grid_size = len(col_totals)
        row_totals = [0] * grid_size
        start_row = 0
        start_positions = {}
        for r, row in enumerate(lines[2:-1]):
            if row[0] == "A":
                start_row = r
            row_totals[r] = int(row[-1])
            for c, col in enumerate(row[1]):
                if col != ".":
                    start_positions[(r, c)] = Piece.from_pipe(col)
        end_col = lines[-1].index("B") - 1
        return cls(
            name, grid_size, col_totals, row_totals, start_row, end_col, start_positions
        )


@dataclass
class PuzzleSolution:
    puzzle: Puzzle
    complete_grid: list[list[Piece]]

    def serialise(self) -> str:
        # slight hack: make every piece a starting piece
        puzzle = copy(self.puzzle)
        puzzle.start_positions = {
            (r, c): val
            for r, row in enumerate(self.complete_grid)
            for c, val in enumerate(row)
        }
        return puzzle.serialise()
