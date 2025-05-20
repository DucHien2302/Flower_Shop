from fastapi.security import APIKeyHeader


sessions = {}
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)