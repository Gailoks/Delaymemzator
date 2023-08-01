from dataclasses import dataclass
from datetime import datetime
from enum import Enum

@dataclass
class Meme:
    datetime: datetime
    url: str