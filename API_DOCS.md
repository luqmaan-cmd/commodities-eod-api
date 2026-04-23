# Commodities EOD API

## Overview

A FastAPI microservice for querying end-of-day (EOD) commodities price data. This API provides programmatic access to historical and current commodity prices across multiple categories including Energy, Metals, Grains, Softs, and Livestock.

**Data Source:** End-of-day data is ingested from EODHD (End of Day Historical Data) API and stored in a PostgreSQL database.

**Deployment:** Hosted on Google Cloud Run with VPC connectivity to the database.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   EODHD API     │────▶│   Ingestion VM   │────▶│   PostgreSQL DB     │
│  (Data Source)  │     │  (Scheduled ETL) │     │  (Private IP)       │
└─────────────────┘     └──────────────────┘     └──────────────────┬──┘
                                                          │
                                                          │ VPC Connector
                                                          ▼
                                                ┌─────────────────────┐
                                                │   Cloud Run API     │
                                                │   (This Service)    │
                                                └─────────────────────┘
```

## Base URL

```
https://commodities-api-832081557693.europe-west2.run.app
```

## Authentication

All endpoints require an API key. Provide it using one of these methods:

**Option 1: Query Parameter**
```
?api_key=YOUR_API_KEY
```

**Option 2: HTTP Header**
```
X-API-Key: YOUR_API_KEY
```

---

## Endpoints

### Health Check

Check API and database connectivity.

**Request:**
```bash
curl -X GET \
  -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/health"
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

### List All Symbols

Get all available commodity symbols.

**Request:**
```bash
curl -X GET \
  -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/symbols"
```

**Response:**
```json
{
  "symbols": ["ALI", "BZ", "CB", "CC", "CL", "CPO", "CT", "DC", "DY", "EBM", ...]
}
```

---

### List All Categories

Get all available commodity categories.

**Request:**
```bash
curl -X GET \
  -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/categories"
```

**Response:**
```json
{
  "categories": ["Energy", "Grains", "Livestock", "Metals", "Other", "Softs"]
}
```

---

### Latest Data for All Commodities

Get the most recent EOD data for all commodities. Optionally filter by category.

**Request:**
```bash
# All commodities
curl -X GET \
  -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/latest"

# Filtered by category
curl -X GET \
  -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/latest?category=Metals"
```

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| category | string | No | Filter by category: Energy, Metals, Grains, Softs, Livestock, Other |

**Response:**
```json
[
  {
    "date": "2026-04-22",
    "symbol": "CL",
    "name": "Crude Oil (WTI)",
    "open": "92.13",
    "high": "92.13",
    "low": "92.13",
    "close": "92.13",
    "adjusted_close": "92.13",
    "volume": 280762,
    "category": "Energy",
    "ingestion_ts": "2026-04-23T05:00:25.816691"
  },
  {
    "date": "2026-04-22",
    "symbol": "NG",
    "name": "Natural Gas",
    "open": "1.89",
    "high": "1.92",
    "low": "1.87",
    "close": "1.91",
    "adjusted_close": "1.91",
    "volume": 125000,
    "category": "Energy",
    "ingestion_ts": "2026-04-23T05:00:26.123456"
  }
]
```

---

### Latest Data for Single Commodity

Get the most recent EOD data for a specific commodity.

**Request:**
```bash
curl -X GET \
  -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/latest/CL"
```

**Path Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| symbol | string | Yes | Commodity symbol (e.g., CL, GC, SI) |

**Response:**
```json
{
  "date": "2026-04-22",
  "symbol": "CL",
  "name": "Crude Oil (WTI)",
  "open": "92.13",
  "high": "92.13",
  "low": "92.13",
  "close": "92.13",
  "adjusted_close": "92.13",
  "volume": 280762,
  "category": "Energy",
  "ingestion_ts": "2026-04-23T05:00:25.816691"
}
```

---

### Get Commodity History by Symbol

Get historical EOD data for a specific commodity with pagination and date filtering.

**Request:**
```bash
curl -X GET \
  -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/CL?start_date=2024-01-01&end_date=2024-12-31&page=1&page_size=10"
```

**Path Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| symbol | string | Yes | Commodity symbol |

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| start_date | date | No | Start date (YYYY-MM-DD) |
| end_date | date | No | End date (YYYY-MM-DD) |
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 100, max: 1000) |

**Response:**
```json
{
  "data": [
    {
      "date": "2024-12-31",
      "symbol": "CL",
      "name": "Crude Oil (WTI)",
      "open": "71.50",
      "high": "72.30",
      "low": "71.20",
      "close": "71.89",
      "adjusted_close": "71.89",
      "volume": 285000,
      "category": "Energy",
      "ingestion_ts": "2025-01-01T05:00:15.123456"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 250,
  "total_pages": 25
}
```

---

### List All Commodities (Paginated)

Get all EOD data across all commodities with pagination and filtering.

**Request:**
```bash
curl -X GET \
  -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities?category=Energy&page=1&page_size=10"
```

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| start_date | date | No | Start date (YYYY-MM-DD) |
| end_date | date | No | End date (YYYY-MM-DD) |
| category | string | No | Filter by category: Energy, Metals, Grains, Softs, Livestock, Other |
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 100, max: 1000) |

