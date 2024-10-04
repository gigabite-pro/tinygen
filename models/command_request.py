from pydantic import BaseModel

class CommandRequest(BaseModel):
    repoUrl: str
    prompt: str
