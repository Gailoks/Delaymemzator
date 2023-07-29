from __future__ import annotations
import models
from abc import ABC, abstractmethod
from asyncio import coroutine
import models

class MemeSource(ABC):
    @abstractmethod
    def set_router(self, router: MemeRouter) -> None:
        pass

class MemeIntake(ABC):
    @abstractmethod
    def upload_meme(self, sender_id: int, meme: models.Meme):
        pass

    @abstractmethod
    def validate_upload(self, sender_id: int, meme: models.Meme):
        pass


class MemeRouter:
    def __init__(self, sources: list[MemeSource], intakes: dict[str, MemeIntake]):
        self.__sources = sources
        self.__intakes = intakes
        pass

    def initialize(self):
        for source in self.__sources:
            source.set_router(self)

    async def route_meme(self, sender_id: int, addresses: list[str], meme: models.Meme):
        
        for address in addresses:
            if address not in self.__intakes:
                return f"Unknown address {address}"

        targets = list(map(lambda x: (self.__intakes[x], x), addresses))

        for intake in targets:
            try:
                await intake[0].validate_upload(sender_id, meme)
            except Exception as ex:
                return f"Enable to send to {intake[1]}, reason:\n{str(ex)}"

        coroutines: list = []

        for intake in targets:
            coroutines.append(intake[0].upload_meme(sender_id, meme))

        errors: list[Exception] = []

        for coroutine in coroutines:
            try:
                await coroutine
            except Exception as ex:
                errors.append(ex)

        if errors:
            return "\n".join(map(str, errors))
        else:
            return "Successful"