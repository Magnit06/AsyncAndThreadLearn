from __future__ import annotations
import os
import asyncio
from pprint import pprint
from time import time
from abc import abstractmethod, ABC

import requests
import aiohttp
import aiofile

URL_TO_PHOTO: str = 'https://jsonplaceholder.typicode.com/photos/'
URL_TO_ALBUM: str = 'https://jsonplaceholder.typicode.com/albums/'
PATH: str = './photos'
STEP: int = 5000 // 8


def async_time_tracking(fun):
    """Асинхронный декоратор подсчета времени выполнения"""

    async def wrapper(*args, **kwargs) -> str:
        init_time = time()
        res_fun = await fun(*args, **kwargs)
        res_time = time() - init_time
        return f"{res_fun}\nВремя выполнения {fun.__name__} {res_time} с"

    return wrapper


async def save_photo(content, dir_name, photo_name) -> str:
    """сохраняем фотографии"""
    path_to_save: str = os.path.join(PATH, str(dir_name) + '/')
    full_path: str = os.path.normpath(path_to_save + str(photo_name) + str('.png'))
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)
    async with aiofile.async_open(full_path, 'wb') as img:
        await img.write(content)
    print(f"Скачано фото: {photo_name + '.png'}")
    return f"Скачано фото путь: {full_path}"


async def fetch_content(url, session, dir_name, photo_name) -> str:
    """
    Получаем фотографии
    """
    async with session.get(url=url, allow_redirects=True) as response:
        content = await response.read()
        return await save_photo(content, dir_name, photo_name)


@async_time_tracking
async def main() -> None:
    """
    Создаем задачи
    """
    parser = Parser(prepare_logic=PrepareAlbums(), url=URL_TO_ALBUM)
    albums: dict = parser.dict_data_from_json()
    # меняем на другой вариант подготовки данных
    parser.prepare_logic = PreparePhotos()
    parser.url = URL_TO_PHOTO
    photos: dict = parser.dict_data_from_json()
    # собираем данные в один лист для удобства
    package_data = PackageData(packed_albums=albums, packed_photos=photos)
    compressed_data: list = package_data.package()
    array_task: list = []
    async with aiohttp.ClientSession() as session:
        for data in compressed_data:
            task = asyncio.create_task(fetch_content(url=data[2],
                                                     session=session,
                                                     dir_name=data[0],
                                                     photo_name=data[1]))
            array_task.append(task)
        results = await asyncio.gather(*array_task)
    pprint(results)


class PrepareLogic(ABC):

    @abstractmethod
    def prepare_data(self, json_data: list[dict]) -> dict:
        pass


class PrepareAlbums(PrepareLogic):

    def prepare_data(self, json_data: list[dict]) -> dict:
        """Забираем нужные данные альбома в удобный вид"""
        all_album: dict = {}
        for album in json_data:
            all_album[album['id']] = album['title']
        return all_album


class PreparePhotos(PrepareLogic):

    def prepare_data(self, json_data: list[dict]) -> dict:
        """Забираем нужные данные фото в удобный вид"""
        all_photo: dict = {}
        for photo in json_data:
            all_photo[photo['id']] = [photo['albumId'], photo['title'], photo['url']]
        return all_photo


class Parser:

    def __init__(self, prepare_logic: PrepareLogic, url: str) -> None:
        self._prepare_logic = prepare_logic
        self.url = url

    @property
    def prepare_logic(self) -> PrepareLogic:
        return self._prepare_logic

    @prepare_logic.setter
    def prepare_logic(self, prepare_logic: PrepareLogic) -> None:
        self._prepare_logic = prepare_logic

    def dict_data_from_json(self) -> dict:
        """Получаем только необходимые данные от json-формата"""
        data_json = Parser.get_json_data(url=self.url)
        dict_data = self._prepare_logic.prepare_data(json_data=data_json)
        return dict_data

    @staticmethod
    def get_json_data(url: str) -> list[dict]:
        """возвращаем ответ json от указанного адреса"""
        response = requests.get(url=url)
        return response.json()


class PackageData:
    """Класс собирает все необходимые данные в удобный формат"""

    def __init__(self, packed_albums: dict, packed_photos: dict) -> None:
        self.packed_albums = packed_albums
        self.packed_photos = packed_photos

    def package(self) -> list:
        """собираем данные в единый лист
        list['название альбома', 'название фотографии', 'url для скачивания']
        """
        package_data: list = []
        for key, value in self.packed_photos.items():
            package_data.append([self.packed_albums[value[0]], value[1], value[2]])
        return package_data


if __name__ == '__main__':
    print(asyncio.run(main()))
