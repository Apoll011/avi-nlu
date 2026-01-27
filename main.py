import typer
import os
from src.models import Lang
from src.config import __version__, engine_base_path
from src.app import serve as api_serve
from typing_extensions import Annotated
from src.ui import AVI_BANNER
from click import clear

if not os.path.exists(engine_base_path):
    os.makedirs(engine_base_path)

cli = typer.Typer(add_completion=False)


@cli.command()
def serve(
    lang: Lang = Lang.EN,
    host: Annotated[str, typer.Argument(help="THe host IP.")] = "0.0.0.0",
    port: Annotated[
        int,
        typer.Argument(
            help="The server port. Unless that you edit the port on Avi too, dont change this."
        ),
    ] = 1178,
    verbose: bool = False,
):
    """
    Starts a web api for AVI NLU
    """
    api_serve(lang, host, port, verbose)


@cli.command()
def version(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed version and build information."
    ),
):
    """
    Show AVI NLU version information.
    """
    import platform
    import sys

    if verbose:
        typer.echo("Build Information:")
        typer.echo("  Package: ", nl=False)
        typer.secho("AVI NLU", fg=typer.colors.CYAN)
        typer.echo("  Version: ", nl=False)
        typer.secho(__version__, fg=typer.colors.CYAN)
        typer.echo()
        typer.echo("Runtime Information:")
        typer.echo("  Platform: ", nl=False)
        typer.secho(platform.system().lower(), fg=typer.colors.CYAN)
        typer.echo("  Architecture: ", nl=False)
        typer.secho(platform.machine(), fg=typer.colors.CYAN)
        typer.echo("  Python: ", nl=False)
        typer.secho(
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            fg=typer.colors.CYAN,
        )
        typer.echo()
        typer.echo("For more information, visit: ", nl=False)
        typer.secho("https://github.com/apoll011/AviNLU", fg=typer.colors.CYAN)


if __name__ == "__main__":
    clear()

    typer.secho(AVI_BANNER, fg=typer.colors.CYAN, bold=True)
    typer.echo("  System Version: ", nl=False)
    typer.secho(__version__, fg=typer.colors.CYAN)
    typer.echo("  " + "─" * 46)

    cli()
