# File Browser Client

Клиент на Python для взаимодействия с API [File Browser](https://filebrowser.org/).

## Описание

Этот клиент предоставляет удобный интерфейс для выполнения основных операций с файлами на сервере File Browser, таких как получение списка файлов и их скачивание.

## Основные возможности

- Автоматическая аутентификация и получение токена.
- Автоматическое обновление токена при его истечении (обработка ошибки 401).
- Получение списка файлов и директорий.
- Скачивание файлов с сервера.
- Гибкая настройка сессий (timeout, user-agent, ограничение скорости).
- Подробное логирование операций.

## Установка

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/nickkitovsky/filebrowser-client.git
    cd filebrowser-client
    ```

2.  **Создайте и активируйте виртуальное окружение:**
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # macOS / Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

## Настройка

Перед использованием клиента необходимо настроить переменные окружения.

1.  Создайте файл `.env` в корневой директории проекта, скопировав содержимое из `.env_template`.

2.  Заполните файл `.env` вашими учетными данными:
    ```plaintext
    filebrowser_user="your_username"
    filebrowser_password="your_password"
    filebrowser_url="http://your-filebrowser-instance.com"
    ```

## Пример использования

Основная логика инициализации и использования клиента находится в файле `main.py`. Вы можете запустить его для проверки работоспособности.

```bash
python main.py
```