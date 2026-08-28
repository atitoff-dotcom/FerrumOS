from typing import Optional
from pydantic import BaseModel

class DeployRequest(BaseModel):
    code: str
    filename: Optional[str] = None
    board: str = "esp32c6_supermini"
    force: bool = False

class ValidateRequest(BaseModel):
    code: str
    board: str = "esp32c6_supermini"
    task_id: Optional[str] = None

class ScriptSaveRequest(BaseModel):
    code: str

class MqttTestRequest(BaseModel):
    host: Optional[str] = "192.168.1.114"
    port: Optional[int] = 1883
    username: Optional[str] = "alex"
    password: Optional[str] = "bh0020"
