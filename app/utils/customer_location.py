# app/services/geocode_service.py
import httpx
from fastapi import HTTPException

from config import YANDEX_API_KEY


async def get_coordinates_from_address(address: str) -> tuple[float, float]:
    base_url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": YANDEX_API_KEY,
        "geocode": f"Минск, {address}",
        "format": "json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Ошибка при запросе к Яндекс.Картам")

    data = response.json()
    try:
        geo_objects = data["response"]["GeoObjectCollection"]["featureMember"]
        if not geo_objects:
            raise HTTPException(status_code=404, detail="Не найдено местоположение для указанного адреса")

        geo_object = geo_objects[0]["GeoObject"]
        coordinates_str = geo_object["Point"]["pos"]
        longitude, latitude = map(float, coordinates_str.split(" "))

        return latitude, longitude
    except (IndexError, KeyError):
        raise HTTPException(status_code=404, detail="Не удалось найти координаты для указанного адреса")
