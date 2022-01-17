# AsyncAndThreadLearn
## Первое домашнее задание
### Описание
Реализовать парсер [с сайта](https://jsonplaceholder.typicode.com/) в несколько потоков или процессов, объекты 
[albums/](https://jsonplaceholder.typicode.com/albums/) и [photos/](https://jsonplaceholder.typicode.com/photos/).


Скачиваем все альбомы и фотографии, кладем их по папкам /альбом/название_фотографии

#### Требования:

Парсер реализовать на ООП, соблюдая SOLID.
Для соединения по http можно использовать [это](https://docs.python-requests.org/en/latest/).

Необходимо реализовать декоратор, для замерки работы времени всего скрипта, необходимо реализовать декоратор для замерки времени метода, который скачивает.

## Второе домашнее задание
### Описание

Реализовать парсер с [сайта](https://jsonplaceholder.typicode.com/) используя асинхронность, объекты [albums/](https://jsonplaceholder.typicode.com/albums/) 
и [photos/](https://jsonplaceholder.typicode.com/photos/).
Скачиваем все альбоы и фотографии, кладем их по папкам /альбом/название_фотографии

#### Требования:

Парсер реализовать на ООП, соблюдая SOLID.
Использовать aiohttp, aiofiles для работы с http и файлами.

Необходимо реализовать декоратор, для замерки работы времени всего скрипта.