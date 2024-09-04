#meta developer: @qShad0
import os
import subprocess
import shutil
import tempfile

from telethon import TelegramClient, events, sync, utils

from .. import loader, utils

class GitRepoMod(loader.Module):
    """Клонирует репозиторий GitHub и отправляет его в виде zip-архива"""

    strings = {'name': 'GitRepo'}

    @loader.command()
    async def git(self, message):
        """Клонирует репозиторий GitHub и отправляет его в виде zip-архива"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("Укажите URL репозитория GitHub.")
            return

        url = args.strip()

        # Проверка URL
        if not url.startswith("https://github.com/"):
            await message.edit("Неверный формат URL. URL должен быть в формате https://github.com/<user>/<repo>")
            return

        try:
            # Создание временной директории с помощью contextmanager
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_dir = os.path.join(temp_dir, "repo")
                zip_file = os.path.join(temp_dir, "repo.zip")

                # Создание папки repo, если она не существует
                os.makedirs(repo_dir, exist_ok=True)

                # Клонирование репозитория
                process = subprocess.run(['git', 'clone', url, repo_dir], capture_output=True, text=True)
                if process.returncode != 0:
                    error_message = f"Ошибка при клонировании репозитория: {process.stderr}"
                    await message.edit(error_message)
                    return

                # Архивация репозитория
                process = subprocess.run(['zip', '-r', zip_file, repo_dir], capture_output=True, text=True)
                if process.returncode != 0:
                    error_message = f"Ошибка при архивации репозитория: {process.stderr}"
                    await message.edit(error_message)
                    return

                await message.client.delete_messages(message.chat_id, message.id)
                # Отправка файла
                await message.client.send_file(message.chat_id, zip_file, caption="Вот ваш репозиторий в виде zip-архива.")

        except Exception as e:
            await message.edit(f"Произошла ошибка: {e}")