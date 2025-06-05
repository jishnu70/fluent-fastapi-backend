from pydantic import BaseModel

class AttachmentResponse(BaseModel):
    id: int
    file_name: str
    file_type: str
    file_url: str