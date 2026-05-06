from src.client import FileBrowserClient, SessionFactory, TokenProvider
from src.config import api_creds, session_config

url = api_creds.filebrowser_url
session_factory = SessionFactory(config=session_config)
token_provider = TokenProvider(
    base_url=url,
    username=api_creds.filebrowser_user.get_secret_value(),
    password=api_creds.filebrowser_password.get_secret_value(),
    session_factory=session_factory,
)
client = FileBrowserClient(
    base_url=url,
    token_provider=token_provider,
    session_factory=session_factory,
)
