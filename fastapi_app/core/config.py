from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Настройки приложения для интеграции Django, FastAPI и Telegram-бота."""

    # База данных
    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_server: str = Field(alias="POSTGRES_SERVER", default="localhost")
    postgres_port: int = Field(alias="POSTGRES_PORT", default=5000)

    # Telegram-бот
    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")

    # VK API
    vk_access_token: str = Field(alias="VK_ACCESS_TOKEN")
    vk_group_id: str = Field(alias="VK_GROUP_ID")

    # Данные первого суперпользователя
    first_superuser_first_name: str = Field(alias="FIRST_SUPERUSER_FIRST_NAME")
    first_superuser_last_name: str = Field(alias="FIRST_SUPERUSER_LAST_NAME")
    first_superuser_middle_name: str = Field(alias="FIRST_SUPERUSER_MIDDLE_NAME")
    first_superuser_telegram_id: int = Field(alias="FIRST_SUPERUSER_TELEGRAM_ID", default=0)
    first_superuser_role: str = Field(alias="FIRST_SUPERUSER_ROLE", default="ADMIN")
    first_superuser_email: str = Field(alias="FIRST_SUPERUSER_EMAIL")
    first_superuser_phone: str = Field(alias="FIRST_SUPERUSER_PHONE")
    first_superuser_additional_info: str = Field(alias="FIRST_SUPERUSER_ADDITIONAL_INFO", default=None)
    first_superuser_password: str = Field(alias="FIRST_SUPERUSER_PASSWORD")

    # Web-сервер
    web_server_host: str = Field(alias="WEB_SERVER_HOST", default="0.0.0.0")
    web_server_port: int = Field(alias="WEB_SERVER_PORT", default=8443)

    @property
    def database_url(self) -> str:
        """Создание строки подключения к базе данных для asyncpg."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(
        env_file="../infra/.env",  # Путь относительно текущей директории
        case_sensitive=False,
        env_file_encoding="utf-8",
    )

settings = Settings()
