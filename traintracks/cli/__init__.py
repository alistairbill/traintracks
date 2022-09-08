import click
import io

from ..__about__ import __version__
from ..core import Puzzle, PuzzleFormat
from ..generator import Generator
from ..solver import Solver

GENERATE_RETRIES = 3


@click.group()
def cli():
    pass


@cli.command()
@click.argument("output", type=click.File("w"))
@click.option("--size", default=8, help="Grid size of each puzzle.")
@click.option("-n", default=1, help="Number of puzzles to generate.")
def generate(output: io.TextIOWrapper, size: int, n: int):
    """Generate puzzles."""
    for i in range(n):
        for _ in range(GENERATE_RETRIES):
            sol = Generator(size, f"gen_{size}#{i}").solution()
            if sol is not None:
                output.write(sol.puzzle.serialise())
                output.write("\n")
                break
        else:
            click.echo(f"generation of puzzle {i} failed")
            continue


@cli.command()
@click.argument("input", type=click.File("r"))
@click.option(
    "--format", default="pipes", type=click.Choice(PuzzleFormat)  #  type: ignore
)
def solve(input: io.TextIOWrapper, format: PuzzleFormat):
    """Solve puzzles."""
    for raw in input.read().split("\n\n" if format == PuzzleFormat.PIPES else "\n"):
        puzzle = Puzzle.parse(raw, format)
        sol = Solver(puzzle).solution()
        if sol is None:
            click.echo(f"{puzzle.name}: no solution found")
        else:
            click.echo(sol.serialise())
