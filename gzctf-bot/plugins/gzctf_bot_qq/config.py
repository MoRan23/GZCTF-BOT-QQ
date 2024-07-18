from pydantic import BaseModel


class Config(BaseModel):
    CONFIG: dict = {
        "SEND_LIST": [972788436],
        "GAME_LIST": [],
        "GZCTF_URL": "https://nnd.edaker.com/",
        "GZ_USER": "admin",
        "GZ_PASS": "Test123.",
    }