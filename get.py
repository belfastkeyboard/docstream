import requests
from time import sleep
from threading import Lock
from cache import store_cache, check_cache

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


def get_content(url: str) -> bytes | None:
    cached_result: tuple | None = check_cache(url)

    if cached_result:
        return cached_result[0]

    online_result: bytes = make_request(url)

    if online_result:
        store_cache(url, online_result)
        return online_result

    return None