**Response:**
```json
{
  "data": [
    {
      "date": "2026-04-22",
      "symbol": "CL",
      "name": "Crude Oil (WTI)",
      "open": "92.13",
      "high": "92.13",
      "low": "92.13",
      "close": "92.13",
      "adjusted_close": "92.13",
      "volume": 280762,
      "category": "Energy",
      "ingestion_ts": "2026-04-23T05:00:25.816691"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 72944,
  "total_pages": 7295
}
```

---

### Query Multiple Commodities

Query EOD data for multiple symbols in a single request.

**Request:**
```bash
curl -X POST \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["CL", "GC", "SI"], "start_date": "2024-01-01", "end_date": "2024-12-31"}' \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/query?page=1&page_size=10"
```

**Request Body:**
```json
{
  "symbols": ["CL", "GC", "SI"],
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 100, max: 1000) |

**Response:**
```json
{
  "data": [
    {
      "date": "2024-12-31",
      "symbol": "CL",
      "name": "Crude Oil (WTI)",
      "open": "71.50",
      "high": "72.30",
      "low": "71.20",
      "close": "71.89",
      "adjusted_close": "71.89",
      "volume": 285000,
      "category": "Energy",
      "ingestion_ts": "2025-01-01T05:00:15.123456"
    },
    {
      "date": "2024-12-31",
      "symbol": "GC",
      "name": "Gold",
      "open": "2062.50",
      "high": "2070.00",
      "low": "2060.00",
      "close": "2065.30",
      "adjusted_close": "2065.30",
      "volume": 150000,
      "category": "Metals",
      "ingestion_ts": "2025-01-01T05:00:18.654321"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 750,
  "total_pages": 75
}
```

---

## Available Commodities

### Energy
| Symbol | Name |
|--------|------|
| CL | Crude Oil (WTI) |
| NG | Natural Gas |
| BZ | Brent Crude Oil |
| HO | Heating Oil |
| RB | RBOB Gasoline |
| EBM | Ethanol |
| EH | Ethanol (CBOT) |
| EMA | Ethanol (CME) |
| LGOc3 | Gas Oil |

### Metals
| Symbol | Name |
|--------|------|
| GC | Gold |
| SI | Silver |
| HG | Copper |
| PL | Platinum |
| PA | Palladium |
| ALI | Aluminum |
| NICKEL | Nickel |
| CB | Cobalt |
| TIO | Iron Ore |
| HRC | Hot Rolled Coil Steel |

### Grains
| Symbol | Name |
|--------|------|
| ZC | Corn |
| ZS | Soybeans |
| ZW | Wheat |
| KE | Wheat (KCBT) |
| ZL | Soybean Oil |
| SM | Soybean Meal |
| O | Oats |
| ZR | Rough Rice |

### Softs
| Symbol | Name |
|--------|------|
| CC | Cocoa |
| CT | Cotton |
| KC | Coffee |
| OJ | Orange Juice |
| SB | Sugar |
| RU | Rubber |
| CPO | Crude Palm Oil |

### Livestock
| Symbol | Name |
|--------|------|
| LE | Live Cattle |
| HE | Lean Hogs |
| FC | Feeder Cattle |
| DC | Class III Milk |
| GDK | Class IV Milk |
| DY | Dry Whey |
| NCFY | NC Feeder Cattle |

### Other
| Symbol | Name |
|--------|------|
| LBR | Lumber |
| W | Wheat |

---

## Error Responses

### 401 Unauthorized
Missing or invalid authentication.

```json
{
  "detail": "API Key is required (use X-API-Key header or api_key query parameter)"
}
```

**Example:**
```bash
curl -X GET "https://commodities-api-832081557693.europe-west2.run.app/commodities/latest"
# Response: {"detail": "API Key is required (use X-API-Key header or api_key query parameter)"}
```

### 403 Forbidden
Invalid API key provided.

```json
{
  "detail": "Invalid API Key"
}
```

**Example:**
```bash
curl -X GET \
  -H "X-API-Key: invalid_key" \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/latest"
# Response: {"detail": "Invalid API Key"}
```

### 404 Not Found
Requested resource not found.

```json
{
  "detail": "Symbol 'XYZ' not found"
}
```

**Example:**
```bash
curl -X GET \
  -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/latest/XYZ"
# Response: {"detail": "Symbol 'XYZ' not found"}
```

### 500 Internal Server Error
Server-side error (database connectivity, etc.).

```json
{
  "detail": "Internal server error"
}
```

---

## Interactive Documentation

Swagger UI documentation with interactive testing:
```
https://commodities-api-832081557693.europe-west2.run.app/docs
```

ReDoc documentation:
```
https://commodities-api-832081557693.europe-west2.run.app/redoc
```

---

## Rate Limits

No rate limits currently enforced.

---

## Data Freshness

Data is ingested daily from EODHD API. The `ingestion_ts` field in each record indicates when the data was loaded into the database.

---

## Support

For issues or questions, contact the development team.
