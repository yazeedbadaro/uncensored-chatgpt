from threading import Thread
from queue import Queue
from transformers import TextStreamer
from fastapi import Depends, HTTPException,status
from .database import get_db,execute_query
from . import oauth2
from pydantic import UUID1
from .schemas import ContentOut
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("cognitivecomputations/dolphin-2.6-mistral-7b-dpo-laser")
model = AutoModelForCausalLM.from_pretrained("cognitivecomputations/dolphin-2.6-mistral-7b-dpo-laser").to("cuda")
model.eval()

# Custom TextStreamer class
class CustomStreamer(TextStreamer):
    def __init__(self, queue, tokenizer, skip_prompt, **decode_kwargs) -> None:
        super().__init__(tokenizer, skip_prompt, **decode_kwargs)
        self._queue = queue
        self.stop_signal = None
        self.timeout = 1

    def on_finalized_text(self, text: str, stream_end: bool = False):
        self._queue.put(text.split("<|im_end|>")[0])
        if stream_end:
            self._queue.put(self.stop_signal)

# Dependency to create a new queue for each API call
async def get_streamer_queue():
    return Queue()

async def model_get_content(chat_id: UUID1 ,system_msg_n: int,db=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  
    query = f"""
    SELECT
        c.content,
        c.role,
        c.created_at AS content_created_time
    FROM (
        SELECT
            cont.content_id,
            cont.chat_id,
            cont.content,
            cont.role,
            cont.n_tokens,
            cont.created_at,
            SUM(cont.n_tokens) OVER (PARTITION BY cont.chat_id ORDER BY cont.created_at DESC) AS cumulative_tokens
        FROM content cont
        JOIN chat ch ON cont.chat_id = ch.chat_id
        WHERE ch.owner_id = UUID_TO_BIN(%s)
        AND cont.chat_id = UUID_TO_BIN(%s)
    ) c
    WHERE cumulative_tokens <= {32000-system_msg_n}
    ORDER BY c.created_at;
        """
    results = await execute_query(query,(current_user["id"],chat_id),db=db)
    if not results:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Content not found")
    return [ContentOut(**result) for result in results]

async def insert_content(chat_id: UUID1,content,role,n_tokens,current_user: int = Depends(oauth2.get_current_user),db=Depends(get_db)):
    try:
        query="""
            INSERT INTO content (content_id, chat_id,content,role,n_tokens) VALUES
            (UUID_TO_BIN(UUID()), UUID_TO_BIN(%s),%s,%s,%s);
        """
        
        await execute_query(query,(chat_id,content,role,n_tokens),db=db)
        
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Chat not found")

def start_generation(queue, query):
    
    inputs = tokenizer(query, return_tensors="pt", add_special_tokens=False).to("cuda")
    streamer_queue = queue
    streamer = CustomStreamer(streamer_queue, tokenizer, True)

    generation_kwargs = dict(**inputs, streamer=streamer, max_new_tokens=32000)
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

async def response_generator(queue, query,chat_id: UUID1 , db=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    text="<|im_start|>assistant\n"
    start_generation(queue, query)

    while True:
        value = queue.get()
        if value is None:
            break
        text+=value
        yield value
        queue.task_done()
        
    text+="<|im_end|>\n"
    await insert_content(chat_id=chat_id,content=text,role="bot",n_tokens=len(tokenizer(text,add_special_tokens=False)["input_ids"]),current_user = current_user,db=db)
