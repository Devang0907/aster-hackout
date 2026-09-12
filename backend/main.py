from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import FRONTEND_URL

from api.factories import router as factories_router
from api.emissions import router as emissions_router
from api.recommendations import router as recommendations_router
from api.simulations import router as simulations_router
from api.materials import router as materials_router
from api.energy import router as energy_router
from api.waste import router as waste_router
from api.logistics import router as logistics_router


app = FastAPI(
    title="CarbonWise API",
    description="Backend API for CarbonWise",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


app.include_router(factories_router)
app.include_router(emissions_router)
app.include_router(recommendations_router)
app.include_router(simulations_router)
app.include_router(materials_router)
app.include_router(energy_router)
app.include_router(waste_router)
app.include_router(logistics_router)


@app.get("/")
async def root():

    return {
        "message": "CarbonWise API is running"
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }
