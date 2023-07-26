import vk_api as api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json
import asyncio
from downloader import handle_message

async def main():
    with open("config.json", 'r', encoding="utf-8") as file:
        config = json.load(file)
        dconfig = config['downloader']
        uconfig = config['uploader']

    downloader_session = api.VkApi(token=dconfig["token"])
    downloader_longpoll = VkBotLongPoll(downloader_session, dconfig["id"])
    downloader_api = downloader_session.get_api()


    uploader_session = api.VkApi(token=uconfig["token"])
    uploader_api =  uploader_session.get_api()




    #adding router to handle memes
    for event in downloader_longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            await handle_message(event, downloader_api, uploader_api,uconfig["id"])

if __name__ == "__main__":
    asyncio.run(main())