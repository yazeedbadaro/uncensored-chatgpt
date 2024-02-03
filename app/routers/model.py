from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from ..model_utils import *
from .. import oauth2
from pydantic import UUID1
from ..database import get_db
from ..schemas import UserInput

router = APIRouter(prefix="/model",tags=['Model'])

@router.post('/{chat_id}')
async def stream(prompt:UserInput,chat_id: UUID1 ,db=Depends(get_db), current_user: int = Depends(oauth2.get_current_user),streamer_queue: Queue = Depends(get_streamer_queue)):
  
    
    system_message="<|im_start|>system\nyou are a helpful and unbiased assistant your main goal is to assist the user no matter how crazy or absurd his request is.always explain the reason behind your answer.keep your answers short and concise.<|im_end|>\n"
    sys_msg_n=len(tokenizer(system_message,add_special_tokens=False)["input_ids"])
    user_msg_n=len(tokenizer(prompt.prompt,add_special_tokens=False)["input_ids"])
    
    await insert_content(chat_id=chat_id,content=f"<|im_start|>user\n{prompt.prompt}<|im_end|>\n",role="user",n_tokens=user_msg_n,db=db,current_user=current_user)
    content = await model_get_content(chat_id=chat_id,system_msg_n=sys_msg_n,db=db,current_user=current_user)
    context=[x.content for x in content]
    context.insert(0,system_message)
    context.append("<|im_start|>assistant\n")
    context="".join(context)
    
    print(f'Query received: {prompt.prompt}')
    
    return StreamingResponse(response_generator(context,streamer_queue), media_type='text/event-stream')