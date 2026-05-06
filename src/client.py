from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urljoin

from curl_cffi import CurlOpt, Session
from curl_cffi.requests.exceptions import HTTPError, RequestException
from curl_cffi.requests.impersonate import DEFAULT_CHROME, BrowserTypeLiteral
from curl_cffi.requests.models import Response

from .config import SessionConfig
from .logger import get_logger

logger = get_logger(__name__)


class SessionFactory:
    """Фабрика для создания и настройки HTTP сессий."""

    def __init__(self, config: SessionConfig):
        self.config = config

    @contextmanager
    def create_session(
        self,
        impersonate: BrowserTypeLiteral = DEFAULT_CHROME,
        token: str = "",
    ) -> Generator[Session[Response], Any, None]:
        """Создает и настраивает сессию в виде контекстного менеджера."""
        session = Session(
            headers=self.config.headers.copy(),
            impersonate=impersonate,
        )
        if token:
            session.headers.update({"X-Auth": token})
        session.curl.setopt(CurlOpt.TIMEOUT, self.config.timeout_s)
        session.curl.setopt(CurlOpt.MAX_RECV_SPEED_LARGE, self.config.speed_limit_bytes)

        try:
            yield session
        finally:
            session.close()


class TokenProvider:
    """Отвечает за получение и хранение токена аутентификации."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        session_factory: SessionFactory,
    ):
        self.base_url = base_url
        self.username = username
        self.password = password
        self._token: str = ""
        self.session_factory = session_factory

    def get_token(self) -> str:
        if not self._token:
            self._fetch_token()
        return self._token

    def invalidate_token(self) -> None:
        """Сбрасывает текущий токен, чтобы при следующем запросе был получен новый."""
        self._token = ""

    def _fetch_token(self) -> None:
        url = urljoin(self.base_url, "/api/login")
        payload = {"username": self.username, "password": self.password}

        try:
            logger.info("Попытка авторизации...")
            with self.session_factory.create_session() as session:
                response = session.post(url, json=payload)
                response.raise_for_status()
                self._token = response.text.strip('"')
            logger.info("Успешная авторизация. Токен получен.")
        except RequestException as e:
            logger.error("Сетевая ошибка при авторизации: %s", e)  # noqa: TRY400
            raise
        except ValueError as e:
            logger.error("Ошибка парсинга ответа сервера: %s", e)  # noqa: TRY400
            raise
        except Exception:
            logger.exception("Непредвиденная ошибка при логине")
            raise


class FileBrowserClient:
    def __init__(
        self,
        base_url: str,
        token_provider: TokenProvider,
        session_factory: SessionFactory,
    ):
        self.base_url = base_url
        self.token_provider = token_provider
        self.session_factory = session_factory

    def _make_request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        url: str,
        *,
        raise_for_status: bool = True,
        stream: bool = False,
    ) -> Response:
        try:
            token = self.token_provider.get_token()
            with self.session_factory.create_session(token=token) as session:
                response = session.request(method, url, stream=stream)
                if raise_for_status and response:
                    response.raise_for_status()
                return response  # pyright: ignore[reportReturnType]
        except HTTPError as e:
            if (
                e.response is not None
                and e.response.status_code == 401  # Unauthorized  # noqa: PLR2004
            ):
                logger.warning("Токен истек или недействителен. Попытка обновления...")
                self.token_provider.invalidate_token()
                token = self.token_provider.get_token()  # Получаем новый токен
                with self.session_factory.create_session(token=token) as session:
                    response = session.request(method, url, stream=stream)
                    if raise_for_status and response:
                        response.raise_for_status()
                    return response  # pyright: ignore[reportReturnType]
            raise

    def ls(self, directory_path: str = "/", *, files_only: bool = False) -> list:
        url = urljoin(self.base_url, f"/api/resources{directory_path}")
        try:
            response = self._make_request("GET", url)
            if files_only:
                files: list[str] = [
                    item["path"]
                    for item in response.json().get("items", [])
                    if not item.get("isDir")
                ]
            else:
                files = [item["path"] for item in response.json().get("items", [])]
            logger.info(
                "В директории '%s' найдено %s элементов.",
                directory_path,
                len(files),
            )
        except KeyError as e:
            logger.error("Ошибка парсинга JSON ответа: %s", e)  # noqa: TRY400
        except ValueError as e:
            logger.error("Ошибка парсинга JSON ответа: %s", e)  # noqa: TRY400
        except RequestException as e:
            logger.error("Ошибка получения списка файлов: %s", e)  # noqa: TRY400
        else:
            return files
        return []

    def download_file(
        self,
        file: str,
        download_dir: str = "./downloads",
    ) -> Path | None:
        url = urljoin(self.base_url, f"/api/raw{file}")
        save_dir = Path(download_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        file_path = Path(file)
        save_path = save_dir / file_path.name
        logger.info("Выбран файл для скачивания: %s", file_path.name)

        try:
            response = self._make_request("GET", url, stream=True)
            with save_path.open(mode="wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            logger.info("Файл успешно сохранен по пути: %s", save_path)
        except OSError as e:
            logger.error(  # noqa: TRY400
                "Ошибка ввода/вывода при записи файла %s: %s",
                save_path,
                e,
            )
        except Exception:
            logger.exception(
                "Критическая ошибка при скачивании файла %s",
                file_path.name,
            )
        else:
            return save_path
        return None
