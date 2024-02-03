from aiomysql import create_pool
import os
from app.main import app
from app.database import get_db
import pytest
from fastapi.testclient import TestClient
from yoyo import read_migrations
from yoyo import get_backend
from app.oauth2 import create_access_token
from app.database import execute_query

class TestDatabase:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await create_pool(
            host=os.environ.get("DATABASE_HOSTNAME"), 
            port=int(os.environ.get("DATABASE_PORT")),
            user=os.environ.get("DATABASE_USERNAME"), 
            password=os.environ.get("DATABASE_PASSWORD"), 
            db=os.environ.get("DATABASE_NAME")+"_test",
            autocommit=True
        )

    async def disconnect(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()


@pytest.fixture
def client():
    backend = get_backend(f'mysql://{os.environ.get("DATABASE_USERNAME")}:{os.environ.get("DATABASE_PASSWORD")}@{os.environ.get("DATABASE_HOSTNAME")}/{os.environ.get("DATABASE_NAME")}_test')
    migrations = read_migrations('migrations')
    
    # Rollback all migrations
    backend.rollback_migrations(backend.to_rollback(migrations))
    
    # Apply any outstanding migrations
    backend.apply_migrations(backend.to_apply(migrations))

    db = TestDatabase()
    
    async def override_get_db():
        try:
            await db.connect()
            yield db.pool
        finally:
            await db.disconnect()
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "user@example.com",
                 "password": "Password123$"}
    res = client.post("/user/signup", json=user_data)

    assert res.status_code == 201
    return user_data

@pytest.fixture
async def token(test_user):
    db=TestDatabase()
    await db.connect()
    query="""
        SELECT BIN_TO_UUID(user_id) as user_id FROM user WHERE email= %s;
    """
    
    id= await execute_query(query,test_user["email"],db=db.pool)
    await db.disconnect()
    return create_access_token({"user_id": id[0]['user_id']})

@pytest.fixture
async def authorized_client(client, token):
    res= await token
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {res}"
    }
    return client


@pytest.fixture
async def test_chats():
    db=TestDatabase()
    await db.connect()
    #get user id
    query="""
        SELECT BIN_TO_UUID(user_id) as user_id FROM user WHERE email= %s;
    """
    id= await execute_query(query,"user@example.com",db=db.pool)
    #create chats
    query="""
    INSERT INTO chat (chat_id,owner_id) VALUES
    (UUID_TO_BIN(UUID()), UUID_TO_BIN(%s));
    """
    #insert 3 chats
    for i in range(3):
        await execute_query(query,id[0]["user_id"],db=db.pool)
    
    #get one of the chat ids
    query="SELECT BIN_TO_UUID(chat_id) AS chat_id,created_at FROM chat WHERE owner_id=UUID_TO_BIN(%s)"
    res=await execute_query(query,id[0]["user_id"],db=db.pool)
    
    #insert content
    query="""
        INSERT INTO content (content_id, chat_id,content,role) VALUES
        (UUID_TO_BIN(UUID()), UUID_TO_BIN(%s),%s,%s);
    """
    
    await execute_query(query,(res[0]["chat_id"],"hello","user"),db=db.pool)
    await execute_query(query,(res[0]["chat_id"],"hello how can i help you?","bot"),db=db.pool)
    
    
    await db.disconnect()
    
    return res[0]["chat_id"]
    


