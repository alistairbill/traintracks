from traintracks.core import *
from tests.consts import CHRIS, PIPES, PUZZLE


def test_parse_chris():
    assert Puzzle.parse_chris(CHRIS) == PUZZLE


def test_parse_pipes():
    assert Puzzle.parse_pipes(PIPES) == PUZZLE


def test_serialise_pipes():
    assert PUZZLE.serialise_pipes() == PIPES
