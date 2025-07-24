from pydantic import BaseModel

class UpdatePublicKey(BaseModel):
    user_id: int
    public_key: str
