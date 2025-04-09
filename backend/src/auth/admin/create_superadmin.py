import asyncio
import getpass
from sqlalchemy import text
from src.db.database import async_engine
from src.auth.schemas import Role
from src.auth.service import get_password_hash


async def create_superadmin():
    print("=== Создание суперадминистратора ===")
    email = input("Введите email: ")
    password = getpass.getpass("Введите пароль: ")
    confirm_password = getpass.getpass("Подтвердите пароль: ")

    if password != confirm_password:
        print("Ошибка: Пароли не совпадают!")
        return

    hashed_password = get_password_hash(password)

    async with async_engine.begin() as conn:
        result = await conn.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": email}
        )
        if result.fetchone():
            print(f"Ошибка: Пользователь с email {email} уже существует!")
            return
        await conn.execute(
            text("""
                INSERT INTO users 
                (email, hashed_password, role, disabled, is_verified, verification_token, reset_token)
                VALUES 
                (:email, :hashed_password, :role, :disabled, :is_verified, NULL, NULL)
            """),
            {
                "email": email,
                "hashed_password": hashed_password,
                "role": Role.superadmin,
                "disabled": False,
                "is_verified": True
            }
        )
        print(f"Суперадминистратор {email} успешно создан!")


if __name__ == "__main__":
    asyncio.run(create_superadmin())