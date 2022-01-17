"""
1 домашнее задание
"""
import os
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import requests
from requests import Response

URL_TO_PHOTO: str = 'https://jsonplaceholder.typicode.com/photos/'
URL_TO_ALBUM: str = 'https://jsonplaceholder.typicode.com/albums/'
PATH: str = './photos'


def time_tracking(fun):
    """Декоратор подсчета времени выполнения"""
    from datetime import datetime

    def wrapper(*args, **kwargs) -> str:
        init_time = datetime.now()
        res_fun: Any = fun(*args, **kwargs)
        res_time = datetime.now() - init_time
        return f"{res_fun}\nВремя выполнения {fun.__name__} {res_time.seconds} с"

    return wrapper


@time_tracking
def save_photo(all_data: list) -> str:
    """сохраняем фотографии"""
    i = 0
    for data in all_data:
        path_to_save: str = os.path.join(PATH, str(data[0]) + '/')
        full_path: str = os.path.normpath(path_to_save + str(data[1]) + str('.png'))
        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)
        photo_to_save: Response = requests.get(data[2])
        with open(full_path, 'wb') as img:
            img.write(photo_to_save.content)
        i += 1
        print(f"Скачано фото {full_path}")
    return f"Скачано {i} фотографий"


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


@time_tracking
def main() -> None:
    parser = Parser(prepare_logic=PrepareAlbums(), url=URL_TO_ALBUM)
    albums: dict = parser.dict_data_from_json()
    # меняем на другой вариант подготовки данных
    parser.prepare_logic = PreparePhotos()
    parser.url = URL_TO_PHOTO
    photos: dict = parser.dict_data_from_json()
    # собираем данные в один лист для удобства
    package_data = PackageData(packed_albums=albums, packed_photos=photos)
    compressed_data: list = package_data.package()
    with ThreadPoolExecutor(max_workers=4) as workers:
        results = workers.map(save_photo,
                              (compressed_data[0:1250],
                               compressed_data[1250:2500],
                               compressed_data[2500:3750],
                               compressed_data[3750:5000]))
        for result in results:
            print(result)


if __name__ == '__main__':
    print(main())
