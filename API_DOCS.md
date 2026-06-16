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

## Version

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | Current | Initial release — all endpoints, API key auth, SQL query support |

---

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

> **Note:** Symbol path parameters are case-insensitive. For example, `cl`, `Cl`, and `CL` all resolve to the same commodity.

---

## Endpoints

### Health Check

Check API and database connectivity.

**HTTPS:** `https://commodities-api-832081557693.europe-west2.run.app/health?api_key=YOUR_API_KEY`

**Request:**
```bash
curl -X GET \
  -H "X-API-Key: YOUR_API_KEY" \
  "https://commodities-api-832081557693.europe-west2.run.app/health"
```

**Response (healthy):**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Response (unhealthy):**
```json
{
  "status": "unhealthy",
  "database": "error: <error message>"
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| status | string | `"healthy"` or `"unhealthy"` |
| database | string | `"connected"` on success, or `"error: <message>"` on failure |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success (returns healthy or unhealthy status) |
| 401 | Missing API key |
| 403 | Invalid API key |

---

### List All Symbols

Get all available commodity symbols.

**HTTPS:** `https://commodities-api-832081557693.europe-west2.run.app/commodities/symbols?api_key=YOUR_API_KEY`

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

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| symbols | string[] | Alphabetically sorted list of all available commodity symbols |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Missing API key |
| 403 | Invalid API key |

---

### List All Categories

Get all available commodity categories.

**HTTPS:** `https://commodities-api-832081557693.europe-west2.run.app/commodities/categories?api_key=YOUR_API_KEY`

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

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| categories | string[] | Alphabetically sorted list of commodity categories |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Missing API key |
| 403 | Invalid API key |

---

### Latest Data for All Commodities

Get the most recent EOD data for all commodities. Optionally filter by category.

> **Note:** This endpoint is **not paginated** — it returns one record per symbol in a single response.

**HTTPS (all):** `https://commodities-api-832081557693.europe-west2.run.app/commodities/latest?api_key=YOUR_API_KEY`

**HTTPS (by category):** `https://commodities-api-832081557693.europe-west2.run.app/commodities/latest?category=Metals&api_key=YOUR_API_KEY`

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

