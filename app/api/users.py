from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.core.security import decode_access_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await User.get(payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found or inactive")
    return user

@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active
    }

@router.get("/")
async def users_list(current: User = Depends(get_current_user)):
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return await User.find_all().to_list()