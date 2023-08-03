import asyncio
from typing import Awaitable, Callable, Any
from datetime import datetime

TaskErrorCallback = Callable[[Exception, Any], Awaitable[None] | None]

class Scheduler:
    def __init__(self):
        pass

    def schedule(self, async_state: Any, task: Callable[[Any], Awaitable[None] | None], execution_time: datetime, error_callback: TaskErrorCallback):
        timeout = (execution_time - datetime.now()).microseconds//1000
        if timeout <= 1000:
            raise Exception("Execution time in past")
        asyncio.create_task(self.__schedule_coroutine(async_state, task, error_callback, timeout))

    async def __schedule_coroutine(async_state: Any, task: Callable[[Any], Awaitable[None] | None], error_callback: TaskErrorCallback, timeout: int):
        await asyncio.sleep(timeout)
        try:
            await task(async_state)
        except Exception as ex:
            await error_callback(ex, async_state)
