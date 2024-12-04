import os
from shutil import copyfileobj
from fastapi import UploadFile

from config import UPLOAD_FOLDER


async def save_image(file: UploadFile):
    # Генерация уникального имени для файла
    filename = f"{file.filename}"

    # Путь для хранения изображения внутри контейнера
    container_image_path = os.path.join(UPLOAD_FOLDER, filename)

    # Путь для локального хранения
    local_image_path = os.path.join("static/", filename)

    # Сохраняем файл внутри контейнера
    with open(container_image_path, "wb") as buffer:
        copyfileobj(file.file, buffer)

    # Сохраняем файл локально
    with open(local_image_path, "wb") as buffer:
        copyfileobj(file.file, buffer)

    return container_image_path
