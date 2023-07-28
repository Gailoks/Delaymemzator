import aiosqlite


class SQLighter:

    async def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = await aiosqlite.connect(database)

    async def add_user(self, user_id, group_id, type):
        """Добовляем нового пользователя"""
        await self.connection.execute("INSERT INTO `Users` (`user_id`, `group_id`, `type`) VALUES(?,?,?)", (user_id, group_id, type))
        await self.connection.commit()
        
    async def get_users(self):
        """Получение всех id пользователей"""
        
        return await self.connection.execute_fetchall("SELECT `user_id` FROM `Users`",())
    
        
    async def get_user(self, user_id):
        """Получаем пользователя"""
        return await self.connection.execute_fetchall("SELECT * FROM `Users` WHERE `user_id` = ?",(user_id))

    async def remove_user(self, user_id):
        """удаляем пользователя из базы даных"""
        await self.connection.execute("DELETE * FROM `Users` WHERE `user_id` = ?",(user_id))
        await self.connection.commit()

    async def close(self):
        """Закрываем соединение с БД"""
        await self.connection.close()
