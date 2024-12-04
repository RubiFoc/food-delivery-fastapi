import os
from shutil import copyfileobj
from fastapi import UploadFile

from config import UPLOAD_FOLDER


async def save_image(file: UploadFile):
    filename = f"{file.filename}"

    container_image_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(container_image_path, "wb") as buffer:
        copyfileobj(file.file, buffer)

    return container_image_path
