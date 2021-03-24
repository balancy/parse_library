import re

from bs4 import BeautifulSoup
import requests

URL_SITE = "https://tululu.org"
URL_SYFY_SUFFIX = "/l55/"


def find_books_urls(num_pages=1):
    """Find sy-fy books urls from a given number of pages in Sy-Fy category on site tululu.org

    :param num_pages: number of pages
    :return: books urls
    """

    if num_pages < 1:
        print("Задайте число страниц большее или равное 1")
        return

    all_books = []
    for pagenumber in range(1, num_pages+1):
        r = requests.get(f"{URL_SITE}{URL_SYFY_SUFFIX}{pagenumber}", verify=False, allow_redirects=False)
        r.raise_for_status()

        soup = BeautifulSoup(r.content, 'lxml')

        content = soup.find('div', id='content')
        books = content.find_all('a', title=re.compile('Бесплатная библиотека.*читать online'))
        for book in books:
            all_books.append(f"{URL_SITE}{book['href']}")

    return all_books


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()

    found_books = find_books_urls(1)
    print(found_books)
