from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
import math

from app.database import get_db
from app.models import CommodityEOD
from app.schemas import (
    CommodityEODResponse,
    CommodityQuery,
    PaginatedResponse,
    HealthResponse,
    SQLQueryRequest,
    SQLQueryResponse
)
from app.auth import verify_api_key
from app.sql_validator import validate_select_query

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(func.now())
        return HealthResponse(status="healthy", database="connected")
    except Exception as e:
        return HealthResponse(status="unhealthy", database=f"error: {str(e)}")


@router.get("/commodities/symbols")
async def get_symbols(db: Session = Depends(get_db)):
    result = db.query(CommodityEOD.symbol).distinct().order_by(CommodityEOD.symbol).all()
    return {"symbols": [r[0] for r in result]}


@router.get("/commodities/categories")
async def get_categories(db: Session = Depends(get_db)):
    result = db.query(CommodityEOD.category).distinct().order_by(CommodityEOD.category).all()
    return {"categories": [r[0] for r in result if r[0]]}


@router.get("/commodities/latest")
async def get_all_latest(category: Optional[str] = None, db: Session = Depends(get_db)):
    base_query = db.query(CommodityEOD)
    if category:
        base_query = base_query.filter(CommodityEOD.category == category)

    subquery = base_query.with_entities(
        CommodityEOD.symbol,
        func.max(CommodityEOD.date).label("max_date")
    ).group_by(CommodityEOD.symbol).subquery()

    result = db.query(CommodityEOD).join(
        subquery,
        and_(
            CommodityEOD.symbol == subquery.c.symbol,
            CommodityEOD.date == subquery.c.max_date
        )
    ).all()

    return [CommodityEODResponse.model_validate(r) for r in result]


@router.get("/commodities/latest/{symbol}", response_model=CommodityEODResponse)
async def get_latest_by_symbol(symbol: str, db: Session = Depends(get_db)):
    result = db.query(CommodityEOD).filter(
        CommodityEOD.symbol == symbol.upper()
    ).order_by(CommodityEOD.date.desc()).first()

    if not result:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")

    return CommodityEODResponse.model_validate(result)


@router.get("/commodities/{symbol}")
async def get_commodity_by_symbol(
    symbol: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(CommodityEOD).filter(CommodityEOD.symbol == symbol.upper())

    if start_date:
        query = query.filter(CommodityEOD.date >= start_date)
    if end_date:
        query = query.filter(CommodityEOD.date <= end_date)

    total = query.count()
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size

    results = query.order_by(CommodityEOD.date.desc()).offset(offset).limit(page_size).all()

    return PaginatedResponse(
        data=[CommodityEODResponse.model_validate(r) for r in results],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages
    )


@router.get("/commodities")
async def get_all_commodities(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(CommodityEOD)

    if start_date:
        query = query.filter(CommodityEOD.date >= start_date)
    if end_date:
        query = query.filter(CommodityEOD.date <= end_date)
    if category:
        query = query.filter(CommodityEOD.category == category)

    total = query.count()
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size

    results = query.order_by(CommodityEOD.date.desc(), CommodityEOD.symbol).offset(offset).limit(page_size).all()

    return PaginatedResponse(
        data=[CommodityEODResponse.model_validate(r) for r in results],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages
    )


@router.post("/commodities/query")
async def query_commodities(
    query: CommodityQuery,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    symbols = [s.upper() for s in query.symbols]
    db_query = db.query(CommodityEOD).filter(CommodityEOD.symbol.in_(symbols))

    if query.start_date:
        db_query = db_query.filter(CommodityEOD.date >= query.start_date)
    if query.end_date:
        db_query = db_query.filter(CommodityEOD.date <= query.end_date)

    total = db_query.count()
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size

    results = db_query.order_by(CommodityEOD.date.desc(), CommodityEOD.symbol).offset(offset).limit(page_size).all()

    return PaginatedResponse(
        data=[CommodityEODResponse.model_validate(r) for r in results],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages
    )


@router.post("/commodities/sql", response_model=SQLQueryResponse)
async def execute_sql_query(
    body: SQLQueryRequest,
    db: Session = Depends(get_db)
):
    validated_query = validate_select_query(body.query)

    try:
        # Set a query timeout to prevent runaway queries
        db.execute(text("SET LOCAL statement_timeout = '30000'"))

        params = body.params or {}
        result = db.execute(text(validated_query), params)

        columns = list(result.keys())
        rows = result.fetchall()

        # Convert row tuples to dicts, serializing non-JSON types
        data = []
        for row in rows:
            row_dict = {}
            for col, val in zip(columns, row):
                if isinstance(val, Decimal):
                    row_dict[col] = float(val)
                elif isinstance(val, datetime):
                    row_dict[col] = val.isoformat()
                elif isinstance(val, date):
                    row_dict[col] = val.isoformat()
                else:
                    row_dict[col] = val
            data.append(row_dict)

        return SQLQueryResponse(
            columns=columns,
            data=data,
            row_count=len(data)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution error: {str(e)}"
        )
