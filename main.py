import os
import re

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests


FOLDER = "books/"
SITE_URL = "https://tululu.org/"
NUMBER_BOOKS = 10


def check_for_redirect(status_code) -> None:
    """Checks if given status_code is redirect status code.

    :param status_code: given status_code
    """

    if status_code == 302:
        raise requests.HTTPError


def get_html(link, book_id) -> str:
    """Gets html code from given link.

    :param link: site link
    :param book_id: id of the book on site
    :return: html code
    """

    r = requests.get(f"{link}/b{book_id}/", verify=False, allow_redirects=False)
    r.raise_for_status()
    check_for_redirect(r.status_code)

    return r.text


def get_filename(html) -> str:
    """Gets filename from html. It'll be the html title with .txt extension.

    :param html: html code
    :return: filename
    """

    soup = BeautifulSoup(html, "lxml")
    searching_line = soup.find('table', class_='tabs').find('div', id='content').find('h1').text
    title, author = searching_line.split('::')

    return f"{sanitize_filename(title.strip())}.txt"


def create_dir(path) -> None:
    """Checks if directory exists. If not, create it.

    :param path: directory path
    """

    if not os.path.exists(path):
        os.makedirs(path)


def get_txt_link(html) -> str:
    """Getting relative link to download txt.

    :param html: html code
    :return: relative link to download txt
    """

    soup = BeautifulSoup(html, 'lxml')
    link_to_txt = soup.find('a', title=re.compile('скачать книгу txt'))
    if not link_to_txt:
        raise FileNotFoundError

    return link_to_txt['href']


def download_txt(url, filename, folder='books/') -> str:
    """Downloads txt file and saves it in given folder.

    :param url: link where to get file
    :param filename: name of file to save
    :param folder: folder where to save file
    :return: path to the file
    """

    create_dir(folder)
    path = f"{folder}{sanitize_filename(filename)}"

    response = requests.get(f"{SITE_URL}{url}", verify=False)
    response.raise_for_status()

    with open(path, 'wb') as f:
        f.write(response.content)

    return path


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()

    for book_id in range(1, NUMBER_BOOKS):
        try:
            html = get_html(SITE_URL, book_id)
            filename = get_filename(html)
            relative_txt_link = get_txt_link(html)
            path = download_txt(relative_txt_link, filename, FOLDER)
        except requests.HTTPError:
            print(f"For book with id={book_id} there is a redirection")
        except FileNotFoundError:
            print(f"For book with id={book_id} txt file is not found")
