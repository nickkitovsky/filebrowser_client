from typing import Literal

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class LoggerConfig(BaseModel):
    format: str = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"  # noqa: E501
    console_log_level: LogLevel = "DEBUG"
    file_log_level: LogLevel = "WARNING"
    date_format: str = "%Y-%m-%d %H:%M:%S"


class ApiCredentials(BaseSettings):
    filebrowser_user: SecretStr
    filebrowser_password: SecretStr
    filebrowser_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class SessionConfig(BaseModel):
    timeout_s: int = 5
    speed_limit_bytes: int = 500 * 1024
    headers: dict[str, str] = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",  # noqa: E501
    }


session_config = SessionConfig()
logger_config = LoggerConfig()
api_creds = ApiCredentials()  # type: ignore[call-arg]
