import pytest

@pytest.mark.asyncio
async def test_create_chat(authorized_client):
    client = await authorized_client
    res=client.get("/chat/create_chat")
    assert res.status_code == 200
    
@pytest.mark.asyncio
async def test_get_chat(authorized_client,test_chats):
    client = await authorized_client
    await test_chats
    res=client.get("/chat/get_chats")
    print(res.json())
    assert res.status_code == 200
    assert len(res.json())==3
    
@pytest.mark.asyncio
async def test_get_chat(authorized_client,test_chats):
    client = await authorized_client
    await test_chats
    res=client.get("/chat/get_chats")
    assert res.status_code == 200
    assert len(res.json())==3

@pytest.mark.asyncio
async def test_get_content(authorized_client,test_chats):
    client = await authorized_client
    id=await test_chats
    res=client.get(f"/chat/get_content/{id}")
    assert res.status_code == 200
    assert len(res.json())==2

@pytest.mark.asyncio
async def test_get_content(authorized_client,test_chats):
    client = await authorized_client
    id=await test_chats
    res1=client.post(f"/chat/insert_content/{id}?text='hey my friend'")
    res2=client.get(f"/chat/get_content/{id}")

    assert res1.status_code == 200
    assert len(res2.json())==3    