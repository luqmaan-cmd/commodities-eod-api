from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List


class CommodityEODResponse(BaseModel):
    date: date
    symbol: str
    name: str
    open: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    close: Optional[Decimal] = None
    adjusted_close: Optional[Decimal] = None
    volume: Optional[int] = None
    category: Optional[str] = None
    ingestion_ts: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommodityQuery(BaseModel):
    symbols: List[str]
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class PaginatedResponse(BaseModel):
    data: List[CommodityEODResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class HealthResponse(BaseModel):
    status: str
    database: str
