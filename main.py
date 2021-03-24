import argparse
import json
import os
import re

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests

from parse_tululu_category import find_books_urls

BOOKS_FOLDER = "books/"
IMAGES_FOLDER = "images/"
SITE_URL = "https://tululu.org/"


def fetch_parsed_html_by_id(book_id):
    """Gets parsed html code from book page by its od.

    :param book_id: book id
    :return: parsed html
    """

    r = requests.get(f"{SITE_URL}/b{book_id}/", verify=False, allow_redirects=False)
    r.raise_for_status()

    if r.status_code == 302:
        raise requests.HTTPError

    soup = BeautifulSoup(r.text, "lxml")
    return soup


def fetch_parsed_html_by_url(book_url):
    """Gets parsed html code from book page url.

    :param book_url: book url
    :return: parsed html
    """

    r = requests.get(book_url, verify=False, allow_redirects=False)
    r.raise_for_status()

    return BeautifulSoup(r.text, "lxml")


def extract_title_author(soup) -> (str, str):
    """Gets book title and author from parsed html.

    :param soup: parsed html
    :return: book title, author
    """

    title_author = soup.find('table', class_='tabs').find('div', id='content').find('h1').text
    title, author = title_author.split('::')

    return title.strip(), author.strip()


def download_image(soup) -> str:
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
        return [f"{comment_elm.find('span').text}" for comment_elm in comment_elms]


def extract_genres(soup):
    """Gets book genres.

    :param soup: parsed html
    :return: book genres
    """

    genre_elms = soup.find_all('a', title=re.compile('перейти к книгам этого жанра'))
    return [genre_elm.text for genre_elm in genre_elms]


def create_descriptive_json(books_urls):
    """Create descriptive json file containing information about all downloaded books.

    :param books_urls: urls for books
    """

    descriptive_json = []
    for book_url in books_urls:
        print(book_url)
        try:
            soup = fetch_parsed_html_by_url(book_url)
        except requests.HTTPError:
            continue

        record = dict()
        txt_url = extract_txt_url(soup)
        if not txt_url:
            continue

        record['title'], record['author'] = extract_title_author(soup)
        record['img_src'] = download_image(soup)
        record['comments'] = extract_comments(soup)
        record['genres'] = extract_genres(soup)
        record['book_path'] = download_txt(txt_url, record['title'])

        descriptive_json.append(record)

    with open('library.json', 'w', encoding='utf-8') as file:
        json.dump(descriptive_json, file, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download books (title, author, genre, image, comments).")
    parser.add_argument("num_pages", help="How many pages to download books from", type=int)
    args = parser.parse_args()

    requests.packages.urllib3.disable_warnings()

    os.makedirs(BOOKS_FOLDER, exist_ok=True)
    os.makedirs(IMAGES_FOLDER, exist_ok=True)

    books_urls = find_books_urls(args.num_pages)
    create_descriptive_json(books_urls)
