from fastapi import APIRouter, Depends,status,HTTPException
from ..database import get_db,execute_query
from ..utils import *
from ..schemas import UserIn

router = APIRouter(prefix="/users",tags=['User'])


@router.post("/",status_code=status.HTTP_201_CREATED)
async def sign_up(user:UserIn,db=Depends(get_db)):
    
    user.password= hash(user.password.get_secret_value())
    
    query="""
    INSERT INTO user (user_id, email,password) VALUES
    (UUID_TO_BIN(UUID()), %s,%s);
    """
    try:
        await execute_query(query,(user.email,user.password),db=db)
    except:  
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="user already exists")