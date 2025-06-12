from pydantic import BaseModel

class PartnerInfoResponse(BaseModel):
    id: int
    user_name: str
    public_key: str

    class Config:
        from_attributes=True