**Response Schema:** Array of `CommodityEODResponse` objects (see [CommodityEODResponse](#commodityeodresponse-schema) below).

> **Note:** Results have no guaranteed sort order.

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Missing API key |
| 403 | Invalid API key |

---

### Latest Data for Single Commodity

Get the most recent EOD data for a specific commodity.

**HTTPS:** `https://commodities-api-832081557693.europe-west2.run.app/commodities/latest/CL?api_key=YOUR_API_KEY`

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

**Response Schema:** A single `CommodityEODResponse` object (see [CommodityEODResponse](#commodityeodresponse-schema) below).

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Missing API key |
| 403 | Invalid API key |

---

### Get Commodity History by Symbol

Get historical EOD data for a specific commodity with pagination and date filtering.

> **Note:** Results are sorted by `date` descending (most recent first).

**HTTPS:** `https://commodities-api-832081557693.europe-west2.run.app/commodities/CL?start_date=2024-01-01&end_date=2024-12-31&page=1&page_size=10&api_key=YOUR_API_KEY`

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

**Response Schema:** A `PaginatedResponse` containing `CommodityEODResponse` items (see schemas below).

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Missing API key |
| 403 | Invalid API key |
| 422 | Invalid query parameters |

---

### List All Commodities (Paginated)

Get all EOD data across all commodities with pagination and filtering.

> **Note:** Results are sorted by `date` descending, then `symbol` ascending.

**HTTPS:** `https://commodities-api-832081557693.europe-west2.run.app/commodities?category=Energy&page=1&page_size=10&api_key=YOUR_API_KEY`

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

**Response Schema:** A `PaginatedResponse` containing `CommodityEODResponse` items (see schemas below).

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Missing API key |
| 403 | Invalid API key |
| 422 | Invalid query parameters |

---

### Query Multiple Commodities

Query EOD data for multiple symbols in a single request.

> **Note:** Results are sorted by `date` descending, then `symbol` ascending.

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

**Request Body Fields:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| symbols | string[] | Yes | List of commodity symbols to query |
| start_date | date | No | Start date filter (YYYY-MM-DD) |
| end_date | date | No | End date filter (YYYY-MM-DD) |

**Query Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 100, max: 1000) |

**Response Schema:** A `PaginatedResponse` containing `CommodityEODResponse` items (see schemas below).

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Missing API key |
| 403 | Invalid API key |
| 422 | Invalid request body or query parameters |

---

### Execute Raw SQL Query

Execute a read-only SQL SELECT query against the commodities database. Designed for programmatic and agent use.

**Security:** Only `SELECT` statements are permitted. Semicolons, SQL comments, and non-SELECT statements are rejected.

**Request:**
```bash
curl -X POST \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT symbol, close, date FROM commodities_eod WHERE symbol = :symbol ORDER BY date DESC LIMIT 5", "params": {"symbol": "CL"}}' \
  "https://commodities-api-832081557693.europe-west2.run.app/commodities/sql"
```

**Request Body:**
```json
{
  "query": "SELECT symbol, close, date FROM commodities_eod WHERE symbol = :symbol ORDER BY date DESC LIMIT 5",
  "params": {
    "symbol": "CL"
  }
}
```

**Request Body Fields:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| query | string | Yes | SQL SELECT statement to execute. Supports named parameters with `:param` syntax. |
| params | object | No | Key-value pairs for parameterized query binding (e.g. `{"symbol": "CL"}` binds `:symbol` in the query) |

**Response:**
```json
{
  "columns": ["symbol", "close", "date"],
  "data": [
    {
      "symbol": "CL",
      "close": 92.13,
      "date": "2026-04-22"
    },
    {
      "symbol": "CL",
      "close": 91.50,
      "date": "2026-04-21"
    }
  ],
  "row_count": 2
}
```

**Response Fields:**
| Name | Type | Description |
|------|------|-------------|
| columns | string[] | List of column names in the result set |
| data | object[] | Array of row objects, keyed by column name |
| row_count | integer | Number of rows returned |

**Validation Errors:**

| Input | Error |
|-------|-------|
| Empty query | 400: "Query cannot be empty" |
| `DROP TABLE commodities_eod` | 400: "Only SELECT statements are allowed" |
| `SELECT * FROM t; DROP TABLE t` | 400: "Semicolons are not allowed in queries" |
| `SELECT * FROM t -- comment` | 400: "SQL comments are not allowed in queries" |
| `INSERT INTO t VALUES (1)` | 400: "Only SELECT statements are allowed" |
| Multiple statements | 400: "Only a single SQL statement is allowed" |

**Notes:**
- A 30-second query timeout is enforced to prevent runaway queries
- Parameterized queries are strongly recommended to prevent SQL injection
- `Decimal` values are returned as floats, `date`/`datetime` values as ISO 8601 strings

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Validation error (see table above) |
| 401 | Missing API key |
| 403 | Invalid API key |
| 422 | Invalid request body |
| 500 | Query execution error (returns `"Query execution error: <message>"`) |

---

## Database Schema

The database contains a single table used by all endpoints:

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

**Column Reference:**

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | Trading date (part of composite primary key) |
| `symbol` | VARCHAR(20) | Commodity ticker symbol (part of composite primary key) |
| `name` | VARCHAR(100) | Full commodity name |
| `open` | NUMERIC | Opening price |
| `high` | NUMERIC | Highest price of the day |
| `low` | NUMERIC | Lowest price of the day |
| `close` | NUMERIC | Closing price |
| `adjusted_close` | NUMERIC | Adjusted closing price (corporate actions, splits) |
| `volume` | BIGINT | Trading volume |
| `category` | VARCHAR(50) | Commodity category: Energy, Metals, Grains, Softs, Livestock, Other. May be `null` for recently ingested records. |
| `ingestion_ts` | TIMESTAMP | Timestamp when the record was ingested into the database |

**Categories:** Energy, Metals, Grains, Softs, Livestock, Other

---

## Available Commodities

### Energy
| Symbol | Name |
|--------|------|
| CL | Crude Oil (WTI) |
| NG | Natural Gas |
| BZ | Brent Crude |
| HO | Heating Oil |
| RB | RBOB Gasoline |
| EBM | Milling Wheat N2 |
| EH | Ethanol |
| EMA | Maize (Paris) |
| LGOc3 | Gas Oil |

### Metals
| Symbol | Name |
|--------|------|
| GC | Gold (COMEX) |
| SI | Silver |
| HG | Copper |
| PL | Platinum |
| PA | Palladium |
| ALI | Aluminum (COMEX) |
| NICKEL | Nickel |
| CB | Cash-settled Butter |
| TIO | Iron Ore 62% Fe |
| HRC | Hot-Rolled Coil Steel |

### Grains
| Symbol | Name |
|--------|------|
| ZC | Corn |
| ZS | Soybean |
| KE | KC Hard Red Winter Wheat |
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
| CPO | Palm Oil |

### Livestock
| Symbol | Name |
|--------|------|
| LE | Live Cattle |
| HE | Lean Hogs |
| FC | Feeder Cattle |
| DC | Class III Milk |
| GDK | Class IV Milk |
| DY | Dry Whey |
| NCFY | Newcastle Coal |

### Other
| Symbol | Name |
|--------|------|
| LBR | Lumber |
| W | Wheat (CBOT) |

---

## Response Schemas

### CommodityEODResponse Schema

Returned by all commodity data endpoints as individual items.

| Field | Type | Description |
|-------|------|-------------|
| date | string (date) | Trading date (YYYY-MM-DD) |
| symbol | string | Commodity ticker symbol |
| name | string | Full commodity name |
| open | string (decimal) \| null | Opening price |
| high | string (decimal) \| null | Highest price of the day |
| low | string (decimal) \| null | Lowest price of the day |
| close | string (decimal) \| null | Closing price |
| adjusted_close | string (decimal) \| null | Adjusted closing price (corporate actions, splits) |
| volume | integer \| null | Trading volume |
| category | string \| null | Commodity category (Energy, Metals, Grains, Softs, Livestock, Other). May be `null` for recently ingested records. |
| ingestion_ts | string (datetime) \| null | ISO 8601 timestamp when the record was ingested |

> **Note:** Price fields (`open`, `high`, `low`, `close`, `adjusted_close`) are returned as strings to preserve decimal precision. The SQL endpoint returns them as floats instead.

### PaginatedResponse Schema

Returned by paginated endpoints (`GET /commodities/{symbol}`, `GET /commodities`, `POST /commodities/query`).

| Field | Type | Description |
|-------|------|-------------|
| data | CommodityEODResponse[] | Array of commodity records for the current page |
| page | integer | Current page number (1-based) |
| page_size | integer | Number of items per page |
| total | integer | Total number of matching records |
| total_pages | integer | Total number of pages |

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
Server-side error (database connectivity, query execution failure, etc.).

```json
{
  "detail": "Query execution error: <error message>"
}
```

> **Note:** The `detail` message varies by endpoint. The SQL endpoint returns `"Query execution error: <msg>"`. Other endpoints may return generic FastAPI error responses.

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

For issues or questions, open an issue on the [GitHub repository](https://github.com/luqmaan2000/commodities-api).
