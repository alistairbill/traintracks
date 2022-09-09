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
@click.option(
    "--format",
    default=PuzzleFormat.PIPES,
    type=click.Choice(PuzzleFormat),  #  type: ignore
    help="Puzzle output format.",
)
def generate(output: io.TextIOWrapper, size: int, n: int, format: PuzzleFormat):
    """Generate puzzles."""
    for i in range(n):
        for _ in range(GENERATE_RETRIES):
            sol = Generator(size, f"gen_{size}#{i}").solution()
            if sol is not None:
                output.write(sol.puzzle.serialise(format))
                output.write("\n")
                break
        else:
            click.echo(f"generation of puzzle {i} failed")
            continue


@cli.command()
@click.argument("input", type=click.File("r"))
@click.option(
    "--input-format",
    default=PuzzleFormat.PIPES,
    type=click.Choice(PuzzleFormat),  #  type: ignore
    help="Puzzle input format.",
)
@click.option(
    "--output-format",
    default=PuzzleFormat.PIPES,
    type=click.Choice(PuzzleFormat),  #  type: ignore
    help="Puzzle output format.",
)
def solve(
    input: io.TextIOWrapper, input_format: PuzzleFormat, output_format: PuzzleFormat
):
    """Solve puzzles."""
    for raw in input.read().split(
        "\n\n" if input_format == PuzzleFormat.PIPES else "\n"
    ):
        puzzle = Puzzle.parse(raw, input_format)
        sol = Solver(puzzle).solution()
        if sol is None:
            click.echo(f"{puzzle.name}: no solution found")
        else:
            click.echo(sol.serialise(output_format))
