from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Corridor")

    api = APIRouter(prefix="/api")
    # Feature routers are included on `api` here (health arrives in Task 4).
    app.include_router(api)

    return app


app = create_app()
