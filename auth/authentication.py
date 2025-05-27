from fastapi import HTTPException, Cookie

# Dependency to get the current user
def get_user_dependency(sessions: dict):
    def dependency(session_id: str = Cookie(None)):
        if session_id is None or session_id not in sessions:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return sessions[session_id]  # Return user_id
    return dependency