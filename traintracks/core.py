from enum import Enum, IntEnum, IntFlag, unique
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

    def move(self, row: int, col: int) -> tuple[int, int]:
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

    @classmethod
    def from_chris(cls, name: str) -> "Piece":
        return {
            "SW": Piece.SW,
            "EW": Piece.EW,
            "SE": Piece.SE,
            "NW": Piece.NW,
            "NS": Piece.NS,
            "NE": Piece.NE,
        }[name]

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


@unique
class PuzzleFormat(str, Enum):
    PIPES = "pipes"
    CHRIS = "chris"


@dataclass
class Puzzle:
    grid_size: int
    col_totals: list[int]
    row_totals: list[int]
    start_row: int
    end_col: int
    start_positions: dict[tuple[int, int], Piece]
    name: str = ""

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
    def parse(cls, raw: str, format: PuzzleFormat) -> "Puzzle":
        if format == PuzzleFormat.PIPES:
            return cls.parse_pipes(raw)
        else:
            return cls.parse_chris(raw)

    @classmethod
    def parse_pipes(cls, raw: str) -> "Puzzle":
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
            grid_size, col_totals, row_totals, start_row, end_col, start_positions, name
        )

    @classmethod
    def parse_chris(cls, raw: str) -> "Puzzle":
        parts = raw.split("-")
        pieces = parts[-1].split(".")
        start_row = 8 - int(parts[0][0])
        end_col = int(parts[0][1]) - 1
        return cls(
            grid_size=8,
            col_totals=[int(t) for t in parts[1]],
            row_totals=[int(t) for t in parts[2]],
            start_row=start_row,
            end_col=end_col,
            start_positions={(start_row, 0): Piece.EW, (7, end_col): Piece.NS}
            | {(8 - int(p[1]), int(p[0]) - 1): Piece.from_chris(p[2:]) for p in pieces},
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
