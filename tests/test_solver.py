from traintracks.core import Piece, PuzzleFormat
from traintracks.solver import *
from tests.consts import PUZZLE, SOLUTION


def test_solver():
    sol = Solver(PUZZLE).solution()
    assert sol is not None
    assert sol.puzzle == PUZZLE
    assert sol.serialise(PuzzleFormat.PIPES) == SOLUTION
