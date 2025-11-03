from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class PriceIn(BaseModel):
    date: datetime
    market: str
    product: str = "Coconut Shell Charcoal"
    price: float
    currency: str = "USD"
    unit: str = "per tonne"
    source_url: Optional[str] = None


class Price(PriceIn):
    id: Optional[str] = Field(default=None, alias="_id")


class StatsRequest(BaseModel):
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    markets: Optional[List[str]] = None


class CompareRequest(BaseModel):
    startA: datetime
    endA: datetime
    startB: datetime
    endB: datetime
    markets: Optional[List[str]] = None
