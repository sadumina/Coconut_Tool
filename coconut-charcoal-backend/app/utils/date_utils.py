from datetime import datetime

def month_key(dt: datetime) -> str:
    """
    Convert a datetime into a YYYY-MM formatted string.
    Example: "2025-01"
    Used for grouping prices by month.
    """
    return dt.strftime("%Y-%m")
