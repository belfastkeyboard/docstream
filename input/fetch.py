import requests
from time import sleep
from threading import Lock
from bs4 import BeautifulSoup
from .cache import store_cache, check_cache


lock = Lock()


def make_request(url: str, retry=3, delay=1, timeout=30) -> bytes | None:
    with lock:
        sleep(5)

        for i in range(retry):
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                return response.content
            except requests.exceptions.RequestException as e:
                print(e)

                if i < retry:
                    sleep(delay)
                else:
                    raise

    return None


def do_fetch(url: str) -> bytes:
    result: bytes = check_cache(url)

    if result:
        return result

    result = make_request(url)

    if result:
        store_cache(url, result)
        return result

    return b''


def fetch_url_content(url: str) -> BeautifulSoup:
    result: bytes = do_fetch(url)

    soup = BeautifulSoup(result, 'html.parser')

    return soup
