import os
import requests
from random import randint
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote


def save_image_from_url(url, file_name, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    with open(file_name, 'wb') as file:
        file.write(response.content)


def get_comix_info(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_upload_server_url(token, group_id):
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    params = {
        "access_token": token,
        "v": 5.131,
        "group_id": group_id,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()["response"]["upload_url"]


def upload_photo_server(url, file_name):
    with open(file_name, "rb") as photo_file:
        files = {"photo": photo_file}
        response = requests.post(url, files=files)
        response.raise_for_status()

        return response.json()["photo"],\
            response.json()["server"],\
            response.json()["hash"]


def save_wall_photo(token, group_id, photo_urls, photo_server, photo_hash):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {
        "access_token": os.getenv("VK_ACCESS_TOKEN"),
        "group_id":  os.getenv("VK_GROUP_ID"),
        "v": 5.131,
        "photo": photo_urls,
        "server": photo_server,
        "hash": photo_hash,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()

    return response.json()["response"][0]["owner_id"],\
        response.json()["response"][0]["id"]


def posting_wall(token, group_id, message, photo_owner_id, photo_id):
    url = "https://api.vk.com/method/wall.post"
    params = {
        "access_token": token,
        "v": 5.131,
        "owner_id": "-{}".format(group_id),
        "from_group": group_id,
        "message": message,
        "attachments": "photo{}_{}".format(photo_owner_id, photo_id)
        }
    response = requests.post(url, params=params)
    response.raise_for_status()


def main():
    load_dotenv()

    comix_count = 2770
    comix_url = f"https://xkcd.com/{randint(0, comix_count)}/info.0.json"
    comix_info = get_comix_info(comix_url)
    comix_img_url = comix_info['img']
    comix_file_name = os.path.split(unquote(urlparse(comix_img_url).path))[-1]
    save_image_from_url(comix_img_url, comix_file_name)
    alt_comix = comix_info['alt']

    upload_server_url = get_upload_server_url(
                            os.getenv("VK_ACCESS_TOKEN"),
                            os.getenv("VK_GROUP_ID"))

    photo_urls, photo_server, photo_hash = upload_photo_server(
        upload_server_url,
        comix_file_name)

    photo_owner_id, photo_id = save_wall_photo(os.getenv("VK_ACCESS_TOKEN"),
                                               os.getenv("VK_GROUP_ID"),
                                               photo_urls,
                                               photo_server,
                                               photo_hash)

    posting_wall(os.getenv("VK_ACCESS_TOKEN"),
                 os.getenv("VK_GROUP_ID"),
                 alt_comix,
                 photo_owner_id,
                 photo_id)

    os.remove(comix_file_name)


if __name__ == "__main__":
    main()
