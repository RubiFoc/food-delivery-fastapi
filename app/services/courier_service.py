import requests
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import GOOGLE_MAPS_DIRECTIONS_API_URL
from models.delivery import Courier


# Функция для обновления местоположения курьера на основе его текущих координат
def update_courier_location(api_key: str, courier_id: int, lat: float, lon: float, session: AsyncSession):
    """Обновляем местоположение курьера в базе данных на основе его координат"""
    courier = await session.execute(select(Courier).where(Courier.id == courier_id))
    courier = courier.scalar_one_or_none()

    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")

    # Обновляем координаты курьера
    courier.location = f"{lat},{lon}"
    await session.commit()


def get_travel_time(api_key: str, origin: str, destination: str) -> int:
    """Получаем время в пути между курьером и заказом через Google Maps Directions API"""
    params = {
        'origin': origin,
        'destination': destination,
        'key': api_key,
        'mode': 'driving',  # Режим транспорта (можно настроить)
        'departure_time': 'now'
    }
    response = requests.get(GOOGLE_MAPS_DIRECTIONS_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['routes']:
            # Получаем время в пути из первого маршрута
            duration = data['routes'][0]['legs'][0]['duration']['value']
            return duration  # Время в пути в секундах
    return None
