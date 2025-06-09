from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_server: str = Field(alias="POSTGRES_SERVER")
    postgres_port: int = Field(alias="POSTGRES_PORT")

    @property
    def database_url(self) -> str:
        """Создание строки подключения к базе данных."""
        return (
            f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@'
            f'{self.postgres_server}:{self.postgres_port}/{self.postgres_db}'
        )


    model_config = SettingsConfigDict(
        env_file="../infra/.env",
        case_sensitive=False)


settings = Settings()
