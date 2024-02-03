from pydantic import BaseModel, EmailStr, SecretStr, validator, UUID1
import re
from datetime import datetime

class UserIn(BaseModel):
    email: EmailStr
    password: SecretStr

    @validator("password")
    def validate_password(cls, value):
        # Validate password requirements (at least 8 characters, one capital letter, one special character, one number)
        password_str = value.get_secret_value()
        
        if len(password_str) < 8:
            raise ValueError("Password must be at least 8 characters")

        if not any(char.isupper() for char in password_str):
            raise ValueError("Password must contain at least one capital letter")

        if not any(char.isdigit() for char in password_str):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password_str):
            raise ValueError("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
        return value

class UserInput(BaseModel):
    prompt: str

    @validator("prompt")
    def clean_input(cls, value):
        # Clean whitespace and convert to lowercase
        cleaned_prompt = value.strip().lower()

        # Remove special characters
        cleaned_prompt = re.sub(r'[^\w\s]', '', cleaned_prompt)

        # Example: Remove mentions and hashtags
        cleaned_prompt = re.sub(r'@[A-Za-z0-9_]+|#[A-Za-z0-9_]+', '', cleaned_prompt)

        # Example: Remove URLs
        cleaned_prompt = re.sub(r'http\S+', '', cleaned_prompt)
        
        # Remove special tokens
        cleaned_prompt = re.sub(r'<\|im_end\|>', '', cleaned_prompt)
        cleaned_prompt = re.sub(r'<\|im_start\|>', '', cleaned_prompt)

        return cleaned_prompt
    
class ContentIn(BaseModel):
    text: str
    
class ContentOut(BaseModel):
    content: str
    content_created_time: datetime
    role: str
    
class ChatOut(BaseModel):
    chat_id: UUID1
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str