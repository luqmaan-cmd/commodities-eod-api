from fastapi import FastAPI
from app.routes import commodities

app = FastAPI(
    title="Commodities EOD API",
    description="API for querying end-of-day commodities data",
    version="1.0.0"
)

app.include_router(commodities.router)
