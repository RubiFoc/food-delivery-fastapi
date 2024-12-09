from fastapi import FastAPI
from pydantic import BaseModel
from sqladmin import Admin, ModelView
from starlette.middleware.cors import CORSMiddleware

from auth.database import engine
from models.delivery import User, Role, Courier, Restaurant, Dish, Order, OrderStatus, Cart
from routers.courier import courier_router
from routers.courier_worker import courier_worker_router
from routers.users import router as auth_router
from routers.delivery import router as delivery_router
from routers.admin import admin_router
from routers.kitchen_worker import kitchen_worker_router
from settings.fastapi_settings import fastapi_settings

app = FastAPI(
    title="Food delivery"
)
# admin = Admin(app, engine)


# # Представление для модели User
# class UserAdminView(ModelView):
#     model = User
#     pk_columns = [User.id]
#     column_list = [User.id, User.email, User.username, User.role_id, User.is_active, User.is_superuser]
#
#
# # Представление для модели Role
# class RoleAdminView(ModelView):
#     model = Role
#     pk_columns = [Role.id]
#     column_list = [Role.id, Role.name, Role.permissions]
#
#
# # Представление для модели Courier
# class CourierAdminView(ModelView):
#     model = Courier
#     pk_columns = [Courier.id]
#     column_list = [Courier.id, Courier.rating, Courier.number_of_marks, Courier.rate, Courier.location, Courier.role_id]
#
#
# # Представление для модели Restaurant
# class RestaurantAdminView(ModelView):
#     model = Restaurant
#     pk_columns = [Restaurant.id]
#     column_list = [Restaurant.id, Restaurant.name, Restaurant.location, Restaurant.rating, Restaurant.number_of_marks]
#
#
# # Представление для модели Dish
# class DishAdminView(ModelView):
#     model = Dish
#     pk_columns = [Dish.id]
#     column_list = [Dish.id, Dish.name, Dish.price, Dish.weight, Dish.rating, Dish.number_of_marks, Dish.profit,
#                    Dish.time_of_preparing, Dish.image_path]
#
#
# # Представление для модели Order
# class OrderAdminView(ModelView):
#     model = Order
#     pk_columns = [Order.id]
#     column_list = [Order.id, Order.price, Order.weight, Order.time_of_creation, Order.location, Order.time_of_delivery,
#      Order.expected_time_of_delivery, Order.status]
#
#
# # Представление для модели OrderStatus
# class OrderStatusAdminView(ModelView):
#     model = OrderStatus
#     pk_columns = [Order.id]
#     column_list = [OrderStatus.order_id, OrderStatus.is_prepared, OrderStatus.is_delivered]
#
#
# # Представление для модели Cart
# class CartAdminView(ModelView):
#     model = Cart
#     pk_columns = [Cart.id]
#     column_list = [Cart.id, Cart.customer_id]
#
#
# # Добавляем все представления в административную панель
# admin.add_view(UserAdminView)
# admin.add_view(RoleAdminView)
# admin.add_view(CourierAdminView)
# admin.add_view(RestaurantAdminView)
# admin.add_view(DishAdminView)
# admin.add_view(OrderAdminView)
# admin.add_view(OrderStatusAdminView)
# admin.add_view(CartAdminView)

# Включаем роутеры в приложение
app.include_router(courier_worker_router)
app.include_router(auth_router)
app.include_router(delivery_router)
app.include_router(admin_router)
app.include_router(kitchen_worker_router)
app.include_router(courier_router)

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=fastapi_settings.host, port=fastapi_settings.port)
