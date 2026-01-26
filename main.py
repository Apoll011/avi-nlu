import typer
import os
import lingua_franca
from src.models import Lang
from src.kit import IntentKit
from src.config import __version__, engine_base_path
from src.app import serve as api_serve
from typing_extensions import Annotated
from rich.progress import Progress, SpinnerColumn, TextColumn

lingua_franca.load_languages(["en", "pt"])

if not os.path.exists(engine_base_path):
    os.makedirs(engine_base_path)

cli = typer.Typer()


@cli.command()
def train(
    lang: Annotated[
        Lang, typer.Argument(help="The language to train the engine with")
    ] = Lang.EN,
):
    """
    Trains the engine on a specified language and saves the engine on the engine data folder
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Training...", total=None)
        IntentKit(lang).train()


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
):
    """
    Starts a web api for AVI NLU
    """
    api_serve(lang, host, port)


@cli.command()
def version():
    """
    The current Avi Version
    """
    print("AVI NLU v" + __version__)
    print("Made by Tiago Inês, at Embrasse Studio.")


if __name__ == "__main__":
    cli()
