from datetime import datetime
from typing import Optional

from fastapi import Depends, Request, HTTPException
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas
from sqlalchemy.ext.asyncio import AsyncSession

from config import SECRET_MANAGER
from auth.database import get_user_db, get_async_session
from models.delivery import User, Customer, Courier, KitchenWorker, Admin

SECRET = SECRET_MANAGER

from sqlalchemy.future import select


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

        # Создаем асинхронную сессию
        async for session in get_async_session():  # Используем async for
            await self._create_related_role(user, session)

    async def _create_related_role(self, user: User, session: AsyncSession):
        # Проверяем роль пользователя и создаем соответствующую запись
        if user.role_id == 1:  # Предполагаем, что роль клиента
            new_customer = Customer(id=user.id, balance=0, role_id=user.role_id)
            session.add(new_customer)
        elif user.role_id == 4:  # Предполагаем, что роль администратора
            new_admin = Admin(id=user.id, role_id=user.role_id)
            session.add(new_admin)

        await session.commit()  # Сохраняем изменения

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:
        """
        Создает пользователя в базе данных с проверкой для администраторов.
        """
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["is_verified"] = True
        user_dict["is_superuser"] = True

        # Проверяем роль пользователя
        if user_create.role_id == 4:  # Роль администратора
            user_dict["is_verified"] = True
            user_dict["is_superuser"] = True
            async for session in get_async_session():
                result = await session.execute(
                    select(User).filter(User.role_id == 4)
                )
                admin_count = len(result.scalars().all())  # Подсчёт записей
                if admin_count > 0:
                    # Проверяем, чтобы запрос был инициирован администратором
                    # if not request or not hasattr(request, "user"):
                    #     raise HTTPException(status_code=404, detail="Only an existing admin can create another admin.")
                    # if not request.user.is_authenticated or request.user.role_id != 4:
                    #     raise HTTPException(status_code=404, detail="Only an existing admin can create another admin.")
                    raise HTTPException(status_code=404, detail="Only an existing admin can create another admin.")
        else:
            user_dict["is_verified"] = False
            user_dict["is_superuser"] = False

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


class CourierWorkerManager(BaseUserManager[User, int]):
    async def on_after_register(self, user: User, session: AsyncSession):
        """
        Создание записи в соответствующей таблице после регистрации.
        """
        if user.role_id == 2:  # Роль курьера
            new_courier = Courier(id=user.id, location="", role_id=user.role_id)
            session.add(new_courier)
        elif user.role_id == 3:  # Роль работника кухни
            new_worker = KitchenWorker(id=user.id, role_id=user.role_id)
            session.add(new_worker)
        await session.commit()

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:
        """
        Создаёт пользователя с заданными настройками для курьера и работника кухни.
        """
        await self.validate_password(user_create.password, user_create)

        # Проверка на существование пользователя с таким email
        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user:
            raise exceptions.UserAlreadyExists()

        # Проверка на допустимые значения role_id
        if user_create.role_id not in [2, 3]:
            raise HTTPException(
                status_code=400,
                detail="Invalid role_id. Only roles for couriers (2) and kitchen workers (3) are allowed."
            )

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )

        # Хешируем пароль
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        # Устанавливаем значения is_superuser и is_verified
        user_dict["is_superuser"] = False
        user_dict["is_verified"] = False

        # Создаём пользователя
        created_user = await self.user_db.create(user_dict)

        # Выполняем постобработку после регистрации
        async for session in get_async_session():
            await self.on_after_register(created_user, session)

        return created_user


class AdminManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Действия после регистрации администратора.
        """
        print(f"Admin user {user.id} has been registered.")

        async for session in get_async_session():
            await self._create_admin_role(user, session)

    async def _create_admin_role(self, user: User, session: AsyncSession):
        """
        Создаёт запись в таблице Admin для зарегистрированного пользователя-администратора.
        """
        if user.role_id == 4:  # Проверяем, что роль администратора
            new_admin = Admin(id=user.id, role_id=user.role_id)
            session.add(new_admin)
            await session.commit()

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:
        """
        Создаёт пользователя с ролью администратора.
        """
        await self.validate_password(user_create.password, user_create)

        # Проверка уникальности email
        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user:
            raise exceptions.UserAlreadyExists()

        # Проверяем, что роль соответствует администратору
        if user_create.role_id != 4:
            raise HTTPException(
                status_code=400,
                detail="Only users with role_id=4 (Admin) can be created using this manager."
            )

        # Подготовка данных для создания пользователя
        user_dict = user_create.create_update_dict_superuser()
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["is_verified"] = True
        user_dict["is_superuser"] = True
        user_dict["role_id"] = 4

        # Создание пользователя
        created_user = await self.user_db.create(user_dict)

        # Выполняем действия после регистрации
        await self.on_after_register(created_user, request)

        return created_user


# Зависимость для получения AdminManager
async def get_admin_manager(user_db=Depends(get_user_db)):
    yield AdminManager(user_db)



async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


async def get_courier_worker_manager(user_db=Depends(get_user_db)):
    yield CourierWorkerManager(user_db)

