import aiosqlite
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class User:
    id: int
    group_id: int

class DBContext(ABC):
    @abstractmethod
    async def add_user(self, user: User):
        pass

    @abstractmethod
    async def remove_user(self, user_id: int):
        pass

    @abstractmethod
    async def get_users(self):
        pass

    @abstractmethod
    async def get_user(self, user_id: int):
        pass

class SQLiteDBContext(DBContext):
    TABLE_NAME = "VK"

    connection: aiosqlite.Connection

    async def connect(self, connection_string: str):
        self.connection = await aiosqlite.connect(connection_string)

    async def add_user(self, user: User):
        await self.connection.execute(f"INSERT INTO `{SQLiteDBContext.TABLE_NAME}` (`id`, `group_id`) VALUES(?, ?, ?)", (user.id, user.group_id))
        await self.connection.commit()
        
    async def get_users(self):        
        return await self.connection.execute_fetchall(f"SELECT `id` FROM `{SQLiteDBContext.TABLE_NAME}`")
    
    async def get_user(self, user_id: int):
        result = await self.connection.execute_fetchall(f"SELECT (`id`, `group_id`) FROM `{SQLiteDBContext.TABLE_NAME}` WHERE `id` = ?", (user_id))
        element = next(result)
        return User(element['id'], element['group_id'])

    async def remove_user(self, user_id: int):
        await self.connection.execute(f"DELETE * FROM `{SQLiteDBContext.TABLE_NAME}` WHERE `id` = ?", (user_id))
        await self.connection.commit()

    async def close(self):
        await self.connection.close()
