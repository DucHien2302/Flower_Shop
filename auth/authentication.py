from fastapi import Depends, HTTPException
from globals import api_key_header

# Dependency to get the current user
def get_user_dependency(sessions: dict):
    def dependency(session_id: str = Depends(api_key_header)):
        if session_id is None or session_id not in sessions:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return sessions[session_id]  # Return user_id
    return dependency