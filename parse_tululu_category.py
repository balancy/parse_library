import re

from bs4 import BeautifulSoup
import requests

URL_SITE = "https://tululu.org"
URL_SYFY_SUFFIX = "/l55/"


def find_books_urls(start_page, end_page=0):
    """Find sy-fy books urls from pages starting at start_page and finishing at end_page

    :param start_page: page to start looking books at
    :param end_page: page to finish looking books at
    :return: books urls
    """

    if start_page < 1:
        print("Задайте стартовую страницу больше 1")
        return

    end_page = end_page if end_page > start_page else start_page
    all_books = []
    for pagenumber in range(start_page, end_page+1):
        r = requests.get(f"{URL_SITE}{URL_SYFY_SUFFIX}{pagenumber}", verify=False, allow_redirects=False)
        r.raise_for_status()

        soup = BeautifulSoup(r.content, 'lxml')

        selector = "#content [title*='читать online']"
        for book in soup.select(selector):
            all_books.append(f"{URL_SITE}{book['href']}")

    return all_books


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()

    found_books = find_books_urls(1)
    print(found_books)
