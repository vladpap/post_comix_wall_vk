import os
import requests
from random import randint
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote


class VkApiError(Exception):
    pass


def get_random_comix():
    comix_count = 2770
    comix_url = f"https://xkcd.com/{randint(0, comix_count)}/info.0.json"
    response = requests.get(comix_url)
    response.raise_for_status()

    comix_metadata = response.json()
    comix_img_url = comix_metadata['img']
    comix_file_name = os.path.split(unquote(urlparse(comix_img_url).path))[-1]
    comix_description = comix_metadata['alt']

    response = requests.get(comix_img_url)
    response.raise_for_status()

    with open(comix_file_name, 'wb') as file:
        file.write(response.content)

    return comix_file_name, comix_description


def raise_vk_response_for_error(vk_response, msg=""):
    if "error" in vk_response:
        error = vk_response["error"]
        except_message = "VK API Error ({}):\ncode: {}\n{}".format(
            msg, error['error_code'], error['error_msg'])
        raise VkApiError(except_message)


def get_upload_server_url(token, group_id):
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    params = {
        "access_token": token,
        "v": 5.131,
        "group_id": group_id,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    server_url_metadata = response.json()

    raise_vk_response_for_error(server_url_metadata,
                                msg="Method getWallUploadServer")

    return server_url_metadata["response"]["upload_url"]


def upload_photo_server(url, file_name):
    with open(file_name, "rb") as photo_file:
        files = {"photo": photo_file}
        response = requests.post(url, files=files)
    response.raise_for_status()

    server_photo_metadata = response.json()

    if server_photo_metadata["photo"] == "[]":
        raise VkApiError("Error upload photo on server.")

    return server_photo_metadata["photo"],\
        server_photo_metadata["server"],\
        server_photo_metadata["hash"]


def save_wall_photo(token, group_id, photo_urls, photo_server, photo_hash):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {
        "access_token": token,
        "group_id": group_id,
        "v": 5.131,
        "photo": photo_urls,
        "server": photo_server,
        "hash": photo_hash,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()

    raise_vk_response_for_error(response.json(),
                                msg="Method photos.saveWallPhoto")

    wall_photo_metadata = response.json()["response"][0]

    return wall_photo_metadata["owner_id"], wall_photo_metadata["id"]


def posting_wall(token, group_id, message, photo_owner_id, photo_id):
    url = "https://api.vk.com/method/wall.post"
    params = {
        "access_token": token,
        "v": 5.131,
        "owner_id": "-{}".format(group_id),
        "message": message,
        "attachments": "photo{}_{}".format(photo_owner_id, photo_id)
        }
    response = requests.post(url, params=params)
    response.raise_for_status()

    raise_vk_response_for_error(response.json(),
                                msg="Method wall.post")


def main():
    load_dotenv()
    vk_access_token = os.environ.get("VK_ACCESS_TOKEN")
    vk_group_id = os.environ.get("VK_GROUP_ID")

    error_environ = ""
    if not vk_access_token:
        error_environ = \
            "\nError: not defined environment variable 'VK_ACCESS_TOKEN'."
    if not vk_group_id:
        error_environ += \
            "\nError: not defined environment variable 'VK_GROUP_ID'."

    if error_environ:
        print(error_environ)
        exit(0)

    try:

        comix_file_name, comix_description = get_random_comix()

        upload_server_url = get_upload_server_url(vk_access_token, vk_group_id)

        photo_urls, photo_server, photo_hash = upload_photo_server(
            upload_server_url,
            comix_file_name)

        photo_owner_id, photo_id = save_wall_photo(vk_access_token,
                                                   vk_group_id,
                                                   photo_urls,
                                                   photo_server,
                                                   photo_hash)

        posting_wall(vk_access_token,
                     vk_group_id,
                     comix_description,
                     photo_owner_id,
                     photo_id)
    except VkApiError as e:
        print(e)
        print("line", e.__traceback__.tb_lineno)
    finally:
        os.remove(comix_file_name)


if __name__ == "__main__":
    main()
