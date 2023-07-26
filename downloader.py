from vk_api.bot_longpoll import VkBotEvent
from vk_api.vk_api import VkApiMethod
import vk_api 
import dateparser
import requests
import datetime
import time
import io



def delayed_post(date_time: datetime, photo_url: str, uploader_api, owner_id):
    temp = io.BytesIO(requests.get(photo_url).content)


    temp.seek(0)
    uploader = vk_api.VkUpload(uploader_api)
    uploaded_photo = uploader.photo_wall(temp,group_id=owner_id)[0]

    photo_id  = uploaded_photo["id"]
    photo_owner_id = uploaded_photo["owner_id"]
    photo_attachment = f"photo{photo_owner_id}_{photo_id}"
    


    uploader_api.wall.post(owner_id = -owner_id, from_group = 1, attachments = photo_attachment, publish_date = int(time.mktime(date_time.timetuple())))






    
async def handle_message(event: VkBotEvent, downloader_api: VkApiMethod, uploader_api: VkApiMethod, owner_id: int):
    message = event.obj["message"]
    id = message["from_id"]
    
    def answer(text:str):
        downloader_api.messages.send(user_id = id, message = text, random_id = 0)

    if id != 559888974 and id != 507016336:
        return answer(f"You are not availible to post your id: {id} \n please contact @travertin35")
    

    text = message.get("text")
    if not text:
        return answer("Wrong data no text handled")
    
    time = dateparser.parse(text)
    if not time:
        return answer("Wrong date format")
    
    attachments = message.get("attachments")
    if not attachments:
        return answer("No attachments found")

    photo = list(filter(lambda x: x["type"]=="photo", attachments))
    wall = list(filter(lambda x: x["type"]=="wall", attachments))

    if photo:

        photo_url = photo[0]["photo"]["sizes"][-1]["url"]
        delayed_post(time, photo_url, uploader_api, owner_id)
        return answer(f"Sucssesful added new post to {time}")

    if wall:
        post = wall[0]["wall"]["attachments"]
        photo = list(filter(lambda x: x["type"]=="photo", post))
        if photo:
            photo_url = photo[0]["photo"]["sizes"][-1]["url"]
            delayed_post(time, photo_url, uploader_api, owner_id)
            return answer(f"Sucssesful added new post to {time}")

    