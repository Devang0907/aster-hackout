from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class RecommendationRequest(BaseModel):
    factory_id: int


class SimulationRequest(BaseModel):
    factory_id: int
    changes: Dict[str, Any] = {}


class Factory(BaseModel):
    name: str
    location: Optional[str] = None
    industry: Optional[str] = None
