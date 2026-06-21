from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: float

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()  # type: ignore
