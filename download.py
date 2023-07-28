import requests
import io 

def download(link:str)->io.BytesIO:
    file = io.BytesIO(requests.get(link).content)
    file.seek(0)
    return file