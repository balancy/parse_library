import argparse
import os
import re

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests

BOOKS_FOLDER = "books/"
IMAGES_FOLDER = "images/"
SITE_URL = "https://tululu.org/"


def fetch_parsed_html(book_id):
    """Gets parsed html code from book page.

    :param book_id: book id
    :return: parsed html
    """

    r = requests.get(f"{SITE_URL}/b{book_id}/", verify=False, allow_redirects=False)
    r.raise_for_status()

    if r.status_code == 302:
        raise requests.HTTPError

    soup = BeautifulSoup(r.text, "lxml")
    return soup


def extract_title_author(soup) -> (str, str):
    """Gets book title and author from parsed html.

    :param soup: parsed html
    :return: book title, author
    """

    title_author = soup.find('table', class_='tabs').find('div', id='content').find('h1').text
    title, author = title_author.split('::')

    return title.strip(), author.strip()


def extract_download_image(soup) -> str:
    """Gets book image url and downloads image from this url.

    :param soup: parsed html
    :return: path to the image on the drive
    """

    image_url = soup.find('table', class_='d_book').find('img')['src']
    response = requests.get(f"{SITE_URL}{image_url}", verify=False)
    response.raise_for_status()

    image_name = image_url.split('/')[-1]
    path = f"{IMAGES_FOLDER}{image_name}"

    with open(path, 'wb') as f:
        f.write(response.content)

    return path


def extract_txt_url(soup):
    """Gets relative url to text version of the book.

    :param soup: parsed html
    :return: relative link to text version of the book
    """

    link_to_txt = soup.find('a', title=re.compile('скачать книгу txt'))
    if link_to_txt:
        return link_to_txt['href']


def download_txt(text_url, title) -> str:
    """Downloads text version of the book and returns path to it.

    :param text_url: url where to get file from
    :param title: title of the book
    :return: path to the file
    """

    response = requests.get(f"{SITE_URL}{text_url}", verify=False)
    response.raise_for_status()

    path = f"{BOOKS_FOLDER}{sanitize_filename(title)}.txt"

    with open(path, 'wb') as f:
        f.write(response.content)

    return path


def extract_comments(soup):
    """Gets comments from parsed html.

    :param soup: parsed html
    :return: comments
    """

    comment_elms = soup.find_all('div', class_='texts')
    if comment_elms:
        return [f"'{comment_elm.find('span').text}'" for comment_elm in comment_elms]


def extract_genres(soup):
    """Gets book genres.

    :param soup: parsed html
    :return: book genres
    """

    genre_elms = soup.find_all('a', title=re.compile('перейти к книгам этого жанра'))
    return [genre_elm.text for genre_elm in genre_elms]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download books (title, author, genre, image, comments).")
    parser.add_argument("start_id", help="Book id to start parsing with", type=int)
    parser.add_argument("end_id", help="Book id to end parsing with", type=int)
    args = parser.parse_args()

    requests.packages.urllib3.disable_warnings()

    os.makedirs(BOOKS_FOLDER, exist_ok=True)
    os.makedirs(IMAGES_FOLDER, exist_ok=True)

    for book_id in range(args.start_id, args.end_id):
        try:
            soup = fetch_parsed_html(book_id)
        except requests.HTTPError:
            continue

        title, author = extract_title_author(soup)
        print(f"Название: {title}\nАвтор: {author}")

        path_image = extract_download_image(soup)
        print(f"Путь к изображению: '{path_image}'")

        txt_url = extract_txt_url(soup)
        if txt_url:
            path_txt = download_txt(txt_url, title)
            print(f"Путь к текстовой версии книги: '{path_txt}'")

        comments = extract_comments(soup)
        if comments:
            print(f"Комментарии: {'; '.join(comments)}")

        genres = extract_genres(soup)
        print(f"Жанр книги: {', '.join(genres)}")

        print()
