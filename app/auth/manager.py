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
        elif user.role_id == 2:  # Предполагаем, что роль курьера
            new_courier = Courier(id=user.id, location="", role_id=user.role_id)
            session.add(new_courier)
        elif user.role_id == 3:  # Предполагаем, что роль кухонного работника
            new_worker = KitchenWorker(id=user.id, role_id=user.role_id)
            session.add(new_worker)
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

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
