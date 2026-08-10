from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: float
    db_name: str
    redis_url: str
    cache_ttl_sec: int

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()  # type: ignore
