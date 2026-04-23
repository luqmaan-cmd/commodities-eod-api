from sqlalchemy import Column, Date, String, Numeric, BigInteger, DateTime
from app.database import Base


class CommodityEOD(Base):
    __tablename__ = "commodities_eod"

    date = Column(Date, primary_key=True, nullable=False)
    symbol = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    open = Column(Numeric, nullable=True)
    high = Column(Numeric, nullable=True)
    low = Column(Numeric, nullable=True)
    close = Column(Numeric, nullable=True)
    adjusted_close = Column(Numeric, nullable=True)
    volume = Column(BigInteger, nullable=True)
    category = Column(String, nullable=True)
    ingestion_ts = Column(DateTime, nullable=True)
