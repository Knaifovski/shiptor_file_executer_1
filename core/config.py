from pydantic import BaseSettings
import os

class Setting(BaseSettings):
    user: str
    password: str
    shiptor_base_host: str
    shiptor_standby_base_host: str
    class Config:
        env_file = os.path.join(os.getcwd(),'.env')