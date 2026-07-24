# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AnalisisImagenes API",
        description=(
            "API de apoyo para analisis dermatologico. "
            "No sustituye el diagnostico medico profesional."
        ),
        version="0.1.0",
    )
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(router)
    return app


app = create_app()
