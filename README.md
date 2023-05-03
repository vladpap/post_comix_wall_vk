![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![VK](https://img.shields.io/badge/вконтакте-%232E87FB.svg?&style=for-the-badge&logo=vk&logoColor=white)
# Пост комиксов на стене группы [вк](https://vk.com/)

Размешение на стене группы [ВКонтакте](https://vk.com/) комикса руки [Рэндела Манро](https://xkcd.com) выбранное случайным образом. 

## Установка.
- Python3 должен быть уже установлен.
- Рекомендуется использовать среду окружения [venv](https://docs.python.org/3/library/venv.html) 
для изоляции проекта.
 - Используйте `pip` (или `pip3`, если есть конфликт с Python2) для установки зависимостей
```console
$ pip install -r requirements.txt
```

- Создать группу ВКонтакте.

- Создать приложение с правами: `photos`, `groups`, `wall` и `offline`.

- Получить токен

- Создать файл `.env` с переменными:
    - `VK_GROUP_ID` - id группы ВКонтакте, куда постить комиксы;
    - `VK_ACCESS_TOKEN` токен приложения ВКонтакте.
```console
VK_GROUP_ID=***********
VK_ACCESS_TOKEN=**********
```

## Запуск

```console
$ python main.py
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python [Devman](https://dvmn.org).


<img src="https://dvmn.org/assets/img/logo.8d8f24edbb5f.svg" alt= “” width="102" height="25">
