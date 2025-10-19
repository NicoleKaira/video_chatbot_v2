# User class
from pydantic import BaseModel


class User(BaseModel):
    username: str
    role: str

class UserDetails(BaseModel):
    username: str
    password: str

