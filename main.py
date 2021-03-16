import os

import requests


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()

    dir_path = "books"
    create_dir(dir_path)

    url = "https://tululu.org/txt.php"

    for i in range(10):
        r = requests.get(url, params={"id": 32175 + i}, verify=False)
        r.raise_for_status()

        open(f"{dir_path}/{i}.txt", "wb").write(r.content)
