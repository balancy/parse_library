import os
import re

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests


BOOKS_FOLDER = "books/"
IMAGES_FOLDER = "images/"
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


def get_title_image(html) -> (str, str):
    """Gets book title and image link from html.

    :param html: html code
    :return: book title and image link
    """

    soup = BeautifulSoup(html, "lxml")
    title_author = soup.find('table', class_='tabs').find('div', id='content').find('h1').text
    title, author = title_author.split('::')
    image_url = soup.find('table', class_='d_book').find('img')['src']

    return f"{sanitize_filename(title.strip())}", image_url


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


def download_image(url, folder='images/') -> str:
    """Saves image in given folder.

    :param url: link where to get image
    :param folder: folder where to save image
    :return: path to the image
    """

    create_dir(folder)

    response = requests.get(f"{SITE_URL}{url}", verify=False)
    response.raise_for_status()

    image_name = url.split('/')[-1]
    path = f"{folder}{image_name}"

    with open(path, 'wb') as f:
        f.write(response.content)

    return path


def get_comments(html) -> list:
    """Gets comments from html code.

    :param html: html code
    :return: comments
    """

    soup = BeautifulSoup(html, 'lxml')
    comment_elms = soup.find_all('div', class_='texts')

    comments = list()
    if comment_elms:
        for comment_elm in comment_elms:
            comments.append(comment_elm.find('span').text)

    return comments


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()

    for book_id in range(1, NUMBER_BOOKS):
        try:
            html = get_html(SITE_URL, book_id)
            title, image_url = get_title_image(html)
            path_image = download_image(image_url, IMAGES_FOLDER)
            relative_txt_link = get_txt_link(html)
            path_book = download_txt(relative_txt_link, f"{title}.txt", BOOKS_FOLDER)
            comments = get_comments(html)
            if comments:
                print(comments)
        except requests.HTTPError:
            print(f"For book with id={book_id} there is a redirection")
        except FileNotFoundError:
            print(f"For book with id={book_id} txt file is not found")
