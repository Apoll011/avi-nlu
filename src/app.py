from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from src.kit import IntentKit
from src.models import Alive, Lang, Route, AppError
from src.config import __version__
from src.utils import get_kit
from src.routes.intent_recognition import intent_router
from src.routes.lang import lang_router
from scalar_fastapi import get_scalar_api_reference

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


def serve(lang: Lang = Lang.EN, host: str = "0.0.0.0", port: int = 1178):
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
