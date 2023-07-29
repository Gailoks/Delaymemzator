import abstractions
import models
from termcolor import colored


class DevIntake(abstractions.MemeIntake):
    def __init__(self, name: str, mode) -> None:
        self.__name = name
        self.__mode = mode
        pass

    async def upload_meme(self, sender_id: int, meme: models.Meme):
        if self.__mode == 'fail':
            raise Exception(f"Dev exception from DevIntake({self.__name}) in upload_meme")

        print(f"[DevIntake {colored(self.__name, 'red')}]: {colored('sender', 'red')}:{sender_id}, {colored('datetime', 'red')}:{meme.datetime}, {colored('url', 'red')}:{meme.url}")

    async def validate_upload(self, sender_id: int, meme: models.Meme):
        if self.__mode == 'invalid':
            raise Exception(f"Dev exception from DevIntake({self.__name}) in validate_upload")