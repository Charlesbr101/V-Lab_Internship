import re
from sqlalchemy.exc import IntegrityError


def _to_http_validation_error(msg: str, loc=None, type_: str = "integrity_error") -> dict:
    """Wrap a single message into FastAPI's HTTPValidationError-like shape.

    Returns a dict: {"detail": [{"loc": [...], "msg": "...", "type": "..."}]}
    """
    if loc is None:
        loc = ["body"]
    return [{"loc": loc, "msg": msg, "type": type_}]


def parse_integrity_error(err: IntegrityError) -> dict:
    """Return a HTTPValidationError-shaped object for common DB integrity errors.

    This maps duplicate-key and foreign-key failures to a validation-style
    response so routers can pass the object directly as an HTTPException
    detail payload and the client will receive a structured validation error.
    """
    orig = getattr(err, "orig", None)
    msg = str(orig) if orig is not None else str(err)

    # MySQL duplicate entry: "Duplicate entry 'value' for key 'key'"
    if "Duplicate entry" in msg:
        m = re.search(r"Duplicate entry '(.+?)' for key '(.+?)'", msg)
        if m:
            value, key = m.groups()
            # Normalize key name: could be like `users.email` or index name.
            # Prefer the last part after a dot if present.
            key_clean = key.split('.')[-1].strip('`')
            friendly = f"{key_clean} already exists ({value})"
            return _to_http_validation_error(friendly, loc=["body", key_clean], type_="value_error.unique")
        return _to_http_validation_error("Duplicate entry", type_="value_error.duplicate")

    # Foreign key related failures
    if "foreign key" in msg.lower() or "constraint fails" in msg.lower() or "1452" in msg or "1451" in msg:
        return _to_http_validation_error("Foreign key constraint failed: referenced resource not found", type_="value_error.foreign_key")

    # Fallback: wrap the original message
    return _to_http_validation_error(msg, type_="value_error")