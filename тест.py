import asyncio
import aiohttp
import os
import json
import hashlib

# Функция для загрузки файлов из репозитория
async def download_repo(repo_url, temp_folder):
    async with aiohttp.ClientSession() as session:
        async with session.get(repo_url) as resp:  # Получаем содержимое репозитория
            if resp.status == 200:  # Если запрос успешен
                os.makedirs(temp_folder, exist_ok=True)  # Создаем временную папку, если ее нет
                files = json.loads(await resp.text())  # Преобразуем JSON-ответ в объект Python
                for file in files:  # Проходим по каждому файлу в репозитории
                    url = file['url']  # Получаем URL файла
                    file_path = os.path.join(temp_folder, file['path'])  # Создаем путь до файла
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Создаем папки для файла, если их нет
                    async with session.get(url) as file_resp:  # Получаем содержимое файла
                        if file_resp.status == 200:  # Если запрос успешен
                            with open(file_path, 'wb') as f:  # Создаем файл и записываем в него содержимое
                                f.write(await file_resp.content.read())


# Функция для расчета хеш-сумм файлов в папке
async def calculate_hashes(folder):
    hashes = {}
    for dirpath, _, filenames in os.walk(folder):  # Проходим по всем папкам и файлам в заданной папке
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)  # Создаем путь до файла
            with open(file_path, 'rb') as f:  # Открываем файл в бинарном режиме
                content = f.read()  # Считываем содержимое файла
            file_hash = hashlib.sha256(content).hexdigest()  # Рассчитываем хеш-сумму содержимого файла
            hashes[file_path] = file_hash  # Сохраняем хеш-сумму для файла
    return hashes


async def main():
    repo_url = 'https://gitea.radium.group/api/v1/repos/radium/project-configuration/contents'  # URL репозитория
    temp_folder = './temp'  # Временная папка для загрузки файлов
    await download_repo(repo_url, temp_folder)  # Загружаем файлы из репозитория
    hashes = await calculate_hashes(temp_folder)  # Рассчитываем хеш-суммы для файлов в папке
    with open('hashes.txt', 'w') as f:  # Открываем файл для записи хеш-сумм
        for file_path, file_hash in hashes.items():  # Проходим по всем хеш-суммам файлов
            f.write(f'{file_path}: {file_hash}\n')  # Записываем путь до файла и его хеш-сумму в файл


if __name__ == '__main__':
    asyncio.run(main())  # Запускаем основную функцию с помощью asyncio
