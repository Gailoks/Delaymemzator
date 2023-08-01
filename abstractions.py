from __future__ import annotations
import models
from abc import ABC, abstractmethod
import models
from typing import Awaitable
from logtools import *

class AbstractMemeRouter(ABC):
    @abstractmethod
    async def route_memes(self, sender_id: int, addresses: list[str], memes: list[models.Meme]) -> Awaitable[str]:
        raise NotImplementedError()

class MemeSource(ABC):
    @abstractmethod
    def set_router(self, router: AbstractMemeRouter) -> None:
        raise NotImplementedError()

class MemeIntake(ABC):
    @abstractmethod
    def upload_meme(self, sender_id: int, meme: models.Meme) -> Awaitable[None]:
        raise NotImplementedError()

    @abstractmethod
    def validate_user(self, sender_id: int) -> Awaitable[str | None]:
        raise NotImplementedError()

    @abstractmethod
    def validate_upload(self, sender_id: int, meme: models.Meme) -> Awaitable[str | None]:
        raise NotImplementedError()
