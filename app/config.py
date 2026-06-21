from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: float
    db_name: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()  # type: ignore
