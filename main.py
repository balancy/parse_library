import os

import requests


def create_dir(path) -> None:
    """Checks if directory exists. If not, create it.

    :param path: directory path
    """

    if not os.path.exists(path):
        os.makedirs(path)


def check_for_redirect(status_code) -> None:
    """Checks if given status_code is redirect status code.

    :param status_code: given status_code
    """

    if status_code == 302:
        raise requests.HTTPError


def read_from_link(link, book_id):
    """Read given link and return its content.

    :param link: given link
    :param book_id: given parameter
    :return: downloaded content of the link
    """

    r = requests.get(link, params={"id": book_id}, verify=False, allow_redirects=False)
    r.raise_for_status()
    check_for_redirect(r.status_code)

    return r.content


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()

    dir_path = "books"
    create_dir(dir_path)

    url = "https://tululu.org/txt.php"

    for i in range(10):
        try:
            response = read_from_link(url, i)
            open(f"{dir_path}/{i}.txt", "wb").write(response)
        except requests.HTTPError:
            pass
