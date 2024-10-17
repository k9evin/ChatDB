from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mysql_connection_string: str = "mysql+pymysql://root:574817621@localhost/chatdb"
    mongo_connection_string: str = "mongodb://localhost:27017/"
    mongo_db_name: str = "chatdb"

    class Config:
        env_file = ".env"


settings = Settings()
