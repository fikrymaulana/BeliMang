from pydantic import BaseModel

class ImageUploadResponse(BaseModel):
    message: str
    data: dict

    class Config:
        schema_extra = {
            "example": {
                "message": "File uploaded successfully",
                "data": {
                    "imageUrl": "https://awss3.d87801e9-fcfc-42a8-963b-fe86d895b51a.jpeg"
                }
            }
        }