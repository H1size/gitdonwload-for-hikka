#meta developer: @qShad0_bio
import os
import tempfile
import zipfile
from git import Repo
from telethon import TelegramClient, events, sync, utils
from .. import loader, utils
import os
import wget

def download_file(url, output_path=None):
    """
    Скачивает файл по указанному URL с помощью wget.

    :param url: URL файла для скачивания
    :param output_path: Путь для сохранения файла (опционально)
    :return: Путь к скачанному файлу
    """
    try:
        if output_path:
            # Если указан путь для сохранения, используем его
            filename = wget.download(url, out=output_path)
        else:
            # Иначе скачиваем в текущую директорию
            filename = wget.download(url)
        return filename
    except Exception as e:
        return "Error"

class GitRepoMod(loader.Module):
    """Клонирует git репозиторий и отправляет его в виде zip-архива"""

    strings = {'name': 'GitRepo'}

    @loader.command()
    async def git(self, message):
        """Клонирует git репозиторий и отправляет его в виде zip-архива"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Укажите URL git репозитория.</b>")
            return

        url = args.strip()
        await utils.answer(message, "<b>Начинаю загрузку....</b>")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_dir = os.path.join(temp_dir, "repo")
                os.makedirs(repo_dir, exist_ok=True)

                # Клонирование репозитория
                try:
                    repo = Repo.clone_from(url, repo_dir)
                    repo_name = os.path.basename(repo.remotes.origin.url.rstrip('.git'))
                except Exception as e:
                    await utils.answer(message, f"<b>Ошибка при клонировании репозитория: {str(e)}</b>")
                    return

                # Архивация репозитория
                zip_file = os.path.join(temp_dir, f"{repo_name}.zip")
                try:
                    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, _, files in os.walk(repo_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, repo_dir)
                                zipf.write(file_path, arcname)
                except Exception as e:
                    await utils.answer(message, f"<b>Ошибка при архивации репозитория: {str(e)}</b>")
                    return

                await utils.answer_file(message, zip_file, f"<b>Репозиторий {repo_name} в виде zip-архива.</b>")
                await message.delete()

        except Exception as e:
            await utils.answer(message, f"<b>Произошла ошибка: {str(e)}</b>")

    @loader.command()
    async def wget(self, message):
        """Сохраняет файл из интернета"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Укажите URL с файлом</b>")
            return

        url = args.strip()
        await utils.answer(message, "<b>Начинаю загрузку....</b>")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_dir = os.path.join(temp_dir, "wget")
                os.makedirs(repo_dir, exist_ok=True)

                # Клонирование репозитория
                try:
                    repo = download_file(url, repo_dir)
                except Exception as e:
                    await utils.answer(message, f"<b>Ошибка сохранения: {str(e)}</b>")
                    return

                await utils.answer_file(message, repo, f"<b>Файл {url} успешно сохранен</b>")
                await message.delete()

        except Exception as e:
            await utils.answer(message, f"<b>Произошла ошибка: {str(e)}</b>")