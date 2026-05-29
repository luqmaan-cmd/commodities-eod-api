# Commodities EOD API

A FastAPI microservice for querying end-of-day (EOD) commodities price data from a PostgreSQL database.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   EODHD API     │────▶│   Ingestion VM   │────▶│   PostgreSQL DB     │
│  (Data Source)  │     │  (Scheduled ETL) │     │  (Private IP)       │
└─────────────────┘     └──────────────────┘     └──────────────────┬──┘
                                                          │
                                                          │ VPC Connector
                                                          │ (bls-connector)
                                                          ▼
                                                ┌─────────────────────┐
                                                │   Cloud Run API     │
                                                │   (FastAPI)         │
                                                └─────────────────────┘
                                                          │
                                                          ▼
                                                ┌─────────────────────┐
                                                │   API Consumers     │
                                                │   (External Apps)   │
                                                └─────────────────────┘
```

## Features

- RESTful API for querying commodities EOD data
- Category-based filtering (Energy, Metals, Grains, Softs, Livestock, Other)
- Pagination support for large datasets
- Date range filtering
- API key authentication (header or query parameter)
- OpenAPI/Swagger documentation

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Deployment:** Google Cloud Run
- **Networking:** VPC Connector for private DB access

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- API key for authentication

### Installation

```bash
# Clone the repository
git clone https://github.com/luqmaan-cmd/commodities-eod-api.git
cd commodities-eod-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run the server
uvicorn app.main:app --reload
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DB_HOST` | PostgreSQL host address |
| `DB_PORT` | PostgreSQL port (default: 5432) |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |
| `API_KEY` | API key for authentication |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/commodities/symbols` | List all commodity symbols |
| GET | `/commodities/categories` | List all categories |
| GET | `/commodities/latest` | Latest data for all commodities |
| GET | `/commodities/latest/{symbol}` | Latest data for a single commodity |
| GET | `/commodities/{symbol}` | Historical data for a commodity |
| GET | `/commodities` | All commodities (paginated) |
| POST | `/commodities/query` | Query multiple commodities |
| POST | `/commodities/sql` | Execute read-only SQL query |

### Authentication

All endpoints require an API key via:

**Header:**
```
X-API-Key: YOUR_API_KEY
```

**Query Parameter:**
```
?api_key=YOUR_API_KEY
```

### Example Requests

```bash
# Get all categories
curl -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/categories"

# Get latest data for all metals
curl -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/latest?category=Metals"

# Get historical data for Crude Oil
curl -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/CL?start_date=2024-01-01&end_date=2024-12-31"

# Query multiple commodities
curl -X POST \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["CL", "GC", "SI"]}' \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/query"
```

## Available Commodities

| # | Name | Ticker | Category |
|---|------|--------|----------|
| 1 | Aluminum | ALI | Metals |
| 2 | Brent Crude Oil | BZ | Energy |
| 3 | Class III Milk | DC | Livestock |
| 4 | Class IV Milk | GDK | Livestock |
| 5 | Cobalt | CB | Metals |
| 6 | Cocoa | CC | Softs |
| 7 | Coffee | KC | Softs |
| 8 | Copper | HG | Metals |
| 9 | Corn | ZC | Grains |
| 10 | Cotton | CT | Softs |
| 11 | Crude Oil (WTI) | CL | Energy |
| 12 | Crude Palm Oil | CPO | Softs |
| 13 | Dry Whey | DY | Livestock |
| 14 | Ethanol | EBM | Energy |
| 15 | Ethanol (CBOT) | EH | Energy |
| 16 | Ethanol (CME) | EMA | Energy |
| 17 | Feeder Cattle | FC | Livestock |
| 18 | Gas Oil | LGOc3 | Energy |
| 19 | Gold | GC | Metals |
| 20 | Heating Oil | HO | Energy |
| 21 | Hot Rolled Coil Steel | HRC | Metals |
| 22 | Iron Ore | TIO | Metals |
| 23 | Lean Hogs | HE | Livestock |
| 24 | Live Cattle | LE | Livestock |
| 25 | Lumber | LBR | Other |
| 26 | NC Feeder Cattle | NCFY | Livestock |
| 27 | Natural Gas | NG | Energy |
| 28 | Nickel | NICKEL | Metals |
| 29 | Oats | O | Grains |
| 30 | Orange Juice | OJ | Softs |
| 31 | Palladium | PA | Metals |
| 32 | Platinum | PL | Metals |
| 33 | RBOB Gasoline | RB | Energy |
| 34 | Rough Rice | ZR | Grains |
| 35 | Rubber | RU | Softs |
| 36 | Silver | SI | Metals |
| 37 | Soybean Meal | SM | Grains |
| 38 | Soybean Oil | ZL | Grains |
| 39 | Soybeans | ZS | Grains |
| 40 | Sugar | SB | Softs |
| 41 | Wheat | W | Other |
| 42 | Wheat (KCBT) | KE | Grains |

### Category Summary

| Category | Count |
|----------|-------|
| Energy | 9 |
| Metals | 10 |
| Grains | 8 |
| Softs | 7 |
| Livestock | 7 |
| Other | 2 |
| **Total** | **42** |

## Database Schema

```sql
CREATE TABLE commodities_eod (
    date            DATE NOT NULL,
    symbol          VARCHAR(20) NOT NULL,
    name            VARCHAR(100) NOT NULL,
    open            NUMERIC,
    high            NUMERIC,
    low             NUMERIC,
    close           NUMERIC,
    adjusted_close  NUMERIC,
    volume          BIGINT,
    category        VARCHAR(50),
    ingestion_ts    TIMESTAMP,
    PRIMARY KEY (date, symbol)
);
```

## Deployment

### Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy commodities-api \
  --source . \
  --platform managed \
  --region europe-west2 \
  --vpc-connector bls-connector \
  --service-account SERVICE_ACCOUNT_EMAIL \
  --allow-unauthenticated
```

### Requirements

- VPC connector for private database access
- Service account with appropriate permissions
- Environment variables set via Cloud Run

## Project Structure

```
commodities-eod-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── config.py         # Settings and configuration
│   ├── database.py       # Database connection
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── auth.py           # API key authentication
│   ├── sql_validator.py  # SQL query validation
│   └── routes/
│       ├── __init__.py
│       └── commodities.py  # API endpoints
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
├── API_DOCS.md
└── README.md
```

## Interactive Documentation

- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

## License

MIT License
