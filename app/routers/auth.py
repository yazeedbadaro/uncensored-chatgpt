from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import database, utils, oauth2
from ..schemas import Token
from fastapi_limiter.depends import RateLimiter


router = APIRouter(tags=['Authentication'])

@router.post('/login',response_model=Token,dependencies=[Depends(RateLimiter(times=3,minutes=5))])
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db= Depends(database.get_db)):
    
    query="""
    SELECT BIN_TO_UUID(user_id) as id,email,password from user where email = %s;
    """
    
    result=await database.execute_query(query,(user_credentials.username),db=db)
    user=result[0]

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(user_credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user_id": user["id"]})

    return {"access_token": access_token, "token_type": "bearer"}