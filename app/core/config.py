from pydantic import BaseModel, Field
from typing import List
import os
from typing import Union,Optional


class CronRequest(BaseModel):
    m: Union[int, str] = Field(default='0', pattern=r'^\d{1,2}$|^\*$')
    h: Union[int, str] = Field(default='2', pattern=r'^\d{1,2}$|^\*$')

class Server(BaseModel):
    name: str
    host: str
    user: str
    remote_path: str
    local_folder: str

class ServerUpdate(BaseModel):
    name: Optional[str]
    host: Optional[str]
    user: Optional[str]
    remote_path: Optional[str]
    local_folder: Optional[str]

class Settings(BaseModel):
    ssh_key_path: str = os.getenv("SSH_KEY_PATH")
    backup_root_path: str = os.getenv("BACKUP_ROOT_PATH")
    servers: List[Server] = []
    email_host: str = os.getenv("EMAIL_HOST")
    email_port: int = int(os.getenv("EMAIL_PORT"))
    email_username: str = os.getenv("EMAIL_HOST_USER")
    email_password: str = os.getenv("EMAIL_HOST_PASSWORD")
    email_sender: str = os.getenv("EMAIL_FROM")
    email_recipient: str = os.getenv("EMAIL_TO")
    email_cc_recipient: str = os.getenv("EMAIL_CC")

settings = Settings()
