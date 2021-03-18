import os
import re

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests


class Book:
    def __init__(self, book_id, site_url="https://tululu.org/", images_folder='images/', books_folder='books/'):
        self.site_url = site_url
        self.book_id = book_id
        self.images_folder = images_folder
        self.books_folder = books_folder

    @staticmethod
    def check_folders(images_folder='images/', books_folder='books/') -> None:
        """Checks if folders exist. If not, create them.
        """

        for folder in (images_folder, books_folder):
            if not os.path.exists(folder):
                os.makedirs(folder)

    def get_html(self) -> str:
        """Gets html code for book page.

        :return: html code
        """

        r = requests.get(f"{self.site_url}/b{str(self.book_id)}/", verify=False, allow_redirects=False)
        r.raise_for_status()

        if r.status_code == 302:
            raise requests.HTTPError

        return r.text

    @staticmethod
    def get_title_image(html) -> (str, str):
        """Gets book title and image link from html code.

        :param html: html code
        :return: book title and image link
        """

        soup = BeautifulSoup(html, "lxml")
        title_author = soup.find('table', class_='tabs').find('div', id='content').find('h1').text
        title, author = title_author.split('::')
        image_url = soup.find('table', class_='d_book').find('img')['src']

        return f"{title.strip()}", image_url

    def download_image(self, image_url) -> str:
        """Saves image in given folder.

        :param image_url: link where to get image
        :return: path to the image on the drive
        """

        response = requests.get(f"{self.site_url}{image_url}", verify=False)
        response.raise_for_status()

        image_name = image_url.split('/')[-1]
        path = f"{self.images_folder}{image_name}"

        with open(path, 'wb') as f:
            f.write(response.content)

        return path

    @staticmethod
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

    def download_txt(self, text_url, title) -> str:
        """Downloads txt file and saves it in given folder.

        :param text_url: link where to get file
        :param title: title of the book
        :return: path to the file
        """

        response = requests.get(f"{self.site_url}{text_url}", verify=False)
        response.raise_for_status()

        path = f"{self.books_folder}{sanitize_filename(title)}.txt"

        with open(path, 'wb') as f:
            f.write(response.content)

        return path

    @staticmethod
    def get_comments(html) -> list:
        """Gets comments from html code.

        :param html: html code
        :return: comments
        """

        soup = BeautifulSoup(html, 'lxml')
        comment_elms = soup.find_all('div', class_='texts')

        if comment_elms:
            comments = [comment_elm.find('span').text for comment_elm in comment_elms]
            return comments

        return list()
