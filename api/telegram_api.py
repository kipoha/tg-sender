import requests

from decouple import config as cfg

from typing import Tuple, Union


TELEGRAM_BOT_TOKEN = cfg("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def get_chat(chat_id: Union[str, int]) -> Tuple[bool, str]:
    url = f"{BASE_URL}/getChat"
    response = requests.get(url, params={"chat_id": chat_id})
    data = response.json()

    if data.get("ok"):
        return True, data.get('result', {}).get("title", "Нет названия")
    
    return False, data.get("description", "Ошибка запроса")

