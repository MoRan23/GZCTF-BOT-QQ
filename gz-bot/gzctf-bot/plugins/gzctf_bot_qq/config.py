from pydantic import BaseModel


class Config(BaseModel):
    CONFIG: dict = {
        "SEND_LIST": [],
        "GAME_LIST": [],
        "GZCTF_URL": "",
        "GZ_USER": "",
        "GZ_PASS": "",
    }