import time
import lingua_franca
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from src.kit import IntentKit
from src.models import Alive, Lang, Route, AppError
from src.config import __version__
from src.utils import get_kit
from src.routes.intent_recognition import intent_router
from src.routes.lang import lang_router
from scalar_fastapi import get_scalar_api_reference
import typer
from src.ui import AVI_BANNER
import uvicorn

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
    docs_url=None,
    redoc_url=None,
)

app.include_router(intent_router, prefix="/intent_recognition", tags=["intent"])
app.include_router(lang_router, prefix="/lang", tags=["lang"])


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
        },
    )


@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="AvI NLU API",
        scalar_proxy_url="https://proxy.scalar.com",
        hide_models=True,
        expand_all_responses=True,
        expand_all_model_sections=True,
        overrides={
            "theme": "bluePlanet",
            "showToolbar": "localhost",
            "operationTitleSource": "summary",
            "orderSchemaPropertiesBy": "alpha",
            "showOperationId": False,
        },
    )


@app.get("/", name="Route")
async def route() -> Route:
    return Route(name="Avi")


@app.get(
    "/avi/alive",
    name="Check If Alive",
    description="This checks if Avi is running and send the basic values",
)
async def alive(intentKit=Depends(get_kit)) -> Alive:
    return Alive(on=True, intent_kit=intentKit.loaded, version=__version__)


def serve(
    lang: Lang = Lang.EN, host: str = "0.0.0.0", port: int = 1178, verbose: bool = False
):
    """
    Start the AVI NLU server.
    """
    import threading

    try:
        steps = [
            ("Initializing Environment", lambda: None),
            (
                "Loading Intent Engine",
                lambda: setattr(app.state, "intentKit", IntentKit(lang)),
            ),
            (
                f"Configuring Language: {lang.name}",
                lambda: lingua_franca.load_languages(["en", "pt"]),
            ),
            ("Initializing Runtime", lambda: None),
        ]

        for i, (step_name, step_func) in enumerate(steps, 1):
            with typer.progressbar(
                length=1,
                label=f"[{i}/{len(steps)}] {step_name}",
                show_pos=False,
                show_percent=False,
            ) as bar:
                step_func()
                bar.update(1)

        typer.echo()

        def print_server_ready():
            import time

            time.sleep(3)
            typer.echo()
            typer.secho(
                f"Server started on http://{host}:{port}",
                fg=typer.colors.BRIGHT_GREEN,
                bold=True,
            )
            if not verbose:
                typer.secho("Press Ctrl+C to stop", fg=typer.colors.BRIGHT_BLACK)
            typer.echo()

        ready_thread = threading.Thread(target=print_server_ready, daemon=True)
        ready_thread.start()

        # Run uvicorn
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info" if verbose else "error",
            access_log=verbose,
        )

    except KeyboardInterrupt:
        typer.echo("\n")
        typer.secho("Shutdown requested", fg=typer.colors.YELLOW)
        typer.secho("Goodbye.", fg=typer.colors.BRIGHT_CYAN)
        typer.echo()

    except OSError as e:
        if "Address already in use" in str(e):
            typer.echo("\n")
            typer.secho("Error: Port already in use", fg=typer.colors.RED, bold=True)
            typer.echo(f"Try: --port {port + 1}")
            typer.echo()
        else:
            typer.echo("\n")
            typer.secho(f"Error: {str(e)}", fg=typer.colors.RED, bold=True)
            typer.echo()
        raise typer.Exit(code=1)

    except Exception as e:
        typer.echo("\n")
        typer.secho(f"Error: {str(e)}", fg=typer.colors.RED, bold=True)

        if verbose:
            import traceback

            typer.echo()
            traceback.print_exc()

        typer.echo()
        raise typer.Exit(code=1)
