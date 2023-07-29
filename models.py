from dataclasses import dataclass
from datetime import datetime

@dataclass
class Meme:
    datetime: datetime
    url: str
    