from datetime import datetime, timedelta

from fastapi import Depends, FastAPI
import typer
import os
import lingua_franca
from src.models import Lang
from src.kit import IntentKit
from src.config import __version__, engine_base_path
from src.utils import get_kit
from typing_extensions import Annotated
from rich.progress import Progress, SpinnerColumn, TextColumn
from src.routes.intent_recognition import intent_router
from src.routes.lang import lang_router

lingua_franca.load_languages(["en", "pt"])

if not os.path.exists(engine_base_path):
    os.makedirs(engine_base_path)

app = FastAPI(
    title="Avi Server",
    version=__version__,
    description="Avi api server that handles complex and heavy tasks such as nlp etc.",
    summary="Avi base server used for handling heavy functions",
    contact={"name": "Tiago Bernardo", "email": "tiagorobotik@gmail.com"},
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

app.include_router(intent_router, prefix="/intent_recognition", tags=["intent"])
app.include_router(lang_router, prefix="/lang", tags=["lang"])

cli = typer.Typer()


@app.get("/", name="Route")
async def route():
    return {"response": {"name": "Avi"}}


@app.get(
    "/avi/alive",
    name="Check If Alive",
    description="This checks if Avi is running and send the basic values",
)
async def alive(intentKit=Depends(get_kit)):
    response = {
        "on": True,
        "kit": {
            "all_on": True and intentKit.loaded,
            "intent": intentKit.loaded,
        },
        "version": __version__,
    }
    return {"response": response}


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
    import uvicorn

    try:
        print("=" * 50)
        print("Press Ctrl+C to stop")
        print("Waiting for application startup.")
        print(f"App started on http://{host}:{port}")
        print("=" * 50)
        app.state.intentKit = IntentKit(lang)
        uvicorn.run(app, host=host, port=port, log_level="warning")

    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        import traceback

        traceback.print_exc()
        input("Press Enter to exit...")


@cli.command()
def version():
    """
    The current Avi Version
    """
    print("AVI NLU v" + __version__)
    print("Made by Tiago Inês, at Embrasse Studio.")


if __name__ == "__main__":
    cli()
