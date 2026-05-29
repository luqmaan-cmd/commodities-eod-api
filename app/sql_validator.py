import sqlparse
from fastapi import HTTPException, status


def validate_select_query(query: str) -> str:
    """Validate that a SQL query is a safe, read-only SELECT statement.

    Enforces:
    - Only SELECT statements (no INSERT, UPDATE, DELETE, DROP, ALTER, etc.)
    - No semicolons (prevents statement chaining)
    - No SQL comments (prevents obfuscation)
    - Only a single statement

    Returns the cleaned query string on success.
    Raises HTTPException(400) on validation failure.
    """
    cleaned = query.strip()

    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )

    # Reject semicolons to prevent multi-statement injection
    if ";" in cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Semicolons are not allowed in queries"
        )

    # Reject SQL comments to prevent obfuscation
    if "--" in cleaned or "/*" in cleaned or "*/" in cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SQL comments are not allowed in queries"
        )

    # Parse the SQL statement(s)
    parsed = sqlparse.parse(cleaned)

    if len(parsed) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only a single SQL statement is allowed"
        )

    statement = parsed[0]
    stmt_type = statement.get_type()

    if stmt_type != "SELECT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SELECT statements are allowed"
        )

    return cleaned
