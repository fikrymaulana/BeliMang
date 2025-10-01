from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials
import uuid
from ..admin.utils import require_user_type
from ..admin.models import UserType
from .service import minio_service
from .schemas import ImageUploadResponse

router = APIRouter()

@router.post("/image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(require_user_type(UserType.admin))
):
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .jpg and .jpeg files are allowed."
        )

    # Validate file size (10KB to 2MB)
    file_size = 0
    file_data = b""

    # Read file in chunks to validate size
    while True:
        chunk = await file.read(1024)  # Read in 1KB chunks
        if not chunk:
            break
        file_size += len(chunk)
        file_data += chunk

        # Check size limits during reading
        if file_size > 2 * 1024 * 1024:  # 2MB
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum size is 2MB."
            )

    if file_size < 10 * 1024:  # 10KB
        raise HTTPException(
            status_code=400,
            detail="File size too small. Minimum size is 10KB."
        )

    try:
        # Upload to MinIO
        image_url = await minio_service.upload_image(file_data, "jpeg")

        return ImageUploadResponse(
            message="File uploaded successfully",
            data={"imageUrl": image_url}
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )