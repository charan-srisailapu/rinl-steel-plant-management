import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "mysql+asyncmy://root:password@localhost:3306/rinl_steel_plant"
    jwt_secret: str = "rinl-steel-plant-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")


settings = Settings()
