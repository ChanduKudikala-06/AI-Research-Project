from fastapi import Request,HTTPException


async def require_api_key(request:Request)->None:
    config=request.app.state.config
    if not config.api_key:
        return #disabled
    key=request.headers.get("X-API-Key","")
    if key!=config.api_key:
        raise HTTPException(status_code=401,detail="Invalid or missing api key.")