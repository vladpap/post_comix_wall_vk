import os
import requests
from random import randint
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote


def get_random_comix():
    comix_count = 2770
    comix_url = f"https://xkcd.com/{randint(0, comix_count)}/info.0.json"
    response = requests.get(comix_url)
    response.raise_for_status()

    comix_info = response.json()
    comix_img_url = comix_info['img']
    comix_file_name = os.path.split(unquote(urlparse(comix_img_url).path))[-1]
    comix_description = comix_info['alt']

    response = requests.get(comix_img_url)
    response.raise_for_status()

    with open(comix_file_name, 'wb') as file:
        file.write(response.content)

    return comix_file_name, comix_description


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

        server_photo_info = response.json()

        return server_photo_info["photo"],\
            server_photo_info["server"],\
            server_photo_info["hash"]


def save_wall_photo(token, group_id, photo_urls, photo_server, photo_hash):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {
        "access_token": token,
        "group_id":  group_id,
        "v": 5.131,
        "photo": photo_urls,
        "server": photo_server,
        "hash": photo_hash,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()

    wall_photo_info = response.json()["response"][0]

    return wall_photo_info["owner_id"], wall_photo_info["id"]


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
    VK_ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN")
    VK_GROUP_ID = os.getenv("VK_GROUP_ID")

    try:
        comix_file_name, comix_description = get_random_comix()

        upload_server_url = get_upload_server_url(VK_ACCESS_TOKEN,VK_GROUP_ID)

        photo_urls, photo_server, photo_hash = upload_photo_server(
            upload_server_url,
            comix_file_name)

        photo_owner_id, photo_id = save_wall_photo(VK_ACCESS_TOKEN,
                                                   VK_GROUP_ID,
                                                   photo_urls,
                                                   photo_server,
                                                   photo_hash)

        posting_wall(VK_ACCESS_TOKEN,
                     VK_GROUP_ID,
                     comix_description,
                     photo_owner_id,
                     photo_id)
    except Exception as e:
        raise e
    finally:
        os.remove(comix_file_name)


if __name__ == "__main__":
    main()
