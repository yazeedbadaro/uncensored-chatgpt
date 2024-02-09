from fastapi import APIRouter, Depends, HTTPException,status
from ..database import get_db,execute_query
from .. import oauth2
from pydantic import UUID1
from typing import List
from ..schemas import ChatOut,ContentOut,ContentIn

router = APIRouter(prefix="/chats",tags=['Chat'])

@router.get("/{chat_id}",status_code=status.HTTP_200_OK,response_model=List[ContentOut])
async def get_content(chat_id: UUID1 ,db=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    query = """
    SELECT
         ct.content,
         ct.created_at AS content_created_time,
         ct.role
     FROM
         user u
     JOIN
         chat c ON u.user_id = c.owner_id
     JOIN
         content ct ON c.chat_id = ct.chat_id
     WHERE
         u.user_id = UUID_TO_BIN(%s)
         AND 
         c.chat_id = UUID_TO_BIN(%s)
    ORDER BY c.created_at;
        """
    result = await execute_query(query,(current_user["id"],chat_id),db=db)
    if not result:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Content not found")
    return result

@router.get("/",status_code=status.HTTP_200_OK,response_model=List[ChatOut])
async def get_chats(db=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    query="SELECT BIN_TO_UUID(chat_id) AS chat_id,created_at FROM chat WHERE owner_id=UUID_TO_BIN(%s)"
    
    result = await execute_query(query,current_user["id"],db=db)
    if not result:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Chat not found")
    return result

@router.post("/",status_code=status.HTTP_200_OK)
async def create_chat(db=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    query="""
    INSERT INTO chat (chat_id,owner_id) VALUES
    (UUID_TO_BIN(UUID()), UUID_TO_BIN(%s));
    """
    await execute_query(query,current_user["id"],db=db)