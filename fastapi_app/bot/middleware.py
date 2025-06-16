from aiogram import BaseMiddleware

class DatabaseMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        return await handler(event, data)

class RoleMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        return await handler(event, data)