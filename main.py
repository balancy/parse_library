import argparse
import json
import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests

from parse_tululu_category import find_last_page_number, find_books_urls

BOOKS_FOLDER = "books/"
IMAGES_FOLDER = "images/"
SITE_URL = "https://tululu.org/"


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

    title_author = soup.select_one("table.tabs div#content h1").text
    title, author = title_author.split('::')

    return title.strip(), author.strip()


def download_image(soup, img_folder) -> str:
    """Gets book image url and downloads image from this url.

    :param soup: parsed html
    :param img_folder: folder to save images
    :return: path to the image on the drive
    """

    image_url = soup.select_one("table.d_book img")['src']
    response = requests.get(f"{SITE_URL}{image_url}", verify=False)
    response.raise_for_status()

    image_name = os.path.basename(image_url)
    path = os.path.join(img_folder, image_name)

    with open(path, 'wb') as f:
        f.write(response.content)

    return path


def extract_txt_url(soup):
    """Gets relative url to text version of the book.

    :param soup: parsed html
    :return: relative link to text version of the book
    """

    link_to_txt = soup.select_one("a[title*='скачать книгу txt']")
    if link_to_txt:
        return link_to_txt['href']


def download_txt(text_url, title, books_folder) -> str:
    """Downloads text version of the book and returns path to it.

    :param text_url: url where to get file from
    :param title: title of the book
    :param books_folder: folder to save books
    :return: path to the file
    """

    response = requests.get(f"{SITE_URL}{text_url}", verify=False)
    response.raise_for_status()

    path = os.path.join(books_folder, f"{sanitize_filename(title)}.txt")

    with open(path, 'wb') as f:
        f.write(response.content)

    return path


def extract_comments(soup):
    """Gets comments from parsed html.

    :param soup: parsed html
    :return: comments
    """

    comment_elms = soup.select("div.texts")
    if comment_elms:
        return [f"{comment_elm.find('span').text}" for comment_elm in comment_elms]


def extract_genres(soup):
    """Gets book genres.

    :param soup: parsed html
    :return: book genres
    """

    genre_elms = soup.select("a[title*='перейти к книгам этого жанра']")
    return [genre_elm.text for genre_elm in genre_elms]


def create_descriptive_json(books_urls, books_folder, img_folder, json_path, flag_skip_images, flag_skip_txt):
    """Create descriptive json file containing information about all downloaded books.

    :param books_urls: urls for books
    :param books_folder: folder containing text versions of books
    :param img_folder: folder containing images
    :param json_path: path to save descriptive json
    :param flag_skip_images: are images skipping
    :param flag_skip_txt: are text versions of books skipping
    """

    descriptive_json = []
    for book_url in books_urls:
        try:
            soup = fetch_parsed_html_by_url(book_url)
        except requests.HTTPError:
            print(f"'book_url' is not found.")
            continue

        record = dict()
        record['title'], record['author'] = extract_title_author(soup)
        if not flag_skip_images:
            record['img_src'] = download_image(soup, img_folder)
        if not flag_skip_txt:
            if txt_url := extract_txt_url(soup):
                record['book_path'] = download_txt(txt_url, record['title'], books_folder)

        if comments := extract_comments(soup):
            record['comments'] = comments
        record['genres'] = extract_genres(soup)

        descriptive_json.append(record)

    with open(os.path.join(json_path, 'library.json'), 'w', encoding='utf-8') as file:
        json.dump(descriptive_json, file, ensure_ascii=False)


def make_folders(folders_list) -> None:
    """Make folders if they don't exist or ignore if they exist.

    :param folders_list: list of folders
    """

    for folder in folders_list:
        if folder:
            os.makedirs(folder, exist_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download books (title, author, genre, image, comments).")
    parser.add_argument("-s", "--start_page", help="Which page to start download books from", type=int, default=1)
    parser.add_argument("-e", "--end_page", help="Which page to finish download books at", type=int,
                        default=find_last_page_number())
    parser.add_argument("--books_folder", help="Folder to save books", default=BOOKS_FOLDER)
    parser.add_argument("--imgs_folder", help="Folder to save images", default=IMAGES_FOLDER)
    parser.add_argument("--skip_imgs", action="store_true", help="Skip images downloading?")
    parser.add_argument("--skip_txt", action="store_true", help="Skip text versions downloading?")
    parser.add_argument("--json_path", help="Folder to save descriptive json file", default='')
    args = parser.parse_args()

    requests.packages.urllib3.disable_warnings()

    make_folders((args.books_folder, args.imgs_folder, args.json_path))

    books_urls = find_books_urls(args.start_page, args.end_page)
    if books_urls:
        create_descriptive_json(
            books_urls,
            args.books_folder,
            args.imgs_folder,
            args.json_path,
            args.skip_imgs,
            args.skip_txt,
        )
